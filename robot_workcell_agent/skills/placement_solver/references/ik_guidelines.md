# Inverse Kinematics (IK) Guidelines

This reference provides IK checking methods and best practices for validating robot reachability during placement optimization.

## IK Fundamentals

### What is IK Checking?
Inverse Kinematics determines if a robot can physically reach a target position and orientation with its end-effector.

### Why IK Matters in Placement
- Validates that robot can reach all objects in workcell
- Identifies joint limit violations
- Detects singular configurations
- Ensures collision-free poses exist

## IK Success Criteria

### Position Reachability
```python
def is_position_reachable(target_xyz, robot_base, max_reach, min_reach):
    """
    Check if XYZ position is within robot's workspace
    """
    distance = np.linalg.norm(target_xyz[:2] - robot_base[:2])
    z_height = target_xyz[2] - robot_base[2]
    
    # Horizontal reach check
    if distance > max_reach or distance < min_reach:
        return False
    
    # Vertical reach check (simplified spherical workspace)
    total_distance = np.sqrt(distance**2 + z_height**2)
    if total_distance > max_reach:
        return False
    
    return True
```

### Full IK Solution
```python
def check_ik_feasibility(target_pose, robot_model):
    """
    Verify full 6-DOF IK solution exists
    
    Args:
        target_pose: [x, y, z, roll, pitch, yaw]
        robot_model: Robot URDF/MJCF model
    
    Returns:
        bool: True if IK solution exists
    """
    # Use robot's IK solver (e.g., KDL, TracIK, or Genesis built-in)
    joint_solution = robot_model.inverse_kinematics(target_pose)
    
    if joint_solution is None:
        return False
    
    # Check joint limits
    if not within_joint_limits(joint_solution, robot_model):
        return False
    
    # Check for singular configurations
    if is_singular(joint_solution, robot_model):
        return False
    
    return True
```

## Robot-Specific IK Parameters

### UR5 (Universal Robots 5)
```python
ur5_params = {
    "max_reach": 0.85,  # meters
    "min_reach": 0.15,
    "vertical_reach": 0.85,
    "joint_limits": {
        # All joints: ±360° (continuous)
        "shoulder_pan": [-2*pi, 2*pi],
        "shoulder_lift": [-2*pi, 2*pi],
        "elbow": [-2*pi, 2*pi],
        "wrist_1": [-2*pi, 2*pi],
        "wrist_2": [-2*pi, 2*pi],
        "wrist_3": [-2*pi, 2*pi]
    },
    "optimal_reach_range": [0.3, 0.6],  # 35-70% of max reach
    "dof": 6
}
```

### Franka Emika Panda
```python
panda_params = {
    "max_reach": 0.855,
    "min_reach": 0.15,
    "vertical_reach": 0.75,
    "joint_limits": {
        "joint1": [-2.8973, 2.8973],  # ±166°
        "joint2": [-1.7628, 1.7628],  # ±101°
        "joint3": [-2.8973, 2.8973],
        "joint4": [-3.0718, -0.0698],  # -176° to -4°
        "joint5": [-2.8973, 2.8973],
        "joint6": [-0.0175, 3.7525],   # -1° to 215°
        "joint7": [-2.8973, 2.8973]
    },
    "optimal_reach_range": [0.35, 0.65],
    "dof": 7,  # Redundant 7-DOF provides extra flexibility
    "redundancy": True
}
```

### UR3 (Compact)
```python
ur3_params = {
    "max_reach": 0.50,
    "min_reach": 0.10,
    "vertical_reach": 0.45,
    "joint_limits": {
        # Similar to UR5 but shorter reach
        # All joints: ±360°
    },
    "optimal_reach_range": [0.2, 0.4],
    "dof": 6
}
```

## IK Sampling Strategies

### Approach Poses
For each object position, test multiple approach angles:

