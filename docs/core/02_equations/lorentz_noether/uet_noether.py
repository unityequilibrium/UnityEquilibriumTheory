"""
Legacy UET Noether Diagnostic Module
====================================

This module preserves early spatial diagnostics for compatibility and code
archaeology. It does not currently derive Noether currents from the same
covariant action and physical dynamics used by the GR correspondence program.
Its gradient-flow updates and real-field charge proxy are not conservation
proofs.

Purpose:
- Derive Noether currents for all symmetries
- Check conservation laws numerically
- Provide the theoretical foundation for UET

Theory:
Noether's Theorem: For every continuous symmetry, there is a conserved current.

For symmetry transformation: δC = ε·X(C)
Noether current: J^μ = (∂L/∂(∂_μC))·X(C) - K^μ
Conservation: ∂_μ J^μ = 0
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Tuple, Callable
from dataclasses import dataclass

from docs.core.uet_parameters import UETParameters


LEGACY_NOETHER_EVIDENCE_STATUS = "BLOCKED_FOR_CONSERVATION_PROOF_CLAIMS"


@dataclass
class NoetherCurrent:
    """Represents a Noether current."""
    name: str
    current: np.ndarray
    divergence: float
    is_conserved: bool
    symmetry_type: str


class UETNoether:
    """Legacy spatial diagnostics; not a covariant Noether proof."""

    def __init__(self, params: UETParameters = None):
        if params is None:
            self.params = UETParameters(kappa=1.0, beta=1.0)
        else:
            self.params = params

    def lagrangian_density(
        self,
        C: np.ndarray,
        grad_C: np.ndarray,
        I: np.ndarray = None
    ) -> np.ndarray:
        """
        Compute Lagrangian density for UET.

        L = (κ/2)|∇C|² + (1/2)|∇I|² - V(C) - (1/2)m_I²I² + β C·I

        where V(C) = (α/2)(|C|²-C₀²)² + (γ/4)(|C|²-C₀²)⁴
        """
        from docs.core.uet_master_equation import potential_V

        V = potential_V(C, self.params)
        kinetic_C = (self.params.kappa / 2) * grad_C**2

        if I is not None:
            grad_I = np.gradient(I, np.gradient(np.arange(len(I)))) # Simplified dx
            kinetic_I = 0.5 * grad_I**2
            mass_I = 0.5 * self.params.kappa_I * I**2
            interaction = self.params.beta * C * I
        else:
            kinetic_I = 0
            mass_I = 0
            interaction = 0

        L = kinetic_C + kinetic_I - V - mass_I + interaction

        return L

    def noether_current_general(
        self,
        C: np.ndarray,
        X: Callable[[np.ndarray], np.ndarray],
        dx: float
    ) -> NoetherCurrent:
        """
        Compute Noether current for general symmetry transformation.

        For transformation δC = ε·X(C):
        J = (∂L/∂(∇C))·X(C)

        Args:
            C: Field
            X: Transformation function X(C)
            dx: Spatial step

        Returns:
            NoetherCurrent object
        """
        # Compute gradient of Lagrangian
        grad_C = np.gradient(C, dx)

        # ∂L/∂(∇C) = κ·∇C
        dL_dgrad = self.params.kappa * grad_C

        # Noether current
        J = dL_dgrad * X(C)

        # Divergence
        divergence = np.gradient(J, dx).sum()

        # Check conservation
        is_conserved = np.abs(divergence) < 1e-8

        return NoetherCurrent(
            name="General",
            current=J,
            divergence=divergence,
            is_conserved=is_conserved,
            symmetry_type="Continuous"
        )

    def energy_momentum_tensor(
        self,
        C: np.ndarray,
        dx: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Derive energy-momentum tensor for translation symmetry.

        For translation invariance (time and space), we get:
        - Energy conservation: ∂E/∂t = 0
        - Momentum conservation: ∂P/∂t = 0

        Energy density: T^00 = Σ (∂L/∂(∂_0φ_i))∂_0φ_i - L
        Momentum density: T^0i = Σ (∂L/∂(∂_iφ_i))∂_0φ_i
        """
        # Compute gradients
        grad_C = np.gradient(C, dx)

        # Lagrangian density (Assume I is zero for simple tensor check if not provided)
        L = self.lagrangian_density(C, grad_C)

        # Hamiltonian density (H = Σ π_i φ_i_dot - L)
        # For static gradient check: H = (κ/2)|∇C|² + V(C)
        energy_density = (self.params.kappa / 2) * grad_C**2 - L + (self.params.kappa * grad_C**2)

        # Momentum density p = ∂L/∂(∇C)
        momentum_density = self.params.kappa * grad_C

        return energy_density, momentum_density

    def check_energy_conservation(
        self,
        C: np.ndarray,
        dx: float,
        dt: float = 0.01,
        steps: int = 10
    ) -> Dict:
        """
        Check energy conservation from time translation invariance.

        ∂E/∂t = 0

        Check if total energy is conserved over time (not constant across space).
        """
        # Simulate time evolution
        energies = []

        for i in range(steps):
            # Energy at time t
            energy_density, _ = self.energy_momentum_tensor(C, dx)
            total_energy = np.sum(energy_density) * dx
            energies.append(total_energy)

            # Simple time evolution (gradient flow)
            grad_C = np.gradient(C, dx)
            C = C - dt * grad_C

        # Check if energy is conserved over time
        energy_change = np.abs(energies[-1] - energies[0])
        is_conserved = energy_change < 1e-8

        result = {
            "total_energy_initial": energies[0],
            "total_energy_final": energies[-1],
            "energy_change": energy_change,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL"
        }

        return result

    def check_momentum_conservation(
        self,
        C: np.ndarray,
        dx: float,
        dt: float = 0.01,
        steps: int = 10
    ) -> Dict:
        """
        Check momentum conservation from spatial translation invariance.

        ∂P/∂t = 0

        Check if total momentum is conserved over time (not zero).
        """
        # Simulate time evolution
        momenta = []

        for i in range(steps):
            # Momentum at time t
            _, momentum_density = self.energy_momentum_tensor(C, dx)
            total_momentum = np.sum(momentum_density) * dx
            momenta.append(total_momentum)

            # Simple time evolution (gradient flow)
            grad_C = np.gradient(C, dx)
            C = C - dt * grad_C

        # Check if momentum is conserved over time
        momentum_change = np.abs(momenta[-1] - momenta[0])
        is_conserved = momentum_change < 1e-8

        result = {
            "total_momentum_initial": momenta[0],
            "total_momentum_final": momenta[-1],
            "momentum_change": momentum_change,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL"
        }

        return result

    def angular_momentum_density(
        self,
        C: np.ndarray,
        x: np.ndarray,
        dx: float
    ) -> np.ndarray:
        """
        Derive angular momentum density from rotation symmetry.

        L = x × p
        """
        _, momentum_density = self.energy_momentum_tensor(C, dx)

        # Angular momentum density
        L_density = x * momentum_density

        return L_density

    def check_angular_momentum_conservation(
        self,
        C: np.ndarray,
        x: np.ndarray,
        dx: float,
        dt: float = 0.01,
        steps: int = 10
    ) -> Dict:
        """
        Check angular momentum conservation from rotation symmetry.

        ∂L/∂t = 0

        Check if total angular momentum is conserved over time (not zero).
        """
        # Simulate time evolution
        angular_momenta = []

        for i in range(steps):
            # Angular momentum at time t
            L_density = self.angular_momentum_density(C, x, dx)
            total_L = np.sum(L_density) * dx
            angular_momenta.append(total_L)

            # Simple time evolution (gradient flow)
            grad_C = np.gradient(C, dx)
            C = C - dt * grad_C

        # Check if angular momentum is conserved over time
        L_change = np.abs(angular_momenta[-1] - angular_momenta[0])
        is_conserved = L_change < 1e-8

        result = {
            "total_angular_momentum_initial": angular_momenta[0],
            "total_angular_momentum_final": angular_momenta[-1],
            "angular_momentum_change": L_change,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL"
        }

        return result

    def charge_current(
        self,
        C: np.ndarray,
        I: np.ndarray,
        dx: float
    ) -> np.ndarray:
        """
        Derive charge current from U(1) gauge symmetry.

        J^μ = (∂L/∂(∂_μC))·δC + (∂L/∂(∂_μI))·δI

        For U(1) phase invariance:
        J = β (C* ∂_μ I - I* ∂_μ C)  # Standard complex current
        Simplified for real fields in current engine:
        J = β C·I
        """
        # Charge density
        charge_density = self.params.beta * C * I

        # Current (simplified)
        current = np.gradient(charge_density, dx)

        return current

    def check_charge_conservation(
        self,
        C: np.ndarray,
        I: np.ndarray,
        dx: float
    ) -> Dict:
        """
        Check charge conservation from U(1) gauge symmetry.

        ∂_μ J^μ = 0
        """
        current = self.charge_current(C, I, dx)

        # Divergence of current
        divergence = np.gradient(current, dx).sum()

        # Check conservation
        is_conserved = np.abs(divergence) < 1e-8

        result = {
            "divergence": divergence,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL"
        }

        return result

    def comprehensive_conservation_check(
        self,
        C: np.ndarray,
        I: np.ndarray,
        x: np.ndarray,
        dx: float
    ) -> Dict:
        """
        Run comprehensive conservation check for all symmetries.
        """
        results = {}

        # 1. Energy conservation
        results["energy"] = self.check_energy_conservation(C, dx)

        # 2. Momentum conservation
        results["momentum"] = self.check_momentum_conservation(C, dx)

        # 3. Angular momentum conservation
        results["angular_momentum"] = self.check_angular_momentum_conservation(C, x, dx)

        # 4. Charge conservation
        results["charge"] = self.check_charge_conservation(C, I, dx)

        # Summary
        passed = sum(1 for r in results.values() if r["is_conserved"])
        total = len(results)

        results["summary"] = {
            "passed": passed,
            "total": total,
            "ratio": passed / total
        }

        return results

    def check_energy_conservation_complex(
        self,
        C: np.ndarray,
        dx: float,
        dt: float = 0.01,
        steps: int = 10
    ) -> Dict:
        """
        Check energy conservation for complex fields.

        ∂E/∂t = 0

        Check if total energy is conserved over time (not constant across space).
        """
        # Use magnitude for complex fields
        C_magnitude = np.abs(C)

        # Simulate time evolution
        energies = []

        for i in range(steps):
            # Energy at time t
            energy_density, _ = self.energy_momentum_tensor(C_magnitude, dx)
            total_energy = np.sum(energy_density) * dx
            energies.append(total_energy)

            # Simple time evolution (gradient flow)
            grad_C = np.gradient(C_magnitude, dx)
            C_magnitude = C_magnitude - dt * grad_C

        # Check if energy is conserved over time
        energy_change = np.abs(energies[-1] - energies[0])
        is_conserved = energy_change < 1e-8

        result = {
            "total_energy_initial": energies[0],
            "total_energy_final": energies[-1],
            "energy_change": energy_change,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL",
            "field_type": "Complex"
        }

        return result

    def check_momentum_conservation_complex(
        self,
        C: np.ndarray,
        dx: float,
        dt: float = 0.01,
        steps: int = 10
    ) -> Dict:
        """
        Check momentum conservation for complex fields.

        ∂P/∂t = 0

        Check if total momentum is conserved over time (not zero).
        """
        # Use magnitude for complex fields
        C_magnitude = np.abs(C)

        # Simulate time evolution
        momenta = []

        for i in range(steps):
            # Momentum at time t
            _, momentum_density = self.energy_momentum_tensor(C_magnitude, dx)
            total_momentum = np.sum(momentum_density) * dx
            momenta.append(total_momentum)

            # Simple time evolution (gradient flow)
            grad_C = np.gradient(C_magnitude, dx)
            C_magnitude = C_magnitude - dt * grad_C

        # Check if momentum is conserved over time
        momentum_change = np.abs(momenta[-1] - momenta[0])
        is_conserved = momentum_change < 1e-8

        result = {
            "total_momentum_initial": momenta[0],
            "total_momentum_final": momenta[-1],
            "momentum_change": momentum_change,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL",
            "field_type": "Complex"
        }

        return result

    def check_angular_momentum_conservation_complex(
        self,
        C: np.ndarray,
        x: np.ndarray,
        dx: float,
        dt: float = 0.01,
        steps: int = 10
    ) -> Dict:
        """
        Check angular momentum conservation for complex fields.

        ∂L/∂t = 0

        Check if total angular momentum is conserved over time (not zero).
        """
        # Use magnitude for complex fields
        C_magnitude = np.abs(C)

        # Simulate time evolution
        angular_momenta = []

        for i in range(steps):
            # Angular momentum at time t
            L_density = self.angular_momentum_density(C_magnitude, x, dx)
            total_L = np.sum(L_density) * dx
            angular_momenta.append(total_L)

            # Simple time evolution (gradient flow)
            grad_C = np.gradient(C_magnitude, dx)
            C_magnitude = C_magnitude - dt * grad_C

        # Check if angular momentum is conserved over time
        L_change = np.abs(angular_momenta[-1] - angular_momenta[0])
        is_conserved = L_change < 1e-8

        result = {
            "total_angular_momentum_initial": angular_momenta[0],
            "total_angular_momentum_final": angular_momenta[-1],
            "angular_momentum_change": L_change,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL",
            "field_type": "Complex"
        }

        return result

    def check_charge_conservation_complex(
        self,
        C: np.ndarray,
        I: np.ndarray,
        dx: float
    ) -> Dict:
        """
        Check charge conservation for complex fields.

        ∂_μ J^μ = 0
        """
        # Use magnitude for complex fields
        C_magnitude = np.abs(C)
        I_magnitude = np.abs(I)

        current = self.charge_current(C_magnitude, I_magnitude, dx)

        # Divergence of current
        divergence = np.gradient(current, dx).sum()

        # Check conservation
        is_conserved = np.abs(divergence) < 1e-8

        result = {
            "divergence": divergence,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL",
            "field_type": "Complex"
        }

        return result

    def check_energy_conservation_time_dependent(
        self,
        C: np.ndarray,
        dx: float,
        dt: float = 0.01,
        steps: int = 10
    ) -> Dict:
        """
        Check energy conservation for time-dependent fields.

        ∂E/∂t = 0

        Check if total energy is conserved over time (not constant across space).
        """
        # Simulate time evolution
        energies = []

        for i in range(steps):
            # Energy at time t
            energy_density, _ = self.energy_momentum_tensor(C, dx)
            total_energy = np.sum(energy_density) * dx
            energies.append(total_energy)

            # Simple time evolution (gradient flow)
            grad_C = np.gradient(C, dx)
            C = C - dt * grad_C

        # Check if energy is conserved over time
        energy_change = np.abs(energies[-1] - energies[0])
        is_conserved = energy_change < 1e-8

        result = {
            "total_energy_initial": energies[0],
            "total_energy_final": energies[-1],
            "energy_change": energy_change,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL",
            "field_type": "Time-dependent"
        }

        return result

    def check_momentum_conservation_time_dependent(
        self,
        C: np.ndarray,
        dx: float,
        dt: float = 0.01,
        steps: int = 10
    ) -> Dict:
        """
        Check momentum conservation for time-dependent fields.

        ∂P/∂t = 0

        Check if total momentum is conserved over time (not zero).
        """
        # Simulate time evolution
        momenta = []

        for i in range(steps):
            # Momentum at time t
            _, momentum_density = self.energy_momentum_tensor(C, dx)
            total_momentum = np.sum(momentum_density) * dx
            momenta.append(total_momentum)

            # Simple time evolution (gradient flow)
            grad_C = np.gradient(C, dx)
            C = C - dt * grad_C

        # Check if momentum is conserved over time
        momentum_change = np.abs(momenta[-1] - momenta[0])
        is_conserved = momentum_change < 1e-8

        result = {
            "total_momentum_initial": momenta[0],
            "total_momentum_final": momenta[-1],
            "momentum_change": momentum_change,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL",
            "field_type": "Time-dependent"
        }

        return result

    def check_angular_momentum_conservation_time_dependent(
        self,
        C: np.ndarray,
        x: np.ndarray,
        dx: float,
        dt: float = 0.01,
        steps: int = 10
    ) -> Dict:
        """
        Check angular momentum conservation for time-dependent fields.

        ∂L/∂t = 0

        Check if total angular momentum is conserved over time (not zero).
        """
        # Simulate time evolution
        angular_momenta = []

        for i in range(steps):
            # Angular momentum at time t
            L_density = self.angular_momentum_density(C, x, dx)
            total_L = np.sum(L_density) * dx
            angular_momenta.append(total_L)

            # Simple time evolution (gradient flow)
            grad_C = np.gradient(C, dx)
            C = C - dt * grad_C

        # Check if angular momentum is conserved over time
        L_change = np.abs(angular_momenta[-1] - angular_momenta[0])
        is_conserved = L_change < 1e-8

        result = {
            "total_angular_momentum_initial": angular_momenta[0],
            "total_angular_momentum_final": angular_momenta[-1],
            "angular_momentum_change": L_change,
            "is_conserved": is_conserved,
            "status": "PASS" if is_conserved else "FAIL",
            "field_type": "Time-dependent"
        }

        return result

    def comprehensive_conservation_check_complex(
        self,
        C: np.ndarray,
        I: np.ndarray,
        x: np.ndarray,
        dx: float
    ) -> Dict:
        """
        Run comprehensive conservation check for complex fields.
        """
        results = {}

        # 1. Energy conservation
        results["energy"] = self.check_energy_conservation_complex(C, dx)

        # 2. Momentum conservation
        results["momentum"] = self.check_momentum_conservation_complex(C, dx)

        # 3. Angular momentum conservation
        results["angular_momentum"] = self.check_angular_momentum_conservation_complex(C, x, dx)

        # 4. Charge conservation
        results["charge"] = self.check_charge_conservation_complex(C, I, dx)

        # Summary
        passed = sum(1 for r in results.values() if r["is_conserved"])
        total = len(results)

        results["summary"] = {
            "passed": passed,
            "total": total,
            "ratio": passed / total,
            "field_type": "Complex"
        }

        return results

    def comprehensive_conservation_check_time_dependent(
        self,
        C: np.ndarray,
        I: np.ndarray,
        x: np.ndarray,
        dx: float
    ) -> Dict:
        """
        Run comprehensive conservation check for time-dependent fields.

        Legacy callers may provide a flattened ``(n_time, n_space)`` history.
        The underlying diagnostics are one-spatial-state routines, so this
        compatibility boundary selects the final spatial snapshot before
        dispatching.  It prevents a shape mismatch without implying that this
        legacy module proves conservation for the full history.
        """
        x_array = np.asarray(x)
        C_array = np.asarray(C)
        if C_array.size != x_array.size:
            if C_array.size % x_array.size:
                raise ValueError(
                    "time-dependent C history must contain an integer number "
                    "of spatial snapshots"
                )
            C_array = C_array.reshape(-1, x_array.size)[-1]

        I_array = np.asarray(I)
        if I_array.size != C_array.size:
            if I_array.size % C_array.size:
                raise ValueError(
                    "time-dependent I history must match the spatial snapshot "
                    "or contain an integer number of snapshots"
                )
            I_array = I_array.reshape(-1, C_array.size)[-1]

        results = {}

        # 1. Energy conservation
        results["energy"] = self.check_energy_conservation_time_dependent(C_array, dx)

        # 2. Momentum conservation
        results["momentum"] = self.check_momentum_conservation_time_dependent(C_array, dx)

        # 3. Angular momentum conservation
        results["angular_momentum"] = self.check_angular_momentum_conservation_time_dependent(C_array, x_array, dx)

        # 4. Charge conservation (same as original)
        results["charge"] = self.check_charge_conservation(C_array, I_array, dx)

        # Summary
        passed = sum(1 for r in results.values() if r["is_conserved"])
        total = len(results)

        results["summary"] = {
            "passed": passed,
            "total": total,
            "ratio": passed / total,
            "field_type": "Time-dependent"
        }

        return results


def test_noether():
    """Test Noether's Theorem implementation."""
    print("=" * 70)
    print("UET NOETHER'S THEOREM TEST")
    print("=" * 70)

    # Create test fields
    N = 100
    x = np.linspace(-5, 5, N)
    C = np.exp(-x**2)  # Gaussian (symmetric)
    I = np.random.randn(N) * 0.1  # Information field
    dx = 0.1

    # Create Noether instance
    noether = UETNoether()

    # Run comprehensive check
    results = noether.comprehensive_conservation_check(C, I, x, dx)

    print("\nCONSERVATION SUMMARY")
    print("=" * 70)

    for name, result in results.items():
        if name == "summary":
            continue
        status_icon = "✅" if result["is_conserved"] else "❌"
        print(f"{status_icon} {name}: {result['status']}")

    print(f"\nPassed: {results['summary']['passed']}/{results['summary']['total']}")

    print("\n" + "=" * 70)
    print("LEGACY NOETHER DIAGNOSTIC: CONSERVATION PROOF CLAIM BLOCKED")
    print("=" * 70)

    return results


if __name__ == "__main__":
    test_noether()
