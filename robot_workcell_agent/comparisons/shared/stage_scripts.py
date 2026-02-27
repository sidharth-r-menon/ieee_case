"""
Direct script runners for Stage 2 and Stage 3.

Wraps the actual skill scripts (solve_placement.py, build_and_execute.py)
so comparison pipelines can call them deterministically with proper I/O.
"""

import json
import subprocess
import sys
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Paths
SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def run_solve_placement(stage1_data: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    """
    Run the placement solver script directly.

    Args:
        stage1_data: Validated Stage 1 JSON.
        timeout: Timeout in seconds.

    Returns:
        Stage 2 result dict.
    """
    script_path = SKILLS_DIR / "placement_solver" / "scripts" / "solve_placement.py"
    if not script_path.exists():
        return {"error": f"Script not found: {script_path}", "status": "error"}

    input_json = json.dumps(stage1_data)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            return {
                "error": f"Script exited with code {result.returncode}",
                "stderr": result.stderr[:500],
                "status": "error",
            }

        return json.loads(result.stdout)

    except subprocess.TimeoutExpired:
        return {"error": "Timeout", "status": "error"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON output", "stdout": result.stdout[:300], "status": "error"}
    except Exception as e:
        return {"error": str(e), "status": "error"}


def run_genesis_build_and_execute(genesis_input: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
    """
    Run the genesis build_and_execute script directly.

    Args:
        genesis_input: Prepared genesis input with fixed paths.
        timeout: Timeout in seconds (genesis is slow).

    Returns:
        Stage 3 result dict.
    """
    script_path = SKILLS_DIR / "genesis_scene_builder" / "scripts" / "build_and_execute.py"
    if not script_path.exists():
        return {"error": f"Script not found: {script_path}", "status": "error"}

    input_json = json.dumps(genesis_input)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Genesis outputs JSON to stdout
        if result.stdout.strip():
            return json.loads(result.stdout)
        return {
            "error": f"No stdout. Exit code: {result.returncode}",
            "stderr": result.stderr[:500],
            "status": "error",
        }

    except subprocess.TimeoutExpired:
        return {"error": "Genesis timeout", "status": "error"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from genesis", "status": "error"}
    except Exception as e:
        return {"error": str(e), "status": "error"}


def prepare_genesis_input(
    stage1_data: Dict[str, Any],
    stage2_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merge Stage 1 + Stage 2 into genesis input (same logic as skill_toolset.prepare_genesis_input).

    Args:
        stage1_data: Validated Stage 1 JSON.
        stage2_data: Stage 2 placement solver output.

    Returns:
        Genesis input dict ready for fix_genesis_paths.
    """
    components = []
    robot_selection = stage1_data.get("robot_selection", {})
    stage1_components = stage1_data.get("workcell_components", [])
    optimized_components = stage2_data.get("optimized_components", [])
    optimized_dict = {comp["name"]: comp for comp in optimized_components}

    # Find pedestal and conveyor info
    pedestal_pos = [0.0, 0.0, 0.0]
    pedestal_height = 0.5
    conveyor_pos = [0.5, 0.0, 0.0]
    conveyor_height = 0.82

    for opt in optimized_components:
        ct = (opt.get("component_type") or "").lower()
        cn = (opt.get("name") or "").lower()
        if "pedestal" in ct or "pedestal" in cn:
            pedestal_pos = opt.get("position", pedestal_pos)
            pedestal_height = opt.get("dimensions", [0.6, 0.6, 0.5])[2]
        elif "conveyor" in ct or "conveyor" in cn:
            conveyor_pos = opt.get("position", conveyor_pos)
            conveyor_height = opt.get("dimensions", [2.0, 0.64, 0.82])[2]

    # 1. Robot on top of pedestal
    if robot_selection:
        components.append({
            "name": "robot",
            "component_type": "robot",
            "urdf": robot_selection.get("urdf_path", ""),
            "position": [pedestal_pos[0], pedestal_pos[1], pedestal_height],
            "orientation": [0, 0, 0],
            "dimensions": [0.1, 0.1, 0.5],
        })

    # 2. Optimized components
    for opt in optimized_components:
        c = opt.copy()
        if "mjcf_path" in c:
            c["urdf"] = c.pop("mjcf_path")
        if "urdf" not in c:
            for s1c in stage1_components:
                if s1c.get("name") == c.get("name"):
                    c["urdf"] = s1c.get("mjcf_path", "")
                    break
        components.append(c)

    # 3. Carton / objects not in Stage 2
    for comp in stage1_components:
        name = comp.get("name")
        ct = (comp.get("component_type") or "").lower()
        if name in optimized_dict:
            continue
        if ct in ["robot", "manipulator", "arm", "gripper"]:
            continue
        is_carton = any(kw in ct for kw in ["carton", "box", "object", "item", "bottle"])
        if is_carton:
            pos = [conveyor_pos[0], conveyor_pos[1], conveyor_height + 0.02]
        else:
            dims = comp.get("dimensions", [0.5, 0.5, 0.5])
            pos = [0, 0, dims[2] / 2]
        components.append({
            "name": name,
            "component_type": comp.get("component_type", ""),
            "urdf": comp.get("mjcf_path", ""),
            "position": pos,
            "orientation": [0, 0, 0],
            "dimensions": comp.get("dimensions", [0.5, 0.5, 0.5]),
        })

    return {
        "components": components,
        "robot_info": robot_selection,
        "task_objective": stage1_data.get("task_objective", ""),
        "execute_trajectory": True,
        "motion_targets": stage2_data.get("motion_targets", {}),
        "z_lift": 0.4,
    }


def fix_genesis_paths(genesis_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix component paths using the same catalog as skill_toolset.fix_genesis_paths.

    Args:
        genesis_input: Output from prepare_genesis_input.

    Returns:
        Genesis input with resolved absolute paths.
    """
    CATALOG = {
        "franka_panda": str(PROJECT_ROOT / "mujoco_menagerie/franka_emika_panda/panda.xml"),
        "panda": str(PROJECT_ROOT / "mujoco_menagerie/franka_emika_panda/panda.xml"),
        "ur5": str(PROJECT_ROOT / "mujoco_menagerie/universal_robots_ur5e/ur5e.xml"),
        "ur5e": str(PROJECT_ROOT / "mujoco_menagerie/universal_robots_ur5e/ur5e.xml"),
        "ur10": str(PROJECT_ROOT / "mujoco_menagerie/universal_robots_ur10e/ur10e.xml"),
        "ur10e": str(PROJECT_ROOT / "mujoco_menagerie/universal_robots_ur10e/ur10e.xml"),
        "conveyor": str(PROJECT_ROOT / "workcell_components/conveyors/conveyor_belt.xml"),
        "conveyor_belt": str(PROJECT_ROOT / "workcell_components/conveyors/conveyor_belt.xml"),
        "pedestal": str(PROJECT_ROOT / "workcell_components/pedestals/robot_pedestal.xml"),
        "robot_pedestal": str(PROJECT_ROOT / "workcell_components/pedestals/robot_pedestal.xml"),
        "pallet": str(PROJECT_ROOT / "workcell_components/pallets/euro_pallet.xml"),
        "euro_pallet": str(PROJECT_ROOT / "workcell_components/pallets/euro_pallet.xml"),
        "carton": str(PROJECT_ROOT / "workcell_components/boxes/cardboard_box.xml"),
        "cardboard_box": str(PROJECT_ROOT / "workcell_components/boxes/cardboard_box.xml"),
        "box": str(PROJECT_ROOT / "workcell_components/boxes/medium_box.xml"),
    }

    def resolve(name: str, comp_type: str, robot_model: str = "") -> str:
        nl = name.lower().replace(" ", "_").replace("-", "_")
        tl = comp_type.lower()
        if robot_model:
            mk = robot_model.lower().replace(" ", "_").replace("-", "_")
            if mk in CATALOG:
                return CATALOG[mk]
        if nl in CATALOG:
            return CATALOG[nl]
        if tl in CATALOG:
            return CATALOG[tl]
        for kw in ["conveyor", "pallet", "pedestal", "carton", "box"]:
            if kw in nl or kw in tl:
                if kw in CATALOG:
                    return CATALOG[kw]
        return ""

    components = genesis_input.get("components", [])
    robot_info = genesis_input.get("robot_info", {})

    for comp in components:
        ct = (comp.get("component_type") or "").lower()
        rm = robot_info.get("model", "") if ct == "robot" else ""
        new_path = resolve(comp.get("name", ""), ct, rm)
        if new_path and os.path.exists(new_path):
            comp["urdf"] = new_path

    return genesis_input
