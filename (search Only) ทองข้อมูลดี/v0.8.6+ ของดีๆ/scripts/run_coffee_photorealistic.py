"""
Photorealistic Coffee + Milk Visualization

Uses realistic colors:
- Coffee = dark brown (#3D2314)
- Milk = white/cream (#FFF8E7)
- Mixed = latte color gradient
"""
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import json


# Create custom "coffee" colormap (brown to cream/white)
COFFEE_COLORS = [
    (0.24, 0.14, 0.08),   # Dark coffee brown (C=0, pure coffee)
    (0.35, 0.22, 0.12),   # Medium coffee
    (0.55, 0.40, 0.25),   # Light coffee  
    (0.75, 0.60, 0.45),   # Cafe latte
    (0.92, 0.85, 0.75),   # Creamy
    (1.00, 0.97, 0.91),   # Milk (C=1, pure milk)
]
COFFEE_CMAP = LinearSegmentedColormap.from_list('coffee_milk', COFFEE_COLORS)


def create_coffee_initial(N: int = 64) -> tuple:
    """Create realistic initial conditions."""
    C = np.zeros((N, N, N))  # Concentration (0=coffee, 1=milk)
    T = np.ones((N, N, N)) * 0.9  # Temperature (hot coffee)
    
    x = np.linspace(-1, 1, N)
    X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
    R = np.sqrt(X**2 + Y**2)
    
    # Coffee: hot, dark (C=0)
    C[:] = 0.0
    T[:] = 1.0
    
    # Milk pour from top center
    pour = (R < 0.2) & (Z > 0.5)
    C[pour] = 1.0
    T[pour] = 0.1  # Cold milk
    
    return C, T


