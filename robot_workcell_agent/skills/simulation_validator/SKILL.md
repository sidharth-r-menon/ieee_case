---
name: simulation_validator
description: "Stage 3: Validates physical feasibility through simulation. Use when: (1) Need to verify layout stability and safety, (2) Check for collisions and static equilibrium, (3) Validate robot reachability with IK. Runs simulation loop and reports pass/fail with specific failure reasons."
metadata:
  stage: "3"
---

# Simulation Validator

## Overview
Executes physics simulation to verify layout feasibility. Performs multiple validation checks to ensure safe, stable, and reachable workcell configuration.

## Usage
```bash
python scripts/validate_simulation.py --scene_id "scene_1234" --checks "stability,collision,ik" --sim_steps 200
```

## Validation Checks

### 1. Static Stability
- Simulates physics for N steps
- Checks for toppling (high aspect ratio objects)
- Monitors orientation changes
- **Pass**: All objects remain stable

### 2. Collision Detection
- Checks all entity pairs for interpenetration
- Uses bounding box overlap detection
- Includes safety margins
- **Pass**: No collisions detected

### 3. IK Reachability
- Calculates 2D distance from robot to objects
- Compares against robot max reach
- **Pass**: All objects within reach envelope

## Result Format
- **pass**: All checks passed
- **fail**: One or more checks failed with specific reasons

## Input Schema
{
  "scene_id": "string",
  "checks_required": ["stability", "collision", "ik_reachability"]
}

## Output Schema
{
  "result": "pass/fail",
  "failure_reason": "string (e.g., 'Collision detected between Robot_Link_5 and Table')",
  "sim_data": "object (Optional telemetry)"
}