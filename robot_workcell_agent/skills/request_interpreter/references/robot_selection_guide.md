# Robot Selection Guide

## Overview
Use this guide to select the optimal robot for the workcell task. All robots are available in the Genesis simulation with URDF/MJCF files.

## Quick Selection Logic

### Step 1: Calculate Requirements
From the task, determine:
- **Payload Required** = Object weight + Gripper weight (~1kg) + Safety margin (20%)
- **Reach Required** = Max distance from robot base to furthest pick/place point + 20% margin
- **Task Type**: Palletizing, assembly, machine tending, pick-place, etc.

### Step 2: Filter by Constraints
Eliminate robots that don't meet minimum requirements:
- ❌ Payload too low
- ❌ Reach too short
- ❌ Not suitable for environment (collaborative vs industrial)

### Step 3: Select Optimal
From remaining options, prefer:
- ✅ Best payload/reach match (not oversized)
- ✅ Appropriate for task type
- ✅ Cost-effective (smaller is cheaper)
- ✅ Industry standard (UR series most common)

## Robot Comparison Table

| Robot | Payload | Reach | DOF | Repeatability | Best For | Environment | URDF Path |
|-------|---------|-------|-----|---------------|----------|-------------|-----------|
| **Franka Panda** | 3kg | 855mm | 7 | ±0.1mm | Research, precision assembly, collaborative | Human-friendly | `mujoco_menagerie/franka_panda/panda.xml` |
| **UR3** | 3kg | 500mm | 6 | ±0.03mm | Compact spaces, light assembly, electronics | Collaborative | `mujoco_menagerie/universal_robots_ur3e/ur3e.xml` |
| **UR5** | 5kg | 850mm | 6 | ±0.03mm | Palletizing, machine tending, packaging | Industrial/Collaborative | `mujoco_menagerie/universal_robots_ur5e/ur5e.xml` |
| **UR10** | 10kg | 1300mm | 6 | ±0.05mm | Heavy palletizing, long reach tasks | Industrial | `mujoco_menagerie/universal_robots_ur10e/ur10e.xml` |
| **KUKA KR3** | 3kg | 645mm | 6 | ±0.02mm | Precision assembly, small parts | Industrial | `mujoco_menagerie/kuka_kr3/kr3.xml` |

## Selection by Payload

| Payload Range | Recommended Robots |
|---------------|-------------------|
| 0 - 2kg | Panda, UR3, KUKA KR3 |
| 2 - 4kg | Panda, UR3, UR5, KUKA KR3 |
| 4 - 6kg | UR5 |
| 6 - 10kg | UR10 |
| > 10kg | UR10 (max capacity) |

## Selection by Reach

| Reach Range | Recommended Robots |
|-------------|-------------------|
| < 500mm | UR3 |
| 500 - 700mm | UR3, KUKA KR3, Panda |
| 700 - 900mm | UR5, Panda, KUKA KR3 |
| 900 - 1300mm | UR10 |
| > 1300mm | UR10 (max 1.3m) |

## Selection by Task Type

### Palletizing (Stacking cartons, boxes)
**Best Choices**: UR5, UR10
- Need: Moderate-high payload (3-10kg), medium-long reach, speed
- **Light palletizing** (<5kg): UR5
- **Medium palletizing** (5-10kg): UR10
- **Heavy palletizing** (>10kg): UR10 (max capacity)

### Pick-and-Place (Sorting, packaging)
**Best Choices**: UR3, UR5, KUKA KR3
- Need: Moderate payload, speed, repeatability
- **Small parts**: UR3, KUKA KR3
- **Medium parts**: UR5
- **Large parts**: UR10

### Assembly (Screwing, gluing, fitting)
**Best Choices**: Panda, KUKA KR3, UR3
- Need: High precision, 6-7 DOF, sensitive force control
- **Research/Collaborative**: Panda (7-DOF)
- **Industrial precision**: KUKA KR3
- **Standard assembly**: UR3, UR5

### Machine Tending (CNC loading)
**Best Choices**: UR5, UR10
- Need: Moderate-high payload, reach, reliability
- **Small machines**: UR5
- **Large machines**: UR10

## Selection Examples

### Example 1: Palletizing 5kg cartons
**Requirements**:
- Payload: 5kg + 1kg gripper = 6kg
- Reach: ~800mm (conveyor to pallet)
- Task: Repetitive palletizing

**Analysis**:
- ❌ Panda, UR3, KUKA KR3: Payload too low (<5kg)
- ✅ UR5: 5kg payload (exactly matches requirement)
- ✅ UR10: 10kg payload (oversized, higher cost)

**Selection**: **UR5** - Exactly meets payload requirement, 850mm reach covers workspace, industry standard for palletizing, cost-effective

## Detailed Specifications

For complete specifications including joint ranges, speeds, and advanced features, refer to individual robot files:

- `robots/franka_emika_panda.md`
- `robots/ur3.md`
- `robots/ur5.md`
- `robots/ur10.md`
- `robots/kuka_kr3.md`

**Note**: Only UR-series, Franka Panda, and KUKA KR3 robots are available in the simulation asset library.

## Output Format

When you've selected a robot, add it to Stage 1 JSON:

```json
{
  "robot_selection": {
    "model": "ur5",
    "manufacturer": "Universal Robots",
    "payload_kg": 5.0,
    "reach_m": 0.85,
    "justification": "UR5 selected for 5kg payload capacity matching the carton weight, 850mm reach covers conveyor to pallet distance, proven reliability for palletizing applications",
    "urdf_path": "mujoco_menagerie/universal_robots_ur5e/ur5e.xml"
  }
}
```

**Justification must explain**:
1. Why payload is sufficient
2. Why reach is adequate
3. Why this robot fits the task type

## Critical Reminders

- Always add 1kg for gripper weight
- Add 20% safety margin to reach calculations
- Consider cycle time requirements
- Verify robot fits in available workspace
- For collaborative tasks near humans, prefer Panda or UR series
