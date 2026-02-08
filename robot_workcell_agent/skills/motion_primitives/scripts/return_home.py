#!/usr/bin/env python3
"""
Return Home Script - Return robot to home position

Usage:
    python return_home.py
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import motion_tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.motion_tools import return_home as return_home_tool


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Return robot to home position"
    )
    return parser.parse_args()


def main():
    """Execute return_home operation"""
    args = parse_args()
    
    # Execute the return_home operation
    result_json = return_home_tool.invoke({})
    
    # Parse and display result
    result = json.loads(result_json)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
