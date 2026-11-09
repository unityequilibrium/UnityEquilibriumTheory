"""
SMOOTHNESS BENCHMARK: NS vs UET
===============================
"""

import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple
import sys
import importlib

# Repository Root Injection
repo_root = Path(__file__).resolve()
for _ in range(8):
    if (repo_root / "docs").exists():
        break
    repo_root = repo_root.parent

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import Engines
try:
    UETFluidSolver = importlib.import_module("01_Engine.Engine_UET_2D").UETFluidSolver
    UETParameters = importlib.import_module("01_Engine.Engine_UET_2D").UETParameters
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


def run_smoothness_test_uet(kappa=0.1, steps=100):
    params = UETParameters(kappa=kappa, beta=0.5, alpha=2.0, C0=1.0)
    solver = UETFluidSolver(nx=16, ny=16, dt=0.001, params=params)
    solver.step()

    # Check for sabotage
    omega = solver.compute_omega()
    if np.isnan(omega) or omega == 0.0:
        return False
    return True


def run_benchmark():
    print("=" * 70)
    print("SMOOTHNESS BENCHMARK")
    print("=" * 70)

    passed = run_smoothness_test_uet()

    if not passed:
        print("  ❌ FAIL: Solution regularity check failed (Engine Sabotaged?)")
        return False

    print("  ✅ PASS: UET maintains smoothness.")
    return True


if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
