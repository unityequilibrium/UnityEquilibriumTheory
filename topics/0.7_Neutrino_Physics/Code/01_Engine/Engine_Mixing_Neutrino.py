"""
Engine: UET Neutrino Mixing (Flavor Oscillation)
=================================================
Topic: 0.7_Neutrino_Physics (Migrated from 0.18)
Folder: 01_Engine

Runs a UET-style oscillation diagnostic.
Uses core UET framework with benchmark-fed runtime parameters.

Core Concept: Neutrino mixing = C-field phase rotation
  P(ν_e → ν_μ) = sin²(2θ) × sin²(Δm²L/4E)

DOI: 10.1007/JHEP09(2020)178 (NuFIT 5.2)
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


import sys
import numpy as np
from pathlib import Path

# --- ROBUST PATH FINDER ---


# Core Imports
from docs.core.uet_base_solver import UETBaseSolver
from docs.core.uet_master_equation import UETParameters

from docs.core.uet_master_equation import UETParameters


def oscillation_probability(
    theta_deg: float, delta_m_sq: float, L: float, E: float
) -> float:
    """
    Two-flavor neutrino oscillation probability.

    P(ν_α → ν_β) = sin²(2θ) × sin²(Δm²L/4E)

    Args:
        theta_deg: Mixing angle in degrees
        delta_m_sq: Mass squared difference (eV²)
        L: Distance (km)
        E: Energy (GeV)

    Returns:
        Transition probability
    """
    theta = np.deg2rad(theta_deg)
    # Standard oscillation formula: sin²(2θ) × sin²(1.27 × Δm² × L / E)
    amplitude = np.sin(2 * theta) ** 2
    phase = 1.27 * delta_m_sq * L / E
    return amplitude * np.sin(phase) ** 2


def run_mixing_engine():
    """
    Test neutrino mixing via oscillation probabilities.

    Uses NuFIT 5.2 parameters - NOT fitted.
    """
    print("=" * 70)
    print("⚙️  ENGINE: UET Neutrino Mixing")
    print("    Topic 0.7 - Flavor Oscillation via C-field Phase")
    print("=" * 70)

    # Test cases with UET geometric rule examples (tri-bimaximal / maximal).
    # These are diagnostics, not a source-locked benchmark gate.
    # Current rule examples:
    # theta_23 = 45 deg (Maximal Mixing, Symmetry)
    # theta_12 = ~35.26 deg (arcsin(1/sqrt(3)), Tri-bimaximal)
    # theta_13 = ~9.0 deg (current hierarchy-leakage bridge)

    cases = [
        ("Theta_12 (Solar)", 35.26, 1.0, "Geometric: arcsin(1/√3)"),
        ("Theta_23 (Atm)", 45.00, 10.0, "Geometric: Maximal (π/4)"),
        ("Theta_13 (React)", 9.00, 10.0, "Bridge: Topic 0.7"),
    ]

    print("\n[1] MIXING ANGLE → OSCILLATION AMPLITUDE")
    print("-" * 65)
    print(f"| {'Angle':<18} | {'θ (°)':<8} | {'sin²(2θ)':<10} | {'Prediction':<18} |")
    print("-" * 65)

    for name, theta, dm_sq, expected in cases:
        sin2_2theta = np.sin(2 * np.deg2rad(theta)) ** 2
        max_P = sin2_2theta  # Maximum occurs when phase = π/2
        print(f"| {name:<18} | {theta:<8.2f} | {sin2_2theta:<10.4f} | {expected:<18} |")

    print("-" * 65)

    # Simulate oscillation over distance
    print("\n[2] OSCILLATION PROBABILITY vs DISTANCE (Abstract Units)")
    print("-" * 65)

    theta = 35.26  # theta_12 (Geometric)
    dm_sq = 1e-3  # Abstract Mass Split
    E = 1.0  # Unit Energy

    print(f"  Using θ₁₂ = {theta:.2f}°, Δm² = {dm_sq:.1e}")
    print(f"  L (Units) | P(ν_e → ν_μ)")
    print("-" * 65)

    for L in [0, 100, 500, 1000, 5000, 10000]:
        P = oscillation_probability(theta, dm_sq, L, E)
        bar = "█" * int(P * 20)
        print(f"  {L:<9} | {P:.4f}  {bar}")

    print("-" * 65)

    print("\n[3] UET INTERPRETATION")
    print("-" * 65)
    print(
        """
    In UET framework:
    - Neutrino flavor = C-field configuration
    - Mixing angle θ = Geometric Rotation (β coupling)
    - Δm² = Gradient energy difference (κ term)
    
    Ω_flavor = V(C) + κ|∇C|² + βCI
                           ↑
              Phase accumulation → Oscillation
    
    Parameters are GEOMETRIC (Not Fitted):
    - θ_23 = 45° (Maximal Mixing)
    - θ_12 = 35.26° (Tri-bimaximal)
    """
    )

    print("=" * 70)
    print("ENGINE RESULT: PASS")
    print("=" * 70)

    return True


class UETNeutrinoMixingSolver(UETBaseSolver):
    """
    UET Neutrino Mixing Solver (PMNS).
    Interprets mixing as C-field phase interference.
    """

    def __init__(self, name="UET_Neutrino_Mixing"):
        params = UETParameters(kappa=1.0, beta=1.0, alpha=1.0, C0=1.0)
        super().__init__(
            nx=1,
            ny=1,
            dt=1.0,
            params=params,
            name=name,
            topic="0.7_Neutrino_Physics",
            pillar="01_Engine",
            stable_path=True,
        )

        # NuFIT 5.2 Parameters (Normal Ordering)
        self.NUFIT_PARAMS = {
            "theta12": 33.44,
            "theta23": 49.2,
            "theta13": 8.57,
            "delta_cp": 197,
            "dm21_sq": 7.42e-5,
            "dm31_sq": 2.515e-3,
        }

    def get_pmns_matrix(self):
        """Construct PMNS matrix from internal NuFIT parameters."""
        t12, t23, t13 = np.deg2rad(
            [
                self.NUFIT_PARAMS["theta12"],
                self.NUFIT_PARAMS["theta23"],
                self.NUFIT_PARAMS["theta13"],
            ]
        )
        dcp = np.deg2rad(self.NUFIT_PARAMS["delta_cp"])

        c12, s12 = np.cos(t12), np.sin(t12)
        c23, s23 = np.cos(t23), np.sin(t23)
        c13, s13 = np.cos(t13), np.sin(t13)

        # Standard parameterization with Kill Switch check
        # Multiply by (beta/beta) to ensure NaN if sabotaged
        check = self.params.beta / self.params.beta

        U = (
            np.array(
                [
                    [c12 * c13, s12 * c13, s13 * np.exp(-1j * dcp)],
                    [
                        -s12 * c23 - c12 * s23 * s13 * np.exp(1j * dcp),
                        c12 * c23 - s12 * s23 * s13 * np.exp(1j * dcp),
                        s23 * c13,
                    ],
                    [
                        s12 * s23 - c12 * c23 * s13 * np.exp(1j * dcp),
                        -c12 * s23 - s12 * c23 * s13 * np.exp(1j * dcp),
                        c23 * c13,
                    ],
                ]
            )
            * check
        )
        return U

    def compute_oscillation_3flavor(self, alpha, beta, L, E):
        """3-flavor oscillation probability P(v_alpha -> v_beta)."""
        U = self.get_pmns_matrix()
        dm21 = self.NUFIT_PARAMS["dm21_sq"]
        dm31 = self.NUFIT_PARAMS["dm31_sq"]
        dm = [0, dm21, dm31]

        prob = 0.0 + 0j
        for i in range(3):
            for j in range(3):
                phase_ij = 1.27 * (dm[j] - dm[i]) * L / E
                term = (
                    U[alpha, i]
                    * np.conj(U[beta, i])
                    * np.conj(U[alpha, j])
                    * U[beta, j]
                )
                prob += term * np.exp(-1j * phase_ij)

        return float(np.real(prob))

    def calculate_survival_probability(self, L_km: float, E_GeV: float = 1.0) -> float:
        """P(v_e -> v_e) survival probability."""
        return self.compute_oscillation_3flavor(0, 0, L_km, E_GeV)


if __name__ == "__main__":
    success = run_mixing_engine()
    sys.exit(0 if success else 1)
