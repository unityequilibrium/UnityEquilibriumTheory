"""
UET Visualization: 2D Neural Field Dynamics (Topic 0.22)
========================================================
Restoration from v0.8.6.
Visualizes the interaction of C (Excitatory) and I (Inhibitory) fields.
Logic: ∂C/∂t = κ∇²C - dV/dC - β(C - I)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.22_Biophysics_Origin_of_Life"
OUTPUT_DIR = TOPIC_DIR / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Thermodynamics / Aesthetics
plt.style.use('dark_background')



# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def run_neural_2d_sim(N=64, T=5.0, dt=0.01):
    """Simulates 2D Neural Field Dynamics."""
    print(f"Running 2D Neural Simulation ({N}x{N})...")
    
    # Parameters (v0.8.6 heritage)
    kappa = 0.3
    beta = 0.8
    
    # Initial state: Random noise in C, zero in I
    C = np.random.normal(0, 0.1, (N, N))
    I = np.zeros((N, N))
    
    # Add a "stimulus" in the center
    C[N//4:3*N//4, N//4:3*N//4] += 0.5
    
    history_C = [C.copy()]
    history_I = [I.copy()]
    
    n_steps = int(T / dt)
    for step in range(n_steps):
        # Laplacian (periodic BCs)
        lapC = (np.roll(C, 1, 0) + np.roll(C, -1, 0) + np.roll(C, 1, 1) + np.roll(C, -1, 1) - 4*C)
        lapI = (np.roll(I, 1, 0) + np.roll(I, -1, 0) + np.roll(I, 1, 1) + np.roll(I, -1, 1) - 4*I)
        
        # Potential derivative dV/dφ = φ(φ² - 1)
        dv_C = C * (C**2 - 1)
        dv_I = I * (I**2 - 1)
        
        # Dynamics
        dC = (kappa * lapC - dv_C - beta * (C - I))
        dI = (kappa * lapI - dv_I - beta * (I - C)) * 0.2 # Inhibitory is slower
        
        C = C + dt * dC
        I = I + dt * dI
        
        if step % 5 == 0:
            history_C.append(C.copy())
            history_I.append(I.copy())
            
    return history_C, history_I

def animate_neural_2d():
    history_C, history_I = run_neural_2d_sim()
    
    print("Generating Animation...")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    def update(frame):
        axes[0].clear()
        axes[1].clear()
        
        im0 = axes[0].imshow(history_C[frame], cmap='magma', vmin=-1.5, vmax=1.5)
        axes[0].set_title("Excitatory Field (C)")
        axes[0].axis('off')
        
        im1 = axes[1].imshow(history_I[frame], cmap='viridis', vmin=-1.5, vmax=1.5)
        axes[1].set_title("Inhibitory Field (I)")
        axes[1].axis('off')
        
        fig.suptitle(f"UET Neural Field Dynamics | Step {frame*5}")
        return []

    ani = animation.FuncAnimation(fig, update, frames=len(history_C), interval=50)
    
    out_path = OUTPUT_DIR / "neural_field_dynamics_2d.gif"
    ani.save(out_path, writer='pillow', fps=20)
    print(f"✅ Saved to {out_path}")
    plt.close()

if __name__ == "__main__":
    animate_neural_2d()
