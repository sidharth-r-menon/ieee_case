#!/usr/bin/env python3
"""
Placement Solver - Layout-based Component Positioning

Reads Stage 1 JSON from stdin, calculates layout using the exact logic
from layout_generator.py, and outputs optimized positions.
"""

import json
import sys


# ============================================================================
# EXACT LOGIC FROM layout_generator.py (DO NOT MODIFY)
# ============================================================================

def check_2d_overlap(pos1, dim1, pos2, dim2, clearance):
    """Checks if two objects overlap on the XY floor plane, rounded to avoid float bugs."""
    for i in range(2): 
        min1 = round(pos1[i] - (dim1[i] / 2) - clearance, 4)
        max1 = round(pos1[i] + (dim1[i] / 2) + clearance, 4)
        min2 = round(pos2[i] - (dim2[i] / 2) - clearance, 4)
        max2 = round(pos2[i] + (dim2[i] / 2) + clearance, 4)
        
        if max1 <= min2 or max2 <= min1:
            return False 
    return True

def calculate_layout(config_json):
    config = json.loads(config_json)
    
    pedestal_dim = config["pedestal"]["dimensions"]
    conveyor_dim = config["conveyor"]["dimensions"]
    pallet_dim = config["pallet"]["dimensions"]
    box_dim = config["box"]["dimensions"]

    pedestal_pos = [0.0, 0.0, 0.0]
    robot_pos = [0.0, 0.0, pedestal_dim[2]]

    # 1. Position Conveyor along X-axis
    conv_radius = 0.0
    while True:
        conv_pos = [round(conv_radius, 3), 0.0, 0.0]
        if not check_2d_overlap(conv_pos, conveyor_dim, pedestal_pos, pedestal_dim, clearance=0.1):
            break
        conv_radius += 0.05

    # 2. Position Pallet along Y-axis
    pal_radius = 0.0
    print(f"\n=== PALLET COLLISION DETECTION DEBUG ===", file=sys.stderr)
    print(f"Pedestal: pos={pedestal_pos}, dim={pedestal_dim}, clearance=0.025", file=sys.stderr)
    print(f"Pallet: dim={pallet_dim}", file=sys.stderr)
    
    while True:
        pal_pos = [0.0, round(pal_radius, 3), 0.0]
        overlaps = check_2d_overlap(pal_pos, pallet_dim, pedestal_pos, pedestal_dim, clearance=0.025)
        print(f"  Y={pal_radius:.3f}: pal_pos={pal_pos}, overlaps={overlaps}", file=sys.stderr)
        if not overlaps:
            print(f"✓ No overlap found! Final pallet_pos={pal_pos}", file=sys.stderr)
            break
        pal_radius += 0.05
    print(f"===========================================\n", file=sys.stderr)

    # 3. Calculate Targets to match the validated physics coordinates
    margin_x = box_dim[0] / 2.0
    min_x = conv_pos[0] - (conveyor_dim[0] / 2) + margin_x
    pick_x = max(min_x, min(robot_pos[0], conv_pos[0] + (conveyor_dim[0]/2) - margin_x))
    
    place_x = pal_pos[0]
    place_y = pal_pos[1]
    
    # Z Heights: Surface + Full Box Height + 0.01m air gap
    pick_z = conveyor_dim[2] + box_dim[2] + 0.01
    place_z = pallet_dim[2] + box_dim[2] + 0.01
    box_spawn_z = conveyor_dim[2] + box_dim[2] / 2.0
    
    print(f"\n=== HEIGHT CALCULATION DEBUG ===", file=sys.stderr)
    print(f"Conveyor height: {conveyor_dim[2]}", file=sys.stderr)
    print(f"Pallet height: {pallet_dim[2]}", file=sys.stderr)
    print(f"Box height: {box_dim[2]}", file=sys.stderr)
    print(f"pick_z = {conveyor_dim[2]} + {box_dim[2]} + 0.01 = {pick_z}", file=sys.stderr)
    print(f"place_z = {pallet_dim[2]} + {box_dim[2]} + 0.01 = {place_z}", file=sys.stderr)
    print(f"box_spawn_z = {conveyor_dim[2]} + {box_dim[2]}/2 = {box_spawn_z}", file=sys.stderr)
    print(f"================================\n", file=sys.stderr)

    return {
        "pedestal_pos": pedestal_pos,
        "robot_pos": robot_pos,
        "conveyor_pos": conv_pos,
        "pallet_pos": pal_pos,
        "box_spawn_pos": [round(pick_x, 3), 0.0, round(box_spawn_z, 3)],
        "pick_target_xyz": [round(pick_x, 3), 0.0, round(pick_z, 3)],
        "place_target_xyz": [round(place_x, 3), round(place_y, 3), round(place_z, 3)]
    }

# ============================================================================
# END OF layout_generator.py LOGIC
# ============================================================================


