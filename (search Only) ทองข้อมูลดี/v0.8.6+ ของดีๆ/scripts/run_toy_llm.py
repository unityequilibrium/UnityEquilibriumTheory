#!/usr/bin/env python
"""
Toy LLM Simulation using UET dynamics.

Maps UET concepts to language model dynamics:
- C field = Token embedding states
- I field = Attention context / memory
- β coupling = Self-attention strength
- s-tilt = Prompt anchors (forcing)
- Ω = "Coherence energy" (lower = more coherent output)

Usage:
    python scripts/run_toy_llm.py --out runs_gallery
    python scripts/run_toy_llm.py --prompt "creative" 
    python scripts/run_toy_llm.py --prompt "factual"
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


def create_prompt_anchor(N: int, prompt_type: str) -> np.ndarray:
    """
    Create anchor pattern based on prompt type.
    This simulates the embedding of a prompt.
    
    N×N grid represents: tokens (rows) × embedding dims (cols)
    """
    anchor = np.zeros((N, N))
    
    if prompt_type == "creative":
        # Creative: multiple scattered attractors (high entropy)
        n_seeds = 5
        for _ in range(n_seeds):
            cx, cy = np.random.randint(2, N-2), np.random.randint(2, N-2)
            strength = np.random.uniform(0.5, 1.0)
            for i in range(N):
                for j in range(N):
                    dist = np.sqrt((i - cx)**2 + (j - cy)**2) / N
                    anchor[i, j] += strength * np.exp(-dist**2 / 0.05)
        anchor = anchor / anchor.max() * 0.8
        
    elif prompt_type == "factual":
        # Factual: single strong attractor (low entropy, focused)
        cx, cy = N // 2, N // 2
        for i in range(N):
            for j in range(N):
                dist = np.sqrt((i - cx)**2 + (j - cy)**2) / N
                anchor[i, j] = np.exp(-dist**2 / 0.1)
        anchor = anchor * 1.2
        
    elif prompt_type == "qa":
        # Q&A: question pattern → answer region
        # Question tokens (top half)
        for i in range(N // 3):
            for j in range(N):
                anchor[i, j] = 0.5 * np.sin(j * np.pi / N)**2
        # Answer region (bottom, needs to fill)
        anchor[2*N//3:, :] = -0.3  # Negative = "needs filling"
        
    elif prompt_type == "code":
        # Code: structured, hierarchical patterns
        for i in range(N):
            for j in range(N):
                # Indentation structure
                if i % 4 == 0:
                    anchor[i, j] = 0.8  # High-level structure
                elif i % 2 == 0:
                    anchor[i, j] = 0.4  # Mid-level
                else:
                    anchor[i, j] = 0.2 * np.sin(j * 2 * np.pi / N)
                    
    else:  # random
        anchor = np.random.randn(N, N) * 0.3
    
    return anchor


def create_token_init(N: int, temperature: float = 0.5) -> tuple[np.ndarray, np.ndarray]:
    """
    Create initial token states.
    
    Returns:
        C0: Initial token embeddings (random)
        I0: Initial attention context (near zero)
    """
    # Tokens start as random noise (ungenerated)
    C0 = np.random.randn(N, N) * temperature
    
    # Context starts empty
    I0 = np.zeros((N, N))
    
    return C0, I0


def compute_coherence(C: np.ndarray, I: np.ndarray) -> float:
    """
    Compute coherence metric.
    High coherence = tokens align with context.
    """
    # Correlation between C and I
    corr = np.corrcoef(C.flatten(), I.flatten())[0, 1]
    return float(corr) if np.isfinite(corr) else 0.0


def compute_entropy(C: np.ndarray) -> float:
    """
    Compute entropy of token distribution.
    Lower entropy = more focused/deterministic output.
    """
    # Normalize to probability-like
    p = np.abs(C) / (np.abs(C).sum() + 1e-10)
    p = p.flatten()
    p = p[p > 1e-10]
    return float(-np.sum(p * np.log(p)))


def run_llm_simulation(C0: np.ndarray, I0: np.ndarray, anchor: np.ndarray,
                       config: dict, n_snapshots: int = 60):
    """
    Run LLM-like token generation simulation.
    """
    N = C0.shape[0]
    L = config.get("L", 10.0)
    T = config.get("T", 3.0)
    dt = config.get("dt", 0.02)
    beta = config.get("beta", 0.7)  # Attention strength
    kappa = config.get("kappa", 0.2)  # Smoothness
    temperature = config.get("temperature", 0.3)
    
    n_steps = int(T / dt)
    snapshot_every = max(1, n_steps // n_snapshots)
    
    C = C0.copy()  # Token states
    I = I0.copy()  # Context
    
    # Histories
    C_history = [C.copy()]
    I_history = [I.copy()]
    t_history = [0.0]
    coherence = [compute_coherence(C, I)]
    entropy = [compute_entropy(C)]
    anchor_align = [float(np.mean(C * anchor))]
    
    print(f"  Running LLM simulation: {N}×{N} grid, {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # Laplacian (token smoothing)
        def laplacian(f):
            return (
                np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
                np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) - 4*f
            ) * (N / L)**2
        
        lapC = laplacian(C)
        lapI = laplacian(I)
        
        # UET dynamics for LLM:
        # C (tokens) attracted to context (I) and prompt anchor
        # I (context) builds from tokens
        
        dC = (kappa * lapC 
              - C * (C**2 - 1)  # Token normalization
              - beta * (C - I)  # Attention to context
              + anchor * 0.3)  # Prompt guidance
        
        dI = (kappa * lapI * 0.5
              - I * (I**2 - 1)  
              - beta * (I - C) * 0.3  # Context builds slowly
              + temperature * np.random.randn(N, N) * 0.1)  # Stochastic sampling
        
        C = C + dt * dC
        I = I + dt * dI
        
        # Clip
        C = np.clip(C, -2, 2)
        I = np.clip(I, -2, 2)
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            I_history.append(I.copy())
            t_history.append(t)
            coherence.append(compute_coherence(C, I))
            entropy.append(compute_entropy(C))
            anchor_align.append(float(np.mean(C * anchor)))
    
    return {
        "C": C_history,
        "I": I_history,
        "t": t_history,
        "coherence": coherence,
        "entropy": entropy,
        "anchor_align": anchor_align,
    }


def make_llm_animation(case_dir: Path, history: dict, anchor: np.ndarray, 
                       fps: int = 12) -> Path:
    """Create animated visualization of LLM dynamics."""
    C_history = history["C"]
    I_history = history["I"]
    t_history = history["t"]
    
    n_frames = len(C_history)
    N = C_history[0].shape[0]
    
    c_lim = 1.5
    
    fig = plt.figure(figsize=(14, 8))
    
    def update(frame):
        fig.clear()
        
        C = C_history[frame]
        I = I_history[frame]
        t = t_history[frame]
        
        # Layout: 2x3
        ax1 = fig.add_subplot(231)  # Tokens
        ax2 = fig.add_subplot(232)  # Context
        ax3 = fig.add_subplot(233)  # Prompt anchor
        ax4 = fig.add_subplot(234)  # Coherence
        ax5 = fig.add_subplot(235)  # Entropy
        ax6 = fig.add_subplot(236)  # Token-Context diff
        
        # Token states
        im1 = ax1.imshow(C, cmap='viridis', vmin=-c_lim, vmax=c_lim)
        ax1.set_title('🔤 Token Embeddings (C)', fontsize=10)
        ax1.set_xlabel('Embedding dim')
        ax1.set_ylabel('Token position')
        
        # Context
        im2 = ax2.imshow(I, cmap='plasma', vmin=-c_lim, vmax=c_lim)
        ax2.set_title('🧠 Attention Context (I)', fontsize=10)
        ax2.set_xlabel('Embedding dim')
        
        # Anchor
        im3 = ax3.imshow(anchor, cmap='coolwarm', vmin=-1, vmax=1)
        ax3.set_title('📌 Prompt Anchor', fontsize=10)
        ax3.set_xlabel('Embedding dim')
        
        # Coherence over time
        ax4.plot(t_history[:frame+1], history["coherence"][:frame+1], 'g-', lw=2)
        ax4.set_xlim(0, t_history[-1])
        ax4.set_ylim(-0.2, 1.0)
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Coherence')
        ax4.set_title('📊 Token-Context Coherence', fontsize=10)
        ax4.grid(True, alpha=0.3)
        ax4.axhline(0, color='gray', lw=0.5)
        
        # Entropy
        ax5.plot(t_history[:frame+1], history["entropy"][:frame+1], 'r-', lw=2)
        ax5.set_xlim(0, t_history[-1])
        ax5.set_ylim(0, max(history["entropy"]) * 1.2)
        ax5.set_xlabel('Time')
        ax5.set_ylabel('Entropy')
        ax5.set_title('🎲 Output Entropy', fontsize=10)
        ax5.grid(True, alpha=0.3)
        
        # C-I difference
        diff = C - I
        im6 = ax6.imshow(diff, cmap='RdBu_r', vmin=-c_lim, vmax=c_lim)
        ax6.set_title('⚡ Token-Context Gap (C-I)', fontsize=10)
        ax6.set_xlabel('Embedding dim')
        ax6.set_ylabel('Token position')
        
        fig.suptitle(f'🤖 UET LLM Dynamics | t = {t:.2f}', fontsize=13, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "CI_evolution.gif"
    print(f"  Saving LLM animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def make_llm_summary_plot(case_dir: Path, history: dict, anchor: np.ndarray) -> Path:
    """Create summary plot."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    t = history["t"]
    
    # Final token state
    axes[0, 0].imshow(history["C"][-1], cmap='viridis')
    axes[0, 0].set_title('Final Token State')
    axes[0, 0].set_xlabel('Embedding dim')
    axes[0, 0].set_ylabel('Token position')
    
    # Coherence + Anchor alignment
    ax1 = axes[0, 1]
    ax1.plot(t, history["coherence"], 'g-', lw=2, label='Coherence')
    ax1.plot(t, history["anchor_align"], 'b--', lw=1.5, label='Prompt Align')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Score')
    ax1.set_title('Coherence & Prompt Alignment')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Entropy
    axes[1, 0].fill_between(t, 0, history["entropy"], color='red', alpha=0.3)
    axes[1, 0].plot(t, history["entropy"], 'r-', lw=2)
    axes[1, 0].set_xlabel('Time')
    axes[1, 0].set_ylabel('Entropy')
    axes[1, 0].set_title('Output Entropy Over Time')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Token evolution comparison (start vs end)
    diff = history["C"][-1] - history["C"][0]
    axes[1, 1].imshow(diff, cmap='RdBu_r')
    axes[1, 1].set_title('Token Change (Final - Initial)')
    axes[1, 1].set_xlabel('Embedding dim')
    axes[1, 1].set_ylabel('Token position')
    
    plt.tight_layout()
    
    output_path = case_dir / "llm_summary.png"
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def make_scatter_animation(case_dir: Path, history: dict, prompt_type: str, fps: int = 15) -> Path:
    """Create animated scatter plot showing Coherence vs Entropy phase space."""
    coherence = history["coherence"]
    entropy = history["entropy"]
    t = history["t"]
    
    n_frames = len(coherence)
    
    # Normalize entropy for display
    max_entropy = max(entropy)
    entropy_norm = [e / max_entropy for e in entropy]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    def update(frame):
        ax.clear()
        
        # Plot trajectory up to current frame
        if frame > 0:
            for i in range(frame):
                alpha = 0.1 + 0.9 * (i / frame)
                ax.plot(coherence[i:i+2], entropy_norm[i:i+2], 'b-', alpha=alpha, lw=1)
        
        # Current point
        ax.scatter(coherence[frame], entropy_norm[frame], s=200, c='red',
                  edgecolors='white', linewidth=2, zorder=10)
        
        # Future points (faint)
        if frame < n_frames - 1:
            ax.scatter(coherence[frame+1:], entropy_norm[frame+1:], s=10, c='gray', alpha=0.1)
        
        # Quadrant lines
        ax.axhline(0.5, color='gray', lw=0.5, alpha=0.5)
        ax.axvline(0.5, color='gray', lw=0.5, alpha=0.5)
        
        # Quadrant labels
        ax.text(0.8, 0.85, 'Creative\n(High Both)', ha='center', va='center',
               fontsize=9, alpha=0.3, fontweight='bold')
        ax.text(0.2, 0.85, 'Random\n(Low Coherence)', ha='center', va='center',
               fontsize=9, alpha=0.3, fontweight='bold')
        ax.text(0.2, 0.15, 'Noise\n(Low Both)', ha='center', va='center',
               fontsize=9, alpha=0.3, fontweight='bold')
        ax.text(0.8, 0.15, 'Focused\n(Optimal)', ha='center', va='center',
               fontsize=9, alpha=0.3, fontweight='bold', color='green')
        
        ax.set_xlim(-0.1, 1.0)
        ax.set_ylim(0, 1.0)
        ax.set_xlabel('Coherence (Token-Context Alignment)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Entropy (Normalized)', fontsize=12, fontweight='bold')
        ax.set_title(f'🤖 LLM Phase Space | {prompt_type.upper()}\nt = {t[frame]:.2f}',
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.2)
        
        # Add direction arrow
        if frame > 0:
            dx = coherence[frame] - coherence[frame-1]
            dy = entropy_norm[frame] - entropy_norm[frame-1]
            if abs(dx) > 0.001 or abs(dy) > 0.001:
                ax.arrow(coherence[frame], entropy_norm[frame], dx*2, dy*2,
                        head_width=0.02, head_length=0.01, fc='red', ec='red', alpha=0.5)
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "scatter_animation.gif"
    print(f"  Saving scatter animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def run_llm_demo(prompt_type: str, out_dir: Path, N: int = 32, T: float = 3.0):
    """Run a complete LLM demo."""
    print(f"\n🤖 Running LLM Demo: {prompt_type}")
    
    case_dir = out_dir / f"toy_llm_{prompt_type}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Create prompt anchor
    anchor = create_prompt_anchor(N, prompt_type)
    
    # Create initial states
    C0, I0 = create_token_init(N, temperature=0.5)
    
    config = {
        "L": 10.0,
        "T": T,
        "dt": 0.02,
        "beta": 0.7,
        "kappa": 0.2,
        "temperature": 0.3,
    }
    
    # Run simulation
    history = run_llm_simulation(C0, I0, anchor, config)
    
    # Save snapshots
    snapshot_dir = case_dir / "snapshots"
    snapshot_dir.mkdir(exist_ok=True)
    for i, (C, I, t) in enumerate(zip(history["C"], history["I"], history["t"])):
        np.savez(snapshot_dir / f"step_{i:04d}.npz", C=C, I=I, t=t, anchor=anchor)
    
    # Save config
    cfg = {
        "case_id": f"toy_llm_{prompt_type}",
        "model": "C_I",
        "prompt_type": prompt_type,
        "grid": {"N": N},
        "domain": {"L": config["L"]},
        "time": {"T": T, "dt": config["dt"]},
        "params": {
            "beta": config["beta"], 
            "kappa": config["kappa"],
            "temperature": config["temperature"]
        },
        "description": f"LLM simulation - {prompt_type} prompt"
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    
    # Save summary
    summary = {
        "case_id": f"toy_llm_{prompt_type}",
        "status": "PASS",
        "prompt_type": prompt_type,
        "final_coherence": float(history["coherence"][-1]),
        "final_entropy": float(history["entropy"][-1]),
        "description": f"UET LLM Dynamics - {prompt_type.upper()}"
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create visualizations
    make_llm_animation(case_dir, history, anchor)
    make_llm_summary_plot(case_dir, history, anchor)
    make_scatter_animation(case_dir, history, prompt_type)
    
    print(f"  ✅ Demo saved to: {case_dir}")
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="Run toy LLM simulation")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--prompt", default="all",
                       choices=["creative", "factual", "qa", "code", "all"],
                       help="Prompt type")
    parser.add_argument("--N", type=int, default=32, help="Grid size")
    parser.add_argument("--T", type=float, default=3.0, help="Simulation time")
    
    args = parser.parse_args()
    out_dir = Path(args.out)
    
    print("🤖 UET LLM Token Dynamics Simulation")
    print("=" * 40)
    print(f"Grid: {args.N}×{args.N} (tokens × embedding dims)")
    print(f"Time: T={args.T}")
    
    if args.prompt == "all":
        prompts = ["creative", "factual", "qa", "code"]
    else:
        prompts = [args.prompt]
    
    for prompt in prompts:
        run_llm_demo(prompt, out_dir, N=args.N, T=args.T)
    
    print("\n" + "=" * 40)
    print("✅ LLM demos complete!")
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()
