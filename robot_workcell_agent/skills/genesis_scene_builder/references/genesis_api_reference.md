# Genesis Scene Building API Reference

This reference provides Genesis physics engine API usage patterns for building robot workcell simulations.

## Basic Scene Setup

### Initialize Genesis
```python
import genesis as gs

# Initialize Genesis
gs.init(
    backend=gs.cpu,          # or gs.cuda for GPU
    logging_level='warning'  # 'debug', 'info', 'warning', 'error'
)

# Create scene
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,              # 10ms timestep
        substeps=10,          # Physics substeps per step
        gravity=(0, 0, -9.81) # m/s²
    ),
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(2.0, 2.0, 1.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
        max_FPS=60
    ),
    rigid_options=gs.options.RigidOptions(
        enable_collision=True,
        enable_self_collision=False
    ),
    show_viewer=True
)
```

### Build Scene
```python
# Must call build() before adding entities
scene.build()
```

## Loading Assets

### Robot (MJCF/URDF)
```python
# Load robot from MJCF
robot = scene.add_entity(
    gs.morphs.MJCF(
        file='xml/universal_robots/ur5/ur5.xml',
        pos=(0.0, 0.0, 0.75),      # Position [x, y, z]
        euler=(0, 0, 0),            # Orientation [roll, pitch, yaw] in degrees
        scale=1.0
    ),
)

# Alternative: Load from URDF
robot = scene.add_entity(
    gs.morphs.URDF(
        file='urdf/ur5/ur5.urdf',
        pos=(0.0, 0.0, 0.75),
        euler=(0, 0, 0),fixedBase=True  # Fix base to ground
    ),
)
```

### Common Robot Paths
```python
robot_files = {
    "ur3": "xml/universal_robots/ur3/ur3.xml",
    "ur5": "xml/universal_robots/ur5/ur5.xml",
    "ur10": "xml/universal_robots/ur10/ur10.xml",
    "franka_panda": "xml/franka_emika_panda/panda.xml",
    "abb_irb1200": "xml/abb/irb1200/irb1200.xml",
    "kuka_kr3": "xml/kuka/kr3/kr3.xml"
}
```

### Table/Plane
```python
# Ground plane
ground = scene.add_entity(
    gs.morphs.Plane(),
)

# Workbench table
table = scene.add_entity(
    gs.morphs.Box(
        size=(1.5, 1.0, 0.05),  # Length, Width, Height
        pos=(0.75, 0.0, 0.35),
        euler=(0, 0, 0),
        fixed=True  # Static object
    ),
)

# Or load from MJCF
table = scene.add_entity(
    gs.morphs.MJCF(
        file='xml/furniture/workbench.xml',
        pos=(0.75, 0.0, 0.0),
        euler=(0, 0, 0)
    ),
)
```

### Objects (Primitives)
```python
# Box
box = scene.add_entity(
    gs.morphs.Box(
        size=(0.1, 0.1, 0.1),
        pos=(0.5, 0.0, 0.8),
        euler=(0, 0, 45),
        fixed=False
    ),
)

# Cylinder
cylinder = scene.add_entity(
    gs.morphs.Cylinder(
        radius=0.05,
        height=0.15,
        pos=(0.6, 0.0, 0.8),
        euler=(0, 0, 0),
        fixed=False
    ),
)

# Sphere
sphere = scene.add_entity(
    gs.morphs.Sphere(
        radius=0.04,
        pos=(0.4, 0.0, 0.8),
        fixed=False
    ),
)
```

### Objects (Mesh)
```python
# Load custom mesh
apple = scene.add_entity(
    gs.morphs.Mesh(
        file='meshes/food/apple.obj',  # or .stl, .dae
        pos=(0.5, 0.2, 0.8),
        euler=(0, 0, 0),
        scale=0.001,  # Convert mm to m if needed
        fixed=False
    ),
)

# With physics properties
bottle = scene.add_entity(
    gs.morphs.Mesh(
        file='meshes/bottles/plastic_500ml.obj',
        pos=(0.6, 0.2, 0.8),
        euler=(0, 0, 0),
        scale=0.001,
        fixed=False,
        collision=True,
        density=1000.0  # kg/m³ (water density)
    ),
)
```