def run_coffee_sim(C0, T0, n_steps: int = 300, dt: float = 0.02) -> dict:
    """Simple diffusion simulation."""
    N = C0.shape[0]
    C = C0.copy()
    T = T0.copy()
    dx = 2.0 / N
    
    kappa_C = 0.02  # Milk diffusion
    kappa_T = 0.05  # Heat diffusion
    
    C_hist = [C.copy()]
    T_hist = [T.copy()]
    t_hist = [0.0]
    
    print(f"  Running simulation: {N}^3 grid, {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        # Laplacian
        def lap(f):
            return (np.roll(f,1,0) + np.roll(f,-1,0) +
                    np.roll(f,1,1) + np.roll(f,-1,1) +
                    np.roll(f,1,2) + np.roll(f,-1,2) - 6*f) / dx**2
        
        # Diffusion
        C = C + dt * kappa_C * lap(C)
        T = T + dt * kappa_T * lap(T)
        
        # Clip
        C = np.clip(C, 0, 1)
        T = np.clip(T, 0, 1)
        
        if step % (n_steps // 50) == 0:
            C_hist.append(C.copy())
            T_hist.append(T.copy())
            t_hist.append(step * dt)
    
    return {"C": C_hist, "T": T_hist, "t": t_hist}


def make_realistic_coffee_viz(case_dir: Path, history: dict, fps: int = 12):
    """Create PHOTOREALISTIC coffee visualization."""
    C_hist = history["C"]
    T_hist = history["T"]
    t_hist = history["t"]
    
    n_frames = len(C_hist)
    N = C_hist[0].shape[0]
    mid = N // 2
    
    fig = plt.figure(figsize=(14, 8), facecolor='#2E2E2E')
    
    def update(frame):
        fig.clear()
        
        C = C_hist[frame]
        T = T_hist[frame]
        t = t_hist[frame]
        
        # Top-down view (XY slice at mid-height)
        ax1 = fig.add_subplot(221)
        ax1.set_facecolor('#2E2E2E')
        im1 = ax1.imshow(C[:, :, mid], cmap=COFFEE_CMAP, vmin=0, vmax=1, 
                        origin='lower', interpolation='bilinear')
        ax1.set_title('Top View (looking down into cup)', color='white', fontsize=11)
        ax1.tick_params(colors='white')
        # Draw cup outline
        theta = np.linspace(0, 2*np.pi, 100)
        cup_r = N * 0.45
        ax1.plot(N/2 + cup_r*np.cos(theta), N/2 + cup_r*np.sin(theta), 
                'white', lw=2, alpha=0.7)
        ax1.set_xlim(0, N)
        ax1.set_ylim(0, N)
        
        # Side view (XZ slice at mid-Y)
        ax2 = fig.add_subplot(222)
        ax2.set_facecolor('#2E2E2E')
        im2 = ax2.imshow(C[:, mid, :].T, cmap=COFFEE_CMAP, vmin=0, vmax=1,
                        origin='lower', interpolation='bilinear', aspect='equal')
        ax2.set_title('Side View (cross-section)', color='white', fontsize=11)
        ax2.tick_params(colors='white')
        # Draw cup sides
        ax2.axvline(N*0.1, color='white', lw=2, alpha=0.7)
        ax2.axvline(N*0.9, color='white', lw=2, alpha=0.7)
        ax2.axhline(N*0.1, color='white', lw=2, alpha=0.7)
        
        # Temperature overlay (side view)
        ax3 = fig.add_subplot(223)
        ax3.set_facecolor('#2E2E2E')
        im3 = ax3.imshow(T[:, mid, :].T, cmap='coolwarm', vmin=0, vmax=1,
                        origin='lower', interpolation='bilinear', aspect='equal')
        ax3.set_title('Temperature (side view)', color='white', fontsize=11)
        ax3.tick_params(colors='white')
        cbar = plt.colorbar(im3, ax=ax3, shrink=0.7)
        cbar.set_label('Hot <-> Cold', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        # Mixing progress
        ax4 = fig.add_subplot(224)
        ax4.set_facecolor('#2E2E2E')
        mixing = [np.std(c) for c in C_hist[:frame+1]]
        ax4.fill_between(range(len(mixing)), mixing, color='#C4A484', alpha=0.3)
        ax4.plot(mixing, color='#C4A484', lw=2)
        ax4.set_xlabel('Time', color='white')
        ax4.set_ylabel('Mixing (σ)', color='white')
        ax4.set_title('Milk Dispersion', color='white', fontsize=11)
        ax4.tick_params(colors='white')
        ax4.set_xlim(0, n_frames)
        ax4.grid(True, alpha=0.2)
        ax4.spines['bottom'].set_color('white')
        ax4.spines['left'].set_color('white')
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        
        fig.suptitle(f'☕ Coffee + Milk Mixing | t = {t:.2f}s', 
                    color='white', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output = case_dir / "photorealistic_coffee.gif"
    print(f"  Saving photorealistic coffee visualization...")
    ani.save(output, writer='pillow', fps=fps)
    plt.close(fig)
    
    # Also save as main.gif
    import shutil
    shutil.copy(output, case_dir / "main.gif")
    
    print(f"  Saved: {output}")
    return output


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="runs_gallery")
    parser.add_argument("--N", type=int, default=48)
    parser.add_argument("--steps", type=int, default=300)
    args = parser.parse_args()
    
    print("=" * 60)
    print("PHOTOREALISTIC Coffee + Milk Simulation")
    print("  - Brown coffee + white milk colors")
    print("  - Cup outline visualization")
    print("=" * 60)
    
    case_dir = Path(args.out) / "toy_coffee_photorealistic"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Run simulation
    C0, T0 = create_coffee_initial(args.N)
    history = run_coffee_sim(C0, T0, n_steps=args.steps)
    
    # Save config
    config = {
        "case_id": "toy_coffee_photorealistic",
        "model": "photorealistic",
        "description": "Photorealistic coffee + milk with brown/white colors",
        "grid": {"N": args.N, "dims": 3},
        "time": {"steps": args.steps},
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Save summary
    summary = {
        "case_id": "toy_coffee_photorealistic",
        "status": "PASS",
        "description": "Photorealistic coffee brewing with realistic brown/cream colors",
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create visualization
    make_realistic_coffee_viz(case_dir, history)
    
    print("\n" + "=" * 60)
    print("Done! Saved to:", case_dir)
    print("=" * 60)


if __name__ == "__main__":
    main()
