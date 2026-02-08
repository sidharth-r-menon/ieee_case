# Universal Robots UR5

## Overview
The UR5 is a medium-sized collaborative robot offering an ideal balance of reach and payload capacity. It's the most popular robot in the UR e-Series lineup, suitable for a wide range of industrial applications.

## Specifications

### Physical Dimensions
- **Reach**: 850 mm
- **Weight**: 20.6 kg
- **Footprint**: Ø 190 mm
- **Mounting**: Floor, wall, ceiling, or angle

### Payload Capacity
- **Maximum Payload**: 5 kg
- **Payload at Maximum Speed**: 4 kg
- **Optimal Payload**: 2-4 kg for best performance
- **Payload at Maximum Reach**: 5 kg

### Degrees of Freedom
- **DOF**: 6 (revolute joints)

### Performance
- **Repeatability**: ±0.03 mm
- **Maximum Joint Speed**: 180°/s (all joints)
- **Maximum TCP Speed**: 1 m/s
- **Maximum TCP Acceleration**: 15 m/s²
- **Typical Cycle Time**: ~3 seconds for standard pick-and-place

### Joint Ranges
- **Joint 1 (Base)**: ±360° (infinite rotation)
- **Joint 2 (Shoulder)**: ±360° (infinite rotation)
- **Joint 3 (Elbow)**: ±360° (infinite rotation)
- **Joint 4 (Wrist 1)**: ±360° (infinite rotation)
- **Joint 5 (Wrist 2)**: ±360° (infinite rotation)
- **Joint 6 (Wrist 3)**: ±360° (infinite rotation)

### Tool Interface
- **Payload Capacity**: 5 kg (includes tool weight)
- **I/O Ports**: 2 digital inputs, 2 digital outputs, 2 analog inputs
- **Power Supply**: 12V DC (600 mA), 24V DC (600 mA)
- **Communication**: Ethernet, Modbus TCP, PROFINET

## Use Cases

### Primary Applications
- **Machine Tending**: CNC machine loading/unloading
- **Pick and Place**: Medium-weight parts, packaging operations
- **Palletizing**: Box and case stacking
- **Assembly**: Component assembly, screwdriving, gluing
- **Quality Inspection**: Camera integration, measurement tasks
- **Material Handling**: Part transfer, bin picking
- **Welding**: Arc welding, spot welding (with appropriate tool)

### Ideal For
- Parts weighing 1-5 kg
- Medium reach applications (up to 850 mm)
- Industrial manufacturing environments
- Collaborative workspaces
- Automated production lines
- Flexible manufacturing systems
- Medium-volume production

### Not Recommended For
- Heavy payloads (>5 kg)
- Very long reach requirements (>850 mm)
- Ultra-high-speed applications (cycle time <1 sec)
- Very large part handling
- Extremely harsh environments without protection

## Safety Features
- **Safety Rating**: Category 3, PLd per EN ISO 13849-1
- 17 configurable safety functions
- Built-in force and torque sensing
- Advanced collision detection
- Configurable safety zones (tool, speed, boundaries)
- Emergency stop and protective stop
- Power and force limiting (17 safety functions)
- Safety I/O for integration

## Communication & Control
- **Control Interface**: URScript, RTDE (Real-Time Data Exchange)
- **Programming**: 
  - PolyScope touchscreen interface
  - Python via URX or RTDE
  - C++ via UR Client Library
  - ROS/ROS2 drivers
- **Real-time Control**: 500 Hz servo rate, 125 Hz trajectory control
- **Supported Frameworks**: ROS, ROS2, Genesis, MoveIt
- **Network**: 100 Mbps Ethernet, Modbus TCP, PROFINET

## Genesis Integration
- **MJCF/URDF**: Compatible with standard UR5 models
- **End-Effector Link**: `wrist_3_link` or `tool0`
- **Home Position**: `[0, -1.57, 0, -1.57, 0, 0]` (typical)
- **Tool Flange**: ISO 9409-1-50-4-M6

## Gripper Compatibility
### Common Grippers
- **Robotiq 2F-85**: 2-finger adaptive gripper (most common)
- **Robotiq 3F**: 3-finger adaptive gripper
- **OnRobot RG2/RG6**: Electric parallel grippers
- **Schunk Co-act JGP**: Pneumatic gripper
- **Zimmer GEH6000**: Electric gripper
- **Vacuum Grippers**: Various vacuum cup solutions
- **Custom End-effectors**: Via tool flange

## Typical Applications by Industry
- **Automotive**: Parts handling, quality inspection, assembly
- **Electronics**: PCB handling, testing, packaging
- **Food & Beverage**: Packaging, palletizing (with food-grade protection)
- **Metalworking**: Machine tending, deburring, grinding
- **Pharmaceuticals**: Packaging, inspection, material handling
- **Plastics**: Injection molding machine tending, assembly
- **Logistics**: Order fulfillment, sorting, packaging

## Performance Characteristics
- **Power Consumption**: 
  - Idle: ~35W
  - Average operation: ~100W
  - Peak: ~300W
- **Noise Level**: <60 dB(A)
- **Temperature Range**: 0-50°C (operating)
- **Relative Humidity**: 5-95% (non-condensing)
- **IP Rating**: IP54 (with optional protection)

## Maintenance
- **Expected Lifespan**: 35,000 hours MTBF
- **Maintenance Interval**: Minimal, annual inspection recommended
- **Warranty**: 12 months standard
- **Consumables**: None (maintenance-free joints)
- **Service**: Modular design for easy joint replacement

## Advantages
- Excellent reach-to-payload ratio
- Very high repeatability (±0.03 mm)
- Easy programming and deployment
- Safe for collaborative applications
- Compact footprint
- Flexible mounting options
- Large ecosystem of accessories
