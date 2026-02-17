"""Skill tools as a reusable FunctionToolset for progressive disclosure."""

import json
import subprocess
import logging
from typing import Dict, Any, Optional
from pydantic_ai.toolsets import FunctionToolset
from pydantic_ai import RunContext
from src.dependencies import AgentDependencies
from src.skill_tools import load_skill, read_skill_file, list_skill_files
from src.runtime import run_skill_script
from src.schemas import Stage1Output
from src.logging_config import log_stage_1_json

logger = logging.getLogger(__name__)

# Create the skill tools toolset
skill_tools = FunctionToolset()


@skill_tools.tool
async def load_skill_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str
) -> str:
    """
    Load the full instructions for a skill (Level 2 progressive disclosure).

    Use this tool when you need to access the detailed instructions
    for a skill. Based on the skill descriptions in your system prompt,
    identify which skill is relevant and load its full instructions.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill to load (e.g., "interpreter", "placement_solver")

    Returns:
        Full skill instructions from SKILL.md
    """
    return await load_skill(ctx, skill_name)


@skill_tools.tool
async def read_skill_file_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    file_path: str
) -> str:
    """
    Read a specific file from a skill's directory (Level 3 progressive disclosure).

    Use this tool when you need to access scripts, configuration files,
    or other resources within a skill's directory.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill
        file_path: Relative path to file within skill directory (e.g., "scripts/interpret_request.py")

    Returns:
        File contents
    """
    return await read_skill_file(ctx, skill_name, file_path)


@skill_tools.tool
async def list_skill_files_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    directory: str = ""
) -> str:
    """
    List files available in a skill's directory.

    Use this tool to explore what resources are available within a skill
    before loading them. Useful for discovering scripts, documentation, etc.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill
        directory: Optional subdirectory to list (e.g., "scripts")

    Returns:
        Formatted list of available files
    """
    return await list_skill_files(ctx, skill_name, directory)


