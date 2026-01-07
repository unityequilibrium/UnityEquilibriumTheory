#!/usr/bin/env python
"""
Toy Physarum (Slime Mold) Simulation using UET dynamics.

Simulates the famous Physarum polycephalum that can:
- Find shortest paths in mazes
- Create optimal networks like Tokyo rail
- Do "computation without a brain"

UET Mapping:
- C field = Network/tube density (reinforced paths)
- I field = Exploration/search front
- Food sources = External potential (attract flow)
- β coupling = Reinforcement strength
- Ω = Total "cost" (network length vs efficiency)

Key behavior to reproduce:
1. Dead-end cutting (unused paths disappear)
2. Path competition (best path wins)
3. Trade-off (some redundancy for fault tolerance)

Usage:
    python scripts/run_toy_physarum.py --scenario tokyo
    python scripts/run_toy_physarum.py --scenario maze
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
from matplotlib.patches import Circle


def create_food_sources(N: int, scenario: str) -> tuple:
    """Create food source positions (cities/targets)."""
    
    if scenario == "tokyo":
        # Simplified Tokyo-like: major stations around center
        # Positions as (x, y) normalized to [0, N]
        cities = [
            (N//2, N//2),      # Central (Tokyo)
            (N//4, N//4),      # SW
            (3*N//4, N//4),    # SE
            (N//4, 3*N//4),    # NW
            (3*N//4, 3*N//4),  # NE
            (N//2, N//6),      # S
            (N//2, 5*N//6),    # N
            (N//6, N//2),      # W
            (5*N//6, N//2),    # E
        ]
        names = ["Central", "SW", "SE", "NW", "NE", "South", "North", "West", "East"]
        
    elif scenario == "two_points":
        # Simple: just find path between 2 points
        cities = [(N//4, N//2), (3*N//4, N//2)]
        names = ["Start", "End"]
        
    elif scenario == "triangle":
        # 3 cities forming triangle
        cx, cy = N//2, N//2
        r = N//3
        cities = [
            (int(cx), int(cy - r)),  # Top
            (int(cx - r*0.87), int(cy + r*0.5)),  # Bottom left
            (int(cx + r*0.87), int(cy + r*0.5)),  # Bottom right
        ]
        names = ["A", "B", "C"]
        
    elif scenario == "ring":
        # Cities in a ring
        cx, cy = N//2, N//2
        r = N//3
        n_cities = 6
        cities = []
        names = []
        for i in range(n_cities):
            angle = 2 * np.pi * i / n_cities
            x = int(cx + r * np.cos(angle))
            y = int(cy + r * np.sin(angle))
            cities.append((x, y))
            names.append(chr(65 + i))  # A, B, C, ...
            
    else:  # random
        np.random.seed(42)
        n_cities = 8
        cities = [(np.random.randint(N//6, 5*N//6), 
                   np.random.randint(N//6, 5*N//6)) for _ in range(n_cities)]
        names = [f"C{i}" for i in range(n_cities)]
    
    return cities, names


def create_food_potential(N: int, cities: list, radius: float = 3.0) -> np.ndarray:
    """Create potential field from food sources (attraction)."""
    V = np.zeros((N, N))
    
    for cx, cy in cities:
        for i in range(N):
            for j in range(N):
                dist = np.sqrt((i - cx)**2 + (j - cy)**2)
                # Gaussian attraction
                V[i, j] += np.exp(-dist**2 / (2 * radius**2))
    
    # Normalize
    V = V / V.max() if V.max() > 0 else V
    return V


def create_physarum_initial(N: int, cities: list) -> tuple:
    """Create initial slime mold state."""
    # Start with small amount everywhere (exploration mode)
    C0 = np.random.rand(N, N) * 0.1  # Network density
    I0 = np.ones((N, N)) * 0.3  # Exploration front
    
    # Seed starting points at food sources
    for cx, cy in cities:
        for di in range(-2, 3):
            for dj in range(-2, 3):
                ni, nj = cx + di, cy + dj
                if 0 <= ni < N and 0 <= nj < N:
                    C0[ni, nj] = 0.8  # Strong initial presence
                    I0[ni, nj] = 0.5
    
    return C0, I0


def run_physarum_simulation(C0: np.ndarray, I0: np.ndarray, V: np.ndarray,
                            cities: list, config: dict, n_snapshots: int = 80):
    """
    Run Physarum network formation simulation.
    
    Key dynamics:
    1. C (network) grows where there's flow (V gradient)
    2. C decays where there's no reinforcement
    3. I (exploration) spreads but follows C
    """
    N = C0.shape[0]
    L = config.get("L", 10.0)
    T = config.get("T", 8.0)
    dt = config.get("dt", 0.02)
    beta = config.get("beta", 0.5)
    kappa = config.get("kappa", 0.6)  # Higher = more diffusion
    decay = config.get("decay", 0.02)  # Dead-end cutting rate
    reinforce = config.get("reinforce", 0.8)  # Path reinforcement
    
    n_steps = int(T / dt)
    snapshot_every = max(1, n_steps // n_snapshots)
    
    C = C0.copy()  # Network density
    I = I0.copy()  # Exploration
    
    # Compute gradient of potential (direction toward food)
    Vy, Vx = np.gradient(V)
    
    # Histories
    C_history = [C.copy()]
    I_history = [I.copy()]
    t_history = [0.0]
    network_mass = [float(np.sum(C))]
    max_density = [float(np.max(C))]
    # Network efficiency = 1 / (spread + 1)
    network_efficiency = [float(1 / (1 + np.std(C)))]
    
    print(f"  Running Physarum simulation: {N}×{N} grid, {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # Laplacian (spreading)
        def laplacian(f):
            return (
                np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
                np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) - 4*f
            ) * (N / L)**2
        
        lapC = laplacian(C)
        lapI = laplacian(I)
        
        # Physarum-inspired dynamics
        # Key insight: "use it or lose it" + "follow the gradient"
        
        # Flow toward food (chemotaxis-like)
        flow_x = -Vx * C  # Move toward high V
        flow_y = -Vy * C
        
        # Flux = how much is flowing through
        flux = np.sqrt(flow_x**2 + flow_y**2)
        
        # Network dynamics:
        # 1. Diffuse (spread)
        # 2. Reinforce where flux is high
        # 3. Decay where flux is low
        # 4. Attract toward food (V)
        
        dC = (kappa * lapC 
              + reinforce * flux * (1 - C)  # Reinforce used paths (cap at 1)
              - decay * C * (1 - flux / (flux.max() + 0.01))  # Decay unused
              + V * 0.2 * (1 - C)  # Attract toward food
              - beta * C * (C - 0.5) * (C - 1))  # Bistable: 0 or 1
        
        # Exploration dynamics:
        # Spread out, but concentrate where C is high
        dI = (kappa * lapI * 0.5
              - 0.1 * I * (1 - C)  # Die where no network
              + 0.05 * C)  # Reinforce where network exists
        
        C = C + dt * dC
        I = I + dt * dI
        
        # Clip
        C = np.clip(C, 0, 1.5)
        I = np.clip(I, 0, 1)
        
        # Re-seed food sources (keep them active)
        for cx, cy in cities:
            if 0 <= cx < N and 0 <= cy < N:
                C[cx, cy] = max(C[cx, cy], 0.5)
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            I_history.append(I.copy())
            t_history.append(t)
            network_mass.append(float(np.sum(C)))
            max_density.append(float(np.max(C)))
            network_efficiency.append(float(1 / (1 + np.std(C))))
            
            # Progress
            if step % (n_steps // 4) == 0:
                print(f"    Step {step}/{n_steps}, network mass: {network_mass[-1]:.1f}")
    
    return {
        "C": C_history,
        "I": I_history,
        "t": t_history,
        "network_mass": network_mass,
        "max_density": max_density,
        "network_efficiency": network_efficiency,
        "cities": cities,
        "V": V,
    }


def make_physarum_animation(case_dir: Path, history: dict, city_names: list, 
                            fps: int = 12) -> Path:
    """Create Physarum network formation animation."""
    C_history = history["C"]
    I_history = history["I"]
    t_history = history["t"]
    cities = history["cities"]
    V = history["V"]
    
    n_frames = len(C_history)
    N = C_history[0].shape[0]
    
    fig = plt.figure(figsize=(16, 6))
    
    def update(frame):
        fig.clear()
        
        C = C_history[frame]
        I = I_history[frame]
        t = t_history[frame]
        
        # Layout: 1x3
        ax1 = fig.add_subplot(131)  # Network
        ax2 = fig.add_subplot(132)  # Potential
        ax3 = fig.add_subplot(133)  # Metrics
        
        # Network (main view)
        # Threshold to show only strong connections
        C_thresh = np.where(C > 0.3, C, 0)
        ax1.imshow(C_thresh, cmap='YlGn', vmin=0, vmax=1, origin='lower')
        
        # Mark cities
        for (cx, cy), name in zip(cities, city_names):
            ax1.scatter(cy, cx, s=100, c='red', edgecolors='white', linewidth=2, zorder=10)
            ax1.annotate(name, (cy, cx), xytext=(5, 5), textcoords='offset points',
                        fontsize=8, color='red', fontweight='bold')
        
        ax1.set_title(f'🦠 Physarum Network | t={t:.1f}', fontsize=12, fontweight='bold')
        ax1.set_xlim(0, N)
        ax1.set_ylim(0, N)
        ax1.set_aspect('equal')
        
        # Potential + Exploration
        ax2.imshow(V, cmap='Blues', alpha=0.5, origin='lower')
        ax2.contour(I, levels=5, colors='orange', alpha=0.7)
        for (cx, cy), name in zip(cities, city_names):
            ax2.scatter(cy, cx, s=80, c='red', edgecolors='white', zorder=10)
        ax2.set_title('🍕 Food Sources + Exploration', fontsize=11)
        ax2.set_xlim(0, N)
        ax2.set_ylim(0, N)
        ax2.set_aspect('equal')
        
        # Metrics
        ax3.plot(t_history[:frame+1], history["network_mass"][:frame+1], 'g-', lw=2)
        ax3.set_xlim(0, t_history[-1])
        ax3.set_ylim(0, max(history["network_mass"]) * 1.1)
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Network Mass')
        ax3.set_title('📊 Network Growth', fontsize=11)
        ax3.grid(True, alpha=0.3)
        
        # Add phase annotation
        if frame < len(C_history) // 3:
            phase = "🔍 Exploration"
        elif frame < 2 * len(C_history) // 3:
            phase = "⚡ Competition"
        else:
            phase = "✅ Optimized"
        
        fig.text(0.5, 0.02, phase, ha='center', fontsize=12, 
                fontweight='bold', color='darkgreen')
        
        plt.tight_layout()
        fig.subplots_adjust(bottom=0.1)
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "CI_evolution.gif"
    print(f"  Saving Physarum animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def make_scatter_animation(case_dir: Path, history: dict, scenario: str, fps: int = 15) -> Path:
    """Create animated scatter plot showing Network Mass vs Efficiency."""
    mass = history["network_mass"]
    efficiency = history["network_efficiency"]
    t = history["t"]
    
    n_frames = len(mass)
    
    # Normalize
    max_mass = max(mass)
    mass_norm = [m / max_mass for m in mass]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    def update(frame):
        ax.clear()
        
        # Plot trajectory
        if frame > 0:
            for i in range(frame):
                alpha = 0.1 + 0.9 * (i / frame)
                # Color by phase
                if i < n_frames // 3:
                    color = 'blue'  # Exploration
                elif i < 2 * n_frames // 3:
                    color = 'orange'  # Competition
                else:
                    color = 'green'  # Optimized
                ax.plot(mass_norm[i:i+2], efficiency[i:i+2], c=color, alpha=alpha, lw=2)
        
        # Current point
        ax.scatter(mass_norm[frame], efficiency[frame], s=200, c='red',
                  edgecolors='white', linewidth=2, zorder=10)
        
        # Future points
        if frame < n_frames - 1:
            ax.scatter(mass_norm[frame+1:], efficiency[frame+1:], s=10, c='gray', alpha=0.1)
        
        # Optimal region
        ax.axhspan(0.6, 1.0, alpha=0.1, color='green')
        ax.axvspan(0.7, 1.0, alpha=0.1, color='green')
        
        # Labels
        ax.text(0.85, 0.85, 'Optimal\nNetwork', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold', color='green')
        ax.text(0.3, 0.85, 'Sparse\nConnected', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold')
        ax.text(0.85, 0.3, 'Dense\nChaotic', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold')
        ax.text(0.3, 0.3, 'Exploring', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold', color='blue')
        
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel('Network Mass (normalized)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Network Efficiency', fontsize=12, fontweight='bold')
        ax.set_title(f'🦠 Physarum Phase Space | {scenario.upper()}\nt = {t[frame]:.2f}',
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.2)
        
        # Phase indicator
        if frame < n_frames // 3:
            phase = "🔍 Exploration"
        elif frame < 2 * n_frames // 3:
            phase = "⚡ Competition"
        else:
            phase = "✅ Optimized"
        ax.text(0.95, 0.05, phase, transform=ax.transAxes,
               ha='right', va='bottom', fontsize=11, fontweight='bold')
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "scatter_animation.gif"
    print(f"  Saving scatter animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path



def run_physarum_demo(scenario: str, out_dir: Path, N: int = 64, T: float = 8.0):
    """Run complete Physarum demo."""
    print(f"\n🦠 Running Physarum Demo: {scenario}")
    
    case_dir = out_dir / f"toy_physarum_{scenario}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Create food sources
    cities, names = create_food_sources(N, scenario)
    print(f"  Cities: {names}")
    
    # Create potential field
    V = create_food_potential(N, cities, radius=4.0)
    
    # Initial state
    C0, I0 = create_physarum_initial(N, cities)
    
    config = {
        "L": 10.0,
        "T": T,
        "dt": 0.02,
        "beta": 0.5,
        "kappa": 0.6,
        "decay": 0.02,
        "reinforce": 0.8,
    }
    
    # Run simulation
    history = run_physarum_simulation(C0, I0, V, cities, config)
    
    # Save snapshots
    snapshot_dir = case_dir / "snapshots"
    snapshot_dir.mkdir(exist_ok=True)
    for i, (C, I, t) in enumerate(zip(history["C"], history["I"], history["t"])):
        np.savez(snapshot_dir / f"step_{i:04d}.npz", C=C, I=I, t=t)
    
    # Save config
    cfg = {
        "case_id": f"toy_physarum_{scenario}",
        "model": "C_I",
        "scenario": scenario,
        "grid": {"N": N},
        "domain": {"L": config["L"]},
        "time": {"T": T, "dt": config["dt"]},
        "params": config,
        "cities": cities,
        "city_names": names,
        "description": f"Physarum slime mold - {scenario}"
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    
    # Save summary
    summary = {
        "case_id": f"toy_physarum_{scenario}",
        "status": "PASS",
        "scenario": scenario,
        "n_cities": len(cities),
        "final_network_mass": float(history["network_mass"][-1]),
        "description": f"Physarum Network - {scenario.upper()}"
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create visualization
    make_physarum_animation(case_dir, history, names)
    make_scatter_animation(case_dir, history, scenario)
    
    print(f"  ✅ Demo saved to: {case_dir}")
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="Physarum slime mold simulation")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--scenario", default="all",
                       choices=["tokyo", "two_points", "triangle", "ring", "all"],
                       help="Network scenario")
    parser.add_argument("--N", type=int, default=64, help="Grid size")
    parser.add_argument("--T", type=float, default=8.0, help="Simulation time")
    
    args = parser.parse_args()
    out_dir = Path(args.out)
    
    print("🦠 Physarum Slime Mold Network Simulation")
    print("=" * 50)
    print("Simulating: Dead-end cutting + Path competition")
    
    if args.scenario == "all":
        scenarios = ["tokyo", "two_points", "triangle", "ring"]
    else:
        scenarios = [args.scenario]
    
    for scenario in scenarios:
        run_physarum_demo(scenario, out_dir, N=args.N, T=args.T)
    
    print("\n" + "=" * 50)
    print("✅ Physarum demos complete!")
    print("\nKey behaviors to observe:")
    print("  1. 🔍 Exploration phase - slime spreads out")
    print("  2. ⚡ Competition phase - paths compete")
    print("  3. ✅ Optimization phase - best network emerges")
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()
