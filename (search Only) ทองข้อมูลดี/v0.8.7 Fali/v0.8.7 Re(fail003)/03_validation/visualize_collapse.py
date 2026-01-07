"""
Visual Comparison: UECT vs Newton vs Einstein
==============================================

Create plots showing why UECT doesn't match Newton/Einstein.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Create figure with 2 subplots
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# ============================================================
# PLOT 1: UECT vs Newton Energy over Time
# ============================================================
ax1 = axes[0]

# Parameters
M = 1.0  # kg
a = 2.0  # m/s² (constant acceleration)
t = np.linspace(0, 5, 100)  # 0 to 5 seconds

# Newton: E = ½mv² = ½m(at)² = ½ma²t²
E_newton = 0.5 * M * (a * t) ** 2

# UECT: dE/dt = Ma² → E = Ma²t (integrating from 0)
E_uect = M * a**2 * t

ax1.plot(t, E_newton, "b-", linewidth=3, label="Newton: E = ½mv² = ½ma²t²")
ax1.plot(t, E_uect, "r--", linewidth=3, label="UECT: E = Ma²t")
ax1.fill_between(t, E_newton, E_uect, alpha=0.3, color="red", label="Difference (Error)")

ax1.set_xlabel("Time (s)", fontsize=12)
ax1.set_ylabel("Energy (J)", fontsize=12)
ax1.set_title("Newton vs UECT Energy\n(M=1kg, a=2m/s²)", fontsize=14, fontweight="bold")
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 5)
ax1.set_ylim(0, 60)

# Add annotation
ax1.annotate(
    "At t=5s:\nNewton: 50J\nUECT: 20J\n(60% error!)",
    xy=(5, 50),
    xytext=(3.5, 40),
    fontsize=10,
    arrowprops=dict(arrowstyle="->", color="black"),
    bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.8),
)

# ============================================================
# PLOT 2: Power Comparison (dE/dt)
# ============================================================
ax2 = axes[1]

# Newton: dE/dt = mv·a = m(at)·a = ma²t
dE_dt_newton = M * a**2 * t

# UECT: dE/dt = Ma² (constant!)
dE_dt_uect = np.ones_like(t) * M * a**2

ax2.plot(t, dE_dt_newton, "b-", linewidth=3, label="Newton: P = mva = ma²t")
ax2.plot(t, dE_dt_uect, "r--", linewidth=3, label="UECT: P = Ma² (constant!)")
ax2.fill_between(t, dE_dt_newton, dE_dt_uect, alpha=0.3, color="red", label="Difference")

ax2.set_xlabel("Time (s)", fontsize=12)
ax2.set_ylabel("Power dE/dt (W)", fontsize=12)
ax2.set_title("Power: Newton vs UECT\n(Why they differ)", fontsize=14, fontweight="bold")
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, 5)
ax2.set_ylim(0, 25)

# Add annotation
ax2.annotate(
    "UECT: constant power\nNewton: power grows with v",
    xy=(2.5, 4),
    xytext=(1, 12),
    fontsize=10,
    arrowprops=dict(arrowstyle="->", color="black"),
    bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.8),
)

# Add main title
fig.suptitle("Why UECT Does NOT Collapse to Newton", fontsize=16, fontweight="bold", y=1.02)

plt.tight_layout()

# Save
script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, "uect_vs_newton.png")
plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Plot saved: {save_path}")

# ============================================================
# PLOT 3: Einstein Comparison
# ============================================================
fig2, ax3 = plt.subplots(figsize=(10, 6))

# Speed of light
c = 299792458  # m/s

# Different accelerations to reach C
v = np.linspace(0, c, 100)

# Newton kinetic energy: E = ½mv²
E_newton_kin = 0.5 * M * v**2

# Einstein rest energy: E = mc² (constant!)
E_einstein = M * c**2 * np.ones_like(v)

# Einstein total energy (relativistic): E = γmc²
gamma = 1 / np.sqrt(1 - (v / c) ** 2 + 1e-10)  # Add small number to avoid div by 0
E_einstein_rel = gamma * M * c**2

ax3.semilogy(v / c, E_newton_kin, "b-", linewidth=3, label="Newton: E = ½mv²")
ax3.axhline(
    y=M * c**2,
    color="g",
    linestyle="--",
    linewidth=3,
    label=f"Einstein Rest: E = mc² = {M*c**2:.2e} J",
)
ax3.semilogy(v / c, E_einstein_rel, "r-", linewidth=3, label="Einstein Relativistic: E = γmc²")

ax3.set_xlabel("v/c (fraction of light speed)", fontsize=12)
ax3.set_ylabel("Energy (J) [log scale]", fontsize=12)
ax3.set_title(
    "Energy vs Velocity: Einstein vs Newton\nE=mc² is REST energy, not kinetic!",
    fontsize=14,
    fontweight="bold",
)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, 0.999)

# Annotation
ax3.annotate(
    "E = mc² is the MINIMUM energy\n(when v=0, particle at rest)",
    xy=(0.1, M * c**2),
    xytext=(0.3, M * c**2 * 0.01),
    fontsize=10,
    arrowprops=dict(arrowstyle="->", color="black"),
    bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.8),
)

plt.tight_layout()

save_path2 = os.path.join(script_dir, "einstein_energy.png")
plt.savefig(save_path2, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Plot saved: {save_path2}")

print("\nDone! Check the plots.")
plt.show()
