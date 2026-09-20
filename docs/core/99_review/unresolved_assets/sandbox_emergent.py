import numpy as np
import matplotlib.pyplot as plt
import os

def simulate_emergence():
    # Simulation Parameters
    N = 200        # Grid size
    dx = 1.0       # Spatial step
    dt = 0.01      # Time step
    steps = 5000   # Total steps

    # Physics Parameters
    D_C = 0.1      # Diffusion of Mass (C)
    D_I = 0.5      # Diffusion of Game Landscape (I)
    decay_I = 0.05 # How fast the game resets if empty
    beta = 1.5     # How much Mass (C^2) bends the Game (I)
    gamma = 2.0    # How strongly the Game (I) pulls the Mass (C)

    # Initial Conditions
    # Start with a small random bump of mass in the center, flat elsewhere
    x = np.linspace(-N//2, N//2, N)
    C = np.exp(-(x**2)/20) + 0.1 * np.random.rand(N) 
    I = np.zeros(N) # Game landscape starts completely flat!

    # To store history for plotting
    history_C = [C.copy()]
    history_I = [I.copy()]
    plot_steps = [0, 1000, 3000, 4999]

    for step in range(steps):
        # 1. Calculate Spatial Gradients (Laplacian)
        laplacian_C = (np.roll(C, 1) - 2*C + np.roll(C, -1)) / dx**2
        laplacian_I = (np.roll(I, 1) - 2*I + np.roll(I, -1)) / dx**2

        # 2. Emergent Equations!
        
        # Game (I) is bent by Mass (C^2)
        dI_dt = D_I * laplacian_I - decay_I * I + beta * (C**2)
        
        # Mass (C) is pulled by the Game (I) and naturally diffuses
        # Using a simple gradient flow towards high I: C * dI/dx (simplification for visual)
        grad_I = (np.roll(I, -1) - np.roll(I, 1)) / (2*dx)
        grad_C = (np.roll(C, -1) - np.roll(C, 1)) / (2*dx)
        pull_force = gamma * (C * laplacian_I + grad_C * grad_I)
        
        dC_dt = D_C * laplacian_C + pull_force

        # 3. Time Step Update
        C = C + dt * dC_dt
        I = I + dt * dI_dt

        # Prevent instability in simple explicit solver
        C = np.clip(C, 0, 10)
        I = np.clip(I, 0, 50)

        if step in plot_steps:
            history_C.append(C.copy())
            history_I.append(I.copy())

    # Generate the Visualization
    plt.figure(figsize=(12, 8))
    for idx, t in enumerate(plot_steps):
        plt.subplot(2, 2, idx+1)
        plt.plot(x, history_C[idx+1], label='Mass (C) [Players]', color='blue', linewidth=2)
        plt.plot(x, history_I[idx+1], label='Game Landscape (I) [Rules]', color='red', linestyle='--', linewidth=2)
        plt.title(f"Time Step: {t}")
        plt.xlabel("Space")
        plt.ylabel("Intensity")
        plt.legend()
        plt.grid(True)
        if idx == 0:
            plt.ylim(-0.5, 2)
        else:
            plt.ylim(-0.5, max(np.max(history_C[-1]), np.max(history_I[-1])) * 1.2)

    plt.tight_layout()
    output_path = os.path.abspath('Result/sandbox_emergence.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    print(f"Graph saved to {output_path}")

if __name__ == '__main__':
    simulate_emergence()
