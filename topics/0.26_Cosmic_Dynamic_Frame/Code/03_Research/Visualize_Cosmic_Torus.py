import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

# Setup Path
current_path = Path(__file__).resolve()
result_dir = current_path.parent.parent / "Result"
result_dir.mkdir(parents=True, exist_ok=True)


def visualize_cosmic_torus():
    print("🌌 Visualizing Cosmic Topology: The Donut Universe")

    # Define Torus Parameters
    R = 4  # Major radius (distance from center of hole to tube center)
    r = 1.5  # Minor radius (radius of the tube)

    # Meshgrid for Torus surface
    u = np.linspace(0, 2 * np.pi, 100)  # Angle around the tube
    v = np.linspace(0, 2 * np.pi, 100)  # Angle of the torus ring
    u, v = np.meshgrid(u, v)

    # Torus parametric equations
    x = (R + r * np.cos(v)) * np.cos(u)
    y = (R + r * np.cos(v)) * np.sin(u)
    z = r * np.sin(v)

    # Create figure
    fig = plt.figure(figsize=(12, 10))
    plt.style.use("dark_background")
    ax = fig.add_subplot(111, projection="3d")

    # Plot Surface (Wireframe-ish style)
    # We use plot_surface with alpha vs wireframe for better "Volume" feel
    surf = ax.plot_surface(
        x, y, z, cmap="magma", alpha=0.8, rstride=5, cstride=5, linewidth=0.2, edgecolors="orange"
    )

    # Draw "Flow Lines" (Material Circulation)
    # Simulating the flow of galaxies/matter recycling through the universe
    # A spiral path on the torus
    theta = np.linspace(0, 8 * np.pi, 200)
    phi = 3 * theta  # Winding number

    flow_x = (R + (r + 0.2) * np.cos(phi)) * np.cos(theta)
    flow_y = (R + (r + 0.2) * np.cos(phi)) * np.sin(theta)
    flow_z = (r + 0.2) * np.sin(phi)

    ax.plot(
        flow_x,
        flow_y,
        flow_z,
        color="cyan",
        linewidth=2,
        label="Cosmic Flow (Matter Recycling)\nNo Big Bang, Just Big Flow",
    )

    # Annotations
    ax.text(
        0,
        0,
        4,
        "The Universe is a Donut (Torus)",
        color="orange",
        fontsize=14,
        ha="center",
        fontweight="bold",
    )
    ax.text(
        0,
        0,
        -4,
        "Total Curvature = 0 (Appears Flat)\nBut topologically infinite",
        color="white",
        ha="center",
    )

    # Set view
    ax.view_init(elev=60, azim=0)
    ax.set_axis_off()
    ax.legend(loc="lower right")

    plt.title(
        "UET Cosmic Topology (Topic 0.26)\nWhy the Universe has no Edge and no Beginning",
        fontsize=16,
        color="white",
    )

    output_path = result_dir / "Cosmic_Torus_Proof.png"
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    print(f"✅ Graph Generated: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    visualize_cosmic_torus()
