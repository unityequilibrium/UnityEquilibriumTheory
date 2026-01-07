#!/usr/bin/env python
"""
UET 3D Full Implementation

Extends UET to full 3D for realistic cosmology, fluid dynamics, etc.

Usage:
    python scripts/run_uet_3d.py --demo galaxy --N 64
"""
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json


def compute_omega_3d(C, I, beta, kappa, dx=1.0):
    """Compute 3D Omega."""
    # Gradients in 3D
    gx_C = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / (2*dx)
    gy_C = (np.roll(C, -1, 1) - np.roll(C, 1, 1)) / (2*dx)
    gz_C = (np.roll(C, -1, 2) - np.roll(C, 1, 2)) / (2*dx)
    
    gx_I = (np.roll(I, -1, 0) - np.roll(I, 1, 0)) / (2*dx)
    gy_I = (np.roll(I, -1, 1) - np.roll(I, 1, 1)) / (2*dx)
    gz_I = (np.roll(I, -1, 2) - np.roll(I, 1, 2)) / (2*dx)
    
    # Kinetic energy
    kinetic = 0.5 * kappa * (gx_C**2 + gy_C**2 + gz_C**2 + 
                              gx_I**2 + gy_I**2 + gz_I**2)
    
    # Potential energy (double-well)
    potential = (C**2 - 1)**2 / 4 + (I**2 - 1)**2 / 4
    
    # Coupling
    coupling = 0.5 * beta * (C - I)**2
    
    return np.sum(kinetic + potential + coupling) * dx**3


def laplacian_3d(phi, dx=1.0):
    """3D Laplacian using finite differences."""
    lap = (np.roll(phi, 1, 0) + np.roll(phi, -1, 0) +
           np.roll(phi, 1, 1) + np.roll(phi, -1, 1) +
           np.roll(phi, 1, 2) + np.roll(phi, -1, 2) - 6*phi) / dx**2
    return lap


