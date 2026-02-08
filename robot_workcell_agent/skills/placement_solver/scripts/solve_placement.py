#!/usr/bin/env python3
"""
Placement Solver - Optimize entity positions using PSO or Diffusion

Usage:
    python solve_placement.py --scene_json "path/to/scene.json" --algorithm "pso" --iterations 100
"""

import argparse
import json
import sys
import numpy as np
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Optimize spatial placement of entities"
    )
    parser.add_argument(
        "--scene_json",
        type=str,
        required=True,
        help='Path to scene JSON with entities and zones'
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="pso",
        choices=["pso", "diffusion"],
        help='Optimization algorithm to use'
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help='Number of optimization iterations'
    )
    return parser.parse_args()


def load_scene_data(scene_json_path):
    """Load scene data from JSON file"""
    try:
        with open(scene_json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load scene data: {e}")


def check_collision(pos1, size1, pos2, size2, safety_margin=0.1):
    """Check if two entities collide with safety margin"""
    for i in range(2):  # Check x and y
        dist = abs(pos1[i] - pos2[i])
        min_dist = (size1[i] + size2[i]) / 2 + safety_margin
        if dist < min_dist:
            return True
    return False


def check_zone_constraint(position, zone_bounds):
    """Check if position is within zone bounds"""
    x, y = position
    x_min, y_min = zone_bounds["bounds_min"]
    x_max, y_max = zone_bounds["bounds_max"]
    return x_min <= x <= x_max and y_min <= y <= y_max


def compute_ik_score(position, robot_base, max_reach):
    """
    Simplified IK reachability score
    Returns 0 if reachable, penalty if out of reach
    """
    dist = np.sqrt((position[0] - robot_base[0])**2 + (position[1] - robot_base[1])**2)
    if dist <= max_reach:
        return 0.0
    else:
        return (dist - max_reach) ** 2 * 10  # Quadratic penalty


def evaluate_layout(positions, entities, zones, robot_config):
    """
    Evaluate layout quality
    Lower score is better
    """
    cost = 0.0
    
    # Robot reach penalty
    robot_base = [0, 0]  # Assume robot at origin
    max_reach = robot_config.get("max_reach_m", 0.85)
    
    for i, entity in enumerate(entities):
        if entity.get("type") != "robot":
            ik_cost = compute_ik_score(positions[i][:2], robot_base, max_reach)
            cost += ik_cost * 5.0  # Weight for IK
    
    # Collision penalty
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            size_i = entities[i].get("dimensions", [0.3, 0.3, 0.3])
            size_j = entities[j].get("dimensions", [0.3, 0.3, 0.3])
            
            if check_collision(positions[i][:2], size_i[:2], positions[j][:2], size_j[:2]):
                cost += 100.0  # Heavy penalty for collision
    
    # Zone constraint penalty
    for i, entity in enumerate(entities):
        assigned_zone_id = entity.get("assigned_zone")
        if assigned_zone_id:
            zone = next((z for z in zones if z["zone_id"] == assigned_zone_id), None)
            if zone and not check_zone_constraint(positions[i][:2], zone):
                cost += 50.0  # Penalty for zone violation
    
    return cost


def pso_optimize(entities, zones, robot_config, iterations=100):
    """
    Particle Swarm Optimization for placement
    """
    np.random.seed(42)
    
    n_entities = len(entities)
    n_particles = 30
    
    # Initialize particles (x, y, theta for each entity)
    positions = np.random.uniform(-0.5, 0.5, (n_particles, n_entities, 3))
    velocities = np.random.uniform(-0.1, 0.1, (n_particles, n_entities, 3))
    
    personal_best_positions = positions.copy()
    personal_best_scores = np.array([evaluate_layout(p, entities, zones, robot_config) for p in positions])
    
    global_best_idx = np.argmin(personal_best_scores)
    global_best_position = personal_best_positions[global_best_idx].copy()
    global_best_score = personal_best_scores[global_best_idx]
    
    # PSO parameters
    w = 0.7  # Inertia
    c1 = 1.5  # Cognitive
    c2 = 1.5  # Social
    
    for iteration in range(iterations):
        for i in range(n_particles):
            # Update velocity
            r1, r2 = np.random.random(2)
            velocities[i] = (w * velocities[i] + 
                           c1 * r1 * (personal_best_positions[i] - positions[i]) +
                           c2 * r2 * (global_best_position - positions[i]))
            
            # Update position
            positions[i] += velocities[i]
            
            # Evaluate
            score = evaluate_layout(positions[i], entities, zones, robot_config)
            
            # Update personal best
            if score < personal_best_scores[i]:
                personal_best_scores[i] = score
                personal_best_positions[i] = positions[i].copy()
                
                # Update global best
                if score < global_best_score:
                    global_best_score = score
                    global_best_position = positions[i].copy()
    
    return global_best_position, global_best_score


def diffusion_optimize(entities, zones, robot_config, iterations=100):
    """
    Diffusion-based optimization (simplified gradient descent)
    """
    np.random.seed(42)
    
    n_entities = len(entities)
    
    # Initialize random positions
    positions = np.random.uniform(-0.5, 0.5, (n_entities, 3))
    
    learning_rate = 0.01
    best_positions = positions.copy()
    best_score = evaluate_layout(positions, entities, zones, robot_config)
    
    for iteration in range(iterations):
        # Add noise (diffusion)
        noise = np.random.normal(0, 0.05, positions.shape)
        trial_positions = positions + noise
        
        # Evaluate
        score = evaluate_layout(trial_positions, entities, zones, robot_config)
        
        # Accept if better
        if score < best_score:
            best_score = score
            best_positions = trial_positions.copy()
            positions = trial_positions
        else:
            # Reduce noise over time (annealing)
            positions = positions * 0.99 + best_positions * 0.01
    
    return best_positions, best_score


def main():
    """Execute placement optimization"""
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
    
    entities = scene_data.get("entities_to_place", [])
    zones = scene_data.get("defined_zones", [])
    robot_config = scene_data.get("robot_configuration", {})
    
    if not entities:
        print(json.dumps({
            "success": False,
            "error": "No entities to place"
        }, indent=2))
        sys.exit(1)
    
    # Run optimization
    if args.algorithm == "pso":
        optimal_positions, final_cost = pso_optimize(entities, zones, robot_config, args.iterations)
    else:  # diffusion
        optimal_positions, final_cost = diffusion_optimize(entities, zones, robot_config, args.iterations)
    
    # Format results
    placements = []
    for i, entity in enumerate(entities):
        placements.append({
            "entity_id": entity.get("id", f"entity_{i}"),
            "type": entity.get("type"),
            "position": {
                "x": float(optimal_positions[i][0]),
                "y": float(optimal_positions[i][1]),
                "z": entity.get("z_height", 0.42)
            },
            "orientation": {
                "theta": float(optimal_positions[i][2])
            }
        })
    
    result = {
        "status": "success",
        "algorithm_used": args.algorithm,
        "iterations": args.iterations,
        "placements": placements,
        "final_cost_score": float(final_cost),
        "quality": "excellent" if final_cost < 10 else "good" if final_cost < 50 else "acceptable"
    }
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
