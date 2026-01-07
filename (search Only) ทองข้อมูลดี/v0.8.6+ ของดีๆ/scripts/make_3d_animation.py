#!/usr/bin/env python
"""
3D Surface Animation Generator.
Creates rotating 3D terrain animations from 2D field snapshots.

Usage:
    python scripts/make_3d_animation.py runs_gallery/toy_coffee_milk_mixing
    python scripts/make_3d_animation.py runs_gallery/BIAS_C --rotate
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


def load_snapshots(case_dir: Path) -> tuple[list, list, list]:
    """Load all snapshots from a case directory."""
    snapshot_dir = case_dir / "snapshots"
    if not snapshot_dir.exists():
        raise FileNotFoundError(f"No snapshots in {case_dir}")
    
    npz_files = sorted(snapshot_dir.glob("step_*.npz"), 
                       key=lambda p: int(p.stem.split("_")[1]))
    
    if not npz_files:
        raise FileNotFoundError(f"No step_*.npz files in {snapshot_dir}")
    
    C_list, I_list, t_list = [], [], []
    for npz_path in npz_files:
        data = np.load(npz_path)
        C_list.append(data["C"])
        I_list.append(data.get("I", np.zeros_like(data["C"])))
        t_list.append(float(data.get("t", 0)))
    
    return C_list, I_list, t_list


def make_3d_surface_gif(case_dir: Path, field: str = "C", rotate: bool = True, 
                         fps: int = 15, elev: float = 30) -> Path:
    """
    Create a 3D surface animation GIF.
    
    Args:
        case_dir: Directory containing snapshots
        field: "C", "I", or "combined" (C-I energy)
        rotate: Whether to rotate the view during animation
        fps: Frames per second
        elev: Elevation angle
    """
    print(f"📦 Loading snapshots from {case_dir}...")
    C_list, I_list, t_list = load_snapshots(case_dir)
    
    n_frames = len(C_list)
    N = C_list[0].shape[0]
    
    # Create meshgrid
    x = np.linspace(0, 1, N)
    y = np.linspace(0, 1, N)
    X, Y = np.meshgrid(x, y)
    
    # Get data based on field choice
    if field == "C":
        data_list = C_list
        title = "C Field"
        cmap = 'coolwarm'
    elif field == "I":
        data_list = I_list
        title = "I Field"
        cmap = 'RdYlBu_r'
    else:  # combined
        data_list = [C - I for C, I in zip(C_list, I_list)]
        title = "C - I (Difference)"
        cmap = 'seismic'
    
    # Get global z limits
    z_min = min(d.min() for d in data_list)
    z_max = max(d.max() for d in data_list)
    z_range = z_max - z_min
    if z_range < 0.1:
        z_range = 1.0
    
    print(f"🎨 Creating 3D animation ({n_frames} frames)...")
    
    # Create figure
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Initial surface
    surf = ax.plot_surface(X, Y, data_list[0], cmap=cmap, 
                           vmin=z_min, vmax=z_max,
                           linewidth=0, antialiased=True, alpha=0.9)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel(field)
    ax.set_zlim(z_min - 0.1*z_range, z_max + 0.1*z_range)
    ax.set_title(f'{title} | t=0.00')
    
    # Color bar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label=field)
    
    def update(frame):
        ax.clear()
        
        # Rotation angle
        if rotate:
            azim = 45 + frame * (360 / n_frames)  # Full rotation
        else:
            azim = 45
        
        ax.view_init(elev=elev, azim=azim)
        
        # Plot surface
        surf = ax.plot_surface(X, Y, data_list[frame], cmap=cmap,
                               vmin=z_min, vmax=z_max,
                               linewidth=0, antialiased=True, alpha=0.9)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel(field)
        ax.set_zlim(z_min - 0.1*z_range, z_max + 0.1*z_range)
        ax.set_title(f'{title} | t={t_list[frame]:.2f}')
        
        return [surf]
    
    # Create animation
    ani = animation.FuncAnimation(
        fig, update, frames=n_frames, interval=1000//fps, blit=False
    )
    
    # Save
    output_name = f"3D_{field}_rotate.gif" if rotate else f"3D_{field}.gif"
    output_path = case_dir / output_name
    
    print(f"💾 Saving animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"✅ Saved: {output_path}")
    return output_path


def make_combined_3d_gif(case_dir: Path, fps: int = 12) -> Path:
    """Create a dual 3D view with both C and I fields rotating."""
    print(f"📦 Loading snapshots from {case_dir}...")
    C_list, I_list, t_list = load_snapshots(case_dir)
    
    n_frames = len(C_list)
    N = C_list[0].shape[0]
    
    x = np.linspace(0, 1, N)
    y = np.linspace(0, 1, N)
    X, Y = np.meshgrid(x, y)
    
    # Get global limits
    c_min, c_max = min(c.min() for c in C_list), max(c.max() for c in C_list)
    i_min, i_max = min(i.min() for i in I_list), max(i.max() for i in I_list)
    
    print(f"🎨 Creating dual 3D animation ({n_frames} frames)...")
    
    fig = plt.figure(figsize=(14, 6))
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')
    
    def update(frame):
        ax1.clear()
        ax2.clear()
        
        azim = 45 + frame * (360 / n_frames)
        elev = 25 + 10 * np.sin(frame * 2 * np.pi / n_frames)  # Gentle bob
        
        ax1.view_init(elev=elev, azim=azim)
        ax2.view_init(elev=elev, azim=azim)
        
        # C field (coffee - warm colors)
        ax1.plot_surface(X, Y, C_list[frame], cmap='YlOrRd',
                        vmin=c_min, vmax=c_max, alpha=0.9)
        ax1.set_title(f'C (Coffee) | t={t_list[frame]:.2f}')
        ax1.set_zlim(c_min, c_max)
        ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('C')
        
        # I field (milk - cool colors)
        ax2.plot_surface(X, Y, I_list[frame], cmap='YlGnBu',
                        vmin=i_min, vmax=i_max, alpha=0.9)
        ax2.set_title(f'I (Milk) | t={t_list[frame]:.2f}')
        ax2.set_zlim(i_min, i_max)
        ax2.set_xlabel('X'); ax2.set_ylabel('Y'); ax2.set_zlabel('I')
        
        fig.suptitle('☕ UET Coffee Dynamics - 3D Evolution', fontsize=14, fontweight='bold')
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "3D_dual_rotate.gif"
    print(f"💾 Saving animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"✅ Saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Create 3D rotating surface animation")
    parser.add_argument("case_dir", help="Case directory with snapshots")
    parser.add_argument("--field", choices=["C", "I", "combined"], default="C",
                       help="Which field to visualize")
    parser.add_argument("--rotate", action="store_true", default=True,
                       help="Rotate view during animation")
    parser.add_argument("--no-rotate", action="store_false", dest="rotate")
    parser.add_argument("--fps", type=int, default=12, help="Frames per second")
    parser.add_argument("--dual", action="store_true", 
                       help="Create dual view with both C and I")
    
    args = parser.parse_args()
    case_dir = Path(args.case_dir)
    
    if args.dual:
        make_combined_3d_gif(case_dir, fps=args.fps)
    else:
        make_3d_surface_gif(case_dir, args.field, args.rotate, args.fps)


if __name__ == "__main__":
    main()
