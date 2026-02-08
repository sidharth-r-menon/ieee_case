#!/usr/bin/env python3
"""
Robot Selector - Select optimal robot based on task requirements

Usage:
    python select_robot.py --task "packing apples" --payload 5.0
"""

import argparse
import json
import sys
import re
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Select best robot for task based on requirements"
    )
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help='Task description (e.g., "packing apples", "heavy lifting")'
    )
    parser.add_argument(
        "--payload",
        type=float,
        default=None,
        help='Required payload capacity in kg (optional)'
    )
    parser.add_argument(
        "--reach",
        type=float,
        default=None,
        help='Required reach in meters (optional)'
    )
    return parser.parse_args()


def parse_robot_markdown(filepath):
    """
    Parse robot markdown file and extract specifications
    
    Args:
        filepath: Path to markdown file
        
    Returns:
        dict: Robot specifications
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    robot_id = filepath.stem
    
    # Extract payload (kg)
    payload_match = re.search(r'\*\*Maximum Payload\*\*:\s*(\d+(?:\.\d+)?)\s*kg', content)
    max_payload_kg = float(payload_match.group(1)) if payload_match else 3.0
    
    # Extract reach (mm or m)
    reach_match = re.search(r'\*\*Reach\*\*:\s*(\d+(?:\.\d+)?)\s*(mm|m)', content)
    if reach_match:
        reach_value = float(reach_match.group(1))
        reach_unit = reach_match.group(2)
        max_reach_m = reach_value / 1000.0 if reach_unit == 'mm' else reach_value
    else:
        max_reach_m = 0.5
    
    # Extract repeatability to determine precision
    repeatability_match = re.search(r'\*\*Repeatability\*\*:\s*±(\d+(?:\.\d+)?)\s*mm', content)
    if repeatability_match:
        repeatability = float(repeatability_match.group(1))
        precision = "high" if repeatability <= 0.05 else "medium"
    else:
        precision = "medium"
    
    # Extract use cases from Primary Applications section
    use_cases = []
    primary_apps_match = re.search(r'### Primary Applications\s*(.*?)(?:###|##|\Z)', content, re.DOTALL)
    if primary_apps_match:
        apps_text = primary_apps_match.group(1).lower()
        # Extract keywords from applications
        keywords = re.findall(r'\*\*(.*?)\*\*:', apps_text)
        use_cases = [kw.strip().lower() for kw in keywords]
    
    # Extract ideal for section for additional use cases
    ideal_for_match = re.search(r'### Ideal For\s*(.*?)(?:###|##|\Z)', content, re.DOTALL)
    if ideal_for_match:
        ideal_text = ideal_for_match.group(1).lower()
        # Look for common keywords
        if 'collaborative' in ideal_text or 'collaborative' in content.lower()[:500]:
            use_cases.append('collaborative')
        if 'precision' in ideal_text or 'lab' in ideal_text:
            use_cases.append('precision')
        if 'compact' in ideal_text or 'small' in ideal_text:
            use_cases.append('compact')
        if 'heavy' in ideal_text:
            use_cases.append('heavy')
        if 'fast' in ideal_text or 'high-speed' in ideal_text:
            use_cases.append('fast')
    
    # Extract overview/description
    overview_match = re.search(r'## Overview\s*(.*?)(?:##|\Z)', content, re.DOTALL)
    description = overview_match.group(1).strip() if overview_match else f"Robot {robot_id}"
    description = description.split('\n')[0]  # Take first line only
    
    return {
        "model_id": robot_id,
        "max_payload_kg": max_payload_kg,
        "max_reach_m": max_reach_m,
        "precision": precision,
        "use_cases": use_cases if use_cases else ["general"],
        "description": description
    }


def load_robot_database():
    """
    Load robot specifications from markdown files in references folder
    
    Returns:
        dict: Robot database
    """
    # Get references folder path relative to script
    script_dir = Path(__file__).parent
    references_dir = script_dir.parent / "references"
    
    if not references_dir.exists():
        print(f"Warning: References folder not found at {references_dir}", file=sys.stderr)
        return {}
    
    robot_db = {}
    
    # Load all markdown files
    for md_file in references_dir.glob("*.md"):
        try:
            robot_spec = parse_robot_markdown(md_file)
            robot_db[robot_spec["model_id"]] = robot_spec
        except Exception as e:
            print(f"Warning: Failed to parse {md_file.name}: {e}", file=sys.stderr)
    
    return robot_db


def select_robot(task_description, required_payload=None, required_reach=None, robot_database=None):
    """
    Select best robot based on task requirements
    
    Args:
        task_description: Natural language task description
        required_payload: Required payload in kg (optional)
        required_reach: Required reach in meters (optional)
        robot_database: Robot specifications database (optional, will load if None)
        
    Returns:
        dict: Selected robot with reasoning
    """
    # Load robot database if not provided
    if robot_database is None:
        robot_database = load_robot_database()
    
    if not robot_database:
        return {
            "selected_robot": None,
            "reasoning": "No robot database available. Please ensure robot reference files exist."
        }
    
    task_lower = task_description.lower()
    
    # Filter by payload if specified
    candidates = {}
    for robot_id, specs in robot_database.items():
        if required_payload and specs["max_payload_kg"] < required_payload:
            continue
        if required_reach and specs["max_reach_m"] < required_reach:
            continue
        candidates[robot_id] = specs
    
    if not candidates:
        return {
            "selected_robot": None,
            "reasoning": f"No robot meets requirements: payload={required_payload}kg, reach={required_reach}m"
        }
    
    # Score candidates based on task keywords
    scores = {}
    for robot_id, specs in candidates.items():
        score = 0
        for keyword in specs["use_cases"]:
            if keyword.lower() in task_lower:
                score += 1
        scores[robot_id] = score
    
    # Select robot with highest score
    if max(scores.values()) > 0:
        best_robot_id = max(scores, key=scores.get)
    else:
        # Default selection based on common scenarios
        if "heavy" in task_lower or "lift" in task_lower:
            # Prefer robots with high payload
            best_robot_id = max(candidates.keys(), key=lambda k: candidates[k]["max_payload_kg"])
        elif "precision" in task_lower or "lab" in task_lower or "research" in task_lower:
            # Prefer high precision robots
            high_precision = [k for k, v in candidates.items() if v["precision"] == "high"]
            best_robot_id = high_precision[0] if high_precision else list(candidates.keys())[0]
        elif "compact" in task_lower or "small" in task_lower:
            # Prefer compact robots (small reach)
            best_robot_id = min(candidates.keys(), key=lambda k: candidates[k]["max_reach_m"])
        else:
            # Default to medium payload robot
            best_robot_id = sorted(candidates.keys(), key=lambda k: abs(candidates[k]["max_payload_kg"] - 5.0))[0]
    
    selected = candidates[best_robot_id]
    
    return {
        "selected_robot": {
            "model_id": selected["model_id"],
            "max_payload_kg": selected["max_payload_kg"],
            "max_reach_m": selected["max_reach_m"],
            "precision": selected["precision"]
        },
        "reasoning": selected["description"]
    }


def main():
    """Execute robot selection"""
    args = parse_args()
    
    # Select robot
    result = select_robot(args.task, args.payload, args.reach)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result["selected_robot"] else 1)


if __name__ == "__main__":
    main()
