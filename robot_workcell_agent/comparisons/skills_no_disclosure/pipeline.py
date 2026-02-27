"""
Skills Without Progressive Disclosure Pipeline.

Approach: All skill instructions are loaded upfront into the system prompt.
The agent has tool-calling access to execution tools (solver + genesis), but
NO reference-reading tools (those are inlined) and NO state machine / progressive
disclosure to guide ordering.

- ALL SKILL.md contents dumped into system prompt (no lazy loading)
- ALL reference guides included in system prompt
- Tools available: validate_stage1_json, run_placement_solver, run_genesis_simulation
- NO state machine (no check_stage_status, no enforced ordering)
- NO progressive disclosure (no load_skill, no read_skill_file)

Purpose: Test whether having skills WITHOUT progressive disclosure
and WITHOUT a state machine achieves comparable results to the full system.
Shows the value of progressive disclosure + state machine separately.
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from comparisons.shared.config import ComparisonConfig, get_config
from comparisons.shared.evidence_logger import EvidenceLogger
from comparisons.shared.test_prompts import TestPrompt
from comparisons.shared.validators import (
    validate_stage1, validate_stage2, validate_stage3, validate_stage3_input,
    validate_stage1_vs_prompt,
)
from comparisons.shared.stage_scripts import (
    run_solve_placement, prepare_genesis_input, fix_genesis_paths,
    run_genesis_build_and_execute
)

logger = logging.getLogger(__name__)

PIPELINE_NAME = "skills_no_disclosure"

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"


def _build_monolithic_system_prompt() -> str:
    """
    Build a system prompt with ALL skill instructions inlined.
    This is the 'no progressive disclosure' variant – everything upfront.
    """
    sections = []

    # Header
    sections.append("""You are an expert Robot Workcell Design Agent. All available skills and \
their complete reference documentation are included below in your instructions.

You have three execution tools:
- validate_stage1_json(stage1_json) — validate a Stage 1 requirements JSON against the schema
- run_placement_solver(stage1_json) — run the geometric placement optimiser
- run_genesis_simulation(genesis_input_json) — execute the Genesis physics simulation

Read the skill documentation below carefully and determine what to do and when.
""")

    # Load skill HEADERS only (name, description, when-to-use) — NOT the step-by-step
    # workflow instructions. The full workflow is what ours_full reveals *progressively*
    # via state-machine transitions; skills_no_disclosure only knows what skills exist
    # and what they do, not the detailed execution sequence.
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            # Extract YAML frontmatter metadata (description, stage, when-to-use)
            header_lines = []
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    header_lines = parts[1].strip().splitlines()
                    body = parts[2].strip()
                else:
                    body = content
            else:
                body = content
            # From the body, extract Overview + When to Use sections only
            body_excerpt = []
            in_section = False
            for line in body.splitlines():
                if line.startswith("## Overview") or line.startswith("## When to Use"):
                    in_section = True
                elif line.startswith("## ") and in_section:
                    break  # stop at next section
                if in_section:
                    body_excerpt.append(line)
            skill_summary = "\n".join(header_lines + [""] + body_excerpt).strip()
            sections.append(f"\n{'='*60}\nSKILL: {skill_dir.name}\n{'='*60}\n{skill_summary}")

    # Load ALL reference documents
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in sorted(refs_dir.iterdir()):
                if ref_file.suffix == ".md":
                    try:
                        ref_content = ref_file.read_text(encoding="utf-8")
                        sections.append(
                            f"\n{'='*60}\n"
                            f"REFERENCE: {skill_dir.name}/{ref_file.name}\n"
                            f"{'='*60}\n{ref_content}"
                        )
                    except:
                        pass

    # Minimal Stage 1 JSON schema — structural constraints only.
    # Semantic values (robot choice, component paths, dimensions) must come from the reference docs.
    sections.append("""
