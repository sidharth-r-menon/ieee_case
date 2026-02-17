#!/usr/bin/env python3
"""
Genesis Scene Builder + Trajectory Executor - Combined version

Builds the Genesis scene AND executes trajectory if requested.
Based on genesis_world_pnp_4.py complete workflow.

Input: JSON with components and optional motion_targets
Output: JSON with build result and optional trajectory result
"""

import json
import sys
import os
import numpy as np

# Configure stderr logging
def log_stderr(msg):
    """Log to stderr for debugging."""
    print(f"[genesis] {msg}", file=sys.stderr, flush=True)

log_stderr("="*80)
log_stderr("GENESIS SCENE BUILDER + EXECUTOR STARTED")
log_stderr("="*80)

try:
    import genesis as gs
    log_stderr("✅ Genesis module imported")
except ImportError as e:
    log_stderr(f"❌ FATAL: Genesis not found: {e}")
    print(json.dumps({"error": "genesis module not found", "success": False}))
    sys.exit(1)


def execute_trajectory(robot, end_effector, down_quat, scene, target_pos, phase_name="", is_plunge=False, reuse_qpos=None):
    """Execute trajectory to target (from pnp_4.py)"""
    log_stderr(f"[{phase_name}] Target: {target_pos}")
    
    current_qpos = robot.get_dofs_position()
    
    qpos_goal = reuse_qpos if reuse_qpos is not None else robot.inverse_kinematics(
        link=end_effector,
        pos=target_pos,
        quat=down_quat,
        rot_mask=[True, True, True],
        init_qpos=current_qpos
    )
    
    path = robot.plan_path(
        qpos_goal=qpos_goal,
        num_waypoints=150,
        smooth_path=not is_plunge,
        max_nodes=5000
    )

    if path is None:
        path = robot.plan_path(qpos_goal=qpos_goal, num_waypoints=150, smooth_path=False)

    if path is not None:
        for waypoint in path:
            robot.control_dofs_position(waypoint)
            scene.step()
        for _ in range(40):
            scene.step()
        return qpos_goal
    
    log_stderr(f"[{phase_name}] FAILED - no path found")
    return None


