import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

# Setup Path
current_path = Path(__file__).resolve()
# Go up to Topic Root (Code -> Topic) -> Result
result_dir = current_path.parent.parent.parent / "Result"
result_dir.mkdir(parents=True, exist_ok=True)


def visualize_fermat_modularity():
    print("🌌 Visualizing Fermat's Last Theorem: Modularity vs Singularity")

    # 1. Create the "Modular Surface" (The Stable UET Universe)
    # Represented by a harmonic function (e.g., Modular Form analogue)
    x = np.linspace(-3, 3, 100)
    y = np.linspace(-3, 3, 100)
    X, Y = np.meshgrid(x, y)

    # A "Modular" surface is highly symmetric and periodic
    # Z_modular = cos(x)*cos(y) * exp... mimicking a stable potential
    Z_modular = np.cos(2 * X) * np.cos(2 * Y) * np.exp(-(X**2 + Y**2) / 5)

    # 2. Create the "Fermat Singularity" (The Forbidden State)
    # A Frey curve arising from a Fermat solution would be "too sharp" or "non-modular"
    # We represent it as a spike that pierces the harmony
    Z_fermat = np.zeros_like(Z_modular)
    # Create a spike at (0,0) - The "Counterexample"
    R = np.sqrt(X**2 + Y**2)
    Z_fermat = 3.0 * np.exp(-(R**2) * 10)  # Sharp spike

    # Plot
    fig = plt.figure(figsize=(14, 8))
    plt.style.use("dark_background")
    ax = fig.add_subplot(111, projection="3d")

    # Plot Modular Surface (Wireframe / Translucent)
    surf = ax.plot_surface(
        X, Y, Z_modular, cmap="viridis", alpha=0.6, linewidth=0.5, edgecolors="green"
    )

    # Plot Fermat Singularity (Red Spike)
    # Only plot where passing a threshold to keep it clean
    ax.plot_surface(X, Y, Z_fermat, color="red", alpha=0.9, rstride=5, cstride=5)

    # Annotations
    ax.text(
        0,
        0,
        3.5,
        "Fermat's Counterexample ($x^n+y^n=z^n$)\n(Forbidden Spike)",
        color="red",
        fontsize=12,
        ha="center",
    )
    ax.text(2, 2, 0.5, "Modular Universe (Stable)", color="lime", fontsize=10)

    ax.set_title(
        "UET Geometry: Why Fermat's Last Theorem is True\n(Non-Modular Spikes cannot exist in a Modular Universe)",
        fontsize=16,
        color="white",
    )
    ax.set_axis_off()  # Clean look

    output_path = result_dir / "Fermat_Modularity_Proof.png"
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    print(f"✅ Graph Generated: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    visualize_fermat_modularity()
