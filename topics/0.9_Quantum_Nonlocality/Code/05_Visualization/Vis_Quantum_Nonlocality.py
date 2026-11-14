"""
UET Visualization Standard: Quantum Nonlocality (Topic 0.9)
===========================================================
Objective: Represent the "Extreme" depth of UET Quantum Research.
Plots:
1. Geometric Bell Violation (S-Bound 2*sqrt(2))
2. DNA Proton Tunneling (Mutation Risk)
3. Double Slit Interference (Information Field)
4. Qubit T1 Relaxation (Entropy Diffusion)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH


# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.9_Quantum_Nonlocality"
OUTPUT_DIR = TOPIC_DIR / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetics
plt.style.use("dark_background")
UET_CYAN = "#00e5ff"
UET_MAGENTA = "#ff00ff"
UET_GOLD = "#ffd700"


def plot_geometric_bell():
    """Visualizes the 4D Hypercube logic for Bell Violation."""
    print("Generating Geometric Bell Violation Plot...")

    # Concept: Classical is 3D slice (S=2), Quantum is 4D diagonal (S=2.828)
    labels = [
        "Classical Limit\n(Local Realist)",
        "Hensen et al.\n(Experimental)",
        "UET Prediction\n(4D Geometry)",
    ]
    values = [2.0, 2.42, 2.828]
    colors = ["#555555", UET_MAGENTA, UET_CYAN]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=colors, alpha=0.8, width=0.5)

    # Add horizontal lines for limits
    ax.axhline(y=2.0, color="white", linestyle="--", alpha=0.5, label="Bell Bound (S=2)")
    ax.axhline(
        y=2.828, color=UET_CYAN, linestyle=":", alpha=0.8, label=r"Tsirelson Bound ($2\sqrt{2}$)"
    )

    # Annotate Values
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.05,
            f"{h:.3f}",
            ha="center",
            va="bottom",
            color="white",
            fontweight="bold",
        )

    ax.set_ylim(0, 3.5)
    ax.set_ylabel("CHSH Parameter S")
    ax.set_title(
        "Quantum Nonlocality: Geometric Violation of Bell's Inequality", fontsize=14, color=UET_CYAN
    )
    ax.legend(loc="lower right")
    ax.grid(axis="y", alpha=0.1)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "bell_violation_geometric.png", dpi=200)
    plt.close()


def plot_dna_tunneling():
    """Visualizes Information Leak in DNA."""
    print("Generating DNA Tunneling Plot...")

    # Transmission probability vs Barrier Width
    L = np.linspace(0.2, 1.0, 100) * 1e-10  # Angstroms to meters
    V = 0.4 * 1.6e-19  # 0.4 eV
    m_p = 1.67e-27
    hbar = 1.054e-34

    # UET Tunneling Decay
    kappa = np.sqrt(2 * m_p * V) / hbar
    T = np.exp(-2 * kappa * L)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(L * 1e10, T, color=UET_MAGENTA, linewidth=2, label="Tunneling Probability")
    ax.fill_between(L * 1e10, 0, T, color=UET_MAGENTA, alpha=0.2)

    # Highlight Biological Scale (0.5 Å)
    ax.axvline(x=0.5, color="white", linestyle="--", alpha=0.5)
    ax.scatter(
        [0.5],
        [np.exp(-2 * kappa * 0.5e-10)],
        color=UET_GOLD,
        s=100,
        zorder=5,
        label="DNA H-Bond Scale",
    )

    ax.set_yscale("log")
    ax.set_xlabel("Barrier Width (Ångströms)")
    ax.set_ylabel("Transmission Probability (log)")
    ax.set_title(
        "Quantum Biology: DNA Proton Tunneling & Information Leak", fontsize=14, color=UET_MAGENTA
    )
    ax.legend()
    ax.grid(alpha=0.1, which="both")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "dna_tunneling_leak.png", dpi=200)
    plt.close()


def plot_double_slit():
    """Visualizes Information Field Interference."""
    print("Generating Double Slit Interference Plot...")

    x = np.linspace(-10, 10, 1000)
    d = 2.0  # distance between slits
    a = 0.5  # slit width
    lam = 1.0  # wavelength
    L = 10.0  # distance to screen

    theta = np.arctan(x / L)
    beta = np.pi * d * np.sin(theta) / lam
    alpha = np.pi * a * np.sin(theta) / lam

    intensity = (np.cos(beta) ** 2) * (np.sinc(alpha / np.pi) ** 2)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(x, intensity, color=UET_CYAN, linewidth=2, label="UET Information Gradient")

    # Custom colormap for interference
    from matplotlib.colors import LinearSegmentedColormap

    colors_list = [(0, 0, 0), (0, 0.9, 1.0)]
    cm_interf = LinearSegmentedColormap.from_list("cyan_black_custom", colors_list, N=100)

    # Aesthetics: Gradient background for the "Screen"
    ax.imshow(
        np.tile(intensity, (10, 1)),
        extent=[-10, 10, -0.2, 1.2],
        aspect="auto",
        cmap=cm_interf,
        alpha=0.3,
    )

    ax.set_xlim(-10, 10)
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel("Screen Position")
    ax.set_ylabel("Information Density")
    ax.set_title(
        "Wave-Particle Duality: Information Field Interference", fontsize=14, color=UET_CYAN
    )

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "double_slit_interference.png", dpi=200)
    plt.close()


def plot_qubit_diffusion():
    """Visualizes Qubit T1 decay as Entropy Diffusion."""
    print("Generating Qubit Entropy Diffusion Plot...")

    # 2D Heatmap of a decaying Gaussian (representing Information Density σ)
    size = 100
    x = np.linspace(-5, 5, size)
    y = np.linspace(-5, 5, size)
    X, Y = np.meshgrid(x, y)

    # Time slices
    times = [1, 5, 20]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for i, t in enumerate(times):
        # Gaussian diffusion: sigma^2 = sigma0^2 + 2Dt
        sigma = np.sqrt(1 + 0.5 * t)
        Z = (1 / (sigma**2)) * np.exp(-(X**2 + Y**2) / (2 * sigma**2))

        im = axes[i].imshow(Z, extent=[-5, 5, -5, 5], cmap="magma", origin="lower")
        axes[i].set_title(rf"Time T = {t} $\mu s$")
        axes[i].axis("off")

    fig.suptitle(
        "Qubit T1 Relaxation: Information Diffusion into Vacuum", fontsize=16, color=UET_MAGENTA
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(OUTPUT_DIR / "qubit_t1_diffusion.png", dpi=200)
    plt.close()


def run_all():
    print("🚀 Running Topic 0.9 Extreme Visualization Suite...")
    plot_geometric_bell()
    plot_dna_tunneling()
    plot_double_slit()
    plot_qubit_diffusion()
    print("✅ All visualizations generated in Result/01_Showcase.")


if __name__ == "__main__":
    run_all()