## Entity Properties

### Set Material Properties
```python
# Friction
entity.set_friction(0.8)  # Static friction coefficient

# Density (affects mass)
entity.set_density(500.0)  # kg/m³

# Restitution (bounciness)
entity.set_restitution(0.3)  # 0 = no bounce, 1 = perfect bounce

# Damping
entity.set_damping(
    linear=0.1,   # Linear velocity damping
    angular=0.1   # Angular velocity damping
)
```

### Get Entity Information
```python
# Position and orientation
pos = entity.get_pos()  # Returns [x, y, z]
quat = entity.get_quat()  # Returns quaternion [w, x, y, z]
euler = entity.get_euler()  # Returns [roll, pitch, yaw] in radians

# Velocity
lin_vel = entity.get_vel()  # Linear velocity [vx, vy, vz]
ang_vel = entity.get_ang_vel()  # Angular velocity [wx, wy, wz]

# Bounding box
bbox = entity.get_AABB()  # Axis-aligned bounding box
# Returns: [[x_min, y_min, z_min], [x_max, y_max, z_max]]

# Mass
mass = entity.get_mass()  # kg
```

### Set Entity State
```python
# Teleport entity (no physics)
entity.set_pos([0.5, 0.0, 1.0])
entity.set_quat([1, 0, 0, 0])  # Identity rotation
entity.set_euler([0, 0, 1.57])  # 90 degrees yaw

# Apply forces/velocities
entity.set_vel([0.1, 0.0, 0.0])  # Set linear velocity
entity.set_ang_vel([0, 0, 0.5])  # Set angular velocity

# Apply impulse (instant velocity change)
entity.apply_impulse(
    impulse=[0, 0, 5.0],  # Impulse vector
    pos=[0, 0, 0]          # Application point (local coords)
)

# Apply force (continuous)
entity.apply_force(
    force=[0, 0, 10.0],   # Force vector
    pos=[0, 0, 0]          # Application point
)
```

## Robot Control

### Get Robot DOF information
```python
# Get number of degrees of freedom
n_dofs = robot.n_dofs

# Get DOF names
dof_names = robot.get_dof_names()  # e.g., ['shoulder_pan_joint', ...]

# Get joint limits
lower_limits = robot.get_dof_lower_limits()
upper_limits = robot.get_dof_upper_limits()
```

### Set Robot Joint Positions
```python
# Set all joint positions at once
joint_positions = [0, -1.57, 0, -1.57, 0, 0]  # UR5 home pose
robot.set_dofs_position(joint_positions)

# Set single joint
robot.set_dof_position(index=0, position=0.5)

# Set joint velocities
joint_velocities = [0.0] * robot.n_dofs
robot.set_dofs_velocity(joint_velocities)
```

### Get Robot State
```python
# Get current joint positions
current_joints = robot.get_dofs_position()

# Get current joint velocities
current_vels = robot.get_dofs_velocity()

# Get end-effector pose
ee_pose = robot.get_link_pos(link_name='tool0')  # Position
ee_quat = robot.get_link_quat(link_name='tool0')  # Orientation
```

### Control Robot
```python
# Position control (PD controller)
robot.control_dofs_position(
    target_positions=joint_positions,
    kp=100.0,  # Proportional gain
    kd=10.0    # Derivative gain
)

# Velocity control
robot.control_dofs_velocity(
    target_velocities=joint_velocities,
    kv=100.0   # Velocity gain
)

# Torque control
robot.control_dofs_force(
    target_forces=joint_torques
)
```

## Gripper Control

### Parallel Jaw Gripper (UR5 + Robotiq 2F-85)
```python
# Get gripper DOF indices (last 2 DOFs for Panda, specific joints for others)
gripper_dofs = [-2, -1]  # For Franka Panda

# Open gripper
robot.control_dofs_position(
    target_positions=[0.04, 0.04],  # Open position
    dof_indices=gripper_dofs,
    kp=100.0
)

# Close gripper
robot.control_dofs_position(
    target_positions=[0.0, 0.0],  # Closed position
    dof_indices=gripper_dofs,
    kp=100.0
)

# Check if object grasped (detect contact force)
gripper_forces = robot.get_dofs_force(dof_indices=gripper_dofs)
is_grasping = abs(gripper_forces[0]) > 1.0  # Force threshold
```

