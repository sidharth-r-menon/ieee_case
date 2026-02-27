"""
Stage-level validators for evaluating pipeline outputs.

Validates Stage 1 JSON against the Pydantic schema, Stage 2 placement
solver output, and Stage 3 genesis/trajectory output.
"""

import json
import logging
import math
import hashlib
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Import the canonical schema from parent project
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.schemas import Stage1Output


# ── Stage 1 Validation ──────────────────────────────────────────────

# Valid top-level path roots for mjcf_path fields.
# Paths that do not start with one of these segments are rejected.
_VALID_MJCF_ROOTS: set = {
    "workcell_components",   # all environment components
    "mujoco_menagerie",      # robot models from the menagerie
    # Common robot sub-directory names accepted at the top level too:
    "universal_robots_ur5e",
    "universal_robots_ur10e",
    "franka_emika_panda",
    "franka_fr3",
    "ufactory_lite6",
    "ufactory_xarm7",
    "kinova_gen3",
    "kuka_iiwa_14",
    "rethink_robotics_sawyer",
}

# Tolerance for throughput consistency check (fractional, 0.10 = ±10 %).
# ±10 % is strict enough to catch agents that copy throughput numbers without
# computing their mathematical relationship (3600 / items_per_hour), while
# allowing for small rounding differences in careful implementations.
_THROUGHPUT_TOLERANCE = 0.10


