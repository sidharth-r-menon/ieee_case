"""
LangChain Tool-Calling Pipeline.

Approach: LangChain AgentExecutor with tool calling + memory/RAG.
- ALL reference docs accessible as tools (RAG-style)
- Tools for placement solver and genesis execution
- ConversationBufferMemory for multi-turn
- NO domain-specific state machine
- NO progressive disclosure (all tools visible at once)

Purpose: Test whether general LLM orchestration with tools is sufficient
without domain-specific workflow control.
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List

from comparisons.shared.config import ComparisonConfig, get_config
from comparisons.shared.evidence_logger import EvidenceLogger
from comparisons.shared.test_prompts import TestPrompt
from comparisons.shared.validators import (
    validate_stage1, validate_stage2, validate_stage3_input,
    validate_stage1_vs_prompt, validate_stage3_agent_submission,
)
from comparisons.shared.stage_scripts import (
    run_solve_placement, prepare_genesis_input, fix_genesis_paths,
)

logger = logging.getLogger(__name__)

PIPELINE_NAME = "langchain_tools"

LANGCHAIN_SYSTEM_PROMPT = """You are a robot workcell design assistant. Complete the 3-stage pipeline below in order.

WORKFLOW:
1. Call read_gap_analysis_guide, read_standard_objects_guide, and read_robot_selection_guide to gather all required information before producing any JSON.
2. Call validate_stage1_json with your Stage 1 JSON. Fix any errors reported and retry if needed.
3. Call run_placement_solver with the validated Stage 1 JSON string.
4. Call run_genesis_simulation with the merged scene JSON built from Stage 1 + Stage 2 outputs.

STAGE 1 JSON — required top-level fields:
  stage_1_complete        boolean — must be true
  task_objective          string — minimum 50 characters
  task_specification      object: name, sku_id, dimensions [L,W,H floats], weight_kg (float >0), material, quantity (int)
  additional_objects      array (can be empty)
  robot_selection         object: model, manufacturer, payload_kg (float >0), reach_m (float >0), justification (≥50 chars), urdf_path
  workcell_components     array — each item: name, component_type, mjcf_path (relative .xml path), position (null), orientation (null), dimensions [L,W,H]
  spatial_reasoning       object: zones (array, each has zone_name, zone_type, center_position [x,y,z], radius_m >0), material_flow (≥30 chars), accessibility (≥30 chars), reasoning (≥50 chars)
  throughput_requirement  object: items_per_hour (number), cycle_time_seconds (number)
  constraints             array
  missing_info            array — must be []

Constraints:
  - workcell_components MUST include one of each: pedestal, conveyor/belt, pallet, and the target object (carton/box).
  - All positions and orientations in workcell_components must be null.
  - robot payload_kg must be ≥ object weight_kg.
  - cycle_time_seconds must match 3600 / items_per_hour (within 15%).
  - Use relative mjcf_path values only — consult the reference guides for correct paths and dimensions.

STAGE 3 JSON — required top-level fields (build by merging Stage 1 robot_selection + Stage 2 optimized_components):
  components        array — one per scene object, each with: name, component_type, urdf (relative path), position [x,y,z], orientation [rx,ry,rz], dimensions [L,W,H]. The robot entry must have component_type "robot".
  robot_info        object — copy of Stage 1 robot_selection
  task_objective    string — copy of Stage 1 task_objective
  execute_trajectory  boolean — must be true
  motion_targets    object — copy of Stage 2 motion_targets
  z_lift            number
