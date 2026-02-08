#!/usr/bin/env python3
"""
Lift Script - Lift the grasped object vertically

Usage:
    python lift.py --height 0.1
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import motion_tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.motion_tools import lift as lift_tool


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Lift the grasped object vertically"
    )
    parser.add_argument(
        "--height",
        type=float,
        default=0.1,
        help="Height to lift in meters (default: 0.1)"
    )
    return parser.parse_args()


def main():
    """Execute lift operation"""
    args = parse_args()
    
    # Execute the lift operation
    result_json = lift_tool.invoke({"height": args.height})
    
    # Parse and display result
    result = json.loads(result_json)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
