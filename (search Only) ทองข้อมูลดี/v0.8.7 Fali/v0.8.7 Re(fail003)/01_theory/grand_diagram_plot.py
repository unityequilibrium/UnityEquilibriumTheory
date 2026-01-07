import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

"""
GRAND UNIFICATION DIAGRAM (Visual Render)
=========================================
Style: Matching 'physics_connections.png'
Status: Visualizing the Complementary Layer Architecture
"""


def draw_grand_diagram():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 14)
    ax.axis("off")

    # --- STYLES ---
    # Layer 1: Physics (Foundation) - Blue
    c_phys = "#E3F2FD"  # Light Blue
    ec_phys = "#1565C0"  # Dark Blue

    # Layer 2: UET (Observer) - Orange
    c_uet = "#FFF3E0"  # Light Orange
    ec_uet = "#EF6C00"  # Dark Orange

    # Layer 3: Outcome (Phenomena) - Green
    c_out = "#E8F5E9"  # Light Green
    ec_out = "#2E7D32"  # Dark Green

    # --- DRAWING FUNCTIONS ---
    def draw_box(x, y, w, h, color, edge, label, subtext, fontsize=12):
        box = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.2", facecolor=color, edgecolor=edge, linewidth=2
        )
        ax.add_patch(box)
        ax.text(
            x + w / 2,
            y + h - 0.5,
            label,
            fontsize=fontsize,
            fontweight="bold",
            ha="center",
            color=edge,
        )
        ax.text(
            x + w / 2,
            y + h / 2 - 0.3,
            subtext,
            fontsize=9,
            ha="center",
            va="center",
            color="#333333",
        )
        return box

    def draw_arrow(x1, y1, x2, y2, color, text=""):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=color, lw=2)
        )
        if text:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            ax.text(
                mid_x,
                mid_y,
                text,
                fontsize=9,
                ha="center",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"),
            )

    # ==========================
    # LAYER 3: OUTCOMES (Top)
    # ==========================
    ax.text(
        8,
        13.5,
        "LAYER 3: EXPLAINED PHENOMENA",
        fontsize=14,
        fontweight="bold",
        ha="center",
        color=ec_out,
    )

    # Galaxy Node
    draw_box(
        1,
        11,
        3.5,
        2,
        c_out,
        ec_out,
        "Dark Matter Effect",
        "Galaxy Rotation Curves\n(No new particles)",
    )

    # Life Node
    draw_box(6, 11, 4, 2, c_out, ec_out, "Life & Biology", "Homeostasis\n(Balanced C/I)")

    # Econ Node
    draw_box(
        11.5, 11, 3.5, 2, c_out, ec_out, "Economic Crisis", "Bubbles & Crashes\n(Value vs Activity)"
    )

    # ==========================
    # LAYER 2: UET (Middle)
    # ==========================
    ax.text(
        8,
        9.5,
        "LAYER 2: UET INFORMATION LAYER (Observer)",
        fontsize=14,
        fontweight="bold",
        ha="center",
        color=ec_uet,
    )

    # UET Core Box (Big)
    draw_box(4, 5.5, 8, 3.5, c_uet, ec_uet, "UET OBSERVER ENGINE", "")

    # Internal Variables
    # Omega (Center)
    draw_box(6.5, 6, 3, 1.5, "#FFFFFF", ec_uet, "Ω (Omega)", "System Stress\n(Potential)")

    # I (Left)
    draw_box(4.5, 6.5, 1.5, 1.5, "#FFE0B2", ec_uet, "I", "Closure\n(Identity)")

    # V (Right)
    draw_box(10, 6.5, 1.5, 1.5, "#FFE0B2", ec_uet, "V", "Value\n(Order)")

    # ==========================
    # LAYER 1: PHYSICS (Bottom)
    # ==========================
    ax.text(
        8,
        4.5,
        "LAYER 1: PHYSICAL REALITY (Foundation)",
        fontsize=14,
        fontweight="bold",
        ha="center",
        color=ec_phys,
    )

    # Newton
    draw_box(1, 1, 3.5, 2.5, c_phys, ec_phys, "NEWTON", "F = ma\nGravity")

    # Thermo
    draw_box(6, 1, 4, 2.5, c_phys, ec_phys, "THERMODYNAMICS", "dS > 0\nFree Energy")

    # Quantum
    draw_box(11.5, 1, 3.5, 2.5, c_phys, ec_phys, "QUANTUM", "Hψ = Eψ\nInformation")

    # ==========================
    # CONNECTIONS (Arrows)
    # ==========================

    # 1. Physics -> UET (Input)
    draw_arrow(2.75, 3.5, 5.25, 5.5, ec_phys, "Energy Landscape")  # Newton -> UET
    draw_arrow(8, 3.5, 8, 5.5, ec_phys, "Entropic State")  # Thermo -> UET
    draw_arrow(13.25, 3.5, 10.75, 5.5, ec_phys, "Info Density")  # Quantum -> UET

    # 2. UET Internal
    # I -> Omega (Closure creates Stress)
    draw_arrow(6, 7.25, 6.5, 7.25, ec_uet)
    # Omega -> V (Minimizing Stress creates Value)
    draw_arrow(9.5, 7.25, 10, 7.25, ec_uet)

    # 3. UET -> Outcome (Explanation)
    # I -> Galaxy (Dark Matter)
    draw_arrow(5.5, 9, 2.75, 11, ec_out, "Closure Drag (I-Field)")

    # Balance -> Life
    draw_arrow(8, 9, 8, 11, ec_out, "Optimal C/I Balance")

    # V -> Econ
    draw_arrow(10.5, 9, 13.25, 11, ec_out, "Value/Price Divergence")

    # ==========================
    # TITLE & LEGEND
    # ==========================
    ax.text(
        8,
        0.5,
        "The Complementary Layer Architecture (UET v3.0)",
        fontsize=16,
        fontweight="bold",
        ha="center",
    )

    # Save
    output_path = "research_v3/01_theory/grand_unification_visual.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Diagram saved to {output_path}")


if __name__ == "__main__":
    draw_grand_diagram()
