#!/usr/bin/env python3
"""
Simulation Validator - Validate scene through physics simulation

Usage:
    python validate_simulation.py --scene_id "scene_1234" --checks "stability,collision,ik"
"""

import argparse
import json
import sys
import numpy as np
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Validate scene through simulation checks"
    )
    parser.add_argument(
        "--scene_id",
        type=str,
        required=True,
        help='Scene ID to validate'
    )
    parser.add_argument(
        "--checks",
        type=str,
        default="stability,collision,ik_reachability",
        help='Comma-separated list of checks to perform'
    )
    parser.add_argument(
        "--sim_steps",
        type=int,
        default=200,
        help='Number of simulation steps'
    )
    return parser.parse_args()


def check_static_stability(scene_data, sim_steps=200):
    """
    Simulate and check if objects remain stable
    
    Returns:
        dict: Stability check result
    """
    # Simulate basic physics (simplified)
    # In real implementation, this would use Genesis physics engine
    
    # Check for toppling by monitoring orientation changes
    unstable_objects = []
    
    # Simplified check: assume objects with high center of gravity might topple
    for entity in scene_data.get("entities", []):
        entity_id = entity.get("entity_id")
        dimensions = entity.get("dimensions", [0.1, 0.1, 0.2])
        
        # Height to width ratio
        if len(dimensions) >= 3:
            aspect_ratio = dimensions[2] / min(dimensions[0], dimensions[1])
            
            # High aspect ratio objects are more likely to be unstable
            if aspect_ratio > 3.0:
                unstable_objects.append({
                    "entity_id": entity_id,
                    "reason": f"High aspect ratio: {aspect_ratio:.2f}, may topple"
                })
    
    is_stable = len(unstable_objects) == 0
    
    return {
        "check_type": "static_stability",
        "passed": is_stable,
        "sim_steps": sim_steps,
        "unstable_objects": unstable_objects if not is_stable else None,
        "message": "All objects stable" if is_stable else f"{len(unstable_objects)} potentially unstable objects detected"
    }


def check_collision(scene_data):
    """
    Check for interpenetration/collision between entities
    
    Returns:
        dict: Collision check result
    """
    entities = scene_data.get("entities", [])
    collisions = []
    
    # Check pairwise collisions
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            entity_a = entities[i]
            entity_b = entities[j]
            
            pos_a = entity_a.get("initial_pose", {}).get("position", [0, 0, 0])
            pos_b = entity_b.get("initial_pose", {}).get("position", [0, 0, 0])
            
            # Simplified bounding box collision
            # Assume default sizes if not specified
            size_a = [0.3, 0.3, 0.3]  # Default size
            size_b = [0.3, 0.3, 0.3]
            
            # Check if bounding boxes overlap
            collision_detected = True
            for axis in range(3):
                dist = abs(pos_a[axis] - pos_b[axis])
                min_dist = (size_a[axis] + size_b[axis]) / 2
                
                if dist >= min_dist:
                    collision_detected = False
                    break
            
            if collision_detected:
                collisions.append({
                    "entity_a": entity_a.get("entity_id"),
                    "entity_b": entity_b.get("entity_id"),
                    "distance": float(np.linalg.norm(np.array(pos_a) - np.array(pos_b)))
                })
    
    is_collision_free = len(collisions) == 0
    
    return {
        "check_type": "collision",
        "passed": is_collision_free,
        "collisions": collisions if not is_collision_free else None,
        "message": "No collisions detected" if is_collision_free else f"{len(collisions)} collision(s) detected"
    }


def check_ik_reachability(scene_data):
    """
    Check if robot can reach target objects via IK
    
    Returns:
        dict: IK reachability check result
    """
    entities = scene_data.get("entities", [])
    
    # Find robot
    robot = next((e for e in entities if "robot" in e.get("entity_id", "").lower()), None)
    
    if not robot:
        return {
            "check_type": "ik_reachability",
            "passed": True,
            "message": "No robot in scene, IK check skipped"
        }
    
    robot_pos = robot.get("initial_pose", {}).get("position", [0, 0, 0])
    max_reach = 0.855  # Default Panda reach
    
    unreachable_objects = []
    
    # Check reach to all objects
    for entity in entities:
        if entity.get("entity_id") == robot.get("entity_id"):
            continue  # Skip robot itself
        
        if "table" in entity.get("entity_id", "").lower():
            continue  # Skip furniture
        
        obj_pos = entity.get("initial_pose", {}).get("position", [0, 0, 0])
        
        # Calculate 2D distance (x, y)
        dist_2d = np.sqrt((obj_pos[0] - robot_pos[0])**2 + (obj_pos[1] - robot_pos[1])**2)
        
        # Check if within reach
        if dist_2d > max_reach:
            unreachable_objects.append({
                "entity_id": entity.get("entity_id"),
                "distance": float(dist_2d),
                "max_reach": max_reach,
                "reason": f"Object at {dist_2d:.3f}m exceeds max reach of {max_reach}m"
            })
    
    is_reachable = len(unreachable_objects) == 0
    
    return {
        "check_type": "ik_reachability",
        "passed": is_reachable,
        "robot_position": robot_pos,
        "max_reach": max_reach,
        "unreachable_objects": unreachable_objects if not is_reachable else None,
        "message": "All objects reachable" if is_reachable else f"{len(unreachable_objects)} unreachable object(s)"
    }


def load_scene_data(scene_id):
    """
    Load scene data (mock implementation)
    In real implementation, this would load from Genesis scene
    """
    # Mock scene data - in reality this would come from Genesis
    return {
        "scene_id": scene_id,
        "entities": [
            {
                "entity_id": "robot_panda",
                "initial_pose": {"position": [0, 0, 0]},
                "dimensions": [0.2, 0.2, 0.5]
            },
            {
                "entity_id": "table_1",
                "initial_pose": {"position": [0, 0, -0.4]},
                "dimensions": [1.5, 1.0, 0.75]
            }
        ]
    }


def main():
    """Execute simulation validation"""
    args = parse_args()
    
    # Parse checks
    requested_checks = [c.strip() for c in args.checks.split(',')]
    
    # Load scene data
    scene_data = load_scene_data(args.scene_id)
    
    # Run requested checks
    check_results = []
    all_passed = True
    failure_reasons = []
    
    if "stability" in requested_checks:
        result = check_static_stability(scene_data, args.sim_steps)
        check_results.append(result)
        if not result["passed"]:
            all_passed = False
            failure_reasons.append(result["message"])
    
    if "collision" in requested_checks:
        result = check_collision(scene_data)
        check_results.append(result)
        if not result["passed"]:
            all_passed = False
            failure_reasons.append(result["message"])
    
    if "ik_reachability" in requested_checks or "ik" in requested_checks:
        result = check_ik_reachability(scene_data)
        check_results.append(result)
        if not result["passed"]:
            all_passed = False
            failure_reasons.append(result["message"])
    
    # Compile final result
    final_result = {
        "scene_id": args.scene_id,
        "result": "pass" if all_passed else "fail",
        "checks_performed": requested_checks,
        "total_checks": len(check_results),
        "passed_checks": sum(1 for c in check_results if c["passed"]),
        "failed_checks": sum(1 for c in check_results if not c["passed"]),
        "failure_reason": "; ".join(failure_reasons) if failure_reasons else None,
        "check_details": check_results,
        "sim_steps": args.sim_steps
    }
    
    # Pretty print the result
    print(json.dumps(final_result, indent=2))
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
