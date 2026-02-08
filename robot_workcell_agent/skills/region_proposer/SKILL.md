---
name: region_proposer
description: "Stage 2: Analyzes task workflow to divide workspace into logical regions (Safe Zones, Work Zones, Exclusion Zones). Use when: (1) Need to spatially organize workcell layout, (2) Define placement constraints for entities, (3) Create zones based on task type (pick_place, assembly, packing). Outputs bounded regions with priority levels."
metadata:
  stage: "2"
---

# Region Proposer

## Overview
Divides workspace surface into logical, task-appropriate regions. Creates spatial organization framework for placement optimization.

## Usage
```bash
python scripts/propose_regions.py --task_type "pick_place" --table_dims "1.5,1.0"
```

## Task-Specific Layouts
- **pick_place**: Input zone (left) + Output zone (right)
- **assembly**: Central assembly zone + Peripheral parts zones
- **packing**: Input tray + Packing zone + Output stack

## Zone Types
- **Robot Base Zone**: Reserved area for robot mounting (priority 1)
- **Work Zones**: Primary manipulation areas (priority 2-3)
- **Storage Zones**: Material staging areas (priority 2)
- **Exclusion Zones**: Safety margins and reserved spaces (priority 0)

## Input Schema
{
  "task_type": "string (e.g., 'pick_place', 'assembly')",
  "table_dims": [1.5, 1.0],
  "required_zones": ["robot_base", "input_tray", "output_stack"]
}

## Output Schema
{
  "zones": [
    {
      "zone_id": "robot_base_zone",
      "bounds_min": [-0.2, -0.5],
      "bounds_max": [0.2, -0.3],
      "priority": 1
    },
    {
      "zone_id": "input_tray_zone",
      "bounds_min": [0.4, 0.1],
      "bounds_max": [0.8, 0.4],
      "priority": 2
    }
  ]
}