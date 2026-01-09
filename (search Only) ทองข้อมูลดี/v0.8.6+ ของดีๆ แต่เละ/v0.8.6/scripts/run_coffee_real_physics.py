"""
Enhanced Coffee Brewing Simulation with REAL Physics Parameters

Real-world values:
- Coffee temperature: 92-96°C (brewing), mapped to 0.8-1.0
- Milk temperature: 4-8°C (refrigerated), mapped to 0.0-0.1
- Diffusion coefficient: D ≈ 1×10⁻⁹ m²/s (milk in water)
- Thermal diffusivity: α ≈ 1.4×10⁻⁷ m²/s (water)
- Density: ρ_coffee ≈ 1000 kg/m³, ρ_milk ≈ 1030 kg/m³
- Viscosity: μ ≈ 10⁻³ Pa·s (water at 90°C)
- Gravity: g = 9.81 m/s²

Scaling:
- Length scale: L = 0.1 m (10 cm cup diameter)
- Time scale: t = 10 s (typical mixing time)
- Velocity scale: v = L/t = 0.01 m/s

Dimensionless numbers:
- Reynolds: Re = ρvL/μ ≈ 10 (laminar flow)
- Péclet (mass): Pe_m = vL/D ≈ 10⁶ (convection >> diffusion)
- Péclet (heat): Pe_h = vL/α ≈ 700 (convection >> conduction)
- Rayleigh: Ra = gβΔTL³/(να) ≈ 10⁵ (buoyancy-driven)

Usage:
    python scripts/run_coffee_real_physics.py --scenario realistic_pour
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


# REAL PHYSICS PARAMETERS
REAL_PARAMS = {
    # Temperatures (°C)
    "T_coffee": 95.0,      # Hot coffee
    "T_milk": 5.0,         # Cold milk from fridge
    "T_ambient": 20.0,     # Room temperature
    
    # Diffusion (m²/s)
    "D_milk": 1e-9,        # Milk in water
    "alpha_thermal": 1.4e-7,  # Thermal diffusivity of water
    
    # Densities (kg/m³)
    "rho_coffee": 1000.0,
    "rho_milk": 1030.0,    # Milk slightly denser
    
    # Viscosity (Pa·s)
    "mu": 1e-3,            # Water at 90°C
    
    # Gravity
    "g": 9.81,             # m/s²
    
    # Geometry
    "L": 0.1,              # Cup diameter (m)
    "H": 0.12,             # Cup height (m)
    
    # Time
    "t_mix": 30.0,         # Typical mixing time (s)
}


def scale_to_dimensionless(real_params: dict) -> dict:
    """
    Convert real physics parameters to dimensionless UET parameters.
    
    Scaling:
    - Length: L_ref = cup diameter
    - Time: t_ref = mixing time
    - Temperature: T_ref = ΔT = T_coffee - T_milk
    """
    L = real_params["L"]
    t_ref = real_params["t_mix"]
    v_ref = L / t_ref
    T_ref = real_params["T_coffee"] - real_params["T_milk"]
    
    # Dimensionless diffusion coefficients
    kappa_C = real_params["D_milk"] * t_ref / L**2
    kappa_T = real_params["alpha_thermal"] * t_ref / L**2
    
    # Dimensionless buoyancy (Rayleigh number contribution)
    beta = 2e-4  # Thermal expansion coefficient (1/K)
    Ra = (real_params["g"] * beta * T_ref * L**3) / \
         (real_params["mu"] / real_params["rho_coffee"] * real_params["alpha_thermal"])
    buoyancy = Ra * kappa_T / (L/t_ref)  # Simplified
    
    # Dimensionless viscosity (Reynolds number)
    Re = real_params["rho_coffee"] * v_ref * L / real_params["mu"]
    viscosity = 1.0 / Re
    
    # Density ratio
    density_ratio = real_params["rho_milk"] / real_params["rho_coffee"]
    
    return {
        "kappa_C": float(kappa_C),
        "kappa_T": float(kappa_T),
        "buoyancy": float(min(buoyancy, 1.0)),  # Cap at 1.0 for stability
        "viscosity": float(viscosity),
        "density_ratio": float(density_ratio),
        "Re": float(Re),
        "Ra": float(Ra),
    }


def create_realistic_coffee_initial(N: int) -> tuple:
    """
    Create realistic initial conditions for coffee brewing.
    
    Scenario: Milk poured from top into hot coffee
    """
    C = np.zeros((N, N, N))  # Milk concentration
    T = np.ones((N, N, N))   # Temperature (normalized: 1=hot, 0=cold)
    vx = np.zeros((N, N, N))
    vy = np.zeros((N, N, N))
    vz = np.zeros((N, N, N))
    
    # Create cylindrical cup
    x = np.linspace(-1, 1, N)
    X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
    R = np.sqrt(X**2 + Y**2)
    
    # Coffee: hot, fills most of cup
    coffee_region = (R < 0.8) & (Z < 0.7)
    T[coffee_region] = 1.0  # Hot coffee (95°C)
    
    # Milk: cold, poured from top center
    pour_region = (R < 0.15) & (Z > 0.6)
    C[pour_region] = 1.0    # Pure milk
    T[pour_region] = 0.0    # Cold milk (5°C)
    vz[pour_region] = -0.3  # Downward pour velocity
    
    return C, T, vx, vy, vz


def run_realistic_coffee_simulation(C0, T0, vx0, vy0, vz0, params: dict, 
                                    T_time: float = 30.0, dt: float = 0.05,
                                    n_snapshots: int = 60):
    """
    Run coffee simulation with REAL physics parameters.
    """
    N = C0.shape[0]
    L = REAL_PARAMS["L"]
    
    n_steps = int(T_time / dt)
    snapshot_every = max(1, n_steps // n_snapshots)
    
    C = C0.copy()
    T = T0.copy()
    vx, vy, vz = vx0.copy(), vy0.copy(), vz0.copy()
    
    # Extract dimensionless parameters
    kappa_C = params["kappa_C"]
    kappa_T = params["kappa_T"]
    buoyancy = params["buoyancy"]
    viscosity = params["viscosity"]
    density_ratio = params["density_ratio"]
    
    # Histories
    C_history = [C.copy()]
    T_history = [T.copy()]
    t_history = [0.0]
    mixing_index = [float(np.std(C))]
    avg_temp = [float(np.mean(T))]
    
    dx = 2.0 / N  # Normalized domain [-1, 1]
    
    print(f"  Running REALISTIC coffee simulation:")
    print(f"    Grid: {N}³, Steps: {n_steps}, dt: {dt}")
    print(f"    Real time: {T_time:.1f}s")
    print(f"    κ_C: {kappa_C:.2e}, κ_T: {kappa_T:.2e}")
    print(f"    Buoyancy: {buoyancy:.3f}, Re: {params['Re']:.1f}, Ra: {params['Ra']:.1e}")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # 3D operators
        def laplacian_3d(f):
            return (
                np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
                np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) +
                np.roll(f, 1, axis=2) + np.roll(f, -1, axis=2) - 6*f
            ) / dx**2
        
        def grad_x(f):
            return (np.roll(f, -1, axis=0) - np.roll(f, 1, axis=0)) / (2*dx)
        
        def grad_y(f):
            return (np.roll(f, -1, axis=1) - np.roll(f, 1, axis=1)) / (2*dx)
        
        def grad_z(f):
            return (np.roll(f, -1, axis=2) - np.roll(f, 1, axis=2)) / (2*dx)
        
        def convection(f, vx, vy, vz):
            return vx * grad_x(f) + vy * grad_y(f) + vz * grad_z(f)
        
        # Temperature evolution: ∂T/∂t = α∇²T - v·∇T
        dT = kappa_T * laplacian_3d(T) - convection(T, vx, vy, vz)
        
        # Concentration evolution: ∂C/∂t = D∇²C - v·∇C
        dC = kappa_C * laplacian_3d(C) - convection(C, vx, vy, vz)
        
        # Buoyancy force (Boussinesq approximation)
        # Hot rises: +T contribution
        # Milk (denser) sinks: -C contribution
        buoyancy_force = buoyancy * (T - 0.5) - 0.1 * (density_ratio - 1.0) * C
        
        # Velocity evolution (simplified Navier-Stokes)
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
        
        # Damping (friction)
        vx *= 0.98
        vy *= 0.98
        vz *= 0.98
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            T_history.append(T.copy())
            t_history.append(t)
            mixing_index.append(float(np.std(C)))
            avg_temp.append(float(np.mean(T)))
            
            if step % (n_steps // 5) == 0:
                print(f"    t={t:.1f}s: mixing={mixing_index[-1]:.3f}, T_avg={avg_temp[-1]:.3f}")
    
    return {
        "C": C_history,
        "T": T_history,
        "t": t_history,
        "mixing_index": mixing_index,
        "avg_temp": avg_temp,
    }


def make_combined_animation(case_dir: Path, history: dict, params: dict, fps: int = 12):
    """Create COMBINED animation with ALL visualizations in one GIF."""
    from mpl_toolkits.mplot3d import Axes3D
    
    C_history = history["C"]
    T_history = history["T"]
    t_history = history["t"]
    
    n_frames = len(C_history)
    N = C_history[0].shape[0]
    
    # Real temperature scale
    T_min = REAL_PARAMS["T_milk"]
    T_max = REAL_PARAMS["T_coffee"]
    
    # Meshgrid for 3D
    x = np.arange(N)
    y = np.arange(N)
    X, Y = np.meshgrid(x, y)
    mid = N // 2
    
    fig = plt.figure(figsize=(20, 10))
    
    def update(frame):
        fig.clear()
        
        C = C_history[frame]
        T = T_history[frame]
        t = t_history[frame]
        T_real = T_min + T * (T_max - T_min)
        
        # Slices
        C_slice = C[:, :, mid]
        T_slice = T[:, :, mid]
        diff = C_slice - T_slice
        
        # Row 1: Temperature/Concentration heatmaps
        # 1.1 Milk concentration
        ax1 = fig.add_subplot(241)
        im1 = ax1.imshow(C[:, :, mid], cmap='YlOrBr_r', vmin=0, vmax=1, origin='lower')
        ax1.set_title('Milk (XY)', fontsize=10, fontweight='bold')
        plt.colorbar(im1, ax=ax1, shrink=0.7)
        
        # 1.2 Temperature XY
        ax2 = fig.add_subplot(242)
        im2 = ax2.imshow(T_real[:, :, mid], cmap='coolwarm', vmin=T_min, vmax=T_max, origin='lower')
        ax2.set_title('Temp (XY)', fontsize=10, fontweight='bold')
        plt.colorbar(im2, ax=ax2, shrink=0.7, label='C')
        
        # 1.3 Temperature XZ (vertical slice)
        ax3 = fig.add_subplot(243)
        im3 = ax3.imshow(T_real[:, mid, :], cmap='coolwarm', vmin=T_min, vmax=T_max, origin='lower')
        ax3.set_title('Temp (XZ)', fontsize=10, fontweight='bold')
        plt.colorbar(im3, ax=ax3, shrink=0.7)
        
        # 1.4 Metrics
        ax4 = fig.add_subplot(244)
        ax4.plot(t_history[:frame+1], history["mixing_index"][:frame+1], 'b-', lw=2)
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Mixing', color='b')
        ax4.set_xlim(0, t_history[-1])
        ax4.grid(True, alpha=0.3)
        ax4_twin = ax4.twinx()
        T_avg_real = T_min + np.array(history["avg_temp"][:frame+1]) * (T_max - T_min)
        ax4_twin.plot(t_history[:frame+1], T_avg_real, 'r-', lw=2)
        ax4_twin.set_ylabel('Temp', color='r')
        ax4.set_title('Metrics', fontsize=10, fontweight='bold')
        
        # Row 2: Phase Space + 3D Surfaces
        # 2.1 Phase Space
        ax5 = fig.add_subplot(245)
        c_flat = C_slice.flatten()
        t_flat = T_slice.flatten()
        colors = np.sqrt(c_flat**2 + t_flat**2)
        ax5.scatter(c_flat[::4], t_flat[::4], c=colors[::4], s=8, cmap='viridis', alpha=0.6)
        ax5.set_xlim(-0.1, 1.1)
        ax5.set_ylim(-0.1, 1.1)
        ax5.set_xlabel('C (Milk)')
        ax5.set_ylabel('T (Temp)')
        ax5.set_title('Phase Space', fontsize=10, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        ax5.plot([0, 1], [0, 1], 'k--', alpha=0.3)
        
        # 2.2 C Field 3D
        ax6 = fig.add_subplot(246, projection='3d')
        ax6.plot_surface(X, Y, C_slice, cmap='coolwarm', alpha=0.8, edgecolor='none')
        ax6.set_zlim(0, 1)
        ax6.set_title('C Field', fontsize=10, fontweight='bold')
        ax6.view_init(elev=25, azim=45 + frame*3)
        
        # 2.3 C-T diff 3D
        ax7 = fig.add_subplot(247, projection='3d')
        ax7.plot_surface(X, Y, diff, cmap='RdBu_r', alpha=0.8, edgecolor='none')
        ax7.set_zlim(-1, 1)
        ax7.set_title('C - T', fontsize=10, fontweight='bold')
        ax7.view_init(elev=25, azim=45 + frame*3)
        
        # 2.4 Info box
        ax8 = fig.add_subplot(248)
        ax8.axis('off')
        info = f"""REAL PHYSICS
        
