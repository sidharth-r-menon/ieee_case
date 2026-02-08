# Region Proposal Templates

This reference contains standard workspace region layouts for common robot workcell tasks.

## Pick and Place Layout

### Overview
Classic two-zone layout for transferring objects from input to output locations.

### Regions
1. **Input Zone** (Priority: 2)
   - Location: Left side of workspace
   - Typical Size: 30-40% of table surface
   - Purpose: Source objects staging area
   - Constraints: Away from robot base, within reach
   - Buffer: 0.05m from edges

2. **Output Zone** (Priority: 2)
   - Location: Right side of workspace
   - Typical Size: 30-40% of table surface
   - Purpose: Destination for picked objects
   - Constraints: Away from robot base, within reach
   - Buffer: 0.05m from edges

3. **Robot Base Zone** (Priority: 1)
   - Location: Center-back of workspace
   - Typical Size: Robot footprint + 0.1m clearance
   - Purpose: Reserved for robot mounting
   - Constraints: No objects allowed
   - Buffer: 0.1m safety margin

4. **Transit Zone** (Priority: 0)
   - Location: Between input and output
   - Purpose: Path clearance for robot motion
   - Constraints: Keep clear during operation

### Example Configuration
```
Table: 1.5m × 1.0m
- Input Zone: [0.1, 0.1] to [0.6, 0.9]
- Output Zone: [0.9, 0.1] to [1.4, 0.9]
- Robot Base: [0.65, 0.45] (center position)
```

## Assembly Layout

### Overview
Multi-zone layout with central assembly area surrounded by parts storage zones.

### Regions
1. **Assembly Zone** (Priority: 3)
   - Location: Center of workspace (robot optimal reach)
   - Typical Size: 0.4m × 0.4m square
   - Purpose: Main assembly operations
   - Constraints: Maximum reachability, collision-free
   - Buffer: 0.05m clearance

2. **Parts Zone 1** (Priority: 2)
   - Location: Front-left quadrant
   - Purpose: Primary component storage
   - Access: Frequent access required

3. **Parts Zone 2** (Priority: 2)
   - Location: Front-right quadrant
   - Purpose: Secondary component storage
   - Access: Moderate access

4. **Parts Zone 3** (Priority: 2)
   - Location: Left side
   - Purpose: Tertiary/bulk parts
   - Access: Occasional access

5. **Tool Zone** (Priority: 2)
   - Location: Right side
   - Purpose: Tool storage/changing area
   - Constraints: Fixed positions for tool registration

6. **Robot Base Zone** (Priority: 1)
   - Location: Back-center
   - Purpose: Robot mounting area
   - Constraints: No interference zone

7. **Finished Product Zone** (Priority: 2)
   - Location: Front-center edge
   - Purpose: Completed assembly staging
   - Access: Easy removal by operator

### Example Configuration
```
Table: 2.0m × 1.5m
- Assembly Zone: [0.8, 0.55] to [1.2, 0.95] (center)
- Parts Zones: Surrounding assembly zone
- Robot Base: [1.0, 1.3] (back-center)
```

## Packing Layout

### Overview
Linear flow layout optimized for packaging operations.

### Regions
1. **Input Tray** (Priority: 2)
   - Location: Left side
   - Typical Size: Tray dimensions + clearance
   - Purpose: Unpacked items source
   - Constraints: Fixed position for consistency

2. **Packing Zone** (Priority: 3)
   - Location: Center-front
   - Purpose: Active packing area (box/container)
   - Constraints: Must accommodate various box sizes
   - Buffer: 0.1m around box

3. **Output Stack** (Priority: 2)
   - Location: Right side
   - Purpose: Packed boxes accumulation
   - Constraints: Stable stacking area

4. **Box Supply** (Priority: 1)
   - Location: Back-right corner
   - Purpose: Empty box storage
   - Access: Intermittent (manual replenishment)

5. **Robot Base Zone** (Priority: 1)
   - Location: Back-center
   - Purpose: Robot mounting
   - Constraints: Reserved area

### Example Configuration
```
Table: 1.8m × 1.0m
- Input Tray: [0.1, 0.2] to [0.5, 0.8]
- Packing Zone: [0.7, 0.2] to [1.1, 0.7]
- Output Stack: [1.3, 0.2] to [1.7, 0.8]
- Robot Base: [0.9, 0.85]
```

## Machine Tending Layout

### Overview
Configuration for loading/unloading CNC machines or similar equipment.

### Regions
1. **Machine Door Zone** (Priority: 3)
   - Location: Front-center (facing machine)
   - Purpose: CNC machine access point
   - Constraints: Fixed position, aligned with machine door
   - Clearance: 0.15m for door swing

2. **Input Parts Buffer** (Priority: 2)
   - Location: Left side
   - Purpose: Raw parts staging
   - Capacity: 5-10 parts queue

3. **Output Parts Buffer** (Priority: 2)
   - Location: Right side
   - Purpose: Finished parts staging
   - Capacity: 5-10 parts queue

4. **Robot Base Zone** (Priority: 1)
   - Location: Back-center
   - Purpose: Robot mounting
   - Constraints: Optimal reach to machine and buffers

5. **Tool Exchange Zone** (Priority: 1)
   - Location: Back-right corner
   - Purpose: Gripper/tool changing station
   - Constraints: Fixed position for repeatability

