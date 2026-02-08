---
name: placement_solver
description: "Stage 2: Calculates optimal (x, y, theta) positions for all entities using PSO algorithms. Use when: (1) Need to position multiple entities in workspace, (2) Optimize layout for reachability and collision avoidance, (3) Satisfy spatial constraints from region proposer. Iteratively minimizes cost function based on IK, collisions, and zone constraints."
metadata:
  stage: "2"
---

# Placement Solver

## Overview
Optimizes spatial positioning of all workcell entities through PSO (Particle Swarm Optimization). Balances competing objectives: reachability, collision avoidance, and zone compliance.

## When to Use This Skill
- After Stage 1 is complete (all requirements gathered)
- After `region_proposer` has defined spatial zones
- Ready to compute optimal layout positions

## Workflow Instructions for Agent

**Step 1: Prepare Layout Data**
Create a JSON file with:
- List of entities to place (robot, table, objects)
- Defined zones from `region_proposer`
- Any positioning constraints

**Step 2: Execute PSO Script**
Run the optimization:
```bash
python skills/placement_solver/scripts/solve_placement.py --scene_json "layout_data.json" --algorithm "pso" --iterations 100
```

**Step 3: Parse Results**
Script outputs:
```json
{
  "optimized_layout": {
    "robot": {"position": [0.0, 0.0, 0.0], "orientation": [0, 0, 0]},
    "table": {"position": [0.5, 0.3, 0.0], "orientation": [0, 0, 0]}
  },
  "optimization_metrics": {
    "final_cost": 8.5,
    "iterations": 100,
    "convergence": "good"
  }
}
```

**Step 4: Interpret Quality**
- **Excellent**: cost < 10 (ready for simulation)
- **Good**: 10 ≤ cost < 50 (acceptable, minor issues)
- **Poor**: cost ≥ 50 (consider adjusting constraints)

**Step 5: Present Results to User**
Show:
- Optimized positions for each entity
- Cost metrics and quality assessment
- **CRITICAL**: ASK FOR USER CONFIRMATION before proceeding to Stage 3

**Step 6: Wait for Confirmation**
DO NOT proceed to Stage 3 until user explicitly confirms the layout.

**Step 7: Next Action**
Once confirmed → Load `genesis_scene_builder` skill

## Usage
```bash
python scripts/solve_placement.py --scene_json "scene.json" --algorithm "pso" --iterations 100
```

## Algorithm Selection
- **PSO (default)**: Fast convergence, good for moderate complexity (30 particles, social+cognitive forces)
- **Diffusion**: More thorough exploration, better for complex layouts (gradient descent with noise)

## Cost Function
1. **IK Reachability** (weight: 5.0): Penalize unreachable positions
2. **Collision Avoidance** (weight: 100.0): Heavy penalty for interpenetration
3. **Zone Compliance** (weight: 50.0): Penalize zone boundary violations

## Output Quality
- **Excellent**: cost < 10
- **Good**: 10 ≤ cost < 50  
- **Acceptable**: cost ≥ 50

## Input Schema
{
  "entities_to_place": "array",
  "defined_zones": "array (Output from Region Proposer)",
  "algorithm": "string ('pso' | 'diffusion')",
  "iterations": 100
}

## Output Schema
{
  "status": "success",
  "placements": "array (List of entity IDs and their final x,y,z,quat)",
  "final_cost_score": "float (lower is better)"
}