Coffee: {REAL_PARAMS['T_coffee']:.0f}C
Milk: {REAL_PARAMS['T_milk']:.0f}C
Re = {params['Re']:.0f}
Ra = {params['Ra']:.1e}

t = {t:.1f}s
mixing = {history['mixing_index'][frame]:.3f}"""
        ax8.text(0.1, 0.5, info, fontsize=11, family='monospace',
                verticalalignment='center', transform=ax8.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        fig.suptitle(f'REALISTIC Coffee Brewing | t = {t:.1f}s / {t_history[-1]:.1f}s',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "combined_animation.gif"
    print(f"  Saving COMBINED animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  Saved: {output_path}")
    return output_path


def make_scatter_animation(case_dir: Path, history: dict, fps: int = 15):
    """Create scatter animation with Phase Space + 3D surfaces like Coffee Milk Mixing."""
    from mpl_toolkits.mplot3d import Axes3D
    
    C_history = history["C"]
    T_history = history["T"]
    t_history = history["t"]
    
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
        ax2.view_init(elev=25, azim=45 + frame*2)
        
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
        
        fig.suptitle(f'toy_coffee_real_physics | t = {t:.3f}', fontsize=12, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "scatter_animation.gif"
    print(f"  Saving scatter animation with 3D surfaces...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  Saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Realistic coffee brewing with real physics")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--N", type=int, default=32, help="Grid size")
    parser.add_argument("--T", type=float, default=30.0, help="Simulation time (seconds)")
    
    args = parser.parse_args()
    
    print("REALISTIC Coffee Brewing Simulation")
    print("=" * 60)
    print("Real Physics Parameters:")
    print(f"  Coffee: {REAL_PARAMS['T_coffee']}C")
    print(f"  Milk: {REAL_PARAMS['T_milk']}C")
    print(f"  Diffusion: {REAL_PARAMS['D_milk']:.2e} m2/s")
    print(f"  Cup size: {REAL_PARAMS['L']*100:.1f} cm diameter")
    print("=" * 60)
    
    # Scale to dimensionless
    params = scale_to_dimensionless(REAL_PARAMS)
    print("\nDimensionless Parameters:")
    for k, v in params.items():
        print(f"  {k}: {v:.3e}")
    print()
    
    # Create case directory
    case_dir = Path(args.out) / "toy_coffee_real_physics"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Initial conditions
    C0, T0, vx0, vy0, vz0 = create_realistic_coffee_initial(args.N)
    
    # Run simulation
    history = run_realistic_coffee_simulation(C0, T0, vx0, vy0, vz0, params, 
                                             T_time=args.T, dt=0.05)
    
    # Save config
    config = {
        "case_id": "toy_coffee_real_physics",
        "model": "realistic_brewing",
        "description": "Coffee brewing with REAL physics parameters",
        "real_params": REAL_PARAMS,
        "dimensionless_params": params,
        "grid": {"N": args.N, "dims": 3},
        "time": {"T": args.T, "dt": 0.05},
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Save summary
    summary = {
        "case_id": "toy_coffee_real_physics",
        "status": "PASS",
        "final_mixing": float(history["mixing_index"][-1]),
        "final_temp": float(history["avg_temp"][-1]),
        "description": "Realistic coffee brewing with real temperature, diffusion, and buoyancy",
        "Omega0": float(history["mixing_index"][0]),
        "OmegaT": float(history["mixing_index"][-1]),
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create visualizations
    make_combined_animation(case_dir, history, params)  # ALL-IN-ONE mega animation
    make_scatter_animation(case_dir, history)  # Scatter for gallery button
    
    # Copy combined as main.gif for gallery detection
    import shutil
    shutil.copy(case_dir / "combined_animation.gif", case_dir / "main.gif")
    
    print("\n" + "=" * 60)
    print("Realistic Coffee Demo Complete!")
    print(f"   Saved to: {case_dir}")
    print("\nVisualizations:")
    print("  - combined_animation.gif (ALL-IN-ONE: heatmaps + 3D + phase space)")
    print("  - scatter_animation.gif (Phase Space + 3D surfaces)")
    print("  - main.gif (gallery thumbnail)")
    print("\nPhysics Included:")
    print("  - Real temperatures (95C coffee, 5C milk)")
    print("  - Real diffusion coefficient (1e-9 m2/s)")
    print("  - Buoyancy (hot rises, cold sinks)")
    print("  - Density effects (milk denser)")
    print("  - Reynolds & Rayleigh numbers")


if __name__ == "__main__":
    main()

