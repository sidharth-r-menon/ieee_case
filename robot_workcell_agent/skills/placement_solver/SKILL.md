---
name: placement_solver
description: "Stage 2 — Layout Optimization: Computes optimal physical positions for all workcell components. Use ONLY after Stage 1 is complete (submit_stage1_json succeeded)."
metadata:
  stage: "2"
  skill_type: "main"
  order: 7
---

# Placement Solver — Stage 2 Layout Optimization

## Overview
Runs `layout_generator.py` to calculate collision-free 3D positions for all workcell components. Robot and pedestal are fixed at origin; conveyor is placed along X-axis; pallet along Y-axis.

## When to Use
After Stage 1 JSON is validated and user confirms to proceed.

## Workflow

**Step 1 — Retrieve Stage 1 data**
```python
stage1_data = get_stage1_data()
```

**Step 2 — Run placement solver**
```python
run_skill_script_tool("placement_solver", "solve_placement", stage1_data)
```
The script extracts robot reach, component dimensions (matched by keyword: pedestal/conveyor/pallet/carton), and computes positions automatically. No manual field construction needed.

**Step 3 — Show results, ask confirmation**
Show the computed positions and motion targets then ask:
"Does this layout look correct? Should I proceed to Stage 3 (Genesis simulation)?"

**Step 4 — Wait for user response**
- User confirms → proceed to `genesis_scene_builder`
- User requests changes → re-run after adjusting Stage 1 dimensions

## Script Output Keys
- `optimized_components` — list of components with filled `position`, `orientation`, `dimensions`, `mjcf_path`
- `motion_targets` — `pick_target_xyz`, `place_target_xyz`, `box_spawn_pos` used by trajectory
- `layout_coordinates` — same targets plus `pedestal_pos`, `conveyor_pos`, `pallet_pos`
- `status` — `"success"` or error message