### Suction Gripper (Simulated)
```python
# Create suction constraint when contact detected
def activate_suction(robot_ee, target_object):
    """Simulate suction by creating fixed constraint"""
    constraint = scene.add_constraint(
        gs.constraint.Fixed(
            entity_a=robot,
            entity_b=target_object,
            link_a='tool0',
            pos_a=[0, 0, 0],
            pos_b=[0, 0, 0]
        )
    )
    return constraint

def deactivate_suction(constraint):
    """Release object"""
    scene.remove_constraint(constraint)
```

## Scene Simulation

### Run Simulation Loop
```python
# Reset scene
scene.reset()

# Simulation loop
for step in range(1000):
    # Control commands
    robot.control_dofs_position(target_positions)
    
    # Step simulation
    scene.step()
    
    # Read sensor data / check constraints
    current_pos = robot.get_dofs_position()
    
    # Render (if viewer enabled)
    # Automatically renders at specified FPS
```

### Stepping Options
```python
# Single step
scene.step()

# Step N times
scene.step(n=10)

# Step with control in same call
scene.step(n=1)
robot.control_dofs_position(targets)
```

## Collision Detection

### Check Collisions
```python
# Get all collisions in scene
collisions = scene.get_contacts()

# Check specific entity pair
is_colliding = scene.check_collision(entity_a=robot, entity_b=table)

# Get contact points
contacts = scene.get_contacts_between(entity_a=robot, entity_b=box)
for contact in contacts:
    pos = contact.pos  # Contact position
    normal = contact.normal  # Contact normal
    force = contact.force  # Contact force magnitude
```

### Collision Filtering
```python
# Disable collision between specific entities
scene.set_collision_filter(entity_a=robot, entity_b=table, enable=False)

# Disable self-collision for robot
robot.set_self_collision(False)
```

## Camera and Visualization

### Add Camera Sensor
```python
# Add RGB camera
camera = scene.add_camera(
    pos=(1.5, 1.5, 1.0),
    lookat=(0.0, 0.0, 0.5),
    fov=60,
    width=640,
    height=480
)

# Capture image
rgb_image = camera.render()  # Returns numpy array (H, W, 3)

# Add depth camera
depth_camera = scene.add_camera(
    pos=(1.5, 1.5, 1.0),
    lookat=(0.0, 0.0, 0.5),
    fov=60,
    width=640,
    height=480,
    depth=True
)

depth_image = depth_camera.render_depth()  # Returns (H, W) depth map
```

### Visualization Markers
```python
# Add visual marker (debugging)
marker = scene.add_entity(
    gs.morphs.Sphere(
        radius=0.02,
        pos=(0.5, 0.0, 0.8),
        fixed=True,
        collision=False,  # Visual only, no physics
        color=(1, 0, 0, 1)  # RGBA
    ),
)
```

## Common Patterns

### Pattern 1: Load Workcell from Layout JSON
```python
def build_scene_from_layout(layout_json):
    """
    Build Genesis scene from placement optimizer JSON output
    """
    scene = gs.Scene(...)
    scene.build()
    
    entities = {}
    
    # Load robot
    robot_data = layout_json["robot"]
    robot = scene.add_entity(
        gs.morphs.MJCF(
            file=get_robot_file(robot_data["model_id"]),
            pos=robot_data["position"],
            euler=robot_data["orientation"]
        )
    )
    entities["robot"] = robot
    
    # Load table
    table_data = layout_json["table"]
    table = scene.add_entity(
        gs.morphs.Box(
            size=table_data["dimensions"],
            pos=table_data["position"],
            fixed=True
        )
    )
    entities["table"] = table
    
    # Load objects
    for obj_data in layout_json["objects"]:
        obj = scene.add_entity(
            create_object_from_spec(obj_data)
        )
        entities[obj_data["id"]] = obj
    
    return scene, entities

def create_object_from_spec(obj_spec):
    """Convert object spec to Genesis morph"""
    if obj_spec["type"] == "mesh":
        return gs.morphs.Mesh(
            file=obj_spec["asset_path"],
            pos=obj_spec["position"],
            euler=obj_spec["orientation"],
            scale=obj_spec.get("scale", 1.0)
        )
    elif obj_spec["type"] == "box":
        return gs.morphs.Box(
            size=obj_spec["dimensions"],
            pos=obj_spec["position"],
            euler=obj_spec["orientation"]
        )
    # ... handle other types
```

