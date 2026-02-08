#!/usr/bin/env python3
"""
Move To Script - Move robot end-effector to a target position

Usage:
    python move_to.py --position "0.5,0.0,0.42"
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import motion_tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.motion_tools import move_to as move_to_tool


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Move robot end-effector to a target position"
    )
    parser.add_argument(
        "--position",
        type=str,
        required=True,
        help='Target position as "x,y,z" (e.g., "0.5,0.0,0.42")'
    )
    return parser.parse_args()


def main():
    """Execute move_to operation"""
    args = parse_args()
    
    # Execute the move_to operation
    result_json = move_to_tool.invoke({"target_position": args.position})
    
    # Parse and display result
    result = json.loads(result_json)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
