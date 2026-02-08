# Asset Organization and Paths

This reference documents the expected structure and naming conventions for Genesis simulation assets.

## Directory Structure

```
assets/
├── robots/
│   ├── universal_robots/
│   │   ├── ur3/
│   │   │   ├── ur3.xml (MJCF)
│   │   │   ├── ur3.urdf
│   │   │   └── meshes/
│   │   ├── ur5/
│   │   └── ur10/
│   ├── franka_emika/
│   │   └── panda/
│   │       ├── panda.xml
│   │       └── meshes/
│   ├── abb/
│   └── kuka/
├── objects/
│   ├── fruits/
│   │   ├── apple.obj
│   │   ├── apple_collision.obj
│   │   ├── orange.obj
│   │   └── banana.obj
│   ├── containers/
│   │   ├── box_small.obj
│   │   ├── box_medium.obj
│   │   └── bin_plastic.obj
│   ├── bottles/
│   │   ├── bottle_500ml.obj
│   │   └── bottle_1L.obj
│   └── electronics/
│       ├── pcb_standard.obj
│       └── smartphone_case.obj
├── furniture/
│   ├── workbench_standard.xml
│   ├── table_small.xml
│   └── shelf_metal.xml
└── machinery/
    ├── conveyor_small.xml
    └── conveyor_medium.xml
```

## Asset Naming Conventions

### Robots
Format: `{manufacturer}_{model}.xml` or `.urdf`

Examples:
- `ur5.xml` - Universal Robots UR5
- `panda.xml` - Franka Emika Panda
- `irb1200.xml` - ABB IRB 1200
- `kr3.xml` - KUKA KR3

### Objects
Format: `{category}_{type}_{variant}.obj`

Examples:
- `fruit_apple_01.obj`
- `container_box_medium.obj`
- `bottle_plastic_500ml.obj`
- `electronics_pcb_standard.obj`

### Collision Meshes
Format: `{object_name}_collision.obj`

Examples:
- `apple_collision.obj` - Simplified collision mesh
- `bottle_collision.obj` - Cylinder approximation

## Robot Asset Requirements

### MJCF Format (Preferred)
```xml
<mujoco model="ur5">
    <compiler angle="radian" meshdir="meshes/" />
    
    <asset>
        <mesh name="base" file="base.stl" />
        <mesh name="shoulder" file="shoulder.stl" />
        <!-- More meshes -->
    </asset>
    
    <worldbody>
        <body name="base_link" pos="0 0 0">
            <geom type="mesh" mesh="base" />
            <!-- Joint and link definitions -->
        </body>
    </worldbody>
    
    <actuator>
        <!-- Motor definitions for each joint -->
    </actuator>
</mujoco>
```

### URDF Format (Alternative)
```xml
<?xml version="1.0"?>
<robot name="ur5">
    <link name="base_link">
        <visual>
            <geometry>
                <mesh filename="package://ur5/meshes/base.stl"/>
            </geometry>
        </visual>
        <collision>
            <geometry>
                <mesh filename="package://ur5/meshes/base_collision.stl"/>
            </geometry>
        </collision>
        <inertial>
            <mass value="4.0"/>
            <inertia ixx="0.00443" ixy="0.0" ixz="0.0" 
                     iyy="0.00443" iyz="0.0" izz="0.0072"/>
        </inertial>
    </link>
    <!-- More links and joints -->
</robot>
```

### Required Properties
- **Mesh files**: STL or OBJ format
- **Joint definitions**: All DOFs with limits
- **Inertial properties**: Mass and inertia tensor
- **Collision geometry**: Simplified where possible
- **End-effector link**: Named `tool0` or `ee_link`

## Object Asset Requirements

### Mesh Format
- **File types**: OBJ (preferred), STL, DAE
- **Units**: Meters (convert from mm if needed)
- **Origin**: Object center or bottom-center
- **Orientation**: +Z up, +X forward

### Dual Mesh Approach
1. **Visual Mesh**: High-detail for rendering
   - `object_name.obj`
   - Can have many triangles (10k+)
   - Include textures if needed

2. **Collision Mesh**: Simplified for physics
   - `object_name_collision.obj`
   - Keep triangle count low (<1000)
   - Convex hull or simplified geometry

