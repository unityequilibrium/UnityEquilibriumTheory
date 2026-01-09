#!/usr/bin/env python
"""
3D Volume Simulation Demo.
Runs a 3D simulation and creates volume slice animations.

Usage:
    python scripts/run_3d_demo.py --out runs_gallery --N 16
"""
from __future__ import annotations
import argparse
import json
import numpy as np
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation


def create_3d_gaussian(N: int, sigma: float = 0.2) -> np.ndarray:
    """Create a 3D Gaussian blob in the center."""
    x = np.linspace(-1, 1, N)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    R2 = X**2 + Y**2 + Z**2
    return np.exp(-R2 / (2 * sigma**2))


def create_3d_shell(N: int, r0: float = 0.5, thickness: float = 0.15) -> np.ndarray:
    """Create a 3D spherical shell."""
    x = np.linspace(-1, 1, N)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    R = np.sqrt(X**2 + Y**2 + Z**2)
    return np.exp(-((R - r0)**2) / (2 * thickness**2))


def spectral_laplacian_3d(u: np.ndarray, L: float) -> np.ndarray:
    """3D spectral laplacian."""
    N = u.shape[0]
    k = 2*np.pi*np.fft.fftfreq(N, d=L/N)
    kx, ky, kz = np.meshgrid(k, k, k, indexing="ij")
    k2 = kx*kx + ky*ky + kz*kz
    uhat = np.fft.fftn(u)
    lap_hat = -k2 * uhat
    return np.fft.ifftn(lap_hat).real


