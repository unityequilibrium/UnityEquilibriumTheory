#!/usr/bin/env python
"""
Scatter/Phase Space Visualization for UET fields.
Creates scatter plot visualizations instead of heatmaps.

Usage:
    python scripts/make_scatter_viz.py runs_gallery/toy_coffee_milk_mixing
    python scripts/make_scatter_viz.py runs_gallery/BIAS_C --animate
"""
from __future__ import annotations
import argparse
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D


def load_snapshot(case_dir: Path, step: int = None) -> tuple:
    """Load a single snapshot."""
    snapshot_dir = case_dir / "snapshots"
    if not snapshot_dir.exists():
        raise FileNotFoundError(f"No snapshots in {case_dir}")
    
    npz_files = sorted(snapshot_dir.glob("step_*.npz"))
    if not npz_files:
        raise FileNotFoundError(f"No step_*.npz files")
    
    # Use middle snapshot if not specified
    if step is None:
        step = len(npz_files) // 2
    
    data = np.load(npz_files[min(step, len(npz_files)-1)])
    return data["C"], data.get("I", np.zeros_like(data["C"])), float(data.get("t", 0))


def load_all_snapshots(case_dir: Path) -> tuple:
    """Load all snapshots."""
    snapshot_dir = case_dir / "snapshots"
    npz_files = sorted(snapshot_dir.glob("step_*.npz"))
    
    C_list, I_list, t_list = [], [], []
    for f in npz_files:
        data = np.load(f)
        C_list.append(data["C"])
        I_list.append(data.get("I", np.zeros_like(data["C"])))
        t_list.append(float(data.get("t", 0)))
    
    return C_list, I_list, t_list


def make_scatter_plot(case_dir: Path, step: int = None) -> Path:
    """Create static scatter visualization."""
    C, I, t = load_snapshot(case_dir, step)
    N = C.shape[0]
    
    fig = plt.figure(figsize=(15, 5))
    
    # 1. Phase space: C vs I
    ax1 = fig.add_subplot(131)
    colors = np.linspace(0, 1, N*N)
    scatter = ax1.scatter(C.flatten(), I.flatten(), c=colors, cmap='viridis', 
                          alpha=0.5, s=15, edgecolors='none')
    ax1.set_xlabel('C value', fontsize=11)
    ax1.set_ylabel('I value', fontsize=11)
    ax1.set_title('Phase Space (C vs I)', fontsize=12, fontweight='bold')
    ax1.axhline(0, color='gray', lw=0.5, alpha=0.5)
    ax1.axvline(0, color='gray', lw=0.5, alpha=0.5)
    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-1.5, 1.5)
    ax1.grid(True, alpha=0.3)
    
    # 2. 3D scatter - C field
    ax2 = fig.add_subplot(132, projection='3d')
    X, Y = np.meshgrid(np.arange(N), np.arange(N))
    ax2.scatter(X.flatten(), Y.flatten(), C.flatten(), 
                c=C.flatten(), cmap='RdBu_r', s=8, alpha=0.7)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('C')
    ax2.set_title('3D Point Cloud (C)', fontsize=12, fontweight='bold')
    
    # 3. 3D scatter - C-I difference
    ax3 = fig.add_subplot(133, projection='3d')
    diff = C - I
    ax3.scatter(X.flatten(), Y.flatten(), diff.flatten(), 
                c=diff.flatten(), cmap='seismic', s=8, alpha=0.7)
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_zlabel('C - I')
    ax3.set_title('3D Point Cloud (C - I)', fontsize=12, fontweight='bold')
    
    fig.suptitle(f'{case_dir.name} | t = {t:.3f}', fontsize=14)
    plt.tight_layout()
    
    output_path = case_dir / "scatter_viz.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✅ Saved: {output_path}")
    return output_path


def make_scatter_animation(case_dir: Path, fps: int = 10) -> Path:
    """Create animated scatter visualization."""
    print(f"📦 Loading snapshots from {case_dir}...")
    C_list, I_list, t_list = load_all_snapshots(case_dir)
    
    n_frames = len(C_list)
    N = C_list[0].shape[0]
    X, Y = np.meshgrid(np.arange(N), np.arange(N))
    
    # Get global limits
    c_min = min(c.min() for c in C_list)
    c_max = max(c.max() for c in C_list)
    
    print(f"🎨 Creating scatter animation ({n_frames} frames)...")
    
    fig = plt.figure(figsize=(14, 5))
    
    def update(frame):
        fig.clear()
        
        C = C_list[frame]
        I = I_list[frame]
        t = t_list[frame]
        
        # 1. Phase space
        ax1 = fig.add_subplot(131)
        ax1.scatter(C.flatten(), I.flatten(), c=np.linspace(0, 1, N*N), 
                   cmap='viridis', alpha=0.5, s=10)
        ax1.set_xlabel('C value')
        ax1.set_ylabel('I value')
        ax1.set_title('Phase Space')
        ax1.set_xlim(c_min - 0.2, c_max + 0.2)
        ax1.set_ylim(c_min - 0.2, c_max + 0.2)
        ax1.axhline(0, color='gray', lw=0.5)
        ax1.axvline(0, color='gray', lw=0.5)
        ax1.grid(True, alpha=0.3)
        
        # 2. 3D C field
        ax2 = fig.add_subplot(132, projection='3d')
        ax2.scatter(X.flatten(), Y.flatten(), C.flatten(), 
                   c=C.flatten(), cmap='RdBu_r', s=5, alpha=0.7)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('C')
        ax2.set_title('C Field')
        ax2.set_zlim(c_min, c_max)
        
        # 3. 3D rotating view
        ax3 = fig.add_subplot(133, projection='3d')
        diff = C - I
        ax3.scatter(X.flatten(), Y.flatten(), diff.flatten(), 
                   c=diff.flatten(), cmap='seismic', s=5, alpha=0.7)
        ax3.set_xlabel('X')
        ax3.set_ylabel('Y')
        ax3.set_zlabel('C - I')
        ax3.set_title('C - I')
        ax3.view_init(elev=25, azim=45 + frame * (180 / n_frames))
        
        fig.suptitle(f'{case_dir.name} | t = {t:.3f}', fontsize=13, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "scatter_animation.gif"
    print(f"💾 Saving animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"✅ Saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Create scatter visualizations")
    parser.add_argument("case_dir", help="Case directory with snapshots")
    parser.add_argument("--step", type=int, help="Specific snapshot step")
    parser.add_argument("--animate", action="store_true", help="Create animation")
    parser.add_argument("--fps", type=int, default=10, help="FPS for animation")
    
    args = parser.parse_args()
    case_dir = Path(args.case_dir)
    
    if args.animate:
        make_scatter_animation(case_dir, fps=args.fps)
    else:
        make_scatter_plot(case_dir, step=args.step)


if __name__ == "__main__":
    main()
