# PSO Algorithm Configuration

This reference provides optimal Particle Swarm Optimization (PSO) parameters and cost function weights for different workcell layout scenarios.

## PSO Parameters

### Standard Configuration
```python
{
    "num_particles": 50,
    "num_iterations": 100,
    "w": 0.7,          # Inertia weight
    "c1": 1.5,         # Cognitive parameter (particle's best)
    "c2": 1.5,         # Social parameter (swarm's best)
    "bounds": {
        "x": [0.0, 2.0],      # meters
        "y": [0.0, 1.5],      # meters
        "theta": [0, 360]     # degrees
    }
}
```

### Fast Convergence (Small Workspace)
- Use when: Workspace < 1m², few entities (< 5)
- `num_particles`: 30
- `num_iterations`: 50
- `w`: 0.6 (lower inertia for faster convergence)
- `c1`: 2.0, `c2`: 2.0

### Thorough Search (Complex Layouts)
- Use when: Many entities (> 8), tight constraints
- `num_particles`: 100
- `num_iterations`: 200
- `w`: 0.8 (higher inertia for exploration)
- `c1`: 1.2, `c2`: 1.8

### Precision Mode (High-Accuracy Required)
- Use when: Precision tasks, tight tolerances
- `num_particles`: 80
- `num_iterations`: 150
- `w`: 0.75
- `c1`: 1.4, `c2`: 1.6
- Add: Position tolerance = 0.01m

## Cost Function Components

### 1. Reachability Cost
**Weight**: 0.40 (highest priority)

Penalizes positions outside robot's reachable workspace.

```python
def reachability_cost(position, robot_base):
    distance = np.linalg.norm(position[:2] - robot_base[:2])
    
    if distance > max_reach:
        return 1000.0  # Hard penalty
    elif distance < min_reach:
        return 500.0   # Too close
    elif distance > optimal_reach:
        return (distance - optimal_reach) * 10.0
    else:
        return 0.0  # Within optimal zone
```

**Parameters**:
- `max_reach`: Robot's maximum reach (e.g., 0.85m for UR5)
- `min_reach`: 0.15m (avoid robot base collision)
- `optimal_reach`: 0.6 * max_reach (sweet spot)

### 2. Collision Cost
**Weight**: 0.30

Prevents entity overlaps and collision interference.

```python
def collision_cost(entity1, entity2):
    # Bounding box collision check
    bbox1 = get_bounding_box(entity1)
    bbox2 = get_bounding_box(entity2)
    
    if bboxes_intersect(bbox1, bbox2):
        return 1000.0  # Hard collision
    
    # Soft buffer zone
    distance = min_distance(bbox1, bbox2)
    safety_margin = 0.05  # 5cm buffer
    
    if distance < safety_margin:
        return (safety_margin - distance) * 100.0
    else:
        return 0.0
```

**Collision Buffer Zones**:
- Robot base: 0.10m clearance
- Between objects: 0.05m clearance
- Table edges: 0.05m clearance
- Human interaction zones: 0.15m clearance

### 3. Zone Compliance Cost
**Weight**: 0.20

Encourages entities to stay within assigned regions from region_proposer.

```python
def zone_compliance_cost(entity, assigned_zone):
    entity_center = entity.position[:2]
    
    if point_in_polygon(entity_center, assigned_zone.boundary):
        # Inside zone - check how centered
        distance_to_center = np.linalg.norm(
            entity_center - assigned_zone.center
        )
        return distance_to_center * 2.0
    else:
        # Outside zone - strong penalty
        distance_to_zone = distance_to_polygon(
            entity_center, assigned_zone.boundary
        )
        return 100.0 + distance_to_zone * 50.0
```

### 4. Orientation Cost
**Weight**: 0.10

Optimizes entity orientation for task efficiency.

```python
def orientation_cost(entity, robot_base):
    # Prefer entities facing robot
    entity_to_robot = robot_base[:2] - entity.position[:2]
    entity_forward = [
        np.cos(np.radians(entity.theta)),
        np.sin(np.radians(entity.theta))
    ]
    
    # Dot product for alignment
    alignment = np.dot(entity_forward, entity_to_robot)
    alignment = alignment / np.linalg.norm(entity_to_robot)
    
    # Cost is lower when aligned (alignment = 1)
    return (1.0 - alignment) * 5.0
```

**Orientation Preferences**:
- Input zones: Face toward robot (0-45° deviation)
- Output zones: Face away from robot (135-180° from robot)
- Assembly zones: Face robot directly (0-15° deviation)
- Storage: Face outward for access

## Task-Specific Cost Weights

### Pick and Place
```python
cost_weights = {
    "reachability": 0.45,
    "collision": 0.30,
    "zone_compliance": 0.20,
    "orientation": 0.05
}
```
Priority: Reachability and collision avoidance