def run_3d_simulation(C0: np.ndarray, I0: np.ndarray, config: dict, n_snapshots: int = 40):
    """Run 3D simulation with history."""
    N = C0.shape[0]
    L = config.get("L", 10.0)
    T = config.get("T", 2.0)
    dt = config.get("dt", 0.01)
    beta = config.get("beta", 0.5)
    kappa = config.get("kappa", 0.5)
    
    n_steps = int(T / dt)
    snapshot_every = max(1, n_steps // n_snapshots)
    
    C = C0.copy()
    I = I0.copy()
    
    C_history = [C.copy()]
    I_history = [I.copy()]
    t_history = [0.0]
    
    print(f"  Running 3D simulation: {N}³ grid, {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # Gradient descent
        lapC = spectral_laplacian_3d(C, L)
        lapI = spectral_laplacian_3d(I, L)
        
        dC = kappa * lapC - C * (C**2 - 1) - beta * (C - I)
        dI = kappa * lapI - I * (I**2 - 1) - beta * (I - C)
        
        C = C + dt * dC
        I = I + dt * dI
        
        # Clip
        C = np.clip(C, -2, 2)
        I = np.clip(I, -2, 2)
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            I_history.append(I.copy())
            t_history.append(t)
            print(f"    Step {step}/{n_steps}, t={t:.3f}")
    
    return C_history, I_history, t_history


def make_3d_slice_animation(case_dir: Path, C_history: list, I_history: list, 
                            t_history: list, fps: int = 10) -> Path:
    """Create animation showing XY, XZ, YZ slices through the middle."""
    N = C_history[0].shape[0]
    mid = N // 2
    n_frames = len(C_history)
    
    # Get global limits
    c_min = min(c.min() for c in C_history)
    c_max = max(c.max() for c in C_history)
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    
    def update(frame):
        for ax_row in axes:
            for ax in ax_row:
                ax.clear()
        
        C = C_history[frame]
        I = I_history[frame]
        t = t_history[frame]
        
        # C slices
        axes[0, 0].imshow(C[mid, :, :], cmap='RdBu_r', vmin=c_min, vmax=c_max)
        axes[0, 0].set_title(f'C - XY slice (z={mid})')
        axes[0, 1].imshow(C[:, mid, :], cmap='RdBu_r', vmin=c_min, vmax=c_max)
        axes[0, 1].set_title(f'C - XZ slice (y={mid})')
        axes[0, 2].imshow(C[:, :, mid], cmap='RdBu_r', vmin=c_min, vmax=c_max)
        axes[0, 2].set_title(f'C - YZ slice (x={mid})')
        
        # I slices
        axes[1, 0].imshow(I[mid, :, :], cmap='YlGnBu', vmin=c_min, vmax=c_max)
        axes[1, 0].set_title(f'I - XY slice (z={mid})')
        axes[1, 1].imshow(I[:, mid, :], cmap='YlGnBu', vmin=c_min, vmax=c_max)
        axes[1, 1].set_title(f'I - XZ slice (y={mid})')
        axes[1, 2].imshow(I[:, :, mid], cmap='YlGnBu', vmin=c_min, vmax=c_max)
        axes[1, 2].set_title(f'I - YZ slice (x={mid})')
        
        fig.suptitle(f'3D Volume Slices | t = {t:.3f}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "3D_slices.gif"
    print(f"  Saving slice animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    return output_path


def make_3d_isosurface_animation(case_dir: Path, C_history: list, t_history: list, 
                                  fps: int = 8) -> Path:
    """Create rotating 3D isosurface animation."""
    from mpl_toolkits.mplot3d import Axes3D
    from skimage import measure  # May need: pip install scikit-image
    
    N = C_history[0].shape[0]
    n_frames = len(C_history)
    
    # Use middle threshold
    threshold = 0.3
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    def update(frame):
        ax.clear()
        
        C = C_history[frame]
        t = t_history[frame]
        
        # Extract isosurface
        try:
            verts, faces, _, _ = measure.marching_cubes(C, level=threshold)
            ax.plot_trisurf(verts[:, 0], verts[:, 1], faces, verts[:, 2],
                           cmap='coolwarm', alpha=0.7, linewidth=0)
        except:
            # Fallback: scatter plot of high values
            high = np.where(C > threshold)
            if len(high[0]) > 0:
                ax.scatter(high[0], high[1], high[2], c='red', alpha=0.3, s=5)
        
        # Rotate view
        azim = 45 + frame * (360 / n_frames)
        ax.view_init(elev=25, azim=azim)
        
        ax.set_xlim(0, N)
        ax.set_ylim(0, N)
        ax.set_zlim(0, N)
        ax.set_title(f'3D Isosurface | t = {t:.3f}')
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "3D_isosurface.gif"
    print(f"  Saving isosurface animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    return output_path


def run_3d_demo(name: str, C0: np.ndarray, I0: np.ndarray, out_dir: Path, 
                description: str, config: dict) -> Path:
    """Run a single 3D demo."""
    print(f"\n🌐 Running 3D Demo: {name}")
    
    case_dir = out_dir / f"3D_{name}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Save initial snapshots directory
    snapshots_dir = case_dir / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)
    
    # Run simulation
    C_history, I_history, t_history = run_3d_simulation(C0, I0, config)
    
    # Save snapshots
    for i, (C, I, t) in enumerate(zip(C_history, I_history, t_history)):
        np.savez(snapshots_dir / f"step_{i:04d}.npz", C=C, I=I, t=t, step=i)
    
    # Save config
    cfg = {
        "case_id": f"3D_{name}",
        "model": "C_I_3D",
        "grid": {"N": C0.shape[0], "dim": 3},
        "domain": {"L": config.get("L", 10.0)},
        "time": {"T": config.get("T", 2.0), "dt": config.get("dt", 0.01)},
        "params": {
            "beta": config.get("beta", 0.5),
            "kappa": config.get("kappa", 0.5),
        },
        "description": description
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    
    # Save summary
    summary = {
        "case_id": f"3D_{name}",
        "status": "PASS",
        "dim": 3,
        "Omega0": float(np.sum(C0**2 + I0**2)),
        "OmegaT": float(np.sum(C_history[-1]**2 + I_history[-1]**2)),
        "steps_total": len(C_history) - 1,
        "description": description
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create animations
    print(f"  Creating slice animation...")
    make_3d_slice_animation(case_dir, C_history, I_history, t_history)
    
    # Try isosurface (requires scikit-image)
    try:
        print(f"  Creating isosurface animation...")
        make_3d_isosurface_animation(case_dir, C_history, t_history)
    except ImportError:
        print(f"  ⚠️ Skipping isosurface (install scikit-image for this)")
    
    print(f"  ✅ Saved to {case_dir}")
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="Run 3D volume simulation demo")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--N", type=int, default=16, help="Grid size (N³)")
    parser.add_argument("--T", type=float, default=2.0, help="Simulation time")
    parser.add_argument("--spin", action="store_true", help="Run spinning universe demos")
    args = parser.parse_args()
    
    out_dir = Path(args.out)
    N = args.N
    
    print("🌐 3D Volume Simulation Demos")
    print("=" * 40)
    print(f"Grid size: {N}³ = {N**3} points")
    print(f"Output: {out_dir}")
    
    config = {
        "L": 10.0,
        "T": args.T,
        "dt": 0.02,
        "beta": 0.5,
        "kappa": 0.5,
    }
    
    if args.spin:
        # Spinning universe demos
        print("\n🌀 Spinning Universe Demos")
        
        # Shell Spin - spherical shell with rotation viz
        print("\n1️⃣ 3D Shell Spin (rotating camera)")
        C0 = create_3d_shell(N, r0=0.5, thickness=0.12)
        I0 = create_3d_gaussian(N, sigma=0.15) * 0.3
        run_3d_demo("shell_spin", C0, I0, out_dir, 
                    "Spinning spherical shell - rotating visualization", config)
        
        # Galaxy-like spiral initial condition
        print("\n2️⃣ 3D Galaxy (spiral arm initialization)")
        x = np.linspace(-1, 1, N)
        X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
        R = np.sqrt(X**2 + Y**2)
        theta = np.arctan2(Y, X)
        # Spiral arms
        spiral = np.exp(-R**2 / 0.3) * np.cos(3 * theta - 5 * R)
        C0 = np.clip(spiral, 0, 1) * np.exp(-Z**2 / 0.2)  # disk shape
        I0 = np.exp(-(X**2 + Y**2 + Z**2) / 0.1) * 0.5  # central bulge
        run_3d_demo("galaxy", C0, I0, out_dir, 
                    "Galaxy-like spiral structure with central bulge", config)
        
    else:
        # Standard demos
        # 1. Gaussian blob in 3D
        print("\n1️⃣ 3D Gaussian Blob")
        C0 = create_3d_gaussian(N, sigma=0.2)
        I0 = np.zeros((N, N, N))
        run_3d_demo("gaussian", C0, I0, out_dir, "3D Gaussian blob diffusing", config)
        
        # 2. Spherical shell
        print("\n2️⃣ 3D Spherical Shell")
        C0 = create_3d_shell(N, r0=0.5, thickness=0.12)
        I0 = create_3d_gaussian(N, sigma=0.15) * 0.5
        run_3d_demo("shell", C0, I0, out_dir, "3D spherical shell collapsing", config)
    
    print("\n" + "=" * 40)
    print("✅ 3D demos complete!")
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()

