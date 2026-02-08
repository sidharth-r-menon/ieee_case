#!/usr/bin/env python3
"""
SKU Analyzer - Resolve object keywords to specific asset IDs

Usage:
    python analyze_sku.py --keyword "apple"
"""

import argparse
import json
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Resolve object keyword to specific asset ID and dimensions"
    )
    parser.add_argument(
        "--keyword",
        type=str,
        required=True,
        help='Object keyword (e.g., "apple", "box", "bottle")'
    )
    return parser.parse_args()


# Asset database mapping keywords to specific IDs
ASSET_DATABASE = {
    # Fruits
    "apple": {
        "sku_id": "mesh_fruit_apple_01",
        "dimensions": [0.08, 0.08, 0.09],  # x, y, z in meters
        "category": "fruit",
        "weight_kg": 0.2
    },
    "orange": {
        "sku_id": "mesh_fruit_orange_01",
        "dimensions": [0.09, 0.09, 0.09],
        "category": "fruit",
        "weight_kg": 0.15
    },
    "banana": {
        "sku_id": "mesh_fruit_banana_01",
        "dimensions": [0.18, 0.04, 0.04],
        "category": "fruit",
        "weight_kg": 0.12
    },
    
    # Containers
    "box": {
        "sku_id": "container_cardboard_medium",
        "dimensions": [0.30, 0.30, 0.20],
        "category": "container",
        "weight_kg": 0.5
    },
    "small box": {
        "sku_id": "container_cardboard_small",
        "dimensions": [0.15, 0.15, 0.10],
        "category": "container",
        "weight_kg": 0.2
    },
    "large box": {
        "sku_id": "container_cardboard_large",
        "dimensions": [0.50, 0.40, 0.30],
        "category": "container",
        "weight_kg": 1.0
    },
    "bin": {
        "sku_id": "container_plastic_bin",
        "dimensions": [0.40, 0.30, 0.20],
        "category": "container",
        "weight_kg": 0.8
    },
    
    # Bottles
    "bottle": {
        "sku_id": "bottle_plastic_500ml",
        "dimensions": [0.07, 0.07, 0.20],
        "category": "bottle",
        "weight_kg": 0.5
    },
    "water bottle": {
        "sku_id": "bottle_plastic_1l",
        "dimensions": [0.08, 0.08, 0.25],
        "category": "bottle",
        "weight_kg": 1.0
    },
    
    # Basic shapes
    "cube": {
        "sku_id": "primitive_cube_10cm",
        "dimensions": [0.10, 0.10, 0.10],
        "category": "primitive",
        "weight_kg": 0.5
    },
    "cylinder": {
        "sku_id": "primitive_cylinder_10cm",
        "dimensions": [0.10, 0.10, 0.15],
        "category": "primitive",
        "weight_kg": 0.6
    },
    "sphere": {
        "sku_id": "primitive_sphere_10cm",
        "dimensions": [0.10, 0.10, 0.10],
        "category": "primitive",
        "weight_kg": 0.4
    },
    
    # Tools
    "screwdriver": {
        "sku_id": "tool_screwdriver_standard",
        "dimensions": [0.20, 0.03, 0.03],
        "category": "tool",
        "weight_kg": 0.2
    },
    "wrench": {
        "sku_id": "tool_wrench_adjustable",
        "dimensions": [0.25, 0.05, 0.02],
        "category": "tool",
        "weight_kg": 0.3
    },
    
    # Workspace furniture
    "table": {
        "sku_id": "furniture_worktable_standard",
        "dimensions": [1.50, 1.00, 0.75],
        "category": "furniture",
        "weight_kg": 30.0
    },
    "workbench": {
        "sku_id": "furniture_workbench_industrial",
        "dimensions": [2.00, 0.80, 0.85],
        "category": "furniture",
        "weight_kg": 50.0
    },
    "shelf": {
        "sku_id": "furniture_shelf_4tier",
        "dimensions": [1.00, 0.40, 1.80],
        "category": "furniture",
        "weight_kg": 25.0
    },
    
    # Conveyor
    "conveyor": {
        "sku_id": "conveyor_belt_1m",
        "dimensions": [1.00, 0.30, 0.80],
        "category": "machinery",
        "weight_kg": 40.0
    }
}


def analyze_sku(keyword):
    """
    Resolve keyword to specific asset ID
    
    Args:
        keyword: Object keyword
        
    Returns:
        dict: Asset information or error
    """
    keyword_lower = keyword.lower().strip()
    
    # Direct match
    if keyword_lower in ASSET_DATABASE:
        asset = ASSET_DATABASE[keyword_lower]
        return {
            "success": True,
            "keyword": keyword,
            "sku_id": asset["sku_id"],
            "dimensions": asset["dimensions"],
            "category": asset["category"],
            "weight_kg": asset["weight_kg"]
        }
    
    # Partial match
    for key, asset in ASSET_DATABASE.items():
        if keyword_lower in key or key in keyword_lower:
            return {
                "success": True,
                "keyword": keyword,
                "matched_key": key,
                "sku_id": asset["sku_id"],
                "dimensions": asset["dimensions"],
                "category": asset["category"],
                "weight_kg": asset["weight_kg"]
            }
    
    # No match found
    return {
        "success": False,
        "keyword": keyword,
        "error": f"No asset found for keyword: {keyword}",
        "available_keywords": list(ASSET_DATABASE.keys())[:10]  # Show first 10 as hint
    }


def main():
    """Execute SKU analysis"""
    args = parse_args()
    
    # Analyze SKU
    result = analyze_sku(args.keyword)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
