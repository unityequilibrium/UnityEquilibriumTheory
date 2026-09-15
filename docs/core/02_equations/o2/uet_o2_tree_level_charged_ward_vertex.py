"""Action-derived tree-level charged Euclidean Ward vertex.

This lane checks the Ward identity implied by the declared finite-density
charged propagator before any loop self-energy or transport coefficient is
admitted.  It is an algebraic tree-level identity in the natural-unit normal
branch, not a renormalized microscopic vertex or a physical Kubo calculation.

With ``P=(omega_n, p)`` and ``Q=(nu_m, q)``, the declared inverse propagator is

``D_E^{-1}(P)=(omega_n+i*mu_eff)^2+|p|^2+m_eff^2``

and the bare vertex is

``Gamma_E^0=2*(omega_n+i*mu_eff)+nu_m``
``Gamma_E^i=2*p_i+q_i``.

The Euclidean Ward identity is
``Q_0*Gamma_E^0+q_i*Gamma_E^i = D_E^{-1}(P+Q)-D_E^{-1}(P)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_density_charged_vertex import (
    charged_euclidean_inverse,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_finite_density_eos import effective_mass_sq


TREE_LEVEL_CHARGED_WARD_STATUS = (
    "PASS_ACTION_DERIVED_TREE_LEVEL_CHARGED_WARD_VERTEX_LANE"
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _relative_complex(first: complex, second: complex) -> float:
    return float(abs(first - second) / max(abs(second), 1.0e-300))


def _vertex(
    omega_n: float,
    momentum: np.ndarray,
    nu_m: float,
    transfer: np.ndarray,
    effective_chemical_potential: float,
) -> np.ndarray:
    """Return the bare Euclidean charged vertex for ``P -> P+Q``."""

    return np.asarray(
        (
            2.0 * (float(omega_n) + 1.0j * effective_chemical_potential)
            + float(nu_m),
            *(2.0 * momentum + transfer),
        ),
        dtype=complex,
    )


@dataclass(frozen=True)
class TreeLevelChargedWardVertexState:
    """Residuals and scope controls for the tree-level Ward identity."""

    temperature: float
    chemical_potential: float
    effective_chemical_potential: float
    effective_mass: float
    sample_count: int
    ward_residuals: tuple[float, ...]
    max_ward_residual: float
    zero_transfer_vertex_residual: float
    charge_conjugation_residual: float
    normal_branch: bool
    tree_level_current_vertex_completed: bool = True
    loop_renormalized_offshell_vertex_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "ACTION_DERIVED_TREE_LEVEL_WARD_IDENTITY_NO_EXTERNAL_DATA"


def tree_level_charged_ward_vertex_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
) -> TreeLevelChargedWardVertexState:
    """Evaluate the declared tree-level Ward identity on fixed test points."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    config = config or FiniteTemperatureO2QuasiparticleConfig()

    mass_sq = float(effective_mass_sq(space_response, config.eos))
    mass = sqrt(_positive(mass_sq, "effective mass squared"))
    kinetic = _positive(config.eos.matter.matter_kinetic, "matter kinetic")
    effective_mu = sqrt(kinetic) * chemical_potential
    normal_branch = abs(effective_mu) < mass
    if not normal_branch:
        raise ValueError("tree-level charged Ward lane requires the normal branch")

    scale = mass
    samples = (
        (
            0.17 * scale,
            scale * np.asarray((0.31, -0.12, 0.19), dtype=float),
            0.09 * scale,
            scale * np.asarray((0.07, 0.16, -0.11), dtype=float),
        ),
        (
            -0.23 * scale,
            scale * np.asarray((-0.21, 0.28, 0.14), dtype=float),
            -0.13 * scale,
            scale * np.asarray((0.18, -0.05, 0.09), dtype=float),
        ),
        (
            0.41 * scale,
            scale * np.asarray((0.11, 0.07, -0.34), dtype=float),
            0.05 * scale,
            scale * np.asarray((-0.08, 0.13, 0.06), dtype=float),
        ),
    )

    ward_residuals: list[float] = []
    charge_conjugation_residuals: list[float] = []
    zero_transfer_residuals: list[float] = []
    for omega_n, momentum, nu_m, transfer in samples:
        momentum_after = momentum + transfer
        lhs = charged_euclidean_inverse(
            omega_n + nu_m,
            float(np.linalg.norm(momentum_after)),
            effective_mu,
            mass,
        ) - charged_euclidean_inverse(
            omega_n,
            float(np.linalg.norm(momentum)),
            effective_mu,
            mass,
        )
        vertex = _vertex(omega_n, momentum, nu_m, transfer, effective_mu)
        rhs = complex(nu_m * vertex[0] + np.dot(transfer, vertex[1:]))
        ward_residuals.append(_relative_complex(lhs, rhs))

        conjugate_lhs = charged_euclidean_inverse(
            omega_n + nu_m,
            float(np.linalg.norm(momentum_after)),
            -effective_mu,
            mass,
        ) - charged_euclidean_inverse(
            omega_n,
            float(np.linalg.norm(momentum)),
            -effective_mu,
            mass,
        )
        charge_conjugation_residuals.append(
            _relative_complex(conjugate_lhs, np.conjugate(lhs))
        )

        zero_vertex = _vertex(omega_n, momentum, 0.0, np.zeros(3), effective_mu)
        zero_target = np.asarray(
            (2.0 * (omega_n + 1.0j * effective_mu), *(2.0 * momentum)),
            dtype=complex,
        )
        zero_transfer_residuals.append(
            float(
                np.linalg.norm(zero_vertex - zero_target)
                / max(np.linalg.norm(zero_target), 1.0e-300)
            )
        )

    values = (
        effective_mu,
        mass,
        *ward_residuals,
        *charge_conjugation_residuals,
        *zero_transfer_residuals,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("tree-level charged Ward state is not finite")

    return TreeLevelChargedWardVertexState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        effective_chemical_potential=float(effective_mu),
        effective_mass=float(mass),
        sample_count=len(samples),
        ward_residuals=tuple(float(value) for value in ward_residuals),
        max_ward_residual=float(max(ward_residuals)),
        zero_transfer_vertex_residual=float(max(zero_transfer_residuals)),
        charge_conjugation_residual=float(max(charge_conjugation_residuals)),
        normal_branch=normal_branch,
    )


