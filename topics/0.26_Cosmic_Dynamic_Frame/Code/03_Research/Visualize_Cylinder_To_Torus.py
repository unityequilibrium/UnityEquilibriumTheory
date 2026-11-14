import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

# Setup Path
current_path = Path(__file__).resolve()
result_dir = current_path.parent.parent / "Result"
result_dir.mkdir(parents=True, exist_ok=True)


def visualize_cylinder_torus():
    print("🌌 Visualizing Topology: Cylinder is the Father of Torus")

    fig = plt.figure(figsize=(14, 6))
    plt.style.use("dark_background")

    # 1. Plot Cylinder (The User's View)
    ax1 = fig.add_subplot(121, projection="3d")
    z = np.linspace(-2, 2, 50)
    theta = np.linspace(0, 2 * np.pi, 50)
    theta_grid, z_grid = np.meshgrid(theta, z)
    x_cyl = np.cos(theta_grid)
    y_cyl = np.sin(theta_grid)

    ax1.plot_surface(
        x_cyl, y_cyl, z_grid, cmap="winter", alpha=0.6, edgecolors="blue", linewidth=0.2
    )
    ax1.set_title("1. Your View: The Infinite Cylinder\n(Flow goes Up/Down forever)", color="cyan")
    ax1.set_axis_off()

    # Arrows for flow
    ax1.quiver(0, 0, -2.5, 0, 0, 5, color="white", arrow_length_ratio=0.1)
    ax1.text(0, 0, 3, "Energy Flow", color="white", ha="center")

    # 2. Plot Torus (UET View - Connected Ends)
    ax2 = fig.add_subplot(122, projection="3d")

    # Torus is just a cylinder bent 360 degrees
    R = 3
    r = 1
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, 2 * np.pi, 50)
    u, v = np.meshgrid(u, v)
    x_tor = (R + r * np.cos(v)) * np.cos(u)
    y_tor = (R + r * np.cos(v)) * np.sin(u)
    z_tor = r * np.sin(v)

    ax2.plot_surface(
        x_tor, y_tor, z_tor, cmap="magma", alpha=0.6, edgecolors="orange", linewidth=0.2
    )
    ax2.set_title(
        "2. UET View: The Connected Cylinder (Torus)\n(Top connects to Bottom = Recycling)",
        color="orange",
    )
    ax2.set_axis_off()

    # Annotation connecting them
    plt.suptitle(
        "Topology Truth: A Torus is just a Cylinder that bites its own tail!",
        fontsize=16,
        color="white",
        y=0.95,
    )

    output_path = result_dir / "Cylinder_vs_Torus.png"
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    print(f"✅ Graph Generated: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    visualize_cylinder_torus()
