---
name: genesis_scene_builder
description: "Stage 3 — Simulation: Builds and runs the Genesis physics simulation. Use ONLY after Stage 2 layout is complete."
metadata:
  stage: "3"
  skill_type: "main"
  order: 8
  substeps:
    - simulation_validator
---

# Genesis Scene Builder — Stage 3 Simulation

## CRITICAL: Only One Script Exists

Script name: **`build_and_execute`** — do NOT call `build_scene` (deleted).

## Mandatory 3-Step Sequence

Execute in order with **no text output between steps**:

```python
# Step 1 — Merge Stage 1 + Stage 2 (auto-includes trajectory params)
genesis_input = prepare_genesis_input()

# Step 2 — Fix all component paths to absolute catalog paths
fixed_genesis = fix_genesis_paths(genesis_input)

# Step 3 — Build scene and execute pick-place trajectory
run_skill_script_tool("genesis_scene_builder", "build_and_execute", fixed_genesis)
```

**Never**: pass an empty dict `{}`, skip `fix_genesis_paths`, or pass `genesis_input` instead of `fixed_genesis` to Step 3.

## What Happens
Genesis opens in a new terminal/viewer, spawns all components, then immediately runs the 6-phase pick-place trajectory (HOVER PICK → PLUNGE → LIFT → HOVER PLACE → DROP → RETRACT). The viewer stays open after completion.

## Output
Success: `{"success": true, "trajectory_executed": true, "trajectory_status": "success", "phases_completed": 6}`

Trajectory failure: `{"success": true, "trajectory_status": "failed", "trajectory_error": "HOVER PICK failed - no path found"}`

## What to Tell the User
- **Success**: "✅ Design validated — viewer is open, all 6 trajectory phases completed."
- **Failure**: "⚠️ Trajectory failed at [PHASE] — the layout may need adjustment. Would you like to iterate?"


