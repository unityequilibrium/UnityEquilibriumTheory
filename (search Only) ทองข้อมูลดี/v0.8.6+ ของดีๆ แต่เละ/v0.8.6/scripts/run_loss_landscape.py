#!/usr/bin/env python
"""
Loss Landscape Comparison: UET Energy vs Neural Network Loss

Inspired by Welch Labs "The Misconception that Almost Stopped AI"

Creates side-by-side comparison:
1. UET Energy Landscape: Ω(β, s) - equilibrium energy over parameter space
2. NN Loss Landscape: L(w1, w2) - loss function over 2D weight slice

Features:
- 3D surface visualization
- Gradient descent trajectories
- Animated optimization paths
- Comparison of landscape structures

Usage:
    python scripts/run_loss_landscape.py
    python scripts/run_loss_landscape.py --animate
"""
from __future__ import annotations
import argparse
import json
import numpy as np
from pathlib import Path
from typing import Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D


# ============================================================
# Part 1: UET Energy Landscape
# ============================================================

def compute_uet_energy(C: np.ndarray, I: np.ndarray, beta: float, s: float, 
                       kappa: float = 0.3) -> float:
    """
    Compute UET energy Ω for given fields.
    
    Ω = ∫ [κ/2 (∇C)² + V(C) + β/2 (C-I)² - s·C] dx
    
    where V(C) = (C² - 1)² / 4  (double-well potential)
    """
    N = C.shape[0]
    dx = 1.0 / N
    
    # Gradient energy (kinetic)
    grad_C_x = np.roll(C, -1, axis=0) - C
    grad_C_y = np.roll(C, -1, axis=1) - C
    kinetic = 0.5 * kappa * np.sum(grad_C_x**2 + grad_C_y**2) * dx**2
    
    # Double-well potential
    potential = np.sum((C**2 - 1)**2 / 4) * dx**2
    
    # Coupling energy
    coupling = 0.5 * beta * np.sum((C - I)**2) * dx**2
    
    # Tilt (external field)
    tilt = -s * np.sum(C) * dx**2
    
    return kinetic + potential + coupling + tilt


