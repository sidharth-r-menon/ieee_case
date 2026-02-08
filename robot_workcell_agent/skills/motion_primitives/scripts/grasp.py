#!/usr/bin/env python3
"""
Grasp Script - Close the gripper to grasp an object

Usage:
    python grasp.py --object "box_1"
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import motion_tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.motion_tools import grasp as grasp_tool


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Grasp an object by closing the gripper"
    )
    parser.add_argument(
        "--object",
        type=str,
        required=True,
        help='Name of the object to grasp (e.g., "box_1", "cube")'
    )
    return parser.parse_args()


def main():
    """Execute grasp operation"""
    args = parse_args()
    
    # Execute the grasp operation
    result_json = grasp_tool.invoke({"target_name": args.object})
    
    # Parse and display result
    result = json.loads(result_json)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
