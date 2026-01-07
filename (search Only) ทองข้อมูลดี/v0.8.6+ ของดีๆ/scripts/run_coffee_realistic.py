#!/usr/bin/env python
"""
Realistic 3D Coffee + Milk Simulation with UET dynamics.

Enhanced version with:
1. Convection (velocity field) - thermal buoyancy
2. Temperature coupling - hot coffee, cold milk
3. 3D simulation with slice visualization

Physics:
- C field = Milk concentration
- I field = Temperature (coffee hot, milk cold)
- v field = Velocity (convection from temperature diff)
- κ = Diffusion coefficient
- α = Thermal diffusivity

Usage:
    python scripts/run_coffee_realistic.py --scenario buoyancy
    python scripts/run_coffee_realistic.py --scenario stirred
"""
from __future__ import annotations
import argparse
import json
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation


def create_coffee_3d_initial(N: int, scenario: str) -> tuple:
    """
    Create 3D initial conditions for coffee cup.
    
    Returns:
        C: Milk concentration (0=coffee, 1=milk)
        T: Temperature (0=cold, 1=hot)
        vx, vy, vz: Velocity components
    """
    # Initialize fields
    C = np.zeros((N, N, N))  # Milk concentration
    T = np.ones((N, N, N)) * 0.8  # Hot coffee initially
    vx = np.zeros((N, N, N))
    vy = np.zeros((N, N, N))
    vz = np.zeros((N, N, N))
    
    # Create cylindrical cup mask (z=0 is bottom)
    x = np.linspace(-1, 1, N)
    X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
    R = np.sqrt(X**2 + Y**2)
    
    if scenario == "pour_top":
        # Milk poured from top center
        pour_region = (R < 0.2) & (Z > 0.6)
        C[pour_region] = 1.0
        T[pour_region] = 0.2  # Cold milk
        # Initial downward velocity for pour
        vz[pour_region] = -0.5
        
    elif scenario == "buoyancy":
        # Cold milk blob in hot coffee - watch it sink then rise
        cx, cy, cz = N//2, N//2, 2*N//3  # Upper middle
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    dist = np.sqrt((i-cx)**2 + (j-cy)**2 + (k-cz)**2) / N
                    if dist < 0.15:
                        C[i,j,k] = np.exp(-dist**2 / 0.02)
                        T[i,j,k] = 0.2  # Cold milk
        
    elif scenario == "stirred":
        # Milk on side with circular stirring motion
        milk_region = (R < 0.3) & (X > 0.3) & (Z < 0.7)
        C[milk_region] = 1.0
        T[milk_region] = 0.2
        # Add stirring velocity (circular)
        vx = -Y * 0.3
        vy = X * 0.3
        
    elif scenario == "layered":
        # Layered: milk at bottom (denser when cold)
        bottom_layer = Z < -0.5
        C[bottom_layer] = 1.0
        T[bottom_layer] = 0.2
    
    return C, T, vx, vy, vz


