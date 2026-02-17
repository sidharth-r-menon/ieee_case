---
name: placement_solver
description: "Main Skill 7 - Layout Optimization: Determines optimal positions for all workcell components using layout_generator.py. Use when: (1) Stage 1 requirements are complete and confirmed, (2) Need to compute optimal component positions."
metadata:
  stage: "2"
  skill_type: "main"
  order: 7
---

# Placement Solver - Layout-based Component Positioning

## Overview
Uses the `layout_generator.py` script to calculate optimal positions for all workcell components. The script employs geometric calculations to ensure collision-free layout with proper clearances and reachability.

## When to Use This Skill
- After Stage 1 JSON is validated AND user confirms to proceed
- Ready to compute optimal 3D positions for all components
- Before building the Genesis simulation

## How This Works

The `layout_generator.py` script uses a geometric algorithm instead of PSO to calculate component placements:

1. **Fixed Robot Position**: Robot and pedestal are fixed at origin [0,0,0]
2. **Conveyor Placement**: Positioned along X-axis with collision avoidance
3. **Pallet Placement**: Positioned along Y-axis with collision avoidance
4. **Target Calculation**: Computes pick/place targets for trajectory execution

### Workflow Instructions

**Step 1: Retrieve Stage 1 Data**
Use the `get_stage1_data()` tool to retrieve the validated Stage 1 JSON:
```python
stage1_data = get_stage1_data()  # Returns the complete Stage 1 dict
```

This contains:
- `robot_selection` → robot reach limit (reach_m)
- `workcell_components` → list of all components with dimensions
- `task_specification` → manipulated object dimensions
- `spatial_reasoning`, `constraints`, etc.

**Step 2: Execute Layout Generation**
Pass the Stage 1 data directly to the placement solver:

```python
run_skill_script_tool(
    "placement_solver",
    "solve_placement",
    stage1_data  # Pass the dict from get_stage1_data()
)
```

### Internal Layout Generator Logic

The `layout_generator.py` script constructs a JSON input from Stage 1 data:

### Internal Layout Generator Logic

The `layout_generator.py` script constructs a JSON input from Stage 1 data:

**Input Format** (constructed from Stage 1):
```json
{
    "robot": {
        "name": "ur5",
        "reach_max": 0.85,
        "reach_min": 0.20
    },
    "pedestal": {
        "dimensions": [0.60, 0.60, 0.50]
    },
    "conveyor": {
        "dimensions": [2.00, 0.64, 0.82]
    },
    "pallet": {
        "dimensions": [1.20, 0.80, 0.15]
    },
    "box": {
        "dimensions": [0.30, 0.30, 0.30]
    }
}
```

**Algorithm**:
1. Places pedestal and robot at origin [0,0,0]
2. Positions conveyor along X-axis using iterative collision avoidance (0.1m clearance)
3. Positions pallet along Y-axis using iterative collision avoidance (0.025m clearance)
4. Calculates pick/place targets based on surface heights and box dimensions

**Step 3: Parse Results**
Script returns:
```json
{
  "status": "success",
  "optimized_components": [
    {
      "name": "robot_pedestal",
      "component_type": "pedestal",
      "position": [0.0, 0.0, 0.0],
      "orientation": [0, 0, 0],
      "dimensions": [0.6, 0.6, 0.5],
      "mjcf_path": "workcell_components/pedestals/robot_pedestal.xml"
    },
    {
      "name": "conveyor_input",
      "component_type": "conveyor",
      "position": [1.5, 0.0, 0.0],
      "orientation": [0, 0, 0],
      "dimensions": [2.0, 0.64, 0.82],
      "mjcf_path": "workcell_components/conveyors/conveyor_belt.xml"
    },
    {
      "name": "pallet_station",
      "component_type": "pallet",
      "position": [0.0, 0.75, 0.0],
      "orientation": [0, 0, 0],
      "dimensions": [1.2, 0.8, 0.15],
      "mjcf_path": "workcell_components/pallets/euro_pallet.xml"
    }
  ],
  "layout_coordinates": {
    "pedestal_pos": [0.0, 0.0, 0.0],
    "robot_pos": [0.0, 0.0, 0.5],
    "conveyor_pos": [1.5, 0.0, 0.0],
    "pallet_pos": [0.0, 0.75, 0.0],
    "box_spawn_pos": [0.65, 0.0, 1.13],
    "pick_target_xyz": [0.65, 0.0, 1.13],
    "place_target_xyz": [0.0, 0.75, 0.46]
  },
  "motion_targets": {
    "robot_pos": [0.0, 0.0, 0.5],
    "pick_target_xyz": [0.65, 0.0, 1.13],
    "place_target_xyz": [0.0, 0.75, 0.46],
    "box_spawn_pos": [0.65, 0.0, 1.13]
  }
}
```

