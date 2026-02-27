"""
Naive LLM (Zero-Shot) Pipeline.

Approach: LLM-only – no tools, no references, no state machine.

  Stage 1 – Zero-shot JSON generation from task description + schema spec.
             Validated via Pydantic (Stage1Output.model_validate).

  Stage 2 – LLM generates 3-D placement coordinates from Stage 1 JSON.
             Validated by running our deterministic solver on the same input
             and comparing the LLM positions against the reference solution.
             Pass if ≥ 50 % of component positions are within 0.5 m AND
             both motion targets are within 0.5 m of the solver reference.

  Stage 3 – Always recorded as FAIL (score = 0).
             A zero-shot LLM call cannot drive the Genesis physics simulator;
             it has no mechanism to build a scene, resolve MJCF paths, or
             execute a 6-phase pick-and-place trajectory.

Purpose: Baseline – tests raw LLM capability at structured JSON generation
         and spatial layout reasoning, without any tooling support.
"""

import json
import time
import logging
from typing import Dict, Any, Optional

from comparisons.shared.config import ComparisonConfig, get_config
from comparisons.shared.evidence_logger import EvidenceLogger
from comparisons.shared.test_prompts import TestPrompt
from comparisons.shared.validators import (
    validate_stage1, validate_stage2, compare_stage2_to_reference
)
from comparisons.shared.stage_scripts import run_solve_placement
from comparisons.naive_llm.prompts import STAGE1_SYSTEM_PROMPT, STAGE2_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

PIPELINE_NAME = "naive_llm"

# Tolerances used when comparing LLM placement to the solver reference.
POSITION_TOLERANCE_M = 0.5   # per-component Euclidean error threshold (metres)
MOTION_TOLERANCE_M   = 0.5   # pick / place target error threshold (metres)
MIN_MATCH_FRACTION   = 0.5   # fraction of reference components that must match


def _call_llm_zero_shot(
    config: ComparisonConfig, system_prompt: str, user_prompt: str
) -> tuple:
    """Make a single zero-shot LLM call.

    Returns:
        (text, prompt_tokens, completion_tokens)
    """
    client = config.get_openai_client()

    response = client.chat.completions.create(
        model=config.azure_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )

    prompt_tok     = response.usage.prompt_tokens     if response.usage else 0
    completion_tok = response.usage.completion_tokens if response.usage else 0
    return response.choices[0].message.content, prompt_tok, completion_tok


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Best-effort JSON extraction from LLM response."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        try:
            return json.loads(text[start:end])
        except Exception:
            pass

    if "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        try:
            return json.loads(text[start:end])
        except Exception:
            pass

    # Try finding first { to last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1:
        try:
            return json.loads(text[first_brace:last_brace + 1])
        except Exception:
            pass

    return None