6. **Exclusion Zone** (Priority: 0)
   - Location: Around machine door arc
   - Purpose: Safety clearance for door operation
   - Constraints: No objects during machine operation

### Example Configuration
```
Table: 2.0m × 1.0m
Machine Position: Front edge, centered
- Machine Door: [1.0, 0.0] (front-center edge)
- Input Buffer: [0.2, 0.3] to [0.6, 0.7]
- Output Buffer: [1.4, 0.3] to [1.8, 0.7]
- Robot Base: [1.0, 0.85]
```

## Inspection/Quality Control Layout

### Overview
Layout optimized for vision-guided inspection tasks.

### Regions
1. **Inspection Station** (Priority: 3)
   - Location: Center-front (optimal lighting/camera view)
   - Typical Size: 0.3m × 0.3m
   - Purpose: Fixed inspection position
   - Constraints: Precise position for camera calibration
   - Lighting: Controlled area

2. **Input Queue** (Priority: 2)
   - Location: Left side
   - Purpose: Parts awaiting inspection
   - Capacity: 10-20 parts

3. **Pass Output** (Priority: 2)
   - Location: Right-front
   - Purpose: Accepted parts collection
   - Access: Easy operator access

4. **Fail Output** (Priority: 2)
   - Location: Right-back
   - Purpose: Rejected parts collection
   - Separation: Clear physical separation from pass output

5. **Robot Base Zone** (Priority: 1)
   - Location: Back-center
   - Purpose: Robot mounting
   - Constraints: Doesn't obstruct camera view

6. **Camera Zone** (Priority: 0)
   - Location: Above inspection station
   - Purpose: Vision system mounting
   - Constraints: No obstruction, fixed position

### Example Configuration
```
Table: 1.5m × 1.0m
- Inspection Station: [0.75, 0.3] (precise center position)
- Input Queue: [0.2, 0.2] to [0.5, 0.8]
- Pass Output: [1.0, 0.1] to [1.4, 0.4]
- Fail Output: [1.0, 0.6] to [1.4, 0.9]
- Robot Base: [0.75, 0.85]
- Camera: [0.75, 0.3, 0.8] (above inspection)
```

## Laboratory Automation Layout

### Overview
High-precision layout for sample handling and scientific equipment.

### Regions
1. **Sample Input** (Priority: 2)
   - Location: Left side
   - Purpose: Test tubes/samples staging
   - Constraints: Organized grid pattern
   - Temperature: May require cooling

2. **Processing Station** (Priority: 3)
   - Location: Center
   - Purpose: Equipment interaction point (pipette, centrifuge, etc.)
   - Constraints: Precise XYZ positioning
   - Access: Multiple positions per equipment

3. **Intermediate Storage** (Priority: 2)
   - Location: Center-right
   - Purpose: In-process sample holding
   - Constraints: Temperature controlled (if needed)

4. **Analysis Station** (Priority: 3)
   - Location: Front-right
   - Purpose: Spectrometer/analyzer equipment
   - Constraints: Fixed position, gentle placement

5. **Sample Output** (Priority: 2)
   - Location: Right side
   - Purpose: Completed samples collection
   - Constraints: Organized storage

6. **Robot Base Zone** (Priority: 1)
   - Location: Back-center
   - Purpose: Robot mounting
   - Constraints: Minimal vibration

7. **Waste Disposal** (Priority: 1)
   - Location: Back-right corner
   - Purpose: Contaminated sample disposal
   - Constraints: Sealed container

### Example Configuration
```
Table: 2.0m × 1.2m
- Sample Input: [0.1, 0.3] to [0.4, 0.9] (rack grid)
- Processing: [0.8, 0.5] to [1.2, 0.7]
- Analysis: [1.5, 0.2] to [1.9, 0.5]
- Robot Base: [1.0, 1.05]
```

## Region Priority System

### Priority Levels
- **Priority 0**: Exclusion zones (keep clear)
- **Priority 1**: Critical infrastructure (robot base, fixed equipment)
- **Priority 2**: Active work zones (input/output areas)
- **Priority 3**: Primary operation zones (assembly, inspection)

### Buffer Zones
- **Minimum Buffer**: 0.05m (general clearance)
- **Safety Buffer**: 0.10m (around moving parts)
- **Operator Access Buffer**: 0.15m (human interaction zones)

## Scaling Guidelines

### Small Workspace (< 1m²)
- Limit to 3-4 regions maximum
- Prioritize essential zones only
- Minimum region size: 0.2m × 0.2m

### Medium Workspace (1-3m²)
- Standard layouts work well
- 4-6 regions typical
- Minimum region size: 0.3m × 0.3m

### Large Workspace (> 3m²)
- Can accommodate 6-8 regions
- Consider sub-zones within regions
- May benefit from multiple robots

## Adaptive Considerations

### Robot Reach Constraints
- All work zones must be within robot's maximum reach
- Optimal zones: 50-80% of maximum reach
- Avoid extreme joint angles

### Collision Avoidance
- Maintain 0.1m minimum clearance between zones
- Consider robot arm sweep volume
- Account for gripper/tool dimensions

### Task-Specific Adjustments
- High-frequency access zones should be closer to optimal reach
- Low-frequency zones can be at workspace periphery
- Critical precision tasks should be in robot's sweet spot (60-70% reach)
