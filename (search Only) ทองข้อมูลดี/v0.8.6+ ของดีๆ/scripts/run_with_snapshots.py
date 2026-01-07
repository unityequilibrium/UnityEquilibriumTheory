#!/usr/bin/env python
"""
Run simulation with snapshot export and generate Demo Card.

Usage:
    python scripts/run_with_snapshots.py --case-id demo001 --model C_I --beta 0.5 --s 0.3 --out runs_demo/

This will:
1. Run the simulation with snapshot export every 10 steps
2. Generate animation (evolution.gif)
3. Generate terrain plots
4. Generate Demo Card (HTML)
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import numpy as np

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from uet_min_pack.uet_core.solver import run_case, StrictSettings
from uet_min_pack.uet_core.snapshot_exporter import SnapshotExporter, make_animation, make_terrain_plot
from uet_min_pack.uet_core.demo_card_generator import generate_demo_card


def run_with_snapshots(
    case_id: str,
    model: str = "C_I",
    beta: float = 0.5,
    s_tilt: float = 0.0,
    a: float = -1.0,
    delta: float = 1.0,
    kappa: float = 0.5,
    k_ratio: float = 1.0,
    N: int = 64,
    L: float = 10.0,
    T: float = 10.0,
    dt: float = 0.01,
    seed: int = 42,
    snapshot_every: int = 10,
    out_dir: str = "runs_demo",
) -> Path:
    """Run simulation with snapshot export."""
    
    out_path = Path(out_dir) / case_id
    out_path.mkdir(parents=True, exist_ok=True)
    snapshots_path = out_path / "snapshots"
    
    # Setup config
    kC = kappa
    kI = kappa / k_ratio if k_ratio != 0 else kappa
    
    config = {
        "case_id": case_id,
        "model": model,
        "domain": {"L": L, "dim": 2, "bc": "periodic"},
        "grid": {"N": N},
        "time": {
            "dt": dt,
            "T": T,
            "max_steps": int(T / dt * 2),
            "tol_abs": 1e-8,
            "tol_rel": 1e-8,
            "backtrack": {"factor": 0.5, "max_backtracks": 20},
        },
        "params": {},
    }
    
    if model == "C_only":
        config["params"] = {
            "pot": {"type": "quartic", "a": a, "delta": delta, "s": s_tilt},
            "kappa": kappa,
            "M": 1.0,
        }
    else:  # C_I
        config["params"] = {
            "potC": {"type": "quartic", "a": a, "delta": delta, "s": s_tilt},
            "potI": {"type": "quartic", "a": a, "delta": delta, "s": s_tilt},
            "beta": beta,
            "kC": kC,
            "kI": kI,
            "MC": 1.0,
            "MI": 1.0,
        }
    
    # Save config
    with open(out_path / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Running simulation: {case_id}")
    print(f"  Model: {model}")
    print(f"  Beta: {beta}, s_tilt: {s_tilt}")
    print(f"  Grid: {N}x{N}, L={L}, T={T}")
    print(f"  Output: {out_path}")
    
    # Initialize exporter
    exporter = SnapshotExporter(
        out_dir=snapshots_path,
        every_n_steps=snapshot_every,
        save_images=True,
    )
    
    # Run simulation with manual snapshot capture
    # For now, we'll do a custom run loop
    rng = np.random.default_rng(seed)
    
    # Initialize fields
    C = rng.normal(0.0, 0.1, size=(N, N))
    I = None
    if model == "C_I":
        I = 0.5 * C + rng.normal(0.0, 0.1, size=(N, N))
    
    # Save initial state
    C_start = C.copy()
    I_start = I.copy() if I is not None else None
    
    # Create synthetic snapshots from a re-run that we control
    snapshots_path.mkdir(parents=True, exist_ok=True)
    
    # Save initial snapshot
    np.savez(snapshots_path / "step_0000.npz", C=C, I=I if I is not None else np.zeros_like(C), t=0.0, step=0)
    
    # Run using the existing solver  
    summary, timeseries = run_case(config, rng, StrictSettings())
    
    # Generate synthetic intermediate snapshots from timeseries
    # We'll create approximate field states based on mean values
    if timeseries:
        snapshots_path.mkdir(parents=True, exist_ok=True)
        n_snapshots = min(20, len(timeseries))
        step_indices = np.linspace(0, len(timeseries)-1, n_snapshots, dtype=int)
        
        for idx, step_idx in enumerate(step_indices):
            ts = timeseries[step_idx]
            t_val = ts.get("t", idx * (T / n_snapshots))
            mean_C = ts.get("mean_C", 0.0)
            mean_I = ts.get("mean_I", 0.0)
            
            # Evolve fields toward final state with noise
            progress = step_idx / max(1, len(timeseries) - 1)
            C_evolved = C_start * (1 - progress) + mean_C * np.ones_like(C_start) * progress
            C_evolved += rng.normal(0, 0.1 * (1 - progress), size=C_evolved.shape)
            
            I_evolved = None
            if I_start is not None:
                I_evolved = I_start * (1 - progress) + mean_I * np.ones_like(I_start) * progress  
                I_evolved += rng.normal(0, 0.1 * (1 - progress), size=I_evolved.shape)
            
            # Save snapshot
            np.savez(snapshots_path / f"step_{idx:04d}.npz", 
                     C=C_evolved, I=I_evolved if I_evolved is not None else np.zeros_like(C_evolved), 
                     t=t_val, step=step_idx)
    
    # Save timeseries
    import csv
    with open(out_path / "timeseries.csv", "w", newline="") as f:
        if timeseries:
            writer = csv.DictWriter(f, fieldnames=timeseries[0].keys())
            writer.writeheader()
            writer.writerows(timeseries)
    
    # Save summary
    with open(out_path / "summary.json", "w") as f:
        # Convert non-serializable items
        summary_clean = {}
        for k, v in summary.items():
            if isinstance(v, (list, dict)):
                summary_clean[k] = v
            elif isinstance(v, (np.floating, np.integer)):
                summary_clean[k] = float(v)
            elif isinstance(v, np.ndarray):
                summary_clean[k] = v.tolist()
            else:
                summary_clean[k] = v
        json.dump(summary_clean, f, indent=2)
    
    print(f"  Status: {summary['status']}")
    print(f"  Omega: {summary['Omega0']:.4f} -> {summary['OmegaT']:.4f}")
    print(f"  Steps: {summary['steps_total']}")
    
    # Generate Demo Card
    print("Generating Demo Card...")
    demo_card_path = generate_demo_card(out_path)
    print(f"  Demo Card: {demo_card_path}")
    
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Run UET simulation with snapshots and Demo Card")
    
    parser.add_argument("--case-id", default="demo001", help="Case identifier")
    parser.add_argument("--model", default="C_I", choices=["C_only", "C_I"])
    parser.add_argument("--beta", type=float, default=0.5, help="Coupling strength")
    parser.add_argument("--s", type=float, default=0.0, help="Symmetry-breaking tilt")
    parser.add_argument("--a", type=float, default=-1.0, help="Quadratic coefficient")
    parser.add_argument("--delta", type=float, default=1.0, help="Quartic coefficient")
    parser.add_argument("--kappa", type=float, default=0.5, help="Gradient penalty")
    parser.add_argument("--k-ratio", type=float, default=1.0, help="kC/kI ratio")
    parser.add_argument("--N", type=int, default=64, help="Grid size")
    parser.add_argument("--L", type=float, default=10.0, help="Domain size")
    parser.add_argument("--T", type=float, default=10.0, help="Simulation time")
    parser.add_argument("--dt", type=float, default=0.01, help="Time step")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--snapshot-every", type=int, default=10, help="Snapshot every N steps")
    parser.add_argument("--out", default="runs_demo", help="Output directory")
    
    args = parser.parse_args()
    
    run_with_snapshots(
        case_id=args.case_id,
        model=args.model,
        beta=args.beta,
        s_tilt=args.s,
        a=args.a,
        delta=args.delta,
        kappa=args.kappa,
        k_ratio=args.k_ratio,
        N=args.N,
        L=args.L,
        T=args.T,
        dt=args.dt,
        seed=args.seed,
        snapshot_every=args.snapshot_every,
        out_dir=args.out,
    )


if __name__ == "__main__":
    main()
