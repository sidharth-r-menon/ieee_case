---
name: request_interpreter
description: "Stage 1: Takes raw natural language user requests and maps them to structured JSON scene data format. Use when: (1) Starting a new robot workcell design task, (2) Processing initial user input describing robot tasks, (3) Converting conversational requirements into structured data. Fills known fields and marks unknowns as null or TBD for further resolution."
metadata:
  stage: "1"
---

# Request Interpreter

## Overview
Converts natural language requests into structured scene data format. This is the **ENTRY POINT** for translating user requirements into the Golden JSON structure used throughout the system.

## When to Use This Skill
- User describes a new robot workcell design task
- Starting fresh with natural language input
- First step of Stage 1 (Interpretation)

## Workflow Instructions for Agent

**Step 1: Extract User Request**
- Get the user's natural language description of their workcell needs
- If user provides partial info, ask them to describe the complete task

**Step 2: Execute Script**
Run the interpretation script:
```bash
python skills/request_interpreter/scripts/interpret_request.py --text "<user_description>"
```

**Step 3: Parse JSON Output**
The script outputs JSON with structure:
```json
{
  "partial_scene_data": {
    "robot_configuration": { "model_id": "franka_panda" or null },
    "workcell_assets": [{"type": "table", "model_id": "TBD", "position": null}],
    "task_type": "pick_place" or null,
    "task_description": "<original text>"
  }
}
```

**Step 4: Present Results**
Show the user:
- What information was successfully extracted
- What fields are missing (null or TBD)

**Step 5: Next Action**
- If there are null/TBD fields → Load `gap_resolver` skill
- If everything is complete → Load `robot_selector` skill

**CRITICAL**: Save the `partial_scene_data` - you'll need it for subsequent skills!

## Usage
```bash
python scripts/interpret_request.py --text "Set up a packing station with a Panda robot"
```

## What It Does
- Extracts robot model mentions (Panda, UR5, etc.)
- Identifies task type (pick_place, assembly, packing)
- Detects workspace furniture (table, workbench)
- Recognizes common objects (box, apple, bottle)
- Marks unresolved fields as null or TBD

## Input Schema
{
  "text": "Set up a packing station with a Panda robot."
}

## Output Schema
{
  "partial_scene_data": {
    "robot_configuration": { "model_id": "franka_panda" },
    "workcell_assets": [], 
    "constraints": null
  }
}