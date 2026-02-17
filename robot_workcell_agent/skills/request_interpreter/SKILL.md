---
name: request_interpreter
description: "Main Skill 1 - Entry Point: Interprets natural language requests and identifies workcell requirements. Use when: (1) Starting any new robot workcell design task, (2) User provides task description. This is ALWAYS the first skill to use."
metadata:
  stage: "1"
  skill_type: "main"
  order: 1
---

# Request Interpreter - Stage 1 Entry Point

## Overview
The **ENTRY POINT** for all workcell design tasks. Your job is to gather requirements through conversation and output a validated Stage 1 JSON when complete.

## When to Use This Skill
- **ALWAYS** at the start of any workcell design task
- User describes what they need in natural language
- First step before any optimization or simulation

## Required Actions Checklist

When request_interpreter is loaded, you MUST:

✅ **1. Load ALL three reference guides immediately:**
   - `read_skill_file_tool("request_interpreter", "references/gap_analysis_guide.md")`
   - `read_skill_file_tool("request_interpreter", "references/standard_objects.md")`
   - `read_skill_file_tool("request_interpreter", "references/robot_selection_guide.md")`

✅ **2. Ask iterative questions** using gap_analysis_guide to prioritize

✅ **3. Use standard_objects.md** to fill in dimensions for common items

✅ **4. Use robot_selection_guide.md** to select optimal robot with justification

✅ **5. Output Stage 1 JSON** when all required fields are complete

✅ **6. Auto-proceed to placement_solver** immediately after outputting JSON

## Stage 1 Workflow

This is an **LLM-GUIDED conversational skill** - NO script execution.

### Step 1: Initial Analysis
Read the user's request and identify:
- **Task type**: palletizing, pick-place, assembly, packing, machine tending
- **Objects being manipulated**: cartons, boxes, bottles, apples, etc.
- **Workspace elements**: conveyor, pallet, table, bins
- **Robot hints**: Any specific robot mentioned?
- **Requirements**: Speed, precision, payload, safety

### Step 2: Load Reference Guides (REQUIRED)
**YOU MUST load and consult these reference guides** to properly analyze the task:

**🔍 Load `references/gap_analysis_guide.md`** to:
- Understand what information is required for Stage 1
- Identify missing critical fields
- Prioritize what questions to ask first
- Know when you have complete information

**📦 Load `references/standard_objects.md`** to:
- Get dimensions for standard objects (pallets, cartons, bottles, etc.)
- Make reasonable assumptions when user says "standard" or "typical"
- Convert vague descriptions to specific dimensions
- Always state your assumptions clearly to the user

**🤖 Load `references/robot_selection_guide.md`** to:
- Understand available robots and their capabilities
- Calculate payload requirements (object + gripper + margin)
- Match robots to task types (palletizing, assembly, etc.)
- Select optimal robot with proper justification
- For detailed specs, reference the individual robot files

**CRITICAL**: Don't guess or assume - actually load and read these guides before responding!

### Step 3: Iterative Questioning
- Ask 3-5 focused questions at a time
- Use gap_analysis_guide.md to prioritize questions
- Use standard_objects.md to fill in reasonable defaults
- Build on previous answers - don't repeat questions
- Focus on critical gaps first (dimensions, weight, throughput)

### Step 4: Spatial Reasoning & Component Planning
Once you have the information, plan the workcell components:

**REQUIRED COMPONENTS** (Always include these):
1. **Robot pedestal** - Platform to mount the robot (typically 0.75-0.9m height)
2. **Objects being manipulated** - The cartons/boxes/items for pick-place (these are components too!)
3. **Input components** - Conveyor, table, or bin where objects start
4. **Output components** - Pallet, table, or bin where objects end up
5. **Safety components** - Fencing if required

**Spatial reasoning checklist**:
- **Component arrangement**: Where should each component be positioned? (positions filled later by placement_solver - leave as null for now)
- **Material flow**: How do items move through the workcell?
- **Zones**: Define input, output, robot, buffer zones
- **Accessibility**: Ensure all pick/place points are within robot reach
- **Safety**: Consider clearances and safety fencing

**CRITICAL**: For pick-place/palletizing tasks, include the carton/box as a workcell_component (component_type: 'carton' or 'object') even though it's also in task_specification - it needs to be spawned in the simulation!

**WRONG - DO NOT DO THIS**:
```json
"workcell_components": [
  {
    "name": "robot",
    "position": [0, 0, 0.75],  // ❌ WRONG - should be null
    "orientation": [0, 0, 0, 1]  // ❌ WRONG - should be null
  }
  // ❌ Missing pedestal
  // ❌ Missing carton/box components
]
```

