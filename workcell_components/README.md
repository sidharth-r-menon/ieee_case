# Workcell Components Library

This directory contains MJCF models for common industrial workcell components that can be used with the Genesis Scene Builder.

## Directory Structure

```
workcell_components/
├── tables/
│   ├── standard_table.xml      # Standard work table (1.5m x 1.0m x 0.75m height)
│   └── workbench.xml            # Large workbench (2.0m x 1.2m x 0.8m height)
├── boxes/
│   ├── small_box.xml            # Small box (0.1m cube)
│   ├── medium_box.xml           # Medium box (0.2m cube)
│   └── cardboard_box.xml        # Cardboard box (0.3m cube)
├── conveyors/
│   └── conveyor_belt.xml        # Conveyor belt (2.0m x 0.6m)
├── pedestals/
│   └── robot_pedestal.xml       # Robot mounting pedestal (0.5m diameter, 0.9m height)
└── pallets/
    └── euro_pallet.xml          # Euro pallet (1.2m x 0.8m x 0.144m)
```

## Component Specifications

### Tables

**standard_table.xml**
- Dimensions: 1.5m (L) x 1.0m (W) x 0.75m (H)
- Mass: ~28 kg
- Use: Standard work surface

**workbench.xml**
- Dimensions: 2.0m (L) x 1.2m (W) x 0.8m (H)
- Mass: ~42 kg
- Use: Large work area for multiple operations

### Boxes

**small_box.xml**
- Dimensions: 0.1m x 0.1m x 0.1m
- Mass: 0.1 kg
- Use: Small parts, fasteners

**medium_box.xml**
- Dimensions: 0.2m x 0.2m x 0.2m
- Mass: 0.3 kg
- Use: Medium-sized objects

**cardboard_box.xml**
- Dimensions: 0.3m x 0.3m x 0.3m
- Mass: 0.5 kg
- Use: Packaging, storage

### Conveyors

**conveyor_belt.xml**
- Dimensions: 2.0m (L) x 0.6m (W) x 0.8m (H)
- Mass: ~50 kg
- Use: Material transport

### Pedestals

**robot_pedestal.xml**
- Dimensions: 0.5m (diameter) x 0.9m (H)
- Mass: ~65 kg
- Use: Robot mounting platform

### Pallets

**euro_pallet.xml**
- Dimensions: 1.2m (L) x 0.8m (W) x 0.144m (H)
- Mass: ~24 kg
- Use: Material handling, storage

## Usage with Genesis Scene Builder

To use these components in your scene, reference them with the full path:

```json
{
  "name": "main_table",
  "urdf": "D:/GitHub/ieee_case/workcell_components/tables/standard_table.xml",
  "position": [0.5, 0.0, 0.375],
  "orientation": [0, 0, 0]
}
```

## Notes

- All models are in MJCF format (.xml)
- All dimensions are in meters
- All angles are in degrees
- Fixed components (tables, conveyors, pedestals) should have appropriate mass and friction
- Coordinate system: X-forward, Y-left, Z-up