```python
def generate_approach_poses(object_position, num_samples=8):
    """
    Generate multiple approach orientations for IK testing
    """
    poses = []
    z_offset = 0.10  # 10cm above object
    
    for i in range(num_samples):
        angle = (2 * np.pi * i) / num_samples
        
        # Top-down approach
        pose_top = {
            "position": [object_position[0], object_position[1], 
                        object_position[2] + z_offset],
            "orientation": [0, np.pi, angle]  # Roll, Pitch, Yaw
        }
        poses.append(pose_top)
        
        # Angled approach (45 degrees)
        offset_x = 0.05 * np.cos(angle)
        offset_y = 0.05 * np.sin(angle)
        pose_angled = {
            "position": [object_position[0] + offset_x, 
                        object_position[1] + offset_y,
                        object_position[2] + z_offset],
            "orientation": [0, np.pi/4, angle]
        }
        poses.append(pose_angled)
    
    return poses
```

### Success Threshold
Object is considered reachable if **at least one** approach pose has valid IK solution.

## Simplified IK for Optimization

During PSO optimization, use fast approximation methods:

### Method 1: Distance-Based (Fastest)
```python
def fast_reachability_check(position, robot_base, max_reach):
    """
    Simple distance check - very fast but conservative
    """
    distance = np.linalg.norm(position[:2] - robot_base[:2])
    return distance <= max_reach * 0.95  # 5% safety margin
```

**Use when**: Initial PSO iterations, many particles

### Method 2: Geometric IK (Fast)
```python
def geometric_ik_check(target, robot):
    """
    Analytical IK for specific robot geometries
    Faster than numerical IK solvers
    """
    # For robots with spherical wrist (UR series, Panda)
    # Decouple position (first 3 joints) and orientation (wrist)
    
    # Position subproblem
    if not solve_position_ik(target[:3], robot):
        return False
    
    # Orientation subproblem
    if not solve_orientation_ik(target[3:], robot):
        return False
    
    return True
```

**Use when**: Mid-stage PSO, candidate validation

### Method 3: Numerical IK (Accurate)
```python
def numerical_ik_check(target, robot, max_iterations=50):
    """
    Full numerical IK solver (e.g., Jacobian-based)
    Most accurate but slowest
    """
    # Use Genesis/PyBullet/MoveIt IK solver
    solution = robot.compute_ik(
        target_pose=target,
        max_iter=max_iterations,
        tolerance=0.001
    )
    
    return solution is not None
```

**Use when**: Final solution validation, low particle count

## Reachability Maps

### Pre-compute Reachability
Instead of checking IK for every position during optimization, pre-compute a reachability map:

```python
def build_reachability_map(robot, workspace_bounds, resolution=0.05):
    """
    Pre-compute which positions are reachable
    
    Args:
        robot: Robot model
        workspace_bounds: [[x_min, x_max], [y_min, y_max], [z_min, z_max]]
        resolution: Grid cell size in meters
    
    Returns:
        3D binary array: 1 if reachable, 0 if not
    """
    x_range = np.arange(workspace_bounds[0][0], 
                       workspace_bounds[0][1], resolution)
    y_range = np.arange(workspace_bounds[1][0], 
                       workspace_bounds[1][1], resolution)
    z_range = np.arange(workspace_bounds[2][0], 
                       workspace_bounds[2][1], resolution)
    
    reachability_map = np.zeros((len(x_range), len(y_range), len(z_range)))
    
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            for k, z in enumerate(z_range):
                position = [x, y, z]
                
                # Test multiple orientations
                reachable = False
                for orientation in sample_orientations(8):
                    pose = position + orientation
                    if check_ik_feasibility(pose, robot):
                        reachable = True
                        break
                
                reachability_map[i, j, k] = 1 if reachable else 0
    
    return reachability_map
```

**Benefit**: Lookup is O(1) vs IK solve is O(n)

