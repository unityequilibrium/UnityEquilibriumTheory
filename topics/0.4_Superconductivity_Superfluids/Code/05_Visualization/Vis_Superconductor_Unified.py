"""
UET Visualization Suite: Superconductivity (Topic 0.4)
======================================================
Generates "Real Research Graphs" for the showcase.
1. Phase Transition: The Drop (R -> 0 at Tc)
2. Quantum Vortex: Superfluid rotation (Lattice)
3. Meissner Effect: Field Exclusion
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path



# --- ROBUST PATH SETUP ---


# Define Output Directory
OUTPUT_DIR = (
    root_path
    / "docs"
    / "topics"
    / "0.4_Superconductivity_Superfluids"
    / "Result"
    / "01_Showcase"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set Style
plt.style.use("dark_background")
sns.set_palette("bright")




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def plot_phase_transition():
    """Generate Superconductor_Phase_Transition.png"""
    print("Generating Phase Transition Plot...")

    T = np.linspace(0, 20, 500)
    Tc = 9.2  # Niobium

    # Normal Metal (Linear-ish)
    R_normal = 0.5 + 0.1 * T

    # Superconductor (Drop)
    # Model: Step function smoothed by sigmoid
    # R_sc = R_normal / (1 + exp(-alpha * (T - Tc)))
    # But for visual impact, a sharper transition
    R_sc = R_normal.copy()
    R_sc[T < Tc] = 1e-9  # Effectively zero

    # Add some transition width data points for realism
    width = 0.2
    transition_mask = (T >= Tc) & (T < Tc + width)
    R_sc[transition_mask] = R_normal[transition_mask] * (T[transition_mask] - Tc) / width

    plt.figure(figsize=(10, 6))

    plt.plot(T, R_normal, "--", color="gray", alpha=0.5, label="Normal Metal (Ohmic)")
    plt.plot(T, R_sc, "-", color="#00ffff", linewidth=3, label="Superconductor (UET/BCS)")

    plt.axvline(x=Tc, color="white", linestyle=":", alpha=0.8, label=f"Critical Temp Tc = {Tc}K")
    plt.text(Tc + 0.5, 0.2, "Phase Transition\n(Entropy Collapse)", color="white", fontsize=12)

    plt.title("The Drop: Resistance Vanishes at Critical Temperature", fontsize=14)
    plt.xlabel("Temperature (K)")
    plt.ylabel("Resistance (Ohms)")
    plt.legend()
    plt.grid(True, alpha=0.2)

    plt.savefig(OUTPUT_DIR / "Superconductor_Phase_Transition.png", dpi=150)
    plt.close()


def plot_vortex_lattice():
    """Generate Quantum_Vortex_Lattice.png"""
    print("Generating Vortex Lattice Plot...")

    # Grid
    x = np.linspace(-10, 10, 200)
    y = np.linspace(-10, 10, 200)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    # Hexagonal Lattice Basis
    a = 4.0
    vectors = [
        0,
        a,
        -a,
        a * np.exp(1j * np.pi / 3),
        a * np.exp(-1j * np.pi / 3),
        -a * np.exp(1j * np.pi / 3),
        -a * np.exp(-1j * np.pi / 3),
        # Second shell (approx)
        2 * a,
        -2 * a,
    ]

    # Order Parameter Psi approx product of (z - z_i)
    Psi = np.ones_like(Z, dtype=complex)

    for v in vectors:
        # Each vortex is a zero in the wavefunction
        # Factor: (z - pos) / |z - pos| * tanh(|z-pos|) to regularize
        # Simplified: just plotting magnitude dip
        r = np.abs(Z - v)
        Psi *= np.tanh(r / 1.0)  # Core size 1.0

    Magnitude = np.abs(Psi)

    plt.figure(figsize=(8, 8))
    plt.imshow(Magnitude, extent=[-10, 10, -10, 10], cmap="inferno", origin="lower")
    plt.colorbar(label="Order Parameter |Ψ|")

    plt.title("Quantum Vortex Lattice (Abrikosov State)", fontsize=14)
    plt.xlabel("x (Coherence Lengths)")
    plt.ylabel("y (Coherence Lengths)")

    plt.savefig(OUTPUT_DIR / "Quantum_Vortex_Lattice.png", dpi=150)
    plt.close()


def plot_meissner_effect():
    """Generate Meissner_Levitation_Field.png"""
    print("Generating Meissner Effect Plot...")

    # Potential Flow around a Cylinder
    # Stream function psi = U * y * (1 - R^2 / r^2)

    Y, X = np.mgrid[-3:3:100j, -3:3:100j]
    R_cyl = 1.0
    U = 1.0

    R = np.sqrt(X**2 + Y**2)
    Theta = np.arctan2(Y, X)

    # Mask inside cylinder
    outside = R >= R_cyl

    # Stream function (magnetic field lines)
    # Perfect Diamagnetism implies field goes AROUND
    Psi = np.zeros_like(R)
    Psi[outside] = U * Y[outside] * (1 - R_cyl**2 / R[outside] ** 2)

    plt.figure(figsize=(8, 6))

    # Plot Field Lines
    plt.contour(X, Y, Psi, 20, colors="#00ffcc", alpha=0.8)

    # Plot Superconductor
    circle = plt.Circle((0, 0), R_cyl, color="#333333", fill=True, zorder=2)
    plt.gca().add_patch(circle)
    plt.gca().add_patch(
        plt.Circle((0, 0), R_cyl, color="#ffffff", fill=False, linewidth=2, zorder=3)
    )

    plt.text(-0.8, -0.1, "SC\n(B=0)", color="white", fontsize=12, fontweight="bold")

    plt.title("Meissner Effect: Magnetic Field Expulsion", fontsize=14)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.xlim(-3, 3)
    plt.ylim(-3, 3)
    plt.gca().set_aspect("equal")
    plt.grid(True, alpha=0.1)

    plt.savefig(OUTPUT_DIR / "Meissner_Levitation_Field.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    print("=== Generating UET Superconductivity Visualizations ===")
    try:
        plot_phase_transition()
        plot_vortex_lattice()
        plot_meissner_effect()
        print(f"\n[SUCCESS] All plots saved to: {OUTPUT_DIR}")
    except Exception as e:
        print(f"\n[ERROR] Output failed: {e}")
