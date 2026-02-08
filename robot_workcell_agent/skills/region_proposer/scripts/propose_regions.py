#!/usr/bin/env python3
"""
Region Proposer - Divide workspace into logical zones

Usage:
    python propose_regions.py --task_type "pick_place" --table_dims "1.5,1.0"
"""

import argparse
import json
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Propose logical workspace regions based on task type"
    )
    parser.add_argument(
        "--task_type",
        type=str,
        required=True,
        help='Task type: pick_place, assembly, packing'
    )
    parser.add_argument(
        "--table_dims",
        type=str,
        required=True,
        help='Table dimensions as "width,depth" in meters'
    )
    parser.add_argument(
        "--required_zones",
        type=str,
        default="",
        help='Comma-separated list of required zones'
    )
    return parser.parse_args()


def propose_regions(task_type, table_dims, required_zones=None):
    """
    Generate logical regions based on task workflow
    
    Args:
        task_type: Type of task (pick_place, assembly, packing)
        table_dims: [width, depth] of table in meters
        required_zones: List of required zone names
        
    Returns:
        dict: Proposed zones with bounds and priorities
    """
    width, depth = table_dims
    
    zones = []
    
    # Robot base zone (always needed, center-front)
    zones.append({
        "zone_id": "robot_base_zone",
        "description": "Reserved area for robot mounting",
        "bounds_min": [-0.2, -depth/2],
        "bounds_max": [0.2, -depth/2 + 0.2],
        "priority": 1,
        "type": "exclusion"
    })
    
    if task_type == "pick_place":
        # Input zone (left side)
        zones.append({
            "zone_id": "input_zone",
            "description": "Pick location for source objects",
            "bounds_min": [-width/2 + 0.1, -depth/4],
            "bounds_max": [-width/4, depth/4],
            "priority": 2,
            "type": "work"
        })
        
        # Output zone (right side)
        zones.append({
            "zone_id": "output_zone",
            "description": "Place location for target objects",
            "bounds_min": [width/4, -depth/4],
            "bounds_max": [width/2 - 0.1, depth/4],
            "priority": 2,
            "type": "work"
        })
        
    elif task_type == "assembly":
        # Central assembly zone
        zones.append({
            "zone_id": "central_assembly_zone",
            "description": "Main assembly work area",
            "bounds_min": [-0.3, 0.1],
            "bounds_max": [0.3, 0.5],
            "priority": 3,
            "type": "work"
        })
        
        # Parts zones (peripheral)
        zones.append({
            "zone_id": "parts_zone_left",
            "description": "Component storage area",
            "bounds_min": [-width/2 + 0.1, 0.0],
            "bounds_max": [-0.4, depth/2 - 0.1],
            "priority": 2,
            "type": "storage"
        })
        
        zones.append({
            "zone_id": "parts_zone_right",
            "description": "Component storage area",
            "bounds_min": [0.4, 0.0],
            "bounds_max": [width/2 - 0.1, depth/2 - 0.1],
            "priority": 2,
            "type": "storage"
        })
        
    elif task_type == "packing":
        # Input tray zone
        zones.append({
            "zone_id": "input_tray_zone",
            "description": "Source items to be packed",
            "bounds_min": [-width/2 + 0.2, 0.1],
            "bounds_max": [-width/4, depth/2 - 0.1],
            "priority": 2,
            "type": "work"
        })
        
        # Packing zone (center-right)
        zones.append({
            "zone_id": "packing_zone",
            "description": "Active packing area",
            "bounds_min": [0.0, 0.1],
            "bounds_max": [width/3, depth/2 - 0.1],
            "priority": 3,
            "type": "work"
        })
        
        # Output stack zone
        zones.append({
            "zone_id": "output_stack_zone",
            "description": "Completed packages",
            "bounds_min": [width/2 - 0.3, 0.0],
            "bounds_max": [width/2 - 0.1, depth/3],
            "priority": 2,
            "type": "storage"
        })
    
    else:
        # Generic layout for unknown task types
        zones.append({
            "zone_id": "work_zone_center",
            "description": "General work area",
            "bounds_min": [-0.4, 0.0],
            "bounds_max": [0.4, 0.6],
            "priority": 2,
            "type": "work"
        })
    
    # Safety margin zone (edges)
    zones.append({
        "zone_id": "safety_margin",
        "description": "Edge safety buffer",
        "bounds_min": [-width/2, -depth/2],
        "bounds_max": [width/2, depth/2],
        "priority": 0,
        "type": "exclusion",
        "note": "0.1m margin from edges"
    })
    
    return {
        "task_type": task_type,
        "table_dimensions": {"width": width, "depth": depth},
        "zones": zones,
        "total_zones": len(zones)
    }


def main():
    """Execute region proposal"""
    args = parse_args()
    
    # Parse table dimensions
    try:
        table_dims = [float(x) for x in args.table_dims.split(',')]
        if len(table_dims) != 2:
            raise ValueError("Table dimensions must be width,depth")
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid table dimensions: {e}"
        }, indent=2))
        sys.exit(1)
    
    # Parse required zones if provided
    required_zones = args.required_zones.split(',') if args.required_zones else None
    
    # Propose regions
    result = propose_regions(args.task_type, table_dims, required_zones)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
