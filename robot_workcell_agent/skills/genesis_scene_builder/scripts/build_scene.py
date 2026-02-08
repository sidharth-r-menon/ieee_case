#!/usr/bin/env python3
"""
Genesis Scene Builder - Construct Genesis simulation environment

Usage:
    python build_scene.py --layout_json "path/to/layout.json"
"""

import argparse
import json
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Build Genesis simulation scene from layout plan"
    )
    parser.add_argument(
        "--layout_json",
        type=str,
        required=True,
        help='Path to layout plan JSON file'
    )
    parser.add_argument(
        "--physics_substeps",
        type=int,
        default=10,
        help='Physics simulation substeps'
    )
    return parser.parse_args()


def load_layout_plan(layout_json_path):
    """Load layout plan from JSON file"""
    try:
        with open(layout_json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load layout plan: {e}")


def build_scene(layout_plan, physics_settings):
    """
    Construct Genesis scene from layout plan
    
    Args:
        layout_plan: Dictionary with entity placements
        physics_settings: Physics configuration
        
    Returns:
        dict: Scene construction result
    """
    loaded_assets = []
    scene_entities = []
    
    # Process each placement
    placements = layout_plan.get("placements", [])
    
    for placement in placements:
        entity_id = placement.get("entity_id")
        entity_type = placement.get("type")
        position = placement.get("position", {})
        orientation = placement.get("orientation", {})
        
        # Map entity type to asset file
        asset_mapping = {
            "robot": "robots/franka_panda/panda.urdf",
            "table": "furniture/table_standard.urdf",
            "box": "objects/box_medium.urdf",
            "apple": "objects/apple.obj",
            "bottle": "objects/bottle.urdf",
            "conveyor": "machinery/conveyor_belt.urdf"
        }
        
        asset_file = asset_mapping.get(entity_type, f"objects/{entity_type}.urdf")
        
        scene_entity = {
            "entity_id": entity_id,
            "asset_path": asset_file,
            "initial_pose": {
                "position": [
                    position.get("x", 0),
                    position.get("y", 0),
                    position.get("z", 0.42)
                ],
                "orientation": {
                    "euler": [0, 0, orientation.get("theta", 0)]
                }
            },
            "properties": {
                "mass": placement.get("mass", 1.0),
                "fixed_base": entity_type in ["robot", "table", "conveyor"]
            }
        }
        
        scene_entities.append(scene_entity)
        loaded_assets.append(entity_id)
    
    # Scene configuration
    scene_config = {
        "scene_id": f"scene_{hash(str(layout_plan)) % 10000:04d}",
        "physics_settings": physics_settings,
        "entities": scene_entities,
        "lighting": {
            "ambient_intensity": 0.6,
            "directional_lights": [
                {
                    "direction": [1, 1, -1],
                    "intensity": 0.8
                }
            ]
        },
        "cameras": [
            {
                "camera_id": "overhead",
                "position": [0, 0, 2.0],
                "look_at": [0, 0, 0.5],
                "fov": 60
            }
        ]
    }
    
    return {
        "scene_id": scene_config["scene_id"],
        "loaded_assets": loaded_assets,
        "total_entities": len(scene_entities),
        "physics_settings": physics_settings,
        "scene_config": scene_config,
        "ready_to_sim": True
    }


def main():
    """Execute scene building"""
    args = parse_args()
    
    # Load layout plan
    try:
        layout_plan = load_layout_plan(args.layout_json)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2))
        sys.exit(1)
    
    # Physics settings
    physics_settings = {
        "gravity": [0, 0, -9.8],
        "substeps": args.physics_substeps,
        "dt": 0.01
    }
    
    # Build scene
    result = build_scene(layout_plan, physics_settings)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
