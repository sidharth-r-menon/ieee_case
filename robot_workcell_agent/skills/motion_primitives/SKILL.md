---
name: motion_primitives
description: "Runtime: Atomic robot motion primitives for iterative pick-and-place operations with validation between each phase. Use when executing robot manipulation tasks that require: (1) Step-by-step motion control with validation between phases, (2) Fine-grained debugging of motion sequences, (3) Custom pick-and-place workflows, (4) Recovery from motion failures. Each primitive (approach, grasp, lift, place, release, retreat) can be executed independently via Python scripts, enabling validation-driven workflows instead of monolithic commands. Use only during the SIMULATION/EXECUTION PHASE."
metadata:
  stage: "runtime"
---

# Motion Primitives

## Overview
This skill provides atomic robot motion primitives for iterative pick-and-place operations. Unlike monolithic pick-and-place commands, each motion primitive can be executed independently, allowing for fine-grained control and validation at every step.

## Core Philosophy
- **Atomic Operations**: Each motion is a discrete, testable unit
- **Iterative Execution**: Execute one phase → validate → proceed to next phase
- **Validation-Driven**: Each step can be validated before continuing
- **Composable**: Primitives can be combined in flexible sequences

## Motion Primitives Reference

### 1. **approach** - Pre-grasp positioning
Move above a target position with a vertical offset.
```bash
python scripts/approach.py --position "0.5,0.0,0.42" --offset 0.1
```
- **When to use**: Before grasping, to position robot above object
- **Parameters**: position (x,y,z), offset (default: 0.1m)
- **Validation**: Verify robot is positioned correctly above object

### 2. **move_to** - Direct positioning
Move robot end-effector to a specific target position.
```bash
python scripts/move_to.py --position "0.5,0.0,0.42"
```
- **When to use**: For direct positioning or moving to grasp height
- **Parameters**: position (x,y,z)
- **Validation**: Check if robot reached target position within tolerance

### 3. **grasp** - Close gripper
Close the gripper to grasp an object.
```bash
python scripts/grasp.py --object "box_1"
```
- **When to use**: After positioning at grasp location
- **Parameters**: object (name of object)
- **Validation**: Check if object is secured in gripper

### 4. **lift** - Vertical lift
Lift the grasped object vertically.
```bash
python scripts/lift.py --height 0.1
```
- **When to use**: After successful grasp
- **Parameters**: height (default: 0.1m)
- **Validation**: Verify object is lifted and remains grasped

### 5. **place** - Descend and position
Descend and place the grasped object at a target location.
```bash
python scripts/place.py --position "0.3,0.0,0.42"
```
- **When to use**: When moving to place location (at elevated height)
- **Parameters**: position (x,y,z)
- **Validation**: Check if object is at target location

### 6. **release** - Open gripper
Open the gripper to release the grasped object.
```bash
python scripts/release.py
```
- **When to use**: After placing object at target
- **Parameters**: None
- **Validation**: Verify gripper is open and object is released

### 7. **retreat** - Vertical retreat
Move the end-effector upward to retreat from object.
```bash
python scripts/retreat.py --height 0.1
```
- **When to use**: After releasing object
- **Parameters**: height (default: 0.1m)
- **Validation**: Confirm robot has cleared the object

### 8. **return_home** - Home position
Return robot to its home/neutral position.
```bash
python scripts/return_home.py
```
- **When to use**: After completing task sequence
- **Parameters**: None
- **Validation**: Verify robot is at home position

## Standard Pick-and-Place Workflow

Execute a complete pick-and-place sequence with validation at each step:

```bash
# 1. Approach pick location
python scripts/approach.py --position "0.5,0.0,0.42" --offset 0.1
# ✓ Validate: Robot positioned above object

# 2. Move down to grasp position
python scripts/move_to.py --position "0.5,0.0,0.42"
# ✓ Validate: Robot at object level

# 3. Grasp object
python scripts/grasp.py --object "box_1"
# ✓ Validate: Object secured in gripper

# 4. Lift object
python scripts/lift.py --height 0.15
# ✓ Validate: Object lifted successfully

# 5. Move to place location (raised)
python scripts/move_to.py --position "0.3,0.0,0.57"
# ✓ Validate: Robot moved to target area

# 6. Place object
python scripts/place.py --position "0.3,0.0,0.42"
# ✓ Validate: Object placed at target

# 7. Release object
python scripts/release.py
# ✓ Validate: Gripper opened, object released

# 8. Retreat
python scripts/retreat.py --height 0.1
# ✓ Validate: Robot cleared object

# 9. Return home
python scripts/return_home.py
# ✓ Validate: Robot at home position
```

## Script Output Format

All scripts return JSON for easy validation:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "position": [0.5, 0.0, 0.42],
  "timestamp": "2026-02-02T10:30:45"
}
```

**Error response**:
```json
{
  "success": false,
  "message": "Motion executor not initialized",
  "error_code": "INIT_ERROR"
}
```

## Integration Pattern

1. Execute motion primitive script
2. Parse JSON response  
3. Run validation checks (position, grasp status, collision, etc.)
4. If validation passes → proceed to next primitive
5. If validation fails → retry, adjust, or abort

## Advantages Over Monolithic Commands

- **Granular Control**: Execute and validate each phase independently
- **Debugging**: Easier to identify which phase failed
- **Flexibility**: Modify sequence based on validation results
- **Recovery**: Retry individual phases without restarting entire operation
- **Adaptability**: Insert custom logic between phases
- **Observability**: Monitor robot state at each step

## Requirements

- Motion executor must be initialized before using scripts
- Genesis simulation environment must be running
- Proper robot and gripper configuration
- All positions in meters, coordinate system: X (forward), Y (lateral), Z (vertical)
