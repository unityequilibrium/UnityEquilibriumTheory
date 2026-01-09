#!/usr/bin/env python
"""
MI Card to Matrix Generator

Converts a filled MI Card (JSON) to UET matrix CSV for parameter sweeps.
"""
from __future__ import annotations
import json
import csv
from pathlib import Path
from typing import Optional
import numpy as np


def generate_matrix_from_mi_card(
    mi_card_path: str | Path,
    output_path: str | Path = "matrix.csv",
    n_points_per_axis: int = 10,
) -> Path:
    """
    Generate a parameter sweep matrix from an MI Card.
    
    Args:
        mi_card_path: Path to MI Card JSON file
        output_path: Output CSV path
        n_points_per_axis: Number of points per sweep axis
        
    Returns:
        Path to generated matrix CSV
    """
    with open(mi_card_path) as f:
        mi_card = json.load(f)
    
    # Extract sweep plan
    sweep = mi_card.get("sweep_plan", {})
    axis1 = sweep.get("axis1", {})
    axis2 = sweep.get("axis2", {})
    
    # Extract base config
    base = mi_card.get("base_config", {})
    model = base.get("model", "C_I")
    
    # Generate sweep values
    range1 = axis1.get("range", [0, 1])
    range2 = axis2.get("range", [0, 1])
    param1 = axis1.get("param", "s")
    param2 = axis2.get("param", "beta")
    
    values1 = np.linspace(range1[0], range1[1], n_points_per_axis)
    values2 = np.linspace(range2[0], range2[1], n_points_per_axis)
    
    # Generate matrix rows
    rows = []
    case_id = 1
    
    for v1 in values1:
        for v2 in values2:
            row = {
                "case_id": f"case_{case_id:04d}",
                "model": model,
                "grid": base.get("grid", 64),
                "dt": base.get("dt", 0.01),
                "T": base.get("T", 10.0),
                "seed": base.get("seed", 42),
                "params": _build_params_string(base, param1, v1, param2, v2),
            }
            rows.append(row)
            case_id += 1
    
    # Write CSV
    output_path = Path(output_path)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Generated matrix with {len(rows)} cases: {output_path}")
    return output_path


def _build_params_string(base: dict, param1: str, v1: float, param2: str, v2: float) -> str:
    """Build params string for matrix row."""
    # Start with base params
    params = base.get("params", {}).copy()
    
    # Override sweep params
    if param1 == "s":
        if "potC" in params:
            params["potC"]["s"] = v1
        if "potI" in params:
            params["potI"]["s"] = v1
        if "pot" in params:
            params["pot"]["s"] = v1
    elif param1 == "beta":
        params["beta"] = v1
    elif param1 == "kappa" or param1 == "kC":
        params["kC"] = v1
        params["kI"] = v1
    else:
        params[param1] = v1
    
    if param2 == "s":
        if "potC" in params:
            params["potC"]["s"] = v2
        if "potI" in params:
            params["potI"]["s"] = v2
        if "pot" in params:
            params["pot"]["s"] = v2
    elif param2 == "beta":
        params["beta"] = v2
    elif param2 == "kappa" or param2 == "kC":
        params["kC"] = v2
        params["kI"] = v2
    else:
        params[param2] = v2
    
    return json.dumps(params)


