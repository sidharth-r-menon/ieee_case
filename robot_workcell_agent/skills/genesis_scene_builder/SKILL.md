---
name: genesis_scene_builder
description: "Stage 3: Constructs Genesis physics simulation environment from layout plan. Use when: (1) Need to instantiate physical simulation, (2) Load URDF/MJCF assets with initial poses, (3) Configure physics parameters and sensors. Returns initialized scene reference for validation."
metadata:
  stage: "3"
---

# Genesis Scene Builder

## Overview
Creates complete Genesis simulation environment from optimized layout data. Handles asset loading, pose initialization, and simulation configuration.

## When to Use This Skill
- After Stage 2 placement optimization is complete and user-confirmed
- Ready to build 3D physics simulation
- First step of Stage 3 (Validation)

## Workflow Instructions for Agent

**Step 1: Prepare Layout JSON**
Take the optimized layout from `placement_solver` and save to file:
```python
import json
with open('optimized_layout.json', 'w') as f:
    json.dump(optimized_layout, f)
```

**Step 2: Execute Scene Builder**
Run the Genesis scene construction:
```bash
python skills/genesis_scene_builder/scripts/build_scene.py --layout_json "optimized_layout.json" --physics_substeps 10
```

**Step 3: Parse Build Status**
Script outputs:
```json
{
  "scene_id": "workcell_scene_123",
  "entities_spawned": [
    {"type": "robot", "model": "franka_panda", "status": "success"},
    {"type": "table", "model": "standard_table", "status": "success"}
  ],
  "simulation_ready": true,
  "build_time_ms": 1250
}
```

**Step 4: Check Build Status**
- Verify all entities spawned successfully
- Check `simulation_ready: true`
- Report any spawn failures to user

**Step 5: Present Simulation Status**
Inform user:
- Scene built successfully
- List all spawned entities
- Ready for validation

**Step 6: Next Action**
If successful → Load `simulation_validator` skill to run physics checks

## Usage
```bash
python scripts/build_scene.py --layout_json "layout_plan.json" --physics_substeps 10
```

## Asset Mapping
- **robot** → robots/franka_panda/panda.urdf
- **table** → furniture/table_standard.urdf
- **box** → objects/box_medium.urdf
- **conveyor** → machinery/conveyor_belt.urdf

## Scene Configuration
- Physics: gravity [0, 0, -9.8], dt=0.01
- Lighting: ambient + directional lights
- Camera: overhead view at [0, 0, 2.0]
- Fixed base: robot, table, conveyor

## Input Schema
{
  "layout_plan": "object",
  "physics_settings": {
    "gravity": [0, 0, -9.8],
    "substeps": 10
  }
}

## Output Schema
{
  "scene_id": "string",
  "loaded_assets": ["panda", "table", "box_1"],
  "ready_to_sim": "boolean"
}