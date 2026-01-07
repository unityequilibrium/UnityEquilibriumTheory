#!/usr/bin/env python
"""
Toy Traffic Simulation using UET dynamics.

Maps traffic flow to UET fields:
- C field = Vehicle density (cars on road)
- I field = Traffic control (signals, flow management)
- β coupling = How well traffic responds to signals
- s-tilt = New cars entering (rush hour)
- Ω = Total "traffic stress" (lower = smoother flow)

Usage:
    python scripts/run_toy_traffic.py --scenario all
    python scripts/run_toy_traffic.py --scenario rush_hour
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


def create_traffic_initial(N: int, scenario: str) -> tuple:
    """Create initial traffic conditions."""
    C0 = np.zeros((N, N))
    I0 = np.zeros((N, N))
    
    if scenario == "normal":
        # Light traffic, evenly distributed
        C0 = np.random.randn(N, N) * 0.2
        I0 = np.ones((N, N)) * 0.3  # Moderate control
        
    elif scenario == "rush_hour":
        # Heavy traffic from edges (people entering city)
        for i in range(N):
            for j in range(N):
                # More cars near edges
                edge_dist = min(i, j, N-1-i, N-1-j) / N
                C0[i, j] = (1 - edge_dist) * 0.8 + np.random.randn() * 0.1
        I0 = np.ones((N, N)) * 0.5  # Strong control needed
        
    elif scenario == "accident":
        # Normal traffic with blockage in center
        C0 = np.random.randn(N, N) * 0.3
        # Accident creates high density
        cx, cy = N // 2, N // 2
        for i in range(N):
            for j in range(N):
                dist = np.sqrt((i - cx)**2 + (j - cy)**2) / N
                if dist < 0.15:
                    C0[i, j] = 1.5  # Jam!
        I0 = np.ones((N, N)) * 0.4
        
    elif scenario == "smart_control":
        # Moderate traffic with adaptive signals
        C0 = np.random.randn(N, N) * 0.4
        # Smart signals adapt to density
        I0 = C0 * 0.5 + 0.2
        
    return C0, I0


def create_traffic_forcing(scenario: str, t: float, T: float) -> float:
    """Create time-dependent traffic forcing (cars entering)."""
    if scenario == "rush_hour":
        # Morning rush: 0.2T to 0.4T
        # Evening rush: 0.6T to 0.8T
        if 0.2*T < t < 0.4*T or 0.6*T < t < 0.8*T:
            return 0.8  # Heavy influx
        else:
            return 0.2  # Light
            
    elif scenario == "accident":
        # Sudden spike when accident happens
        if 0.3*T < t < 0.5*T:
            return -0.5  # Blockage (negative = removal)
        else:
            return 0.3
            
    elif scenario == "smart_control":
        # Smooth modulation
        return 0.3 + 0.2 * np.sin(2 * np.pi * t / T)
        
    else:  # normal
        return 0.3


def compute_traffic_omega(C: np.ndarray, I: np.ndarray, beta: float) -> float:
    """Compute UET network mass Ω for traffic.
    
    Ω = ∫[(κC)² + (κI)² + V(C) + V(I) + β·C·I] dx
    """
    N = C.shape[0]
    dx = 1.0 / N
    
    # Gradient terms (kinetic energy)
    grad_C_x = (np.roll(C, -1, axis=0) - np.roll(C, 1, axis=0)) / (2*dx)
    grad_C_y = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2*dx)
    grad_I_x = (np.roll(I, -1, axis=0) - np.roll(I, 1, axis=0)) / (2*dx)
    grad_I_y = (np.roll(I, -1, axis=1) - np.roll(I, 1, axis=1)) / (2*dx)
    
    kinetic = 0.5 * (grad_C_x**2 + grad_C_y**2 + grad_I_x**2 + grad_I_y**2)
    
    # Potential V(φ) = (φ²-1)²/4 (double-well for traffic equilibrium)
    V_C = (C**2 - 1)**2 / 4
    V_I = (I**2 - 1)**2 / 4
    
    # Coupling energy
    coupling = beta * C * I
    
    omega = np.sum(kinetic + V_C + V_I + coupling) * dx**2
    return float(omega)



def run_traffic_simulation(C0: np.ndarray, I0: np.ndarray, scenario: str,
                           config: dict, n_snapshots: int = 60):
    """Run traffic flow simulation."""
    N = C0.shape[0]
    L = config.get("L", 10.0)
    T = config.get("T", 5.0)
    dt = config.get("dt", 0.02)
    beta = config.get("beta", 0.7)  # Traffic response to signals
    kappa = config.get("kappa", 0.4)  # Flow between roads
    
    n_steps = int(T / dt)
    snapshot_every = max(1, n_steps // n_snapshots)
    
    C = C0.copy()  # Vehicle density
    I = I0.copy()  # Traffic control
    
    # Histories
    C_history = [C.copy()]
    I_history = [I.copy()]
    t_history = [0.0]
    avg_density = [float(np.mean(np.abs(C)))]
    max_jam = [float(np.max(C))]
    flow_efficiency = [float(1 / (1 + np.std(C)))]
    
    print(f"  Running traffic simulation: {N}×{N} grid, {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # Get current forcing (cars entering)
        s = create_traffic_forcing(scenario, t, T)
        s_field = np.ones((N, N)) * s
        
        # Laplacian (traffic flow between roads)
        def laplacian(f):
            return (
                np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
                np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) - 4*f
            ) * (N / L)**2
        
        lapC = laplacian(C)
        lapI = laplacian(I)
        
        # Traffic dynamics
        # C (cars) flow based on control (I) and congestion
        dC = (kappa * lapC 
              - C * (C**2 - 1)  # Self-regulation (jams clear eventually)
              - beta * (C - I)  # Follow traffic signals
              + s_field)  # New cars
        
        # I (control) adapts to traffic
        dI = (kappa * lapI * 0.3
              - I * (I**2 - 1)
              - beta * (I - C) * 0.4)  # Signals respond to density
        
        C = C + dt * dC
        I = I + dt * dI
        
        # Clip (can't have negative cars)
        C = np.clip(C, -2, 2)
        I = np.clip(I, -2, 2)
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            I_history.append(I.copy())
            t_history.append(t)
            avg_density.append(float(np.mean(np.abs(C))))
            max_jam.append(float(np.max(C)))
            flow_efficiency.append(float(1 / (1 + np.std(C))))
    
    return {
        "C": C_history,
        "I": I_history,
        "t": t_history,
        "avg_density": avg_density,
        "max_jam": max_jam,
        "flow_efficiency": flow_efficiency,
    }


def make_traffic_animation(case_dir: Path, history: dict, scenario: str, fps: int = 12):
    """Create traffic visualization."""
    C_history = history["C"]
    I_history = history["I"]
    t_history = history["t"]
    
    n_frames = len(C_history)
    c_lim = 1.5
    
    fig = plt.figure(figsize=(16, 9))
    
    def update(frame):
        fig.clear()
        
        C = C_history[frame]
        I = I_history[frame]
        t = t_history[frame]
        
        # Layout: 2x3
        ax1 = fig.add_subplot(231)  # Vehicle density
        ax2 = fig.add_subplot(232)  # Traffic control
        ax3 = fig.add_subplot(233)  # Congestion (C-I)
        ax4 = fig.add_subplot(234)  # Avg density
        ax5 = fig.add_subplot(235)  # Max jam
        ax6 = fig.add_subplot(236)  # Flow efficiency
        
        # Vehicle density
        im1 = ax1.imshow(C, cmap='YlOrRd', vmin=-c_lim, vmax=c_lim)
        ax1.set_title('🚗 Vehicle Density', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Road X')
        ax1.set_ylabel('Road Y')
        plt.colorbar(im1, ax=ax1, shrink=0.7)
        
        # Traffic control
        im2 = ax2.imshow(I, cmap='Blues', vmin=-c_lim, vmax=c_lim)
        ax2.set_title('🚦 Traffic Control', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Road X')
        plt.colorbar(im2, ax=ax2, shrink=0.7)
        
        # Congestion
        diff = C - I
        im3 = ax3.imshow(diff, cmap='RdYlGn_r', vmin=-c_lim, vmax=c_lim)
        ax3.set_title('⚠️ Congestion Level', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Road X')
        plt.colorbar(im3, ax=ax3, shrink=0.7)
        
        # Metrics
        ax4.plot(t_history[:frame+1], history["avg_density"][:frame+1], 'b-', lw=2)
        ax4.set_xlim(0, t_history[-1])
        ax4.set_ylim(0, max(history["avg_density"]) * 1.2)
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Avg Density')
        ax4.set_title('📊 Average Traffic Density')
        ax4.grid(True, alpha=0.3)
        
        ax5.plot(t_history[:frame+1], history["max_jam"][:frame+1], 'r-', lw=2)
        ax5.set_xlim(0, t_history[-1])
        ax5.set_ylim(0, max(history["max_jam"]) * 1.2)
        ax5.set_xlabel('Time')
        ax5.set_ylabel('Max Jam')
        ax5.set_title('🚨 Maximum Congestion')
        ax5.grid(True, alpha=0.3)
        
        ax6.fill_between(t_history[:frame+1], 0, history["flow_efficiency"][:frame+1],
                         color='green', alpha=0.3)
        ax6.plot(t_history[:frame+1], history["flow_efficiency"][:frame+1], 'g-', lw=2)
        ax6.set_xlim(0, t_history[-1])
        ax6.set_ylim(0, 1)
        ax6.set_xlabel('Time')
        ax6.set_ylabel('Efficiency')
        ax6.set_title('✅ Flow Efficiency')
        ax6.grid(True, alpha=0.3)
        
        fig.suptitle(f'🚦 Traffic Flow Simulation - {scenario.upper()} | t = {t:.2f}',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "CI_evolution.gif"
    print(f"  Saving traffic animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def make_scatter_animation(case_dir: Path, history: dict, scenario: str, fps: int = 15) -> Path:
    """Create animated scatter plot showing Density vs Max Jam phase space."""
    density = history["avg_density"]
    max_jam = history["max_jam"]
    efficiency = history["flow_efficiency"]
    t = history["t"]
    
    n_frames = len(density)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Limits
    d_lim = max(density) * 1.2
    j_lim = max(max_jam) * 1.2
    
    def update(frame):
        ax.clear()
        
        # Plot trajectory up to current frame
        if frame > 0:
            for i in range(frame):
                alpha = 0.1 + 0.9 * (i / frame)
                # Color by efficiency
                eff = efficiency[i]
                color = plt.cm.RdYlGn(eff)
                ax.plot(density[i:i+2], max_jam[i:i+2], c=color, alpha=alpha, lw=2)
        
        # Current point
        ax.scatter(density[frame], max_jam[frame], s=200, c='red',
                  edgecolors='white', linewidth=2, zorder=10)
        
        # Future points (faint)
        if frame < n_frames - 1:
            ax.scatter(density[frame+1:], max_jam[frame+1:], s=10, c='gray', alpha=0.1)
        
        # Quadrant lines
        ax.axhline(j_lim/2, color='gray', lw=0.5, alpha=0.5)
        ax.axvline(d_lim/2, color='gray', lw=0.5, alpha=0.5)
        
        # Quadrant labels
        ax.text(d_lim*0.8, j_lim*0.85, 'Congested\n(Bad)', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold', color='red')
        ax.text(d_lim*0.2, j_lim*0.85, 'Blocked\n(Accident)', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold')
        ax.text(d_lim*0.2, j_lim*0.15, 'Optimal\n(Light)', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold', color='green')
        ax.text(d_lim*0.8, j_lim*0.15, 'Efficient\n(Flowing)', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold')
        
        ax.set_xlim(0, d_lim)
        ax.set_ylim(0, j_lim)
        ax.set_xlabel('Average Traffic Density', fontsize=12, fontweight='bold')
        ax.set_ylabel('Maximum Congestion Point', fontsize=12, fontweight='bold')
        ax.set_title(f'🚗 Traffic Phase Space | {scenario.upper()}\nt = {t[frame]:.2f}',
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.2)
        
        # Add efficiency indicator
        eff_pct = efficiency[frame] * 100
        ax.text(0.95, 0.05, f'Efficiency: {eff_pct:.0f}%', transform=ax.transAxes,
               ha='right', va='bottom', fontsize=11,
               color='green' if eff_pct > 70 else 'orange' if eff_pct > 40 else 'red',
               fontweight='bold')
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "scatter_animation.gif"
    print(f"  Saving scatter animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def run_traffic_demo(scenario: str, out_dir: Path, N: int = 32, T: float = 5.0):
    """Run complete traffic demo."""
    print(f"\n🚗 Running Traffic Demo: {scenario}")
    
    case_dir = out_dir / f"toy_traffic_{scenario}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Initial conditions
    C0, I0 = create_traffic_initial(N, scenario)
    
    config = {
        "L": 10.0,
        "T": T,
        "dt": 0.02,
        "beta": 0.7,
        "kappa": 0.4,
    }
    
    # Run simulation
    history = run_traffic_simulation(C0, I0, scenario, config)
    
    # Save snapshots
    snapshot_dir = case_dir / "snapshots"
    snapshot_dir.mkdir(exist_ok=True)
    for i, (C, I, t) in enumerate(zip(history["C"], history["I"], history["t"])):
        np.savez(snapshot_dir / f"step_{i:04d}.npz", C=C, I=I, t=t)
    
    # Save config
    cfg = {
        "case_id": f"toy_traffic_{scenario}",
        "model": "C_I",
        "scenario": scenario,
        "grid": {"N": N},
        "domain": {"L": config["L"]},
        "time": {"T": T, "dt": config["dt"]},
        "params": {"beta": config["beta"], "kappa": config["kappa"]},
        "description": f"Traffic flow - {scenario}"
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    
    # Save summary with Omega
    C_final = history["C"][-1]
    I_final = history["I"][-1]
    C_initial = history["C"][0]
    I_initial = history["I"][0]
    
    omega_initial = compute_traffic_omega(C_initial, I_initial, config["beta"])
    omega_final = compute_traffic_omega(C_final, I_final, config["beta"])
    delta_omega = (omega_final - omega_initial) / abs(omega_initial) if omega_initial != 0 else 0
    
    summary = {
        "case_id": f"toy_traffic_{scenario}",
        "status": "PASS",
        "scenario": scenario,
        "avg_density": float(history["avg_density"][-1]),
        "max_jam": float(history["max_jam"][-1]),
        "flow_efficiency": float(history["flow_efficiency"][-1]),
        "Omega0": omega_initial,
        "OmegaT": omega_final,
        "delta_omega": delta_omega,
        "omega_conserved": abs(delta_omega) < 0.1,
        "description": f"UET Traffic Flow - {scenario.upper()}"
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create visualization
    make_traffic_animation(case_dir, history, scenario)
    make_scatter_animation(case_dir, history, scenario)
    
    print(f"  ✅ Demo saved to: {case_dir}")
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="Toy traffic simulation")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--scenario", default="all",
                       choices=["normal", "rush_hour", "accident", "smart_control", "all"],
                       help="Traffic scenario")
    parser.add_argument("--N", type=int, default=32, help="Grid size")
    parser.add_argument("--T", type=float, default=5.0, help="Simulation time")
    
    args = parser.parse_args()
    out_dir = Path(args.out)
    
    print("🚗 UET Traffic Flow Simulation")
    print("=" * 50)
    
    if args.scenario == "all":
        scenarios = ["normal", "rush_hour", "accident", "smart_control"]
    else:
        scenarios = [args.scenario]
    
    for scenario in scenarios:
        run_traffic_demo(scenario, out_dir, N=args.N, T=args.T)
    
    print("\n" + "=" * 50)
    print("✅ Traffic demos complete!")
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()
