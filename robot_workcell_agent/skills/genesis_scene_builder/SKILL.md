---
name: genesis_scene_builder
description: "Main Skill 8 - Scene Construction: Builds the Genesis simulation and spawns all components. Use when: (1) Layout is optimized, (2) Ready to create the physical simulation."
metadata:
  stage: "3"
  skill_type: "main"
  order: 8
  substeps:
    - simulation_validator
---

# Genesis Scene Builder

## CRITICAL - Script Name

**ONLY ONE SCRIPT EXISTS: `build_and_execute`**

❌ **DO NOT CALL:** `build_scene` (deleted, does not exist)
✅ **ALWAYS CALL:** `build_and_execute`

Script path: `skills/genesis_scene_builder/scripts/build_and_execute.py`

## Overview
Builds the Genesis simulation scene with all workcell components AND executes the pick-place trajectory in one smooth workflow.

**Based on genesis_world_pnp_4.py complete implementation**

## Workflow

**MANDATORY: Follow ALL 4 steps - DO NOT skip any!**

### Required Steps (Execute in Order)

**Step 1: Get Stage 2 Data**
```python
stage2_data = get_stage2_data()
```

**Step 2: Prepare Genesis Input (merges Stage 1 + Stage 2)**
```python
genesis_input = prepare_genesis_input()  # Includes trajectory params automatically!
```

**Step 3: Fix Component Paths**
```python
fixed_genesis = fix_genesis_paths(genesis_input)
```

**Step 4: Execute Genesis Scene Builder**
```python
# Call the ONLY script that exists
# Trajectory execution happens automatically (execute_trajectory=True by default)
result = run_skill_script_tool("genesis_scene_builder", "build_and_execute", fixed_genesis)
```

**Complete Example:**
```python
# CORRECT - Full workflow (trajectory params auto-included)
genesis_input = prepare_genesis_input()  # Auto-includes execute_trajectory, motion_targets, z_lift
fixed_genesis = fix_genesis_paths(genesis_input)
result = run_skill_script_tool("genesis_scene_builder", "build_and_execute", fixed_genesis)
```

### Common Errors (DO NOT DO THESE!)

❌ **WRONG: Passing empty dict**
```python
run_skill_script_tool("genesis_scene_builder", "build_and_execute", {})  # NO DATA!
```

❌ **WRONG: Using old script name**
```python
run_skill_script_tool("genesis_scene_builder", "build_scene", fixed_genesis)  # SCRIPT DELETED!
```

❌ **WRONG: Skipping fix_genesis_paths**
```python
genesis_input = prepare_genesis_input()
run_skill_script_tool("genesis_scene_builder", "build_and_execute", genesis_input)  # PATHS BROKEN!
```

✅ **CORRECT: Complete 3-step workflow**
```python
genesis_input = prepare_genesis_input()  # Auto-includes trajectory params
fixed_genesis = fix_genesis_paths(genesis_input)
result = run_skill_script_tool("genesis_scene_builder", "build_and_execute", fixed_genesis)
```

**What happens:**
1. Genesis initializes and creates viewer
2. All components spawn (robot, pedestal, conveyor, pallet, carton)
3. Scene builds
4. Robot immediately executes 6-phase pick-place trajectory:
   - HOVER PICK → PLUNGE → LIFT → HOVER PLACE → DROP → RETRACT
5. Result returns success/failure
6. Viewer stays open for inspection

**When to use:**
- User says "proceed to stage 3", "build the scene", "run simulation"
- User says "yes", "proceed", "do that" after Stage 2
- User wants to execute trajectory or validate the design
- **ALWAYS - this is the default and only workflow**

## What the Script Does

The `build_and_execute.py` script does the complete workflow (like pnp_4.py):