def validate_stage1(stage1_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate Stage 1 output against Pydantic schema PLUS four semantic rules.

    Pass requires ALL six conditions:

    1. Pydantic schema valid (Stage1Output.model_validate succeeds).

    2. Throughput consistency – cycle_time_seconds must be within ±10 % of
       the value implied by items_per_hour  (3600 / items_per_hour).
       Catches LLMs that fill in throughput numbers without reasoning about
       their relationship.

    3. Payload adequacy – robot_selection.payload_kg must be ≥
       task_specification.weight_kg.  A robot cannot safely lift an object
       heavier than its rated payload.

    4. All four required component types present –
       pedestal + conveyor/belt + pallet + target object (carton/box/…).
       A complete palletizing cell needs all four.

    5. mjcf_path root namespace – every path must start with 'workcell_components/'
       or a known robot directory name.  Absolute paths and invented namespaces
       are rejected.

    6. Spatial reasoning zone completeness – spatial_reasoning.zones must
       contain at least 2 zones, with at least one pickup/input zone and one
       placement/output zone.  A single generic zone is insufficient for a
       production-grade specification.

    Returns:
        (success, message, details_dict)
    """
    details: Dict[str, Any] = {
        # ── Pydantic ────────────────────────────────────────────────────
        "schema_valid": False,
        # ── Component inventory ─────────────────────────────────────────
        "has_robot": False,
        "has_components": False,
        "component_count": 0,
        "has_dimensions": False,
        "has_pedestal": False,
        "has_conveyor_or_input": False,
        "has_pallet_or_output": False,
        "has_carton_or_object": False,
        "robot_model": None,
        # ── Strict semantic checks ───────────────────────────────────────
        "throughput_consistent": None,   # True/False/None(not checked)
        "throughput_items_per_hour": None,
        "throughput_cycle_time_s": None,
        "throughput_expected_cycle_s": None,
        "throughput_error_pct": None,
        "payload_adequate": None,        # True/False/None
        "robot_payload_kg": None,
        "object_weight_kg": None,
        "has_all_required_components": False,
        "mjcf_paths_valid": None,        # True/False/None
        "mjcf_invalid_paths": [],
        # ── Error accumulator ───────────────────────────────────────────
        "errors": [],
    }

    if not stage1_data or not isinstance(stage1_data, dict):
        return False, "Stage 1 output is empty or not a dict", details

    # ── Check 1: Pydantic schema ─────────────────────────────────────
    try:
        Stage1Output.model_validate(stage1_data)
        details["schema_valid"] = True
    except Exception as e:
        details["errors"].append(f"Schema: {str(e)[:300]}")

    # ── Shared inventory (used by checks 3–5) ────────────────────────
    robot = stage1_data.get("robot_selection") or {}
    if robot.get("model"):
        details["has_robot"] = True
        details["robot_model"] = robot["model"]

    components: List[Dict] = stage1_data.get("workcell_components") or []
    details["component_count"] = len(components)
    details["has_components"] = len(components) > 0

    for comp in components:
        ct = (comp.get("component_type") or "").lower()
        cn = (comp.get("name") or "").lower()
        dims = comp.get("dimensions") or []

        if dims and len(dims) == 3 and all(isinstance(d, (int, float)) and d > 0 for d in dims):
            details["has_dimensions"] = True

        if "pedestal" in ct or "pedestal" in cn:
            details["has_pedestal"] = True
        if "conveyor" in ct or "conveyor" in cn or "belt" in ct:
            details["has_conveyor_or_input"] = True
        if "pallet" in ct or "pallet" in cn:
            details["has_pallet_or_output"] = True
        if any(kw in ct or kw in cn for kw in [
            "carton", "box", "object", "item", "bottle", "product", "package",
            "workpiece", "part", "bin", "tray", "container", "load", "goods",
            "sku", "payload", "parcel", "crate", "case",
        ]):
            details["has_carton_or_object"] = True

    # ── Check 2: Throughput consistency ──────────────────────────────
    throughput = stage1_data.get("throughput_requirement") or {}
    iph = throughput.get("items_per_hour")
    cts = throughput.get("cycle_time_seconds")

    if iph and cts and isinstance(iph, (int, float)) and isinstance(cts, (int, float)) and iph > 0 and cts > 0:
        details["throughput_items_per_hour"] = float(iph)
        details["throughput_cycle_time_s"] = float(cts)
        expected = 3600.0 / iph
        details["throughput_expected_cycle_s"] = round(expected, 2)
        error_pct = abs(cts - expected) / expected
        details["throughput_error_pct"] = round(error_pct * 100, 1)
        if error_pct <= _THROUGHPUT_TOLERANCE:
            details["throughput_consistent"] = True
        else:
            details["throughput_consistent"] = False
            details["errors"].append(
                f"Throughput inconsistency: {iph:.0f} items/hr implies "
                f"{expected:.1f}s cycle but got {cts}s "
                f"(error {error_pct*100:.0f}% > {_THROUGHPUT_TOLERANCE*100:.0f}% tolerance)"
            )
    else:
        # If either value is absent or zero, treat as inconsistent (LLM should
        # always produce both fields since the schema requires them).
        details["throughput_consistent"] = False
        details["errors"].append(
            "Throughput missing or zero: both items_per_hour and cycle_time_seconds are required"
        )

    # ── Check 3: Payload adequacy ────────────────────────────────────
    robot_payload = robot.get("payload_kg")
    task_spec = stage1_data.get("task_specification") or {}
    obj_weight = task_spec.get("weight_kg")

    if robot_payload and obj_weight and isinstance(robot_payload, (int, float)) and isinstance(obj_weight, (int, float)):
        details["robot_payload_kg"] = float(robot_payload)
        details["object_weight_kg"] = float(obj_weight)
        if robot_payload >= obj_weight:
            details["payload_adequate"] = True
        else:
            details["payload_adequate"] = False
            details["errors"].append(
                f"Payload inadequate: robot rated {robot_payload} kg but object weighs {obj_weight} kg"
            )
    else:
        # Missing payload or weight → cannot verify → treat as failure
        details["payload_adequate"] = False
        details["errors"].append(
            "Payload check skipped: robot payload_kg or task weight_kg missing"
        )

    # ── Check 4: All four required component types ───────────────────
    all_four = (
        details["has_pedestal"]
        and details["has_conveyor_or_input"]
        and details["has_pallet_or_output"]
        and details["has_carton_or_object"]
    )
    details["has_all_required_components"] = all_four
    if not all_four:
        missing = [
            label
            for flag, label in [
                (details["has_pedestal"], "pedestal"),
                (details["has_conveyor_or_input"], "conveyor/belt"),
                (details["has_pallet_or_output"], "pallet"),
                (details["has_carton_or_object"], "target object (carton/box)"),
            ]
            if not flag
        ]
        details["errors"].append(f"Missing required component types: {missing}")

    # ── Check 6: Spatial reasoning zone completeness ─────────────────────
    # A complete workcell design must identify at least 2 distinct functional
    # zones (e.g. a pickup zone and a placement zone). A single generic zone
    # is insufficient for a production-grade specification.
    spatial = stage1_data.get("spatial_reasoning") or {}
    zones: List[Dict] = spatial.get("zones") or []
    zone_types = [str(z.get("zone_type") or "").lower().strip() for z in zones]
    distinct_zone_types = set(zt for zt in zone_types if zt)
    has_pickup_zone = any(
        any(kw in zt for kw in ["pick", "input", "source", "conveyor", "feed"])
        for zt in distinct_zone_types
    )
    has_placement_zone = any(
        any(kw in zt for kw in ["place", "drop", "output", "pallet", "stack", "deposit"])
        for zt in distinct_zone_types
    )
    zone_complete = len(zones) >= 2 and has_pickup_zone and has_placement_zone
    details["spatial_zones_count"] = len(zones)
    details["spatial_zone_complete"] = zone_complete
    if not zone_complete:
        if len(zones) < 2:
            details["errors"].append(
                f"Spatial reasoning incomplete: only {len(zones)} zone(s) defined; "
                "need at least one pickup zone and one placement zone"
            )
        else:
            missing_zt = []
            if not has_pickup_zone:
                missing_zt.append("pickup/input zone")
            if not has_placement_zone:
                missing_zt.append("placement/output zone")
            details["errors"].append(
                f"Spatial reasoning missing required zone types: {missing_zt}. "
                f"Found zone types: {list(distinct_zone_types)}"
            )

    # ── Check 5: mjcf_path root namespace ──────────────────────────────
    # Every path must start with a known top-level directory and end with .xml.
    # This rejects invented namespaces ('assets/', bare filenames) but accepts
    # any filename under a valid root.  Absolute Windows/Unix paths are
    # normalised by extracting the suffix from the first known root segment —
    # this prevents platform-specific path prefixes (e.g. 'D:/GitHub/ieee_case/')
    # from penalising otherwise correct answers.
    invalid_paths: List[str] = []
    for comp in components:
        path: str = (comp.get("mjcf_path") or "").replace("\\", "/").strip()
        if not path:
            invalid_paths.append(f"<empty> [{comp.get('name', '?')}]")
            continue
        # Normalise: if path is absolute or contains a known root somewhere
        # deeper in the string, extract from that root onwards.
        normalised = path
        for root_candidate in _VALID_MJCF_ROOTS:
            idx = path.lower().find(root_candidate + "/")
            if idx > 0:  # found after the start → strip prefix
                normalised = path[idx:]
                break
        root = normalised.split("/")[0].lower()
        if root not in _VALID_MJCF_ROOTS:
            invalid_paths.append(path)  # log original path for clarity

    details["mjcf_invalid_paths"] = invalid_paths
    if invalid_paths:
        details["mjcf_paths_valid"] = False
        details["errors"].append(
            f"Invalid mjcf_path root(s) – must start with 'workcell_components/' "
            f"or a known robot directory: {invalid_paths[:3]}"
        )
    else:
        details["mjcf_paths_valid"] = True

    # ── Final gate: ALL six checks must pass ────────────────────────
    success = (
        details["schema_valid"]
        and details["throughput_consistent"] is True
        and details["payload_adequate"] is True
        and details["has_all_required_components"]
        and details["mjcf_paths_valid"] is True
        and details["spatial_zone_complete"] is True
    )

    if success:
        msg = "Stage 1 validated successfully (schema + 4 semantic checks)"
    else:
        failed = [e for e in details["errors"]]
        msg = "Stage 1 failed: " + "; ".join(failed[:3])
        if len(failed) > 3:
            msg += f" (+{len(failed)-3} more)"

    return success, msg, details


def validate_stage1_vs_prompt(
    stage1_data: Dict[str, Any],
    expected_robot: str,
    expected_components: List[str],
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Cross-check Stage 1 JSON content against what the test prompt explicitly
    requested.  Used to tighten Stage 2 success: passing the solver is not
    enough if the agent selected the wrong robot or forgot required components.

    Checks:
    1. Robot model – stage1 robot_selection.model must contain
       expected_robot (case-insensitive substring match).
    2. Component coverage – for every keyword in expected_components, at least
       one Stage 1 component must contain that keyword in its component_type
       or name (case-insensitive).

    Args:
        stage1_data:         The Stage 1 JSON dict produced by the pipeline.
        expected_robot:      Lower-case robot keyword from the test prompt
                             (e.g. "ur5", "ur5e", "ur10e").
        expected_components: Keywords the prompt requires
                             (e.g. ["pedestal", "conveyor", "pallet", "carton"]).

    Returns:
        (success, message, details_dict)
    """
    details: Dict[str, Any] = {
        "expected_robot": expected_robot,
        "actual_robot_model": None,
        "robot_matches": False,
        "expected_components": list(expected_components),
        "missing_components": [],
        "errors": [],
    }

    if not stage1_data or not isinstance(stage1_data, dict):
        return False, "Stage 1 data is empty or not a dict", details

    # ── Check 1: Robot model ─────────────────────────────────────────
    robot = stage1_data.get("robot_selection") or {}
    actual_model: str = (robot.get("model") or "").lower().strip()
    details["actual_robot_model"] = actual_model
    expected_lc = expected_robot.lower().strip()

    if expected_lc and (expected_lc in actual_model or actual_model in expected_lc):
        details["robot_matches"] = True
    else:
        details["robot_matches"] = False
        details["errors"].append(
            f"Robot mismatch: prompt requires '{expected_robot}' "
            f"but Stage 1 selected '{actual_model}'"
        )

    # ── Check 2: Required component coverage ─────────────────────────
    components: List[Dict] = stage1_data.get("workcell_components") or []
    all_labels: List[str] = []
    for comp in components:
        ct = (comp.get("component_type") or "").lower()
        cn = (comp.get("name") or "").lower()
        all_labels.append(f"{ct} {cn}".strip())

    missing: List[str] = []
    for keyword in expected_components:
        kw_lc = keyword.lower()
        found = any(kw_lc in label for label in all_labels)
        if not found:
            missing.append(keyword)

    details["missing_components"] = missing
    if missing:
        details["errors"].append(
            f"Missing required components: {missing}"
        )

    success = details["robot_matches"] and not missing
    if success:
        msg = (
            f"Stage 1 matches prompt requirements "
            f"(robot='{actual_model}', all {len(expected_components)} component types present)"
        )
    else:
        msg = "Stage 1 vs prompt check failed: " + "; ".join(details["errors"])

    return success, msg, details


# ── Stage 2 Validation ──────────────────────────────────────────────


def validate_stage2(stage2_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate Stage 2 placement solver output.

    Returns:
        (success, message, details_dict)
    """
    details = {
        "status_success": False,
        "has_components": False,
        "component_count": 0,
        "has_motion_targets": False,
        "has_pick_target": False,
        "has_place_target": False,
        "positions_valid": False,
        "all_positions_nonzero": False,
        "errors": [],
    }

    if not stage2_data or not isinstance(stage2_data, dict):
        return False, "Stage 2 output is empty or not a dict", details

    if stage2_data.get("status") == "success":
        details["status_success"] = True
    elif "error" in stage2_data:
        details["errors"].append(stage2_data.get("error", "unknown"))

    # Check optimized components
    opt_comps = stage2_data.get("optimized_components", [])
    details["component_count"] = len(opt_comps)
    details["has_components"] = len(opt_comps) > 0

    # Check positions are valid (not all zeros, not None)
    positions_ok = True
    for comp in opt_comps:
        pos = comp.get("position")
        if pos is None or (not isinstance(pos, list)):
            positions_ok = False
        elif len(pos) != 3:
            positions_ok = False
    details["positions_valid"] = positions_ok and len(opt_comps) > 0

    # Check motion targets
    mt = stage2_data.get("motion_targets", {})
    details["has_motion_targets"] = bool(mt)

    # Require both pick AND place targets to be present
    details["has_pick_target"] = "pick_target_xyz" in mt
    details["has_place_target"] = "place_target_xyz" in mt
    has_both_targets = details["has_pick_target"] and details["has_place_target"]

    # Require that at least some components have non-zero positions.
    # The robot base is legitimately at [0,0,0], but other components
    # (conveyor, pallet, pedestal) should be placed away from the origin.
    zero_position_count = 0
    for comp in opt_comps:
        pos = comp.get("position")
        if pos and len(pos) == 3 and all(v == 0 for v in pos):
            zero_position_count += 1
    # Fail only if EVERY component is at origin – solver must have placed something
    all_pos_nonzero = zero_position_count < len(opt_comps)
    details["all_positions_nonzero"] = all_pos_nonzero

    # ── Layout spread check ─────────────────────────────────────────────────
    # Pick and place targets must be physically separated (a workcell where
    # conveyor and pallet are co-located is geometrically infeasible).
    # Pick target must be at a plausible conveyor height (z > 0.3 m above floor).
    pick_xyz = mt.get("pick_target_xyz")
    place_xyz = mt.get("place_target_xyz")
    layout_spread_ok = True
    spread_error = None
    if pick_xyz and place_xyz and len(pick_xyz) == 3 and len(place_xyz) == 3:
        pick_place_dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(pick_xyz, place_xyz)))
        pick_z = pick_xyz[2]
        if pick_place_dist < 0.8:
            layout_spread_ok = False
            spread_error = (
                f"Pick/place distance {pick_place_dist:.2f} m is too small "
                "(minimum 0.8 m required – conveyor and pallet must be spatially separated)"
            )
        elif pick_z < 0.3:
            layout_spread_ok = False
            spread_error = (
                f"Pick target z={pick_z:.2f} m is below plausible conveyor height "
                "(minimum 0.3 m above floor required)"
            )
    details["layout_spread_ok"] = layout_spread_ok
    if not layout_spread_ok and spread_error:
        details["errors"].append(spread_error)

    success = (
        details["status_success"]
        and details["has_components"]
        and details["positions_valid"]
        and has_both_targets
        and details["all_positions_nonzero"]
        and layout_spread_ok
    )
    if not success:
        reasons = []
        if not details["status_success"]: reasons.append("solver status != success")
        if not details["has_components"]: reasons.append("no optimized components")
        if not details["positions_valid"]: reasons.append("invalid component positions")
        if not has_both_targets: reasons.append("missing pick or place target")
        if not details.get("all_positions_nonzero"): reasons.append("all-zero component positions")
        if not layout_spread_ok: reasons.append(spread_error or "layout spread check failed")
        details["errors"].extend(reasons)
    msg = "Stage 2 validated" if success else f"Stage 2 failed: {'; '.join(details['errors'][:3])}"
    return success, msg, details


# ── Stage 3 Validation ──────────────────────────────────────────────


def validate_stage3(stage3_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate Stage 3 genesis build + trajectory output.

    Returns:
        (success, message, details_dict)
    """
    details = {
        "scene_built": False,
        "trajectory_executed": False,
        "trajectory_success": False,
        "phases_completed": 0,
        "robot_available": False,
        "spawned_count": 0,
        "errors": [],
    }

    if not stage3_data or not isinstance(stage3_data, dict):
        return False, "Stage 3 output is empty or not a dict", details

    details["scene_built"] = stage3_data.get("success", False)
    details["robot_available"] = stage3_data.get("robot_available", False)
    details["spawned_count"] = len(stage3_data.get("spawned_components", []))
    details["trajectory_executed"] = stage3_data.get("trajectory_executed", False)
    details["trajectory_success"] = stage3_data.get("trajectory_status") == "success"
    details["phases_completed"] = stage3_data.get("phases_completed", 0)

    if "error" in stage3_data:
        details["errors"].append(str(stage3_data["error"])[:200])

    success = details["scene_built"] and details["trajectory_success"] and details["phases_completed"] == 6
    msg = "Stage 3 validated" if success else f"Stage 3 incomplete: {details['phases_completed']}/6 phases"
    return success, msg, details


# ── Stage 3 Dry-Run Validation (no Genesis needed) ──────────────────

# Project root – validators.py is at <project_root>/robot_workcell_agent/comparisons/shared/
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def validate_stage3_agent_submission(raw_genesis: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate the genesis JSON that the agent built and submitted to run_genesis_simulation,
    BEFORE any path-fixing is applied.

    This tests whether the LangChain agent correctly assembled the genesis input.
    Component paths (pedestal, conveyor, pallet) are NOT checked because those paths
    are not listed in any reference guide the agent has access to.
    The ROBOT path IS checked because the robot_selection_guide documents exact paths.

    Pass requires ALL of:
      1. 'components' list present with ≥ 3 entries (robot + at least 2 workcell parts).
      2. Exactly one component with component_type == 'robot' present.
      3. execute_trajectory == True and motion_targets dict with both pick/place keys.
      4. The robot component's 'urdf' path exists on disk.
         (Agents receive exact robot paths from read_robot_selection_guide.)
      5. All components have valid 3-element position lists with at least one non-origin.

    Returns:
        (success, message, details_dict)
    """
    details: Dict[str, Any] = {
        "has_components": False,
        "has_robot": False,
        "has_trajectory_params": False,
        "has_both_motion_targets": False,
        "component_count": 0,
        "robot_path_valid": False,
        "robot_urdf": None,
        "positions_valid": False,
        "errors": [],
    }

    if not raw_genesis or not isinstance(raw_genesis, dict):
        return False, "Agent genesis submission is empty or not a dict", details

    # Detect if agent passed Stage 2 data directly (skipped prepare step)
    if "optimized_components" in raw_genesis and "components" not in raw_genesis:
        details["errors"].append(
            "Agent passed Stage 2 data directly without assembling genesis input"
        )
        return False, "Genesis input structure invalid – missing 'components' key", details

    components = raw_genesis.get("components", [])
    details["component_count"] = len(components)
    details["has_components"] = len(components) >= 3  # robot + at least 2 workcell components

    # Check robot component and its path
    robot_comp = None
    for comp in components:
        ct = (comp.get("component_type") or "").lower()
        if ct == "robot":
            details["has_robot"] = True
            robot_comp = comp
            break

    if robot_comp:
        urdf: str = (robot_comp.get("urdf") or robot_comp.get("mjcf_path") or "").replace("\\", "/").strip()
        details["robot_urdf"] = urdf
        if urdf:
            candidate = Path(urdf)
            if not candidate.is_absolute():
                candidate = _PROJECT_ROOT / urdf
            details["robot_path_valid"] = candidate.exists()
        if not details["robot_path_valid"]:
            details["errors"].append(
                f"Robot urdf path does not exist: '{urdf}'. "
                "Use the exact path from read_robot_selection_guide "
                "(e.g. 'mujoco_menagerie/universal_robots_ur5e/ur5e.xml')"
            )

    # Check trajectory params
    mt = raw_genesis.get("motion_targets") or {}
    has_pick = "pick_target_xyz" in mt
    has_place = "place_target_xyz" in mt
    details["has_both_motion_targets"] = has_pick and has_place
    details["has_trajectory_params"] = (
        raw_genesis.get("execute_trajectory", False) is True
        and details["has_both_motion_targets"]
    )

    # Check that at least some component positions are non-zero
    zero_count = 0
    pos_invalid = False
    for comp in components:
        pos = comp.get("position")
        if not pos or not isinstance(pos, list) or len(pos) != 3:
            pos_invalid = True
        elif all(v == 0 for v in pos):
            zero_count += 1
    details["positions_valid"] = (not pos_invalid) and (zero_count < len(components))

    if not details["has_components"]:
        details["errors"].append(f"Too few components: {len(components)} (need ≥ 3)")
    if not details["has_robot"]:
        details["errors"].append("No component with component_type='robot'")
    if not details["has_trajectory_params"]:
        if not raw_genesis.get("execute_trajectory", False):
            details["errors"].append("execute_trajectory must be True")
        if not details["has_both_motion_targets"]:
            details["errors"].append("motion_targets must include pick_target_xyz and place_target_xyz")
    if not details["positions_valid"]:
        details["errors"].append("Component positions are invalid or all-zero")

    success = (
        details["has_components"]
        and details["has_robot"]
        and details["robot_path_valid"]
        and details["has_trajectory_params"]
        and details["positions_valid"]
    )
    msg = (
        "Agent genesis submission valid"
        if success
        else f"Agent genesis invalid: {'; '.join(details['errors'][:2])}"
    )
    return success, msg, details


def validate_stage3_input(genesis_input: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate the input that WOULD be sent to genesis (dry-run).
    Checks that all components have valid paths, positions, etc.

    Returns:
        (success, message, details_dict)
    """
    details = {
        "has_components": False,
        "has_robot": False,
        "has_trajectory_params": False,
        "component_count": 0,
        "paths_resolved": 0,
        "paths_missing": 0,
        "errors": [],
    }

    if not genesis_input or not isinstance(genesis_input, dict):
        return False, "Genesis input is empty or not a dict", details

    # Detect if agent incorrectly passed Stage 2 data to fix_genesis_paths
    # (i.e., skipped calling prepare_genesis_input first)
    if "optimized_components" in genesis_input and "components" not in genesis_input:
        details["errors"].append(
            "stage3_skipped_prepare: agent passed Stage 2 data (optimized_components) directly "
            "to fix_genesis_paths without calling prepare_genesis_input() first"
        )
        return False, "Genesis input incomplete – prepare_genesis_input() was not called", details

    components = genesis_input.get("components", [])
    details["component_count"] = len(components)
    details["has_components"] = len(components) > 0

    for comp in components:
        ct = (comp.get("component_type") or "").lower()
        if ct == "robot":
            details["has_robot"] = True
        urdf = comp.get("urdf", "")
        if urdf and Path(urdf).exists():
            details["paths_resolved"] += 1
        else:
            details["paths_missing"] += 1

    details["has_trajectory_params"] = (
        genesis_input.get("execute_trajectory", False)
        and bool(genesis_input.get("motion_targets"))
    )

    success = (
        details["has_components"]
        and details["has_robot"]
        and details["has_trajectory_params"]
        and details["paths_missing"] <= 1  # Allow at most 1 missing (e.g. dynamic carton)
    )

    msg = "Genesis input valid" if success else "Genesis input incomplete"
    return success, msg, details


# ── Stage 2 Comparison (Naïve LLM only) ────────────────────────────


def _euclidean(a: List[float], b: List[float]) -> float:
    """Euclidean distance between two 3-D points."""
    if len(a) != 3 or len(b) != 3:
        return float("inf")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def compare_stage2_to_reference(
    llm_stage2: Dict[str, Any],
    reference_stage2: Dict[str, Any],
    position_tolerance_m: float = 0.5,
    motion_tolerance_m: float = 0.5,
    min_match_fraction: float = 0.5,
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Compare an LLM-generated Stage 2 output against the reference solver output.

    Used only by the Naïve LLM pipeline: the LLM must produce placement
    coordinates without running the actual solver script, so we validate its
    answer by comparing it to what the solver would have produced.

    PASS criteria (all must be true):
      1. llm_stage2 has a non-empty ``optimized_components`` list.
      2. llm_stage2 has non-empty ``motion_targets`` with pick/place keys.
      3. At least ``min_match_fraction`` of reference components are found in the
         LLM output (matched by name then by component_type) with a 3-D
         Euclidean position error ≤ ``position_tolerance_m``.
      4. Both ``pick_target_xyz`` and ``place_target_xyz`` are within
         ``motion_tolerance_m`` of the reference values.

    Args:
        llm_stage2: Stage 2 JSON produced by the LLM.
        reference_stage2: Stage 2 JSON produced by the deterministic solver.
        position_tolerance_m: Max acceptable positional error per component (m).
        motion_tolerance_m: Max acceptable error for pick/place targets (m).
        min_match_fraction: Fraction of reference components that must be
            within tolerance for the layout to be considered correct.

    Returns:
        (success, message, details_dict)
    """
    details: Dict[str, Any] = {
        "llm_has_components": False,
        "llm_has_motion_targets": False,
        "reference_component_count": 0,
        "matched_components": 0,
        "components_within_tolerance": 0,
        "match_fraction": 0.0,
        "pick_error_m": None,
        "place_error_m": None,
        "pick_within_tolerance": False,
        "place_within_tolerance": False,
        "component_errors": [],
        "errors": [],
        "position_tolerance_m": position_tolerance_m,
        "motion_tolerance_m": motion_tolerance_m,
    }

    # ── Structural checks on LLM output ─────────────────────────
    if not llm_stage2 or not isinstance(llm_stage2, dict):
        return False, "LLM Stage 2 output is empty or not a dict", details

    llm_comps: List[Dict] = llm_stage2.get("optimized_components", [])
    llm_mt: Dict = llm_stage2.get("motion_targets", {})
    ref_comps: List[Dict] = reference_stage2.get("optimized_components", [])

    details["llm_has_components"] = len(llm_comps) > 0
    details["llm_has_motion_targets"] = bool(llm_mt) and (
        "pick_target_xyz" in llm_mt or "place_target_xyz" in llm_mt
    )
    details["reference_component_count"] = len(ref_comps)

    if not details["llm_has_components"]:
        details["errors"].append("LLM produced no optimized_components")
        return False, "LLM Stage 2 has no components", details

    if not details["llm_has_motion_targets"]:
        details["errors"].append("LLM produced no motion_targets")

    # Build lookup of LLM components: name → comp, then type → comp
    llm_by_name: Dict[str, Dict] = {
        c.get("name", "").lower(): c for c in llm_comps if c.get("name")
    }
    llm_by_type: Dict[str, Dict] = {}
    for c in llm_comps:
        ct = (c.get("component_type") or "").lower()
        if ct and ct not in llm_by_type:
            llm_by_type[ct] = c

    # ── Per-component position comparison ───────────────────────
    within_tolerance = 0

    for ref_comp in ref_comps:
        ref_name = (ref_comp.get("name") or "").lower()
        ref_type = (ref_comp.get("component_type") or "").lower()
        ref_pos: Optional[List[float]] = ref_comp.get("position")

        if ref_pos is None or len(ref_pos) != 3:
            continue  # reference itself has no valid position — skip

        # Match by name first, then type
        llm_comp = llm_by_name.get(ref_name) or llm_by_type.get(ref_type)

        if llm_comp is None:
            details["component_errors"].append({
                "ref_name": ref_name,
                "matched": False,
                "error_m": None,
            })
            continue

        details["matched_components"] += 1
        llm_pos: Optional[List[float]] = llm_comp.get("position")

        if llm_pos is None or len(llm_pos) != 3:
            details["component_errors"].append({
                "ref_name": ref_name,
                "matched": True,
                "error_m": None,
                "within_tolerance": False,
            })
            continue

        err = _euclidean(llm_pos, ref_pos)
        ok = err <= position_tolerance_m
        if ok:
            within_tolerance += 1

        details["component_errors"].append({
            "ref_name": ref_name,
            "matched": True,
            "error_m": round(err, 3),
            "within_tolerance": ok,
        })

    details["components_within_tolerance"] = within_tolerance
    n_ref = len(ref_comps) if ref_comps else 1
    details["match_fraction"] = round(within_tolerance / n_ref, 3)

    # ── Motion targets comparison ────────────────────────────────
    ref_mt = reference_stage2.get("motion_targets", {})
    ref_pick = ref_mt.get("pick_target_xyz")
    ref_place = ref_mt.get("place_target_xyz")
    llm_pick = llm_mt.get("pick_target_xyz")
    llm_place = llm_mt.get("place_target_xyz")

    if ref_pick and llm_pick:
        err_pick = _euclidean(llm_pick, ref_pick)
        details["pick_error_m"] = round(err_pick, 3)
        details["pick_within_tolerance"] = err_pick <= motion_tolerance_m
    elif ref_pick:
        details["errors"].append("LLM missing pick_target_xyz")

    if ref_place and llm_place:
        err_place = _euclidean(llm_place, ref_place)
        details["place_error_m"] = round(err_place, 3)
        details["place_within_tolerance"] = err_place <= motion_tolerance_m
    elif ref_place:
        details["errors"].append("LLM missing place_target_xyz")

    # ── Final pass/fail decision ─────────────────────────────────
    layout_ok = details["match_fraction"] >= min_match_fraction
    motion_ok = details["pick_within_tolerance"] and details["place_within_tolerance"]
    has_targets = details["llm_has_motion_targets"]

    success = details["llm_has_components"] and layout_ok and has_targets and motion_ok

    if success:
        msg = (
            f"Stage 2 comparison PASS – {within_tolerance}/{n_ref} components "
            f"within {position_tolerance_m} m, motion targets within {motion_tolerance_m} m"
        )
    else:
        reasons = []
        if not layout_ok:
            reasons.append(
                f"only {within_tolerance}/{n_ref} components within {position_tolerance_m} m "
                f"(need ≥{min_match_fraction*100:.0f}%)"
            )
        if not has_targets:
            reasons.append("missing motion_targets")
        elif not motion_ok:
            if not details["pick_within_tolerance"]:
                reasons.append(f"pick target error {details['pick_error_m']} m > {motion_tolerance_m} m")
            if not details["place_within_tolerance"]:
                reasons.append(f"place target error {details['place_error_m']} m > {motion_tolerance_m} m")
        msg = "Stage 2 comparison FAIL – " + "; ".join(reasons)

    return success, msg, details