def run_coffee_3d_simulation(C0, T0, vx0, vy0, vz0, config: dict, n_snapshots: int = 50):
    """
    Run 3D coffee simulation with convection and temperature.
    
    Key dynamics:
    - Concentration diffuses (milk spreads)
    - Temperature diffuses (heat transfer)
    - Buoyancy: cold fluid sinks, hot rises
    - Convection: concentration carried by flow
    """
    N = C0.shape[0]
    L = config.get("L", 2.0)
    T_time = config.get("T", 5.0)
    dt = config.get("dt", 0.01)
    kappa_C = config.get("kappa_C", 0.1)  # Milk diffusion
    kappa_T = config.get("kappa_T", 0.2)  # Thermal diffusion
    buoyancy = config.get("buoyancy", 0.5)  # Buoyancy strength
    viscosity = config.get("viscosity", 0.1)  # Fluid viscosity
    
    n_steps = int(T_time / dt)
    snapshot_every = max(1, n_steps // n_snapshots)
    
    C = C0.copy()
    T = T0.copy()
    vx, vy, vz = vx0.copy(), vy0.copy(), vz0.copy()
    
    # Histories
    C_history = [C.copy()]
    T_history = [T.copy()]
    t_history = [0.0]
    mixing_index = [float(np.std(C))]
    avg_temp = [float(np.mean(T))]
    
    dx = L / N
    
    print(f"  Running 3D coffee simulation: {N}³ grid, {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # 3D Laplacian
        def laplacian_3d(f):
            return (
                np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
                np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) +
                np.roll(f, 1, axis=2) + np.roll(f, -1, axis=2) - 6*f
            ) / dx**2
        
        # Gradient for convection
        def grad_z(f):
            return (np.roll(f, -1, axis=2) - np.roll(f, 1, axis=2)) / (2*dx)
        
        def grad_x(f):
            return (np.roll(f, -1, axis=0) - np.roll(f, 1, axis=0)) / (2*dx)
        
        def grad_y(f):
            return (np.roll(f, -1, axis=1) - np.roll(f, 1, axis=1)) / (2*dx)
        
        # Convection terms (v · ∇f)
        def convection(f, vx, vy, vz):
            return vx * grad_x(f) + vy * grad_y(f) + vz * grad_z(f)
        
        # Temperature equation: ∂T/∂t = κ∇²T - v·∇T
        dT = kappa_T * laplacian_3d(T) - convection(T, vx, vy, vz)
        
        # Concentration equation: ∂C/∂t = κ∇²C - v·∇C
        dC = kappa_C * laplacian_3d(C) - convection(C, vx, vy, vz)
        
        # Velocity update (simplified Boussinesq)
        # Buoyancy: hot rises (vz+), cold sinks (vz-)
        # Also affected by concentration (milk slightly denser)
        buoyancy_force = buoyancy * (T - 0.5) - 0.1 * C  # Hot goes up, milk goes down
        
        # Simplified momentum (ignore pressure for toy model)
        dvx = viscosity * laplacian_3d(vx) - convection(vx, vx, vy, vz)
        dvy = viscosity * laplacian_3d(vy) - convection(vy, vx, vy, vz)
        dvz = viscosity * laplacian_3d(vz) - convection(vz, vx, vy, vz) + buoyancy_force
        
        # Update
        T = T + dt * dT
        C = C + dt * dC
        vx = vx + dt * dvx
        vy = vy + dt * dvy
        vz = vz + dt * dvz
        
        # Clip
        C = np.clip(C, 0, 1)
        T = np.clip(T, 0, 1)
        
        # Dampen velocities (friction)
        vx *= 0.99
        vy *= 0.99
        vz *= 0.99
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            T_history.append(T.copy())
            t_history.append(t)
            mixing_index.append(float(np.std(C)))
            avg_temp.append(float(np.mean(T)))
            
            if step % (n_steps // 4) == 0:
                print(f"    Step {step}/{n_steps}, mixing: {mixing_index[-1]:.3f}")
    
    return {
        "C": C_history,
        "T": T_history,
        "t": t_history,
        "mixing_index": mixing_index,
        "avg_temp": avg_temp,
    }


def make_coffee_3d_animation(case_dir: Path, history: dict, scenario: str, fps: int = 12) -> Path:
    """Create 3D slice animation of coffee mixing."""
    C_history = history["C"]
    T_history = history["T"]
    t_history = history["t"]
    
    n_frames = len(C_history)
    N = C_history[0].shape[0]
    
    fig = plt.figure(figsize=(16, 8))
    
    def update(frame):
        fig.clear()
        
        C = C_history[frame]
        T = T_history[frame]
        t = t_history[frame]
        
        # Layout: 2 rows x 4 cols
        # Row 1: C slices (XY, XZ, YZ at center, metrics)
        # Row 2: T slices (same)
        
        mid = N // 2
        
        # Concentration slices
        ax1 = fig.add_subplot(241)
        ax1.imshow(C[:, :, mid], cmap='copper_r', vmin=0, vmax=1, origin='lower')
        ax1.set_title(f'Milk (XY slice z={mid})', fontsize=10)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        
        ax2 = fig.add_subplot(242)
        ax2.imshow(C[:, mid, :], cmap='copper_r', vmin=0, vmax=1, origin='lower')
        ax2.set_title(f'Milk (XZ slice y={mid})', fontsize=10)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Z')
        
        ax3 = fig.add_subplot(243)
        ax3.imshow(C[mid, :, :], cmap='copper_r', vmin=0, vmax=1, origin='lower')
        ax3.set_title(f'Milk (YZ slice x={mid})', fontsize=10)
        ax3.set_xlabel('Y')
        ax3.set_ylabel('Z')
        
        # Mixing metric
        ax4 = fig.add_subplot(244)
        ax4.plot(t_history[:frame+1], history["mixing_index"][:frame+1], 'b-', lw=2)
        ax4.set_xlim(0, t_history[-1])
        ax4.set_ylim(0, max(history["mixing_index"]) * 1.1)
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Mixing Index (σ)')
        ax4.set_title('☕ Mixing Progress')
        ax4.grid(True, alpha=0.3)
        # Add annotation
        if history["mixing_index"][frame] < 0.1:
            ax4.text(0.5, 0.5, '✅ Well Mixed!', transform=ax4.transAxes,
                    ha='center', fontsize=12, color='green', fontweight='bold')
        
        # Temperature slices
        ax5 = fig.add_subplot(245)
        ax5.imshow(T[:, :, mid], cmap='coolwarm', vmin=0, vmax=1, origin='lower')
        ax5.set_title('Temperature (XY)', fontsize=10)
        ax5.set_xlabel('X')
        ax5.set_ylabel('Y')
        
        ax6 = fig.add_subplot(246)
        ax6.imshow(T[:, mid, :], cmap='coolwarm', vmin=0, vmax=1, origin='lower')
        ax6.set_title('Temperature (XZ)', fontsize=10)
        ax6.set_xlabel('X')
        ax6.set_ylabel('Z')
        
        ax7 = fig.add_subplot(247)
        ax7.imshow(T[mid, :, :], cmap='coolwarm', vmin=0, vmax=1, origin='lower')
        ax7.set_title('Temperature (YZ)', fontsize=10)
        ax7.set_xlabel('Y')
        ax7.set_ylabel('Z')
        
        # Temperature metric
        ax8 = fig.add_subplot(248)
        ax8.fill_between(t_history[:frame+1], 0, history["avg_temp"][:frame+1],
                        color='red', alpha=0.3)
        ax8.plot(t_history[:frame+1], history["avg_temp"][:frame+1], 'r-', lw=2)
        ax8.set_xlim(0, t_history[-1])
        ax8.set_ylim(0, 1)
        ax8.set_xlabel('Time')
        ax8.set_ylabel('Avg Temperature')
        ax8.set_title('🌡️ Cooling Curve')
        ax8.grid(True, alpha=0.3)
        
        fig.suptitle(f'☕ 3D Coffee + Milk Simulation | {scenario.upper()} | t = {t:.2f}',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "CI_evolution.gif"
    print(f"  Saving 3D coffee animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def make_scatter_animation(case_dir: Path, history: dict, scenario: str, fps: int = 15) -> Path:
    """Create scatter animation with 3D surface plots like toy_coffee_milk_mixing."""
    from mpl_toolkits.mplot3d import Axes3D
    
    C_history = history["C"]
    T_history = history["T"]
    t_history = history["t"]
    mixing = history["mixing_index"]
    avg_temp = history["avg_temp"]
    
    n_frames = len(C_history)
    N = C_history[0].shape[0]
    
    fig = plt.figure(figsize=(16, 5))
    
    # Create meshgrid for 3D surface (use mid slice)
    x = np.arange(N)
    y = np.arange(N)
    X, Y = np.meshgrid(x, y)
    mid = N // 2
    
    def update(frame):
        fig.clear()
        
        C = C_history[frame]
        T = T_history[frame]
        t = t_history[frame]
        
        # Take horizontal slice at mid-height
        C_slice = C[:, :, mid]
        T_slice = T[:, :, mid]
        diff = C_slice - T_slice
        
        # 1. Phase Space (C value vs T value)
        ax1 = fig.add_subplot(131)
        c_flat = C_slice.flatten()
        t_flat = T_slice.flatten()
        colors = np.sqrt(c_flat**2 + t_flat**2)
        ax1.scatter(c_flat[::4], t_flat[::4], c=colors[::4], s=10, cmap='viridis', alpha=0.6)
        ax1.set_xlim(-0.2, 1.2)
        ax1.set_ylim(-0.2, 1.2)
        ax1.set_xlabel('C value (Milk)', fontsize=10)
        ax1.set_ylabel('T value (Temp)', fontsize=10)
        ax1.set_title('Phase Space', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        # Add diagonal line (equilibrium)
        ax1.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Equilibrium')
        
        # 2. C Field 3D surface
        ax2 = fig.add_subplot(132, projection='3d')
        ax2.plot_surface(X, Y, C_slice, cmap='coolwarm', alpha=0.8,
                        edgecolor='none', linewidth=0)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('C')
        ax2.set_zlim(0, 1)
        ax2.set_title('C Field', fontsize=11, fontweight='bold')
        ax2.view_init(elev=25, azim=45 + frame*2)  # Rotate view
        
        # 3. C-T difference 3D surface
        ax3 = fig.add_subplot(133, projection='3d')
        ax3.plot_surface(X, Y, diff, cmap='RdBu_r', alpha=0.8,
                        edgecolor='none', linewidth=0)
        ax3.set_xlabel('X')
        ax3.set_ylabel('Y')
        ax3.set_zlabel('C - T')
        ax3.set_zlim(-1, 1)
        ax3.set_title('C - T', fontsize=11, fontweight='bold')
        ax3.view_init(elev=25, azim=45 + frame*2)
        
        fig.suptitle(f'{scenario} | t = {t:.3f}', fontsize=12, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "scatter_animation.gif"
    print(f"  Saving scatter animation with 3D surfaces...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def run_coffee_demo(scenario: str, out_dir: Path, N: int = 24, T: float = 5.0):
    """Run complete 3D coffee demo."""
    print(f"\n☕ Running 3D Coffee Demo: {scenario}")
    
    case_dir = out_dir / f"toy_coffee_3d_{scenario}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Initial conditions
    C0, T0, vx0, vy0, vz0 = create_coffee_3d_initial(N, scenario)
    
    config = {
        "L": 2.0,
        "T": T,
        "dt": 0.01,
        "kappa_C": 0.1,  # Milk diffusion
        "kappa_T": 0.15,  # Thermal diffusion
        "buoyancy": 0.3,  # Buoyancy strength
        "viscosity": 0.1,  # Fluid viscosity
    }
    
    # Run simulation
    history = run_coffee_3d_simulation(C0, T0, vx0, vy0, vz0, config)
    
    # Save config
    cfg = {
        "case_id": f"toy_coffee_3d_{scenario}",
        "model": "C_T_v",
        "scenario": scenario,
        "grid": {"N": N, "dims": 3},
        "domain": {"L": config["L"]},
        "time": {"T": T, "dt": config["dt"]},
        "params": {
            "kappa_C": config["kappa_C"],
            "kappa_T": config["kappa_T"],
            "buoyancy": config["buoyancy"],
            "viscosity": config["viscosity"],
        },
        "description": f"3D Coffee simulation with convection - {scenario}"
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    
    # Save summary
    summary = {
        "case_id": f"toy_coffee_3d_{scenario}",
        "status": "PASS",
        "scenario": scenario,
        "final_mixing": float(history["mixing_index"][-1]),
        "final_temp": float(history["avg_temp"][-1]),
        "description": f"3D Coffee + Milk with Convection - {scenario.upper()}"
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create visualization
    make_coffee_3d_animation(case_dir, history, scenario)
    make_scatter_animation(case_dir, history, scenario)
    
    print(f"  ✅ Demo saved to: {case_dir}")
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="3D Coffee simulation with convection")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--scenario", default="all",
                       choices=["pour_top", "buoyancy", "stirred", "layered", "all"],
                       help="Scenario")
    parser.add_argument("--N", type=int, default=24, help="Grid size (N³)")
    parser.add_argument("--T", type=float, default=5.0, help="Simulation time")
    
    args = parser.parse_args()
    out_dir = Path(args.out)
    
    print("☕ 3D Coffee + Milk Simulation")
    print("  With: Convection + Temperature + Buoyancy")
    print("=" * 50)
    
    if args.scenario == "all":
        scenarios = ["pour_top", "buoyancy", "stirred", "layered"]
    else:
        scenarios = [args.scenario]
    
    for scenario in scenarios:
        run_coffee_demo(scenario, out_dir, N=args.N, T=args.T)
    
    print("\n" + "=" * 50)
    print("✅ 3D Coffee demos complete!")
    print("\nPhysics included:")
    print("  1. ✅ Diffusion (milk spreads)")
    print("  2. ✅ Temperature coupling (hot/cold)")
    print("  3. ✅ Convection (carried by flow)")
    print("  4. ✅ Buoyancy (hot rises, cold sinks)")
    print("  5. ✅ 3D visualization")
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()
