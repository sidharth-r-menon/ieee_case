# Gap Analysis Guide

## Overview
Use this guide to identify missing information before outputting Stage 1 JSON.

## Schema Validation Checklist

Check against the required Stage 1 output schema:

### Critical Fields (Must Have):
- ✅ **Robot selection**: model, payload capacity, reach
- ✅ **Object specifications**: dimensions [L,W,H], weight, material
- ✅ **Throughput**: items/hour or cycle time
- ✅ **Workspace layout**: component types and general positions
- ✅ **Task objective**: clear description of what needs to be done

### Important Fields (Affects Quality):
- ✅ **Stacking pattern**: for palletizing tasks
- ✅ **Material handling**: gripper type considerations
- ✅ **Safety requirements**: fencing, zones
- ✅ **Constraints**: space, environmental

### Optional Fields (Can Infer):
- Exact component orientations (can assign defaults)
- Brand preferences (can select optimal)
- Aesthetic specifications

## Gap Categories

### Critical Gaps (Must Ask):
- Object dimensions missing or vague ("small boxes")
- Object weight unknown (affects robot selection)
- Throughput not specified (items/hour)
- Workspace constraints unclear

### Important Gaps (Should Ask):
- Stacking pattern for palletizing
- Material type (affects gripper design)
- Safety zone requirements
- Cycle time constraints

### Nice-to-Have (Can Assume):
- Exact orientations (assign defaults)
- Brand preferences (select optimal)
- Color specifications (not critical)

## Question Formulation

Ask specific, quantitative questions ("What are the carton dims in cm? What weight in kg?"). Avoid vague or repeated questions. Ask 3-5 per round.

## Iteration Strategy

After each user response: update understanding → re-check schema → ask remaining gaps. Stop iterating when all critical fields are complete.
