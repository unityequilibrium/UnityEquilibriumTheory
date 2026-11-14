import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Setup Path
current_path = Path(__file__).resolve()
result_dir = (
    current_path.parents[3] / "Result"
)  # Adjust to reach docs/topics/0.21.../Result if needed.
# actually let's stick to the local Result folder relative to the script
result_dir = current_path.parent.parent / "Result"
result_dir.mkdir(parents=True, exist_ok=True)


def visualize_mass_gap():
    print("🌌 Visualizing Yang-Mills Mass Gap: The Toll Fee of the Vacuum")

    r = np.linspace(0.1, 4.0, 100)

    # 1. Electromagnetism (Photon) - Massless
    # Potential V(r) ~ -1/r (Coulomb)
    # Allows excitations of arbitrarily low energy (at large r)
    # But here we plot the "Dispersion" or Energy Cost usually.
    # Let's stick to the Confinement Potential analogy from the README.
    # E(r) ~ linear for confinement.

    # Let's plot the "Potential Energy" V(r)
    # QED (Abelian): V(r) ~ -1/r. Flattens out at 0. Free particles possible.
    V_qed = -0.5 / r

    # QCD (Non-Abelian): V(r) ~ -A/r + Br (Linear Confinement)
    # The "Mass Gap" is technically the energy of the first excited state (Glueball).
    # But visually, the "Confinement" (Infinite Potential) implies you can't have free particles.
    V_qcd = -0.5 / r + 1.5 * r  # Confinement term

    plt.figure(figsize=(12, 8))
    plt.style.use("dark_background")

    # Plot QED
    plt.plot(
        r,
        V_qed,
        "c--",
        linewidth=2,
        label="Electromagnetism (Massless Photon)\nFinite Energy at Infinity -> Free Particles",
    )

    # Plot QCD
    plt.plot(
        r,
        V_qcd,
        "m-",
        linewidth=3,
        label="Yang-Mills (Massive Glueball)\nInfinite Energy at Infinity -> Confinement",
    )

    # Draw the Gap
    # The gap is conceptually the minimum energy to create a stable state (a Glueball).
    # In this potential model, the ground state energy E0 > 0.
    # We'll approximate a ground state level line.
    E_gap = 2.0
    plt.axhline(
        y=E_gap,
        color="yellow",
        linestyle=":",
        label='Mass Gap ($\Delta > 0$)\nMinimum "Toll Fee" to exist',
    )

    # Annotations
    plt.text(2.5, -0.2, "Free Photons (Light)", color="cyan", fontsize=12)
    plt.text(
        1.5, 4.0, "Confined Gluons\n(Strong Force)", color="magenta", fontsize=12, fontweight="bold"
    )

    plt.arrow(0.5, 0, 0, E_gap, color="yellow", length_includes_head=True, head_width=0.05)
    plt.text(0.6, 1.0, "The Gap", color="yellow", fontsize=12, rotation=90)

    plt.ylim(-2, 6)
    plt.title(
        'Why the Strong Force has Mass (Yang-Mills Mass Gap)\nUnlike Light, the Vacuum "GRIPS" Gluons',
        fontsize=16,
        color="white",
    )
    plt.xlabel("Distance (r)", fontsize=12)
    plt.ylabel("Potential Energy V(r)", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()

    output_path = result_dir / "Yang_Mills_Gap_Proof.png"
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    print(f"✅ Graph Generated: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    visualize_mass_gap()