### Pattern 2: Physics Validation Loop
```python
def validate_layout_stability(scene, entities, sim_steps=200):
    """
    Run physics simulation to check layout stability
    """
    scene.reset()
    
    initial_positions = {}
    for name, entity in entities.items():
        if name != "robot" and name != "table":
            initial_positions[name] = entity.get_pos()
    
    # Run simulation
    for step in range(sim_steps):
        scene.step()
    
    # Check stability
    stable = True
    for name, initial_pos in initial_positions.items():
        final_pos = entities[name].get_pos()
        displacement = np.linalg.norm(np.array(final_pos) - np.array(initial_pos))
        
        if displacement > 0.05:  # 5cm threshold
            stable = False
            print(f"{name} moved {displacement:.3f}m")
    
    return stable
```

### Pattern 3: IK Validation in Simulation
```python
def validate_reachability(scene, robot, target_positions):
    """
    Validate robot can reach all target positions using simulation IK
    """
    reachable = {}
    
    for target_name, target_pos in target_positions.items():
        # Add target orientation (top-down grasp)
        target_pose = target_pos + [0, np.pi, 0]  # [x,y,z,roll,pitch,yaw]
        
        # Compute IK
        joint_solution = robot.inverse_kinematics(
            target_pose=target_pose,
            link_name='tool0'
        )
        
        if joint_solution is not None:
            # Verify solution is within joint limits
            lower = robot.get_dof_lower_limits()
            upper = robot.get_dof_upper_limits()
            
            within_limits = all(
                lower[i] <= joint_solution[i] <= upper[i]
                for i in range(len(joint_solution))
            )
            
            reachable[target_name] = within_limits
        else:
            reachable[target_name] = False
    
    return reachable
```

## Performance Optimization

### Use GPU Backend
```python
gs.init(backend=gs.cuda)  # GPU acceleration
```

### Reduce Rendering Overhead
```python
# Disable viewer for headless validation
scene = gs.Scene(show_viewer=False)
```

### Simplify Collision Meshes
```python
# Use primitive shapes for collision when possible
entity = scene.add_entity(
    gs.morphs.Mesh(
        file='meshes/complex_object.obj',
        collision_file='meshes/collision_simple.obj',  # Simplified collision mesh
        pos=(0, 0, 0)
    )
)
```

### Batch Operations
```python
# Set multiple entities at once
positions = np.array([[x1,y1,z1], [x2,y2,z2], ...])
for i, entity in enumerate(entities):
    entity.set_pos(positions[i])
```

## Troubleshooting

### Objects falling through ground/table
- **Check**: Table is set to `fixed=True`
- **Check**: Physics substeps adequate (try `substeps=20`)
- **Fix**: Increase collision margin, reduce timestep

### Robot jerky/unstable motion
- **Fix**: Increase PD gains for position control
- **Fix**: Reduce control frequency (don't send new targets every step)
- **Fix**: Use velocity limits

### Simulation too slow
- **Solution**: Use GPU backend (`gs.cuda`)
- **Solution**: Simplify collision meshes
- **Solution**: Disable viewer (`show_viewer=False`)
- **Solution**: Increase timestep if stability allows

### IK doesn't converge
- **Check**: Target is within robot's workspace
- **Check**: Target orientation is achievable
- **Try**: Different initial joint configuration
- **Try**: Relax orientation constraints
