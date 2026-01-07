"""
Mexican Hat + Symmetry Breaking Test
Quick experiment for UET extensions
"""

import numpy as np
import matplotlib.pyplot as plt

# Parameters
N = 64  # Grid size
mu2 = 1.0  # Mexican hat depth
lam = 1.0  # Quartic coefficient
kappa = 0.5  # Diffusion
dt = 0.01
T = 500  # Steps

# VEV (vacuum expectation value)
v = np.sqrt(mu2 / (2 * lam))
print(f"Expected VEV: |φ| = {v:.4f}")

# Initialize near zero (symmetric state)
np.random.seed(42)
C = 0.01 * np.random.randn(N, N)  # Real part
I = 0.01 * np.random.randn(N, N)  # Imaginary part


def laplacian_2d(phi):
    """2D Laplacian with periodic BC."""
    return (
        np.roll(phi, 1, axis=0)
        + np.roll(phi, -1, axis=0)
        + np.roll(phi, 1, axis=1)
        + np.roll(phi, -1, axis=1)
        - 4 * phi
    )


def dV_dC(C, I):
    """Mexican hat derivative w.r.t C."""
    r_sq = C**2 + I**2
    return C * (-2 * mu2 + 4 * lam * r_sq)


def dV_dI(C, I):
    """Mexican hat derivative w.r.t I."""
    r_sq = C**2 + I**2
    return I * (-2 * mu2 + 4 * lam * r_sq)


def energy(C, I):
    """Total energy (Mexican Hat)."""
    r_sq = C**2 + I**2
    V = -mu2 * r_sq + lam * r_sq**2
    grad_C = 0.5 * kappa * (np.gradient(C, axis=0) ** 2 + np.gradient(C, axis=1) ** 2)
    grad_I = 0.5 * kappa * (np.gradient(I, axis=0) ** 2 + np.gradient(I, axis=1) ** 2)
    return np.mean(V + grad_C + grad_I)


# Track evolution
energies = []
radii = []
angles = []

print("Running Mexican Hat dynamics...")
for t in range(T):
    # Cahn-Hilliard with Mexican Hat
    mu_C = dV_dC(C, I) - kappa * laplacian_2d(C)
    mu_I = dV_dI(C, I) - kappa * laplacian_2d(I)

    C = C + dt * laplacian_2d(mu_C)
    I = I + dt * laplacian_2d(mu_I)

    # Track
    if t % 10 == 0:
        E = energy(C, I)
        r = np.mean(np.sqrt(C**2 + I**2))
        theta = np.mean(np.arctan2(I, C))
        energies.append(E)
        radii.append(r)
        angles.append(theta)

        if t % 100 == 0:
            print(f"t={t:4d}: E={E:.4f}, |φ|={r:.4f}, θ={theta:.2f}")

print("\n" + "=" * 50)
print("RESULTS:")
print("=" * 50)
print(f"Final radius |φ|: {radii[-1]:.4f} (expected: {v:.4f})")
print(f"Final angle θ: {angles[-1]:.4f} rad = {np.degrees(angles[-1]):.1f}°")
print(f"Energy decrease: {energies[0]:.4f} → {energies[-1]:.4f}")
print(f"Symmetry broken: θ ≠ 0 → {'YES!' if abs(angles[-1]) > 0.01 else 'NO'}")

# Check Goldstone mode
print("\n" + "=" * 50)
print("GOLDSTONE CHECK:")
print("=" * 50)

# Perturb in radial direction
C_r = C + 0.1 * C / (np.sqrt(C**2 + I**2) + 1e-10)
I_r = I + 0.1 * I / (np.sqrt(C**2 + I**2) + 1e-10)
E_radial = energy(C_r, I_r)

# Perturb in angular direction
theta_pert = 0.1
C_a = C * np.cos(theta_pert) - I * np.sin(theta_pert)
I_a = C * np.sin(theta_pert) + I * np.cos(theta_pert)
E_angular = energy(C_a, I_a)

E_base = energy(C, I)
print(f"Base energy: {E_base:.6f}")
print(f"Radial perturbation: {E_radial:.6f} (diff: {E_radial - E_base:.6f})")
print(f"Angular perturbation: {E_angular:.6f} (diff: {E_angular - E_base:.6f})")

if abs(E_angular - E_base) < abs(E_radial - E_base) * 0.1:
    print("✅ GOLDSTONE MODE CONFIRMED! Angular mode is nearly massless!")
else:
    print("⚠️ Angular mode has some mass")

# Plot
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Energy
axes[0, 0].plot(energies)
axes[0, 0].set_xlabel("Time (×10)")
axes[0, 0].set_ylabel("Energy")
axes[0, 0].set_title("Energy Decrease (Lyapunov)")
axes[0, 0].axhline(-(mu2**2) / (4 * lam), color="r", linestyle="--", label="Min")

# Radius
axes[0, 1].plot(radii)
axes[0, 1].axhline(v, color="r", linestyle="--", label=f"VEV = {v:.2f}")
axes[0, 1].set_xlabel("Time (×10)")
axes[0, 1].set_ylabel("|φ|")
axes[0, 1].set_title("Radius → VEV (Symmetry Breaking)")
axes[0, 1].legend()

# Angle
axes[0, 2].plot(np.degrees(angles))
axes[0, 2].set_xlabel("Time (×10)")
axes[0, 2].set_ylabel("θ (degrees)")
axes[0, 2].set_title("Angle Selection (Random!)")

# Final C field
im1 = axes[1, 0].imshow(C, cmap="RdBu", vmin=-1, vmax=1)
axes[1, 0].set_title("Final C (Real part)")
plt.colorbar(im1, ax=axes[1, 0])

# Final I field
im2 = axes[1, 1].imshow(I, cmap="RdBu", vmin=-1, vmax=1)
axes[1, 1].set_title("Final I (Imaginary part)")
plt.colorbar(im2, ax=axes[1, 1])

# Final |φ|
r_field = np.sqrt(C**2 + I**2)
im3 = axes[1, 2].imshow(r_field, cmap="hot", vmin=0, vmax=1)
axes[1, 2].set_title(f"Final |φ| (should → {v:.2f})")
plt.colorbar(im3, ax=axes[1, 2])

plt.tight_layout()
import os

output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "mexican_hat_test.png")
plt.savefig(output_path, dpi=150)
print(f"\nPlot saved to: {output_path}")
plt.close()