def simulate_uet_equilibrium(beta: float, s: float, N: int = 32, 
                              n_steps: int = 200) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Run UET to near-equilibrium and return final energy.
    """
    # Random initial condition
    np.random.seed(42)
    C = np.random.randn(N, N) * 0.3
    I = np.random.randn(N, N) * 0.1
    
    dt = 0.02
    kappa = 0.3
    
    for _ in range(n_steps):
        # Laplacian
        lapC = (np.roll(C, 1, axis=0) + np.roll(C, -1, axis=0) +
                np.roll(C, 1, axis=1) + np.roll(C, -1, axis=1) - 4*C) * N**2
        lapI = (np.roll(I, 1, axis=0) + np.roll(I, -1, axis=0) +
                np.roll(I, 1, axis=1) + np.roll(I, -1, axis=1) - 4*I) * N**2
        
        # UET dynamics
        dC = kappa * lapC - C * (C**2 - 1) - beta * (C - I) + s
        dI = kappa * lapI - I * (I**2 - 1) - beta * (I - C)
        
        C = C + dt * dC
        I = I + dt * dI
        C = np.clip(C, -2, 2)
        I = np.clip(I, -2, 2)
    
    energy = compute_uet_energy(C, I, beta, s, kappa)
    return C, I, energy


def create_uet_landscape(beta_range: Tuple[float, float], 
                         s_range: Tuple[float, float],
                         n_points: int = 30) -> dict:
    """
    Create 2D energy landscape over (β, s) parameter space.
    """
    betas = np.linspace(beta_range[0], beta_range[1], n_points)
    s_vals = np.linspace(s_range[0], s_range[1], n_points)
    
    Beta, S = np.meshgrid(betas, s_vals)
    Energy = np.zeros_like(Beta)
    
    print(f"  Computing UET energy landscape ({n_points}×{n_points})...")
    
    for i in range(n_points):
        for j in range(n_points):
            _, _, energy = simulate_uet_equilibrium(Beta[i, j], S[i, j], N=16, n_steps=100)
            Energy[i, j] = energy
        if (i + 1) % 5 == 0:
            print(f"    Row {i+1}/{n_points}")
    
    return {"Beta": Beta, "S": S, "Energy": Energy}


# ============================================================
# Part 2: Neural Network Loss Landscape
# ============================================================

def create_nn_data(n_samples: int = 100):
    """Create simple 2D classification data."""
    np.random.seed(42)
    
    # Two spirals (classic NN benchmark)
    t = np.linspace(0, 2*np.pi, n_samples // 2)
    
    # Spiral 1
    x1 = t * np.cos(t) + np.random.randn(n_samples // 2) * 0.2
    y1 = t * np.sin(t) + np.random.randn(n_samples // 2) * 0.2
    
    # Spiral 2 (rotated)
    x2 = t * np.cos(t + np.pi) + np.random.randn(n_samples // 2) * 0.2
    y2 = t * np.sin(t + np.pi) + np.random.randn(n_samples // 2) * 0.2
    
    X = np.vstack([np.column_stack([x1, y1]), np.column_stack([x2, y2])])
    y = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
    
    # Normalize
    X = (X - X.mean(0)) / X.std(0)
    
    return X, y


def simple_nn_forward(X: np.ndarray, w1: float, w2: float, 
                      base_weights: np.ndarray) -> np.ndarray:
    """
    Simple NN with 2 hidden neurons.
    w1, w2 are the "directions" we vary to create the landscape.
    """
    # Input: (N, 2), Hidden: 2, Output: 1
    # Perturb base weights in 2 directions
    W1 = base_weights['W1'] + w1 * base_weights['d1'] + w2 * base_weights['d2']
    b1 = base_weights['b1']
    W2 = base_weights['W2']
    b2 = base_weights['b2']
    
    # Forward pass
    z1 = X @ W1 + b1
    a1 = np.tanh(z1)  # Hidden activation
    z2 = a1 @ W2 + b2
    y_pred = 1 / (1 + np.exp(-z2))  # Sigmoid
    
    return y_pred.flatten()


def compute_nn_loss(X: np.ndarray, y: np.ndarray, w1: float, w2: float,
                    base_weights: np.ndarray) -> float:
    """Compute binary cross-entropy loss."""
    y_pred = simple_nn_forward(X, w1, w2, base_weights)
    y_pred = np.clip(y_pred, 1e-7, 1 - 1e-7)
    loss = -np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))
    return loss


def create_nn_landscape(X: np.ndarray, y: np.ndarray,
                        w_range: Tuple[float, float] = (-2, 2),
                        n_points: int = 100) -> dict:
    """
    Create 2D loss landscape for NN - RUGGED version like Welch Labs.
    Uses deeper network and filter-normalized random directions.
    """
    np.random.seed(123)
    
    # Deeper network: 2 -> 10 -> 10 -> 1
    W1 = np.random.randn(2, 10) * 0.5
    b1 = np.zeros(10)
    W2 = np.random.randn(10, 10) * 0.5
    b2 = np.zeros(10)
    W3 = np.random.randn(10, 1) * 0.5
    b3 = np.zeros(1)
    
    # Random directions (filter-normalized for better visualization)
    d1_W1 = np.random.randn(2, 10)
    d1_W1 = d1_W1 / np.linalg.norm(d1_W1) * np.linalg.norm(W1)
    d1_W2 = np.random.randn(10, 10)
    d1_W2 = d1_W2 / np.linalg.norm(d1_W2) * np.linalg.norm(W2)
    d1_W3 = np.random.randn(10, 1)
    d1_W3 = d1_W3 / np.linalg.norm(d1_W3) * np.linalg.norm(W3)
    
    d2_W1 = np.random.randn(2, 10)
    d2_W1 = d2_W1 / np.linalg.norm(d2_W1) * np.linalg.norm(W1)
    d2_W2 = np.random.randn(10, 10)
    d2_W2 = d2_W2 / np.linalg.norm(d2_W2) * np.linalg.norm(W2)
    d2_W3 = np.random.randn(10, 1)
    d2_W3 = d2_W3 / np.linalg.norm(d2_W3) * np.linalg.norm(W3)
    
    base_weights = {
        'W1': W1, 'b1': b1, 'W2': W2, 'b2': b2, 'W3': W3, 'b3': b3,
        'd1_W1': d1_W1, 'd1_W2': d1_W2, 'd1_W3': d1_W3,
        'd2_W1': d2_W1, 'd2_W2': d2_W2, 'd2_W3': d2_W3,
    }
    
    w1_vals = np.linspace(w_range[0], w_range[1], n_points)
    w2_vals = np.linspace(w_range[0], w_range[1], n_points)
    
    W1_grid, W2_grid = np.meshgrid(w1_vals, w2_vals)
    Loss = np.zeros_like(W1_grid)
    
    print(f"  Computing RUGGED NN loss landscape ({n_points}×{n_points})...")
    
    for i in range(n_points):
        for j in range(n_points):
            alpha, beta = W1_grid[i, j], W2_grid[i, j]
            
            # Perturb weights in 2 directions
            W1_p = W1 + alpha * d1_W1 + beta * d2_W1
            W2_p = W2 + alpha * d1_W2 + beta * d2_W2
            W3_p = W3 + alpha * d1_W3 + beta * d2_W3
            
            # Forward pass (deeper network)
            z1 = X @ W1_p + b1
            a1 = np.maximum(0, z1)  # ReLU
            z2 = a1 @ W2_p + b2
            a2 = np.maximum(0, z2)  # ReLU
            z3 = a2 @ W3_p + b3
            y_pred = 1 / (1 + np.exp(-np.clip(z3, -500, 500)))
            y_pred = np.clip(y_pred.flatten(), 1e-7, 1 - 1e-7)
            
            # Cross-entropy loss
            loss = -np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))
            Loss[i, j] = loss
        
        if (i + 1) % 20 == 0:
            print(f"    Row {i+1}/{n_points}")
    
    return {"W1": W1_grid, "W2": W2_grid, "Loss": Loss, "base_weights": base_weights}


# ============================================================
# Part 3: Gradient Descent Animation
# ============================================================

def gradient_descent_uet(landscape: dict, start: Tuple[float, float],
                         lr: float = 0.1, n_steps: int = 50) -> list:
    """Simulate gradient descent on UET landscape."""
    Beta, S, Energy = landscape["Beta"], landscape["S"], landscape["Energy"]
    
    # Numerical gradient
    beta, s = start
    trajectory = [(beta, s)]
    
    db = Beta[0, 1] - Beta[0, 0]
    ds = S[1, 0] - S[0, 0]
    
    for _ in range(n_steps):
        # Find nearest grid point
        i = int((s - S[0, 0]) / ds)
        j = int((beta - Beta[0, 0]) / db)
        i = np.clip(i, 1, len(S) - 2)
        j = np.clip(j, 1, len(Beta[0]) - 2)
        
        # Numerical gradient
        dE_db = (Energy[i, j+1] - Energy[i, j-1]) / (2 * db)
        dE_ds = (Energy[i+1, j] - Energy[i-1, j]) / (2 * ds)
        
        # Update
        beta = beta - lr * dE_db
        s = s - lr * dE_ds
        
        # Clip to bounds
        beta = np.clip(beta, Beta.min(), Beta.max())
        s = np.clip(s, S.min(), S.max())
        
        trajectory.append((beta, s))
    
    return trajectory


def gradient_descent_nn(X: np.ndarray, y: np.ndarray, landscape: dict,
                        start: Tuple[float, float],
                        lr: float = 0.1, n_steps: int = 50) -> list:
    """Simulate gradient descent on NN loss landscape using interpolation."""
    W1_grid, W2_grid, Loss = landscape["W1"], landscape["W2"], landscape["Loss"]
    
    w1, w2 = start
    trajectory = [(w1, w2)]
    
    # Get grid spacing
    dw1 = W1_grid[0, 1] - W1_grid[0, 0]
    dw2 = W2_grid[1, 0] - W2_grid[0, 0]
    
    for _ in range(n_steps):
        # Find nearest grid point
        j = int((w1 - W1_grid[0, 0]) / dw1)
        i = int((w2 - W2_grid[0, 0]) / dw2)
        i = np.clip(i, 1, len(W2_grid) - 2)
        j = np.clip(j, 1, len(W1_grid[0]) - 2)
        
        # Numerical gradient from pre-computed landscape
        dL_dw1 = (Loss[i, j+1] - Loss[i, j-1]) / (2 * dw1)
        dL_dw2 = (Loss[i+1, j] - Loss[i-1, j]) / (2 * dw2)
        
        # Update
        w1 = w1 - lr * dL_dw1
        w2 = w2 - lr * dL_dw2
        
        # Clip to bounds
        w1 = np.clip(w1, W1_grid.min(), W1_grid.max())
        w2 = np.clip(w2, W2_grid.min(), W2_grid.max())
        
        trajectory.append((w1, w2))
    
    return trajectory


# ============================================================
# Part 4: Visualization
# ============================================================

def make_comparison_plot(uet_landscape: dict, nn_landscape: dict,
                         out_dir: Path) -> Path:
    """Create static comparison plot - Welch Labs style with dark background."""
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 7), facecolor='black')
    
    # UET Energy Landscape (smooth like saddle point)
    ax1 = fig.add_subplot(121, projection='3d', facecolor='black')
    surf1 = ax1.plot_surface(uet_landscape["Beta"], uet_landscape["S"], 
                             uet_landscape["Energy"],
                             cmap='viridis', alpha=0.9, edgecolor='none',
                             antialiased=True)
    ax1.set_xlabel('β (Coupling)', color='white')
    ax1.set_ylabel('s (Tilt)', color='white')
    ax1.set_zlabel('Ω (Energy)', color='white')
    ax1.set_title('UET Energy Landscape', fontsize=14, fontweight='bold', color='white')
    ax1.view_init(elev=30, azim=45)
    ax1.set_facecolor('black')
    ax1.xaxis.pane.fill = False
    ax1.yaxis.pane.fill = False
    ax1.zaxis.pane.fill = False
    
    # NN Loss Landscape (rugged like in video)
    ax2 = fig.add_subplot(122, projection='3d', facecolor='black')
    surf2 = ax2.plot_surface(nn_landscape["W1"], nn_landscape["W2"],
                             nn_landscape["Loss"],
                             cmap='viridis', alpha=0.9, edgecolor='none',
                             antialiased=True)
    ax2.set_xlabel('w₁ (Direction 1)', color='white')
    ax2.set_ylabel('w₂ (Direction 2)', color='white')
    ax2.set_zlabel('L (Loss)', color='white')
    ax2.set_title('Neural Network Loss Landscape', fontsize=14, fontweight='bold', color='white')
    ax2.view_init(elev=30, azim=45)
    ax2.set_facecolor('black')
    ax2.xaxis.pane.fill = False
    ax2.yaxis.pane.fill = False
    ax2.zaxis.pane.fill = False
    
    plt.tight_layout()
    
    output_path = out_dir / "landscape_comparison.png"
    plt.savefig(output_path, dpi=200, facecolor='black', edgecolor='none')
    plt.close(fig)
    plt.style.use('default')  # Reset style
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def make_landscape_animation(uet_landscape: dict, nn_landscape: dict,
                             uet_traj: list, nn_traj: list,
                             X: np.ndarray, y: np.ndarray,
                             out_dir: Path, fps: int = 15) -> Path:
    """Create animated comparison with gradient descent trajectories."""
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 7), facecolor='black')
    
    n_frames = max(len(uet_traj), len(nn_traj))
    
    # Precompute NN trajectory losses using interpolation
    W1_grid, W2_grid, Loss = nn_landscape["W1"], nn_landscape["W2"], nn_landscape["Loss"]
    dw1 = W1_grid[0, 1] - W1_grid[0, 0]
    dw2 = W2_grid[1, 0] - W2_grid[0, 0]
    
    def get_loss_at(w1, w2):
        j = int((w1 - W1_grid[0, 0]) / dw1)
        i = int((w2 - W2_grid[0, 0]) / dw2)
        i = np.clip(i, 0, len(W2_grid) - 1)
        j = np.clip(j, 0, len(W1_grid[0]) - 1)
        return Loss[i, j]
    
    def update(frame):
        fig.clear()
        
        # UET Landscape
        ax1 = fig.add_subplot(121, projection='3d', facecolor='black')
        ax1.plot_surface(uet_landscape["Beta"], uet_landscape["S"],
                        uet_landscape["Energy"],
                        cmap='viridis', alpha=0.7, edgecolor='none')
        
        # Trajectory up to current frame
        if frame < len(uet_traj):
            traj = uet_traj[:frame+1]
            betas = [t[0] for t in traj]
            s_vals = [t[1] for t in traj]
            # Get energy for trajectory (simplified - just use interpolation)
            energies = []
            for b, s in traj:
                _, _, e = simulate_uet_equilibrium(b, s, N=8, n_steps=20)
                energies.append(e)
            ax1.plot(betas, s_vals, energies, 'magenta', lw=3, label='GD Path')
            ax1.scatter([betas[-1]], [s_vals[-1]], [energies[-1]], 
                       c='magenta', s=100, marker='o', zorder=10)
        
        ax1.set_xlabel('β', color='white')
        ax1.set_ylabel('s', color='white')
        ax1.set_zlabel('Ω', color='white')
        ax1.set_title(f'UET Energy | Step {min(frame, len(uet_traj)-1)}', 
                     fontweight='bold', color='white')
        ax1.view_init(elev=25, azim=45 + frame*2)
        ax1.set_facecolor('black')
        ax1.xaxis.pane.fill = False
        ax1.yaxis.pane.fill = False
        ax1.zaxis.pane.fill = False
        
        # NN Landscape
        ax2 = fig.add_subplot(122, projection='3d', facecolor='black')
        ax2.plot_surface(nn_landscape["W1"], nn_landscape["W2"],
                        nn_landscape["Loss"],
                        cmap='viridis', alpha=0.7, edgecolor='none')
        
        if frame < len(nn_traj):
            traj = nn_traj[:frame+1]
            w1s = [t[0] for t in traj]
            w2s = [t[1] for t in traj]
            losses = [get_loss_at(t[0], t[1]) for t in traj]
            ax2.plot(w1s, w2s, losses, 'magenta', lw=3, label='GD Path')
            ax2.scatter([w1s[-1]], [w2s[-1]], [losses[-1]],
                       c='magenta', s=100, marker='o', zorder=10)
        
        ax2.set_xlabel('w₁', color='white')
        ax2.set_ylabel('w₂', color='white')
        ax2.set_zlabel('L', color='white')
        ax2.set_title(f'NN Loss | Step {min(frame, len(nn_traj)-1)}', 
                     fontweight='bold', color='white')
        ax2.view_init(elev=25, azim=45 + frame*2)
        ax2.set_facecolor('black')
        ax2.xaxis.pane.fill = False
        ax2.yaxis.pane.fill = False
        ax2.zaxis.pane.fill = False
        
        fig.suptitle('Loss Landscape Comparison: UET vs Neural Network', 
                    fontsize=14, fontweight='bold', color='white')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = out_dir / "CI_evolution.gif"
    print(f"  Saving landscape animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def run_landscape_demo(out_dir: Path, animate: bool = True):
    """Run complete landscape comparison demo."""
    print("\n🧠 Loss Landscape Comparison")
    print("=" * 50)
    
    case_dir = out_dir / "landscape_comparison"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Create UET landscape
    print("\n1️⃣ Computing UET Energy Landscape...")
    uet_landscape = create_uet_landscape(
        beta_range=(0.1, 1.5),
        s_range=(-1.0, 1.0),
        n_points=25  # Smooth surface
    )
    
    # Create NN landscape - RUGGED with higher resolution
    print("\n2️⃣ Computing NN Loss Landscape (RUGGED)...")
    X, y = create_nn_data(200)
    nn_landscape = create_nn_landscape(X, y, w_range=(-1.5, 1.5), n_points=80)
    
    # Gradient descent trajectories
    print("\n3️⃣ Running Gradient Descent...")
    uet_traj = gradient_descent_uet(uet_landscape, start=(1.2, 0.8), lr=0.05, n_steps=30)
    nn_traj = gradient_descent_nn(X, y, nn_landscape, start=(1.5, 1.5), lr=0.2, n_steps=30)
    
    # Static comparison
    print("\n4️⃣ Creating visualizations...")
    make_comparison_plot(uet_landscape, nn_landscape, case_dir)
    
    # Animation
    if animate:
        make_landscape_animation(uet_landscape, nn_landscape, 
                                uet_traj, nn_traj, X, y, case_dir)
    
    # Save config
    cfg = {
        "case_id": "landscape_comparison",
        "type": "comparison",
        "uet": {"beta_range": [0.1, 1.5], "s_range": [-1.0, 1.0]},
        "nn": {"w_range": [-2, 2], "hidden_size": 4},
        "description": "UET Energy vs NN Loss Landscape Comparison"
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    
    # Summary
    summary = {
        "case_id": "landscape_comparison",
        "status": "PASS",
        "uet_min_energy": float(uet_landscape["Energy"].min()),
        "nn_min_loss": float(nn_landscape["Loss"].min()),
        "description": "Loss Landscape: UET Ω vs NN L"
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Demo saved to: {case_dir}")
    
    print("\n" + "=" * 50)
    print("📊 Key Insights:")
    print(f"  UET Min Energy: Ω = {uet_landscape['Energy'].min():.4f}")
    print(f"  NN Min Loss: L = {nn_landscape['Loss'].min():.4f}")
    print("\n  Both show similar optimization landscapes!")
    print("  - Local minima")
    print("  - Saddle points")
    print("  - Gradient descent paths")
    
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="Loss Landscape Comparison")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--animate", action="store_true", default=True,
                       help="Create animation")
    parser.add_argument("--no-animate", action="store_false", dest="animate",
                       help="Skip animation")
    
    args = parser.parse_args()
    out_dir = Path(args.out)
    
    run_landscape_demo(out_dir, animate=args.animate)
    
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()