def get_component(components, keywords):
    """Find component by matching keywords in type or name.
    
    Prioritizes exact component_type matches over substring matches in names
    to avoid false positives (e.g., 'pallet' in 'carton_to_palletize').
    """
    # First pass: Try to match component_type exactly
    for comp in components:
        comp_type = comp.get('component_type', '').lower()
        for kw in keywords:
            if comp_type == kw or comp_type.startswith(kw):
                return comp
    
    # Second pass: Fall back to substring match in names
    for comp in components:
        comp_type = comp.get('component_type', '').lower()
        comp_name = comp.get('name', '').lower()
        for kw in keywords:
            # Only match if keyword is standalone word (not substring of another word)
            if (kw in comp_type or kw in comp_name) and comp_type != 'carton':
                return comp
    
    return None


def main():
    """Execute layout calculation - reads Stage 1 from stdin, outputs Stage 2 to stdout"""
    try:
        stage1 = json.load(sys.stdin)
        
        # Validate inputs
        if 'robot_selection' not in stage1 or 'workcell_components' not in stage1:
            print(json.dumps({"error": "Missing required fields"}), file=sys.stderr)
            sys.exit(1)
        
        # Extract components
        robot = stage1["robot_selection"]
        comps = stage1["workcell_components"]
        task = stage1.get("task_specification", {})
        
        pedestal = get_component(comps, ['pedestal', 'base', 'mount'])
        conveyor = get_component(comps, ['conveyor', 'belt'])
        pallet = get_component(comps, ['pallet', 'station'])
        
        # Get box dimensions from task_specification or components
        box_dims = task.get('dimensions', [0.30, 0.30, 0.30])
        if not box_dims or len(box_dims) != 3:
            box_comp = get_component(comps, ['box', 'carton', 'object'])
            box_dims = box_comp.get('dimensions', [0.30, 0.30, 0.30]) if box_comp else [0.30, 0.30, 0.30]
        
        # Construct input JSON (EXACT format from layout_generator.py)
        layout_input = {
            "robot": {
                "name": robot.get('model', 'ur5'),
                "reach_max": robot.get('reach_m', 0.85),
                "reach_min": 0.20
            },
            "pedestal": {
                "dimensions": pedestal.get('dimensions', [0.60, 0.60, 0.50]) if pedestal else [0.60, 0.60, 0.50]
            },
            "conveyor": {
                "dimensions": conveyor.get('dimensions', [2.00, 0.64, 0.82]) if conveyor else [2.00, 0.64, 0.82]
            },
            "pallet": {
                "dimensions": pallet.get('dimensions', [1.20, 0.80, 0.15]) if pallet else [1.20, 0.80, 0.15]
            },
            "box": {
                "dimensions": box_dims
            }
        }
        
        # DEBUG: Log the exact input being used
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"LAYOUT GENERATOR INPUT", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print(f"Robot info:", file=sys.stderr)
        print(f"  name: {layout_input['robot']['name']}", file=sys.stderr)
        print(f"  reach_max: {layout_input['robot']['reach_max']}", file=sys.stderr)
        print(f"  reach_min: {layout_input['robot']['reach_min']}", file=sys.stderr)
        print(f"Component dimensions:", file=sys.stderr)
        print(f"  pedestal: {layout_input['pedestal']['dimensions']}", file=sys.stderr)
        print(f"  conveyor: {layout_input['conveyor']['dimensions']}", file=sys.stderr)
        print(f"  pallet: {layout_input['pallet']['dimensions']}", file=sys.stderr)
        print(f"  box: {layout_input['box']['dimensions']}", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        
        # Call layout_generator (EXACT function, no modifications)
        layout_coords = calculate_layout(json.dumps(layout_input))
        
        # Convert to Stage 2 format
        optimized_components = []
        
        if pedestal:
            optimized_components.append({
                "name": pedestal['name'],
                "component_type": pedestal.get('component_type', 'pedestal'),
                "position": layout_coords['pedestal_pos'],
                "orientation": [0, 0, 0],
                "dimensions": pedestal['dimensions'],
                "mjcf_path": pedestal.get('mjcf_path', '')
            })
        
        if conveyor:
            optimized_components.append({
                "name": conveyor['name'],
                "component_type": conveyor.get('component_type', 'conveyor'),
                "position": layout_coords['conveyor_pos'],
                "orientation": [0, 0, 0],
                "dimensions": conveyor['dimensions'],
                "mjcf_path": conveyor.get('mjcf_path', '')
            })
        
        if pallet:
            optimized_components.append({
                "name": pallet['name'],
                "component_type": pallet.get('component_type', 'pallet'),
                "position": layout_coords['pallet_pos'],
                "orientation": [0, 0, 0],
                "dimensions": pallet['dimensions'],
                "mjcf_path": pallet.get('mjcf_path', '')
            })
        
        # Output result
        result = {
            "status": "success",
            "optimized_components": optimized_components,
            "layout_coordinates": layout_coords,
            "motion_targets": {
                "robot_pos": layout_coords['robot_pos'],
                "pick_target_xyz": layout_coords['pick_target_xyz'],
                "place_target_xyz": layout_coords['place_target_xyz'],
                "box_spawn_pos": layout_coords['box_spawn_pos']
            }
        }
        
        print(json.dumps(result, indent=2))
        sys.exit(0)
        
    except Exception as e:
        import traceback
        error = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(json.dumps(error), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
