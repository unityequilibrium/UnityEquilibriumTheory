#!/usr/bin/env python
"""
Add enhanced visualizations to Physics/GR demos.
Generates: omega_evolution.png, energy_analysis.png, phase_diagram.png
"""
import json
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def compute_omega(C, I, beta=0.5, kappa=0.3):
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


def add_enhanced_viz(demo_dir):
    """Add enhanced visualizations to a demo directory."""
    demo_dir = Path(demo_dir)
    snapshots_dir = demo_dir / "snapshots"
    
    # Try to load snapshots
    if not snapshots_dir.exists():
        print(f"  ⚠️ No snapshots - skipping detailed analysis")
        return False
    
    files = sorted(snapshots_dir.glob("step_*.npz"))
    if len(files) < 5:
        print(f"  ⚠️ Not enough snapshots ({len(files)})")
        return False
    
    # Load all snapshots
    times = []
    omegas = []
    mean_C = []
    mean_I = []
    std_C = []
    std_I = []
    
    for f in files:
        data = np.load(f)
        C = data["C"]
        I = data["I"]
        t = float(data.get("t", 0))
        
        times.append(t)
        omegas.append(compute_omega(C, I))
        mean_C.append(np.mean(C))
        mean_I.append(np.mean(I))
        std_C.append(np.std(C))
        std_I.append(np.std(I))
    
    times = np.array(times)
    omegas = np.array(omegas)
    
    # Load config for title
    config = {}
    if (demo_dir / "config.json").exists():
        with open(demo_dir / "config.json") as f:
            config = json.load(f)
    demo_name = config.get("case_id", demo_dir.name)
    
    plt.style.use('dark_background')
    
    # 1. Omega Evolution Plot
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='black')
    ax.plot(times, omegas, 'cyan', lw=2, label='Ω(t)')
    ax.set_xlabel('Time', color='white', fontsize=12)
    ax.set_ylabel('Network Mass Ω', color='white', fontsize=12)
    ax.set_title(f'{demo_name}: Omega Evolution', color='white', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Annotate start/end
    ax.scatter([times[0]], [omegas[0]], c='lime', s=100, zorder=5, label=f'Ω₀={omegas[0]:.2f}')
    ax.scatter([times[-1]], [omegas[-1]], c='red', s=100, zorder=5, label=f'Ω_T={omegas[-1]:.2f}')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(demo_dir / "omega_evolution.png", dpi=150, facecolor='black')
    plt.close()
    
    # 2. Energy Analysis Plot (decomposition)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), facecolor='black')
    
    # Mean fields
    axes[0,0].plot(times, mean_C, 'orange', lw=2, label='⟨C⟩')
    axes[0,0].plot(times, mean_I, 'purple', lw=2, label='⟨I⟩')
    axes[0,0].set_xlabel('Time', color='white')
    axes[0,0].set_ylabel('Mean Value', color='white')
    axes[0,0].set_title('Mean Field Values', color='white')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Standard deviation
    axes[0,1].plot(times, std_C, 'orange', lw=2, label='σ(C)')
    axes[0,1].plot(times, std_I, 'purple', lw=2, label='σ(I)')
    axes[0,1].set_xlabel('Time', color='white')
    axes[0,1].set_ylabel('Std Dev', color='white')
    axes[0,1].set_title('Field Fluctuations', color='white')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Omega log-scale
    axes[1,0].semilogy(times, np.abs(omegas), 'cyan', lw=2)
    axes[1,0].set_xlabel('Time', color='white')
    axes[1,0].set_ylabel('|Ω| (log)', color='white')
    axes[1,0].set_title('Omega Magnitude (log scale)', color='white')
    axes[1,0].grid(True, alpha=0.3)
    
    # dOmega/dt
    if len(omegas) > 1:
        dt = times[1] - times[0] if times[1] > times[0] else 1
        dOmega = np.gradient(omegas, dt)
        axes[1,1].plot(times, dOmega, 'yellow', lw=2)
    axes[1,1].axhline(0, color='gray', lw=0.5)
    axes[1,1].set_xlabel('Time', color='white')
    axes[1,1].set_ylabel('dΩ/dt', color='white')
    axes[1,1].set_title('Energy Flow Rate', color='white')
    axes[1,1].grid(True, alpha=0.3)
    
    fig.suptitle(f'{demo_name}: Energy Analysis', fontsize=14, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(demo_dir / "energy_analysis.png", dpi=150, facecolor='black')
    plt.close()
    
    # 3. Phase Diagram (C vs I)
    fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
    
    # Color by time
    colors = plt.cm.viridis(np.linspace(0, 1, len(mean_C)))
    for i in range(len(mean_C)-1):
        ax.plot([mean_C[i], mean_C[i+1]], [mean_I[i], mean_I[i+1]], 
                c=colors[i], lw=2)
    
    ax.scatter([mean_C[0]], [mean_I[0]], c='lime', s=150, zorder=5, marker='o', label='Start')
    ax.scatter([mean_C[-1]], [mean_I[-1]], c='red', s=150, zorder=5, marker='s', label='End')
    
    ax.set_xlabel('⟨C⟩', color='white', fontsize=12)
    ax.set_ylabel('⟨I⟩', color='white', fontsize=12)
    ax.set_title(f'{demo_name}: Phase Trajectory', color='white', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(demo_dir / "phase_diagram.png", dpi=150, facecolor='black')
    plt.close()
    
    plt.style.use('default')
    
    # Update summary with analysis
    summary_path = demo_dir / "summary.json"
    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)
        
        summary["analysis"] = {
            "omega_range": [float(min(omegas)), float(max(omegas))],
            "omega_trend": "increasing" if omegas[-1] > omegas[0] else "decreasing",
            "final_mean_C": float(mean_C[-1]),
            "final_mean_I": float(mean_I[-1]),
            "final_std_C": float(std_C[-1]),
            "final_std_I": float(std_I[-1]),
            "n_snapshots": len(files)
        }
        
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
    
    print(f"  ✅ Created: omega_evolution.png, energy_analysis.png, phase_diagram.png")
    return True


def main():
    import sys
    
    base = Path("runs_gallery")
    
    # All physics/GR demos
    demos = [
        "einstein_wave", "einstein_collapse", "einstein_binary",
        "gr_realistic_wave", "gr_realistic_collapse", "gr_realistic_binary", 
        "nr_wave", "nr_collapse", "nr_binary",
        "cosmological_constant", "galaxy_rotation_dm", "landscape_comparison",
        # Extension demos
        "test_delays", "test_multifield", "test_nonlocal", 
        "test_stochastic", "test_memory", "test_custom_potentials"
    ]
    
    print("📊 Adding enhanced visualizations...")
    
    success = 0
    for demo in demos:
        demo_dir = base / demo
        if demo_dir.exists():
            print(f"\n📁 {demo}")
            if add_enhanced_viz(demo_dir):
                success += 1
        else:
            print(f"  ⚠️ {demo}: not found")
    
    print(f"\n✅ Enhanced {success} demos with visualizations!")
    print("\nRun demo card regeneration:")
    print("  python scripts/regenerate_demo_cards.py")


if __name__ == "__main__":
    main()
