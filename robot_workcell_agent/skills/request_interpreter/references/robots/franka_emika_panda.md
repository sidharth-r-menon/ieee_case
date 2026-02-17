# Franka Emika Panda

## Overview
The Franka Emika Panda is a collaborative 7-DOF robotic arm designed for research and industrial applications requiring high precision and safety.

## Specifications

### Physical Dimensions
- **Reach**: 855 mm
- **Weight**: 18 kg (robot arm only)
- **Footprint**: Ø 127 mm

### Payload Capacity
- **Maximum Payload**: 3 kg
- **Recommended Payload**: 2.5 kg for continuous operation
- **Payload at Maximum Speed**: 2 kg

### Degrees of Freedom
- **DOF**: 7 (joints)
- **Additional DOF**: 2 (gripper fingers)

### Performance
- **Repeatability**: ±0.1 mm
- **Maximum Joint Speed**: 
  - Joints 1-4: 2.175 rad/s (≈124.5°/s)
  - Joints 5-7: 2.61 rad/s (≈149.5°/s)
- **Maximum Joint Torque**: Varies by joint (12-87 Nm)
- **Maximum TCP Speed**: 2 m/s
- **Maximum TCP Acceleration**: 13 m/s²

### Gripper
- **Type**: Parallel jaw gripper
- **Maximum Width**: 80 mm
- **Gripping Force**: 70 N (continuous), 140 N (max)
- **Maximum Payload (Gripper)**: 3 kg
- **Stroke**: 80 mm

### Joint Ranges
- **Joint 1**: ±166°
- **Joint 2**: -101° to 101°
- **Joint 3**: ±166°
- **Joint 4**: -176° to -4°
- **Joint 5**: ±166°
- **Joint 6**: -1° to 215°
- **Joint 7**: ±166°

## Use Cases

### Primary Applications
- **Pick and Place Operations**: High-speed object sorting and manipulation
- **Assembly Tasks**: Precision component assembly in electronics and manufacturing
- **Machine Tending**: Loading/unloading CNC machines and other equipment
- **Quality Inspection**: Automated visual inspection and measurement
- **Research and Development**: Academic research, algorithm development, and prototyping

### Ideal For
- Small to medium-sized parts (under 3 kg)
- Operations requiring human-robot collaboration
- Tasks requiring high repeatability and precision
- Confined workspace environments
- Research and educational purposes

### Not Recommended For
- Heavy payload handling (>3 kg)
- High-speed industrial production lines requiring faster cycle times
- Harsh environments (requires clean, controlled environment)
- Applications requiring very long reach (>855 mm)

## Safety Features
- Integrated torque sensors in all 7 joints
- Collision detection and reaction
- Configurable safety zones
- Emergency stop functionality
- Compliance control for safe human interaction

## Communication & Control
- **Control Interface**: FCI (Franka Control Interface)
- **Programming**: C++, Python (via API)
- **Real-time Control**: 1 kHz control loop
- **Supported Frameworks**: ROS, MoveIt, Genesis

## Genesis Integration
- **MJCF File**: `xml/franka_emika_panda/panda.xml`
- **End-Effector Link**: `hand`
- **Home Position**: `[0, -0.785, 0, -2.356, 0, 1.571, 0.785, 0.04, 0.04]`
- **Gripper DOFs**: Last 2 DOFs (indices -2, -1)
- **Gripper Range**: -0.02 (closed) to 0.04 (open)

## Maintenance
- **Expected Lifespan**: 30,000+ operating hours
- **Maintenance Interval**: Annual inspection recommended
- **Consumables**: Gripper pads may require replacement depending on usage
