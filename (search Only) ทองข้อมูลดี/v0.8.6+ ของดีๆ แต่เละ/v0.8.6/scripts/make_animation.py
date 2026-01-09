#!/usr/bin/env python
"""
Generate GIF animations from UET field snapshots.

Usage:
    python make_animation.py <case_dir> [--fps 10] [--field C]
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import TwoSlopeNorm


def load_snapshots(case_dir: Path) -> tuple[list[np.ndarray], list[np.ndarray], list[float]]:
    """Load all snapshots from a case directory."""
    snapshot_dir = case_dir / "snapshots"
    if not snapshot_dir.exists():
        raise FileNotFoundError(f"No snapshots directory found in {case_dir}")
    
    npz_files = sorted(snapshot_dir.glob("step_*.npz"), key=lambda p: int(p.stem.split("_")[1]))
    
    C_list = []
    I_list = []
    t_list = []
    
    for npz_path in npz_files:
        data = np.load(npz_path)
        C_list.append(data["C"])
        if "I" in data:
            I_list.append(data["I"])
        t_list.append(float(data["t"]))
    
    return C_list, I_list, t_list


def make_field_gif(
    case_dir: Path,
    field: str = "C",
    fps: int = 10,
    output_name: str = None,
) -> Path:
    """
    Create GIF animation of field evolution.
    
    Args:
        case_dir: Path to case directory with snapshots
        field: "C", "I", or "both"
        fps: Frames per second
        output_name: Output filename (default: {field}_evolution.gif)
        
    Returns:
        Path to generated GIF
    """
    C_list, I_list, t_list = load_snapshots(case_dir)
    
    if not C_list:
        raise ValueError("No snapshots found")
    
    output_name = output_name or f"{field}_evolution.gif"
    output_path = case_dir / output_name
    
    # Determine global min/max for consistent colorbar
    if field == "C":
        all_data = np.concatenate([c.flatten() for c in C_list])
    elif field == "I" and I_list:
        all_data = np.concatenate([i.flatten() for i in I_list])
    else:
        all_data = np.concatenate([c.flatten() for c in C_list])
    
    vmin, vmax = all_data.min(), all_data.max()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Use diverging colormap centered at 0
    if vmin < 0 < vmax:
        norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
    else:
        norm = None
    
    # Initial frame
    if field == "C":
        data = C_list[0]
    elif field == "I" and I_list:
        data = I_list[0]
    else:
        data = C_list[0]
    
    im = ax.imshow(data, cmap="RdBu_r", norm=norm, vmin=vmin, vmax=vmax, origin="lower")
    title = ax.set_title(f"{field} at t=0.00")
    plt.colorbar(im, ax=ax, label=field)
    
    def update(frame):
        if field == "C":
            data = C_list[frame]
        elif field == "I" and I_list:
            data = I_list[frame]
        else:
            data = C_list[frame]
        
        im.set_array(data)
        title.set_text(f"{field} at t={t_list[frame]:.2f}")
        return [im, title]
    
    ani = animation.FuncAnimation(
        fig, update, frames=len(C_list), interval=1000//fps, blit=True
    )
    
    ani.save(output_path, writer="pillow", fps=fps)
    plt.close(fig)
    
    print(f"✅ Saved: {output_path}")
    return output_path


def make_dual_gif(case_dir: Path, fps: int = 10) -> Path:
    """Create side-by-side C and I animation."""
    C_list, I_list, t_list = load_snapshots(case_dir)
    
    if not I_list:
        print("No I field found, making C-only animation")
        return make_field_gif(case_dir, "C", fps)
    
    output_path = case_dir / "CI_evolution.gif"
    
    # Global ranges
    C_all = np.concatenate([c.flatten() for c in C_list])
    I_all = np.concatenate([i.flatten() for i in I_list])
    vmin_C, vmax_C = C_all.min(), C_all.max()
    vmin_I, vmax_I = I_all.min(), I_all.max()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    im1 = ax1.imshow(C_list[0], cmap="RdBu_r", vmin=vmin_C, vmax=vmax_C, origin="lower")
    ax1.set_title("C (Conscience)")
    plt.colorbar(im1, ax=ax1)
    
    im2 = ax2.imshow(I_list[0], cmap="RdBu_r", vmin=vmin_I, vmax=vmax_I, origin="lower")
    ax2.set_title("I (Instinct)")
    plt.colorbar(im2, ax=ax2)
    
    suptitle = fig.suptitle(f"t = 0.00")
    
    def update(frame):
        im1.set_array(C_list[frame])
        im2.set_array(I_list[frame])
        suptitle.set_text(f"t = {t_list[frame]:.2f}")
        return [im1, im2, suptitle]
    
    ani = animation.FuncAnimation(
        fig, update, frames=len(C_list), interval=1000//fps, blit=True
    )
    
    ani.save(output_path, writer="pillow", fps=fps)
    plt.close(fig)
    
    print(f"✅ Saved: {output_path}")
    return output_path


def make_omega_gif(case_dir: Path, fps: int = 10) -> Path:
    """Create Omega energy density evolution animation."""
    C_list, I_list, t_list = load_snapshots(case_dir)
    
    output_path = case_dir / "omega_density_evolution.gif"
    
    # Load potential parameters from config
    config_path = case_dir / "config.json"
    import json
    with open(config_path) as f:
        config = json.load(f)
    
    params = config.get("params", {})
    a = params.get("a", -1.0)
    delta = params.get("delta", 0.0)
    b = params.get("b", 1.0)
    
    # Simple density: V(C) only
    def V(u):
        return 0.5 * a * (u - delta)**2 + 0.25 * b * (u - delta)**4
    
    omega_list = [V(c) for c in C_list]
    all_omega = np.concatenate([o.flatten() for o in omega_list])
    vmin, vmax = all_omega.min(), all_omega.max()
    
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(omega_list[0], cmap="viridis", vmin=vmin, vmax=vmax, origin="lower")
    title = ax.set_title("Ω density at t=0.00")
    plt.colorbar(im, ax=ax, label="Ω density")
    
    def update(frame):
        im.set_array(omega_list[frame])
        title.set_text(f"Ω density at t={t_list[frame]:.2f}")
        return [im, title]
    
    ani = animation.FuncAnimation(
        fig, update, frames=len(C_list), interval=1000//fps, blit=True
    )
    
    ani.save(output_path, writer="pillow", fps=fps)
    plt.close(fig)
    
    print(f"✅ Saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate GIF animations from UET snapshots")
    parser.add_argument("case_dir", help="Path to case directory with snapshots")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second")
    parser.add_argument("--field", choices=["C", "I", "both", "omega"], default="both",
                        help="Which field to animate")
    
    args = parser.parse_args()
    case_dir = Path(args.case_dir)
    
    if args.field == "both":
        make_dual_gif(case_dir, args.fps)
    elif args.field == "omega":
        make_omega_gif(case_dir, args.fps)
    else:
        make_field_gif(case_dir, args.field, args.fps)


if __name__ == "__main__":
    main()
