---
name: request_interpreter
description: "Stage 1 — Requirements Gathering: Interprets any robot workcell request, gathers requirements via conversation, selects robot, and submits validated JSON via submit_stage1_json. ALWAYS the first skill to use for any new task."
metadata:
  stage: "1"
  skill_type: "main"
  order: 1
---

# Request Interpreter — Stage 1 Entry Point

## Overview
Entry point for all workcell design tasks. Gather requirements through conversation and submit a validated Stage 1 JSON via `submit_stage1_json`.

## Workflow

**Step 1 — Load reference guides (do this immediately after loading this skill)**
Call all three in parallel before doing anything else:
- `read_skill_file_tool('request_interpreter', 'references/gap_analysis_guide.md')` — gap identification checklist
- `read_skill_file_tool('request_interpreter', 'references/standard_objects.md')` — standard dimensions for common objects
- `read_skill_file_tool('request_interpreter', 'references/robot_selection_guide.md')` — robot specs, payload/reach selection logic

**Step 2 — Parse the request**
Identify: task type (palletizing/pick-place/assembly), objects, workspace elements, robot hints, speed requirements.


**Step 3 — Ask iterative questions (3-5 per round)**
**After loading the references, you MUST ask the user a set of requirements-gathering questions and wait for their answers before constructing the Stage 1 JSON.**
Use the gap_analysis_guide to identify critical gaps. Focus on: object dimensions, weight, throughput. Apply standard_objects.md when user says "standard/typical". State any assumed values clearly.

**Step 4 — Select robot** using robot_selection_guide.md logic: calculate payload (object weight + 1 kg gripper + 20% margin) and reach requirements.

**Step 5 — Plan workcell components**
Always include (all `position` and `orientation` must be `null`):
1. `robot_pedestal` (type: `pedestal`)
2. The manipulated object (type: `carton` / `box` / `object`)
3. Input source (type: `conveyor`)
4. Output destination (type: `pallet`)

⚠️ Do NOT add grippers, suction cups, or end-effectors as workcell_components. The gripper is built into the robot model. Including it causes simulation errors.

**Step 6 — Submit via tool (MANDATORY gateway to Stage 2)**
When the user says "proceed", "looks good", "confirm", or "next step" — or when you have all required info — call `submit_stage1_json(data)` immediately. **Never write a text design report and never load any other skill.** The tool is the only way to advance. Fix validation errors and retry. On success, show the returned summary to the user and wait for their explicit confirmation before Stage 2.

---

## Standard Dimensions (use when user says "standard/typical")

| Item | Dimensions [L, W, H] m | Weight |
|------|------------------------|--------|
| Robot Pedestal | [0.60, 0.60, 0.50] | — |
| Conveyor Belt | [2.00, 0.64, 0.82] | — |
| Euro Pallet | [1.20, 0.80, 0.15] | — |
| US Pallet | [1.22, 1.02, 0.144] | — |
| Small Carton | [0.20, 0.15, 0.15] | 1-2 kg |
| Medium Carton | [0.30, 0.30, 0.30] | 3-8 kg |
| Large Carton | [0.60, 0.40, 0.40] | 10-15 kg |
| 500 ml Bottle | [0.07, 0.07, 0.20] | 0.5 kg |
| Apple | [0.08, 0.08, 0.09] | 0.2 kg |
| Small Bin | [0.30, 0.20, 0.15] | — |

---

## Robot Selection

**Payload calc**: object weight + 1 kg gripper + 20% margin. **Reach calc**: max pick/place distance + 20%.

| Robot | Payload | Reach | Best For | urdf_path |
|-------|---------|-------|----------|-----------|
| UR3 | 3 kg | 500 mm | Compact, light assembly | `mujoco_menagerie/universal_robots_ur3e/ur3e.xml` |
| UR5 | 5 kg | 850 mm | Palletizing, packaging (most common) | `mujoco_menagerie/universal_robots_ur5e/ur5e.xml` |
| UR10 | 10 kg | 1300 mm | Heavy palletizing, long reach | `mujoco_menagerie/universal_robots_ur10e/ur10e.xml` |
| Franka Panda | 3 kg | 855 mm | Precision assembly, research | `mujoco_menagerie/franka_emika_panda/panda.xml` |
| KUKA KR3 | 3 kg | 645 mm | Precision small parts | `mujoco_menagerie/kuka_iiwa_14/iiwa_14.xml` |

