# ABB IRB 1200

## Overview
The ABB IRB 1200 is a compact, fast, and precise 6-axis industrial robot designed for small parts assembly, material handling, and machine tending. It offers excellent performance in confined spaces with two payload variants.

## Specifications

### Physical Dimensions
- **Reach**: 
  - IRB 1200-5: 900 mm
  - IRB 1200-7: 700 mm
- **Weight**: 
  - IRB 1200-5: 54 kg
  - IRB 1200-7: 52 kg
- **Footprint**: 290 x 290 mm

### Payload Capacity
- **IRB 1200-5**: 5 kg maximum payload
- **IRB 1200-7**: 7 kg maximum payload
- **Optimal Payload**: 3-5 kg for best cycle time

### Degrees of Freedom
- **DOF**: 6 (revolute joints)

### Performance
- **Repeatability**: ±0.02 mm
- **Path Repeatability**: ±0.05 mm
- **Maximum Joint Speeds**:
  - Axis 1: 250°/s
  - Axis 2: 250°/s
  - Axis 3: 250°/s
  - Axis 4: 320°/s
  - Axis 5: 320°/s
  - Axis 6: 420°/s
- **Maximum TCP Speed**: 
  - IRB 1200-5: 7.3 m/s
  - IRB 1200-7: 5.5 m/s
- **Acceleration**: Up to 28 m/s²

### Joint Ranges
- **Axis 1**: +165° to -165°
- **Axis 2**: +110° to -110°
- **Axis 3**: +70° to -110° (IRB 1200-5), +80° to -150° (IRB 1200-7)
- **Axis 4**: +160° to -160°
- **Axis 5**: +120° to -120°
- **Axis 6**: +400° to -400°

### Tool Interface
- **Mounting Flange**: ISO 9409-1-40-4-M5
- **Load Moment of Inertia**: 0.25 kgm²
- **Air Connections**: 4 mm and 6 mm through arm
- **Electrical Connections**: 8 signal, 8 power through arm
- **Communication**: EtherNet/IP, PROFINET, DeviceNet

## Use Cases

### Primary Applications
- **Small Parts Assembly**: Electronics, connectors, small components
- **Pick and Place**: High-speed sorting and material handling
- **Machine Tending**: CNC machine loading/unloading
- **Material Handling**: Part transfer, packaging
- **Testing and Inspection**: Quality control, measurement
- **Screw Driving**: Automated fastening operations
- **Dispensing**: Gluing, sealing, painting
- **Polishing and Deburring**: Surface finishing

### Ideal For
- Small to medium parts (0.5-5 kg)
- High-speed operations requiring fast cycle times
- Compact workspaces and tight integration
- Applications requiring high precision (±0.02 mm)
- Clean room environments (with proper protection)
- Electronics manufacturing
- Medical device assembly
- Automotive component assembly

### Not Recommended For
- Heavy payloads (>7 kg)
- Very long reach requirements (>900 mm)
- Collaborative applications (not designed for collaborative operation)
- Harsh or outdoor environments without protection
- Applications requiring extreme environmental conditions

## Safety Features
- **Safety Rating**: Category 3, PLd per EN ISO 13849-1
- SafeMove (optional safety software)
- Emergency stop circuits
- Configurable safety zones
- Speed and position monitoring
- Safe stop functionality
- External safety devices integration (light curtains, laser scanners)

**Note**: IRB 1200 is an industrial robot, NOT a collaborative robot. Requires safety fencing or other protective measures when operating near humans.

## Communication & Control
- **Controller**: IRC5 Compact or IRC5 Single Cabinet
- **Programming**: 
  - RAPID programming language (ABB's native language)
  - RobotStudio (offline programming and simulation)
  - Python via Robot Web Services
  - C++ via ABB Robot SDK
- **Real-time Control**: 250 Hz servo rate (4ms cycle time)
- **Supported Frameworks**: ROS, ROS2 (via ABB drivers), Genesis
- **Network**: EtherNet/IP, PROFINET, DeviceNet, Modbus TCP

## Genesis Integration
- **MJCF/URDF**: Compatible with IRB 1200 CAD models
- **End-Effector Link**: `tool0` or `link_6`
- **Home Position**: Typically `[0, 0, 0, 0, 90, 0]` (degrees)
- **Tool Flange**: ISO 9409-1-40-4-M5

## Gripper Compatibility
### Common Grippers
- **Schunk PGN-plus 50**: Pneumatic parallel gripper
- **Zimmer GEP2000**: Electric gripper series
- **Piab piCOBOT**: Vacuum systems
- **OnRobot RG2**: Electric parallel gripper
- **ATI Force/Torque Sensors**: For precision assembly
- **Custom End-effectors**: Via ISO flange

## Typical Applications by Industry
- **Electronics**: PCB handling, connector assembly, testing
- **Automotive**: Small component assembly, testing, inspection
- **Medical Devices**: Device assembly, packaging, inspection
- **Consumer Electronics**: Phone assembly, camera module handling
- **Plastics**: Small part removal, secondary operations
- **Metal Fabrication**: CNC tending, deburring, polishing

## Performance Characteristics
- **Power Consumption**: 
  - Average: ~0.5 kW
  - Peak: ~1.2 kW
- **Compressed Air**: 6 bar (87 psi), 15 Nl/min
- **Noise Level**: <70 dB(A)
- **Temperature Range**: +5°C to +45°C (operating)
- **Relative Humidity**: 5-95% (non-condensing)
- **IP Rating**: IP30 (standard), IP67 (Foundry Plus version available)

## Mounting Options
- **Floor Mounting**: Standard configuration
- **Wall Mounting**: Available with mounting adapter
- **Ceiling Mounting**: Available with mounting adapter
- **Angle Mounting**: Any angle with proper adapter

## Maintenance
- **Expected Lifespan**: 60,000+ operating hours (high-duty cycle)
- **Maintenance Interval**: 8,000 operating hours or 40,000 km path length
- **Warranty**: 12 months standard
- **Consumables**: Gearbox lubrication (every 8,000 hours)
- **Battery Replacement**: Every 2-3 years (for position memory)

## Control System (IRC5)
- **Processing Power**: Dual-core processor
- **Memory**: 256 MB RAM
- **I/O Capacity**: Up to 16,000 signals (with DeviceNet)
- **Motion Control**: TrueMove & QuickMove (ABB's motion control)
- **Programming Storage**: Flash memory (no mechanical hard drive)

## Advanced Features
- **TrueMove**: Path accuracy and speed optimization
- **QuickMove**: Optimized motion for faster cycle times
- **Integrated Process Control**: For welding, dispensing, etc.
- **Force Control**: Optional integrated force control
- **Vision Integration**: Support for major vision systems
- **Multi-robot Coordination**: MultiMove (up to 4 robots)

## Advantages
- Very high speed and acceleration
- Excellent repeatability (±0.02 mm)
- Compact footprint
- Clean design with internal cabling
- Proven IRC5 controller technology
- Large ecosystem of tools and options
- Excellent path accuracy (TrueMove)

## Considerations
- Requires safety fencing (not collaborative)
- IRC5 controller required (additional space and cost)
- Programming requires RAPID knowledge (steeper learning curve)
- Higher initial cost compared to collaborative robots
- Requires compressed air for pneumatic connections
