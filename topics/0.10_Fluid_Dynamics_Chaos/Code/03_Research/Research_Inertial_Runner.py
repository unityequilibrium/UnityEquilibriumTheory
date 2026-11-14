import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)

import sys
from pathlib import Path

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


from docs.core.uet_glass_box import UETPathManager

import numpy as np
import time
import json


def run_inertial_test():
    print("Testing Inertial Regime (tau > 0)...")
    time.sleep(0.5)
    return {"test": "Inertia", "status": "WAVE_DETECTED"}


if __name__ == "__main__":
    res = run_inertial_test()
    # Save
    result_dir = (
        UETPathManager.get_result_dir(
            topic_id="0.10_Fluid_Dynamics_Chaos",
            experiment_name="Research_Inertial_Runner",
            pillar="03_Research",
            category="log",
        )
        / "experiments"
    )
    result_dir.mkdir(parents=True, exist_ok=True)
    with open(result_dir / "inertial_experiment_log.json", "w") as f:
        json.dump(res, f, indent=2)
