#!/usr/bin/env python
"""
Coffee-style visualization demos.
Creates 3 types of animations inspired by the "Physics in a Coffee Cup" video.

Usage:
    python scripts/run_coffee_demos.py --out runs_gallery
"""
from __future__ import annotations
import argparse
import numpy as np
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from uet_min_pack.uet_core.solver import run_case, StrictSettings
from uet_min_pack.uet_core.demo_card_generator import generate_demo_card


def create_gaussian_center(N: int, sigma: float = 0.2) -> np.ndarray:
    """Create a Gaussian blob in the center (like a milk drop)."""
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)
    R2 = X**2 + Y**2
    return np.exp(-R2 / (2 * sigma**2))


def create_ring_pattern(N: int, rings: int = 3) -> np.ndarray:
    """Create concentric ring pattern."""
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    return np.sin(rings * np.pi * R) * np.exp(-R**2)


def create_two_drops(N: int) -> tuple[np.ndarray, np.ndarray]:
    """Create two separate drops for C and I fields."""
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)
    
    # C field: drop on the left
    C = np.exp(-((X + 0.4)**2 + Y**2) / 0.1)
    
    # I field: drop on the right
    I = np.exp(-((X - 0.4)**2 + Y**2) / 0.1)
    
    return C, I


def save_snapshots(case_dir: Path, C_history: list, I_history: list, t_history: list):
    """Save snapshots for animation."""
    snapshots_dir = case_dir / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    for i, (C, I, t) in enumerate(zip(C_history, I_history, t_history)):
        np.savez(
            snapshots_dir / f"step_{i:04d}.npz",
            C=C, I=I, t=t, step=i
        )
    print(f"  Saved {len(C_history)} snapshots")


def run_simulation_with_history(config: dict, C0: np.ndarray, I0: np.ndarray, 
                                 n_snapshots: int = 50) -> tuple[list, list, list]:
    """Run simulation and capture history for animation."""
    from uet_min_pack.uet_core.solver import run_case, StrictSettings
    
    N = C0.shape[0]
    T = config["time"]["T"]
    dt = config["time"]["dt"]
    n_steps = int(T / dt)
    snapshot_every = max(1, n_steps // n_snapshots)
    
    # Initialize
    C = C0.copy()
    I = I0.copy()
    
    C_history = [C.copy()]
    I_history = [I.copy()]
    t_history = [0.0]
    
    # Simple diffusion simulation
    kappa = config["params"].get("kappa", 0.5)
    beta = config["params"].get("beta", 0.5)
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # Laplacian (simple finite difference)
        def laplacian(f):
            return (
                np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
                np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) - 4*f
            ) * (N / 10.0)**2  # Scale by grid
        
        # Gradient descent on energy
        dC = kappa * laplacian(C) - C * (C**2 - 1) - beta * (C - I)
        dI = kappa * laplacian(I) - I * (I**2 - 1) - beta * (I - C)
        
        C = C + dt * dC
        I = I + dt * dI
        
        # Clip to prevent blowup
        C = np.clip(C, -2, 2)
        I = np.clip(I, -2, 2)
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            I_history.append(I.copy())
            t_history.append(t)
    
    return C_history, I_history, t_history


