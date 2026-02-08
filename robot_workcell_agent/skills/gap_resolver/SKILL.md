---
name: gap_resolver
description: "Stage 1: Analyzes partial scene data to identify and resolve missing information. Use when: (1) Scene JSON has null or TBD fields, (2) Need to validate completeness of requirements, (3) Need to generate clarifying questions for user. Attempts automatic resolution via robot-selector and sku-analyzer before prompting user."
metadata:
  stage: "1"
---

# Gap Resolver

## Overview
Smart gap analyzer that identifies missing data and categorizes by priority (critical/important/optional). Tells you what still needs resolution before proceeding.

## When to Use This Skill
- After `request_interpreter` returns partial scene data with null/TBD fields
- User provides incomplete information
- Need to validate completeness before Stage 2

## Workflow Instructions for Agent

**Step 1: Save Scene Data to File**
Write the current `partial_scene_data` to a temporary JSON file:
```python
import json
with open('temp_scene.json', 'w') as f:
    json.dump(partial_scene_data, f)
```

**Step 2: Execute Script**
Run the gap analysis script:
```bash
python skills/gap_resolver/scripts/resolve_gaps.py --scene_json "temp_scene.json"
```

**Step 3: Parse JSON Output**
The script outputs:
```json
{
  "gaps": [
    {
      "field": "robot_configuration.model_id",
      "type": "missing_robot",
      "priority": "critical",
      "description": "Robot model not specified",
      "has_default": false
    }
  ],
  "is_complete": false,
  "summary": {
    "critical_count": 1,
    "important_count": 2,
    "optional_count": 1
  }
}
```

**Step 4: Formulate Natural Questions**
Based on the gaps, generate 8-10 conversational questions:
- Group by topic (robot, objects, workspace, task)
- Use natural language, not field names
- Example: "What robot model would you like to use?" (not "What is robot_configuration.model_id?")

**Step 5: Ask User & Update**
Ask the questions conversationally, get answers, then update `partial_scene_data` with new information.

**Step 6: Loop Until Complete**
Re-run this skill until `is_complete: true`

**Step 7: Next Action**
Once complete → Load `robot_selector` skill

## Usage
```bash
python scripts/resolve_gaps.py --scene_json "path/to/partial_scene.json"
```

## Gap Resolution Process
- **Auto-Resolvable**: Missing robot → robot-selector, Vague assets → sku-analyzer
- **User Input Required**: Missing positions, unclear task type, ambiguous constraints

## Output
Returns list of gaps with resolution strategy and user questions for unresolved items

## Input Schema
{
  "partial_scene_data": "object"
}

## Output Schema
{
  "is_complete": "boolean",
  "updated_scene_data": "object",
  "user_question": "string (Null if resolved internally, otherwise string)"
}