**RIGHT - DO THIS**:
```json
"workcell_components": [
  {
    "name": "robot_pedestal",  // ✅ Pedestal included
    "component_type": "pedestal",
    "position": null,  // ✅ Null
    "orientation": null,  // ✅ Null
    "dimensions": [0.6, 0.6, 0.5]
  },
  {
    "name": "carton_to_stack",  // ✅ Object included
    "component_type": "carton",
    "position": null,  // ✅ Null
    "orientation": null,  // ✅ Null
    "dimensions": [0.3, 0.3, 0.3]
  }
]
```

**IMPORTANT - Component Dimensions**:
- ALL workcell_components MUST have `dimensions` field populated (in meters: [L, W, H])
- Use standard dimensions from `standard_objects.md`:
  - Euro pallet: [1.2, 0.8, 0.15]
  - Medium carton: [0.3, 0.3, 0.3]
  - Conveyor (standard): [2.0, 0.64, 0.82]
  - Robot pedestal: [0.6, 0.6, 0.5]
- If user doesn't specify dimensions, use these standard values
- Dimensions are REQUIRED for placement optimization (collision detection, clearances)

**CRITICAL - Do NOT Include Robot Itself**:
- ❌ **DO NOT** add the robot arm/manipulator as a workcell component
- ✅ **ONLY** add the robot PEDESTAL/MOUNTING PLATFORM as a component
- The robot specification comes from `robot_selection` field (model, reach, payload)
- Example WRONG: `{"name": "UR10_robot", "component_type": "robot"}`  ❌
- Example RIGHT: `{"name": "robot_pedestal", "component_type": "pedestal"}`  ✅
- Workcell components are: pedestal, conveyor, pallet, carton/box, shelves, etc.
- The robot itself is mounted ON the pedestal, not a separate layout component

**Note**: All components should have `position: null` and `orientation: null` at this stage - the `placement_solver` (Stage 2) will compute optimal positions.

Use the robot's reach specification from robot_selection_guide.md to verify all positions are reachable.

### Step 5: Submit Stage 1 JSON via Tool
When you have ALL required fields, call `submit_stage1_json` tool with your JSON.

**DO NOT paste JSON in your text response — YOU MUST call the tool.**

The tool validates your JSON against the Pydantic schema:
- ✅ If valid → Stored, logged, confirmed
- ❌ If invalid → Returns specific errors to fix, then call again

Required fields checklist (review gap_analysis_guide.md):
- ✅ task_objective (clear description, min 50 chars)
- ✅ task_specification (dimensions in meters [L,W,H], weight_kg, material)
- ✅ robot_selection (model, manufacturer, payload_kg, reach_m, justification min 50 chars, urdf_path)
- ✅ workcell_components (each with name, component_type, mjcf_path ending .xml, position [x,y,z], orientation [x,y,z,w])
- ✅ spatial_reasoning (zones list, material_flow, accessibility, reasoning each min 30 chars)
- ✅ throughput_requirement (items_per_hour, cycle_time_seconds)
- ✅ constraints (list of constraint_type, description, value)
- ✅ missing_info MUST be empty array []

### Step 6: Auto-Proceed to Stage 2
**CRITICAL**: After `submit_stage1_json` returns success, **IMMEDIATELY proceed to Stage 2** without waiting:
- Say: "✅ Stage 1 complete! Proceeding to placement optimization..."
- Call `load_skill_tool("placement_solver")`
- Call `run_skill_script_tool("placement_solver", "solve_placement", {"scene_data": <the validated JSON>})`

## Stage 1 Output Schema

This is the EXACT structure to pass to `submit_stage1_json` tool:

