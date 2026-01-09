#!/usr/bin/env python
"""
Toy Stock Market Simulation using UET dynamics.

Maps UET concepts to financial markets:
- C field = Price deviation (volatility field)
- I field = Investor sentiment (fear/greed)
- β coupling = Price-sentiment feedback strength
- s-tilt = Market bias (bullish/bearish news)
- Ω = Market "stress energy" (lower = more stable)

Usage:
    python scripts/run_toy_stock.py --out runs_gallery
    python scripts/run_toy_stock.py --scenario crash
    python scripts/run_toy_stock.py --scenario recovery
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


def create_market_initial(N: int, volatility: float = 0.3) -> tuple[np.ndarray, np.ndarray]:
    """
    Create initial market state.
    N×N grid represents: sectors (rows) × sub-markets (cols)
    
    Returns:
        C0: Initial price deviation field
        I0: Initial sentiment field
    """
    # Price starts near equilibrium with random noise
    C0 = np.random.randn(N, N) * volatility
    
    # Sentiment starts slightly optimistic (mean > 0)
    I0 = np.random.randn(N, N) * 0.2 + 0.1
    
    return C0, I0


def create_shock_schedule(T: float, dt: float, scenario: str) -> list[dict]:
    """
    Create a schedule of market shocks (news events).
    
    Returns list of {t, s_shock, region, description}
    """
    n_steps = int(T / dt)
    
    if scenario == "normal":
        # Random small shocks
        shocks = []
        for i in range(5):
            t = (i + 1) * T / 6
            s = np.random.uniform(-0.3, 0.3)
            shocks.append({
                "t": t, 
                "s": s, 
                "region": "random",
                "desc": "Minor news"
            })
        return shocks
    
    elif scenario == "crash":
        # Big negative shock followed by panic
        return [
            {"t": T*0.2, "s": -0.8, "region": "all", "desc": "Bad news hits"},
            {"t": T*0.3, "s": -1.2, "region": "all", "desc": "Panic selling"},
            {"t": T*0.5, "s": -0.5, "region": "all", "desc": "Continued fear"},
            {"t": T*0.8, "s": +0.3, "region": "all", "desc": "Bottom hunting"},
        ]
    
    elif scenario == "recovery":
        # Start negative, gradual recovery
        return [
            {"t": T*0.1, "s": -0.5, "region": "all", "desc": "Initial fear"},
            {"t": T*0.3, "s": +0.3, "region": "center", "desc": "Hope emerges"},
            {"t": T*0.5, "s": +0.5, "region": "all", "desc": "Recovery begins"},
            {"t": T*0.7, "s": +0.8, "region": "all", "desc": "Bull market"},
            {"t": T*0.9, "s": +0.3, "region": "all", "desc": "Steady growth"},
        ]
    
    elif scenario == "bubble":
        # Irrational exuberance then pop
        return [
            {"t": T*0.1, "s": +0.5, "region": "all", "desc": "FOMO begins"},
            {"t": T*0.25, "s": +1.0, "region": "all", "desc": "Euphoria"},
            {"t": T*0.4, "s": +1.5, "region": "all", "desc": "Peak greed"},
            {"t": T*0.5, "s": -2.0, "region": "all", "desc": "BUBBLE POP!"},
            {"t": T*0.6, "s": -1.0, "region": "all", "desc": "Panic"},
            {"t": T*0.8, "s": +0.2, "region": "all", "desc": "Stabilizing"},
        ]
    
    else:  # custom
        return []


def apply_shock(s_field: np.ndarray, shock: dict, N: int) -> np.ndarray:
    """Apply a shock to the s-tilt field."""
    s_new = s_field.copy()
    
    if shock["region"] == "all":
        s_new += shock["s"]
    elif shock["region"] == "center":
        # Shock centered on grid
        cx, cy = N // 2, N // 2
        for i in range(N):
            for j in range(N):
                dist = np.sqrt((i - cx)**2 + (j - cy)**2) / N
                s_new[i, j] += shock["s"] * np.exp(-dist**2 / 0.1)
    elif shock["region"] == "random":
        # Random region
        cx, cy = np.random.randint(0, N), np.random.randint(0, N)
        for i in range(N):
            for j in range(N):
                dist = np.sqrt((i - cx)**2 + (j - cy)**2) / N
                s_new[i, j] += shock["s"] * np.exp(-dist**2 / 0.1)
    
    return np.clip(s_new, -2, 2)


def run_stock_simulation(C0: np.ndarray, I0: np.ndarray, config: dict, 
                         shocks: list, n_snapshots: int = 60):
    """
    Run stock market simulation.
    
    Returns history of fields and observables.
    """
    N = C0.shape[0]
    L = config.get("L", 10.0)
    T = config.get("T", 5.0)
    dt = config.get("dt", 0.02)
    beta = config.get("beta", 0.6)  # Higher = stronger sentiment-price coupling
    kappa = config.get("kappa", 0.3)  # Diffusion (market contagion)
    
    n_steps = int(T / dt)
    snapshot_every = max(1, n_steps // n_snapshots)
    
    C = C0.copy()  # Price deviation
    I = I0.copy()  # Sentiment
    s = np.zeros((N, N))  # Tilt field (news bias)
    
    # Histories
    C_history = [C.copy()]
    I_history = [I.copy()]
    t_history = [0.0]
    price_index = [float(np.mean(C))]  # Market index
    sentiment_index = [float(np.mean(I))]
    volatility = [float(np.std(C))]
    
    # Shock tracker
    shock_idx = 0
    shock_log = []
    
    print(f"  Running market simulation: {N}×{N} grid, {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # Check for shocks
        while shock_idx < len(shocks) and shocks[shock_idx]["t"] <= t:
            shock = shocks[shock_idx]
            s = apply_shock(s, shock, N)
            shock_log.append({"t": t, "desc": shock["desc"]})
            print(f"    📰 t={t:.2f}: {shock['desc']} (s={shock['s']:+.1f})")
            shock_idx += 1
        
        # Laplacian (market contagion)
        def laplacian(f):
            return (
                np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
                np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) - 4*f
            ) * (N / L)**2
        
        # UET dynamics adapted for markets
        # dC/dt = κ∇²C - C(C²-1) - β(C-I) + s
        # dI/dt = κ∇²I - I(I²-1) - β(I-C)
        
        lapC = laplacian(C)
        lapI = laplacian(I)
        
        # Price dynamics: influenced by sentiment and news
        dC = kappa * lapC - C * (C**2 - 1) - beta * (C - I) + s
        
        # Sentiment dynamics: follows price with lag
        dI = kappa * lapI - I * (I**2 - 1) - beta * (I - C) * 0.5
        
        C = C + dt * dC
        I = I + dt * dI
        
        # Decay the tilt (news effect fades)
        s = s * 0.98
        
        # Clip to prevent extreme values
        C = np.clip(C, -3, 3)
        I = np.clip(I, -3, 3)
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            I_history.append(I.copy())
            t_history.append(t)
            price_index.append(float(np.mean(C)))
            sentiment_index.append(float(np.mean(I)))
            volatility.append(float(np.std(C)))
    
    return {
        "C": C_history,
        "I": I_history,
        "t": t_history,
        "price_index": price_index,
        "sentiment_index": sentiment_index,
        "volatility": volatility,
        "shocks": shock_log,
    }


def make_stock_animation(case_dir: Path, history: dict, fps: int = 12) -> Path:
    """Create animated visualization of market dynamics."""
    C_history = history["C"]
    I_history = history["I"]
    t_history = history["t"]
    price_index = history["price_index"]
    sentiment_index = history["sentiment_index"]
    
    n_frames = len(C_history)
    N = C_history[0].shape[0]
    
    # Global limits
    c_lim = max(abs(c).max() for c in C_history) * 1.1
    
    fig = plt.figure(figsize=(14, 8))
    
    def update(frame):
        fig.clear()
        
        C = C_history[frame]
        I = I_history[frame]
        t = t_history[frame]
        
        # Layout: 2x2 grid
        ax1 = fig.add_subplot(221)  # Price field
        ax2 = fig.add_subplot(222)  # Sentiment field
        ax3 = fig.add_subplot(223)  # Price index over time
        ax4 = fig.add_subplot(224)  # Volatility
        
        # Price field (heatmap)
        im1 = ax1.imshow(C, cmap='RdYlGn', vmin=-c_lim, vmax=c_lim, aspect='equal')
        ax1.set_title('📈 Price Deviation', fontsize=11)
        ax1.set_xlabel('Sub-market')
        ax1.set_ylabel('Sector')
        plt.colorbar(im1, ax=ax1, shrink=0.8)
        
        # Sentiment field
        im2 = ax2.imshow(I, cmap='RdBu_r', vmin=-c_lim, vmax=c_lim, aspect='equal')
        ax2.set_title('💭 Investor Sentiment', fontsize=11)
        ax2.set_xlabel('Sub-market')
        ax2.set_ylabel('Sector')
        plt.colorbar(im2, ax=ax2, shrink=0.8)
        
        # Price index time series
        ax3.plot(t_history[:frame+1], price_index[:frame+1], 'g-', lw=2, label='Price')
        ax3.plot(t_history[:frame+1], sentiment_index[:frame+1], 'b--', lw=1.5, label='Sentiment')
        ax3.axhline(0, color='gray', lw=0.5, alpha=0.5)
        ax3.set_xlim(0, t_history[-1])
        ax3.set_ylim(-1.5, 1.5)
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Index')
        ax3.set_title('📊 Market Index', fontsize=11)
        ax3.legend(loc='upper right', fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # Volatility
        ax4.fill_between(t_history[:frame+1], 0, history["volatility"][:frame+1], 
                        color='orange', alpha=0.5)
        ax4.plot(t_history[:frame+1], history["volatility"][:frame+1], 'r-', lw=1.5)
        ax4.set_xlim(0, t_history[-1])
        ax4.set_ylim(0, max(history["volatility"]) * 1.2)
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Volatility (σ)')
        ax4.set_title('📉 Market Volatility', fontsize=11)
        ax4.grid(True, alpha=0.3)
        
        fig.suptitle(f'🏦 UET Stock Market Simulation | t = {t:.2f}', 
                     fontsize=13, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "CI_evolution.gif"
    print(f"  Saving market animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def make_price_chart(case_dir: Path, history: dict) -> Path:
    """Create static price chart like a stock chart."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    
    t = history["t"]
    price = history["price_index"]
    sentiment = history["sentiment_index"]
    vol = history["volatility"]
    
    # Price chart
    color = ['g' if p >= 0 else 'r' for p in price]
    axes[0].plot(t, price, 'k-', lw=1.5)
    axes[0].fill_between(t, 0, price, where=[p >= 0 for p in price], 
                         color='green', alpha=0.3, label='Bullish')
    axes[0].fill_between(t, 0, price, where=[p < 0 for p in price], 
                         color='red', alpha=0.3, label='Bearish')
    axes[0].axhline(0, color='gray', lw=1)
    axes[0].set_ylabel('Price Index')
    axes[0].set_title('🏦 Market Price Index')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)
    
    # Sentiment
    axes[1].plot(t, sentiment, 'b-', lw=1.5)
    axes[1].fill_between(t, 0, sentiment, where=[s >= 0 for s in sentiment],
                         color='blue', alpha=0.2)
    axes[1].fill_between(t, 0, sentiment, where=[s < 0 for s in sentiment],
                         color='purple', alpha=0.2)
    axes[1].axhline(0, color='gray', lw=1)
    axes[1].set_ylabel('Sentiment')
    axes[1].set_title('💭 Investor Sentiment (Fear/Greed)')
    axes[1].grid(True, alpha=0.3)
    
    # Volatility
    axes[2].fill_between(t, 0, vol, color='orange', alpha=0.5)
    axes[2].plot(t, vol, 'r-', lw=1.5)
    axes[2].set_ylabel('Volatility')
    axes[2].set_xlabel('Time')
    axes[2].set_title('📉 Market Volatility')
    axes[2].grid(True, alpha=0.3)
    
    # Mark shocks
    for shock in history.get("shocks", []):
        for ax in axes:
            ax.axvline(shock["t"], color='purple', lw=0.5, alpha=0.5)
    
    plt.tight_layout()
    
    output_path = case_dir / "price_chart.png"
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def make_scatter_animation(case_dir: Path, history: dict, scenario: str, fps: int = 15) -> Path:
    """Create animated scatter plot showing price-sentiment phase space."""
    price = history["price_index"]
    sentiment = history["sentiment_index"]
    t = history["t"]
    
    n_frames = len(price)
    
    # Global limits
    p_lim = max(abs(min(price)), abs(max(price))) * 1.2
    s_lim = max(abs(min(sentiment)), abs(max(sentiment))) * 1.2
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Color map based on time
    colors = plt.cm.viridis(np.linspace(0, 1, n_frames))
    
    def update(frame):
        ax.clear()
        
        # Plot trajectory up to current frame
        if frame > 0:
            # Faded past trajectory
            for i in range(frame):
                alpha = 0.1 + 0.9 * (i / frame)
                ax.plot(price[i:i+2], sentiment[i:i+2], 'b-', alpha=alpha, lw=1)
        
        # Current point (larger)
        ax.scatter(price[frame], sentiment[frame], s=200, c='red', 
                  edgecolors='white', linewidth=2, zorder=10)
        
        # All future points (faint)
        if frame < n_frames - 1:
            ax.scatter(price[frame+1:], sentiment[frame+1:], s=10, c='gray', alpha=0.1)
        
        # Quadrant lines
        ax.axhline(0, color='gray', lw=0.5, alpha=0.5)
        ax.axvline(0, color='gray', lw=0.5, alpha=0.5)
        
        # Quadrant labels
        ax.text(p_lim*0.8, s_lim*0.8, 'Bull\nMarket', ha='center', va='center', 
               fontsize=10, alpha=0.3, fontweight='bold')
        ax.text(-p_lim*0.8, s_lim*0.8, 'False\nHope', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold')
        ax.text(-p_lim*0.8, -s_lim*0.8, 'Bear\nMarket', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold')
        ax.text(p_lim*0.8, -s_lim*0.8, 'Cautious\nGain', ha='center', va='center',
               fontsize=10, alpha=0.3, fontweight='bold')
        
        ax.set_xlim(-p_lim, p_lim)
        ax.set_ylim(-s_lim, s_lim)
        ax.set_xlabel('Price Deviation', fontsize=12, fontweight='bold')
        ax.set_ylabel('Investor Sentiment', fontsize=12, fontweight='bold')
        ax.set_title(f'📊 Price-Sentiment Phase Space | {scenario.upper()}\nt = {t[frame]:.2f}',
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.2)
        ax.set_aspect('equal')
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "scatter_animation.gif"
    print(f"  Saving scatter animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path



def run_stock_demo(scenario: str, out_dir: Path, N: int = 32, T: float = 5.0):
    """Run a complete stock market demo."""
    print(f"\n📈 Running Stock Demo: {scenario}")
    
    case_dir = out_dir / f"toy_stock_{scenario}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Create initial state
    C0, I0 = create_market_initial(N, volatility=0.2)
    
    # Create shock schedule
    shocks = create_shock_schedule(T, dt=0.02, scenario=scenario)
    
    config = {
        "L": 10.0,
        "T": T,
        "dt": 0.02,
        "beta": 0.6,
        "kappa": 0.3,
    }
    
    # Run simulation
    history = run_stock_simulation(C0, I0, config, shocks)
    
    # Save snapshots
    snapshot_dir = case_dir / "snapshots"
    snapshot_dir.mkdir(exist_ok=True)
    for i, (C, I, t) in enumerate(zip(history["C"], history["I"], history["t"])):
        np.savez(snapshot_dir / f"step_{i:04d}.npz", C=C, I=I, t=t)
    
    # Save config
    cfg = {
        "case_id": f"toy_stock_{scenario}",
        "model": "C_I",
        "scenario": scenario,
        "grid": {"N": N},
        "domain": {"L": config["L"]},
        "time": {"T": T, "dt": config["dt"]},
        "params": {"beta": config["beta"], "kappa": config["kappa"]},
        "description": f"Stock market simulation - {scenario} scenario"
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    
    # Save summary
    summary = {
        "case_id": f"toy_stock_{scenario}",
        "status": "PASS",
        "scenario": scenario,
        "final_price": float(history["price_index"][-1]),
        "max_volatility": float(max(history["volatility"])),
        "n_shocks": len(history["shocks"]),
        "description": f"UET Stock Market - {scenario.upper()}"
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create visualizations
    make_stock_animation(case_dir, history)
    make_price_chart(case_dir, history)
    make_scatter_animation(case_dir, history, scenario)

    
    print(f"  ✅ Demo saved to: {case_dir}")
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="Run toy stock market simulation")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--scenario", default="all", 
                       choices=["normal", "crash", "recovery", "bubble", "all"],
                       help="Market scenario")
    parser.add_argument("--N", type=int, default=32, help="Grid size")
    parser.add_argument("--T", type=float, default=5.0, help="Simulation time")
    
    args = parser.parse_args()
    out_dir = Path(args.out)
    
    print("🏦 UET Stock Market Simulation")
    print("=" * 40)
    print(f"Grid: {args.N}×{args.N}")
    print(f"Time: T={args.T}")
    
    if args.scenario == "all":
        scenarios = ["normal", "crash", "recovery", "bubble"]
    else:
        scenarios = [args.scenario]
    
    for scenario in scenarios:
        run_stock_demo(scenario, out_dir, N=args.N, T=args.T)
    
    print("\n" + "=" * 40)
    print("✅ Stock demos complete!")
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()
