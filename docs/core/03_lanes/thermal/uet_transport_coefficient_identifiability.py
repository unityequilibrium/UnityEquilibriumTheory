"""Scoped identifiability boundary for the Topic 13 transport lane.

The declared covariant O(2) action is conservative and single-copy.  It fixes
the ideal pressure/current/stress sector but contains neither a dissipative
Onsager matrix nor a closed-time-path noise/collision kernel.  This module
constructs two admissible positive transport witnesses to make that
under-determination explicit.  It is a no-go for deriving a unique physical
Kubo coefficient from the current action, not a no-go for a future open-system
extension.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class DissipativeTransportWitness:
    """A candidate longitudinal dissipative sector outside the ideal action."""

    name: str
    onsager_matrix: tuple[tuple[float, float], tuple[float, float]]
    relaxation_time: float
    coefficient_origin: str = "underdetermined_extension_of_conservative_action"

    @property
    def matrix(self) -> np.ndarray:
        return np.asarray(self.onsager_matrix, dtype=float)

    @property
    def eigenvalues(self) -> np.ndarray:
        return np.linalg.eigvalsh(self.matrix)

    @property
    def positive_semidefinite(self) -> bool:
        return bool(np.min(self.eigenvalues) >= -1.0e-12)

    @property
    def positive_relaxation_time(self) -> bool:
        return bool(self.relaxation_time > 0.0)


def conservative_action_transport_witnesses() -> tuple[DissipativeTransportWitness, ...]:
    """Return two distinct PSD transport completions for one ideal action."""

    return (
        DissipativeTransportWitness(
            name="witness_A",
            onsager_matrix=((1.0, 0.2), (0.2, 1.0)),
            relaxation_time=1.0,
        ),
        DissipativeTransportWitness(
            name="witness_B",
            onsager_matrix=((2.0, -0.3), (-0.3, 0.5)),
            relaxation_time=0.5,
        ),
    )


def transport_coefficient_identifiability_contract() -> dict[str, Any]:
    """Return equations, scope, ontology, and the no-go boundary."""

    return {
        "status": "SCOPED_NO_GO_CONSERVATIVE_ACTION_KUBO_IDENTIFIABILITY",
        "equations": {
            "ideal_action_sector": "S_cons[Phi,chi] -> P(X,Phi), N_ideal^mu, T_ideal^munu",
            "dissipative_extension": "J_diss^A = -L^(AB) X_B; tau_A > 0",
            "entropy_production": "nabla_mu J_S^mu = X_A L^(AB) X_B >= 0 for L=L^T >= 0",
            "Kubo_admission": "L^(AB) <- matched retarded correlator with state, units, locator, source hash",
        },
        "units": {
            "unit_lane": "natural for the ideal action; dissipative coefficient units remain source-declared",
            "ideal_sector": "natural action-derived quantities",
            "dissipative_coefficients": "not assigned by the conservative action",
            "physical_SI_map": "open",
        },
        "witness_policy": {
            "witness_count": 2,
            "same_ideal_action": True,
            "witnesses_are_physical_values": False,
            "entropy_positivity_is_sufficient_for_identification": False,
        },
        "scope": {
            "closed": "unique physical Kubo values cannot be inferred from the current conservative single-copy action alone",
            "not_closed": "open-system/CTP microscopic completion, state-matched Kubo records, finite-temperature normal component, SI transport, curved 3+1 transport",
            "future_extension": "a declared SK/open-system action or a source-locked correlator can break this underdetermination",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not a transport coefficient",
            "Phi": "effective response variable; not a dissipative coefficient or temperature",
            "R_gen": "derived history trace only; no transport state or feedback",
            "R_obs": "observer data separate from physical transport dynamics",
        },
        "data_role": "SCOPED_STRUCTURAL_NO_GO_NOT_PHYSICAL_TRANSPORT_EVIDENCE",
        "claim_boundary": "This closes only the identifiability boundary for deriving a unique physical dissipative/Kubo sector from the current conservative action. It does not reject future open-system UET extensions, supply a physical coefficient, close finite-temperature normal transport, or close Full Topic 13.",
    }


__all__ = [
    "DissipativeTransportWitness",
    "conservative_action_transport_witnesses",
    "transport_coefficient_identifiability_contract",
]