```json
{
  "stage_1_complete": true,
  
  "task_objective": "Design a palletizing system to transfer cartons from conveyor and stack them onto pallets at 500 cartons/hour",
  
  "task_specification": {
    "name": "carton",
    "sku_id": "carton_standard_cardboard",
    "dimensions": [0.40, 0.30, 0.25],
    "weight_kg": 5.0,
    "material": "cardboard",
    "quantity": 1
  },
  
  "additional_objects": [],
  
  "robot_selection": {
    "model": "ur5",
    "manufacturer": "Universal Robots",
    "payload_kg": 5.0,
    "reach_m": 0.85,
    "justification": "UR5 selected for 5kg payload capacity, 850mm reach suitable for palletizing tasks, industrial-grade reliability",
    "urdf_path": "D:/GitHub/ieee_case/mujoco_menagerie/universal_robots_ur5e/ur5e.xml"
  },
  
  "workcell_components": [
    {
      "name": "robot_pedestal",
      "component_type": "pedestal",
      "mjcf_path": "D:/GitHub/ieee_case/workcell_components/pedestals/robot_pedestal.xml",
      "position": null,
      "orientation": null,
      "dimensions": [0.6, 0.6, 0.5]
    },
    {
      "name": "conveyor_input",
      "component_type": "conveyor",
      "mjcf_path": "D:/GitHub/ieee_case/workcell_components/conveyors/conveyor_belt.xml",
      "position": null,
      "orientation": null,
      "dimensions": [2.0, 0.64, 0.82]
    },
    {
      "name": "carton_to_palletize",
      "component_type": "carton",
      "mjcf_path": "D:/GitHub/ieee_case/workcell_components/boxes/cardboard_box.xml",
      "position": null,
      "orientation": null,
      "dimensions": [0.3, 0.3, 0.3]
    },
    {
      "name": "pallet_station_1",
      "component_type": "pallet",
      "mjcf_path": "D:/GitHub/ieee_case/workcell_components/pallets/euro_pallet.xml",
      "position": null,
      "orientation": null,
      "dimensions": [1.2, 0.8, 0.15]
    },
    {
      "name": "pallet_station_2",
      "component_type": "pallet",
      "mjcf_path": "D:/GitHub/ieee_case/workcell_components/pallets/euro_pallet.xml",
      "position": null,
      "orientation": null,
      "dimensions": [1.2, 0.8, 0.15]
    }
  ],
  
  "spatial_reasoning": {
    "zones": [
      {
        "zone_name": "input_zone",
        "zone_type": "input",
        "center_position": [-1.0, 0.0, 0.85],
        "radius_m": 0.3
      },
      {
        "zone_name": "output_zone_1",
        "zone_type": "output",
        "center_position": [1.0, -0.5, 0.5],
        "radius_m": 0.6
      },
      {
        "zone_name": "output_zone_2",
        "zone_type": "output",
        "center_position": [1.0, 0.5, 0.5],
        "radius_m": 0.6
      }
    ],
    "material_flow": "Linear flow from conveyor (left) through robot workspace to dual pallet stations (right)",
    "accessibility": "All pick and place points within 850mm robot reach. Conveyor pick point at 850mm height, pallet placement heights vary with stack level",
    "reasoning": "Robot positioned centrally to minimize travel distance. Conveyor on left provides consistent pick point. Dual pallets on right enable continuous operation during pallet changeover."
  },
  
  "throughput_requirement": {
    "items_per_hour": 500,
    "cycle_time_seconds": 7.2
  },
  
  "constraints": [
    {
      "constraint_type": "safety",
      "description": "Industrial robot requires safety fencing around workcell",
      "value": "fencing_required"
    },
    {
      "constraint_type": "throughput",
      "description": "System must handle 500 cartons per hour",
      "value": 500
    }
  ],
  
  "missing_info": []
}
```

**CRITICAL VALIDATIONS**:
- `stage_1_complete` MUST be `true`
- `missing_info` MUST be empty array `[]`
- All dimensions in meters `[length, width, height]`
- **ALL `workcell_components` MUST have `dimensions` field populated** (use standard_objects.md reference)
  - Robot pedestal: [0.6, 0.6, 0.5]
  - Euro pallet: [1.2, 0.8, 0.15]
  - Medium carton: [0.3, 0.3, 0.3]
  - Standard conveyor: [2.0, 0.64, 0.82]
- **`position` and `orientation` MUST be `null` (LITERALLY null, NOT [0,0,0] or any array)** - placement_solver will fill these in Stage 2
- `task_objective` minimum 50 characters
- Robot `justification` minimum 50 characters
- **MUST include robot pedestal as a component** (component_type: 'pedestal' or 'robot_base')
- **MUST include the manipulated object (carton/box) as a component** (component_type: 'carton', 'box', or 'object')
- For palletizing: You need BOTH the robot mounting pedestal AND the cartons being stacked

**After calling `submit_stage1_json`**:
1. Tool returns a summary (not full JSON)
2. **SHOW THIS SUMMARY to the user**
3. **ASK USER**: "Does this look correct? Should I proceed to Stage 2 (component placement optimization)?"
4. **IF user confirms** → Proceed to placement_solver
5. **IF user wants changes** → Ask what to modify, update, call `submit_stage1_json` again

## Error Handling

If user provides incomplete information:
- ❌ DON'T output the JSON yet
- ✅ Ask specific follow-up questions
- ✅ Use gap_analysis_guide.md to identify what's missing
- ✅ Continue iterating until `missing_info` can be empty

## References (Load These!)

**Core Guides** (in `references/`):
- `gap_analysis_guide.md` - How to identify missing information, question prioritization
- `standard_objects.md` - Dimensions database for common objects (pallets, cartons, bottles, etc.)
- `robot_selection_guide.md` - Robot comparison table, selection logic, all 6 robot specifications

**Detailed Robot Specs** (for in-depth analysis):
- `references/robots/franka_emika_panda.md` - 3kg payload, 855mm reach, 7-DOF collaborative
- `references/robots/ur3.md` - 3kg payload, 500mm reach, compact
- `references/robots/ur5.md` - 5kg payload, 850mm reach, most popular
- `references/robots/ur10.md` - 10kg payload, 1300mm reach, heavy-duty
- `references/robots/kuka_kr3.md` - 3kg payload, 645mm reach, precision

**Note**: Load robot_selection_guide.md first for quick selection, then load individual robot files only if you need detailed joint specifications or advanced features.
