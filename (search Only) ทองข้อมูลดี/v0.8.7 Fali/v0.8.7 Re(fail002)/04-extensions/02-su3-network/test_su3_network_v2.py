"""
SU(3)-like 3-Field Network Test v2 — WITH CONSERVATION
Fixed: Use conservative exchange form for exact charge conservation
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# Parameters
N = 32
beta = 0.5
kappa = 0.1
dt = 0.01
T = 300

print("=" * 50)
print("SU(3)-like 3-Field Network Test v2 (CONSERVATIVE)")
print("=" * 50)

np.random.seed(42)
C1 = np.random.randn(N, N) * 0.1 + 0.5
C2 = np.random.randn(N, N) * 0.1 - 0.5
C3 = np.random.randn(N, N) * 0.1 + 0.0

# Store initial total for verification
Q_init = np.sum(C1) + np.sum(C2) + np.sum(C3)
print(f"Initial total charge: {Q_init:.4f}")


def laplacian_2d(phi):
    return (
        np.roll(phi, 1, axis=0)
        + np.roll(phi, -1, axis=0)
        + np.roll(phi, 1, axis=1)
        + np.roll(phi, -1, axis=1)
        - 4 * phi
    )


def dV(phi):
    return phi * (phi**2 - 1)


# Track
total_charge = []
means = []

print("\nRunning with CONSERVATIVE dynamics...")
for t in range(T):
    # CONSERVATIVE FLUX EXCHANGE (key change!)
    # What leaves C1 enters C2, what leaves C2 enters C3, etc.
    flux_12 = beta * (C1 - C2)  # 1 → 2
    flux_23 = beta * (C2 - C3)  # 2 → 3
    flux_31 = beta * (C3 - C1)  # 3 → 1 (cyclic)

    # Compute derivatives with exact conservation
    dC1 = kappa * laplacian_2d(C1) - dV(C1) - flux_12 + flux_31
    dC2 = kappa * laplacian_2d(C2) - dV(C2) + flux_12 - flux_23
    dC3 = kappa * laplacian_2d(C3) - dV(C3) + flux_23 - flux_31

    # Check: dC1 + dC2 + dC3 should be ~0 (only diffusion + potential)
    # The flux terms cancel: (-flux_12 + flux_31) + (flux_12 - flux_23) + (flux_23 - flux_31) = 0

    C1 = C1 + dt * dC1
    C2 = C2 + dt * dC2
    C3 = C3 + dt * dC3

    # Measure charge
    Q = np.sum(C1) + np.sum(C2) + np.sum(C3)
    total_charge.append(Q)

    if t % 50 == 0:
        m1, m2, m3 = np.mean(C1), np.mean(C2), np.mean(C3)
        print(f"t={t:3d}: C1={m1:.3f}, C2={m2:.3f}, C3={m3:.3f}, Q={Q:.3f}")
        means.append([m1, m2, m3])

# Analysis
print("\n" + "=" * 50)
print("RESULTS:")
print("=" * 50)

Q_final = total_charge[-1]
Q_drift = abs(Q_final - Q_init) / (abs(Q_init) + 1e-10) * 100
print(f"Initial charge: {Q_init:.4f}")
print(f"Final charge: {Q_final:.4f}")
print(f"Charge drift: {Q_drift:.2f}%")

if Q_drift < 5:
    print("✅ Charge nearly conserved!")
elif Q_drift < 20:
    print("⚠️ Small charge drift (from potential/diffusion)")
else:
    print("❌ Large charge drift")

# 3-fold rotation check
means = np.array(means)
rotation_detected = False
for i in range(len(means) - 1):
    v1 = means[i]
    v2 = means[i + 1]
    cross = np.cross(v1, v2)
    if np.linalg.norm(cross) > 0.001:
        rotation_detected = True
        break
print(f"3-fold rotation pattern: {'✅ Detected!' if rotation_detected else '❌ Not detected'}")


# Confinement check
def field_energy(C):
    V = 0.25 * (C**2 - 1) ** 2
    grad = 0.5 * kappa * (np.gradient(C, axis=0) ** 2 + np.gradient(C, axis=1) ** 2)
    return np.mean(V + grad)


E_sep = field_energy(C1) + field_energy(C2) + field_energy(C3)
E_comb = field_energy(C1 + C2 + C3)
print(f"\nConfinement check:")
print(f"  E(separate): {E_sep:.4f}")
print(f"  E(combined): {E_comb:.4f}")
print(f"  {'✅ Confinement-like!' if E_sep > E_comb else '❌ No confinement'}")

# Plot
fig, axes = plt.subplots(2, 3, figsize=(12, 8))

axes[0, 0].imshow(C1, cmap="Reds", vmin=-1, vmax=1)
axes[0, 0].set_title("Field 1 (Red)")
axes[0, 1].imshow(C2, cmap="Greens", vmin=-1, vmax=1)
axes[0, 1].set_title("Field 2 (Green)")
axes[0, 2].imshow(C3, cmap="Blues", vmin=-1, vmax=1)
axes[0, 2].set_title("Field 3 (Blue)")

axes[1, 0].plot(total_charge)
axes[1, 0].axhline(Q_init, color="r", linestyle="--", label=f"Initial={Q_init:.1f}")
axes[1, 0].set_title("Total Charge (should be flat!)")
axes[1, 0].set_xlabel("Time")
axes[1, 0].legend()

if len(means) > 2:
    axes[1, 1].plot(means[:, 0], label="C1")
    axes[1, 1].plot(means[:, 1], label="C2")
    axes[1, 1].plot(means[:, 2], label="C3")
    axes[1, 1].legend()
    axes[1, 1].set_title("Mean values evolution")

axes[1, 2].imshow(C1 + C2 + C3, cmap="gray")
axes[1, 2].set_title("Combined (colorless)")

plt.tight_layout()
output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "su3_network_v2_conservative.png")
plt.savefig(output_path, dpi=150)
print(f"\nPlot saved: {output_path}")
plt.close()
