# Object Database - Standard SKUs and Dimensions

This reference contains dimensional data and asset identifiers for common objects used in workcell simulations.

## Fruits

### Apple
- **Asset ID**: `mesh_fruit_apple_01`
- **Dimensions**: [0.08, 0.08, 0.09] meters (L × W × H)
- **Weight**: 0.2 kg
- **Shape**: Roughly spherical
- **Gripping**: Suction or adaptive gripper recommended
- **Keywords**: apple, fruit

### Orange
- **Asset ID**: `mesh_fruit_orange_01`
- **Dimensions**: [0.09, 0.09, 0.09] meters
- **Weight**: 0.25 kg
- **Shape**: Spherical
- **Gripping**: Suction or adaptive gripper
- **Keywords**: orange, citrus, fruit

### Banana
- **Asset ID**: `mesh_fruit_banana_01`
- **Dimensions**: [0.20, 0.04, 0.04] meters
- **Weight**: 0.15 kg
- **Shape**: Elongated curved
- **Gripping**: Parallel jaw gripper
- **Keywords**: banana, fruit

## Containers

### Small Cardboard Box
- **Asset ID**: `container_cardboard_small`
- **Dimensions**: [0.20, 0.20, 0.15] meters
- **Weight**: 0.3 kg (empty), up to 2 kg (loaded)
- **Material**: Cardboard
- **Gripping**: Parallel jaw or vacuum
- **Keywords**: box, small box, container, carton

### Medium Cardboard Box
- **Asset ID**: `container_cardboard_medium`
- **Dimensions**: [0.30, 0.30, 0.20] meters
- **Weight**: 0.5 kg (empty), up to 5 kg (loaded)
- **Material**: Cardboard
- **Gripping**: Parallel jaw or vacuum
- **Keywords**: box, medium box, container, carton

### Large Cardboard Box
- **Asset ID**: `container_cardboard_large`
- **Dimensions**: [0.40, 0.40, 0.30] meters
- **Weight**: 0.8 kg (empty), up to 10 kg (loaded)
- **Material**: Cardboard
- **Gripping**: Wide parallel jaw or vacuum array
- **Keywords**: box, large box, container, carton

### Plastic Bin - Small
- **Asset ID**: `container_bin_plastic_small`
- **Dimensions**: [0.25, 0.15, 0.10] meters
- **Weight**: 0.4 kg (empty)
- **Material**: Rigid plastic
- **Gripping**: Parallel jaw
- **Keywords**: bin, tray, container, plastic

### Plastic Bin - Medium
- **Asset ID**: `container_bin_plastic_medium`
- **Dimensions**: [0.40, 0.30, 0.15] meters
- **Weight**: 0.8 kg (empty)
- **Material**: Rigid plastic
- **Gripping**: Parallel jaw or vacuum
- **Keywords**: bin, tray, container, plastic

## Bottles

### Water Bottle - 500ml
- **Asset ID**: `bottle_plastic_500ml`
- **Dimensions**: [0.07, 0.07, 0.20] meters
- **Weight**: 0.5 kg (filled)
- **Material**: Plastic (PET)
- **Gripping**: Parallel jaw or adaptive gripper
- **Keywords**: bottle, water bottle, beverage

### Water Bottle - 1L
- **Asset ID**: `bottle_plastic_1000ml`
- **Dimensions**: [0.09, 0.09, 0.28] meters
- **Weight**: 1.0 kg (filled)
- **Material**: Plastic (PET)
- **Gripping**: Parallel jaw
- **Keywords**: bottle, water bottle, large bottle, beverage

### Glass Bottle
- **Asset ID**: `bottle_glass_standard`
- **Dimensions**: [0.08, 0.08, 0.25] meters
- **Weight**: 1.2 kg (filled)
- **Material**: Glass
- **Gripping**: Adaptive gripper with force control
- **Keywords**: bottle, glass bottle, beverage

## Geometric Shapes

### Cube - 50mm
- **Asset ID**: `shape_cube_50`
- **Dimensions**: [0.05, 0.05, 0.05] meters
- **Weight**: 0.1 kg
- **Material**: Wood or plastic
- **Gripping**: Parallel jaw or suction
- **Keywords**: cube, block, shape

### Cube - 100mm
- **Asset ID**: `shape_cube_100`
- **Dimensions**: [0.10, 0.10, 0.10] meters
- **Weight**: 0.4 kg
- **Material**: Wood or plastic
- **Gripping**: Parallel jaw or suction
- **Keywords**: cube, block, shape, large

### Cylinder - Standard
- **Asset ID**: `shape_cylinder_standard`
- **Dimensions**: [0.06, 0.06, 0.15] meters (diameter, diameter, height)
- **Weight**: 0.3 kg
- **Material**: Metal or plastic
- **Gripping**: Parallel jaw
- **Keywords**: cylinder, tube, shape

