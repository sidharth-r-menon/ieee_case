#!/usr/bin/env python3
"""
Gap Resolver - Identify and resolve missing scene data

Usage:
    python resolve_gaps.py --scene_json "path/to/partial_scene.json"
"""

import argparse
import json
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Analyze partial scene data and identify gaps"
    )
    parser.add_argument(
        "--scene_json",
        type=str,
        required=True,
        help='Path to partial scene JSON file or JSON string'
    )
    return parser.parse_args()


def load_scene_data(scene_json_input):
    """Load scene data from file or string"""
    # Try as file first
    if Path(scene_json_input).exists():
        with open(scene_json_input, 'r') as f:
            return json.load(f)
    else:
        # Try as JSON string
        try:
            return json.loads(scene_json_input)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON input: {scene_json_input}")


def identify_gaps(scene_data):
    """
    Identify missing or TBD fields in scene data
    
    Args:
        scene_data: Partial scene data dictionary
        
    Returns:
        list: List of identified gaps
    """
    gaps = []
    
    # Check robot configuration
    robot_config = scene_data.get("robot_configuration", {})
    if not robot_config.get("model_id"):
        gaps.append({
            "field": "robot_configuration.model_id",
            "type": "missing_robot",
            "can_auto_resolve": True,
            "resolver": "robot_selector"
        })
    
    # Check workcell assets
    assets = scene_data.get("workcell_assets", [])
    for i, asset in enumerate(assets):
        if asset.get("model_id") == "TBD" or not asset.get("model_id"):
            gaps.append({
                "field": f"workcell_assets[{i}].model_id",
                "type": "vague_asset",
                "object_type": asset.get("type", "unknown"),
                "can_auto_resolve": True,
                "resolver": "sku_analyzer"
            })
        
        if asset.get("position") is None:
            gaps.append({
                "field": f"workcell_assets[{i}].position",
                "type": "missing_position",
                "can_auto_resolve": False,
                "needs_user_input": True
            })
    
    # Check task type
    if not scene_data.get("task_type"):
        gaps.append({
            "field": "task_type",
            "type": "missing_task_type",
            "can_auto_resolve": False,
            "needs_user_input": True
        })
    
    return gaps


def generate_user_questions(gaps):
    """
    Generate natural language questions for gaps that need user input
    
    Args:
        gaps: List of identified gaps
        
    Returns:
        list: List of user-facing questions
    """
    questions = []
    
    for gap in gaps:
        if not gap.get("can_auto_resolve", False):
            if gap["type"] == "missing_task_type":
                questions.append("What type of task will this robot perform? (e.g., pick and place, assembly, packing)")
            elif gap["type"] == "missing_position":
                field = gap["field"]
                questions.append(f"Where should the {gap.get('object_type', 'object')} be positioned? (provide x, y, z coordinates)")
    
    return questions


def main():
    """Execute gap resolution"""
    args = parse_args()
    
    # Load scene data
    try:
        scene_data = load_scene_data(args.scene_json)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2))
        sys.exit(1)
    
    # Identify gaps
    gaps = identify_gaps(scene_data)
    
    # Separate auto-resolvable and user-required gaps
    auto_gaps = [g for g in gaps if g.get("can_auto_resolve", False)]
    user_gaps = [g for g in gaps if not g.get("can_auto_resolve", False)]
    
    # Generate user questions if needed
    user_questions = generate_user_questions(user_gaps)
    
    # Prepare result
    result = {
        "is_complete": len(gaps) == 0,
        "total_gaps": len(gaps),
        "auto_resolvable_gaps": len(auto_gaps),
        "gaps_requiring_user_input": len(user_gaps),
        "gaps": gaps,
        "user_questions": user_questions if user_questions else None,
        "updated_scene_data": scene_data
    }
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result["is_complete"] else 1)


if __name__ == "__main__":
    main()