def run_iteration(
    prompt: TestPrompt,
    iteration_id: int,
    config: ComparisonConfig,
    evidence: EvidenceLogger,
) -> Dict[str, Any]:
    """
    Run one full iteration of the naive LLM pipeline.

    Returns:
        Dict with stage1_success, stage2_success, stage3_success, etc.
    """
    evidence.start_iteration(iteration_id, prompt.id, prompt.prompt)
    result = {"stage1_success": False, "stage2_success": False, "stage3_success": False}

    # Accumulate LLM usage across all calls in this iteration
    total_api_calls = 0
    total_prompt_tok = 0
    total_completion_tok = 0

    # ── STAGE 1: Zero-shot workcell design JSON ───────────────────
    evidence.start_stage("1")
    stage1_data = None

    try:
        t0 = time.time()
        raw_response, p_tok, c_tok = _call_llm_zero_shot(config, STAGE1_SYSTEM_PROMPT, prompt.prompt)
        llm_duration = time.time() - t0
        total_api_calls += 1
        total_prompt_tok += p_tok
        total_completion_tok += c_tok

        evidence.log_tool_call(
            "llm_zero_shot_stage1", "1", f"prompt_len={len(prompt.prompt)}",
            success=True, duration_s=llm_duration, is_appropriate=True,
        )

        stage1_data = _extract_json(raw_response)

        if stage1_data is None:
            evidence.end_stage(
                False, "Failed to parse JSON from LLM Stage 1 response",
                output_data={"raw_response": raw_response[:500]},
            )
        else:
            s1_ok, s1_msg, s1_details = validate_stage1(stage1_data)
            result["stage1_success"] = s1_ok
            evidence.end_stage(s1_ok, s1_msg,
                               output_data=stage1_data, validation_details=s1_details)

    except Exception as e:
        logger.exception(f"Stage 1 error: {e}")
        evidence.log_tool_call("llm_zero_shot_stage1", "1", "error",
                               success=False, duration_s=0, error=str(e))
        evidence.end_stage(False, f"Exception: {str(e)[:200]}")

    # ── STAGE 2: LLM generates placement coordinates then we compare
    #            against the deterministic solver reference.  ───────
    evidence.start_stage("2")

    if stage1_data is None or not result["stage1_success"]:
        evidence.end_stage(False, "Skipped – Stage 1 failed")
    else:
        llm_stage2_data = None
        reference_stage2_data = None

        # 2a. LLM generates placement coordinates
        try:
            user_msg = (
                "Here is the Stage 1 requirements JSON. "
                "Generate optimal 3-D placement positions for all workcell components.\n\n"
                + json.dumps(stage1_data, indent=2)
            )

            t0 = time.time()
            raw_s2, p_tok2, c_tok2 = _call_llm_zero_shot(config, STAGE2_SYSTEM_PROMPT, user_msg)
            llm_s2_duration = time.time() - t0
            total_api_calls += 1
            total_prompt_tok += p_tok2
            total_completion_tok += c_tok2

            evidence.log_tool_call(
                "llm_zero_shot_stage2", "2",
                f"stage1_components={len(stage1_data.get('workcell_components', []))}",
                success=True, duration_s=llm_s2_duration, is_appropriate=True,
            )

            llm_stage2_data = _extract_json(raw_s2)

            if llm_stage2_data is None:
                evidence.end_stage(
                    False, "Failed to parse JSON from LLM Stage 2 response",
                    output_data={"raw_response": raw_s2[:500]},
                )
                evidence.end_iteration()
                return result

        except Exception as e:
            logger.exception(f"Stage 2 LLM call error: {e}")
            evidence.log_tool_call("llm_zero_shot_stage2", "2", "error",
                                   success=False, duration_s=0, error=str(e))
            evidence.end_stage(False, f"Exception in Stage 2 LLM call: {str(e)[:200]}")
            evidence.end_iteration()
            return result

        # 2b. Run actual solver to obtain reference solution
        try:
            t0 = time.time()
            reference_stage2_data = run_solve_placement(stage1_data)
            ref_duration = time.time() - t0
            logger.debug(f"Reference solver completed in {ref_duration:.2f}s")
        except Exception as e:
            logger.warning(f"Reference solver failed – cannot compare Stage 2: {e}")
            # If solver itself fails, we cannot grade the LLM — fall back to
            # structural validation only (does the LLM JSON at least look right?).
            s2_ok, s2_msg, s2_details = validate_stage2(llm_stage2_data)
            s2_details["reference_unavailable"] = True
            result["stage2_success"] = s2_ok
            evidence.end_stage(
                s2_ok,
                f"[STRUCTURAL ONLY – solver unavailable] {s2_msg}",
                output_data=llm_stage2_data,
                validation_details=s2_details,
            )
            evidence.end_iteration()
            return result

        # 2c. Compare LLM output to reference
        s2_ok, s2_msg, s2_details = compare_stage2_to_reference(
            llm_stage2_data,
            reference_stage2_data,
            position_tolerance_m=POSITION_TOLERANCE_M,
            motion_tolerance_m=MOTION_TOLERANCE_M,
            min_match_fraction=MIN_MATCH_FRACTION,
        )
        s2_details["reference_stage2"] = {
            "component_count": len(reference_stage2_data.get("optimized_components", [])),
            "status": reference_stage2_data.get("status"),
        }

        result["stage2_success"] = s2_ok
        evidence.end_stage(
            s2_ok, s2_msg,
            output_data={"llm_output": llm_stage2_data,
                         "reference_output": reference_stage2_data},
            validation_details=s2_details,
        )

    # ── STAGE 3: Not applicable for Naïve LLM (always 0) ─────────
    #
    # The LLM has no mechanism to:
    #   • resolve absolute MJCF/URDF paths on disk
    #   • build a Genesis physics scene
    #   • execute a 6-phase pick-and-place trajectory
    #
    # Stage 3 is therefore always recorded as FAIL for the Naïve LLM
    # baseline.  This is the expected result and is consistent with the
    # paper's claim that tool-less baselines cannot complete the full
    # end-to-end pipeline.
    # ─────────────────────────────────────────────────────────────
    evidence.start_stage("3")
    evidence.end_stage(
        False,
        "Not applicable – Naïve LLM cannot execute Genesis simulation (Stage 3 always 0)",
        validation_details={
            "scene_built": False,
            "trajectory_success": False,
            "phases_completed": 0,
            "reason": (
                "Zero-shot LLM has no tools to resolve asset paths, build a "
                "physics scene, or drive the Genesis simulator trajectory."
            ),
        },
    )
    # Stage 3 is always 0: result["stage3_success"] remains False

    evidence.log_llm_usage(total_api_calls, total_prompt_tok, total_completion_tok)
    evidence.end_iteration()
    return result


def run_pipeline(
    prompts: list,
    config: ComparisonConfig = None,
    start_id: int = 0,
    resume_from=None,
) -> EvidenceLogger:
    """
    Run the full naive LLM pipeline across all prompts.

    Args:
        prompts: List of TestPrompt instances.
        config: Comparison config; uses default if None.
        start_id: Iteration ID offset for batched runs (e.g. 20 → IDs start at 21).
        resume_from: Path to a prior JSON log to merge statistics from.

    Returns:
        EvidenceLogger with all results.
    """
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