"""


def _create_langchain_agent(config: ComparisonConfig):
    """Create a LangChain agent (CompiledStateGraph) with tools and in-memory checkpointer."""
    from langchain_openai import AzureChatOpenAI
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver
    from comparisons.langchain_tools.tools import get_tool_definitions

    llm = AzureChatOpenAI(
        azure_deployment=config.azure_deployment,
        api_key=config.azure_api_key,
        azure_endpoint=config.azure_endpoint,
        api_version=config.azure_api_version,
        temperature=0.3,
        max_tokens=3500,
    )

    tools = get_tool_definitions()

    # create_agent returns a CompiledStateGraph – do NOT wrap in AgentExecutor
    graph = create_agent(
        model=llm,
        tools=tools,
        system_prompt=LANGCHAIN_SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )

    return graph


def _invoke_agent(graph, user_message: str, thread_id: str) -> tuple:
    """Invoke the LangGraph agent graph with a user message.

    recursion_limit=50 gives the agent room for:
      3 RAG reads (6 steps) + up to 5 validate retries (10 steps) +
      placement solver (2 steps) + final answer (1 step) = ~19 steps minimum.
    20 was too low — it hit the limit before completing even one happy path.

    Returns:
        (agent_result_dict, config_dict) so callers can salvage partial state
        via graph.get_state(config) if a RecursionError is raised.
    """
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 25,
    }
    result = graph.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config=config,
    )
    return result, config


def _get_output_text(agent_result: dict) -> str:
    """Extract the final AI text from a graph result's messages list."""
    messages = agent_result.get("messages", [])
    for msg in reversed(messages):
        msg_type = getattr(msg, "type", None)
        if msg_type == "ai":
            content = getattr(msg, "content", "")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return " ".join(
                    block.get("text", "") for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
    return ""


def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Best-effort JSON extraction."""
    try:
        return json.loads(text)
    except:
        pass

    if "```json" in text:
        try:
            start = text.index("```json") + 7
            end = text.index("```", start)
            return json.loads(text[start:end])
        except:
            pass

    fb = text.find("{")
    lb = text.rfind("}")
    if fb != -1 and lb != -1:
        try:
            return json.loads(text[fb:lb + 1])
        except:
            pass

    return None


def _build_tc_output_map(messages: list) -> Dict[str, str]:
    """Build a tool_call_id -> output string map from ToolMessages."""
    tc_outputs: Dict[str, str] = {}
    for msg in messages:
        if getattr(msg, "type", None) == "tool":
            cid = getattr(msg, "tool_call_id", None)
            if cid:
                tc_outputs[cid] = str(getattr(msg, "content", ""))
    return tc_outputs


def _attribute_tool_calls_for_stage(
    messages: list, evidence: EvidenceLogger, stage: str, seen_call_ids: set
) -> None:
    """Log tool calls that belong to `stage` (must be called inside an open stage block).

    Each tool call (by call_id) is attributed exactly ONCE — to the first stage
    that lists it as an expected tool.  Cross-stage calls are ignored so that the
    same call_id is never counted as a miss in one stage and a hit in another.
    If no expected tool was called at all for this stage, a synthetic miss is logged.
    """
    from comparisons.langchain_tools.tools import EXPECTED_TOOLS_BY_STAGE

    expected_tools = set(EXPECTED_TOOLS_BY_STAGE.get(stage, set()))
    tc_outputs = _build_tc_output_map(messages)

    found_expected = False
    for msg in messages:
        if getattr(msg, "type", None) != "ai":
            continue
        for tc in getattr(msg, "tool_calls", []):
            name = tc.get("name", "") if isinstance(tc, dict) else getattr(tc, "name", "")
            call_id = tc.get("id", "") if isinstance(tc, dict) else getattr(tc, "id", "")
            args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})

            # Skip calls already attributed to a prior stage
            if call_id in seen_call_ids:
                continue

            if name in expected_tools:
                seen_call_ids.add(call_id)
                found_expected = True
                evidence.log_tool_call(
                    tool_name=name,
                    stage=stage,
                    args_summary=str(args)[:200],
                    success=True,
                    duration_s=0.0,
                    is_appropriate=True,
                )

    # If the agent never called the expected tool(s) for this stage, log a single miss
    if not found_expected:
        missing = ", ".join(sorted(expected_tools))
        evidence.log_tool_call(
            tool_name=f"<missing: {missing}>",
            stage=stage,
            args_summary="agent did not call expected tool for this stage",
            success=False,
            duration_s=0.0,
            is_appropriate=False,
        )


def _extract_stage_data_from_messages(
    messages: list,
) -> tuple:
    """
    Walk the full message history from a single autonomous agent run and extract:
      - stage1_data : dict | None  (from validate_stage1_json call that passed)
      - stage2_data : dict | None  (from run_placement_solver tool output)
      - stage3_data : dict | None  (from run_genesis_simulation tool output)
    """
    tc_outputs = _build_tc_output_map(messages)

    stage1_data = stage2_data = stage3_data = None

    for msg in messages:
        if getattr(msg, "type", None) != "ai":
            continue
        for tc in getattr(msg, "tool_calls", []):
            name = tc.get("name", "") if isinstance(tc, dict) else getattr(tc, "name", "")
            call_id = tc.get("id", "") if isinstance(tc, dict) else getattr(tc, "id", "")
            args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})
            output = tc_outputs.get(call_id, "")

            # Stage 1: validated input JSON from a passing validate_stage1_json call
            if name == "validate_stage1_json" and stage1_data is None:
                try:
                    result_obj = json.loads(output)
                    if result_obj.get("valid", False):
                        raw = args.get("stage1_json", "") if isinstance(args, dict) else ""
                        candidate = _extract_json_from_text(raw)
                        if candidate:
                            stage1_data = candidate
                except Exception:
                    pass

            # Stage 2: successful placement solver output
            if name == "run_placement_solver" and stage2_data is None:
                candidate = _extract_json_from_text(output)
                if candidate and candidate.get("status") == "success":
                    stage2_data = candidate

            # Stage 3: capture the INPUT args the agent passed to run_genesis_simulation
            # (the tool now returns a dry-run validation result, not simulation output;
            #  we need the input to run validate_stage3_input on it ourselves)
            if name == "run_genesis_simulation" and stage3_data is None:
                raw = args.get("genesis_input_json", "") if isinstance(args, dict) else ""
                candidate = _extract_json_from_text(raw)
                if candidate:
                    stage3_data = candidate

    # Fallback for stage1: scan tool output messages for stage_1_complete marker
    if stage1_data is None:
        for msg in messages:
            if getattr(msg, "type", None) == "tool":
                content = str(getattr(msg, "content", ""))
                if '"stage_1_complete"' in content:
                    candidate = _extract_json_from_text(content)
                    if candidate:
                        stage1_data = candidate
                        break

    # Last-resort stage1: parse final AI text
    if stage1_data is None:
        output_text = _get_output_text({"messages": messages})
        stage1_data = _extract_json_from_text(output_text)

    return stage1_data, stage2_data, stage3_data


def run_iteration(
    prompt: TestPrompt,
    iteration_id: int,
    config: ComparisonConfig,
    evidence: EvidenceLogger,
) -> Dict[str, Any]:
    """
    Run one full iteration of the LangChain pipeline.

    The agent receives the task ONCE and must autonomously orchestrate all stages:
      Stage 1: read guides → generate + validate Stage 1 JSON
      Stage 2: call run_placement_solver with that JSON
      Stage 3: call run_genesis_simulation (dry-run structural validator — genesis never launches)

    The harness only evaluates outputs; it does NOT orchestrate between stages.
    """
    evidence.start_iteration(iteration_id, prompt.id, prompt.prompt)
    result = {"stage1_success": False, "stage2_success": False, "stage3_success": False}

    try:
        agent_graph = _create_langchain_agent(config)
    except Exception as e:
        logger.error(f"Failed to create LangChain agent: {e}")
        for s in ["1", "2", "3"]:
            evidence.start_stage(s)
            evidence.end_stage(False, f"Agent creation failed: {str(e)[:200]}")
        evidence.end_iteration()
        return result

    thread_id = f"{prompt.id}_{iteration_id}"

    full_prompt = (
        f"Design a robotic workcell for this task:\n\n{prompt.prompt}\n\n"
        "Use your available tools to complete the workcell design pipeline."
    )

    # ── Single agent invocation — agent orchestrates everything ──
    t0 = time.time()
    agent_result = None
    messages = []
    try:
        agent_result, _invoke_config = _invoke_agent(agent_graph, full_prompt, thread_id)
        messages = agent_result.get("messages", [])
    except Exception as e:
        err_str = str(e)
        # On GraphRecursionError, try to salvage whatever messages were
        # accumulated in the checkpointer before the limit was hit.
        if "recursion" in err_str.lower():
            try:
                _cfg = {"configurable": {"thread_id": thread_id}}
                partial_state = agent_graph.get_state(_cfg)
                messages = list(getattr(partial_state, "values", {}).get("messages", []))
                logger.warning(
                    f"RecursionError hit — salvaged {len(messages)} messages from graph state"
                )
            except Exception as salvage_err:
                logger.warning(f"Could not salvage partial state: {salvage_err}")
        # If we couldn't salvage anything useful, fail gracefully
        if not messages:
            logger.exception(f"Agent invocation error: {e}")
            for s in ["1", "2", "3"]:
                evidence.start_stage(s)
                evidence.end_stage(False, f"Agent error: {err_str[:200]}")
            evidence.end_iteration()
            return result

    # Extract LLM usage from LangGraph AI messages (each AI turn = one API call)
    lc_api_calls = 0
    lc_prompt_tok = 0
    lc_completion_tok = 0
    for msg in messages:
        if getattr(msg, "type", None) == "ai":
            lc_api_calls += 1
            um = getattr(msg, "usage_metadata", None) or {}
            lc_prompt_tok     += um.get("input_tokens", 0)
            lc_completion_tok += um.get("output_tokens", 0)
    evidence.log_llm_usage(lc_api_calls, lc_prompt_tok, lc_completion_tok)

    # Extract each stage's data from the full message history
    stage1_data, stage2_data, stage3_data_from_agent = _extract_stage_data_from_messages(messages)

    # Shared set so each tool call_id is attributed to exactly one stage
    _seen_call_ids: set = set()

    # ── Evaluate Stage 1 ─────────────────────────────────────────
    evidence.start_stage("1")
    _attribute_tool_calls_for_stage(messages, evidence, "1", _seen_call_ids)
    if stage1_data is None:
        output_text = _get_output_text(agent_result)
        evidence.end_stage(False, "Failed to extract Stage 1 JSON from agent output",
                         output_data={"agent_output": output_text[:500]})
    else:
        s1_ok, s1_msg, s1_details = validate_stage1(stage1_data)
        result["stage1_success"] = s1_ok
        evidence.end_stage(s1_ok, s1_msg,
                         output_data=stage1_data, validation_details=s1_details)

    # ── Evaluate Stage 2 ─────────────────────────────────────────
    evidence.start_stage("2")
    _attribute_tool_calls_for_stage(messages, evidence, "2", _seen_call_ids)
    # _s2_data_ok: tracks whether valid Stage-2 data exists for flow control to Stage 3.
    # result["stage2_success"] is True only when the AGENT autonomously called the solver.
    _s2_data_ok = False
    if not result["stage1_success"]:
        evidence.end_stage(False, "Skipped – Stage 1 invalid")
    elif stage2_data is None:
        # Agent did not call the placement solver — run fallback and penalise
        logger.warning("Agent did not call run_placement_solver; running fallback.")
        evidence.log_tool_call(
            "solve_placement_fallback", "2", "agent_did_not_call",
            success=True, duration_s=0.0, is_appropriate=False
        )
        stage2_data = run_solve_placement(stage1_data)
        s2_ok, s2_msg, s2_details = validate_stage2(stage2_data)
        _s2_data_ok = s2_ok  # data available for Stage 3 flow control
        result["stage2_success"] = False  # agent did not orchestrate this stage
        evidence.end_stage(False, f"[FALLBACK] {s2_msg} – agent did not call placement solver",
                         output_data=stage2_data, validation_details=s2_details)
    else:
        s2_ok, s2_msg, s2_details = validate_stage2(stage2_data)
        _s2_data_ok = s2_ok  # solver data available for Stage 3 flow regardless of quality check
        # Cross-check Stage 1 input quality against what the prompt explicitly required.
        # The solver always succeeds (deterministic), so granting Stage 2 success requires
        # the agent to have also selected the right robot and included all required components.
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

    # ── Evaluate Stage 3 ─────────────────────────────────────────
    # Genesis is never actually launched — we validate the agent's INPUT structure.
    # Pattern is identical to skills_no_disclosure:
    #   - If agent called run_genesis_simulation → validate the JSON it submitted (hit)
    #   - If agent did not call              → harness fallback, log as miss
    evidence.start_stage("3")
    _attribute_tool_calls_for_stage(messages, evidence, "3", _seen_call_ids)
    if not _s2_data_ok:
        evidence.end_stage(False, "Skipped – Stage 2 data unavailable")
    elif stage3_data_from_agent is not None:
        # Agent called run_genesis_simulation.
        # Validate the raw submission first (before path-fixing) — the agent must
        # provide valid, existing file paths.  fix_genesis_paths() rescues bad paths,
        # but the LangChain pipeline receives no path-fixing assistance from the harness.
        s3_ok, s3_msg, s3_details = validate_stage3_agent_submission(stage3_data_from_agent)
        result["stage3_success"] = s3_ok
        evidence.end_stage(s3_ok, f"[DRY-RUN] Agent called genesis – {s3_msg}",
                         output_data=stage3_data_from_agent, validation_details=s3_details)
    else:
        # Agent did not call run_genesis_simulation — harness merges Stage 1+2 and validates
        evidence.log_tool_call(
            "run_genesis_simulation", "3", "agent_did_not_call",
            success=False, duration_s=0.0, is_appropriate=False
        )
        try:
            genesis_input = prepare_genesis_input(stage1_data, stage2_data)
            genesis_input = fix_genesis_paths(genesis_input)
            evidence.log_tool_call(
                "prepare_genesis_input", "3", "harness_fallback",
                success=True, duration_s=0.0, is_appropriate=False
            )
            s3_ok, s3_msg, s3_details = validate_stage3_input(genesis_input)
            result["stage3_success"] = False  # agent did not orchestrate Stage 3
            evidence.end_stage(False,
                             f"[DRY-RUN] Agent did not call run_genesis_simulation – {s3_msg}",
                             output_data=genesis_input, validation_details=s3_details)
        except Exception as e:
            evidence.end_stage(False, f"[DRY-RUN] Exception: {str(e)[:200]}")

    evidence.end_iteration()
    return result


def run_pipeline(
    prompts: list,
    config: ComparisonConfig = None,
    start_id: int = 0,
    resume_from=None,
) -> EvidenceLogger:
    """Run the full LangChain pipeline across all prompts."""
    if config is None:
        config = get_config()

    evidence = EvidenceLogger(PIPELINE_NAME, config.logs_dir / PIPELINE_NAME,
                              resume_from=resume_from)
    logger.info(f"Starting {PIPELINE_NAME} pipeline: {len(prompts)} prompts (start_id={start_id})")

    for i, prompt in enumerate(prompts):
        logger.info(f"  [{i+1}/{len(prompts)}] {prompt.id}: {prompt.description}")
        run_iteration(prompt, start_id + i + 1, config, evidence)

    logger.info(f"{PIPELINE_NAME} complete. Summary: {json.dumps(evidence.get_summary(), indent=2)}")
    return evidence
