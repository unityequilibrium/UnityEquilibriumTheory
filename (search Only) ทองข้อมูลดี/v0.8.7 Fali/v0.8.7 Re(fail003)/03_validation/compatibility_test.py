import numpy as np
import matplotlib.pyplot as plt
import os

"""
COMPATIBILITY TEST: Newton + UET
--------------------------------
This script demonstrates that UET and Newtonian physics can coexist
in the same simulation without contradicting each other.

Layer 1: Basic Physics (Newton)
- A particle moving in a potential well
- Variables: x, v, m, E, F
- Laws: F = ma, E = 0.5mv^2 + U

Layer 2: UET (System/Info)
- The same particle's interaction with the environment
- Variables: C (coupling), I (friction), V (value), Omega (balance)
- Laws: V = M(C/I)^alpha, Omega tracks disequilibrium

Goal: Show that Layer 2 adds information (Efficiency/Value) 
without changing Layer 1's ground truth (Energy conservation).
"""


class PhysSystem:
    def __init__(self, mass=1.0, k=1.0):
        # Physics State
        self.m = mass
        self.k = k  # Spring constant
        self.x = 1.0  # Position
        self.v = 0.0  # Velocity
        self.t = 0.0

        # UET State (Overlay)
        self.C = 0.5  # Initial coupling/openness [0-1]
        self.I = 0.1  # Initial internal friction [0-1]

    def get_forces(self):
        # Newton: F = -kx - gamma*v (if we had damping)
        # Let's assume ideal Newton first (conservative)
        return -self.k * self.x

    def get_energy(self):
        # Newton: E = KE + PE
        ke = 0.5 * self.m * self.v**2
        pe = 0.5 * self.k * self.x**2
        return ke + pe

    def update_physics(self, dt):
        """Standard Verlet integration for Newton"""
        a = self.get_forces() / self.m
        self.x += self.v * dt + 0.5 * a * dt**2

        # New acceleration
        a_new = self.get_forces() / self.m
        self.v += 0.5 * (a + a_new) * dt
        self.t += dt

    def update_uet(self, dt):
        """
        UET Layer: Monitors the system and calculates Value/Omega
        Does NOT change x or v directly (unless we couple them later).

        Scenario:
        - High Velocity = High Interaction Potential (C increases with |v|)
        - High Displacement = High Stress (I increases with |x|)
        """
        # 1. Update C (Coupling) based on physics state
        # Rule: Faster movement = more interaction chance
        target_C = 0.1 + 0.8 * (abs(self.v) / 2.0)  # Normalized roughly
        target_C = np.clip(target_C, 0.01, 1.0)
        self.C += (target_C - self.C) * 2.0 * dt  # Lagged update

        # 2. Update I (Insulation/Stress) based on physics state
        # Rule: Further from center = more stress/resistance
        target_I = 0.1 + 0.8 * (abs(self.x) / 1.5)
        target_I = np.clip(target_I, 0.01, 1.0)
        self.I += (target_I - self.I) * 2.0 * dt

        # 3. Calculate Value (V)
        # V = M * (C/I)^alpha
        # Let's say M=1, alpha=1 for simplicity
        self.V = 1.0 * (self.C / self.I)

        # 4. Calculate Omega (Disequilibrium)
        # Hypothesis: Value reduces Omega.
        # Omega = 1/V (Simple mapping) or Omega = Energy / V
        # Let's use: Omega = TotalEnergy / V
        # Meaning: How much energy costs to maintain this value?
        energy = self.get_energy()
        if self.V > 1e-6:
            self.Omega = energy / self.V
        else:
            self.Omega = 999.0

    def step(self, dt):
        self.update_physics(dt)
        self.update_uet(dt)


def run_simulation():
    sys = PhysSystem()
    dt = 0.05
    steps = 200

    history = {"t": [], "x": [], "E": [], "C": [], "I": [], "V": [], "Omega": []}  # Physics  # UET

    for _ in range(steps):
        sys.step(dt)

        # Record
        history["t"].append(sys.t)
        history["x"].append(sys.x)
        history["E"].append(sys.get_energy())
        history["C"].append(sys.C)
        history["I"].append(sys.I)
        history["V"].append(sys.V)
        history["Omega"].append(sys.Omega)

    return history


def plot_results(h):
    fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    # Plot 1: Physics (The "Truth")
    axs[0].plot(h["t"], h["x"], label="Position (x)", color="blue")
    axs[0].plot(h["t"], h["E"], label="Total Energy (E)", color="black", linestyle="--")
    axs[0].set_ylabel("Newtonian Units")
    axs[0].set_title("Layer 1: Established Physics (Conservative)")
    axs[0].legend()
    axs[0].grid(True)

    # Plot 2: UET Variables (System State)
    axs[1].plot(h["t"], h["C"], label="Openness (C) [v-based]", color="green")
    axs[1].plot(h["t"], h["I"], label="Stress (I) [x-based]", color="red")
    axs[1].set_ylabel("UET Units [0-1]")
    axs[1].set_title("Layer 2: UET System State")
    axs[1].legend()
    axs[1].grid(True)

    # Plot 3: Value and Balance
    axs[2].plot(h["t"], h["V"], label="Value (V = C/I)", color="purple", linewidth=2)
    # Scale Omega to fit
    omega_scaled = np.array(h["Omega"]) / np.max(h["Omega"]) * np.max(h["V"])
    axs[2].plot(
        h["t"], omega_scaled, label="Disequilibrium (Omega) [Scaled]", color="orange", linestyle=":"
    )
    axs[2].set_ylabel("Score")
    axs[2].set_title("Layer 3: Value & Balance (Derived)")
    axs[2].legend()
    axs[2].grid(True)

    plt.xlabel("Time (s)")
    plt.tight_layout()

    output_dir = "research_v3/03_validation/results"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f"{output_dir}/compatibility_test.png")
    print(f"Plot saved to {output_dir}/compatibility_test.png")


if __name__ == "__main__":
    print("Running Newton + UET Compatibility Test...")
    hist = run_simulation()

    # Assertion Checks
    # 1. Physics must be conserved (Energy constant)
    e_variance = np.var(hist["E"])
    print(f"Energy Variance: {e_variance:.6f}")
    if e_variance < 1e-4:
        print("✅ PASS: Newtonian Energy is conserved (UET did not interfere)")
    else:
        print("❌ FAIL: Energy was modified! (Check code)")

    # 2. UET must produce variable output
    v_variance = np.var(hist["V"])
    print(f"Value Variance: {v_variance:.6f}")
    if v_variance > 0.01:
        print("✅ PASS: UET layer is active and describing system state")
    else:
        print("❌ FAIL: UET layer is static")

    plot_results(hist)
