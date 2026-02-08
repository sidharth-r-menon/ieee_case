#!/usr/bin/env python3
"""
Release Script - Open the gripper to release the grasped object

Usage:
    python release.py
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import motion_tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.motion_tools import release as release_tool


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Release the grasped object by opening the gripper"
    )
    return parser.parse_args()


def main():
    """Execute release operation"""
    args = parse_args()
    
    # Execute the release operation
    result_json = release_tool.invoke({})
    
    # Parse and display result
    result = json.loads(result_json)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
