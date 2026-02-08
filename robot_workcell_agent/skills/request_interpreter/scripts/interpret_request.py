#!/usr/bin/env python3
"""
Request Interpreter - Convert natural language to structured scene JSON

Usage:
    python interpret_request.py --text "Set up a packing station with a Panda robot"
"""

import argparse
import json
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Interpret natural language request and map to scene JSON structure"
    )
    parser.add_argument(
        "--text",
        type=str,
        required=True,
        help='Natural language description of the robot task'
    )
    return parser.parse_args()


def interpret_request(text):
    """
    Parse natural language and extract structured scene data
    
    Args:
        text: Natural language request
        
    Returns:
        dict: Partial scene data with filled and null fields
    """
    text_lower = text.lower()
    
    # Initialize partial scene data
    scene_data = {
        "robot_configuration": {},
        "workcell_assets": [],
        "constraints": None,
        "task_description": text
    }
    
    # Robot detection
    robot_keywords = {
        "panda": "franka_panda",
        "franka": "franka_panda",
        "ur3": "ur3",
        "ur5": "ur5",
        "ur10": "ur10",
        "abb": "abb_irb1200",
        "kuka": "kuka_kr3"
    }
    
    for keyword, model_id in robot_keywords.items():
        if keyword in text_lower:
            scene_data["robot_configuration"]["model_id"] = model_id
            break
    else:
        scene_data["robot_configuration"]["model_id"] = None
    
    # Task type detection
    if "pick" in text_lower or "place" in text_lower:
        scene_data["task_type"] = "pick_place"
    elif "assembly" in text_lower:
        scene_data["task_type"] = "assembly"
    elif "pack" in text_lower:
        scene_data["task_type"] = "packing"
    else:
        scene_data["task_type"] = None
    
    # Workspace detection
    if "table" in text_lower or "workbench" in text_lower:
        scene_data["workcell_assets"].append({
            "type": "table",
            "model_id": "TBD",
            "position": None
        })
    
    # Object detection (basic)
    object_keywords = ["box", "apple", "bottle", "cube", "cylinder"]
    for obj in object_keywords:
        if obj in text_lower:
            scene_data["workcell_assets"].append({
                "type": obj,
                "model_id": "TBD",
                "position": None
            })
    
    return {
        "partial_scene_data": scene_data
    }


def main():
    """Execute request interpretation"""
    args = parse_args()
    
    # Interpret the request
    result = interpret_request(args.text)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
