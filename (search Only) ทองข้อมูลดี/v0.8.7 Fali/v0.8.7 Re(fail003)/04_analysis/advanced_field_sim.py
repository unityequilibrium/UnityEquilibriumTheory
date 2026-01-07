import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.animation import FuncAnimation

# Import UET Core logic
# We will use the math functions directly to build a custom observer loop
import sys

sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from uet_core.operators import _kgrid_1d
    from uet_core.energy import omega_CI
    from uet_core.potentials import from_dict
except ImportError as e:
    print(f"Error importing UET Core: {e}")
    sys.exit(1)

"""
ADVANCED FIELD SIMULATION: UET LOGIC v3.0
-----------------------------------------
A "Serious Analysis" of Phase Separation using the 
Complementary Layer Logic.

Physics Layer:
- C: Openness Field (Diffusion-Reaction)
- I: Closure Field (Diffusion-Reaction)
- Interaction: C and I couple via beta parameter.

UET Analysis Layer (The "New Logic"):
- Value (V): Defined as the emergence of orderly structure.
  V ~ Integral( |C - I| ) * StructureFactor ?
  Unpacking V = M(C/I)^alpha locally.
  
Goal: Show that "System Balance" (Omega decrease) correlates with 
"Value Generation" (V increase).
"""


def solve_spectral(rhs, k2, alpha):
    """Solve (I - alpha*Laplacian) u = rhs in Frequency Domain"""
    rhat = np.fft.fftn(rhs)
    # Laplacian in Fourier is -k^2
    # Operator is 1 - alpha*(-k^2) = 1 + alpha*k^2
    uhat = rhat / (1.0 + alpha * k2)
    return np.fft.ifftn(uhat).real


def run_simulation(case_name, N=64, L=10.0, steps=200):
    print(f"Running Advanced Simulation: {case_name}")

    # Grid setup
    dx = L / N
    k = _kgrid_1d(N, L)
    kx, ky = np.meshgrid(k, k, indexing="ij")
    k2 = kx * kx + ky * ky

    # Parameters (Complex Interaction)
    M_C, M_I = 1.0, 1.0
    k_C, k_I = 0.05, 0.05
    beta = 0.5  # Coupling strength

    # Potentials (Bistable - systems want to be Open (1) or Closed (-1))
    pot_C = from_dict({"type": "quartic", "a": -1.0, "delta": 1.0, "s": 0.0})
    pot_I = from_dict({"type": "quartic", "a": -1.0, "delta": 1.0, "s": 0.0})

    # Initialize Fields (Random Noise)
    np.random.seed(42)
    C = np.random.normal(0, 0.2, (N, N))  # Initial fluctuations
    I = np.random.normal(0, 0.2, (N, N))

    dt = 0.01

    history = {"t": [], "Omega": [], "Value_Total": []}
    frames = []

    for step in range(steps):
        # 1. Physics Step (Semi-Implicit Cahn-Hilliard-like)
        # dC/dt = M_C * ( Laplacian(dF/dC) ) <- Conserved (Model B)
        # OR
        # dC/dt = -M_C * ( dF/dC ) <- Non-conserved (Model A / Allen-Cahn)
        # uet_core/solver.py uses Allen-Cahn type (Reaction-Diffusion) with stiffness

        # Explicit part: N(u) = -M * ( V'(u) - beta*Other )
        # Implicit part: L(u) = -M * kappa * Laplacian(u) is actually handled
        # But here let's use the Solver's logic:
        # u_new = (I - dt*M*kappa*Lap)^-1 [ u_old - dt*M*( V'(u) - beta*Other ) ]

        # Forces
        force_C = pot_C.dV(C) - beta * I
        force_I = pot_I.dV(I) - beta * C

        # RHS for implicit solver
        rhs_C = C - dt * M_C * force_C
        rhs_I = I - dt * M_I * force_I

        # Solve
        C = solve_spectral(rhs_C, k2, dt * M_C * k_C)
        I = solve_spectral(rhs_I, k2, dt * M_I * k_I)

        # 2. UET Analysis (The Observer)
        # Calculate Balance (Omega)
        # Omega = Energy Functional
        omega_val = omega_CI(C, I, pot_C, pot_I, beta, k_C, k_I, L)

        # Calculate Value (V)
        # V = Integral of Local Value
        # Local Value v(x) = C(x) / (epsilon + |I(x)|) ??
        # Or simply V = Magnitude of Ordered Structure?
        # Let's use the definition: V = M * (C_openness / I_friction)
        # Here we assume C > 0 is Open, I > 0 is Closed.
        # Shift to positive range for calculation logic if needed
        cutoff = 1e-3
        C_pos = np.abs(C) + cutoff
        I_pos = np.abs(I) + cutoff
        V_field = C_pos / I_pos
        V_total = np.mean(V_field)

        history["t"].append(step * dt)
        history["Omega"].append(omega_val)
        history["Value_Total"].append(V_total)

        if step % 5 == 0:
            frames.append((C.copy(), I.copy(), V_field.copy()))

        print(f"Step {step}: Omega={omega_val:.4f}, Value={V_total:.4f}", end="\r")

    print("\nSimulation Complete.")
    return history, frames


def generate_report(hist, frames):
    output_dir = "research_v3/04_analysis/results"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Timeseries Plot
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = "tab:red"
    ax1.set_xlabel("Time")
    ax1.set_ylabel("System Balance (Omega)", color=color)
    ax1.plot(hist["t"], hist["Omega"], color=color, linewidth=2)
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_title("Correlation: Balance (Physics) vs Value (UET)")
    ax1.grid(True)

    ax2 = ax1.twinx()
    color = "tab:blue"
    ax2.set_ylabel("Total System Value (V)", color=color)
    ax2.plot(hist["t"], hist["Value_Total"], color=color, linewidth=2, linestyle="--")
    ax2.tick_params(axis="y", labelcolor=color)

    fig.tight_layout()
    plt.savefig(f"{output_dir}/timeseries_analysis.png")
    print(f"Saved timeseries to {output_dir}/timeseries_analysis.png")

    # 2. Field Visualization (Start vs Middle vs End)
    indices = [0, len(frames) // 2, len(frames) - 1]
    fig, axs = plt.subplots(3, 3, figsize=(12, 12))

    titles = ["Start (Disorder)", "Middle (Ordering)", "End (Structured)"]

    for i, idx in enumerate(indices):
        C_f, I_f, V_f = frames[idx]

        # Plot C
        im0 = axs[i, 0].imshow(C_f, cmap="viridis")
        axs[i, 0].set_title(f"C (Openness) - {titles[i]}")
        plt.colorbar(im0, ax=axs[i, 0])

        # Plot I
        im1 = axs[i, 1].imshow(I_f, cmap="inferno")
        axs[i, 1].set_title(f"I (Closure) - {titles[i]}")
        plt.colorbar(im1, ax=axs[i, 1])

        # Plot V
        im2 = axs[i, 2].imshow(V_f, cmap="plasma")
        axs[i, 2].set_title(f"V (Value) - {titles[i]}")
        plt.colorbar(im2, ax=axs[i, 2])

    plt.tight_layout()
    plt.savefig(f"{output_dir}/field_evolution.png")
    print(f"Saved fields to {output_dir}/field_evolution.png")


if __name__ == "__main__":
    hist, frames = run_simulation("Phase_Separation Analysis")
    generate_report(hist, frames)