### Object Configuration JSON
```json
{
    "asset_id": "fruit_apple_01",
    "visual_mesh": "objects/fruits/apple.obj",
    "collision_mesh": "objects/fruits/apple_collision.obj",
    "scale": 1.0,
    "mass": 0.2,
    "dimensions": [0.08, 0.08, 0.09],
    "material": {
        "friction": 0.8,
        "restitution": 0.3,
        "density": 800.0
    },
    "texture": "objects/fruits/apple_texture.png"
}
```

## Furniture and Fixtures

### Composite Objects (MJCF)
```xml
<mujoco model="workbench">
    <asset>
        <texture name="wood" type="2d" file="wood_texture.png"/>
        <material name="wood_mat" texture="wood"/>
    </asset>
    
    <worldbody>
        <!-- Table top -->
        <body name="table_top" pos="0 0 0.75">
            <geom type="box" size="0.75 0.5 0.025" 
                  material="wood_mat" mass="20"/>
        </body>
        
        <!-- Table legs -->
        <body name="leg1" pos="0.65 0.45 0.375">
            <geom type="cylinder" size="0.025 0.375" 
                  material="wood_mat" mass="2"/>
        </body>
        <!-- More legs -->
    </worldbody>
</mujoco>
```

### Parameterized Tables
```python
def create_table_asset(length, width, height):
    """
    Generate table MJCF on-the-fly
    """
    table_xml = f"""
    <mujoco model="table_{length}x{width}">
        <worldbody>
            <body name="table_top" pos="0 0 {height}">
                <geom type="box" size="{length/2} {width/2} 0.025" 
                      rgba="0.7 0.5 0.3 1" mass="25"/>
            </body>
        </worldbody>
    </mujoco>
    """
    return table_xml
```

## Asset Loading Patterns

### Pattern 1: Direct Loading
```python
robot = scene.add_entity(
    gs.morphs.MJCF(
        file='assets/robots/universal_robots/ur5/ur5.xml',
        pos=(0, 0, 0.75)
    )
)
```

### Pattern 2: Asset Registry
```python
class AssetRegistry:
    """Centralized asset path management"""
    
    ROBOTS = {
        "ur3": "assets/robots/universal_robots/ur3/ur3.xml",
        "ur5": "assets/robots/universal_robots/ur5/ur5.xml",
        "franka_panda": "assets/robots/franka_emika/panda/panda.xml"
    }
    
    OBJECTS = {
        "apple": "assets/objects/fruits/apple.obj",
        "box_medium": "assets/objects/containers/box_medium.obj"
    }
    
    @classmethod
    def get_robot_path(cls, robot_id):
        return cls.ROBOTS.get(robot_id, None)
    
    @classmethod
    def get_object_path(cls, object_id):
        return cls.OBJECTS.get(object_id, None)

# Usage
robot_path = AssetRegistry.get_robot_path("ur5")
robot = scene.add_entity(gs.morphs.MJCF(file=robot_path, pos=(0,0,0.75)))
```

### Pattern 3: Asset Database with Metadata
```python
import json

class AssetDatabase:
    def __init__(self, db_file='assets/asset_database.json'):
        with open(db_file, 'r') as f:
            self.database = json.load(f)
    
    def get_asset_spec(self, asset_id):
        """Get complete asset specification"""
        return self.database.get(asset_id, None)
    
    def load_object(self, scene, asset_id, pos, euler=(0,0,0)):
        """Load object with all properties"""
        spec = self.get_asset_spec(asset_id)
        if not spec:
            raise ValueError(f"Asset {asset_id} not found")
        
        # Load with collision mesh if available
        if spec.get('collision_mesh'):
            entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=spec['visual_mesh'],
                    collision_file=spec['collision_mesh'],
                    pos=pos,
                    euler=euler,
                    scale=spec.get('scale', 1.0)
                )
            )
        else:
            entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=spec['visual_mesh'],
                    pos=pos,
                    euler=euler,
                    scale=spec.get('scale', 1.0)
                )
            )
        
        # Set material properties
        if 'material' in spec:
            mat = spec['material']
            entity.set_friction(mat.get('friction', 0.5))
            entity.set_restitution(mat.get('restitution', 0.1))
            entity.set_density(mat.get('density', 1000.0))
        
        return entity

# Usage
db = AssetDatabase()
apple = db.load_object(scene, 'fruit_apple_01', pos=(0.5, 0, 0.8))
```