def create_example_mi_card(output_path: str | Path = "example_mi_card.json") -> Path:
    """Create an example MI Card JSON file."""
    mi_card = {
        "metadata": {
            "domain": "Conscience vs Instinct",
            "author": "UET Team",
            "version": "0.9",
        },
        "entity": {
            "description": "Human decision-making system",
            "C": "Conscience (moral reasoning)",
            "I": "Instinct (primal urges)",
            "constraints": [
                "Fields must be bounded",
                "Coupling must exist",
            ],
        },
        "world": {
            "field": "Social/ethical environment",
            "forces": {
                "push": "External incentives (s tilt)",
                "pull": "C-I coupling (beta)",
                "resist": "Gradient penalty (kappa)",
            },
        },
        "mapping": {
            "potential": {
                "description": "Satisfaction in choosing a side",
                "a": -1.0,
                "delta": 1.0,
            },
            "conflict": {
                "description": "Cost of changing mind",
                "kC": 0.5,
                "kI": 0.5,
            },
            "flow": {
                "description": "Decision timescale",
                "MC": 1.0,
                "MI": 1.0,
            },
        },
        "observables": {
            "primary": ["phase", "bias"],
            "exports": ["snapshots", "animation", "terrain"],
        },
        "sweep_plan": {
            "axis1": {
                "param": "s",
                "description": "Tilt - controls direction",
                "range": [-0.5, 0.5],
            },
            "axis2": {
                "param": "beta",
                "description": "Coupling - controls interaction",
                "range": [0.1, 0.9],
            },
        },
        "base_config": {
            "model": "C_I",
            "grid": 64,
            "dt": 0.01,
            "T": 10.0,
            "seed": 42,
            "params": {
                "potC": {"type": "quartic", "a": -1.0, "delta": 1.0, "s": 0.0},
                "potI": {"type": "quartic", "a": -1.0, "delta": 1.0, "s": 0.0},
                "beta": 0.5,
                "kC": 0.5,
                "kI": 0.5,
                "MC": 1.0,
                "MI": 1.0,
            },
        },
    }
    
    output_path = Path(output_path)
    with open(output_path, "w") as f:
        json.dump(mi_card, f, indent=2)
    
    print(f"Created example MI Card: {output_path}")
    return output_path


def validate_mi_card(mi_card_path: str | Path) -> tuple[bool, list[str]]:
    """
    Validate an MI Card for completeness.
    
    Returns:
        (is_valid, list of issues)
    """
    required_sections = ["entity", "world", "mapping", "observables", "sweep_plan", "base_config"]
    issues = []
    
    try:
        with open(mi_card_path) as f:
            mi_card = json.load(f)
    except Exception as e:
        return False, [f"Failed to load JSON: {e}"]
    
    # Check required sections
    for section in required_sections:
        if section not in mi_card:
            issues.append(f"Missing required section: {section}")
    
    # Check entity
    entity = mi_card.get("entity", {})
    if not entity.get("C"):
        issues.append("Entity: C field not defined")
    if not entity.get("description"):
        issues.append("Entity: description not provided")
    
    # Check sweep plan
    sweep = mi_card.get("sweep_plan", {})
    for axis in ["axis1", "axis2"]:
        if axis not in sweep:
            issues.append(f"Sweep plan: {axis} not defined")
        else:
            if "param" not in sweep[axis]:
                issues.append(f"Sweep plan: {axis}.param not defined")
            if "range" not in sweep[axis]:
                issues.append(f"Sweep plan: {axis}.range not defined")
    
    # Check base config
    base = mi_card.get("base_config", {})
    if "model" not in base:
        issues.append("Base config: model not specified")
    if "params" not in base:
        issues.append("Base config: params not specified")
    
    return len(issues) == 0, issues


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MI Card to Matrix Generator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create example
    create_parser = subparsers.add_parser("create-example", help="Create example MI Card")
    create_parser.add_argument("--output", "-o", default="example_mi_card.json")
    
    # Validate
    validate_parser = subparsers.add_parser("validate", help="Validate MI Card")
    validate_parser.add_argument("mi_card", help="Path to MI Card JSON")
    
    # Generate matrix
    gen_parser = subparsers.add_parser("generate", help="Generate matrix from MI Card")
    gen_parser.add_argument("mi_card", help="Path to MI Card JSON")
    gen_parser.add_argument("--output", "-o", default="matrix.csv")
    gen_parser.add_argument("--n-points", "-n", type=int, default=10)
    
    args = parser.parse_args()
    
    if args.command == "create-example":
        create_example_mi_card(args.output)
    elif args.command == "validate":
        is_valid, issues = validate_mi_card(args.mi_card)
        if is_valid:
            print("✅ MI Card is valid!")
        else:
            print("❌ MI Card has issues:")
            for issue in issues:
                print(f"  - {issue}")
    elif args.command == "generate":
        is_valid, issues = validate_mi_card(args.mi_card)
        if not is_valid:
            print("❌ Cannot generate matrix - MI Card has issues:")
            for issue in issues:
                print(f"  - {issue}")
            return
        generate_matrix_from_mi_card(args.mi_card, args.output, args.n_points)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
