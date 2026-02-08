# Universal Robots UR3

## Overview
The UR3 is a lightweight, compact collaborative robot ideal for table-top applications and small assembly tasks. Part of Universal Robots' e-Series.

## Specifications

### Physical Dimensions
- **Reach**: 500 mm
- **Weight**: 11 kg
- **Footprint**: Ø 190 mm
- **Mounting**: Floor, wall, ceiling, or angle

### Payload Capacity
- **Maximum Payload**: 3 kg
- **Payload at Maximum Speed**: 2.5 kg
- **Optimal Payload**: 1-2 kg for best performance

### Degrees of Freedom
- **DOF**: 6 (revolute joints)

### Performance
- **Repeatability**: ±0.03 mm
- **Maximum Joint Speed**: 180°/s (all joints)
- **Maximum TCP Speed**: 1 m/s
- **Maximum TCP Acceleration**: 15 m/s²
- **Typical Cycle Time**: ~2 seconds for simple pick-and-place

### Joint Ranges
- **Joint 1 (Base)**: ±360° (infinite rotation)
- **Joint 2 (Shoulder)**: ±360° (infinite rotation)
- **Joint 3 (Elbow)**: ±360° (infinite rotation)
- **Joint 4 (Wrist 1)**: ±360° (infinite rotation)
- **Joint 5 (Wrist 2)**: ±360° (infinite rotation)
- **Joint 6 (Wrist 3)**: ±360° (infinite rotation)

### Tool Interface
- **Payload Capacity**: 3 kg (includes tool weight)
- **I/O Ports**: 2 digital inputs, 2 digital outputs
- **Power Supply**: 12V/24V DC, 600 mA
- **Communication**: Ethernet, Modbus TCP

## Use Cases

### Primary Applications
- **Light Assembly**: Small component assembly in electronics, medical devices
- **Pick and Place**: Sorting, packaging, and material handling of small parts
- **Quality Testing**: Vision-guided inspection, testing operations
- **Laboratory Automation**: Sample handling, testing equipment automation
- **Desktop Applications**: Space-constrained environments

### Ideal For
- Small, lightweight parts (0.1-2 kg)
- Benchtop and desktop applications
- Limited workspace (reach <500 mm)
- Collaborative environments
- Educational and training purposes
- Precision assembly work

### Not Recommended For
- Payloads exceeding 3 kg
- Long-reach applications (>500 mm required)
- Heavy-duty industrial applications
- High-speed production lines (cycle time <1 sec)
- Harsh or dirty environments

## Safety Features
- **Safety Rating**: Category 3, PLd per EN ISO 13849-1
- Built-in force and torque sensing
- Configurable safety boundaries and speed limits
- Emergency stop and protective stop
- Power and force limiting for collaborative operation
- Safety I/O for integration with other safety equipment

## Communication & Control
- **Control Interface**: URScript, RTDE (Real-Time Data Exchange)
- **Programming**: PolyScope (teach pendant), Python, C++
- **Real-time Control**: 500 Hz servo rate
- **Supported Frameworks**: ROS, ROS2, Genesis
- **Network**: 100 Mbps Ethernet

## Genesis Integration
- **MJCF/URDF**: Compatible with standard UR3 models
- **End-Effector Link**: `wrist_3_link` or `tool0`
- **Home Position**: `[0, -1.57, 0, -1.57, 0, 0]` (typical)
- **Tool Flange**: ISO 9409-1-50-4-M6

## Gripper Compatibility
### Common Grippers
- **Robotiq 2F-85**: 2-finger adaptive gripper
- **OnRobot RG2**: Electric parallel gripper
- **Schunk Co-act EGP-C**: Pneumatic gripper
- **Custom End-effectors**: Via tool flange

## Typical Applications by Industry
- **Electronics**: PCB handling, connector assembly
- **Medical**: Syringe handling, test tube manipulation
- **Education**: Teaching automation, research projects
- **Laboratory**: Sample preparation, equipment tending
- **Packaging**: Small product packaging, labeling

## Maintenance
- **Expected Lifespan**: 35,000 hours MTBF
- **Maintenance Interval**: Minimal, annual check recommended
- **Warranty**: 12 months standard
- **Consumables**: None (maintenance-free joints)