Payload ranges: 0–3 kg → UR3/Panda/KR3 | 3–5 kg → UR5 | 5–10 kg → UR10.

---

## Gap Analysis — Critical Fields (ask if missing)

- Object **dimensions** [L, W, H] and **weight** — affects robot selection
- **Throughput** (items/hour or cycle time)
- **Workspace constraints** (space, safety fencing)
- **Material type** — affects gripper

Optional (can infer): exact orientations, brand preferences.

---

## Required JSON for `submit_stage1_json` — copy this template exactly

```json
{
  "stage_1_complete": true,
  "task_objective": "<string, ≥50 chars describing the full task>",
  "task_specification": {
    "name": "Cardboard Carton",
    "sku_id": "CARTON-001",
    "dimensions": [0.30, 0.30, 0.30],
    "weight_kg": 4.0,
    "material": "cardboard",
    "quantity": 1
  },
  "additional_objects": [],
  "robot_selection": {
    "model": "UR5",
    "manufacturer": "Universal Robots",
    "payload_kg": 5.0,
    "reach_m": 0.85,
    "justification": "<string, ≥50 chars explaining why this robot was chosen>",
    "urdf_path": null
  },
  "workcell_components": [
    {
      "name": "Robot Pedestal",
      "component_type": "pedestal",
      "mjcf_path": "workcell_components/pedestals/robot_pedestal.xml",
      "position": null,
      "orientation": null,
      "dimensions": [0.60, 0.60, 0.50]
    },
    {
      "name": "Conveyor Belt",
      "component_type": "conveyor",
      "mjcf_path": "workcell_components/conveyors/conveyor_belt.xml",
      "position": null,
      "orientation": null,
      "dimensions": [2.00, 0.64, 0.82]
    },
    {
      "name": "Euro Pallet",
      "component_type": "pallet",
      "mjcf_path": "workcell_components/pallets/euro_pallet.xml",
      "position": null,
      "orientation": null,
      "dimensions": [1.20, 0.80, 0.15]
    },
    {
      "name": "Carton",
      "component_type": "carton",
      "mjcf_path": "workcell_components/boxes/cardboard_box.xml",
      "position": null,
      "orientation": null,
      "dimensions": [0.30, 0.30, 0.30]
    }
  ],
  "spatial_reasoning": {
    "zones": [
      {
        "zone_name": "Pick Zone",
        "zone_type": "pick",
        "center_position": [1.5, 0.0, 0.82],
        "radius_m": 0.5
      },
      {
        "zone_name": "Place Zone",
        "zone_type": "place",
        "center_position": [0.0, 0.75, 0.15],
        "radius_m": 0.6
      }
    ],
    "material_flow": "Cartons arrive on conveyor, robot picks each one and stacks onto pallet.",
    "accessibility": "Robot centrally positioned between conveyor and pallet, full reach coverage.",
    "reasoning": "Minimise travel distance between pick and place targets to meet cycle time."
  },
  "throughput_requirement": {
    "items_per_hour": 500,
    "cycle_time_seconds": 7.2
  },
  "constraints": [],
  "missing_info": []
}
```

**Rules** (do NOT deviate):
- `position` / `orientation` MUST be `null` — never `[0,0,0]`
- `mjcf_path` must be the relative path shown above — never absolute
- Do NOT add the robot arm itself as a component; add only the pedestal
- Do NOT add grippers or end-effectors as components
- Always include the manipulated object (carton/box) in `workcell_components`
- `task_objective` ≥ 50 chars; robot `justification` ≥ 50 chars
- `throughput_requirement` must have keys `items_per_hour` and `cycle_time_seconds` (not `target_units`, not a plain integer)
