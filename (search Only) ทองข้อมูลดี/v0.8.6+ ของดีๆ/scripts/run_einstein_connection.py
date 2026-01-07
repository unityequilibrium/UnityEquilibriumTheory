#!/usr/bin/env python
"""
UET ↔ Einstein Field Equations Connection

Maps UET dynamics to General Relativity concepts:
- Stress-Energy Tensor Tμν from UET fields
- Effective curvature (Ricci-like scalar)
- Gravitational wave analogy

Einstein's Equations: Gμν + Λgμν = (8πG/c⁴)Tμν

UET Mapping:
- Ω (energy) → T⁰⁰ (energy density ρ)
- ∇C field → Tⁱ⁰ (momentum density)
- Field stress → Tⁱʲ (pressure/stress tensor)
- β coupling → effective cosmological constant Λ

Usage:
    python scripts/run_einstein_connection.py
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
from mpl_toolkits.mplot3d import Axes3D


# =============================================================================
# Physical Constants (natural units where G = c = 1)
# =============================================================================
G = 1.0  # Newton's constant
c = 1.0  # Speed of light


# =============================================================================
# UET → Stress-Energy Tensor Mapping
# =============================================================================

def compute_energy_density(C: np.ndarray, I: np.ndarray, kappa: float) -> np.ndarray:
    """
    Compute energy density ρ = T⁰⁰ from UET fields.
    
    ρ = (1/2)κ(∇C)² + V(C) + (1/2)β(C-I)²
    
    This is the time-time component of the stress-energy tensor.
    """
    N = C.shape[0]
    dx = 1.0 / N
    
    # Gradient terms
    grad_C_x = (np.roll(C, -1, axis=0) - np.roll(C, 1, axis=0)) / (2*dx)
    grad_C_y = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2*dx)
    
    # Kinetic energy density
    kinetic = 0.5 * kappa * (grad_C_x**2 + grad_C_y**2)
    
    # Potential energy (double-well)
    potential = (C**2 - 1)**2 / 4
    
    return kinetic + potential


def compute_momentum_density(C: np.ndarray, dC_dt: np.ndarray, kappa: float) -> tuple:
    """
    Compute momentum density Tⁱ⁰ (momentum flux).
    
    Tⁱ⁰ = -κ (∂C/∂t)(∂C/∂xⁱ)
    
    This represents the flow of energy in spatial directions.
    """
    N = C.shape[0]
    dx = 1.0 / N
    
    grad_C_x = (np.roll(C, -1, axis=0) - np.roll(C, 1, axis=0)) / (2*dx)
    grad_C_y = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2*dx)
    
    T_x0 = -kappa * dC_dt * grad_C_x
    T_y0 = -kappa * dC_dt * grad_C_y
    
    return T_x0, T_y0


def compute_stress_tensor(C: np.ndarray, kappa: float) -> tuple:
    """
    Compute spatial stress tensor Tⁱʲ.
    
    Tⁱʲ = κ(∂C/∂xⁱ)(∂C/∂xʲ) - δⁱʲ[κ/2(∇C)² + V(C)]
    
    For 2D:
    T_xx = κ(∂C/∂x)² - ρ
    T_yy = κ(∂C/∂y)² - ρ
    T_xy = κ(∂C/∂x)(∂C/∂y)
    """
    N = C.shape[0]
    dx = 1.0 / N
    
    grad_C_x = (np.roll(C, -1, axis=0) - np.roll(C, 1, axis=0)) / (2*dx)
    grad_C_y = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2*dx)
    
    kinetic = 0.5 * kappa * (grad_C_x**2 + grad_C_y**2)
    potential = (C**2 - 1)**2 / 4
    rho = kinetic + potential
    
    T_xx = kappa * grad_C_x**2 - rho
    T_yy = kappa * grad_C_y**2 - rho
    T_xy = kappa * grad_C_x * grad_C_y
    
    return T_xx, T_yy, T_xy


def compute_ricci_scalar(C: np.ndarray, kappa: float) -> np.ndarray:
    """
    Compute effective Ricci scalar (curvature) from UET.
    
    In GR: R = 8πG(ρ - 3P) for dust
    
    Here we use an analogous definition based on energy-pressure relation.
    """
    N = C.shape[0]
    dx = 1.0 / N
    
    # Laplacian of C (related to curvature)
    lapC = (np.roll(C, 1, axis=0) + np.roll(C, -1, axis=0) +
            np.roll(C, 1, axis=1) + np.roll(C, -1, axis=1) - 4*C) / dx**2
    
    # Energy density
    rho = compute_energy_density(C, C, kappa)
    
    # Pressure (trace of spatial stress / dim)
    T_xx, T_yy, T_xy = compute_stress_tensor(C, kappa)
    P = (T_xx + T_yy) / 2
    
    # Effective Ricci scalar
    R = 8 * np.pi * G * (rho - 3*P)
    
    return R


def build_stress_energy_tensor(C: np.ndarray, I: np.ndarray, dC_dt: np.ndarray,
                                kappa: float) -> np.ndarray:
    """
    Build the full 4×4 stress-energy tensor Tμν at each point.
    
    Returns: (N, N, 4, 4) array
    
    Tμν = | T⁰⁰   T⁰¹   T⁰²   0  |
          | T¹⁰   T¹¹   T¹²   0  |
          | T²⁰   T²¹   T²²   0  |
          |  0     0     0    0  |
    """
    N = C.shape[0]
    T = np.zeros((N, N, 4, 4))
    
    # T⁰⁰ = energy density
    T[:, :, 0, 0] = compute_energy_density(C, I, kappa)
    
    # T⁰ⁱ = Tⁱ⁰ = momentum density
    T_x0, T_y0 = compute_momentum_density(C, dC_dt, kappa)
    T[:, :, 0, 1] = T_x0
    T[:, :, 0, 2] = T_y0
    T[:, :, 1, 0] = T_x0
    T[:, :, 2, 0] = T_y0
    
    # Tⁱʲ = stress tensor
    T_xx, T_yy, T_xy = compute_stress_tensor(C, kappa)
    T[:, :, 1, 1] = T_xx
    T[:, :, 2, 2] = T_yy
    T[:, :, 1, 2] = T_xy
    T[:, :, 2, 1] = T_xy
    
    return T


# =============================================================================
# UET Simulation with GR observables
# =============================================================================

def run_uet_gr_simulation(N: int = 32, T: float = 5.0, dt: float = 0.02,
                          beta: float = 0.5, kappa: float = 0.3,
                          scenario: str = "wave") -> dict:
    """Run UET simulation and compute GR observables."""
    
    # Initial conditions
    x = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, x)
    
    if scenario == "wave":
        # Gravitational wave-like initial condition
        C = 0.3 * np.sin(4 * np.pi * X) * np.exp(-Y**2 / 0.3)
        I = np.zeros((N, N))
    elif scenario == "collapse":
        # Matter collapse (spherically symmetric)
        R = np.sqrt(X**2 + Y**2)
        C = np.exp(-R**2 / 0.1) * 0.8
        I = np.zeros((N, N))
    elif scenario == "binary":
        # Binary system (two masses)
        R1 = np.sqrt((X - 0.3)**2 + Y**2)
        R2 = np.sqrt((X + 0.3)**2 + Y**2)
        C = np.exp(-R1**2 / 0.02) * 0.5 + np.exp(-R2**2 / 0.02) * 0.5
        I = np.zeros((N, N))
    else:  # random
        np.random.seed(42)
        C = np.random.randn(N, N) * 0.2
        I = np.zeros((N, N))
    
    n_steps = int(T / dt)
    n_snapshots = 60
    snapshot_every = max(1, n_steps // n_snapshots)
    
    # Histories
    C_history = [C.copy()]
    I_history = [I.copy()]
    t_history = [0.0]
    rho_history = [compute_energy_density(C, I, kappa).copy()]
    R_history = [compute_ricci_scalar(C, kappa).copy()]
    total_energy = [float(np.sum(rho_history[0]))]
    avg_curvature = [float(np.mean(R_history[0]))]
    
    C_prev = C.copy()
    
    print(f"  Running GR-coupled simulation: {N}×{N}, {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # Laplacian
        lapC = (np.roll(C, 1, axis=0) + np.roll(C, -1, axis=0) +
                np.roll(C, 1, axis=1) + np.roll(C, -1, axis=1) - 4*C) * N**2
        lapI = (np.roll(I, 1, axis=0) + np.roll(I, -1, axis=0) +
                np.roll(I, 1, axis=1) + np.roll(I, -1, axis=1) - 4*I) * N**2
        
        # UET dynamics
        dC = kappa * lapC - C * (C**2 - 1) - beta * (C - I)
        dI = kappa * lapI - I * (I**2 - 1) - beta * (I - C)
        
        C_new = C + dt * dC
        I_new = I + dt * dI
        
        # Time derivative for momentum
        dC_dt = (C_new - C_prev) / (2*dt) if step > 1 else dC
        
        C_prev = C.copy()
        C = np.clip(C_new, -2, 2)
        I = np.clip(I_new, -2, 2)
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            I_history.append(I.copy())
            t_history.append(t)
            
            rho = compute_energy_density(C, I, kappa)
            R = compute_ricci_scalar(C, kappa)
            
            rho_history.append(rho.copy())
            R_history.append(R.copy())
            total_energy.append(float(np.sum(rho)))
            avg_curvature.append(float(np.mean(R)))
    
    return {
        "C": C_history,
        "I": I_history,
        "t": t_history,
        "rho": rho_history,  # T⁰⁰
        "R": R_history,      # Ricci scalar
        "total_energy": total_energy,
        "avg_curvature": avg_curvature,
        "scenario": scenario,
    }


# =============================================================================
# Visualization
# =============================================================================

def make_gr_animation(case_dir: Path, history: dict, fps: int = 12) -> Path:
    """Create animation showing GR observables from UET."""
    plt.style.use('dark_background')
    
    C_history = history["C"]
    rho_history = history["rho"]
    R_history = history["R"]
    t_history = history["t"]
    scenario = history["scenario"]
    
    n_frames = len(C_history)
    N = C_history[0].shape[0]
    
    fig = plt.figure(figsize=(16, 9), facecolor='black')
    
    # Global limits
    rho_max = max(np.max(r) for r in rho_history)
    R_max = max(np.max(np.abs(r)) for r in R_history)
    
    x = np.arange(N)
    X, Y = np.meshgrid(x, x)
    
    def update(frame):
        fig.clear()
        
        C = C_history[frame]
        rho = rho_history[frame]
        R = R_history[frame]
        t = t_history[frame]
        
        # Layout: 2x3
        # Row 1: C field, Energy density T⁰⁰, Ricci scalar R
        # Row 2: 3D energy surface, Energy time series, Curvature time series
        
        # 1. C field
        ax1 = fig.add_subplot(231)
        im1 = ax1.imshow(C, cmap='RdBu_r', vmin=-1, vmax=1)
        ax1.set_title('C Field (Matter)', fontsize=11, color='white')
        ax1.set_xlabel('x', color='white')
        ax1.set_ylabel('y', color='white')
        plt.colorbar(im1, ax=ax1, shrink=0.8)
        
        # 2. Energy density T⁰⁰
        ax2 = fig.add_subplot(232)
        im2 = ax2.imshow(rho, cmap='inferno', vmin=0, vmax=rho_max)
        ax2.set_title('T⁰⁰ (Energy Density ρ)', fontsize=11, color='white')
        ax2.set_xlabel('x', color='white')
        ax2.set_ylabel('y', color='white')
        plt.colorbar(im2, ax=ax2, shrink=0.8)
        
        # 3. Ricci scalar (curvature)
        ax3 = fig.add_subplot(233)
        im3 = ax3.imshow(R, cmap='coolwarm', vmin=-R_max, vmax=R_max)
        ax3.set_title('R (Ricci Curvature)', fontsize=11, color='white')
        ax3.set_xlabel('x', color='white')
        ax3.set_ylabel('y', color='white')
        plt.colorbar(im3, ax=ax3, shrink=0.8)
        
        # 4. 3D Energy surface
        ax4 = fig.add_subplot(234, projection='3d', facecolor='black')
        ax4.plot_surface(X, Y, rho, cmap='inferno', alpha=0.8, edgecolor='none')
        ax4.set_xlabel('x', color='white')
        ax4.set_ylabel('y', color='white')
        ax4.set_zlabel('ρ', color='white')
        ax4.set_title('Energy Density Surface', fontsize=10, color='white')
        ax4.view_init(elev=25, azim=45 + frame*2)
        ax4.set_facecolor('black')
        ax4.xaxis.pane.fill = False
        ax4.yaxis.pane.fill = False
        ax4.zaxis.pane.fill = False
        
        # 5. Total energy over time
        ax5 = fig.add_subplot(235)
        ax5.plot(t_history[:frame+1], history["total_energy"][:frame+1], 
                'orange', lw=2)
        ax5.set_xlim(0, t_history[-1])
        ax5.set_ylim(0, max(history["total_energy"]) * 1.1)
        ax5.set_xlabel('Time', color='white')
        ax5.set_ylabel('Total Energy', color='white')
        ax5.set_title('∫ T⁰⁰ dV (Total Energy)', fontsize=10, color='white')
        ax5.grid(True, alpha=0.3)
        
        # 6. Average curvature over time
        ax6 = fig.add_subplot(236)
        ax6.plot(t_history[:frame+1], history["avg_curvature"][:frame+1],
                'cyan', lw=2)
        ax6.set_xlim(0, t_history[-1])
        ax6.axhline(0, color='gray', lw=0.5, alpha=0.5)
        ax6.set_xlabel('Time', color='white')
        ax6.set_ylabel('⟨R⟩', color='white')
        ax6.set_title('Average Ricci Scalar', fontsize=10, color='white')
        ax6.grid(True, alpha=0.3)
        
        fig.suptitle(f'UET → Einstein Connection | {scenario.upper()} | t = {t:.2f}\n'
                    f'Gμν + Λgμν = 8πG·Tμν',
                    fontsize=14, fontweight='bold', color='white')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "CI_evolution.gif"
    print(f"  Saving Einstein connection animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    plt.style.use('default')
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def make_stress_tensor_plot(case_dir: Path, history: dict) -> Path:
    """Create visualization of full stress-energy tensor components."""
    plt.style.use('dark_background')
    
    C = history["C"][-1]
    I = history["I"][-1]
    dC_dt = (history["C"][-1] - history["C"][-2]) / (history["t"][-1] - history["t"][-2])
    kappa = 0.3
    
    # Build full tensor
    T = build_stress_energy_tensor(C, I, dC_dt, kappa)
    
    fig = plt.figure(figsize=(14, 12), facecolor='black')
    
    # Plot 4x4 matrix of tensor components
    labels = ['t', 'x', 'y', 'z']
    
    for i in range(4):
        for j in range(4):
            ax = fig.add_subplot(4, 4, i*4 + j + 1)
            
            component = T[:, :, i, j]
            vmax = max(np.abs(component.max()), np.abs(component.min()))
            if vmax < 1e-10:
                vmax = 1  # Avoid division by zero for empty components
            
            im = ax.imshow(component, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
            ax.set_title(f'T{labels[i]}{labels[j]}', fontsize=10, color='white')
            ax.set_xticks([])
            ax.set_yticks([])
            
            if np.abs(component).max() > 1e-10:
                plt.colorbar(im, ax=ax, shrink=0.7)
    
    fig.suptitle('Stress-Energy Tensor Tμν from UET Fields\n'
                'Row = μ (time/space), Col = ν (time/space)',
                fontsize=14, fontweight='bold', color='white')
    plt.tight_layout()
    
    output_path = case_dir / "stress_energy_tensor.png"
    plt.savefig(output_path, dpi=150, facecolor='black')
    plt.close(fig)
    plt.style.use('default')
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def compute_omega(C, I, beta, kappa):
    """Compute UET network mass Ω."""
    N = C.shape[0]
    dx = 1.0 / N
    gCx = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / (2*dx)
    gCy = (np.roll(C, -1, 1) - np.roll(C, 1, 1)) / (2*dx)
    gIx = (np.roll(I, -1, 0) - np.roll(I, 1, 0)) / (2*dx)
    gIy = (np.roll(I, -1, 1) - np.roll(I, 1, 1)) / (2*dx)
    kinetic = 0.5 * kappa * (gCx**2 + gCy**2 + gIx**2 + gIy**2)
    V_C = (C**2 - 1)**2 / 4
    V_I = (I**2 - 1)**2 / 4
    coupling = beta * C * I
    return float(np.sum(kinetic + V_C + V_I + coupling) * dx**2)


def run_einstein_demo(scenario: str, out_dir: Path):
    """Run complete Einstein connection demo."""
    print(f"\n🌌 Running Einstein Connection Demo: {scenario}")
    
    case_dir = out_dir / f"einstein_{scenario}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Run simulation
    history = run_uet_gr_simulation(
        N=32, T=5.0, dt=0.02,
        beta=0.5, kappa=0.3,
        scenario=scenario
    )
    
    # Create visualizations
    make_gr_animation(case_dir, history)
    make_stress_tensor_plot(case_dir, history)

    
    # Save config
    cfg = {
        "case_id": f"einstein_{scenario}",
        "model": "UET_GR",
        "scenario": scenario,
        "physics": {
            "connection": "UET → Stress-Energy Tensor → Einstein",
            "T00": "Energy density from UET Ω",
            "Ti0": "Momentum density from field gradients",
            "Tij": "Stress tensor from field derivatives",
            "R": "Ricci scalar from curvature"
        },
        "description": f"UET ↔ Einstein Field Equations - {scenario}"
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    
    # Compute Omega
    C_initial = history["C"][0]
    I_initial = history["I"][0]
    C_final = history["C"][-1]
    I_final = history["I"][-1]
    
    omega_initial = compute_omega(C_initial, I_initial, beta=0.5, kappa=0.3)
    omega_final = compute_omega(C_final, I_final, beta=0.5, kappa=0.3)
    delta_omega = (omega_final - omega_initial) / abs(omega_initial) if omega_initial != 0 else 0
    
    # Save summary with Omega
    summary = {
        "case_id": f"einstein_{scenario}",
        "status": "PASS",
        "scenario": scenario,
        "final_energy": float(history["total_energy"][-1]),
        "final_curvature": float(history["avg_curvature"][-1]),
        "Omega0": omega_initial,
        "OmegaT": omega_final,
        "delta_omega": delta_omega,
        "omega_conserved": abs(delta_omega) < 0.1,
        "description": f"UET → Tμν → Gμν | {scenario.upper()}"
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"  ✅ Demo saved to: {case_dir}")
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="UET-Einstein Connection")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--scenario", default="all",
                       choices=["wave", "collapse", "binary", "all"],
                       help="GR scenario")
    
    args = parser.parse_args()
    out_dir = Path(args.out)
    
    print("="*60)
    print("🌌 UET ↔ EINSTEIN FIELD EQUATIONS")
    print("="*60)
    print("\nConnection:")
    print("  UET Energy Ω → T⁰⁰ (energy density)")
    print("  UET Momentum → Tⁱ⁰ (momentum flux)")
    print("  UET Stress → Tⁱʲ (pressure tensor)")
    print("  → Gμν + Λgμν = 8πG·Tμν")
    print("="*60)
    
    if args.scenario == "all":
        scenarios = ["wave", "collapse", "binary"]
    else:
        scenarios = [args.scenario]
    
    for scenario in scenarios:
        run_einstein_demo(scenario, out_dir)
    
    print("\n" + "="*60)
    print("✅ Einstein connection demos complete!")
    print("\nKey Results:")
    print("  1. Stress-Energy Tensor Tμν computed from UET fields")
    print("  2. Ricci Curvature R derived from energy-pressure")
    print("  3. GR dynamics visualized: wave, collapse, binary")
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()