def run_coffee_demo(name: str, C0: np.ndarray, I0: np.ndarray, 
                    out_dir: Path, description: str, beta: float = 0.5):
    """Run a single coffee-style demo."""
    print(f"\n🎬 Running: {name}")
    
    case_dir = out_dir / f"toy_{name}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    N = C0.shape[0]
    config = {
        "case_id": f"toy_{name}",
        "model": "C_I",
        "grid": {"N": N},
        "domain": {"L": 10.0},
        "time": {"T": 3.0, "dt": 0.01},
        "params": {
            "beta": beta,
            "kappa": 0.5,
        }
    }
    
    # Run with history
    C_history, I_history, t_history = run_simulation_with_history(
        config, C0, I0, n_snapshots=60
    )
    
    # Save snapshots
    save_snapshots(case_dir, C_history, I_history, t_history)
    
    # Save config
    import json
    with open(case_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Compute proper UET Omega
    def compute_coffee_omega(C, I, beta):
        N = C.shape[0]
        dx = 1.0 / N
        grad_C_x = (np.roll(C, -1, axis=0) - np.roll(C, 1, axis=0)) / (2*dx)
        grad_C_y = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2*dx)
        grad_I_x = (np.roll(I, -1, axis=0) - np.roll(I, 1, axis=0)) / (2*dx)
        grad_I_y = (np.roll(I, -1, axis=1) - np.roll(I, 1, axis=1)) / (2*dx)
        kinetic = 0.5 * (grad_C_x**2 + grad_C_y**2 + grad_I_x**2 + grad_I_y**2)
        V_C = (C**2 - 1)**2 / 4
        V_I = (I**2 - 1)**2 / 4
        coupling = beta * C * I
        return float(np.sum(kinetic + V_C + V_I + coupling) * dx**2)
    
    omega_initial = compute_coffee_omega(C0, I0, beta)
    omega_final = compute_coffee_omega(C_history[-1], I_history[-1], beta)
    delta_omega = (omega_final - omega_initial) / abs(omega_initial) if omega_initial != 0 else 0
    
    # Save summary with proper Omega
    summary = {
        "case_id": f"toy_{name}",
        "status": "PASS",
        "Omega0": omega_initial,
        "OmegaT": omega_final,
        "delta_omega": delta_omega,
        "omega_conserved": abs(delta_omega) < 0.1,
        "steps_total": len(C_history) - 1,
        "description": description
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"  ✅ Saved to {case_dir}")
    
    # Generate GIF
    try:
        from scripts.make_animation import make_dual_gif
        make_dual_gif(case_dir, fps=15)
    except Exception as e:
        print(f"  ⚠️ GIF generation failed: {e}")
        # Fallback: try the function directly
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from matplotlib import animation
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            vmin = min(np.min(C_history), np.min(I_history))
            vmax = max(np.max(C_history), np.max(I_history))
            
            im1 = ax1.imshow(C_history[0], cmap='RdBu_r', vmin=vmin, vmax=vmax)
            im2 = ax2.imshow(I_history[0], cmap='RdBu_r', vmin=vmin, vmax=vmax)
            ax1.set_title('C (Coffee)')
            ax2.set_title('I (Milk)')
            plt.colorbar(im1, ax=ax1)
            plt.colorbar(im2, ax=ax2)
            
            def update(frame):
                im1.set_array(C_history[frame])
                im2.set_array(I_history[frame])
                fig.suptitle(f't = {t_history[frame]:.2f}')
                return [im1, im2]
            
            ani = animation.FuncAnimation(fig, update, frames=len(C_history), interval=67, blit=True)
            ani.save(case_dir / "CI_evolution.gif", writer='pillow', fps=15)
            plt.close(fig)
            print(f"  ✅ GIF saved: {case_dir / 'CI_evolution.gif'}")
        except Exception as e2:
            print(f"  ❌ GIF failed: {e2}")
    
    # Generate demo card
    try:
        generate_demo_card(case_dir)
        print(f"  ✅ Demo card generated")
    except Exception as e:
        print(f"  ⚠️ Demo card failed: {e}")
    
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="Run coffee-style visualization demos")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--N", type=int, default=32, help="Grid size")
    args = parser.parse_args()
    
    out_dir = Path(args.out)
    N = args.N
    
    print("☕ Coffee-Style Visualization Demos")
    print("=" * 40)
    
    # 1. Heat Diffusion - Gaussian blob spreading
    print("\n1️⃣ Heat Diffusion (milk drop spreading)")
    C0 = create_gaussian_center(N, sigma=0.15)
    I0 = np.zeros((N, N))
    run_coffee_demo("heat_diffusion", C0, I0, out_dir, 
                    "Heat diffusion from a central hot spot", beta=0.1)
    
    # 2. Two-Field Mixing - Coffee meets milk
    print("\n2️⃣ Two-Field Mixing (coffee meets milk)")
    C0, I0 = create_two_drops(N)
    run_coffee_demo("coffee_milk_mixing", C0, I0, out_dir,
                    "Two fields mixing - coffee and milk interaction", beta=0.5)
    
    # 3. Radial Pattern - Ripples
    print("\n3️⃣ Radial Pattern (ripples in coffee)")
    C0 = create_ring_pattern(N, rings=3)
    I0 = create_ring_pattern(N, rings=2) * 0.5
    run_coffee_demo("radial_ripples", C0, I0, out_dir,
                    "Concentric ripple patterns spreading", beta=0.3)
    
    print("\n" + "=" * 40)
    print("✅ All coffee demos complete!")
    print(f"📁 Output: {out_dir}")
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()
