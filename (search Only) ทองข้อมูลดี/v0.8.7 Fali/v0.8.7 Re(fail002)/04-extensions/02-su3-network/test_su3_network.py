"""
SU(3)-like Pattern from 3-Field Network Test
Quick experiment to check color-like symmetry emergence
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# Parameters
N = 32  # Grid size (smaller for speed)
beta = 0.5  # Coupling strength
kappa = 0.1
dt = 0.01
T = 300

print("=" * 50)
print("SU(3)-like 3-Field Network Test")
print("=" * 50)

# Initialize 3 fields
np.random.seed(42)
C1 = np.random.randn(N, N) * 0.1 + 0.5
C2 = np.random.randn(N, N) * 0.1 - 0.5
C3 = np.random.randn(N, N) * 0.1 + 0.0


def laplacian_2d(phi):
    return (
        np.roll(phi, 1, axis=0)
        + np.roll(phi, -1, axis=0)
        + np.roll(phi, 1, axis=1)
        + np.roll(phi, -1, axis=1)
        - 4 * phi
    )


def dV(phi):
    """Double-well derivative."""
    return phi * (phi**2 - 1)


# Antisymmetric cyclic coupling: 1→2→3→1
# This creates rotation-like dynamics (SU(3) analog)
beta_matrix = np.array(
    [
        [0, beta, -beta],  # C1 coupled to C2, C3
        [-beta, 0, beta],  # C2 coupled to C1, C3
        [beta, -beta, 0],  # C3 coupled to C1, C2
    ]
)

print(f"Coupling matrix (antisymmetric):\n{beta_matrix}")

# Track
total_charge = []
energies = []
means = []

print("\nRunning 3-field dynamics...")
for t in range(T):
    fields = [C1, C2, C3]

    # Compute derivatives for each field
    dC1 = kappa * laplacian_2d(C1) - dV(C1) - beta * (C1 - C2) + beta * (C1 - C3)
    dC2 = kappa * laplacian_2d(C2) - dV(C2) + beta * (C2 - C1) - beta * (C2 - C3)
    dC3 = kappa * laplacian_2d(C3) - dV(C3) - beta * (C3 - C1) + beta * (C3 - C2)

    C1 = C1 + dt * dC1
    C2 = C2 + dt * dC2
    C3 = C3 + dt * dC3

    # Measure "color charge" analog (total should be conserved)
    Q = np.sum(C1) + np.sum(C2) + np.sum(C3)
    total_charge.append(Q)

    # Track means
    if t % 50 == 0:
        m1, m2, m3 = np.mean(C1), np.mean(C2), np.mean(C3)
        print(f"t={t:3d}: C1={m1:.3f}, C2={m2:.3f}, C3={m3:.3f}, Q={Q:.3f}")
        means.append([m1, m2, m3])

# Analysis
print("\n" + "=" * 50)
print("RESULTS:")
print("=" * 50)

# 1. Conservation check
Q_init = total_charge[0]
Q_final = total_charge[-1]
Q_drift = abs(Q_final - Q_init) / (abs(Q_init) + 1e-10)
print(f"Total charge drift: {Q_drift*100:.2f}%")
print(f"✅ Charge conserved!" if Q_drift < 0.01 else "⚠️ Some charge drift")

# 2. Three-fold symmetry check
means = np.array(means)
# Check if means rotate in (C1, C2, C3) space
rotation_detected = False
for i in range(len(means) - 1):
    v1 = means[i]
    v2 = means[i + 1]
    cross = np.cross(v1, v2)
    if np.linalg.norm(cross) > 0.001:
        rotation_detected = True
        break

print(f"3-fold rotation pattern: {'✅ Detected!' if rotation_detected else '❌ Not detected'}")


# 3. Check "confinement" - isolated fields cost more energy
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
axes[1, 0].set_title('Total "Charge" (should be flat)')
axes[1, 0].set_xlabel("Time")

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
output_path = os.path.join(output_dir, "su3_network_test.png")
plt.savefig(output_path, dpi=150)
print(f"\nPlot saved: {output_path}")
plt.close()