```python
# Initialize Genesis
gs.init(backend=gs.gpu)
scene = gs.Scene(show_viewer=True)
scene.add_entity(gs.morphs.Plane())

# Spawn all components (robot + workcell items)
for component in components:
    entity = scene.add_entity(gs.morphs.MJCF(file=urdf, pos=position))
    if component_type == "robot":
        robot_entity = entity

# Build scene
scene.build()

# Set robot initial pose
robot_entity.set_dofs_position([0.0, -1.57, 1.57, -1.57, -1.57, 0.0])

# Execute trajectory if requested
if execute_trajectory:
    # Get end effector and targets
    end_effector = robot_entity.get_link('wrist_3_link')
    
    # Execute 6-phase pick-place sequence
    execute_trajectory(...)  # HOVER PICK
    execute_trajectory(...)  # PLUNGE
    execute_trajectory(...)  # LIFT
    execute_trajectory(...)  # HOVER PLACE
    execute_trajectory(...)  # DROP
    execute_trajectory(...)  # RETRACT
    
# Keep viewer alive
while True:
    scene.step()
```

# Spawn all components
for component in components:
    scene.add_entity(gs.morphs.MJCF(file=urdf, pos=position))

# Build scene
scene.build()
```

## Output

**Success:**
```json
{
  "success": true,
  "spawned_components": [
    {"component_name": "UR5", "status": "spawned"},
    {"component_name": "Robot Pedestal", "status": "spawned"},
    {"component_name": "Conveyor", "status": "spawned"},
    {"component_name": "Pallet", "status": "spawned"},
    {"component_name": "Carton", "status": "spawned"}
  ],
  "robot_available": true,
  "trajectory_executed": true,
  "trajectory_status": "success",
  "trajectory_log": ["HOVER PICK", "PLUNGE", "LIFT", "HOVER PLACE", "DROP", "RETRACT"],
  "phases_completed": 6,
  "message": "Genesis scene built successfully. Trajectory executed successfully."
}
```

**Trajectory Failure:**
```json
{
  "success": true,
  "spawned_components": [...],
  "robot_available": true,
  "trajectory_executed": true,
  "trajectory_status": "failed",
  "trajectory_error": "HOVER PICK failed - no path found",
  "message": "Genesis scene built successfully. Trajectory failed: HOVER PICK failed"
}
```

**IMPORTANT: Genesis Runs in Separate Window**

After calling `build_and_execute`, the Genesis simulator will:
1. ✅ Open in a **NEW TERMINAL WINDOW** (decoupled from agent)
2. 👁️ Display the **Genesis 3D viewer** showing the workcell
3. 🤖 **Immediately execute the pick-place trajectory**
4. 🔄 Keep running after trajectory completes for inspection
5. 📊 Show all Genesis logs in its dedicated terminal

**What You Should Tell User:**

If trajectory succeeds:
```
✅ Design validated successfully!

The Genesis 3D viewer is now open showing your workcell. The robot just executed a complete pick-and-place cycle:
- ✅ All 6 trajectory phases completed
- ✅ Robot picked carton from conveyor at [0.65, 0.0, 1.13]
- ✅ Robot placed carton on pallet at [0.0, 0.75, 0.46]

The viewer will stay open so you can inspect the final configuration.
Your palletizing system design is complete and validated!
```

If trajectory fails:
```
⚠️ Trajectory execution failed during [PHASE_NAME]

The Genesis viewer is open. The issue suggests the component layout may need adjustment.
Possible fixes:
- Adjust component positions in Stage 2
- Modify pick/place targets
- Check for collisions or unreachable positions

