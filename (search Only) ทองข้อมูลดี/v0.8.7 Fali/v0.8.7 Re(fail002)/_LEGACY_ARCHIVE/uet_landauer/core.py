"""
UET Landauer Core Module
========================

Core equations based on Landauer principle:
- E_bit = k_B × T × ln(2)
- V = M × (C/I)^α

This is the NEW foundation replacing Cahn-Hilliard.

Author: Santa (Original Vision)
Date: 2025-12-30
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional

# Physical Constants
K_B = 1.380649e-23  # Boltzmann constant (J/K)
LN_2 = np.log(2)  # Natural log of 2


@dataclass
class LandauerParams:
    """Parameters for Landauer-based system."""

    T: float = 300.0  # Temperature (K)
    M: float = 1.0  # Mobility
    alpha: float = 1.0  # Exponent in V = M(C/I)^α


def energy_per_bit(T: float = 300.0) -> float:
    """
    Landauer's principle: minimum energy to erase 1 bit.

    E_bit = k_B × T × ln(2)

    Args:
        T: Temperature in Kelvin (default 300K = room temperature)

    Returns:
        Energy in Joules
    """
    return K_B * T * LN_2


def value_function(C: float, I: float, M: float = 1.0, alpha: float = 1.0) -> float:
    """
    The VALUE function - connects C and I.

    V = M × (C/I)^α

    This is the CORE of the theory:
    - C = Communication rate (openness)
    - I = Isolation rate (closure)
    - V = Value/Order gain

    When C↑ and I↓ → V↑ (more value)
    When C↓ and I↑ → V↓ (less value)

    Args:
        C: Communication rate
        I: Isolation rate (must be > 0)
        M: Mobility (ability to change)
        alpha: Exponent (controls nonlinearity)

    Returns:
        V: Value/Order gain
    """
    if I <= 0:
        raise ValueError("I must be positive (no complete isolation)")

    return M * (C / I) ** alpha


def information_energy(I_bits: float, T: float = 300.0) -> float:
    """
    Convert information (bits) to energy via Landauer.

    E = k_B × T × ln(2) × I_bits

    Args:
        I_bits: Information in bits
        T: Temperature in Kelvin

    Returns:
        Energy in Joules
    """
    return energy_per_bit(T) * I_bits


def energy_rate(dI_dt: float, T: float = 300.0) -> float:
    """
    Rate of energy change from information change.

    dE/dt = k_B × T × ln(2) × dI/dt

    This is the bridge between information dynamics and energy.

    Args:
        dI_dt: Rate of information change (bits/second)
        T: Temperature in Kelvin

    Returns:
        Energy rate in Watts (J/s)
    """
    return energy_per_bit(T) * dI_dt


def behavior_energy(behavior_bits: float, T: float = 300.0) -> float:
    """
    Energy cost of behavior recorded in space.

    E_behavior = Σ(k_B T ln 2) × I_behavior

    This implements the core insight:
    "พฤติกรรม → เสื่อมพลังงาน → บันทึกเป็นข้อมูลลงใน Space"

    Args:
        behavior_bits: Information content of behavior (bits)
        T: Temperature in Kelvin

    Returns:
        Energy dissipated/recorded in Joules
    """
    return information_energy(behavior_bits, T)


class LandauerSystem:
    """
    Complete Landauer-based system with C, I, V dynamics.

    Core equations:
    - E = k_B T ln(2) × I
    - V = M × (C/I)^α
    - dE/dt = k_B T ln(2) × dI/dt
    """

    def __init__(self, params: Optional[LandauerParams] = None):
        """Initialize with parameters."""
        self.params = params or LandauerParams()

        # State variables
        self.C = 1.0  # Communication rate
        self.I = 1.0  # Isolation rate
        self.E = 0.0  # Total energy

        # History
        self.history = {"C": [], "I": [], "V": [], "E": [], "t": []}
        self.t = 0.0

    @property
    def V(self) -> float:
        """Current value V = M(C/I)^α."""
        return value_function(self.C, self.I, self.params.M, self.params.alpha)

    @property
    def E_bit(self) -> float:
        """Energy per bit at current temperature."""
        return energy_per_bit(self.params.T)

    def step(self, dt: float = 0.01, dC: Optional[float] = None, dI: Optional[float] = None):
        """
        Advance system by one time step.

        Args:
            dt: Time step
            dC: Change in C (if None, computed from dynamics)
            dI: Change in I (if None, computed from dynamics)
        """
        # Default dynamics: C and I relax towards each other
        if dC is None:
            dC = 0.1 * (self.I - self.C)  # C → I
        if dI is None:
            dI = -0.1 * (self.I - self.C)  # I → C

        # Update state
        self.C += dC * dt
        self.I = max(0.01, self.I + dI * dt)  # I stays positive

        # Energy from information change
        dE = self.E_bit * abs(dI) * dt
        self.E += dE

        # Record history
        self.t += dt
        self.history["C"].append(self.C)
        self.history["I"].append(self.I)
        self.history["V"].append(self.V)
        self.history["E"].append(self.E)
        self.history["t"].append(self.t)

    def run(self, T: float = 10.0, dt: float = 0.01):
        """
        Run simulation for time T.

        Args:
            T: Total simulation time
            dt: Time step
        """
        steps = int(T / dt)
        for _ in range(steps):
            self.step(dt)

    def summary(self) -> dict:
        """Return summary of current state."""
        return {
            "C": self.C,
            "I": self.I,
            "V": self.V,
            "E": self.E,
            "C_I_ratio": self.C / self.I if self.I > 0 else float("inf"),
            "E_bit": self.E_bit,
            "temperature": self.params.T,
        }


# Quick verification
if __name__ == "__main__":
    print("=" * 60)
    print("Landauer Core Module - Verification")
    print("=" * 60)

    # Test 1: Energy per bit
    E_bit = energy_per_bit(300)
    print(f"\n1. Energy per bit at 300K:")
    print(f"   E_bit = k_B × T × ln(2)")
    print(f"   E_bit = {E_bit:.4e} J")
    print(f"   Expected: ~2.87 × 10⁻²¹ J")
    print(f"   ✓ Correct!" if abs(E_bit - 2.87e-21) < 1e-22 else "   ✗ Check!")

    # Test 2: Value function
    V = value_function(C=2.0, I=1.0, M=1.0, alpha=1.0)
    print(f"\n2. Value function V = M(C/I)^α:")
    print(f"   C=2, I=1, M=1, α=1")
    print(f"   V = {V}")
    print(f"   Expected: 2.0")
    print(f"   ✓ Correct!" if V == 2.0 else "   ✗ Check!")

    # Test 3: System simulation
    print(f"\n3. System simulation:")
    system = LandauerSystem()
    system.C = 2.0
    system.I = 1.0
    print(f"   Initial: C={system.C}, I={system.I}, V={system.V:.2f}")

    system.run(T=10, dt=0.01)
    print(f"   Final:   C={system.C:.2f}, I={system.I:.2f}, V={system.V:.2f}")
    print(f"   Energy recorded: {system.E:.4e} J")

    print("\n" + "=" * 60)
    print("Landauer Core Module - READY")
    print("=" * 60)