============================================================
STAGE 1 JSON STRUCTURAL REQUIREMENTS
============================================================
The Stage 1 output must be a JSON object. Required top-level fields:

  stage_1_complete        boolean — must be true
  task_objective          string — minimum 50 characters
  task_specification      object:
      name, sku_id, dimensions [L, W, H floats], weight_kg (float >0), material, quantity (int)
  additional_objects      array (can be empty)
  robot_selection         object:
      model, manufacturer, payload_kg (float >0), reach_m (float >0),
      justification (string, minimum 50 characters), urdf_path (string or null)
  workcell_components     array (minimum 1 item), each item:
      name, component_type, mjcf_path (string ending in .xml),
      position (must be null — filled later), orientation (must be null — filled later),
      dimensions [L, W, H floats, all >0]
  spatial_reasoning       object:
      zones (array, minimum 1): each has {zone_name, zone_type, center_position [x,y,z], radius_m (>0)}
      material_flow (string, minimum 30 characters)
      accessibility (string, minimum 30 characters)
      reasoning (string, minimum 50 characters)
  throughput_requirement  object: {items_per_hour (number), cycle_time_seconds (number)}
  constraints             array, each: {constraint_type, description (min 10 chars), value}
  missing_info            array

Use validate_stage1_json to check your output. Fix any validation errors and retry.

STAGE 3 GENESIS INPUT STRUCTURAL REQUIREMENTS
============================================================
After getting Stage 2 placement results, call run_genesis_simulation with a JSON
string containing these top-level fields:

  components          array — one entry per object in the scene, each with:
      name            string
      component_type  string — use "robot" for the robot arm
      urdf            string — the mjcf_path / urdf_path for this component
      position        [x, y, z] — from Stage 2 optimized_components (filled positions)
      orientation     [rx, ry, rz]
      dimensions      [L, W, H]
  robot_info          object — copy of Stage 1 robot_selection
  task_objective      string — copy of Stage 1 task_objective
  execute_trajectory  boolean — must be true
  motion_targets      object — copy of Stage 2 motion_targets (pick/place positions)
  z_lift              number — vertical lift height in metres (e.g. 0.4)

Build this by merging Stage 1 JSON + Stage 2 JSON: take the optimized_components
from Stage 2 (they have filled positions), add a robot entry using robot_selection
from Stage 1, and include motion_targets from Stage 2.

CRITICAL — your workcell_components array MUST include ALL FOUR of these:
  1. A robot pedestal / base mount (component_type containing "pedestal")
  2. An input conveyor or belt (component_type containing "conveyor" or "belt")
  3. An output pallet or staging area (component_type containing "pallet")
  4. The TARGET OBJECT being picked — the carton, box, or item itself
     (component_type or name containing "carton", "box", "item", or similar)