Would you like to iterate on the layout?
```

## Validation

- **Scene Build Success**: All components spawned, scene built, viewer open
- **Trajectory Success**: All 6 phases completed without errors
- **Trajectory Failure**: Path planning failed (indicates layout issue)

## Next Step

**Design complete!** Report results to user and offer:
- Inspection of the Genesis viewer
- Iteration on layout if trajectory failed
- Export of final configuration

- `name` (string): Unique name for the component
- `urdf` (string, optional): Path to a URDF or MJCF file (use `.xml` for MJCF)
- `size` (array of 3 floats, optional): Size `[x, y, z]` for box primitives
- `position` (array of 3 floats): Position `[x, y, z]` in the scene
- `orientation` (array of 3 floats, optional): Euler angles `[roll, pitch, yaw]` (default `[0,0,0]`)

### Complete Example

```json
[
  {
    "name": "robot1",
    "urdf": "D:/GitHub/ieee_case/mujoco_menagerie/franka_emika_panda/panda.xml",
    "position": [0.0, 0.0, 0.82],
    "orientation": [0, 0, 0]
  },
  {
    "name": "robot_pedestal",
    "urdf": "D:/GitHub/ieee_case/workcell_components/pedestals/robot_pedestal.xml",
    "position": [0.0, 0.0, 0.45],
    "orientation": [0, 0, 0]
  },
  {
    "name": "work_table",
    "urdf": "D:/GitHub/ieee_case/workcell_components/tables/workbench.xml",
    "position": [1.0, 0.0, 0.4],
    "orientation": [0, 0, 0]
  },
  {
    "name": "conveyor1",
    "urdf": "D:/GitHub/ieee_case/workcell_components/conveyors/conveyor_belt.xml",
    "position": [-1.5, 0.0, 0.4],
    "orientation": [0, 0, 0]
  },
  {
    "name": "pallet1",
    "urdf": "D:/GitHub/ieee_case/workcell_components/pallets/euro_pallet.xml",
    "position": [1.5, 1.0, 0.072],
    "orientation": [0, 0, 0]
  },
  {
    "name": "box1",
    "urdf": "D:/GitHub/ieee_case/workcell_components/boxes/medium_box.xml",
    "position": [1.0, 0.0, 0.9],
    "orientation": [0, 0, 0]
  }
]
```
## Asset Path Construction

The Genesis Scene Builder uses two main asset directories:

1. **Robots**: `D:/GitHub/ieee_case/mujoco_menagerie/`
2. **Workcell Components**: `D:/GitHub/ieee_case/workcell_components/`

### Robot Assets

Robots are located in the `mujoco_menagerie` directory with the following path format:

```
D:/GitHub/ieee_case/mujoco_menagerie/<robot_name>/<robot_file>.xml
```

**Available Robots:**
- Franka Emika Panda: `D:/GitHub/ieee_case/mujoco_menagerie/franka_emika_panda/panda.xml`
- Universal Robots UR3: `D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur3/ur3.xml`
- Universal Robots UR5: `D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur5/ur5.xml`
- Universal Robots UR10: `D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur10/ur10.xml`
- ABB IRB1200: `D:/GitHub/ieee_case/mujoco_menagerie/abb_irb1200/irb1200.xml`
- KUKA KR3: `D:/GitHub/ieee_case/mujoco_menagerie/kuka_kr3/kr3.xml`

### Workcell Component Assets

Workcell components are located in the `workcell_components` directory:

**Tables:**
- Standard Table: `D:/GitHub/ieee_case/workcell_components/tables/standard_table.xml`
- Workbench: `D:/GitHub/ieee_case/workcell_components/tables/workbench.xml`

**Boxes:**
- Small Box: `D:/GitHub/ieee_case/workcell_components/boxes/small_box.xml`
- Medium Box: `D:/GitHub/ieee_case/workcell_components/boxes/medium_box.xml`
- Cardboard Box: `D:/GitHub/ieee_case/workcell_components/boxes/cardboard_box.xml`

**Conveyors:**
- Conveyor Belt: `D:/GitHub/ieee_case/workcell_components/conveyors/conveyor_belt.xml`

**Pedestals:**
- Robot Pedestal: `D:/GitHub/ieee_case/workcell_components/pedestals/robot_pedestal.xml`

**Pallets:**
- Euro Pallet: `D:/GitHub/ieee_case/workcell_components/pallets/euro_pallet.xml`

**Important:** Always use forward slashes `/` in paths to avoid Windows path issues.


## Usage

The agent automatically calls this skill using `run_skill_script_tool`:

```python
result = run_skill_script_tool("genesis_scene_builder", "build_and_execute", genesis_input)
```

The script is called internally by the agent - users never run it directly.

## Output
The script outputs a JSON summary of all spawned components and their status:
```json
{
  "spawned_components": [
    {
      "component_name": "robot1",
      "urdf": "robots/franka_panda/panda.urdf",
      "size": null,
      "position": [0.0, 0.0, 0.42],
      "orientation": [0, 0, 0],
      "status": "spawned"
    },
    {
      "component_name": "table1",
      "urdf": "furniture/table_standard.urdf",
      "size": null,
      "position": [0.5, 0.0, 0.2],
      "orientation": [0, 0, 0],
      "status": "spawned"
    },
    {
      "component_name": "box1",
      "urdf": null,
      "size": [0.1, 0.1, 0.1],
      "position": [0.7, 0.0, 0.5],
      "orientation": [0, 0, 0],
      "status": "spawned"
    }
  ],
  "success": true
}
```

## Notes
- The skill does not perform layout, optimization, or validation—only spawning.
- URDFs with `.xml` extension are treated as MJCF.
- If both `urdf` and `size` are provided, `urdf` takes precedence.
- The ground plane is always added automatically.

## Agent Workflow

**Pre-requisites:**
1. Stage 2 complete with optimized component positions
2. ALL components from placement_solver output (robot pedestal, conveyor, pallet, carton/box, etc.)

**CRITICAL - Component Integrity**:
- **DO NOT drop any components** between Stage 2 and Stage 3
- If placement_solver returned 4 components, pass ALL 4 PLUS the robot to genesis
- Missing components (especially robot or pedestal) will cause incomplete simulations
- Verify component count matches before calling build_and_execute

**Steps for Agent:**

1. **Extract ALL Optimized Components**
   - Get the complete list from placement_solver output: `optimized_components`
   - Include: robot pedestal, input components (conveyor), output components (pallet), objects (carton/box)
   - Do NOT filter or remove any components

2. **Add Robot Component**
   - Robot data goes in separate `"robot"` key in input JSON
   - Robot URDF: `D:/GitHub/ieee_case/mujoco_menagerie/<robot_folder>/<robot_file>.xml`
   - Robot position comes from Stage 2 motion_targets: `robot_pos`

3. **Construct Full Paths for Other Components**
   - Components: `D:/GitHub/ieee_case/workcell_components/<category>/<component>.xml`
   - Use positions from placement_solver output exactly as provided

4. **Build Input JSON Structure**
   ```python
   genesis_input = {
       "robot": {
           "name": "UR5",
           "urdf": "D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur5e/ur5e.xml",
           "position": [0.0, 0.0, 0.5]
       },
       "components": [
           {"name": "Robot Pedestal", "component_type": "pedestal", "urdf": "...", "position": [...]},
           {"name": "Conveyor", "component_type": "conveyor", "urdf": "...", "position": [...]},
           {"name": "Pallet", "component_type": "pallet", "urdf": "...", "position": [...]},
           {"name": "Carton", "component_type": "box", "urdf": "...", "position": [...]}
       ],
       "execute_trajectory": True,
       "motion_targets": {
           "pick_target_xyz": [0.65, 0.0, 1.13],
           "place_target_xyz": [0.0, 0.75, 0.46]
       },
       "z_lift": 0.4
   }
   ```

5. **Execute build_and_execute Script**
   ```python
   result = run_skill_script_tool("genesis_scene_builder", "build_and_execute", genesis_input)
   ```
   
   **CRITICAL - Do NOT Interrupt Execution:**
   - Genesis simulation initialization takes time (30-60 seconds)
   - You will see output like "[Genesis] [INFO] Initializing..."
   - Trajectory execution adds another 10-20 seconds
   - **DO NOT abort or stop** - Wait for complete execution
   - The script will output JSON when complete with trajectory results
   - Only report completion AFTER seeing the final JSON output

6. **Verify Output**
   - Check `success: true` in output
   - Check `robot_available: true` (confirms robot was spawned)
   - Check `trajectory_status: "success"` or `"failed"`
   - Verify all components have `status: "spawned"`

**Reference:**
- See `references/asset_organization.md` for complete asset catalog
- See `references/component_catalog.md` for quick reference paths