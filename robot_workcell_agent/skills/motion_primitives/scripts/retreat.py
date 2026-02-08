#!/usr/bin/env python3
"""
Retreat Script - Move the end-effector upward to retreat from object

Usage:
    python retreat.py --height 0.1
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import motion_tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.motion_tools import retreat as retreat_tool


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Move the robot end-effector upward to retreat from object"
    )
    parser.add_argument(
        "--height",
        type=float,
        default=0.1,
        help="Height to retreat in meters (default: 0.1)"
    )
    return parser.parse_args()


def main():
    """Execute retreat operation"""
    args = parse_args()
    
    # Execute the retreat operation
    result_json = retreat_tool.invoke({"height": args.height})
    
    # Parse and display result
    result = json.loads(result_json)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
