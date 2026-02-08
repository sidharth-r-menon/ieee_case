---
name: robot_selector
description: "Stage 1: Selects optimal robot model based on task requirements including payload capacity, reach, and precision needs. Use when: (1) Robot model is unspecified in requirements, (2) Multiple robot options need evaluation, (3) Task characteristics suggest specific robot capabilities. Maps task descriptions to appropriate robot models from available inventory."
metadata:
  stage: "1"
---

# Robot Selector

## Overview
Intelligent robot selection based on task requirements, payload needs, reach constraints, and precision demands.

## Usage
```bash
python scripts/select_robot.py --task "packing apples" --payload 5.0 --reach 0.8
```

## Selection Criteria
- **Heavy Lifting** → fanuc_m20 (20kg payload)
- **Lab Work/Precision** → franka_panda (collaborative, precise)
- **General Assembly** → ur5 (versatile, 5kg payload)
- **Compact Spaces** → ur3 (small footprint)
- **Fast Operations** → abb_irb1200 (fast and precise)

## Input Schema
{
  "task_description": "string (e.g., 'packing apples')",
  "required_payload_kg": "float (optional)"
}

## Output Schema
{
  "selected_robot": {
    "model_id": "franka_panda",
    "reasoning": "Standard for light manipulation tasks."
  }
}