### Using Reachability Map
```python
def query_reachability_map(position, reachability_map, workspace_bounds, resolution):
    """
    Fast lookup in pre-computed map
    """
    # Convert continuous position to grid indices
    i = int((position[0] - workspace_bounds[0][0]) / resolution)
    j = int((position[1] - workspace_bounds[1][0]) / resolution)
    k = int((position[2] - workspace_bounds[2][0]) / resolution)
    
    # Bounds checking
    if not (0 <= i < reachability_map.shape[0] and
            0 <= j < reachability_map.shape[1] and
            0 <= k < reachability_map.shape[2]):
        return False
    
    return reachability_map[i, j, k] == 1
```

## Integration with Cost Function

### IK-Based Reachability Cost
```python
def ik_reachability_cost(entity_position, robot, approach_samples=8):
    """
    Cost based on IK feasibility
    """
    poses = generate_approach_poses(entity_position, approach_samples)
    
    successful_iks = 0
    for pose in poses:
        if check_ik_feasibility(pose, robot):
            successful_iks += 1
    
    # Cost decreases with more successful IK solutions
    success_rate = successful_iks / len(poses)
    
    if success_rate == 0:
        return 1000.0  # Completely unreachable
    elif success_rate < 0.25:
        return 50.0    # Barely reachable
    elif success_rate < 0.5:
        return 10.0    # Marginally reachable
    else:
        return 0.0     # Well reachable
```

## Handling IK Failures

### Degeneracies and Singularities
```python
def is_singular(joint_config, robot):
    """
    Check if configuration is near singular
    """
    jacobian = robot.compute_jacobian(joint_config)
    
    # Compute manipulability index
    det = np.linalg.det(jacobian @ jacobian.T)
    manipulability = np.sqrt(det)
    
    # Threshold for singularity
    return manipulability < 0.01
```

### Alternative Configurations
Some robots (especially 7-DOF) have multiple IK solutions:

```python
def find_all_ik_solutions(target_pose, robot):
    """
    Find all valid IK solutions for redundant robots
    """
    solutions = []
    
    # For 7-DOF robots, sweep through redundant joint
    if robot.dof == 7:
        for redundant_angle in np.linspace(-pi, pi, 16):
            config = robot.ik_with_redundancy(
                target_pose, 
                redundant_joint_angle=redundant_angle
            )
            if config is not None:
                solutions.append(config)
    else:
        # 6-DOF may have up to 8 solutions (for UR robots)
        solutions = robot.ik_all_solutions(target_pose)
    
    return solutions
```

**Choose best** solution based on:
1. Closest to current joint configuration
2. Furthest from joint limits
3. Highest manipulability
4. Least joint motion required

## Best Practices

### 1. Use Progressive IK Checks
- **Coarse phase**: Distance-based check only
- **Medium phase**: Geometric IK
- **Fine phase**: Full numerical IK validation

### 2. Cache IK Results
- Avoid recomputing IK for same positions
- Use LRU cache for recent queries

### 3. Workspace Discretization
- Define workspace grid (e.g., 5cm resolution)
- Snap entity positions to grid
- Pre-compute IK for grid points

### 4. Batch IK Queries
- Check IK for all entities simultaneously
- Parallelize across entities if using GPU

### 5. Adaptive Sampling
- Use more approach samples for critical objects
- Fewer samples for explorative PSO particles

## Troubleshooting

### Issue: All positions marked unreachable
- **Check**: Robot base position correct?
- **Check**: Max reach parameter accurate?
- **Fix**: Expand workspace bounds or move robot closer

### Issue: IK solver too slow
- **Solution**: Use reachability map (pre-compute)
- **Solution**: Switch to geometric IK
- **Solution**: Reduce approach sample count

### Issue: Valid solutions but poor manipulability
- **Solution**: Add manipulability to cost function
- **Solution**: Prefer central workspace positions
- **Solution**: Avoid extreme joint angles

### Issue: Inconsistent IK results
- **Check**: IK solver tolerance too loose?
- **Check**: Random seed initialization?
- **Fix**: Use deterministic IK solver configuration