### Sphere - 80mm
- **Asset ID**: `shape_sphere_80`
- **Dimensions**: [0.08, 0.08, 0.08] meters
- **Weight**: 0.2 kg
- **Material**: Plastic or rubber
- **Gripping**: Adaptive gripper or suction
- **Keywords**: sphere, ball, shape

## Tools

### Screwdriver
- **Asset ID**: `tool_screwdriver_standard`
- **Dimensions**: [0.15, 0.03, 0.03] meters
- **Weight**: 0.15 kg
- **Material**: Metal/plastic handle
- **Gripping**: Parallel jaw
- **Keywords**: screwdriver, tool

### Wrench
- **Asset ID**: `tool_wrench_adjustable`
- **Dimensions**: [0.20, 0.04, 0.02] meters
- **Weight**: 0.3 kg
- **Material**: Metal
- **Gripping**: Parallel jaw
- **Keywords**: wrench, spanner, tool

### Hammer
- **Asset ID**: `tool_hammer_standard`
- **Dimensions**: [0.30, 0.05, 0.05] meters
- **Weight**: 0.5 kg
- **Material**: Metal head, wood handle
- **Gripping**: Parallel jaw (grip handle)
- **Keywords**: hammer, tool

## Furniture & Fixtures

### Workbench Table
- **Asset ID**: `furniture_workbench_standard`
- **Dimensions**: [1.50, 0.75, 0.75] meters
- **Weight**: 50 kg
- **Material**: Wood/metal
- **Mount Surface**: Yes
- **Keywords**: table, workbench, bench, surface

### Small Table
- **Asset ID**: `furniture_table_small`
- **Dimensions**: [1.00, 0.50, 0.75] meters
- **Weight**: 25 kg
- **Material**: Wood/metal
- **Mount Surface**: Yes
- **Keywords**: table, small table, surface

### Storage Shelf
- **Asset ID**: `furniture_shelf_metal`
- **Dimensions**: [1.20, 0.40, 1.80] meters
- **Weight**: 40 kg
- **Material**: Metal
- **Shelves**: 4 levels
- **Keywords**: shelf, shelving, storage

## Machinery

### Conveyor Belt - Small
- **Asset ID**: `machine_conveyor_small`
- **Dimensions**: [1.00, 0.30, 0.15] meters
- **Weight**: 30 kg
- **Speed**: 0.1-0.5 m/s (configurable)
- **Keywords**: conveyor, belt, transport

### Conveyor Belt - Medium
- **Asset ID**: `machine_conveyor_medium`
- **Dimensions**: [2.00, 0.50, 0.20] meters
- **Weight**: 60 kg
- **Speed**: 0.1-0.8 m/s (configurable)
- **Keywords**: conveyor, belt, transport, long

## Electronics

### Circuit Board (PCB)
- **Asset ID**: `electronics_pcb_standard`
- **Dimensions**: [0.15, 0.10, 0.002] meters
- **Weight**: 0.05 kg
- **Material**: FR4 with components
- **Gripping**: Vacuum recommended
- **Keywords**: pcb, circuit board, electronics

### Smartphone Casing
- **Asset ID**: `electronics_smartphone_case`
- **Dimensions**: [0.15, 0.07, 0.01] meters
- **Weight**: 0.08 kg
- **Material**: Plastic/aluminum
- **Gripping**: Vacuum or adaptive gripper
- **Keywords**: smartphone, phone, case, electronics

## Medical/Laboratory

### Test Tube
- **Asset ID**: `lab_test_tube_standard`
- **Dimensions**: [0.015, 0.015, 0.15] meters (diameter, diameter, height)
- **Weight**: 0.05 kg (with sample)
- **Material**: Glass
- **Gripping**: Specialized tube gripper or adaptive
- **Keywords**: test tube, vial, lab, sample

### Syringe
- **Asset ID**: `medical_syringe_standard`
- **Dimensions**: [0.02, 0.02, 0.12] meters
- **Weight**: 0.03 kg
- **Material**: Plastic
- **Gripping**: Parallel jaw (very light grip)
- **Keywords**: syringe, medical

### Petri Dish
- **Asset ID**: `lab_petri_dish`
- **Dimensions**: [0.09, 0.09, 0.015] meters (diameter, diameter, height)
- **Weight**: 0.02 kg
- **Material**: Plastic
- **Gripping**: Vacuum recommended
- **Keywords**: petri dish, lab, dish

## Usage Notes

### Keyword Matching
- The system performs fuzzy matching on keywords
- Common synonyms are included in keyword lists
- Use the most specific keyword for best results

### Weight Considerations
- Weights listed are typical values
- Always verify against robot payload capacity
- Include gripper weight in total payload calculation

### Gripper Recommendations
- **Suction/Vacuum**: Flat surfaces, light objects, delicate items
- **Parallel Jaw**: Regular shaped objects, moderate grip force
- **Adaptive/3-Finger**: Irregular shapes, variety of sizes
- **Specialized**: Test tubes, medical items, fragile objects

### Asset Loading
- All assets should be available in Genesis scene builder
- MJCF/URDF files are auto-loaded based on asset ID
- Custom assets can be added by extending this database