## Asset Database JSON Schema

```json
{
    "fruit_apple_01": {
        "name": "Apple",
        "category": "fruit",
        "visual_mesh": "assets/objects/fruits/apple.obj",
        "collision_mesh": "assets/objects/fruits/apple_collision.obj",
        "scale": 1.0,
        "dimensions": [0.08, 0.08, 0.09],
        "mass": 0.2,
        "material": {
            "friction": 0.8,
            "restitution": 0.3,
            "density": 800.0
        },
        "gripping": {
            "type": "suction_or_adaptive",
            "approach_offset": 0.10
        },
        "keywords": ["apple", "fruit", "food"]
    }
}
```

## Asset Validation

### Pre-load Validation
```python
def validate_asset_file(filepath):
    """Check if asset file exists and is valid"""
    import os
    from pathlib import Path
    
    path = Path(filepath)
    
    # Existence check
    if not path.exists():
        raise FileNotFoundError(f"Asset not found: {filepath}")
    
    # Format check
    valid_extensions = ['.xml', '.urdf', '.obj', '.stl', '.dae']
    if path.suffix not in valid_extensions:
        raise ValueError(f"Invalid asset format: {path.suffix}")
    
    # Read check (can file be opened?)
    try:
        with open(filepath, 'r') as f:
            content = f.read(100)  # Read first 100 chars
    except Exception as e:
        raise IOError(f"Cannot read asset file: {e}")
    
    return True
```

### Post-load Validation
```python
def validate_loaded_entity(entity):
    """Verify entity loaded correctly"""
    checks = {
        "has_position": entity.get_pos() is not None,
        "has_orientation": entity.get_quat() is not None,
        "has_mass": entity.get_mass() > 0,
        "has_valid_bbox": entity.get_AABB() is not None
    }
    
    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        raise RuntimeError(f"Entity validation failed: {failed}")
    
    return True
```

## Asset Creation Guidelines

### Modeling Best Practices
1. **Origin Placement**
   - Place origin at geometric center or bottom-center
   - Simplifies position calculations

2. **Scale**
   - Model in meters (real-world scale)
   - Or provide scale factor in metadata

3. **Mesh Quality**
   - Visual mesh: High detail OK (10k-50k triangles)
   - Collision mesh: Low poly (100-1000 triangles)
   - Use convex decomposition for complex shapes

4. **Textures**
   - Keep texture resolution reasonable (1024x1024 or 2048x2048)
   - Use embedded textures or relative paths
   - Include texture files in asset package

### Collision Mesh Creation
```python
# Example: Generate collision mesh from visual mesh
import trimesh

def create_collision_mesh(visual_mesh_path, output_path):
    """
    Create simplified collision mesh from visual mesh
    """
    # Load visual mesh
    mesh = trimesh.load(visual_mesh_path)
    
    # Create convex hull
    collision_mesh = mesh.convex_hull
    
    # Simplify (reduce triangle count)
    collision_mesh = collision_mesh.simplify_quadratic_decimation(1000)
    
    # Export
    collision_mesh.export(output_path)
    
    print(f"Collision mesh: {len(collision_mesh.faces)} faces")
    print(f"Original mesh: {len(mesh.faces)} faces")

# Usage
create_collision_mesh(
    'assets/objects/fruits/apple.obj',
    'assets/objects/fruits/apple_collision.obj'
)
```

## Troubleshooting Asset Issues

### Mesh not appearing
- **Check**: File path is correct (relative or absolute)
- **Check**: Mesh scale (might be too small/large)
- **Fix**: Add debug print of entity position
- **Fix**: Verify mesh file in external viewer

### Collision not working
- **Check**: Collision mesh exists and is referenced
- **Check**: Collision enabled in scene options
- **Check**: Mesh is not inside-out (normals)
- **Fix**: Regenerate collision mesh as convex hull

### Robot not moving
- **Check**: MJCF/URDF has actuator definitions
- **Check**: Joint limits are defined
- **Check**: Control commands are being sent
- **Fix**: Verify DOF count matches expected

### Textures missing
- **Check**: Texture paths are relative to mesh file
- **Check**: Texture files exist in correct location
- **Fix**: Use embedded textures or absolute paths
- **Fix**: Copy texture files into assets directory
