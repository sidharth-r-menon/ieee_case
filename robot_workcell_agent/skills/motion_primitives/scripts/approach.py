#!/usr/bin/env python3
"""
Approach Script - Move above a target position with an offset

Usage:
    python approach.py --position "0.5,0.0,0.42" --offset 0.1
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import motion_tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.motion_tools import approach as approach_tool


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Move above a target position with an offset (approach phase)"
    )
    parser.add_argument(
        "--position",
        type=str,
        required=True,
        help='Target position as "x,y,z" (e.g., "0.5,0.0,0.42")'
    )
    parser.add_argument(
        "--offset",
        type=float,
        default=0.1,
        help="Height offset above target in meters (default: 0.1)"
    )
    return parser.parse_args()


def main():
    """Execute approach operation"""
    args = parse_args()
    
    # Execute the approach operation
    result_json = approach_tool.invoke({
        "target_position": args.position,
        "offset": args.offset
    })
    
    # Parse and display result
    result = json.loads(result_json)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
