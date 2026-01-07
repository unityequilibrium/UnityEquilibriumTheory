#!/usr/bin/env python
"""
Add Omega to Einstein demos - run this after einstein demos complete.
"""
import json
import numpy as np
from pathlib import Path


def compute_omega(C, I, beta, kappa):
    """Compute UET Omega."""
    N = C.shape[0]
    dx = 1.0 / N
    
    grad_C_x = (np.roll(C, -1, axis=0) - np.roll(C, 1, axis=0)) / (2*dx)
    grad_C_y = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2*dx)
    grad_I_x = (np.roll(I, -1, axis=0) - np.roll(I, 1, axis=0)) / (2*dx)
    grad_I_y = (np.roll(I, -1, axis=1) - np.roll(I, 1, axis=1)) / (2*dx)
    
    kinetic = 0.5 * kappa * (grad_C_x**2 + grad_C_y**2 + grad_I_x**2 + grad_I_y**2)
    V_C = (C**2 - 1)**2 / 4
    V_I = (I**2 - 1)**2 / 4
    coupling = beta * C * I
    
    return float(np.sum(kinetic + V_C + V_I + coupling) * dx**2)


def add_omega_to_demo(demo_dir):
    """Add Omega to a demo's summary.json."""
    demo_dir = Path(demo_dir)
    summary_file = demo_dir / "summary.json"
    
    # Load snapshots
    snapshots_dir = demo_dir / "snapshots"
    if not snapshots_dir.exists():
        print(f"  ⚠️ No snapshots in {demo_dir.name}")
        return
    
    # Load first and last
    files = sorted(snapshots_dir.glob("step_*.npz"))
    if len(files) < 2:
        print(f"  ⚠️ Not enough snapshots in {demo_dir.name}")
        return
    
    data_0 = np.load(files[0])
    data_f = np.load(files[-1])
    
    C0, I0 = data_0["C"], data_0["I"]
    Cf, If = data_f["C"], data_f["I"]
    
    omega0 = compute_omega(C0, I0, beta=0.5, kappa=0.3)
    omegaf = compute_omega(Cf, If, beta=0.5, kappa=0.3)
    delta = (omegaf - omega0) / abs(omega0) if omega0 != 0 else 0
    
    # Update summary
    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)
    else:
        summary = {}
    
    summary["Omega0"] = omega0
    summary["OmegaT"] = omegaf
    summary["delta_omega"] = delta
    summary["omega_conserved"] = abs(delta) < 0.1
    
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"  ✅ {demo_dir.name}: Ω={omega0:.3f} → {omegaf:.3f} (Δ={delta*100:.1f}%)")


if __name__ == "__main__":
    base = Path("runs_gallery")
    
    print("🌌 Adding Omega to Einstein demos...")
    
    for demo in ["einstein_wave", "einstein_collapse", "einstein_binary"]:
        add_omega_to_demo(base / demo)
    
    print("\n✅ Done!")