**Important**: The `layout_coordinates` and `motion_targets` sections are critical for:
- **Scene Building**: Genesis uses `layout_coordinates` to position components
- **Trajectory Execution**: Motion primitives use `motion_targets` for pick/place operations

**Step 4: Present to User & Ask Confirmation**
**CRITICAL**: DO NOT proceed to Stage 3 until user confirms!

Show user:
Show user:
```
✅ Stage 2 Complete - Component Placement Calculated

Component Positions:
- Robot Pedestal: [0.0, 0.0, 0.0] - Fixed at origin
- Conveyor: [1.5, 0.0, 0.0] (positioned along X-axis)
- Pallet: [0.0, 0.75, 0.0] (positioned along Y-axis)

Motion Targets:
- Pick Target: [0.65, 0.0, 1.13]
- Place Target: [0.0, 0.75, 0.46]

Does this layout look correct? Should I proceed to Stage 3 (build Genesis simulation)?
```

**Step 5: Wait for User Response**
- If user confirms → Proceed to `genesis_scene_builder`
- If user requests changes → Adjust component dimensions in Stage 1 and re-run

## Input Format (from Stage 1)

Pass the entire Stage 1 JSON directly. The script automatically extracts:
```json
{
  "robot_selection": {
    "reach_m": 0.85,
    "model": "ur5",
    ...
  },
  "workcell_components": [
    {
      "name": "robot_pedestal",
      "component_type": "pedestal",
      "dimensions": [0.6, 0.6, 0.5],
      ...
    },
    {
      "name": "conveyor",
      "component_type": "conveyor",
      "dimensions": [2.0, 0.64, 0.82],
      ...
    },
    ...
  ],
  "task_specification": {
    "dimensions": [0.3, 0.3, 0.3],  // Box dimensions
    ...
  }
}
```

**NOTE**: The script extracts component information by matching keywords:
- **Pedestal**: keywords = ['pedestal', 'base', 'mount']
- **Conveyor**: keywords = ['conveyor', 'belt']
- **Pallet**: keywords = ['pallet', 'station']
- **Box**: dimensions from task_specification or components matching ['box', 'carton', 'object']

## Layout Generator Parameters

The `layout_generator.py` uses these parameters:

- **Collision Clearances**:
  - Pedestal clearance: 0.1m
  - Pallet clearance: 0.025m
- **Positioning Strategy**:
  - Iterative radius expansion (0.05m steps)
  - 2D collision checking on XY plane
- **Z-Height Calculations**:
  - Pick Z: conveyor_height + box_height + 0.01m (air gap)
  - Place Z: pallet_height + box_height + 0.01m (air gap)
  - Box spawn Z: conveyor_height + box_height/2

## Output Schema

```json
{
  "status": "success",
  "optimized_components": [
    {
      "name": "component_name",
      "component_type": "type",
      "position": [x, y, z],
      "orientation": [roll, pitch, yaw],
      "dimensions": [length, width, height],
      "mjcf_path": "path/to/component.xml"
    }
  ],
  "layout_coordinates": {
    "pedestal_pos": [x, y, z],
    "robot_pos": [x, y, z],
    "conveyor_pos": [x, y, z],
    "pallet_pos": [x, y, z],
    "box_spawn_pos": [x, y, z],
    "pick_target_xyz": [x, y, z],
    "place_target_xyz": [x, y, z]
  },
  "motion_targets": {
    "robot_pos": [x, y, z],
    "pick_target_xyz": [x, y, z],
    "place_target_xyz": [x, y, z],
    "box_spawn_pos": [x, y, z]
  }
}
```

## How layout_generator.py Constructs the JSON

The `solve_placement.py` script automatically constructs the layout_generator input JSON from Stage 1 data:

1. **Robot Parameters**: Extracted from `robot_selection.reach_m` and `robot_selection.model`
2. **Component Dimensions**: Extracted by matching component_type or name keywords
3. **Box Dimensions**: From `task_specification.dimensions` or box component

No manual JSON construction needed - the script handles it automatically!

## Next Steps After User Confirms

The optimized_components, layout_coordinates, and motion_targets are stored and passed to:
1. **genesis_scene_builder**: Uses optimized_components and layout_coordinates
2. **motion_primitives**: Uses motion_targets for trajectory execution
3. **simulation_validator**: Validates the complete pick-place operation

Load `genesis_scene_builder` skill when user confirms to proceed to Stage 3.