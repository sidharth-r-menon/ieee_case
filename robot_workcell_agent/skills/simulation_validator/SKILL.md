---
name: simulation_validator
description: "DEPRECATED - Trajectory execution is now integrated into genesis_scene_builder. Use build_and_execute script instead."
metadata:
  stage: "3"
  skill_type: "substep"
  parent: "genesis_scene_builder"
  deprecated: true
---

# Simulation Validator (DEPRECATED)

## ⚠️ NOTICE: This skill is deprecated

Trajectory execution is now **integrated** into `genesis_scene_builder` via the `build_and_execute` script.

**DO NOT use this skill separately.**

## What to Use Instead

When user wants to execute trajectory, use the `genesis_scene_builder` skill:

```python
# Get Stage 2 motion targets
stage2_data = get_stage2_data()

# Prepare genesis input
genesis_input = prepare_genesis_input()
fixed_genesis = fix_genesis_paths(genesis_input)

# Add trajectory execution flag
fixed_genesis["execute_trajectory"] = True
fixed_genesis["motion_targets"] = stage2_data["motion_targets"]
fixed_genesis["z_lift"] = 0.4

# Build scene AND execute trajectory in one go
result = run_skill_script_tool("genesis_scene_builder", "build_and_execute", fixed_genesis)
```

This will:
1. Build the Genesis scene
2. Spawn all components (robot + workcell items)
3. Execute the 6-phase pick-place trajectory
4. Return success/failure result

## Why Deprecated

**Technical reason:** Genesis scene and trajectory execution must share the same scene object. 
Running them as separate scripts is architecturally impossible.

**Solution:** Combined into single `build_and_execute` script, matching the reference implementation (genesis_world_pnp_4.py).

---

## Old Documentation (For Reference Only)
```

## What the Script Does

The `execute_and_validate.py` script executes the trajectory (from pnp_4.py):

```python
# Get robot end effector
end_effector = robot.get_link('wrist_3_link')
down_quat = np.array([0, 1, 0, 0])

# Execute pick-place sequence
# 1. HOVER PICK
# 2. PLUNGE to pickup
# 3. LIFT
# 4. HOVER PLACE
# 5. DROP
# 6. RETRACT
```

## Input

```json
{
  "motion_targets": {
    "pick_target_xyz": [0.65, 0.0, 1.13],
    "place_target_xyz": [0.0, 0.75, 0.46]
  },
  "z_lift": 0.4
}
```

## Output

**Success:**
```json
{
  "status": "pass",
  "message": "Trajectory execution completed successfully",
  "trajectory_log": [...],
  "phases_completed": 6,
  "validation_result": "pass"
}
```

**Failure:**
```json
{
  "status": "fail",
  "error": "Path planning failed",
  "message": "Trajectory execution failed: ...",
  "validation_result": "fail"
}
```

## Validation Logic

Simple:
1. Try to execute all 6 trajectory phases
2. If any error occurs → **FAIL** (layout issue)
3. If all complete successfully → **PASS** (design works!)

## Next Steps

- **PASS**: Design complete, report success to user
- **FAIL**: Layout needs adjustment, re-run Stage 2