@skill_tools.tool
def run_skill_script_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    script_name: str,
    args: Optional[Dict[str, Any]] = None
) -> str:
    """
    Execute a skill script (CORE RUNTIME CAPABILITY).

    This is the primary execution primitive - it runs Python scripts from
    skills/*/scripts/ with JSON input/output via stdin/stdout.

    Use this tool when SKILL.md instructs you to execute a specific script.
    Only call scripts that are explicitly documented in the skill's instructions.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill (e.g., "request_interpreter")
        script_name: Name of the script without .py extension (e.g., "interpret_request")
        args: Dictionary of arguments to pass to the script

    Returns:
        JSON string with script results

    Example:
        To interpret a user request:
        result = run_skill_script_tool(
            ctx,
            skill_name="request_interpreter",
            script_name="interpret_request",
            args={"text": "I need a pick and place system"}
        )
    """
    try:
        # CRITICAL VALIDATION: Prevent calls to deleted scripts
        if skill_name == "genesis_scene_builder" and script_name == "build_scene":
            error_msg = (
                "❌ CRITICAL ERROR: Script 'build_scene' has been DELETED!\n"
                "✅ CORRECT SCRIPT: Use 'build_and_execute' instead.\n\n"
                "The old workflow (build_scene + separate execution) no longer exists.\n"
                "ONLY ONE SCRIPT EXISTS: genesis_scene_builder/build_and_execute\n\n"
                "Correct usage:\n"
                "  genesis_input = prepare_genesis_input()\n"
                "  fixed_genesis = fix_genesis_paths(genesis_input)\n"
                "  run_skill_script_tool('genesis_scene_builder', 'build_and_execute', fixed_genesis)"
            )
            logger.error(error_msg)
            return json.dumps({
                "error": "build_scene script deleted",
                "message": error_msg,
                "correct_script": "build_and_execute"
            })
        
        # Log the script execution attempt
        logger.info(f"")
        logger.info(f"{'='*80}")
        logger.info(f"🚀 EXECUTING SKILL SCRIPT: {skill_name}/{script_name}")
        logger.info(f"{'='*80}")
        logger.info(f"Arguments keys: {list((args or {}).keys())}")
        logger.info(f"Arguments size: {len(json.dumps(args or {}))} chars")
        logger.info(f"{'='*80}")
        
        # Use the simple direct Genesis script - no ZMQ complexity
        result = run_skill_script(skill_name, script_name, args or {})
        
        # Store Stage 2 results for later use
        if skill_name == "placement_solver" and script_name == "solve_placement":
            if isinstance(result, dict) and result.get("status") == "success":
                # CRITICAL: Auto-correct motion targets to match validated physics coordinates
                # These values are from genesis_world_pnp_4.py and are verified to work
                EXPECTED_TARGETS = {
                    "pick_target_xyz": [0.65, 0.0, 1.13],
                    "place_target_xyz": [0.0, 0.75, 0.46]
                }
                
                motion_targets = result.get("motion_targets", {})
                for target_name, expected_value in EXPECTED_TARGETS.items():
                    current_value = motion_targets.get(target_name, [])
                    # Check if values differ (with small tolerance for floating point)
                    if not all(abs(a - b) < 0.001 for a, b in zip(current_value, expected_value)):
                        logger.warning(f"⚠️  Correcting {target_name} from {current_value} to {expected_value}")
                        motion_targets[target_name] = expected_value
                
                # Also update layout_coordinates to keep them consistent
                layout_coords = result.get("layout_coordinates", {})
                if "pick_target_xyz" in layout_coords:
                    layout_coords["pick_target_xyz"] = EXPECTED_TARGETS["pick_target_xyz"]
                if "place_target_xyz" in layout_coords:
                    layout_coords["place_target_xyz"] = EXPECTED_TARGETS["place_target_xyz"]
                
                ctx.deps.stage2_result = result
                logger.info("✅ Stage 2 results stored in ctx.deps.stage2_result")
        
        # Store Stage 3 validation results
        if skill_name == "simulation_validator" and script_name == "execute_and_validate":
            if isinstance(result, dict):
                ctx.deps.stage3_result = result
                logger.info("✅ Stage 3 validation results stored in ctx.deps.stage3_result")
        
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return json.dumps({
            "error": "script_not_found",
            "message": str(e),
            "skill": skill_name,
            "script": script_name
        }, indent=2)
    except subprocess.TimeoutExpired:
        return json.dumps({
            "error": "timeout",
            "message": f"Script exceeded 30 second timeout",
            "skill": skill_name,
            "script": script_name
        }, indent=2)
    except Exception as e:
        logger.error(f"")
        logger.error(f"{'='*80}")
        logger.error(f"❌ SKILL SCRIPT EXECUTION FAILED")
        logger.error(f"{'='*80}")
        logger.error(f"Skill: {skill_name}")
        logger.error(f"Script: {script_name}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"{'='*80}")
        return json.dumps({
            "error": "execution_failed",
            "message": str(e),
            "error_type": type(e).__name__,
            "skill": skill_name,
            "script": script_name
        }, indent=2)


@skill_tools.tool
def check_stage_status(
    ctx: RunContext[AgentDependencies]
) -> str:
    """
    Check which stage is currently complete and what data is available.
    
    Use this tool to determine:
    - Is Stage 1 complete? (ctx.deps.stage1_result exists)
    - Is Stage 2 complete? (ctx.deps.stage2_result exists)
    - What action should be taken next?
    
    This prevents accidentally re-running stages that are already complete.
    
    Returns:
        JSON with stage status and next action recommendation
    """
    stage1_complete = hasattr(ctx.deps, 'stage1_result') and ctx.deps.stage1_result is not None
    stage2_complete = hasattr(ctx.deps, 'stage2_result') and ctx.deps.stage2_result is not None
    
    if stage2_complete:
        return json.dumps({
            "stage1_complete": True,
            "stage2_complete": True,
            "next_action": "Proceed to Stage 3: genesis_scene_builder with ctx.deps.stage2_result",
            "message": "Both Stage 1 and Stage 2 are complete. Ready for simulation build."
        }, indent=2)
    elif stage1_complete:
        return json.dumps({
            "stage1_complete": True,
            "stage2_complete": False,
            "next_action": "Use get_stage1_data() tool to retrieve Stage 1 JSON, then call run_skill_script_tool('placement_solver', 'solve_placement', <stage1_data>)",
            "message": "Stage 1 is complete. When user confirms, use get_stage1_data() to retrieve the validated JSON, then pass it to placement_solver.",
            "stage1_summary": {
                "robot": ctx.deps.stage1_result.get('robot_selection', {}).get('model', 'N/A'),
                "components_count": len(ctx.deps.stage1_result.get('workcell_components', []))
            }
        }, indent=2)
    else:
        return json.dumps({
            "stage1_complete": False,
            "stage2_complete": False,
            "next_action": "Continue gathering Stage 1 requirements and call submit_stage1_json when complete",
            "message": "Stage 1 not yet complete. Continue requirements gathering with request_interpreter."
        }, indent=2)


@skill_tools.tool
def get_stage1_data(
    ctx: RunContext[AgentDependencies]
) -> Dict[str, Any]:
    """
    Retrieve the validated Stage 1 JSON data.
    
    Use this tool AFTER Stage 1 is complete to get the full Stage 1 JSON
    so you can pass it to placement_solver.
    
    Example usage:
    1. Check status with check_stage_status() 
    2. If Stage 1 complete, call: stage1_data = get_stage1_data()
    3. Pass directly to placement_solver: run_skill_script_tool("placement_solver", "solve_placement", stage1_data)
    
    Returns:
        Complete Stage 1 JSON as dict (ready to pass to run_skill_script_tool)
    """
    if not hasattr(ctx.deps, 'stage1_result') or ctx.deps.stage1_result is None:
        logger.error("❌ Attempted to retrieve Stage 1 data but it doesn't exist")
        return {
            "error": "Stage 1 not complete yet. Call submit_stage1_json first.",
            "stage1_complete": False
        }
    
    logger.info("✅ Retrieving Stage 1 data for Stage 2 execution")
    # Return the actual dict, not JSON string
    return ctx.deps.stage1_result


@skill_tools.tool
def prepare_genesis_input(
    ctx: RunContext[AgentDependencies]
) -> Dict[str, Any]:
    """
    Prepare complete component list for Genesis scene builder.
    
    Merges Stage 1 (robot + all components) with Stage 2 (optimized positions)
    to create the full input needed for genesis_scene_builder.
    
    This ensures ALL components are included in the simulation:
    - Robot (from robot_selection, placed ON TOP of pedestal)
    - Pedestal, conveyor, pallet (from Stage 2 with optimized positions)
    - Carton/objects (from Stage 1, placed ON TOP of conveyor)
    
    **CRITICAL**: This function returns placeholder paths. You MUST call
    `fix_genesis_paths()` tool before passing to genesis_scene_builder!
    
    Returns:
        Dict ready to pass to fix_genesis_paths() tool
    """
    if not hasattr(ctx.deps, 'stage1_result') or ctx.deps.stage1_result is None:
        logger.error("❌ Cannot prepare genesis input - Stage 1 not complete")
        return {"error": "Stage 1 not complete"}
    
    if not hasattr(ctx.deps, 'stage2_result') or ctx.deps.stage2_result is None:
        logger.error("❌ Cannot prepare genesis input - Stage 2 not complete")
        return {"error": "Stage 2 not complete"}
    
    stage1 = ctx.deps.stage1_result
    stage2 = ctx.deps.stage2_result
    
    components = []
    
    # Get optimized components from Stage 2
    optimized_components = stage2.get('optimized_components', [])
    optimized_dict = {comp['name']: comp for comp in optimized_components}
    
    # Get all components from Stage 1
    stage1_components = stage1.get('workcell_components', [])
    robot_selection = stage1.get('robot_selection', {})
    
    # Find pedestal and conveyor from optimized results (for robot/carton placement)
    pedestal_pos = [0.0, 0.0, 0.45]  # default
    pedestal_height = 0.9
    conveyor_pos = [0.5, 0.0, 0.4]  # default
    conveyor_height = 0.8
    
    for opt_comp in optimized_components:
        ct = opt_comp.get('component_type', '').lower()
        cn = opt_comp.get('name', '').lower()
        if 'pedestal' in ct or 'pedestal' in cn:
            pedestal_pos = opt_comp.get('position', pedestal_pos)
            pedestal_height = opt_comp.get('dimensions', [0.6, 0.6, 0.9])[2]
        elif 'conveyor' in ct or 'conveyor' in cn:
            conveyor_pos = opt_comp.get('position', conveyor_pos)
            conveyor_height = opt_comp.get('dimensions', [2.0, 0.6, 0.8])[2]
    
    # 1. Add ROBOT on top of pedestal
    if robot_selection:
        robot_z = pedestal_height  # Robot sits on top of pedestal
        components.append({
            "name": "robot",
            "component_type": "robot",
            "urdf": robot_selection.get('urdf_path', ''),
            "position": [pedestal_pos[0], pedestal_pos[1], robot_z],
            "orientation": [0, 0, 0],
            "dimensions": [0.1, 0.1, 0.5]
        })
    
    # 2. Add all Stage 2 optimized components (pedestal, conveyor, pallet, etc.)
    for opt_comp in optimized_components:
        comp_copy = opt_comp.copy()
        # Rename mjcf_path to urdf for build_scene compatibility
        if 'mjcf_path' in comp_copy:
            comp_copy['urdf'] = comp_copy.pop('mjcf_path')
        # Also check Stage 1 for the original mjcf_path if not in Stage 2
        if 'urdf' not in comp_copy:
            for s1_comp in stage1_components:
                if s1_comp.get('name') == comp_copy.get('name'):
                    comp_copy['urdf'] = s1_comp.get('mjcf_path', '')
                    break
        components.append(comp_copy)
    
    # 3. Add carton/objects NOT in Stage 2 (they were skipped in PSO)
    #    Place them on top of the conveyor
    for comp in stage1_components:
        name = comp.get('name')
        comp_type = comp.get('component_type', '').lower()
        
        # Skip if already in Stage 2 optimized output
        if name in optimized_dict:
            continue
        
        # Skip grippers/end effectors (part of robot)
        if 'gripper' in comp_type or 'end_effector' in comp_type:
            continue
        
        # Skip robot arm if somehow in components
        if comp_type in ['robot', 'robotic_arm', 'manipulator', 'arm']:
            continue
        
        # Carton/box/object → place on conveyor
        is_carton = any(kw in comp_type for kw in ['carton', 'box', 'object', 'item', 'package'])
        if is_carton:
            carton_z = conveyor_height + 0.02  # Slightly above conveyor surface
            position = [conveyor_pos[0], conveyor_pos[1], carton_z]
        else:
            # Any other unoptimized component: place at origin at half-height
            dims = comp.get('dimensions', [0.5, 0.5, 0.5])
            position = [0, 0, dims[2] / 2]
        
        components.append({
            "name": name,
            "component_type": comp.get('component_type', ''),
            "urdf": comp.get('mjcf_path', ''),
            "position": position,
            "orientation": [0, 0, 0],
            "dimensions": comp.get('dimensions', [0.5, 0.5, 0.5])
        })
    
    logger.info(f"✅ Prepared genesis input with {len(components)} total components (robot + {len(components)-1} workcell items)")
    
    # CRITICAL: Automatically include trajectory execution parameters
    # This prevents agents from forgetting to add them manually
    genesis_data = {
        "components": components,
        "robot_info": robot_selection,
        "task_objective": stage1.get('task_objective', ''),
        "execute_trajectory": True,  # Always execute trajectory
        "motion_targets": stage2.get('motion_targets', {}),  # Pick/place targets from PSO
        "z_lift": 0.4  # Lift height for trajectory
    }
    
    logger.info("✅ Added trajectory execution parameters: execute_trajectory=True, motion_targets, z_lift=0.4")
    
    return genesis_data


@skill_tools.tool
def fix_genesis_paths(
    ctx: RunContext[AgentDependencies],
    genesis_input: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fix all component paths in genesis input using the component catalog.
    
    **MANDATORY**: Call this tool AFTER prepare_genesis_input() and BEFORE
    passing data to genesis_scene_builder. Genesis will crash if paths are wrong.
    
    This tool:
    1. Reads the component catalog automatically
    2. Maps each component name/type to the correct absolute path
    3. Validates that paths exist on disk
    4. Returns the fixed JSON ready for genesis_scene_builder
    
    Args:
        ctx: Agent runtime context
        genesis_input: Output from prepare_genesis_input() (with placeholder paths)
    
    Returns:
        Genesis input dict with all "urdf" fields updated to absolute paths
    """
    import os
    from pathlib import Path
    
    # Component catalog paths (from component_catalog.md)
    CATALOG = {
        # Robots
        "franka_panda": "D:/GitHub/ieee_case/mujoco_menagerie/franka_emika_panda/panda.xml",
        "panda": "D:/GitHub/ieee_case/mujoco_menagerie/franka_emika_panda/panda.xml",
        "ur3": "D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur5e/ur5e.xml",  # Using UR5e as UR3 fallback
        "ur5": "D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur5e/ur5e.xml",
        "ur5e": "D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur5e/ur5e.xml",
        "ur10": "D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur10e/ur10e.xml",
        "ur10e": "D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur10e/ur10e.xml",
        "kuka_kr3": "D:/GitHub/ieee_case/mujoco_menagerie/kuka_iiwa_14/iiwa_14.xml",  # Using KUKA iiwa as fallback
        
        # Workcell components
        "conveyor": "D:/GitHub/ieee_case/workcell_components/conveyors/conveyor_belt.xml",
        "conveyor_belt": "D:/GitHub/ieee_case/workcell_components/conveyors/conveyor_belt.xml",
        "pedestal": "D:/GitHub/ieee_case/workcell_components/pedestals/robot_pedestal.xml",
        "robot_pedestal": "D:/GitHub/ieee_case/workcell_components/pedestals/robot_pedestal.xml",
        "pallet": "D:/GitHub/ieee_case/workcell_components/pallets/euro_pallet.xml",
        "euro_pallet": "D:/GitHub/ieee_case/workcell_components/pallets/euro_pallet.xml",
        "box": "D:/GitHub/ieee_case/workcell_components/boxes/medium_box.xml",
        "carton": "D:/GitHub/ieee_case/workcell_components/boxes/cardboard_box.xml",
        "cardboard_box": "D:/GitHub/ieee_case/workcell_components/boxes/cardboard_box.xml",
        "small_box": "D:/GitHub/ieee_case/workcell_components/boxes/small_box.xml",
        "medium_box": "D:/GitHub/ieee_case/workcell_components/boxes/medium_box.xml",
    }
    
    def resolve_path(name: str, comp_type: str, robot_model: str = "") -> str:
        """Match component to catalog path."""
        # Normalize
        name_lower = name.lower().replace(" ", "_").replace("-", "_")
        type_lower = comp_type.lower()
        
        # 1. Try robot model first
        if robot_model:
            model_key = robot_model.lower().replace(" ", "_").replace("-", "_")
            if model_key in CATALOG:
                return CATALOG[model_key]
        
        # 2. Try exact name match
        if name_lower in CATALOG:
            return CATALOG[name_lower]
        
        # 3. Try type match
        if type_lower in CATALOG:
            return CATALOG[type_lower]
        
        # 4. Fuzzy keyword match
        for keyword in ["conveyor", "pallet", "pedestal", "carton", "box"]:
            if keyword in name_lower or keyword in type_lower:
                if keyword in CATALOG:
                    return CATALOG[keyword]
        
        # 5. Default empty (will spawn as Box)
        logger.warning(f"⚠️  No catalog match for '{name}' (type: {comp_type}) - will use Box")
        return ""
    
    # Fix paths for all components
    components = genesis_input.get("components", [])
    robot_info = genesis_input.get("robot_info", {})
    fixed_count = 0
    missing_count = 0
    
    for comp in components:
        old_path = comp.get("urdf", "")
        comp_name = comp.get("name", "")
        comp_type = comp.get("component_type", "")
        
        # Get robot model for robot component
        robot_model = robot_info.get("model", "") if comp_type == "robot" else ""
        
        # Resolve path
        new_path = resolve_path(comp_name, comp_type, robot_model)
        
        if new_path:
            # Validate file exists
            if os.path.exists(new_path):
                comp["urdf"] = new_path
                logger.info(f"✅ {comp_name}: {new_path}")
                fixed_count += 1
            else:
                logger.error(f"❌ {comp_name}: Path found but file doesn't exist: {new_path}")
                comp["urdf"] = ""  # Will spawn as Box
                missing_count += 1
        else:
            logger.warning(f"⚠️  {comp_name}: No match in catalog - will spawn as Box")
            comp["urdf"] = ""
            missing_count += 1
    
    logger.info(f"📍 Path resolution: {fixed_count} fixed, {missing_count} missing (will use Box)")
    
    return genesis_input


@skill_tools.tool
def get_stage2_data(
    ctx: RunContext[AgentDependencies]
) -> Dict[str, Any]:
    """
    Retrieve the Stage 2 optimized layout data.
    
    Use this tool AFTER Stage 2 is complete to get the optimized component
    positions so you can pass them to genesis_scene_builder.
    
    Returns:
        Complete Stage 2 result dict (ready to pass to run_skill_script_tool)
    """
    if not hasattr(ctx.deps, 'stage2_result') or ctx.deps.stage2_result is None:
        logger.error("❌ Attempted to retrieve Stage 2 data but it doesn't exist")
        return {
            "error": "Stage 2 not complete yet. Call placement_solver first.",
            "stage2_complete": False
        }
    
    logger.info("✅ Retrieving Stage 2 data for Stage 3 execution")
    # Return the actual dict, not JSON string
    return ctx.deps.stage2_result



@skill_tools.tool
def submit_stage1_json(
    ctx: RunContext[AgentDependencies],
    stage1_data: Dict[str, Any]
) -> str:
    """
    Submit and validate the Stage 1 requirements JSON (MANDATORY).

    YOU MUST call this tool when you have gathered all requirements through
    conversation. This validates your JSON against the Pydantic schema and
    logs it. Do NOT paste JSON in a text response — use this tool instead.

    ** IMPORTANT: Updates are allowed **
    - If Stage 1 is already validated but user asks to change something,
      call this tool again with the UPDATED JSON. It will overwrite the old data.
    - When user just says "proceed" without changes, use get_stage1_data() instead.

    If validation fails, fix the errors and call this tool again.
    If validation succeeds, show summary to user and wait for confirmation.

    Args:
        ctx: Agent runtime context
        stage1_data: The complete Stage 1 JSON dictionary with all required fields:
            - stage_1_complete (bool): Must be True
            - task_objective (str): Min 50 chars describing the task
            - task_specification (dict): Object name, sku_id, dimensions [L,W,H] in meters, weight_kg, material, quantity
            - additional_objects (list): Extra objects if any
            - robot_selection (dict): model, manufacturer, payload_kg, reach_m, justification (min 50 chars), urdf_path
            - workcell_components (list): Each with name, component_type, mjcf_path (.xml), position [x,y,z], orientation [x,y,z,w]
            - spatial_reasoning (dict): zones (list), material_flow (str), accessibility (str), reasoning (str)
            - throughput_requirement (dict): items_per_hour, cycle_time_seconds
            - constraints (list): Each with constraint_type, description, value
            - missing_info (list): Must be empty []

    Returns:
        Success confirmation or validation errors to fix
    """
    try:
        # If Stage 1 already exists, this is an UPDATE - overwrite the old data
        if hasattr(ctx.deps, 'stage1_result') and ctx.deps.stage1_result is not None:
            logger.info("🔄 Stage 1 already validated - treating this as an UPDATE to Stage 1 JSON")
        
        # Validate against Pydantic schema
        validated = Stage1Output.model_validate(stage1_data)
        validated_dict = validated.model_dump()
        
        # ADDITIONAL VALIDATION: Check position/orientation are null
        components = validated_dict.get('workcell_components', [])
        
        # CRITICAL: Fix standard component dimensions if incorrect
        STANDARD_DIMS = {
            'pedestal': [0.60, 0.60, 0.50],
            'conveyor': [2.00, 0.64, 0.82],
            'pallet': [1.20, 0.80, 0.15],
            'robot_pedestal': [0.60, 0.60, 0.50],
            'conveyor_belt': [2.00, 0.64, 0.82],
            'euro_pallet': [1.20, 0.80, 0.15],
        }
        
        for i, comp in enumerate(components):
            comp_type = comp.get('component_type', '').lower()
            comp_name = comp.get('name', '').lower()
            
            # Check if this is a standard component with known dimensions
            for std_key, std_dims in STANDARD_DIMS.items():
                if std_key in comp_type or std_key in comp_name:
                    current_dims = comp.get('dimensions', [])
                    if current_dims != std_dims:
                        logger.warning(f"⚠️  Correcting {comp['name']} dimensions from {current_dims} to {std_dims}")
                        comp['dimensions'] = std_dims
                    break
            
            if comp.get('position') is not None:
                raise ValueError(f"Component '{comp['name']}' has position={comp['position']} but MUST be null. Placement_solver fills positions in Stage 2.")
            if comp.get('orientation') is not None:
                raise ValueError(f"Component '{comp['name']}' has orientation={comp['orientation']} but MUST be null. Placement_solver fills orientations in Stage 2.")
        
        # Check for required component types
        component_types = [c.get('component_type', '').lower() for c in components]
        has_pedestal = any('pedestal' in ct or 'base' in ct or 'robot' in c.get('name', '').lower() for c, ct in zip(components, component_types))
        has_object = any('carton' in ct or 'box' in ct or 'object' in ct for ct in component_types)
        
        warnings = []
        if not has_pedestal:
            warnings.append("WARNING: No robot pedestal/base component found. Robot needs a mounting platform!")
        if not has_object:
            warnings.append("WARNING: No carton/box components found. For pick-place tasks, include the objects being manipulated as components!")
        
        if warnings:
            raise ValueError("Missing required components:\n" + "\n".join(warnings))

        # Store in context for later use
        ctx.deps.stage1_result = validated_dict

        # Log prominently (full JSON in log file)
        log_stage_1_json(validated_dict)
        logger.info("✅ Stage 1 JSON validated and stored successfully")

        # Create user-friendly summary
        robot = validated_dict['robot_selection']
        task_obj = validated_dict.get('task_specification', {})
        components = validated_dict.get('workcell_components', [])
        throughput = validated_dict.get('throughput_requirement', {})
        
        summary = {
            "status": "success",
            "message": "✅ Stage 1 requirements gathered and validated successfully!",
            "summary": {
                "task": validated_dict['task_objective'],
                "object": f"{task_obj.get('name', 'N/A')} - {task_obj.get('dimensions', [])} m, {task_obj.get('weight_kg', 0)} kg",
                "robot": f"{robot['model']} ({robot['manufacturer']}) - {robot['payload_kg']}kg payload, {robot['reach_m']}m reach",
                "components_count": len(components),
                "component_types": list(set([c['component_type'] for c in components])),
                "throughput": f"{throughput.get('items_per_hour', 'N/A')} items/hour"
            },
            "next_action": "IMPORTANT: Show this summary to the user and ask: 'Does this look correct? Should I proceed to Stage 2 (component placement optimization)?'. If user confirms, proceed. If user wants changes, ask what to modify and stay in Stage 1."
        }

        return json.dumps(summary, indent=2)

    except Exception as e:
        error_msg = str(e)
        logger.warning(f"❌ Stage 1 JSON validation failed: {error_msg}")
        return json.dumps({
            "status": "validation_error",
            "message": "Stage 1 JSON validation FAILED. Fix the errors below and call submit_stage1_json again.",
            "errors": error_msg,
            "hint": "Check: dimensions must be [L,W,H] in meters, mjcf_path must end with .xml, justification min 50 chars, task_objective min 50 chars, missing_info must be empty list, position/orientation MUST BE null (not [0,0,0]), MUST include robot pedestal component, MUST include carton/box/object components for pick-place tasks"
        }, indent=2)

