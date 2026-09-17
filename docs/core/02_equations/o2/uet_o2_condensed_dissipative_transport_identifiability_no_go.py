"""Scoped identifiability boundary for the condensed dissipative lane.

The finite-temperature O(2) condensed state currently exposes static sector
thermodynamics and a phase stiffness, but it does not expose an independent
normal/condensate relative velocity, a collision kernel, or a retarded
correlator. This module records the resulting structural boundary instead of
silently assigning a dissipative coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


CONDENSED_DISSIPATIVE_TRANSPORT_STATUS = (
    "PASS_SCOPED_CONDENSED_DISSIPATIVE_TRANSPORT_IDENTIFIABILITY_NO_GO"
)
PSD_TOLERANCE = 1.0e-12

Matrix2 = tuple[tuple[float, float], tuple[float, float]]
Vector2 = tuple[float, float]


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _vector(value: Vector2, name: str) -> Vector2:
    if len(value) != 2:
        raise ValueError(f"{name} must have two components")
    result = tuple(_finite(component, name) for component in value)
    return result  # type: ignore[return-value]


def _matrix(value: Matrix2, name: str) -> Matrix2:
    if len(value) != 2 or any(len(row) != 2 for row in value):
        raise ValueError(f"{name} must be a 2x2 matrix")
    result = tuple(
        tuple(_finite(component, name) for component in row) for row in value
    )
    return result  # type: ignore[return-value]


def is_positive_semidefinite_2x2(matrix: Matrix2) -> bool:
    """Return the symmetric 2x2 positive-semidefinite test."""

    m = _matrix(matrix, "matrix")
    symmetric = abs(m[0][1] - m[1][0]) <= PSD_TOLERANCE
    determinant = m[0][0] * m[1][1] - m[0][1] * m[1][0]
    return (
        symmetric
        and m[0][0] >= -PSD_TOLERANCE
        and m[1][1] >= -PSD_TOLERANCE
        and determinant >= -PSD_TOLERANCE
    )


def entropy_production_quadratic(matrix: Matrix2, force: Vector2) -> float:
    """Evaluate the normalized quadratic entropy-production witness."""

    m = _matrix(matrix, "matrix")
    x = _vector(force, "force")
    return float(
        x[0] * (m[0][0] * x[0] + m[0][1] * x[1])
        + x[1] * (m[1][0] * x[0] + m[1][1] * x[1])
    )


def response_vector(matrix: Matrix2, force: Vector2) -> Vector2:
    """Return the normalized dissipative response L_ij X_j."""

    m = _matrix(matrix, "matrix")
    x = _vector(force, "force")
    return (
        float(m[0][0] * x[0] + m[0][1] * x[1]),
        float(m[1][0] * x[0] + m[1][1] * x[1]),
    )


@dataclass(frozen=True)
class CondensedDissipativeTransportBoundary:
    """Witness that static condensed data do not identify dissipative L."""

    temperature: float
    chemical_potential: float
    static_force: Vector2
    probe_force: Vector2
    witness_a: Matrix2
    witness_b: Matrix2
    static_entropy_production_a: float
    static_entropy_production_b: float
    probe_response_a: Vector2
    probe_response_b: Vector2
    witness_a_positive_semidefinite: bool
    witness_b_positive_semidefinite: bool
    static_state_identical: bool
    probe_responses_distinct: bool
    physical_transport_coefficients_emitted: bool = False
    data_role: str = "INTERNAL_STRUCTURAL_CONDENSED_TRANSPORT_NO_GO_NO_SOURCE_ROWS"


def condensed_dissipative_transport_boundary(
    temperature: float,
    chemical_potential: float,
) -> CondensedDissipativeTransportBoundary:
    """Construct the two-witness identifiability boundary.

    The current static lane has no thermodynamic force or relative-flow
    observable. Both positive-semidefinite witnesses therefore reproduce the
    same static entropy production, while a nonzero probe force separates
    their responses. The probe is a mathematical diagnostic, not data or a
    fitted physical transport input.
    """

    temperature = _finite(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")

    static_force: Vector2 = (0.0, 0.0)
    probe_force: Vector2 = (1.0, 0.0)
    witness_a: Matrix2 = ((1.0, 0.0), (0.0, 1.0))
    witness_b: Matrix2 = ((2.0, 0.0), (0.0, 0.5))

    static_a = entropy_production_quadratic(witness_a, static_force)
    static_b = entropy_production_quadratic(witness_b, static_force)
    probe_a = response_vector(witness_a, probe_force)
    probe_b = response_vector(witness_b, probe_force)
    if not isclose(static_a, static_b):
        raise AssertionError("witnesses do not agree on the static state")
    if isclose(probe_a[0], probe_b[0]) and isclose(probe_a[1], probe_b[1]):
        raise AssertionError("witnesses must differ under the probe force")

    return CondensedDissipativeTransportBoundary(
        temperature=temperature,
        chemical_potential=chemical_potential,
        static_force=static_force,
        probe_force=probe_force,
        witness_a=witness_a,
        witness_b=witness_b,
        static_entropy_production_a=float(static_a),
        static_entropy_production_b=float(static_b),
        probe_response_a=probe_a,
        probe_response_b=probe_b,
        witness_a_positive_semidefinite=is_positive_semidefinite_2x2(witness_a),
        witness_b_positive_semidefinite=is_positive_semidefinite_2x2(witness_b),
        static_state_identical=isclose(static_a, static_b),
        probe_responses_distinct=not (
            isclose(probe_a[0], probe_b[0]) and isclose(probe_a[1], probe_b[1])
        ),
    )


def isclose(first: float, second: float) -> bool:
    """Small local comparison helper with a fixed auditable tolerance."""

    return abs(float(first) - float(second)) <= PSD_TOLERANCE


def condensed_dissipative_transport_contract() -> dict[str, object]:
    """Return equations, units, and the no-promotion boundary."""

    return {
        "status": CONDENSED_DISSIPATIVE_TRANSPORT_STATUS,
        "equations": {
            "ideal_entropy_current": (
                "J_S,ideal^mu=s_normal*u_normal^mu because "
                "s_condensate=0 in the declared tree sector"
            ),
            "two_force_entropy_production": "sigma=X_i*L_ij*X_j with L=L^T and L>=0",
            "static_lane_force": (
                "X_static=(0,0) because the current condensed state record "
                "has no gradient or relative-flow observable"
            ),
            "identifiability_witness": (
                "sigma_static(L_A)=sigma_static(L_B)=0 but "
                "L_A*X_probe != L_B*X_probe"
            ),
        },
        "unit_contract": {
            "unit_lane": "normalized natural-unit structural diagnostic",
            "force_vector": (
                "declared normalized thermodynamic/relative-flow forces; "
                "no SI conversion"
            ),
            "onsager_matrix": (
                "normalized natural-unit response matrix; "
                "not a physical Kubo coefficient"
            ),
            "entropy_production": "normalized natural-unit quadratic witness",
            "Phi": "effective response variable; not temperature or a metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state or feedback input",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "derivation_class": (
            "structural identifiability no-go from the declared condensed static "
            "state variables and the positive-semidefinite entropy contract"
        ),
        "observable": (
            "condensed ideal entropy-current boundary and dissipative "
            "transport identifiability"
        ),
        "data_role": "INTERNAL_STRUCTURAL_NO_GO_NO_SOURCE_ROWS",
        "closed_scope": [
            "the declared condensed static lane has zero condensate entropy in its tree-sector state records",
            "two positive-semidefinite dissipative witnesses are observationally identical on the current static state",
            "the witnesses produce distinct responses under a nonzero probe, so the current state cannot identify a unique dissipative matrix",
            "a physical condensed transport coefficient requires a relative-flow/collision kernel or state-matched retarded correlator",
        ],
        "excluded_scope": [
            "a microscopic condensed collision kernel",
            "a physical Kubo/Onsager coefficient",
            "a complete finite-temperature two-fluid constitutive tensor",
            "an SI Phi-to-temperature map or alpha_Phi_K calibration",
            "TTG prediction, holdout access, or external validation",
        ],
        "claim_boundary": (
            "This closes only the scoped identifiability question for the current "
            "condensed static lane. It does not derive a physical dissipative "
            "coefficient, complete two-fluid transport, SI mapping, alpha_Phi_K, "
            "TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "CONDENSED_DISSIPATIVE_TRANSPORT_STATUS",
    "CondensedDissipativeTransportBoundary",
    "condensed_dissipative_transport_boundary",
    "condensed_dissipative_transport_contract",
    "entropy_production_quadratic",
    "is_positive_semidefinite_2x2",
    "response_vector",
]
