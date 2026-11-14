"""
UET Visualization: Realistic GR Restoration (Topic 0.19)
========================================================
Restores the 2D Spacetime Fluid Dynamics from legacy v0.8.6.
Visualizes: 
1. Binary Inspiral (Two mass centers)
2. Singularity Collapse (Oppenheimer-Snyder analog)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.19_Gravity_GR"
OUTPUT_DIR = TOPIC_DIR / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetics
plt.style.use('dark_background')



# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def simulate_gr_scenario(scenario="binary", N=64, T=4.0, dt=0.01):
    print(f"Simulating GR Scenario: {scenario.upper()}...")
    x = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)
    
    # Heritage Parameters
    kappa = 0.4
    beta = 0.6
    
    if scenario == "binary":
        d = 0.35
        R1 = np.sqrt((X - d)**2 + Y**2)
        R2 = np.sqrt((X + d)**2 + Y**2)
        C = 0.6 * (np.exp(-R1**2/0.05) + np.exp(-R2**2/0.05))
        I = -0.5 * (np.exp(-R1**2/0.1) + np.exp(-R2**2/0.1))
    else: # collapse
        C = np.exp(-R**2/0.2) * 0.8
        I = -0.3 / (R + 0.1)
        I = np.clip(I, -1.5, 0)

    history = [C.copy()]
    
    n_steps = int(T / dt)
    for step in range(n_steps):
        t = step * dt
        lapC = (np.roll(C, 1, 0) + np.roll(C, -1, 0) + np.roll(C, 1, 1) + np.roll(C, -1, 1) - 4*C)
        
        if scenario == "binary":
            # Orbital rotation effect (approximate coriolis)
            omega_orbit = 2.0
            coriolis = 0.1 * omega_orbit * (X * np.roll(C, 1, 1) - Y * np.roll(C, 1, 0))
            dC = kappa * lapC - C*(C**2 - 1) - beta*(C - I) + coriolis
        else: # collapse
            dC = kappa * lapC - C*(C**2 - 1) - (beta + 0.2*np.exp(-t)) * (C - I)
            
        C = C + dt * dC
        C = np.clip(C, -2, 2)
        
        if step % 5 == 0:
            history.append(C.copy())
            
    return history

def animate_gr():
    for scenario in ["binary", "collapse"]:
        history = simulate_gr_scenario(scenario)
        
        print(f"Animating {scenario}...")
        fig, ax = plt.subplots(figsize=(6, 6))
        
        def update(frame):
            ax.clear()
            im = ax.imshow(history[frame], cmap='inferno', vmin=0, vmax=1.2, origin='lower')
            ax.set_title(f"Spacetime Fluid: {scenario.upper()}")
            ax.axis('off')
            return []

        ani = animation.FuncAnimation(fig, update, frames=len(history), interval=40)
        out_path = OUTPUT_DIR / f"gr_realistic_{scenario}.gif"
        ani.save(out_path, writer='pillow', fps=25)
        print(f"✅ Saved to {out_path}")
        plt.close()

if __name__ == "__main__":
    animate_gr()