def main():
    try:
        log_stderr("📥 Reading JSON input...")
        input_data = json.load(sys.stdin)
        log_stderr(f"✅ Parsed, keys: {list(input_data.keys())}")
        
        # Build complete components list (robot + other components)
        components = []
        
        # Add robot if provided
        robot_data = input_data.get("robot")
        if robot_data:
            log_stderr(f"🤖 Robot data found: {robot_data.get('name')}")
            robot_component = {
                "name": robot_data.get("name", "robot"),
                "component_type": "robot",  # CRITICAL: Mark as robot
                "urdf": robot_data.get("urdf"),
                "position": robot_data.get("position"),
                "orientation": robot_data.get("orientation", [0, 0, 0])
            }
            components.append(robot_component)
            log_stderr(f"  ✅ Robot added to components list")
        
        # Add other components
        other_components = input_data.get("components", [])
        components.extend(other_components)
        
        execute_motion = input_data.get("execute_trajectory", False)
        motion_targets = input_data.get("motion_targets", {})
        z_lift = input_data.get("z_lift", 0.4)
        
        log_stderr(f"📦 Total components: {len(components)}")
        log_stderr(f"🎯 Execute trajectory: {execute_motion}")
        
        if not components:
            print(json.dumps({"error": "No components", "success": False}))
            sys.exit(1)

        # Initialize Genesis
        log_stderr("🚀 Initializing Genesis...")
        gs.init(backend=gs.gpu)
        scene = gs.Scene(show_viewer=True)
        scene.add_entity(gs.morphs.Plane())
        log_stderr("✅ Genesis initialized")

        # Spawn components
        log_stderr(f"📦 Spawning {len(components)} components...")
        log_stderr(f"")
        log_stderr(f"Component List:")
        for i, comp in enumerate(components):
            log_stderr(f"  {i+1}. {comp.get('name')} - type: {comp.get('component_type', 'unknown')}")
        log_stderr(f"")
        
        spawned = []
        robot_entity = None
        
        for comp in components:
            urdf = comp.get("urdf")
            pos = comp.get("position")
            name = comp.get("name")
            comp_type = comp.get("component_type", "unknown")
            
            if not urdf or not os.path.exists(urdf):
                log_stderr(f"  ⚠️  {name}: File not found")
                spawned.append({"component_name": name, "status": "skipped"})
                continue
            
            log_stderr(f"  - {name} ({comp_type}) at {pos}")
            entity = scene.add_entity(gs.morphs.MJCF(file=urdf, pos=pos))
            
            if comp_type == "robot":
                robot_entity = entity
                log_stderr(f"    🤖 Stored as robot")
            
            spawned.append({
                "component_name": name,
                "urdf": urdf,
                "position": pos,
                "status": "spawned"
            })

        # Build scene
        log_stderr("🔨 Building scene...")
        scene.build()
        log_stderr("✅ Scene built")
        
        # NOTE: DO NOT set initial robot pose - let Genesis use defaults
        # Setting pose manually was causing "index -2 out of bounds" errors in trajectory execution
        # Reference script (genesis_world_pnp_4.py) does not set initial pose
        
        log_stderr("👁️  Genesis viewer is now open")
        
        # Prepare base result
        result = {
            "success": True,
            "spawned_components": spawned,
            "robot_available": robot_entity is not None,
            "message": "Genesis scene built successfully."
        }
        
        # Execute trajectory if requested
        if execute_motion and robot_entity is not None and motion_targets:
            log_stderr("")
            log_stderr("="*80)
            log_stderr("🎯 TRAJECTORY EXECUTION STARTING")
            log_stderr("="*80)
            
            try:
                pick_pos = np.array(motion_targets.get("pick_target_xyz", [0.65, 0.0, 1.13]))
                place_pos = np.array(motion_targets.get("place_target_xyz", [0.0, 0.75, 0.46]))
                
                log_stderr(f"Pick: {pick_pos}, Place: {place_pos}, Lift: {z_lift}m")
                
                end_effector = robot_entity.get_link('wrist_3_link')
                down_quat = np.array([0, 1, 0, 0])
                
                trajectory_log = []
                
                # Phase 1: HOVER PICK
                hover_qpos = execute_trajectory(robot_entity, end_effector, down_quat, scene,
                                               pick_pos + np.array([0, 0, z_lift]), "HOVER PICK")
                if hover_qpos is None:
                    raise RuntimeError("HOVER PICK failed")
                trajectory_log.append("HOVER PICK")
                
               # Phase 2: PLUNGE
                qpos = execute_trajectory(robot_entity, end_effector, down_quat, scene,
                                         pick_pos, "PLUNGE", is_plunge=True)
                if qpos is None:
                    raise RuntimeError("PLUNGE failed")
                trajectory_log.append("PLUNGE")
                
                # Phase 3: LIFT
                qpos = execute_trajectory(robot_entity, end_effector, down_quat, scene,
                                         pick_pos + np.array([0, 0, z_lift]), "LIFT", reuse_qpos=hover_qpos)
                if qpos is None:
                    raise RuntimeError("LIFT failed")
                trajectory_log.append("LIFT")
                
                # Phase 4: HOVER PLACE
                hover_place_qpos = execute_trajectory(robot_entity, end_effector, down_quat, scene,
                                                     place_pos + np.array([0, 0, z_lift]), "HOVER PLACE")
                if hover_place_qpos is None:
                    raise RuntimeError("HOVER PLACE failed")
                trajectory_log.append("HOVER PLACE")
                
                # Phase 5: DROP
                qpos = execute_trajectory(robot_entity, end_effector, down_quat, scene,
                                         place_pos, "DROP", is_plunge=True)
                if qpos is None:
                    raise RuntimeError("DROP failed")
                trajectory_log.append("DROP")
                
                # Phase 6: RETRACT
                qpos = execute_trajectory(robot_entity, end_effector, down_quat, scene,
                                         place_pos + np.array([0, 0, z_lift]), "RETRACT", reuse_qpos=hover_place_qpos)
                if qpos is None:
                    raise RuntimeError("RETRACT failed")
                trajectory_log.append("RETRACT")
                
                log_stderr("="*80)
                log_stderr("✅ TRAJECTORY EXECUTION COMPLETE")
                log_stderr("="*80)
                
                result["trajectory_executed"] = True
                result["trajectory_status"] = "success"
                result["trajectory_log"] = trajectory_log
                result["phases_completed"] = len(trajectory_log)
                result["message"] += " Trajectory executed successfully."
                
            except Exception as traj_error:
                log_stderr(f"❌ Trajectory failed: {traj_error}")
                result["trajectory_executed"] = True
                result["trajectory_status"] = "failed"
                result["trajectory_error"] = str(traj_error)
                result["message"] += f" Trajectory failed: {traj_error}"
        
        # Output result
        log_stderr("📤 Sending result JSON...")
        print(json.dumps(result, indent=2), flush=True)
        log_stderr("✅ JSON sent")
        
        # Keep scene alive
        log_stderr("")
        log_stderr("🔄 Entering simulation loop to keep viewer open...")
        log_stderr("   (Close viewer window or press Ctrl+C to exit)")
        
        import time
        try:
            step_count = 0
            while True:
                scene.step()
                step_count += 1
                if step_count % 200 == 0:
                    log_stderr(f"💓 Scene alive (step {step_count})")
                time.sleep(0.01)
        except KeyboardInterrupt:
            log_stderr("⏹️  Stopped")
            sys.exit(0)
        
    except Exception as e:
        import traceback
        log_stderr(f"❌ FATAL ERROR: {type(e).__name__}: {e}")
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({
            "error": str(e),
            "success": False,
            "traceback": traceback.format_exc()
        }), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_stderr(f"❌ Unhandled exception: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
