"""
UET Visualization Suite: Electroweak Physics (Topic 0.6)
========================================================
Generates "Real Research Graphs" for the showcase.
1. Alpha Decay: Quantum Tunneling (Barrier Penetration)
2. Beta Decay: Continuous Spectrum (Neutrino Evidence)
3. Weak Mixing: Unification Running (The Merge)
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
    root_path / "docs" / "topics" / "0.6_Electroweak_Physics" / "Result" / "01_Showcase"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set Style
plt.style.use("dark_background")
sns.set_palette("bright")




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def plot_alpha_tunneling():
    """Generate Alpha_Decay_Tunneling.png"""
    print("Generating Alpha Tunneling Plot...")

    r = np.linspace(0, 20, 500)

    # Nuclear Potential Well + Coulomb Barrier
    # V(r) = -V0 for r < R (Nuclear Force)
    # V(r) = Z*e^2/r for r > R (Coulomb Repulsion)
    R = 5.0
    V0 = -30.0
    barrier_height = 20.0

    V = np.zeros_like(r)
    V[r < R] = V0

    mask_out = r >= R
    V[mask_out] = barrier_height * (R / r[mask_out])

    # Alpha Particle Energy
    E_alpha = 5.0

    plt.figure(figsize=(10, 6))

    # Plot Potential
    plt.plot(r, V, "-", color="#00aaff", linewidth=3, label="Nuclear + Coulomb Potential")

    # Plot Particle Energy Level
    plt.axhline(
        y=E_alpha,
        color="#ffff00",
        linestyle="--",
        linewidth=2,
        label=f"Alpha Energy ({E_alpha} MeV)",
    )

    # Shade Tunneling Region
    tunnel_mask = (V > E_alpha) & (r > R)
    plt.fill_between(
        r, E_alpha, V, where=tunnel_mask, color="#ff0055", alpha=0.3, label="Quantum Tunneling Zone"
    )

    # Wavefunction simulation (Qualitative)
    psi = np.zeros_like(r)
    # Inside
    psi[r < R] = 10 * np.sin(2 * r[r < R])
    # Tunneling (Decay)
    psi[tunnel_mask] = 10 * np.sin(2 * R) * np.exp(-1.5 * (r[tunnel_mask] - R))
    # Outside (Escaped)
    mask_esc = (r > R) & (~tunnel_mask)
    if np.any(mask_esc):
        start_esc = r[mask_esc][0]
        amp_esc = psi[tunnel_mask][-1] if np.any(tunnel_mask) else 0
        psi[mask_esc] = amp_esc * np.sin(r[mask_esc] - start_esc)

    # Scale psi for visibility
    plt.plot(
        r, psi + E_alpha, "-", color="#00ff00", alpha=0.6, linewidth=1.5, label="Wavefunction ψ(r)"
    )

    plt.title("Alpha Decay: The Great Escape (Quantum Tunneling)", fontsize=14)
    plt.xlabel("Distance from Nucleus Center (fm)")
    plt.ylabel("Energy (MeV)")
    plt.ylim(-40, 30)
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.2)

    plt.savefig(OUTPUT_DIR / "Alpha_Decay_Tunneling.png", dpi=150)
    plt.close()


def plot_beta_spectrum():
    """Generate Beta_Decay_Spectrum.png"""
    print("Generating Beta Spectrum Plot...")

    # Fermi Theory of Beta Decay
    # dN/dE ~ sqrt(E^2 - m^2) * (Q - E)^2 * E

    Q = 10.0  # End point energy (arbitrary units)
    m = 0.511  # Electron mass (approx)

    E = np.linspace(m, Q, 500)
    p = np.sqrt(E**2 - m**2)

    # Spectrum shape
    dN = p * E * (Q - E) ** 2
    # Add correction factor (Coulomb) - simplified
    F = 1.0 + 0.1 / p
    spectrum = dN * F

    plt.figure(figsize=(8, 6))

    plt.plot(E, spectrum, "-", color="#00ffcc", linewidth=3, fillstyle="full")
    plt.fill_between(E, spectrum, color="#00ffcc", alpha=0.2)

    # Annotations
    plt.text(
        Q / 2,
        max(spectrum) * 0.5,
        "Where is the missing energy?\n(Neutrino took it!)",
        color="white",
        ha="center",
    )
    plt.axvline(x=Q, color="red", linestyle="--", label="Max Energy (Q-value)")

    plt.title("Beta Decay Spectrum: The 'Ghost' Particle Signature", fontsize=14)
    plt.xlabel("Electron Energy (Ke)")
    plt.ylabel("Number of Electrons (Counts)")
    plt.legend()
    plt.grid(True, alpha=0.2)

    plt.savefig(OUTPUT_DIR / "Beta_Decay_Spectrum.png", dpi=150)
    plt.close()


def plot_weak_mixing():
    """Generate Weak_Mixing_Angle.png"""
    print("Generating Weak Mixing Plot...")

    # Energy Scale Q (GeV)
    Q = np.logspace(0, 16, 200)  # 1 GeV to GUT scale

    # Running of sin^2(theta_W)
    # Standard Model prediction: Increases slightly then merges
    # Low energy value ~ 0.231

    def running_coupling(q_scale):
        # Simplified RGE approximation
        return 0.231 + 0.005 * np.log10(q_scale) + 0.02 * np.exp(-((np.log10(q_scale) - 15) ** 2))

    sin2_theta = running_coupling(Q)

    plt.figure(figsize=(10, 6))

    plt.semilogx(Q, sin2_theta, "-", color="#ff00ff", linewidth=3)

    # Annotations
    plt.axvline(x=91.2, color="#00ffff", linestyle=":", label="Z-Boson Mass (Electroweak Scale)")
    plt.axvline(x=1e15, color="#ffff00", linestyle="--", label="GUT Scale (The Merge)")

    plt.text(1e2, 0.235, "Electroweak Unification\n(Standard Model)", color="#00ffff")
    plt.text(1e12, 0.28, "Grand Unification\n(All Forces One)", color="#ffff00")

    plt.title("The Merge: Weak Force & Electromagnetism Unification", fontsize=14)
    plt.xlabel("Energy Scale Q (GeV)")
    plt.ylabel("Weak Mixing Angle sin²(θw)")
    plt.legend()
    plt.grid(True, alpha=0.2, which="both")

    plt.savefig(OUTPUT_DIR / "Weak_Mixing_Angle.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    print("=== Generating UET Electroweak Physics Visualizations ===")
    try:
        plot_alpha_tunneling()
        plot_beta_spectrum()
        plot_weak_mixing()
        print(f"\n[SUCCESS] All plots saved to: {OUTPUT_DIR}")
    except Exception as e:
        print(f"\n[ERROR] Output failed: {e}")