def tree_level_charged_ward_vertex_contract() -> dict[str, Any]:
    """Return the identity, units, and non-promotion boundary."""

    return {
        "status": TREE_LEVEL_CHARGED_WARD_STATUS,
        "equations": {
            "charged_euclidean_inverse": "D_E^-1(P)=(omega_n+i*mu_eff)^2+|p|^2+m_eff(Phi)^2",
            "bare_euclidean_vertex": "Gamma_E^0=2*(omega_n+i*mu_eff)+nu_m; Gamma_E^i=2*p_i+q_i",
            "ward_identity": "nu_m*Gamma_E^0+q_i*Gamma_E^i=D_E^-1(P+Q)-D_E^-1(P)",
        },
        "units": {
            "unit_lane": "natural",
            "temperature_chemical_potential_mass_momentum": "energy",
            "D_E_inverse": "energy^2",
            "Q_and_Gamma_E": "energy",
            "Q_dot_Gamma": "energy^2",
        },
        "ontology": {
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived physical/history trace; no independent state or backreaction",
            "R_obs": "separate observer record; not part of the vertex dynamics",
        },
        "derivation_class": (
            "tree-level action-derived finite-density charged Euclidean propagator and "
            "bare current vertex"
        ),
        "observable": "tree-level charged Euclidean Ward-identity residual",
        "data_role": "ACTION_DERIVED_TREE_LEVEL_WARD_IDENTITY_NO_EXTERNAL_DATA",
        "included": {
            "normal_branch_propagator": True,
            "bare_charged_current_vertex": True,
            "finite_density_ward_identity": True,
            "charge_conjugation_boundary": True,
        },
        "excluded": {
            "loop_renormalized_offshell_self_energy": True,
            "loop_renormalized_current_vertex": True,
            "continuum_limit": True,
            "physical_kubo_coefficient": True,
            "finite_temperature_two_fluid_transport": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the tree-level charged Euclidean Ward identity in the "
            "declared natural-unit normal branch. It is not a loop-renormalized "
            "off-shell vertex, physical Kubo coefficient, SI map, TTG prediction, "
            "or Full Topic 13 closure."
        ),
    }


__all__ = [
    "TREE_LEVEL_CHARGED_WARD_STATUS",
    "TreeLevelChargedWardVertexState",
    "tree_level_charged_ward_vertex_state",
    "tree_level_charged_ward_vertex_contract",
]
