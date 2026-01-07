"""
UET Landauer Thermodynamics Module
==================================

Thermodynamic connections for UET:
- Law 0: Equilibrium from behavior
- Law 1: Energy → Information (Landauer)
- Law 2: Behavior → Entropy increase
- Law 3: Space as order source

Author: Santa (Original Vision)
Date: 2025-12-30
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple

from .core import K_B, LN_2, energy_per_bit


@dataclass
class ThermodynamicState:
    """State of a thermodynamic system."""

    E: float = 0.0  # Total energy (J)
    S: float = 0.0  # Entropy (J/K)
    I_bits: float = 0.0  # Information content (bits)
    T: float = 300.0  # Temperature (K)


def law_0_equilibrium(states: list) -> bool:
    """
    Law 0: Thermal Equilibrium.

    Two systems in contact will reach the same temperature.
    In UET terms: behaviors exchange information until balanced.

    Args:
        states: List of ThermodynamicState objects

    Returns:
        True if all systems are in equilibrium (same T)
    """
    if len(states) < 2:
        return True

    T_ref = states[0].T
    return all(np.isclose(s.T, T_ref, rtol=0.01) for s in states)


def law_1_conservation(
    E_initial: float, E_final: float, I_initial: float, I_final: float, T: float = 300.0
) -> Tuple[bool, float]:
    """
    Law 1: Energy Conservation (with Landauer).

    Energy is not lost, but can convert to information:
    ΔE = k_B T ln(2) × ΔI

    Args:
        E_initial: Initial energy
        E_final: Final energy
        I_initial: Initial information (bits)
        I_final: Final information (bits)
        T: Temperature

    Returns:
        (conserved: bool, error: float)
    """
    dE = E_final - E_initial
    dI = I_final - I_initial

    # Expected energy change from information change
    E_expected = energy_per_bit(T) * dI

    # Check conservation
    error = abs(dE - E_expected)
    conserved = error < 1e-25  # Very small tolerance

    return conserved, error


def law_2_entropy_increase(
    S_initial: float, S_final: float, behavior_occurred: bool = True
) -> bool:
    """
    Law 2: Entropy Increase.

    Total entropy of isolated system never decreases.
    In UET: every behavior increases entropy (leaves trace).

    "พฤติกรรม → เสื่อมพลังงาน → เพิ่ม entropy → บันทึกใน Space"

    Args:
        S_initial: Initial entropy
        S_final: Final entropy
        behavior_occurred: Whether any behavior happened

    Returns:
        True if law is satisfied
    """
    dS = S_final - S_initial

    if behavior_occurred:
        # If behavior happened, entropy must increase
        return dS > 0
    else:
        # No behavior = no change (reversible limit)
        return dS >= 0


def law_3_space_is_order(space_info: float, system_disorder: float) -> float:
    """
    Law 3: Space as Ultimate Order.

    At T=0 or maximum order, Space contains all information.
    Space brings disorder from behavior back to order.

    "Space มีความเป็นระเบียบสูงสุด - จัดการทุกอย่าง"

    Args:
        space_info: Information stored in Space
        system_disorder: Disorder in system

    Returns:
        Total order (Space info balances disorder)
    """
    return space_info - system_disorder


def behavior_to_entropy(behavior_bits: float, T: float = 300.0) -> float:
    """
    Convert behavior (information) to entropy change.

    ΔS = k_B × ln(2) × I_behavior

    This is the core insight:
    "ทุกพฤติกรรมทิ้งร่องรอย = เพิ่ม entropy"

    Args:
        behavior_bits: Information content of behavior
        T: Temperature (for reference)

    Returns:
        Entropy change in J/K
    """
    return K_B * LN_2 * behavior_bits


def entropy_to_information(dS: float) -> float:
    """
    Convert entropy change to information.

    I = ΔS / (k_B × ln(2))

    Args:
        dS: Entropy change in J/K

    Returns:
        Information in bits
    """
    return dS / (K_B * LN_2)


class ThermodynamicSystem:
    """
    System following all 4 thermodynamic laws with Landauer bridge.
    """

    def __init__(self, T: float = 300.0):
        """Initialize at temperature T."""
        self.state = ThermodynamicState(T=T)
        self.history = []

    def add_behavior(self, bits: float):
        """
        Add a behavior that produces information.

        This:
        1. Uses energy (Law 1)
        2. Increases entropy (Law 2)
        3. Records in Space (Law 3)
        """
        # Energy cost (Landauer)
        dE = energy_per_bit(self.state.T) * bits
        self.state.E += dE

        # Entropy increase
        dS = behavior_to_entropy(bits, self.state.T)
        self.state.S += dS

        # Information recorded
        self.state.I_bits += bits

        # Record history
        self.history.append(
            {
                "bits": bits,
                "dE": dE,
                "dS": dS,
                "total_E": self.state.E,
                "total_S": self.state.S,
                "total_I": self.state.I_bits,
            }
        )

    def verify_laws(self) -> dict:
        """Verify all thermodynamic laws are satisfied."""
        results = {}

        # Law 1: Check energy-info conservation
        if len(self.history) >= 2:
            first = self.history[0]
            last = self.history[-1]
            conserved, error = law_1_conservation(
                0, last["total_E"], 0, last["total_I"], self.state.T
            )
            results["law_1"] = {"conserved": conserved, "error": error}
        else:
            results["law_1"] = {"conserved": True, "error": 0}

        # Law 2: Check entropy always increased
        entropy_ok = True
        for i in range(1, len(self.history)):
            if self.history[i]["total_S"] < self.history[i - 1]["total_S"]:
                entropy_ok = False
                break
        results["law_2"] = {"entropy_increased": entropy_ok}

        return results


# Quick verification
if __name__ == "__main__":
    print("=" * 60)
    print("Thermodynamics Module - Verification")
    print("=" * 60)

    # Test behavior → entropy → information chain
    system = ThermodynamicSystem(T=300)

    print("\nAdding behaviors...")
    for i in range(5):
        bits = 1000 * (i + 1)
        system.add_behavior(bits)
        print(
            f"  Behavior {i+1}: {bits} bits → E={system.state.E:.4e} J, S={system.state.S:.4e} J/K"
        )

    print("\nVerifying thermodynamic laws...")
    results = system.verify_laws()
    print(f"  Law 1 (Energy conservation): {'✓' if results['law_1']['conserved'] else '✗'}")
    print(f"  Law 2 (Entropy increase): {'✓' if results['law_2']['entropy_increased'] else '✗'}")

    print("\n" + "=" * 60)
    print("Thermodynamics Module - READY")
    print("=" * 60)
