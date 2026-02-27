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


def move_to(robot, end_effector, down_quat, scene, target_pos, phase_name,
            reuse_qpos=None, init_hint=None, max_nodes=8000, carried_entity=None,
            ee_link_name='vacuum_gripper/tcp_link'):
    """
    Execute trajectory to target position.
    Mirrors genesis_world_pnp_7.py move_to() exactly.
    """
    log_stderr(f"\n[{phase_name}] → {np.round(target_pos, 3)}")

    seed = init_hint if init_hint is not None else robot.get_dofs_position()

    qpos_goal = reuse_qpos if reuse_qpos is not None else robot.inverse_kinematics(
        link=end_effector,
        pos=target_pos,
        quat=down_quat,
        rot_mask=[True, True, True],
        init_qpos=seed,
    )

    if qpos_goal is None:
        log_stderr(f"[{phase_name}] ✗ IK failed.")
        return None

    plan_kwargs = {
        "qpos_goal": qpos_goal,
        "num_waypoints": 200,
        "smooth_path": False,
        "max_nodes": max_nodes,
    }

    if carried_entity is not None:
        plan_kwargs["with_entity"] = carried_entity
        plan_kwargs["ee_link_name"] = ee_link_name
        log_stderr(f"[{phase_name}]   (Planning with attached payload)")

    path = robot.plan_path(**plan_kwargs)

    if path is None:
        log_stderr(f"[{phase_name}] ✗ Path planning failed.")
        return None

    log_stderr(f"[{phase_name}] ✓ Executing {len(path)} waypoints.")
    for wp in path:
        robot.control_dofs_position(wp)
        scene.step()
    for _ in range(60):
        scene.step()
    return qpos_goal