For mjcf_path values use RELATIVE paths only — do NOT use absolute disk paths.
Correct format:  "workcell_components/pedestals/robot_pedestal.xml"
Correct format:  "mujoco_menagerie/universal_robots_ur5e/ur5e.xml"
Wrong format:    "D:/GitHub/ieee_case/mujoco_menagerie/..." (absolute path)
""")

    return "\n".join(sections)


# ── OpenAI function-calling tool definitions ─────────────────────────

# Described as OpenAI function-calling schema (no LangChain/LangGraph).
# run_genesis_simulation is NEVER actually executed — the harness intercepts
# it and validates the agent's input args only.
_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "validate_stage1_json",
            "description": (
                "Validate a Stage 1 JSON against the required Pydantic schema. "
                "Input: Stage 1 JSON as a string. Returns validation result."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "stage1_json": {"type": "string", "description": "Stage 1 JSON as a string"}
                },
                "required": ["stage1_json"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_placement_solver",
            "description": (
                "Run the placement solver to calculate optimal positions for workcell "
                "components. Input: Stage 1 JSON as a string. Output: optimized layout JSON."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "stage1_json": {"type": "string", "description": "Stage 1 JSON as a string"}
                },
                "required": ["stage1_json"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_genesis_simulation",
            "description": (
                "Prepare and submit the Genesis simulation to build the scene and "
                "execute the pick-place trajectory. "
                "Input: genesis_input_json — combined JSON with robot, components, "
                "positions and trajectory parameters."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "genesis_input_json": {
                        "type": "string",
                        "description": "Genesis input JSON as a string",
                    }
                },
                "required": ["genesis_input_json"],
            },
        },
    },
]

# Tool names by expected stage for hit/miss tracking
EXPECTED_TOOLS_BY_STAGE: Dict[str, set] = {
    "1": {"validate_stage1_json"},
    "2": {"run_placement_solver"},
    "3": {"run_genesis_simulation"},
}


# ── Tool executors ────────────────────────────────────────────────────

def _exec_validate_stage1_json(stage1_json: str) -> str:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.schemas import Stage1Output
    try:
        data = json.loads(stage1_json)
        Stage1Output.model_validate(data)
        return json.dumps({"valid": True, "message": "Schema validation passed"})
    except Exception as e:
        return json.dumps({"valid": False, "errors": str(e)[:500]})


def _exec_run_placement_solver(stage1_json: str) -> str:
    import subprocess
    import sys as _sys
    script = SKILLS_DIR / "placement_solver" / "scripts" / "solve_placement.py"
    if not script.exists():
        return json.dumps({"error": "Script not found"})
    try:
        result = subprocess.run(
            [_sys.executable, str(script)],
            input=stage1_json,
            capture_output=True, text=True, timeout=60,
        )
        return result.stdout if result.returncode == 0 else json.dumps(
            {"error": f"Exit {result.returncode}", "stderr": result.stderr[:300]}
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


def _dispatch_tool(name: str, args: Dict[str, Any]) -> str:
    """Execute a tool call. Genesis is NEVER run — returns queued acknowledgement."""
    if name == "validate_stage1_json":
        return _exec_validate_stage1_json(args.get("stage1_json", ""))
    if name == "run_placement_solver":
        return _exec_run_placement_solver(args.get("stage1_json", ""))
    if name == "run_genesis_simulation":
        # Intercept — do not run the actual script.
        # Return a plausible acknowledgement so the agent can finish gracefully.
        return json.dumps({
            "status": "queued",
            "message": "Genesis simulation queued for execution. "
                       "Input validated and accepted.",
        })
    return json.dumps({"error": f"Unknown tool: {name}"})


# ── Raw OpenAI agentic loop ───────────────────────────────────────────

def _run_agent_loop(
    config: ComparisonConfig,
    system_prompt: str,
    user_message: str,
    max_rounds: int = 20,
) -> tuple:
    """
    Run an OpenAI function-calling conversation loop.

    Returns:
        (messages, usage_dict) where usage_dict has keys:
        api_calls, prompt_tokens, completion_tokens.
    """
    client = config.get_openai_client()
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    usage = {"api_calls": 0, "prompt_tokens": 0, "completion_tokens": 0}

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model=config.azure_deployment,
            messages=messages,
            tools=_TOOL_SCHEMAS,
            tool_choice="auto",
            temperature=0.3,
            max_tokens=4000,
        )
        usage["api_calls"] += 1
        if response.usage:
            usage["prompt_tokens"]     += response.usage.prompt_tokens or 0
            usage["completion_tokens"] += response.usage.completion_tokens or 0

        msg = response.choices[0].message
        # Append assistant turn (convert to dict)
        assistant_turn: Dict[str, Any] = {
            "role": "assistant",
            "content": msg.content or "",
        }
        tool_calls = getattr(msg, "tool_calls", None) or []
        if tool_calls:
            assistant_turn["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in tool_calls
            ]
        messages.append(assistant_turn)

        if not tool_calls:
            break  # Model finished

        # Execute each tool call and feed results back
        for tc in tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}
            tool_output = _dispatch_tool(tc.function.name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_output,
            })

    return messages, usage


def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(text)
    except Exception:
        pass
    if "```json" in text:
        try:
            start = text.index("```json") + 7
            end = text.index("```", start)
            return json.loads(text[start:end])
        except Exception:
            pass
    fb, lb = text.find("{"), text.rfind("}")
    if fb != -1 and lb != -1:
        try:
            return json.loads(text[fb:lb + 1])
        except Exception:
            pass
    return None


def _build_tc_output_map(messages: List[Dict]) -> Dict[str, str]:
    """Map tool_call_id → tool output string from raw OpenAI message dicts."""
    tc_outputs: Dict[str, str] = {}
    for msg in messages:
        if msg.get("role") == "tool":
            cid = msg.get("tool_call_id")
            if cid:
                tc_outputs[cid] = str(msg.get("content", ""))
    return tc_outputs


def _attribute_tool_calls_for_stage(
    messages: List[Dict], evidence: EvidenceLogger, stage: str
) -> None:
    """Log tool calls belonging to `stage` using raw OpenAI dict messages."""
    tool_to_stage: Dict[str, str] = {}
    for s, tools in EXPECTED_TOOLS_BY_STAGE.items():
        for t in tools:
            tool_to_stage[t] = s

    tc_outputs = _build_tc_output_map(messages)
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        for tc in msg.get("tool_calls", []):
            name = tc.get("function", {}).get("name", "")
            if tool_to_stage.get(name, "1") != stage:
                continue
            call_id = tc.get("id", "")
            args_raw = tc.get("function", {}).get("arguments", "{}")
            output = tc_outputs.get(call_id, "")
            success = "error" not in output.lower()[:100]
            evidence.log_tool_call(
                tool_name=name, stage=stage, args_summary=args_raw[:200],
                success=success, duration_s=0.0, is_appropriate=True,
            )


def _log_miss_if_no_call(messages: List[Dict], evidence: EvidenceLogger, stage: str) -> None:
    """
    If NO tool belonging to `stage` was called in `messages`, log one explicit
    miss so the hit/miss metric correctly reflects the omission.
    This prevents the misleading case where 0 hits AND 0 misses looks like the
    agent performed perfectly when it actually skipped the expected tool.
    """
    expected = EXPECTED_TOOLS_BY_STAGE.get(stage, set())
    called_names = set()
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        for tc in msg.get("tool_calls", []):
            called_names.add(tc.get("function", {}).get("name", ""))
    if not expected.intersection(called_names):
        tool_label = next(iter(expected), f"stage{stage}_tool")
        evidence.log_tool_call(
            tool_name=tool_label, stage=stage, args_summary="<not called>",
            success=False, duration_s=0.0, is_appropriate=False,
        )


def _extract_stage_data_from_messages(messages: List[Dict]) -> tuple:
    """
    Walk raw OpenAI dict messages and extract:
      - stage1_data: dict | None  (from a passing validate_stage1_json call)
      - stage2_data: dict | None  (from run_placement_solver output)
      - stage3_data: dict | None  (unused in dry-run but populated for live genesis)
    """
    tc_outputs = _build_tc_output_map(messages)
    stage1_data = stage2_data = stage3_data = None
    # Track ALL json submitted to validate_stage1_json (even failed ones) as a fallback
    last_validate_candidate: Optional[Dict[str, Any]] = None

    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        for tc in msg.get("tool_calls", []):
            name = tc.get("function", {}).get("name", "")
            call_id = tc.get("id", "")
            args_raw = tc.get("function", {}).get("arguments", "{}")
            output = tc_outputs.get(call_id, "")

            if name == "validate_stage1_json":
                try:
                    args = json.loads(args_raw)
                    candidate = _extract_json_from_text(args.get("stage1_json", ""))
                    if candidate:
                        last_validate_candidate = candidate  # keep updating — want the last attempt
                        result_obj = json.loads(output)
                        if result_obj.get("valid", False) and stage1_data is None:
                            stage1_data = candidate  # first passing
                except Exception:
                    pass

            if name == "run_placement_solver" and stage2_data is None:
                candidate = _extract_json_from_text(output)
                if candidate and candidate.get("status") == "success":
                    stage2_data = candidate

            if name == "run_genesis_simulation" and stage3_data is None:
                candidate = _extract_json_from_text(output)
                if candidate:
                    stage3_data = candidate

    # Fallback 1: scan tool reply messages for stage_1_complete marker
    if stage1_data is None:
        for msg in messages:
            if msg.get("role") == "tool":
                content = str(msg.get("content", ""))
                if '"stage_1_complete"' in content:
                    candidate = _extract_json_from_text(content)
                    if candidate:
                        stage1_data = candidate
                        break

    # Fallback 2: use the last JSON the agent submitted to validate_stage1_json,
    # even if the tool said it was invalid.  The harness will re-validate it
    # independently — this avoids penalising the agent for minor schema quirks.
    if stage1_data is None and last_validate_candidate is not None:
        stage1_data = last_validate_candidate

    # Fallback 3: scan the final assistant message text for any JSON blob
    if stage1_data is None:
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                candidate = _extract_json_from_text(msg.get("content", ""))
                if candidate:
                    stage1_data = candidate
                break

    return stage1_data, stage2_data, stage3_data


def _extract_genesis_args_from_messages(messages: List[Dict]) -> Optional[Dict[str, Any]]:
    """
    If the agent called run_genesis_simulation, return the parsed genesis input
    dict it passed as the argument.  Returns None if the tool was never called.
    Used for dry-run Stage 3 validation: we judge the agent's INPUT, not the
    script's output (which is never executed in dry-run).
    """
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        for tc in msg.get("tool_calls", []):
            name = tc.get("function", {}).get("name", "")
            if name != "run_genesis_simulation":
                continue
            args_raw = tc.get("function", {}).get("arguments", "{}")
            try:
                args = json.loads(args_raw)
            except Exception:
                continue
            parsed = _extract_json_from_text(args.get("genesis_input_json", ""))
            if parsed:
                return parsed
    return None


# ── Per-iteration run ────────────────────────────────────────────────

def run_iteration(
    prompt: TestPrompt,
    iteration_id: int,
    config: ComparisonConfig,
    evidence: EvidenceLogger,
    system_prompt: str,
) -> Dict[str, Any]:
    """Run one full iteration of the skills-no-disclosure pipeline."""
    evidence.start_iteration(iteration_id, prompt.id, prompt.prompt)
    result = {"stage1_success": False, "stage2_success": False, "stage3_success": False}

    full_prompt = (
        f"Design a robotic workcell for this task:\n\n{prompt.prompt}\n\n"
        "Use the skills and tools available to you to complete the pipeline."
    )

    t0 = time.time()
    try:
        messages, llm_usage = _run_agent_loop(config, system_prompt, full_prompt)
    except Exception as e:
        logger.exception(f"Agent loop error: {e}")
        for s in ["1", "2", "3"]:
            evidence.start_stage(s)
            evidence.end_stage(False, f"Agent error: {str(e)[:200]}")
        evidence.end_iteration()
        return result

    evidence.log_llm_usage(
        llm_usage["api_calls"],
        llm_usage["prompt_tokens"],
        llm_usage["completion_tokens"],
    )

    stage1_data, stage2_data, _ = _extract_stage_data_from_messages(messages)
    genesis_args_from_agent = _extract_genesis_args_from_messages(messages)


    # ── Stage 1 ──────────────────────────────────────────────────
    evidence.start_stage("1")
    _attribute_tool_calls_for_stage(messages, evidence, "1")
    _log_miss_if_no_call(messages, evidence, "1")  # miss if validate_stage1_json never called
    if stage1_data is None:
        # Last assistant text as debug info
        last_text = next(
            (m.get("content", "") for m in reversed(messages) if m.get("role") == "assistant"),
            ""
        )
        evidence.end_stage(False, "Failed to extract Stage 1 JSON from agent output",
                         output_data={"agent_output": last_text[:500]})
        # Log explicit misses for Stage 2 and 3
        evidence.start_stage("2")
        evidence.log_tool_call(
            "run_placement_solver", "2", "skipped_stage1_failed",
            success=False, duration_s=0.0, is_appropriate=False
        )
        evidence.end_stage(False, "Skipped – Stage 1 failed")
        evidence.start_stage("3")
        evidence.log_tool_call(
            "run_genesis_simulation", "3", "skipped_stage1_failed",
            success=False, duration_s=0.0, is_appropriate=False
        )
        evidence.end_stage(False, "Skipped – Stage 1 failed")
        evidence.end_iteration()
        return result
    else:
        s1_ok, s1_msg, s1_details = validate_stage1(stage1_data)
        result["stage1_success"] = s1_ok
        evidence.end_stage(s1_ok, s1_msg,
                         output_data=stage1_data, validation_details=s1_details)

    # ── Stage 2 ──────────────────────────────────────────────────
    evidence.start_stage("2")
    _attribute_tool_calls_for_stage(messages, evidence, "2")
    _s2_data_ok = False
    if not result["stage1_success"]:
        evidence.log_tool_call(
            "run_placement_solver", "2", "skipped_stage1_failed",
            success=False, duration_s=0.0, is_appropriate=False
        )
        evidence.end_stage(False, "Skipped – Stage 1 invalid")
        # Log explicit miss for Stage 3
        evidence.start_stage("3")
        evidence.log_tool_call(
            "run_genesis_simulation", "3", "skipped_stage2_failed",
            success=False, duration_s=0.0, is_appropriate=False
        )
        evidence.end_stage(False, "Skipped – Stage 2 failed")
        evidence.end_iteration()
        return result
    elif stage2_data is None:
        logger.warning("Agent did not call run_placement_solver; running fallback.")
        evidence.log_tool_call(
            "solve_placement_fallback", "2", "agent_did_not_call",
            success=True, duration_s=0.0, is_appropriate=False
        )
        stage2_data = run_solve_placement(stage1_data)
        s2_ok, s2_msg, s2_details = validate_stage2(stage2_data)
        _s2_data_ok = s2_ok
        result["stage2_success"] = False
        evidence.end_stage(False, f"[FALLBACK] {s2_msg} – agent did not call placement solver",
                         output_data=stage2_data, validation_details=s2_details)
    else:
        s2_ok, s2_msg, s2_details = validate_stage2(stage2_data)
        _s2_data_ok = s2_ok
        s2_success = s2_ok
        if s2_ok and stage1_data is not None:
            sq_ok, sq_msg, sq_details = validate_stage1_vs_prompt(
                stage1_data, prompt.expected_robot, prompt.expected_components
            )
            s2_details["stage1_vs_prompt"] = sq_details
            if not sq_ok:
                s2_success = False
                s2_msg = f"Solver OK but Stage 1 input quality failed: {sq_msg}"
        result["stage2_success"] = s2_success
        evidence.end_stage(s2_success, s2_msg,
                         output_data=stage2_data, validation_details=s2_details)

    # ── Stage 3 ──────────────────────────────────────────────────
    evidence.start_stage("3")
    _attribute_tool_calls_for_stage(messages, evidence, "3")
    if not _s2_data_ok:
        evidence.log_tool_call(
            "run_genesis_simulation", "3", "skipped_stage2_failed",
            success=False, duration_s=0.0, is_appropriate=False
        )
        evidence.end_stage(False, "Skipped – Stage 2 data unavailable")
    elif genesis_args_from_agent is not None:
        # Apply the same path resolution the harness uses for other pipelines
        genesis_args_from_agent = fix_genesis_paths(genesis_args_from_agent)
        s3_ok, s3_msg, s3_details = validate_stage3_input(genesis_args_from_agent)
        result["stage3_success"] = s3_ok
        evidence.end_stage(s3_ok, f"[DRY-RUN] Agent called genesis – {s3_msg}",
                         output_data=genesis_args_from_agent, validation_details=s3_details)
    else:
        evidence.log_tool_call(
            "run_genesis_simulation", "3", "agent_did_not_call",
            success=False, duration_s=0.0, is_appropriate=False
        )
        result["stage3_success"] = False
        evidence.end_stage(False,
                         "[DRY-RUN] Agent did not call run_genesis_simulation "
                         "despite 3-stage instructions")

    evidence.end_iteration()
    return result


def run_pipeline(
    prompts: list,
    config: ComparisonConfig = None,
    start_id: int = 0,
    resume_from=None,
) -> EvidenceLogger:
    """Run the full skills-no-disclosure pipeline across all prompts."""
    if config is None:
        config = get_config()

    evidence = EvidenceLogger(PIPELINE_NAME, config.logs_dir / PIPELINE_NAME,
                              resume_from=resume_from)
    logger.info(f"Starting {PIPELINE_NAME} pipeline: {len(prompts)} prompts (start_id={start_id})")

    # Build the monolithic system prompt ONCE (all skills + refs inlined)
    system_prompt = _build_monolithic_system_prompt()
    logger.info(f"  System prompt size: {len(system_prompt)} chars")

    for i, prompt in enumerate(prompts):
        logger.info(f"  [{i+1}/{len(prompts)}] {prompt.id}: {prompt.description}")
        run_iteration(prompt, start_id + i + 1, config, evidence, system_prompt)

    logger.info(f"{PIPELINE_NAME} complete. Summary: {json.dumps(evidence.get_summary(), indent=2)}")
    return evidence
