import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Setup Path
current_path = Path(__file__).resolve()
# Go up to Topic Root (Code -> Topic) -> Result
result_dir = current_path.parent.parent.parent / "Result"
result_dir.mkdir(parents=True, exist_ok=True)


def visualize_euler():
    print("🌌 Visualizing Euler's Identity: The Perfect Loop")

    # Define the rotation path in the Complex Plane
    theta = np.linspace(0, np.pi, 100)

    # e^(i*theta)
    real_part = np.cos(theta)
    imag_part = np.sin(theta)

    plt.figure(figsize=(10, 10))
    plt.style.use("dark_background")

    # 1. Plot the Unit Circle (The Stage)
    full_circle = np.linspace(0, 2 * np.pi, 200)
    plt.plot(
        np.cos(full_circle),
        np.sin(full_circle),
        color="#333333",
        linestyle="--",
        label="Unit Circle (Potential)",
    )

    # 2. Plot the Journey (e^ix) - From 1 to -1
    plt.plot(
        real_part,
        imag_part,
        color="cyan",
        linewidth=4,
        label="The Journey ($e^{i\pi}$)\nExpansion & Rotation",
    )

    # 3. Plot the Vital Points
    # Start (Unity)
    plt.plot(1, 0, "wo", markersize=10, label="Unity (+1)\nThe Origin/Source")
    plt.text(1.1, 0, "Start (+1)", color="white", fontsize=12)

    # End (Anti-Unity)
    plt.plot(-1, 0, "ro", markersize=10, label="Anti-Unity (-1)\nThe Destination")
    plt.text(-1.2, 0, "End $e^{i\pi}$ (-1)", color="red", fontsize=12)

    # The Vector Sum (Equilibrium)
    # Visualizing that 1 + (-1) = 0
    # Maybe draw arrows colliding?
    plt.arrow(0, -0.5, 0.9, 0, head_width=0.05, color="white")
    plt.arrow(0, -0.5, -0.9, 0, head_width=0.05, color="red")
    plt.text(0, -0.6, "1 + (-1) = 0\n(Equilibrium)", color="lime", ha="center")

    # Origin
    plt.plot(0, 0, "g+", markersize=15, markeredgewidth=2)
    plt.text(0, 0.1, "The Void (0)", color="lime", ha="center")

    # Annotations for UET interpretation
    plt.title(
        "UET Analysis: Euler's Identity ($e^{i\pi} + 1 = 0$)\nThe Formula of a Perfect Universe",
        fontsize=16,
        color="white",
    )
    plt.xlabel("Real Axis (Existence)", fontsize=12)
    plt.ylabel("Imaginary Axis (Vibration/Time)", fontsize=12)

    plt.grid(True, alpha=0.3)
    plt.axis("equal")
    plt.legend(loc="upper right")

    output_path = result_dir / "Euler_Identity_Proof.png"
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    print(f"✅ Graph Generated: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    visualize_euler()
