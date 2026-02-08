# Common Gaps Reference

This document catalogs frequently missing information in workcell design requirements and provides templates for resolving them.

## Robot Specifications

### Missing Robot Model
**Question Template**: "Which robot model would you prefer? Options include:
- **UR5**: Collaborative, 5kg payload, 850mm reach, ideal for light assembly
- **Franka Panda**: Collaborative, 3kg payload, 855mm reach, high precision
- **ABB IRB1200**: Industrial, 7kg payload, 900mm reach, fast operations
- **KUKA KR3**: Industrial, 3kg payload, 600mm reach, compact footprint"

**Why It Matters**: Robot selection affects payload capacity, reach, speed, and safety requirements.

### Missing End-Effector Type
**Question Template**: "What type of end-effector/gripper is needed?
- Parallel jaw gripper (standard boxes)
- Vacuum suction (flat surfaces)
- Multi-finger gripper (complex shapes)
- Tool holder (for assembly operations)"

**Why It Matters**: End-effector affects grasp planning and object handling strategies.

## Object/SKU Information

### Missing Dimensions
**Question Template**: "What are the dimensions of the [object_name]?
Please provide: Length x Width x Height in millimeters or inches"

**Why It Matters**: Object size affects gripper selection, robot reach requirements, and collision avoidance.

### Missing Weight
**Question Template**: "What is the weight of each [object_name]?
This information is critical for robot payload selection."

**Why It Matters**: Weight directly determines robot model selection and safety factors.

### Missing Material/Fragility
**Question Template**: "What material is the [object_name] made of?
Is it fragile or does it require special handling?"

**Why It Matters**: Affects gripper force, handling speed, and safety margins.

## Workspace Layout

### Missing Workcell Dimensions
**Question Template**: "What are the overall dimensions of the workcell space?
Please provide: Length x Width (x Height if constrained)"

**Why It Matters**: Constrains spatial optimization and robot placement options.

### Missing Element Positions
**Question Template**: "Where should the [element_type] be positioned?
- Specific location (e.g., 'north wall', 'center')
- Let optimization decide
- Constraints (e.g., 'near entrance', 'away from operator zone')"

**Why It Matters**: Fixed positions constrain layout optimization; flexible positions allow better solutions.

### Missing Entry/Exit Points
**Question Template**: "Where do objects enter and exit the workcell?
- Entry point for input materials
- Exit point for finished products"

**Why It Matters**: Determines material flow and influences robot placement.

## Performance Requirements

### Missing Cycle Time
**Question Template**: "What is the target cycle time for operations?
- Time per unit processed
- Throughput (units per hour)
- No specific requirement (optimize for efficiency)"

**Why It Matters**: Affects robot speed settings, number of robots needed, and parallel operation strategies.

### Missing Precision Requirements
**Question Template**: "What level of positioning precision is required?
- ±10mm (rough positioning, palletizing)
- ±1mm (standard assembly)
- ±0.1mm (precision assembly)
- Other specific tolerance"

**Why It Matters**: Determines robot selection and end-effector requirements.

### Missing Throughput Requirements
**Question Template**: "What throughput is required?
- Units per minute/hour/shift
- Peak vs average rates"

**Why It Matters**: Influences number of robots and parallelization strategies.

## Safety & Constraints

### Missing Safety Zones
**Question Template**: "Are there any safety zones or restricted areas?
- Human operator zones
- Maintenance access areas
- Emergency stop zones
- Other exclusion zones"

**Why It Matters**: Affects robot workspace boundaries and collision avoidance strategies.

### Missing Accessibility Requirements
**Question Template**: "What accessibility requirements exist?
- Maintenance access needs
- Operator intervention points
- Loading/unloading access"

**Why It Matters**: Influences layout to ensure human access when needed.

### Missing Space Constraints
**Question Template**: "Are there any space constraints or limitations?
- Maximum workcell footprint
- Height restrictions
- Fixed obstacles (columns, doors, etc.)"

**Why It Matters**: Constrains spatial optimization and robot selection.

## Budget & Timeline

### Missing Budget Constraints
**Question Template**: "What is the budget range for this workcell?
- Robot cost considerations
- End-effector budget
- Infrastructure budget"

**Why It Matters**: Affects robot model selection and solution complexity.

### Missing Timeline
**Question Template**: "What is the desired deployment timeline?
- Rush (prioritize available components)
- Standard (optimize for best solution)
- Flexible (can wait for custom solutions)"

**Why It Matters**: Influences component selection and design decisions.

## Common Gap Patterns

### Pattern 1: "Simple Pick-and-Place"
Users often mention basic operation but miss:
- Object dimensions
- Cycle time requirements
- Workspace dimensions
- Number of SKUs

### Pattern 2: "Assembly Workcell"
Users often mention assembly but miss:
- Part alignment precision
- Assembly sequence
- Tooling requirements
- Quality inspection needs

### Pattern 3: "Palletizing Operation"
Users often mention palletizing but miss:
- Pallet pattern/arrangement
- Layer configuration
- Maximum stack height
- Pallet exchange method

## Resolution Strategies

### For Critical Gaps
1. Ask immediately
2. Provide examples of typical values
3. Explain why the information is essential
4. Offer to proceed with assumptions if user prefers

### For Important Gaps
1. Group related questions together
2. Provide default/typical values
3. Explain impact on design
4. Make it easy for user to skip with "use default"

### For Optional Gaps
1. Mention briefly
2. Indicate they can be optimized later
3. Don't block progress on optional information