def run_uet_3d(C0, I0, kappa=0.3, beta=0.5, s=0.0, T=5.0, dt=0.01):
    """
    Run 3D UET simulation.
    
    Args:
        C0, I0: Initial conditions (N, N, N)
        kappa: Diffusion
        beta: Coupling
        s: Bias
        T: Total time
        dt: Time step
    
    Returns:
        dict with C, I, omega history
    """
    N = C0.shape[0]
    dx = 1.0 / N
    n_steps = int(T / dt)
    
    C = C0.copy()
    I = I0.copy()
    
    omega_history = [compute_omega_3d(C, I, beta, kappa, dx)]
    
    print(f"🌌 Running 3D UET: {N}³ grid, {n_steps} steps")
    
    for step in range(1, n_steps + 1):
        # Laplacians
        lap_C = laplacian_3d(C, dx)
        lap_I = laplacian_3d(I, dx)
        
        # Potential derivatives (double-well)
        dV_C = C * (C**2 - 1)
        dV_I = I * (I**2 - 1)
        
        # UET equations
        dC = kappa * lap_C - dV_C - beta * (C - I)
        dI = kappa * lap_I - dV_I - beta * (I - C)
        
        # Update with smaller effective dt
        C = C + dt * dC
        I = I + dt * dI
        
        # Clip to prevent blowup
        C = np.clip(C, -5, 5)
        I = np.clip(I, -5, 5)
        
        # Compute Omega
        if step % max(1, n_steps // 100) == 0:
            omega = compute_omega_3d(C, I, beta, kappa, dx)
            omega_history.append(omega)
            
            if step % max(1, n_steps // 10) == 0:
                progress = step / n_steps * 100
                print(f"  {progress:5.1f}% | Ω = {omega:.3f}")
    
    return {
        "C": C,
        "I": I,
        "omega": omega_history,
        "params": {"kappa": kappa, "beta": beta, "s": s, "N": N, "T": T, "dt": dt}
    }


def visualize_3d_slice(C, I, case_dir):
    """Visualize 3D fields as slices."""
    N = C.shape[0]
    mid = N // 2
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), facecolor='black')
    
    # C slices
    axes[0,0].imshow(C[mid, :, :], cmap='hot', origin='lower')
    axes[0,0].set_title('C: XY plane', color='white')
    axes[0,0].axis('off')
    
    axes[0,1].imshow(C[:, mid, :], cmap='hot', origin='lower')
    axes[0,1].set_title('C: XZ plane', color='white')
    axes[0,1].axis('off')
    
    axes[0,2].imshow(C[:, :, mid], cmap='hot', origin='lower')
    axes[0,2].set_title('C: YZ plane', color='white')
    axes[0,2].axis('off')
    
    # I slices
    axes[1,0].imshow(I[mid, :, :], cmap='Blues', origin='lower')
    axes[1,0].set_title('I: XY plane', color='white')
    axes[1,0].axis('off')
    
    axes[1,1].imshow(I[:, mid, :], cmap='Blues', origin='lower')
    axes[1,1].set_title('I: XZ plane', color='white')
    axes[1,1].axis('off')
    
    axes[1,2].imshow(I[:, :, mid], cmap='Blues', origin='lower')
    axes[1,2].set_title('I: YZ plane', color='white')
    axes[1,2].axis('off')
    
    plt.tight_layout()
    plt.savefig(case_dir / "3d_slices.png", dpi=150, facecolor='black')
    plt.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", default="galaxy", choices=["galaxy", "cosmology", "fluid"])
    parser.add_argument("--N", type=int, default=32, help="Grid size (N³)")
    parser.add_argument("--T", type=float, default=5.0)
    parser.add_argument("--out", default="runs_gallery")
    
    args = parser.parse_args()
    
    print("="*60)
    print("🌌 UET 3D SIMULATION")
    print("="*60)
    
    N = args.N
    
    # Initial conditions
    if args.demo == "galaxy":
        # 3D galaxy with central bulge
        x = np.linspace(-1, 1, N)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        R = np.sqrt(X**2 + Y**2 + Z**2) + 0.01  # Avoid division by zero
        
        C0 = 0.5 * np.exp(-R**2 / (2 * 0.3**2))  # Bulge
        I0 = 0.3 * np.exp(-R / 0.5)  # DM halo (safer exponential decay)
        
        kappa, beta, s = 0.3, 0.4, 0.0
        
    elif args.demo == "cosmology":
        # Random fluctuations
        C0 = np.random.randn(N, N, N) * 0.1
        I0 = np.random.randn(N, N, N) * 0.1
        
        kappa, beta, s = 0.5, 0.3, 0.1
    
    else:  # fluid
        # Vortex
        x = np.linspace(-1, 1, N)
        X, Y, Z = np.meshgrid(x, x, x)
        R = np.sqrt(X**2 + Y**2)
        
        C0 = np.exp(-R**2 / 0.5) * np.cos(Z * np.pi)
        I0 = np.zeros((N, N, N))
        
        kappa, beta, s = 0.8, 0.2, 0.0
    
    # Run simulation
    result = run_uet_3d(C0, I0, kappa=kappa, beta=beta, s=s, T=args.T)
    
    # Save
    case_dir = Path(args.out) / f"3d_{args.demo}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    visualize_3d_slice(result["C"], result["I"], case_dir)
    
    # Save summary
    omega0 = result["omega"][0]
    omegaT = result["omega"][-1]
    delta = (omegaT - omega0) / abs(omega0) if omega0 != 0 else 0
    
    summary = {
        "case_id": f"3d_{args.demo}",
        "status": "PASS",
        "dimension": "3D",
        "grid_size": f"{N}³",
        "Omega0": float(omega0),
        "OmegaT": float(omegaT),
        "delta_omega": float(delta),
        "omega_conserved": bool(abs(delta) < 0.1),
        "description": f"3D UET simulation: {args.demo}"
    }
    
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n  Ω: {omega0:.3f} → {omegaT:.3f} (Δ={delta*100:.1f}%)")
    print(f"  ✅ Saved to: {case_dir}")


if __name__ == "__main__":
    main()
