"""
LangChain tool definitions for the comparison pipeline.

Wraps the skill scripts and reference documents as LangChain tools.
The agent has RAG-style access to all reference docs + tool calling,
but NO domain-specific state machine or progressive disclosure.
"""

import json
import subprocess
import sys
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"


def get_tool_definitions() -> list:
    """
    Return LangChain-compatible tool definitions.

    These mirror the skill scripts but are exposed as flat tools
    with NO progressive disclosure and NO state machine.
    """
    from langchain_core.tools import tool

    # ── Reference Document Tools (RAG) ───────────────────────────

    @tool
    def read_gap_analysis_guide() -> str:
        """Read the gap analysis reference guide for workcell design requirements.
        Use this to understand what information is needed for a complete design."""
        path = SKILLS_DIR / "request_interpreter" / "references" / "gap_analysis_guide.md"
        if path.exists():
            return path.read_text(encoding="utf-8")[:5000]
        return "Guide not found."

    @tool
    def read_standard_objects_guide() -> str:
        """Read the standard objects reference guide with dimensions for common
        workcell components like pallets, conveyors, boxes, etc."""
        path = SKILLS_DIR / "request_interpreter" / "references" / "standard_objects.md"
        if path.exists():
            return path.read_text(encoding="utf-8")[:5000]
        return "Guide not found."

    @tool
    def read_robot_selection_guide() -> str:
        """Read the robot selection reference guide to choose the right robot
        based on payload, reach, and task requirements."""
        path = SKILLS_DIR / "request_interpreter" / "references" / "robot_selection_guide.md"
        if path.exists():
            return path.read_text(encoding="utf-8")[:5000]
        return "Guide not found."

    # ── Stage 2 Tool ─────────────────────────────────────────────

    @tool
    def run_placement_solver(stage1_json: str) -> str:
        """Run the placement solver to calculate optimal positions for workcell
        components. Input: Stage 1 JSON as a string. Output: optimized layout JSON."""
        script = SKILLS_DIR / "placement_solver" / "scripts" / "solve_placement.py"
        if not script.exists():
            return json.dumps({"error": "Script not found"})
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                input=stage1_json,
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                return result.stdout
            return json.dumps({"error": f"Exit code {result.returncode}", "stderr": result.stderr[:300]})
        except Exception as e:
            return json.dumps({"error": str(e)})

    # ── Stage 3 Tool ─────────────────────────────────────────────

    @tool
    def run_genesis_simulation(genesis_input_json: str) -> str:
        """Submit the Genesis simulation scene for execution.
        Input: prepared genesis JSON string with keys: components, robot_info, task_objective,
        execute_trajectory, motion_targets, z_lift.
        Output: acknowledgement that the simulation has been queued."""
        return json.dumps({
            "status": "queued",
            "message": "Genesis simulation queued for execution. Input received.",
        })

    # ── Stage 1 Validation Tool ──────────────────────────────────

    @tool
    def validate_stage1_json(stage1_json: str) -> str:
        """Validate a Stage 1 JSON against the required schema.
        Input: Stage 1 JSON as a string.
        Returns a simple pass/fail result. Fix any reported errors and retry."""

        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from comparisons.shared.validators import validate_stage1

        try:
            data = json.loads(stage1_json)
        except Exception as e:
            return json.dumps({"valid": False, "error": f"JSON parse error: {str(e)[:200]}"})

        try:
            success, msg, details = validate_stage1(data)
            return json.dumps({"valid": success, "message": msg, "details": details})
        except Exception as e:
            return json.dumps({"valid": False, "error": str(e)[:500]})

    return [
        read_gap_analysis_guide,
        read_standard_objects_guide,
        read_robot_selection_guide,
        run_placement_solver,
        run_genesis_simulation,
        validate_stage1_json,
    ]


# Tool names by expected stage for hit/miss tracking
EXPECTED_TOOLS_BY_STAGE = {
    "1": {"read_gap_analysis_guide", "read_standard_objects_guide",
           "read_robot_selection_guide", "validate_stage1_json"},
    "2": {"run_placement_solver"},
    "3": {"run_genesis_simulation"},
}
