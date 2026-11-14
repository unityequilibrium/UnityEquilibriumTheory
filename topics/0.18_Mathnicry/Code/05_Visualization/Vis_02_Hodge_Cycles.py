import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

# Setup Path
current_path = Path(__file__).resolve()
# Go up to Topic Root (Code -> Topic) -> Result
result_dir = current_path.parent.parent.parent / "Result"
result_dir.mkdir(parents=True, exist_ok=True)


def visualize_hodge():
    print("🌌 Visualizing Hodge Conjecture: The Pixelated Soul of Shapes")

    # 1. Create a "Harmonic Cycle" (Algebraic)
    # A circle x^2 + y^2 = r^2 fits perfectly on a grid (well, effectively)
    # It resonates.
    t = np.linspace(0, 2 * np.pi, 100)
    x_alg = 5 * np.cos(t)
    y_alg = 5 * np.sin(t)
    z_alg = np.zeros_like(t) + 5  # Floating at level 5

    # 2. Create a "Non-Algebraic Cycle" (Messy squiggly thing)
    # This shape doesn't have a simple polynomial definition.
    # In UET, this "leaks" energy.
    t_messy = np.linspace(0, 2 * np.pi, 100)
    x_mess = 5 * np.cos(t_messy) + 0.5 * np.sin(5 * t_messy)  # Perturbed
    y_mess = 5 * np.sin(t_messy) + 0.5 * np.cos(3 * t_messy)  # Perturbed
    z_mess = np.zeros_like(t_messy)

    fig = plt.figure(figsize=(14, 8))
    plt.style.use("dark_background")
    ax = fig.add_subplot(111, projection="3d")

    # Plot the "Manifold Grid" (Lattice)
    grid_x, grid_y = np.meshgrid(np.linspace(-8, 8, 20), np.linspace(-8, 8, 20))
    grid_z = np.zeros_like(grid_x)
    ax.plot_wireframe(
        grid_x,
        grid_y,
        grid_z,
        color="#333333",
        alpha=0.5,
        label='Complex Manifold (The "Pixel Grid")',
    )

    # Plot Algebraic Cycle
    ax.plot(
        x_alg,
        y_alg,
        z_alg,
        color="cyan",
        linewidth=4,
        label="Algebraic Cycle (Harmonic)\nFits the logic of the universe",
    )

    # Plot Non-Algebraic Cycle
    ax.plot(
        x_mess,
        y_mess,
        z_mess,
        color="red",
        linestyle="--",
        linewidth=2,
        label='Random Topological Cycle\n(Will "Dissolve" over time)',
    )

    # Add vertical lines to show "Support" or Logic
    for i in range(0, 100, 10):
        ax.plot([x_alg[i], x_alg[i]], [y_alg[i], y_alg[i]], [0, 5], color="cyan", alpha=0.3)

    ax.text(0, 0, 6, "Algebraic Geometry\n(Perfect Frequency)", color="cyan", ha="center")
    ax.text(0, -7, 0, "Topological Chaos", color="red", ha="center")

    ax.set_title(
        "UET Hodge Conjecture: Shapes with Genetic Memory\nAlgebraic Cycles imply Harmonic Stability on the Lattice",
        fontsize=16,
        color="white",
    )
    ax.set_axis_off()
    ax.legend()

    output_path = result_dir / "Hodge_Lattice_Proof.png"
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    print(f"✅ Graph Generated: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    visualize_hodge()