def main():
    try:
        log_stderr("📥 Reading JSON input...")
        input_data = json.load(sys.stdin)
        log_stderr(f"✅ Parsed, keys: {list(input_data.keys())}")
        
        # Unwrap if agent passed data nested under a wrapper key
        # (agent sometimes wraps args when calling run_skill_script_tool)
        for wrapper_key in ("genesis_input", "scene_data", "genesis_data", "data"):
            if (wrapper_key in input_data
                    and "components" not in input_data
                    and "robot" not in input_data):
                log_stderr(f"🔄 Unwrapping '{wrapper_key}' wrapper key...")
                input_data = input_data[wrapper_key]
                log_stderr(f"✅ Unwrapped, new keys: {list(input_data.keys())}")
                break
        
        # Build complete components list (robot + other components)
        components = []
        
        # Add robot if provided
        robot_data = input_data.get("robot")
        if robot_data:
            log_stderr(f"🤖 Robot data found: {robot_data.get('name')}")
            # Support urdf / urdf_path / mjcf_path key names
            robot_urdf = (robot_data.get("urdf")
                          or robot_data.get("urdf_path")
                          or robot_data.get("mjcf_path"))
            robot_component = {
                "name": robot_data.get("name", "robot"),
                "component_type": "robot",  # CRITICAL: Mark as robot
                "urdf": robot_urdf,
                "position": robot_data.get("position"),
                "orientation": robot_data.get("orientation", [0, 0, 0])
            }
            components.append(robot_component)
            log_stderr(f"  ✅ Robot added to components list (urdf={robot_urdf})")
        
        # Add other components — support both 'components' and 'workcell_components' keys
        other_components = input_data.get("components") or input_data.get("workcell_components", [])
        components.extend(other_components)
        
        execute_motion = input_data.get("execute_trajectory", False)
        motion_targets = input_data.get("motion_targets", {})
        z_lift = input_data.get("z_lift", 0.35)  # Z_HOVER from genesis_world_pnp_7.py
        
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
        carton_entity = None
        
        for comp in components:
            # Support urdf / urdf_path / mjcf_path key names
            urdf = (comp.get("urdf")
                    or comp.get("mjcf_path")
                    or comp.get("urdf_path"))
            pos = comp.get("position")
            name = comp.get("name")
            comp_type = comp.get("component_type", "unknown").lower()  # normalise case
            
            if not urdf or not os.path.exists(urdf):
                log_stderr(f"  ⚠️  {name}: File not found (path={urdf})")
                spawned.append({"component_name": name, "status": "skipped"})
                continue
            
            log_stderr(f"  - {name} ({comp_type}) at {pos}")
            entity = scene.add_entity(gs.morphs.MJCF(file=urdf, pos=pos))
            
            if comp_type == "robot":
                robot_entity = entity
                log_stderr(f"    🤖 Stored as robot")
            elif comp_type in ("carton", "box", "cardboard_box", "carton_to_palletize", "object"):
                carton_entity = entity
                log_stderr(f"    📦 Stored as carton")
            
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
        
        # Set home pose (mirrors genesis_world_pnp_7.py)
        home_qpos = np.array([0.0, -np.pi/2, np.pi/2, -np.pi/2, -np.pi/2, 0.0])
        if robot_entity is not None:
            robot_entity.set_dofs_position(home_qpos)
            robot_entity.control_dofs_position(home_qpos)
            log_stderr("🏠 Home pose set")
        
        log_stderr("👁️  Genesis viewer is now open")
        
        # Prepare base result
        result = {
            "success": True,
            "spawned_components": spawned,
            "robot_available": robot_entity is not None,
            "carton_available": carton_entity is not None,
            "message": "Genesis scene built successfully."
        }
        
        # Execute trajectory if requested
        if execute_motion and robot_entity is not None and motion_targets:
            log_stderr("")
            log_stderr("="*80)
            log_stderr("🎯 TRAJECTORY EXECUTION STARTING (genesis_world_pnp_7 approach)")
            log_stderr("="*80)
            
            try:
                # Defaults from genesis_world_pnp_7.py: BOX_SIZE=0.20
                #   PICK_Z  = 0.82 + 0.20 + 0.002 = 1.022
                #   PLACE_Z = 0.15 + 0.20 + 0.025 = 0.375
                pick_pos  = np.array(motion_targets.get("pick_target_xyz",  [0.65, 0.0, 1.022]))
                place_pos = np.array(motion_targets.get("place_target_xyz", [0.0, 0.75, 0.375]))
                Z_HOVER   = z_lift  # default 0.35 from pnp_7

                log_stderr(f"Pick: {pick_pos}, Place: {place_pos}, Z_HOVER: {Z_HOVER}m")

                end_effector   = robot_entity.get_link('vacuum_gripper/tcp_link')
                down_quat      = np.array([0, 1, 0, 0])   # 180° around X → suction face toward -Z
                ee_link_name   = 'vacuum_gripper/tcp_link'

                # Suction (weld constraint) setup
                rigid          = scene.sim.rigid_solver
                ee_idx         = np.array([end_effector.idx], dtype=gs.np_int)
                weld_active    = False

                def suction_on():
                    nonlocal weld_active
                    if weld_active or carton_entity is None:
                        return
                    box_half = 0.10  # BOX_SIZE / 2
                    tcp_z  = float(end_effector.get_pos()[2])
                    box_z  = float(carton_entity.get_pos()[2])
                    box_top = box_z + box_half
                    gap    = tcp_z - box_top
                    status = "✓ GOOD" if abs(gap) < 0.015 else "⚠ MISALIGNED"
                    log_stderr(f"[SUCTION CHECK] TCP z={tcp_z:.4f}  box_top z={box_top:.4f}  gap={gap:+.4f}  {status}")
                    c_idx = np.array([carton_entity.base_link.idx], dtype=gs.np_int)
                    rigid.add_weld_constraint(c_idx, ee_idx)
                    weld_active = True
                    log_stderr("[SUCTION ON]  Carton welded to TCP.")

                def suction_off():
                    nonlocal weld_active
                    if not weld_active or carton_entity is None:
                        return
                    c_idx = np.array([carton_entity.base_link.idx], dtype=gs.np_int)
                    rigid.delete_weld_constraint(c_idx, ee_idx)
                    weld_active = False
                    log_stderr("[SUCTION OFF] Carton released.")

                trajectory_log = []

                # Settle at home
                log_stderr("[INIT] Settling at home (100 steps)...")
                for _ in range(100):
                    robot_entity.control_dofs_position(home_qpos)
                    scene.step()

                # Phase 1: APPROACH HOVER above pick
                hover_pick = move_to(robot_entity, end_effector, down_quat, scene,
                                     pick_pos + np.array([0, 0, Z_HOVER]),
                                     "1  APPROACH HOVER",
                                     init_hint=home_qpos,
                                     ee_link_name=ee_link_name)
                if hover_pick is None:
                    raise RuntimeError("APPROACH HOVER failed")
                trajectory_log.append("APPROACH HOVER")

                # Phase 2: PLUNGE to box top surface
                qpos = move_to(robot_entity, end_effector, down_quat, scene,
                               pick_pos,
                               "2  PLUNGE to box top",
                               init_hint=hover_pick,
                               ee_link_name=ee_link_name)
                if qpos is None:
                    raise RuntimeError("PLUNGE failed")
                trajectory_log.append("PLUNGE")

                # Engage suction
                suction_on()
                for _ in range(30):
                    scene.step()

                # Phase 3: LIFT straight up (reuse hover joints)
                qpos = move_to(robot_entity, end_effector, down_quat, scene,
                               pick_pos + np.array([0, 0, Z_HOVER]),
                               "3  LIFT",
                               reuse_qpos=hover_pick,
                               carried_entity=carton_entity,
                               ee_link_name=ee_link_name)
                if qpos is None:
                    raise RuntimeError("LIFT failed")
                trajectory_log.append("LIFT")

                # Phase 4: TRANSPORT to hover above pallet
                hover_place = move_to(robot_entity, end_effector, down_quat, scene,
                                      place_pos + np.array([0, 0, Z_HOVER]),
                                      "4  TRANSPORT",
                                      init_hint=hover_pick,
                                      carried_entity=carton_entity,
                                      max_nodes=15000,
                                      ee_link_name=ee_link_name)
                if hover_place is None:
                    raise RuntimeError("TRANSPORT failed")
                trajectory_log.append("TRANSPORT")

                # Phase 5: LOWER box onto pallet
                qpos = move_to(robot_entity, end_effector, down_quat, scene,
                               place_pos,
                               "5  LOWER to pallet",
                               init_hint=hover_place,
                               carried_entity=carton_entity,
                               max_nodes=15000,
                               ee_link_name=ee_link_name)
                if qpos is None:
                    raise RuntimeError("LOWER failed")
                trajectory_log.append("LOWER")

                # Release suction
                suction_off()
                for _ in range(60):
                    scene.step()

                # Phase 6: RETRACT above pallet
                qpos = move_to(robot_entity, end_effector, down_quat, scene,
                               place_pos + np.array([0, 0, Z_HOVER]),
                               "6  RETRACT",
                               reuse_qpos=hover_place,
                               ee_link_name=ee_link_name)
                if qpos is None:
                    raise RuntimeError("RETRACT failed")
                trajectory_log.append("RETRACT")

                log_stderr("="*80)
                log_stderr("✅ PICK-AND-PLACE CYCLE COMPLETE")
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
