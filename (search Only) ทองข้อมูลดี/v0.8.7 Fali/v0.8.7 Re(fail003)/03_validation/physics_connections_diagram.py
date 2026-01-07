"""
Visualize How Newton, Einstein, Thermodynamics Connect
=======================================================

Show the ESTABLISHED connections first, before adding UET.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import os

# Create figure
fig, ax = plt.subplots(figsize=(16, 14))
ax.set_xlim(0, 16)
ax.set_ylim(0, 14)
ax.axis("off")

# Colors
color_einstein = "#45B7D1"  # Blue
color_newton = "#4ECDC4"  # Teal
color_thermo = "#96CEB4"  # Green
color_landauer = "#DDA0DD"  # Plum
color_energy = "#FFD93D"  # Yellow
color_uet = "#FF6B6B"  # Red (question mark)

# ============================================================
# CENTRAL: ENERGY concept
# ============================================================
energy_circle = Circle((8, 10), 1.5, facecolor=color_energy, edgecolor="black", linewidth=3)
ax.add_patch(energy_circle)
ax.text(8, 10, "ENERGY\nE", fontsize=16, fontweight="bold", ha="center", va="center")

# ============================================================
# EINSTEIN (top)
# ============================================================
einstein_box = FancyBboxPatch(
    (5.5, 12),
    5,
    1.5,
    boxstyle="round,pad=0.1",
    facecolor=color_einstein,
    edgecolor="black",
    linewidth=2,
)
ax.add_patch(einstein_box)
ax.text(8, 13, "EINSTEIN", fontsize=14, fontweight="bold", ha="center")
ax.text(8, 12.4, "E = mc^2  |  E = gamma*mc^2", fontsize=11, ha="center")

# Arrow Einstein → Energy
ax.annotate("", xy=(8, 11.5), xytext=(8, 12), arrowprops=dict(arrowstyle="->", color="black", lw=2))

# ============================================================
# NEWTON (left)
# ============================================================
newton_box = FancyBboxPatch(
    (1, 8), 4, 1.5, boxstyle="round,pad=0.1", facecolor=color_newton, edgecolor="black", linewidth=2
)
ax.add_patch(newton_box)
ax.text(3, 9, "NEWTON", fontsize=14, fontweight="bold", ha="center")
ax.text(3, 8.4, "E = (1/2)mv^2  |  F = ma", fontsize=11, ha="center")

# Arrow Newton → Energy
ax.annotate("", xy=(6.5, 10), xytext=(5, 9), arrowprops=dict(arrowstyle="->", color="black", lw=2))

# ============================================================
# THERMODYNAMICS (right)
# ============================================================
thermo_box = FancyBboxPatch(
    (11, 8),
    4,
    1.5,
    boxstyle="round,pad=0.1",
    facecolor=color_thermo,
    edgecolor="black",
    linewidth=2,
)
ax.add_patch(thermo_box)
ax.text(13, 9, "THERMO", fontsize=14, fontweight="bold", ha="center")
ax.text(13, 8.4, "dE = TdS - PdV  |  dS >= 0", fontsize=11, ha="center")

# Arrow Thermo → Energy
ax.annotate("", xy=(9.5, 10), xytext=(11, 9), arrowprops=dict(arrowstyle="->", color="black", lw=2))

# ============================================================
# CONNECTIONS BETWEEN THEM
# ============================================================

# Einstein → Newton (v << c)
ax.annotate(
    "",
    xy=(5, 8.75),
    xytext=(5.5, 12.5),
    arrowprops=dict(arrowstyle="->", color="blue", lw=2.5, connectionstyle="arc3,rad=0.3"),
)
ax.text(
    3.5,
    11,
    "v << c\n(low speed\nlimit)",
    fontsize=10,
    ha="center",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
)

# Newton → Thermo (N → ∞)
ax.annotate(
    "", xy=(11, 8.75), xytext=(5, 8.75), arrowprops=dict(arrowstyle="<->", color="green", lw=2.5)
)
ax.text(
    8,
    8.75,
    "N --> infinity\n(many particles)",
    fontsize=10,
    ha="center",
    va="center",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
)

# ============================================================
# LANDAUER (bottom middle)
# ============================================================
landauer_box = FancyBboxPatch(
    (5.5, 4.5),
    5,
    1.5,
    boxstyle="round,pad=0.1",
    facecolor=color_landauer,
    edgecolor="black",
    linewidth=2,
)
ax.add_patch(landauer_box)
ax.text(8, 5.5, "LANDAUER", fontsize=14, fontweight="bold", ha="center")
ax.text(8, 4.9, "E_bit = k_B * T * ln(2)", fontsize=11, ha="center")

# Thermo → Landauer
ax.annotate(
    "",
    xy=(10, 4.5),
    xytext=(12, 8),
    arrowprops=dict(arrowstyle="->", color="purple", lw=2.5, connectionstyle="arc3,rad=-0.2"),
)
ax.text(
    12,
    6.5,
    "Info <-> Energy\n(bit = thermal)",
    fontsize=10,
    ha="center",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
)

# ============================================================
# UET (bottom - question mark)
# ============================================================
uet_box = FancyBboxPatch(
    (5.5, 1),
    5,
    2,
    boxstyle="round,pad=0.1",
    facecolor=color_uet,
    edgecolor="black",
    linewidth=2,
    linestyle="--",
)
ax.add_patch(uet_box)
ax.text(8, 2.5, "UET / YOUR THEORY", fontsize=14, fontweight="bold", ha="center")
ax.text(8, 1.8, "V = M(C/I)^alpha\ndE/dt = ...", fontsize=11, ha="center")
ax.text(
    8, 1.2, "??? WHERE DOES IT FIT ???", fontsize=10, ha="center", color="darkred", style="italic"
)

# Landauer → UET (confirmed!)
ax.annotate("", xy=(8, 3), xytext=(8, 4.5), arrowprops=dict(arrowstyle="->", color="green", lw=3))
ax.text(
    6,
    3.8,
    "CONFIRMED\nE = kT ln(2)",
    fontsize=10,
    color="green",
    fontweight="bold",
    bbox=dict(boxstyle="round", facecolor="#90EE90", alpha=0.9),
)

# ============================================================
# Title and Legend
# ============================================================
ax.text(8, 13.8, "HOW PHYSICS CONNECTS", fontsize=20, fontweight="bold", ha="center")

# Legend
ax.add_patch(plt.Rectangle((0.5, 0.5), 0.4, 0.3, facecolor="green"))
ax.text(1.1, 0.65, "= Known connection (proven)", fontsize=10, va="center")
ax.add_patch(plt.Rectangle((5, 0.5), 0.4, 0.3, facecolor="red", linestyle="--", edgecolor="black"))
ax.text(5.6, 0.65, "= UET (needs to find its place)", fontsize=10, va="center")

# Key insight
insight_text = """KEY: Newton, Einstein, Thermo all connect through ENERGY
UET connects through Landauer (info <-> energy)
But does UET connect to Newton/Einstein directly?"""
ax.text(
    8,
    7,
    insight_text,
    fontsize=11,
    ha="center",
    bbox=dict(boxstyle="round", facecolor="#FFFFCC", alpha=0.9),
)

plt.tight_layout()

# Save
script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, "physics_connections.png")
plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Plot saved: {save_path}")

plt.show()
