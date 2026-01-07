"""
Memory Effects → Lorentz-like Behavior Test
Check if memory kernel creates finite propagation speed
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import deque

# Parameters
N = 64
kappa = 0.5
tau_mem = 10.0  # Memory timescale
gamma_mem = 0.3  # Memory strength
dt = 0.1
T = 200
buffer_size = int(5 * tau_mem / dt)

print("=" * 50)
print("Memory Effects → Lorentz-like Behavior Test")
print("=" * 50)
print(f"Memory timescale: {tau_mem}")
print(f"Buffer size: {buffer_size}")

# Initialize
np.random.seed(42)
C = np.zeros((N, N))
# Create impulse at center
center = N // 2
C[center - 2 : center + 2, center - 2 : center + 2] = 1.0

# History buffer
history = deque(maxlen=buffer_size)
for _ in range(buffer_size):
    history.append(np.zeros((N, N)))

# Precompute memory kernel (exponential)
t_lags = np.arange(buffer_size) * dt
K_mem = (gamma_mem / tau_mem) * np.exp(-t_lags / tau_mem) * dt


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


def memory_integral(history, K):
    """Compute memory term."""
    if len(history) < len(K):
        return np.zeros_like(history[0])
    h_array = np.array(list(history))
    K_rev = K[::-1][: len(h_array)]
    return np.sum([K_rev[i] * h_array[i] for i in range(len(h_array))], axis=0)


# Track wavefront position
snapshots = []
wavefront_pos = []

print("\nRunning with memory...")
for t in range(T):
    # Memory term
    mem_term = memory_integral(history, K_mem)

    # Dynamics with memory
    dC = kappa * laplacian_2d(C) - dV(C) + mem_term
    C = C + dt * dC

    # Store in history
    history.append(C.copy())

    # Track wavefront (where |C| first exceeds threshold along radius)
    if t % 20 == 0:
        # Radial profile from center
        r_max = N // 2
        profile = np.zeros(r_max)
        for r in range(r_max):
            # Average over circle at radius r
            mask = np.zeros((N, N))
            y, x = np.ogrid[:N, :N]
            dist = np.sqrt((x - center) ** 2 + (y - center) ** 2)
            ring = (dist >= r) & (dist < r + 1)
            if np.sum(ring) > 0:
                profile[r] = np.mean(np.abs(C[ring]))

        # Find wavefront (where amplitude drops below threshold)
        threshold = 0.01
        front = np.where(profile > threshold)[0]
        if len(front) > 0:
            wavefront_pos.append(front[-1])
        else:
            wavefront_pos.append(0)

        snapshots.append(C.copy())
        print(f"t={t:3d}: wavefront at r={wavefront_pos[-1]}")

print("\n" + "=" * 50)
print("RESULTS:")
print("=" * 50)

# Calculate propagation speed
if len(wavefront_pos) > 2:
    times = np.arange(len(wavefront_pos)) * 20 * dt
    positions = np.array(wavefront_pos)

    # Linear fit for speed
    valid = positions > 0
    if np.sum(valid) > 2:
        coef = np.polyfit(times[valid], positions[valid], 1)
        c_eff = coef[0]
        print(f"Effective propagation speed: c_eff = {c_eff:.4f}")
        print(f"Expected from κ: c_expected = √(2κ) = {np.sqrt(2*kappa):.4f}")

        if c_eff > 0 and c_eff < 10:
            print("✅ Finite propagation speed detected!")
        else:
            print("⚠️ Speed may be undefined or infinite")
    else:
        print("⚠️ Not enough data for speed estimate")
        c_eff = None
else:
    print("⚠️ Not enough wavefront data")
    c_eff = None

# Check causality (no influence before wavefront arrives)
print("\nCausality check:")
t_early = 1
t_late = len(snapshots) - 1
if len(snapshots) > 2:
    far_point = (center + 20, center)  # 20 units from center
    C_early = snapshots[t_early][far_point] if t_early < len(snapshots) else 0
    C_late = snapshots[t_late][far_point] if t_late < len(snapshots) else 0
    print(f"  Far point at t_early: {C_early:.6f}")
    print(f"  Far point at t_late: {C_late:.6f}")
    if abs(C_early) < 0.001 and abs(C_late) > 0.001:
        print("✅ Causal behavior: distant points affected later!")
    else:
        print("⚠️ Causality unclear")

# Plot
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Snapshots
for i, (ax, snap) in enumerate(
    zip(axes[0], [snapshots[0], snapshots[len(snapshots) // 2], snapshots[-1]])
):
    im = ax.imshow(snap, cmap="RdBu", vmin=-1, vmax=1)
    ax.set_title(f"Snapshot {i+1}")
    plt.colorbar(im, ax=ax)

# Wavefront evolution
axes[1, 0].plot(wavefront_pos)
axes[1, 0].set_xlabel("Time (×20)")
axes[1, 0].set_ylabel("Wavefront position")
axes[1, 0].set_title("Wavefront Propagation")
if c_eff is not None:
    axes[1, 0].plot(
        [0, len(wavefront_pos)],
        [0, c_eff * len(wavefront_pos) * 20 * dt],
        "r--",
        label=f"c={c_eff:.2f}",
    )
    axes[1, 0].legend()

# Radial profile
r = np.arange(N // 2)
profile_init = np.zeros(N // 2)
profile_final = np.zeros(N // 2)
for ri in range(N // 2):
    y, x = np.ogrid[:N, :N]
    dist = np.sqrt((x - center) ** 2 + (y - center) ** 2)
    ring = (dist >= ri) & (dist < ri + 1)
    if np.sum(ring) > 0:
        profile_init[ri] = np.mean(np.abs(snapshots[0][ring]))
        profile_final[ri] = np.mean(np.abs(snapshots[-1][ring]))

axes[1, 1].plot(r, profile_init, label="Initial")
axes[1, 1].plot(r, profile_final, label="Final")
axes[1, 1].set_xlabel("Radius")
axes[1, 1].set_ylabel("|C|")
axes[1, 1].set_title("Radial Profile (wave spreading)")
axes[1, 1].legend()

# Memory kernel
axes[1, 2].plot(t_lags[:50], K_mem[:50])
axes[1, 2].set_xlabel("Time lag τ")
axes[1, 2].set_ylabel("K(τ)")
axes[1, 2].set_title("Memory Kernel (exponential)")

plt.tight_layout()
import os

output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "lorentz_memory_test.png")
plt.savefig(output_path, dpi=150)
print(f"\nPlot saved: {output_path}")
plt.close()