### Assembly
```python
cost_weights = {
    "reachability": 0.35,
    "collision": 0.25,
    "zone_compliance": 0.25,
    "orientation": 0.15
}
```
Priority: Balanced approach, orientation matters more

### Packing
```python
cost_weights = {
    "reachability": 0.40,
    "collision": 0.35,
    "zone_compliance": 0.20,
    "orientation": 0.05
}
```
Priority: Collision avoidance (dense packing)

### Machine Tending
```python
cost_weights = {
    "reachability": 0.50,
    "collision": 0.25,
    "zone_compliance": 0.15,
    "orientation": 0.10
}
```
Priority: Maximum reachability to machine

## Constraint Handling

### Hard Constraints (Must Satisfy)
1. **Table Boundaries**: No entity center outside table bounds
2. **Robot Base Clearance**: 0.10m minimum from robot footprint
3. **Entity Overlap**: No bounding box intersections
4. **Reach Limits**: All entities within max reach

Implementation:
```python
def check_hard_constraints(solution):
    if not within_table_bounds(solution):
        return False
    if robot_base_collision(solution):
        return False
    if any_entity_overlap(solution):
        return False
    if any_unreachable(solution):
        return False
    return True
```

### Soft Constraints (Optimize)
1. **Zone Preferences**: Stay in assigned regions
2. **Optimal Reach**: Prefer 50-80% of max reach
3. **Orientation Alignment**: Face toward/away from robot
4. **Accessibility**: Leave space for gripper approach

## Position Encoding

### Single Entity
```python
particle_vector = [x, y, theta]
# x, y: Position in meters
# theta: Orientation in degrees [0, 360]
```

### Multiple Entities (N entities)
```python
particle_vector = [
    x1, y1, theta1,
    x2, y2, theta2,
    ...
    xN, yN, thetaN
]
# Dimension: 3N
```

### Fixed Entities (Robot, Table)
- Robot base and table are fixed, not optimized
- Only moveable entities are included in particle vector

## Convergence Criteria

### Standard Termination
- Max iterations reached, OR
- Best cost improvement < 0.01 for 10 consecutive iterations

### Early Stopping (Success)
```python
if best_cost < 5.0 and iterations > 20:
    return "Success - Good solution found"
```

### Failure Detection
```python
if best_cost > 500.0 and iterations > 50:
    return "Failed - No feasible solution"
```

## Advanced Techniques

### Multi-Stage Optimization

**Stage 1**: Coarse positioning (fast)
- Low particles (30), few iterations (50)
- Large position steps
- Only hard constraints

**Stage 2**: Fine-tuning (precision)
- Medium particles (50), medium iterations (100)
- Smaller position steps
- All cost components
- Initialize from Stage 1 best solution

### Adaptive Parameters
```python
# Decrease inertia over time for convergence
w(t) = w_max - (w_max - w_min) * (t / max_iterations)

# Start: w_max = 0.9 (exploration)
# End: w_min = 0.4 (exploitation)
```

### Island Model (Parallel PSO)
- Run 3-5 independent PSO swarms
- Periodically exchange best solutions
- Take overall best result
- Useful for complex, multi-modal cost landscapes

## Scenario-Specific Recommendations

### Scenario: Dense Packing (8+ objects in small space)
- Increase collision weight to 0.40
- Use thorough search configuration
- Enable multi-stage optimization
- Consider island model

### Scenario: Long-Reach Tasks (robot at 80%+ reach)
- Increase reachability weight to 0.50
- Lower threshold for "unreachable" penalty
- Use precision mode configuration

### Scenario: Collaborative Workspace (human interaction)
- Add human interaction zones as exclusion regions
- Increase safety margins to 0.15m
- Lower optimal reach to 40-60% of max

### Scenario: High-Speed Operations
- Prioritize straight-line paths
- Increase orientation weight
- Penalize positions requiring joint limits

## Debugging Cost Function

### Visualization Checklist
1. Plot heat map of cost function over workspace
2. Verify cost increases near boundaries
3. Check collision zones show high cost
4. Confirm optimal zones show low cost

### Common Issues
- **Cost too flat**: Increase weight differences
- **No convergence**: Reduce inertia, increase iterations
- **Local minima**: Use island model or restart with random seeds
- **Unstable**: Check constraint normalization, reduce weights

## Parameter Tuning Guide

### Quick Tuning Process
1. Start with standard configuration
2. Run with visualization enabled
3. Identify dominant cost component
4. Adjust weights ±0.05 based on needs
5. Test with 5 different random seeds
6. Validate with simulation

### Performance Metrics
- **Convergence Speed**: Iterations to reach cost < 10
- **Solution Quality**: Final cost value
- **Consistency**: Std dev across multiple runs
- **Computation Time**: Wall clock time

Target Metrics:
- Convergence: < 50 iterations (standard)
- Final Cost: < 5.0 (good), < 2.0 (excellent)
- Consistency: Std dev < 1.0
- Time: < 5 seconds for small workspace