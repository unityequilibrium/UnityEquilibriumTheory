"""
Feedback and Transition Tracking for UET Harness.
Detects turning points, equilibrium, and identifies simulation phases.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

def analyze_run(run_dir: Path, threshold: float = 0.01) -> Dict[str, Any]:
    """
    Analyze a run directory for transitions and equilibrium.
    Saves and returns a feedback report.
    """
    run_dir = Path(run_dir)
    ts_p = run_dir / "timeseries.csv"
    if not ts_p.exists():
        return {"error": "Missing timeseries.csv"}

    try:
        df = pd.read_csv(ts_p)
    except Exception as e:
        return {"error": f"Failed to read timeseries: {e}"}

    if df.empty or "Omega" not in df.columns:
        return {"error": "Timeseries is empty or missing Omega column"}

    # Use accepted steps
    if "accepted" in df.columns:
        df_acc = df[df["accepted"] == 1].copy()
    else:
        df_acc = df.copy()

    if len(df_acc) < 5:
        return {"status": "insufficient_data", "phases": []}

    omega = df_acc["Omega"].to_numpy()
    steps = df_acc["step"].to_numpy()
    times = df_acc["t"].to_numpy()
    
    # 1. Detect Turning Points (Significant ΔΩ)
    d_omega = np.diff(omega)
    # Scale threshold by initial omega or 1.0
    scale = max(1.0, abs(omega[0]))
    abs_d_omega = np.abs(d_omega)
    
    turning_indices = np.where(abs_d_omega > threshold * scale)[0]
    turning_points = []
    for idx in turning_indices:
        turning_points.append({
            "step": int(steps[idx+1]),
            "t": float(times[idx+1]),
            "omega_before": float(omega[idx]),
            "omega_after": float(omega[idx+1]),
            "delta": float(d_omega[idx])
        })

    # 2. Detect Equilibrium (Stability window)
    equilibrium_reached = False
    equilibrium_step = None
    
    # Simple strategy: look for where mean|ΔΩ| in a sliding window falls below epsilon
    window_size = min(20, len(omega) // 5)
    if window_size > 5:
        epsilon = 1e-5 * scale
        for i in range(len(d_omega) - window_size, -1, -1):
            window_avg = np.mean(np.abs(d_omega[i:i+window_size]))
            if window_avg < epsilon:
                # Potential equilibrium
                equilibrium_reached = True
                equilibrium_step = int(steps[i])
            else:
                # If we were in equilibrium but now we aren't (looking backwards), 
                # then i+1 was the start of equilibrium.
                if equilibrium_reached:
                    equilibrium_step = int(steps[i+1])
                    break
    
    # 3. Identify Phases
    phases = []
    if not turning_points:
        phases.append({"name": "stable_descent", "steps": [int(steps[0]), int(steps[-1])], "avg_omega": float(np.mean(omega))})
    else:
        # Divide into phases based on first and last turning point
        first_tp = turning_points[0]["step"]
        last_tp = turning_points[-1]["step"]
        
        phases.append({
            "name": "initial", 
            "steps": [int(steps[0]), first_tp],
            "avg_omega": float(np.mean(omega[steps < first_tp])) if any(steps < first_tp) else float(omega[0])
        })
        
        phases.append({
            "name": "transition",
            "steps": [first_tp, last_tp],
            "avg_omega": float(np.mean(omega[(steps >= first_tp) & (steps <= last_tp)]))
        })
        
        phases.append({
            "name": "final",
            "steps": [last_tp, int(steps[-1])],
            "avg_omega": float(np.mean(omega[steps > last_tp])) if any(steps > last_tp) else float(omega[-1])
        })

    report = {
        "turning_points": turning_points,
        "equilibrium_reached": equilibrium_reached,
        "equilibrium_step": equilibrium_step,
        "phases": phases,
        "summary": {
            "total_steps": int(steps[-1]),
            "omega_initial": float(omega[0]),
            "omega_final": float(omega[-1]),
            "omega_drop": float(omega[0] - omega[-1])
        }
    }

    # Save to disk
    with open(run_dir / "feedback_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report
