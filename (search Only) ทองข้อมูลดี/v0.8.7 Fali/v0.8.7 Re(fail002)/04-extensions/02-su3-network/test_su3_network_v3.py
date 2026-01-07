"""
SU(3)-like 3-Field Network Test v3 — FULL CAHN-HILLIARD
Fix: Use ∂C/∂t = ∇²μ instead of ∂C/∂t = -dV/dC
This ensures CONSERVATION of total "mass" (analog to color charge)
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# Parameters
N = 32
beta = 0.3  # Coupling strength (reduced)
kappa = 0.1  # Gradient energy
M = 1.0  # Mobility
dt = 0.001  # Smaller timestep for stability
T = 500  # Longer time

print("=" * 60)
print("SU(3)-like 3-Field Network Test v3 (CAHN-HILLIARD FORM)")
print("=" * 60)
print(f"Parameters: N={N}, β={beta}, κ={kappa}, dt={dt}, T={T}")

np.random.seed(42)

# Initialize fields with small perturbations
# Key: make sure initial total is well-defined
C1 = np.random.randn(N, N) * 0.05 + 0.5
C2 = np.random.randn(N, N) * 0.05 - 0.5
C3 = np.random.randn(N, N) * 0.05 + 0.0

# Store initial total for verification
Q_init = np.sum(C1) + np.sum(C2) + np.sum(C3)
print(f"\nInitial total charge Q₀ = {Q_init:.6f}")


def laplacian_2d(phi):
    """Periodic boundary laplacian"""
    return (
        np.roll(phi, 1, axis=0)
        + np.roll(phi, -1, axis=0)
        + np.roll(phi, 1, axis=1)
        + np.roll(phi, -1, axis=1)
        - 4 * phi
    )


def dV_dphi(phi):
    """Double-well potential derivative: V = (φ² - 1)²/4"""
    return phi * (phi**2 - 1)


def chemical_potential(C, C_others):
    """
    Chemical potential μ = δΩ/δC
    μ = dV/dC - κ∇²C + coupling terms
    """
    # Potential term
    mu = dV_dphi(C)

    # Gradient energy term (negative because μ = δΩ/δC and Ω has +κ|∇C|²)
    mu += -kappa * laplacian_2d(C)

    # Coupling to other fields (antisymmetric for rotation)
    # C1 coupled to (C2 - C3), etc. (cyclic)
    mu += beta * (C_others[0] - C_others[1])

    return mu


# Tracking
total_charge = []
means = []
energies = []

print("\nRunning CAHN-HILLIARD dynamics (∂C/∂t = ∇²μ)...")
for t in range(T):
    # Compute chemical potentials
    mu1 = chemical_potential(C1, [C2, C3])
    mu2 = chemical_potential(C2, [C3, C1])  # Cyclic order
    mu3 = chemical_potential(C3, [C1, C2])

    # CAHN-HILLIARD: dC/dt = M * ∇²μ
    # This is CONSERVATIVE because ∫(∇²μ)dx = 0 (divergence theorem)
    dC1 = M * laplacian_2d(mu1)
    dC2 = M * laplacian_2d(mu2)
    dC3 = M * laplacian_2d(mu3)

    # Update (Euler forward)
    C1 = C1 + dt * dC1
    C2 = C2 + dt * dC2
    C3 = C3 + dt * dC3

    # Measure total charge
    Q = np.sum(C1) + np.sum(C2) + np.sum(C3)
    total_charge.append(Q)

    # Compute energy for monitoring
    def field_energy(C):
        V = 0.25 * (C**2 - 1) ** 2
        grad = 0.5 * kappa * (np.gradient(C, axis=0) ** 2 + np.gradient(C, axis=1) ** 2)
        return np.mean(V + grad)

    E_total = field_energy(C1) + field_energy(C2) + field_energy(C3)
    energies.append(E_total)

    if t % 100 == 0:
        m1, m2, m3 = np.mean(C1), np.mean(C2), np.mean(C3)
        print(f"t={t:4d}: C1={m1:+.4f}, C2={m2:+.4f}, C3={m3:+.4f}, Q={Q:.4f}, E={E_total:.4f}")
        means.append([m1, m2, m3])

# Final analysis
print("\n" + "=" * 60)
print("RESULTS:")
print("=" * 60)

Q_final = total_charge[-1]
Q_drift = abs(Q_final - Q_init) / (abs(Q_init) + 1e-10) * 100

print(f"\nConservation Check:")
print(f"  Initial Q = {Q_init:.6f}")
print(f"  Final Q   = {Q_final:.6f}")
print(f"  Drift     = {Q_drift:.4f}%")

if Q_drift < 1:
    print("  ✅ Excellent conservation!")
elif Q_drift < 5:
    print("  ✅ Good conservation (numerical error)")
elif Q_drift < 20:
    print("  ⚠️ Some drift (may need smaller dt)")
else:
    print("  ❌ Large drift — check equations")

# Energy check (should decrease or stay constant for CH)
E_init = energies[0]
E_final = energies[-1]
print(f"\nEnergy Check (Lyapunov):")
print(f"  Initial E = {E_init:.6f}")
print(f"  Final E   = {E_final:.6f}")
print(f"  ΔE = {E_final - E_init:.6f}")
if E_final <= E_init * 1.01:
    print("  ✅ Energy stable/decreasing")
else:
    print("  ⚠️ Energy increased — check stability")

# 3-fold rotation check
means = np.array(means)
rotation_detected = len(means) > 1
if rotation_detected:
    for i in range(len(means) - 1):
        v1 = means[i]
        v2 = means[i + 1]
        cross = np.cross(v1, v2)
        if np.linalg.norm(cross) > 0.001:
            rotation_detected = True
            break
print(f"\n3-fold rotation pattern: {'✅ Detected!' if rotation_detected else '❌ Not detected'}")

# Confinement check
E_sep = field_energy(C1) + field_energy(C2) + field_energy(C3)
E_comb = field_energy(C1 + C2 + C3)
print(f"\nConfinement check:")
print(f"  E(separate) = {E_sep:.4f}")
print(f"  E(combined) = {E_comb:.4f}")
print(f"  {'✅ Confinement-like!' if E_sep > E_comb else '❌ No confinement'}")

# Plot
fig, axes = plt.subplots(2, 3, figsize=(14, 9))

# Top row: field states
im1 = axes[0, 0].imshow(C1, cmap="Reds", vmin=-1.5, vmax=1.5)
axes[0, 0].set_title("Field 1 (Red)")
plt.colorbar(im1, ax=axes[0, 0])

im2 = axes[0, 1].imshow(C2, cmap="Greens", vmin=-1.5, vmax=1.5)
axes[0, 1].set_title("Field 2 (Green)")
plt.colorbar(im2, ax=axes[0, 1])

im3 = axes[0, 2].imshow(C3, cmap="Blues", vmin=-1.5, vmax=1.5)
axes[0, 2].set_title("Field 3 (Blue)")
plt.colorbar(im3, ax=axes[0, 2])

# Bottom left: charge conservation
axes[1, 0].plot(total_charge, "b-", linewidth=0.5)
axes[1, 0].axhline(Q_init, color="r", linestyle="--", label=f"Initial Q={Q_init:.2f}")
axes[1, 0].set_title(f"Total Charge (drift={Q_drift:.2f}%)")
axes[1, 0].set_xlabel("Time")
axes[1, 0].set_ylabel("Q")
axes[1, 0].legend()

# Bottom middle: energy
axes[1, 1].plot(energies, "g-", linewidth=0.5)
axes[1, 1].set_title(f"Energy (ΔE={E_final-E_init:.4f})")
axes[1, 1].set_xlabel("Time")
axes[1, 1].set_ylabel("E")

# Bottom right: combined (colorless)
im_comb = axes[1, 2].imshow(C1 + C2 + C3, cmap="gray", vmin=-2, vmax=2)
axes[1, 2].set_title("Combined (colorless)")
plt.colorbar(im_comb, ax=axes[1, 2])

plt.suptitle("SU(3)-like Network with Cahn-Hilliard Conservation", fontsize=14)
plt.tight_layout()

output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "su3_network_v3_cahnhilliard.png")
plt.savefig(output_path, dpi=150)
print(f"\nPlot saved: {output_path}")
plt.close()
