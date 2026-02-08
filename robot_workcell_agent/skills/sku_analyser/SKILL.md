---
name: sku_analyser
description: "Stage 1: Resolves object keywords to specific asset IDs and retrieves dimensional data. Use when: (1) User mentions objects by common names without specific IDs, (2) Need to map natural language object descriptions to mesh/asset identifiers, (3) Require object dimensions for spatial planning. Searches asset database and returns precise identifiers."
metadata:
  stage: "1"
---

# SKU Analyzer

## Overview
Translates common object names into specific asset IDs with dimensional metadata. Bridges natural language object references with technical asset identifiers.

## Usage
```bash
python scripts/analyze_sku.py --keyword "apple"
```

## Supported Categories
- **Fruits**: apple, orange, banana
- **Containers**: box, bin (small/medium/large)
- **Bottles**: bottle, water bottle
- **Shapes**: cube, cylinder, sphere
- **Tools**: screwdriver, wrench
- **Furniture**: table, workbench, shelf
- **Machinery**: conveyor

## Example Mappings
- "apple" → mesh_fruit_apple_01 [0.08, 0.08, 0.09] 0.2kg
- "box" → container_cardboard_medium [0.3, 0.3, 0.2] 0.5kg
- "bottle" → bottle_plastic_500ml [0.07, 0.07, 0.2] 0.5kg

## Input Schema
{
  "object_keyword": "string"
}

## Output Schema
{
  "sku_id": "string",
  "dimensions": [0.1, 0.1, 0.1]
}