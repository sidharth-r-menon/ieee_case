# Standard Object Dimensions Database

## Overview
Use this reference when users mention common objects without specifying dimensions.

## When to Use
- User says "standard size" or "typical"
- Common objects like pallets, cartons, bottles
- Make assumptions explicit to user

## Standard Dimensions

### Pallets
- **Euro Pallet**: [1.20, 0.80, 0.15] m, 25 kg
- **US Standard Pallet**: [1.22, 1.02, 0.144] m, 30 kg
- **Half Pallet**: [0.60, 0.80, 0.144] m, 12 kg

### Cartons/Boxes
- **Small Carton**: [0.20, 0.15, 0.15] m, 1-2 kg
- **Medium Carton**: [0.30, 0.30, 0.30] m, 3-8 kg
- **Large Carton**: [0.60, 0.40, 0.40] m, 10-15 kg
- **Shipping Box (Standard)**: [0.45, 0.35, 0.30] m, 5 kg

### Bottles
- **500ml Bottle**: [0.07, 0.07, 0.20] m, 0.5 kg
- **1L Bottle**: [0.08, 0.08, 0.25] m, 1.0 kg
- **2L Bottle**: [0.10, 0.10, 0.30] m, 2.0 kg

### Fruits & Vegetables
- **Apple**: [0.08, 0.08, 0.09] m, 0.2 kg
- **Orange**: [0.09, 0.09, 0.09] m, 0.15 kg
- **Banana**: [0.18, 0.04, 0.04] m, 0.12 kg
- **Tomato**: [0.07, 0.07, 0.07] m, 0.15 kg

### Industrial Components
- **Small Bin**: [0.30, 0.20, 0.15] m, 2 kg (empty)
- **Medium Bin**: [0.60, 0.40, 0.30] m, 5 kg (empty)
- **Tray**: [0.40, 0.30, 0.05] m, 1 kg

### Workcell Infrastructure (CRITICAL - USE THESE EXACT DIMENSIONS)
- **Robot Pedestal (Standard)**: [0.60, 0.60, 0.50] m (L × W × H), 50 kg
  - This is the standard mount for industrial robots
  - DO NOT use [0.5, 0.5, 0.5] or other dimensions
- **Conveyor Belt (Standard Industrial)**: [2.00, 0.64, 0.82] m (L × W × H), 100 kg
  - Length: 2.0m, Width: 0.64m (belt width + frame), Height: 0.82m (working height)
  - DO NOT use [1.0, 0.5, 0.5] or other dimensions
- **Pallet (Euro Standard)**: [1.20, 0.80, 0.15] m (already listed above)

## Usage Guidelines

Assume standard dimensions when user says "standard/typical". State assumptions clearly. Ask if user mentions custom sizes, non-standard items, or weights near robot payload limits.
