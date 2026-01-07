"""
Theory Relationship Diagram
============================

Show how UET/UECT CONNECTS to Newton, Einstein, Thermodynamics
NOT overlap - but as limits/special cases.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

# Create figure
fig, ax = plt.subplots(figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis("off")

# Colors
color_uet = "#FF6B6B"  # Red
color_newton = "#4ECDC4"  # Teal
color_einstein = "#45B7D1"  # Blue
color_thermo = "#96CEB4"  # Green
color_landauer = "#DDA0DD"  # Plum

# ============================================================
# Draw main UET box at center-top
# ============================================================
uet_box = FancyBboxPatch(
    (6, 9), 4, 2, boxstyle="round,pad=0.1", facecolor=color_uet, edgecolor="black", linewidth=2
)
ax.add_patch(uet_box)
ax.text(8, 10, "UET / UECT", fontsize=14, fontweight="bold", ha="center", va="center")
ax.text(
    8,
    9.4,
    "dE/dt = M(dC/dt)² - SdC/dt + ∇Φ...\nV = M(C/I)^α\nE = kT ln(2) × I",
    fontsize=9,
    ha="center",
    va="center",
)

# ============================================================
# Draw target theory boxes
# ============================================================

# Newton (bottom left)
newton_box = FancyBboxPatch(
    (1, 1),
    3.5,
    2.5,
    boxstyle="round,pad=0.1",
    facecolor=color_newton,
    edgecolor="black",
    linewidth=2,
)
ax.add_patch(newton_box)
ax.text(2.75, 2.8, "NEWTON", fontsize=12, fontweight="bold", ha="center")
ax.text(2.75, 2.0, "F = ma\nE = ½mv²\ndE/dt = Fv", fontsize=10, ha="center")

# Einstein (bottom middle)
einstein_box = FancyBboxPatch(
    (6, 1),
    4,
    2.5,
    boxstyle="round,pad=0.1",
    facecolor=color_einstein,
    edgecolor="black",
    linewidth=2,
)
ax.add_patch(einstein_box)
ax.text(8, 2.8, "EINSTEIN", fontsize=12, fontweight="bold", ha="center")
ax.text(8, 2.0, "E = mc²\nE² = (pc)² + (mc²)²\nγ = 1/√(1-v²/c²)", fontsize=10, ha="center")

# Thermodynamics (bottom right)
thermo_box = FancyBboxPatch(
    (11.5, 1),
    3.5,
    2.5,
    boxstyle="round,pad=0.1",
    facecolor=color_thermo,
    edgecolor="black",
    linewidth=2,
)
ax.add_patch(thermo_box)
ax.text(13.25, 2.8, "THERMO", fontsize=12, fontweight="bold", ha="center")
ax.text(13.25, 2.0, "dS/dt ≥ 0\ndE/dt = -k∇S\nHeat flow", fontsize=10, ha="center")

# Landauer (middle right)
landauer_box = FancyBboxPatch(
    (12, 5.5),
    3,
    2,
    boxstyle="round,pad=0.1",
    facecolor=color_landauer,
    edgecolor="black",
    linewidth=2,
)
ax.add_patch(landauer_box)
ax.text(13.5, 7, "LANDAUER", fontsize=12, fontweight="bold", ha="center")
ax.text(13.5, 6.2, "E = kT ln(2)\nInfo ↔ Energy", fontsize=10, ha="center")

# ============================================================
# Draw arrows with CONDITIONS
# ============================================================

# UET → Newton (FAILS)
ax.annotate(
    "",
    xy=(2.75, 3.5),
    xytext=(6.5, 9),
    arrowprops=dict(arrowstyle="->", color="red", lw=2, ls="--"),
)
ax.text(
    3.5,
    6.5,
    "IF: S=0, Φ=0\nC=velocity?",
    fontsize=9,
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
)
ax.text(
    2.5,
    5.5,
    "❌ FAILS\n(M·a² ≠ M·v·a)",
    fontsize=9,
    color="red",
    fontweight="bold",
    bbox=dict(boxstyle="round", facecolor="#FFCCCC", alpha=0.9),
)

# UET → Einstein (FAILS)
ax.annotate(
    "", xy=(8, 3.5), xytext=(8, 9), arrowprops=dict(arrowstyle="->", color="red", lw=2, ls="--")
)
ax.text(
    8.5,
    6.5,
    "IF: C=c\nStatic?",
    fontsize=9,
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
)
ax.text(
    8.5,
    5.5,
    "❌ FAILS\n(dE/dt=0 ≠ E)",
    fontsize=9,
    color="red",
    fontweight="bold",
    bbox=dict(boxstyle="round", facecolor="#FFCCCC", alpha=0.9),
)

# UET → Thermo (WORKS!)
ax.annotate(
    "", xy=(13.25, 3.5), xytext=(9.5, 9), arrowprops=dict(arrowstyle="->", color="green", lw=3)
)
ax.text(
    12,
    7,
    "IF: C=const\n∇Φ=0",
    fontsize=9,
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
)
ax.text(
    11,
    5.5,
    "✅ WORKS!\ndE/dt = -k₁∇S",
    fontsize=9,
    color="green",
    fontweight="bold",
    bbox=dict(boxstyle="round", facecolor="#CCFFCC", alpha=0.9),
)

# UET → Landauer (WORKS!)
ax.annotate(
    "", xy=(12, 6.5), xytext=(10, 9.5), arrowprops=dict(arrowstyle="->", color="green", lw=3)
)
ax.text(
    10.5,
    8.2,
    "✅ DIRECT\nE = kT ln(2) × I",
    fontsize=9,
    color="green",
    fontweight="bold",
    bbox=dict(boxstyle="round", facecolor="#CCFFCC", alpha=0.9),
)

# Newton ↔ Einstein (known relationship)
ax.annotate(
    "", xy=(5.5, 2.25), xytext=(4.5, 2.25), arrowprops=dict(arrowstyle="<->", color="black", lw=1.5)
)
ax.text(
    5,
    1.2,
    "v << c",
    fontsize=8,
    ha="center",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
)

# ============================================================
# Add legend/key
# ============================================================
ax.text(1, 11, "THEORY RELATIONSHIP DIAGRAM", fontsize=18, fontweight="bold")
ax.text(1, 10.3, "How does UET connect to known physics?", fontsize=12, style="italic")

# Legend
legend_y = 8.5
ax.add_patch(plt.Rectangle((1, legend_y), 0.4, 0.3, facecolor="green"))
ax.text(1.6, legend_y + 0.15, "= WORKS (confirmed limit)", fontsize=10, va="center")
ax.add_patch(plt.Rectangle((1, legend_y - 0.5), 0.4, 0.3, facecolor="red"))
ax.text(1.6, legend_y - 0.35, "= FAILS (math doesn't match)", fontsize=10, va="center")

# Key insight box
insight_box = FancyBboxPatch(
    (1, 4), 4, 1.2, boxstyle="round,pad=0.1", facecolor="#FFFFCC", edgecolor="black", linewidth=1
)
ax.add_patch(insight_box)
ax.text(3, 4.9, "💡 KEY INSIGHT", fontsize=10, fontweight="bold", ha="center")
ax.text(3, 4.4, "UET IS THERMODYNAMIC\nnot mechanical!", fontsize=9, ha="center")

plt.tight_layout()

# Save
script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, "theory_relationship.png")
plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Plot saved: {save_path}")

plt.show()
