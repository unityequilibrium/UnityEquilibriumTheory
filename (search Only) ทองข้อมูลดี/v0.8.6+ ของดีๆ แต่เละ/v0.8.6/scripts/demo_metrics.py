# demo_metrics.py – simple script that creates a run folder and records a few metrics using the METRICS registry

import os
from pathlib import Path
from datetime import datetime

# Import the record helper from the newly created METRICS module
from uet_core.metrics import record


def create_demo_run(base_dir: str = "runs") -> Path:
    """Create a dummy run directory with a timestamp and return its Path.
    The directory structure follows the spec: runs/<model>/<case_id>/<run_id>/"""
    model = "C_I"
    case_id = "demo_case"
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_path = Path(base_dir) / model / case_id / run_id
    run_path.mkdir(parents=True, exist_ok=True)
    return run_path


def main():
    run_dir = create_demo_run()
    # Record a few example metrics – these keys must exist in METRICS registry
    record("Omega0", 123.45, run_dir=str(run_dir))
    record("OmegaT", 98.76, run_dir=str(run_dir))
    record("dt", 0.01, run_dir=str(run_dir))
    record("energy", 5.32, run_dir=str(run_dir))
    print(f"Demo run created at: {run_dir}")
    print("Metrics written to metrics.json")


if __name__ == "__main__":
    main()
