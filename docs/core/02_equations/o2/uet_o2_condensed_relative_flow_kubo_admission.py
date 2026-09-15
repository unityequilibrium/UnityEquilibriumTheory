"""State-matched Kubo admission for the declared Topic 13 channel.

The preceding condensed loop lane supplies a natural-unit retarded response.
This module turns that response into an explicit coefficient record with the
fields required by the transport contract.  Admission is scoped to the
declared condensed relative-flow contact channel; it does not assert a full
interacting 1PI theory, an external measurement, or an SI transport value.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from docs.core.uet_o2_condensed_loop_renormalized_vertex import (
    LOOP_VERTEX_ACCEPTANCE_THRESHOLD,
    CondensedLoopRenormalizedVertexState,
    condensed_loop_renormalized_vertex_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)

KUBO_ADMISSION_STATUS = (
    "PASS_KUBO_MATCHED_DECLARED_CONDENSED_RELATIVE_FLOW_CHANNEL"
)
KUBO_FORMULA_ID = "uet.o2.thermal.condensed_loop_relative_flow_kubo"
KUBO_EVIDENCE_STATUS = "KUBO_MATCHED"
ACCEPTED_EVIDENCE_STATUSES = ("KUBO_MATCHED", "SOURCE_LOCKED", "EXTERNALLY_MATCHED")


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _source_hash(value: str) -> str:
    result = str(value).lower()
    if len(result) != 64 or any(character not in "0123456789abcdef" for character in result):
        raise ValueError("source_hash must be a 64-character hexadecimal digest")
    return result


@dataclass(frozen=True)
class CondensedRelativeFlowKuboAdmissionState:
    """Accepted coefficient record and scoped admission state."""

    coefficient_name: str
    value: float
    units: str
    hydrodynamic_frame: str
    temperature: float
    chemical_potential: float
    space_response: float
    correlator_formula_id: str
    source_path_or_url: str
    source_hash: str
    evidence_status: str
    uncertainty: float
    uncertainty_scope: str
    state_match: bool
    independent_of_target_data: bool
    holdout_accessed: bool
    parameter_fitting_performed: bool
    physical_anchor_supplied: bool
    physical_kubo_admission_completed: bool
    full_core_unlock: bool
    data_role: str = "DERIVED_ACTION_KUBO_MATCHED_DECLARED_CHANNEL"

    def record(self) -> dict[str, Any]:
        """Return the machine-readable coefficient record."""

        return {
            "coefficient_name": self.coefficient_name,
            "value": self.value,
            "units": self.units,
            "hydrodynamic_frame": self.hydrodynamic_frame,
            "temperature": self.temperature,
            "chemical_potential": self.chemical_potential,
            "space_response": self.space_response,
            "correlator_formula_id": self.correlator_formula_id,
            "source_path_or_url": self.source_path_or_url,
            "source_hash": self.source_hash,
            "evidence_status": self.evidence_status,
            "uncertainty": self.uncertainty,
            "uncertainty_scope": self.uncertainty_scope,
            "state_match": self.state_match,
            "independent_of_target_data": self.independent_of_target_data,
            "holdout_accessed": self.holdout_accessed,
            "parameter_fitting_performed": self.parameter_fitting_performed,
            "physical_anchor_supplied": self.physical_anchor_supplied,
            "physical_kubo_admission_completed": self.physical_kubo_admission_completed,
            "full_core_unlock": self.full_core_unlock,
            "data_role": self.data_role,
        }


def condensed_relative_flow_kubo_admission_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    *,
    source_path_or_url: str,
    source_hash: str,
    reference_space_response: float = 0.0,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    loop_state: CondensedLoopRenormalizedVertexState | None = None,
) -> CondensedRelativeFlowKuboAdmissionState:
    """Build an accepted Kubo record for the declared natural-unit channel."""

    source_path_or_url = str(source_path_or_url)
    if not source_path_or_url:
        raise ValueError("source_path_or_url must not be empty")
    source_hash = _source_hash(source_hash)
    state = loop_state or condensed_loop_renormalized_vertex_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        reference_space_response=reference_space_response,
    )
    value = _finite(state.dc_relative_response, "Kubo coefficient")
    uncertainty = _finite(state.numerical_uncertainty_bound, "Kubo uncertainty")
    if value <= 0.0 or uncertainty < 0.0:
        raise ValueError("Kubo coefficient must be positive and uncertainty non-negative")
    state_match = (
        abs(state.temperature - float(temperature)) <= 1.0e-15
        and abs(state.chemical_potential - float(chemical_potential)) <= 1.0e-15
        and abs(state.space_response - float(space_response)) <= 1.0e-15
        and state.branch == "condensed"
    )
    admission = bool(
        state.loop_renormalization_convergence_passes
        and state.state_matched_retarded_response_completed
        and state.kms_residual <= 1.0e-12
        and state.fdt_residual <= 1.0e-12
        and state.dc_relative_response > 0.0
        and uncertainty <= LOOP_VERTEX_ACCEPTANCE_THRESHOLD
        and state_match
    )
    return CondensedRelativeFlowKuboAdmissionState(
        coefficient_name="K_rel^natural(omega->0)",
        value=value,
        units="natural-unit relative-flow response coefficient; not SI conductivity",
        hydrodynamic_frame="declared condensed relative-flow frame",
        temperature=float(temperature),
        chemical_potential=float(chemical_potential),
        space_response=float(space_response),
        correlator_formula_id=KUBO_FORMULA_ID,
        source_path_or_url=source_path_or_url,
        source_hash=source_hash,
        evidence_status=KUBO_EVIDENCE_STATUS if admission else "OPEN_NOT_ADMITTED",
        uncertainty=uncertainty,
        uncertainty_scope="numerical quadrature convergence for the declared action-derived channel only; no external or model-systematic uncertainty is claimed",
        state_match=state_match,
        independent_of_target_data=(
            state.target_data_used is False and state.xie_2026_accessed is False
        ),
        holdout_accessed=state.xie_2026_accessed,
        parameter_fitting_performed=state.parameter_fitting_performed,
        physical_anchor_supplied=False,
        physical_kubo_admission_completed=admission,
        full_core_unlock=False,
    )


def condensed_relative_flow_kubo_admission_contract() -> dict[str, Any]:
    """Return the admission fields and scoped claim boundary."""

    return {
        "status": KUBO_ADMISSION_STATUS,
        "equations": {
            "retarded_correlator": "G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)",
            "zero_frequency_coefficient": "K_rel^natural=lim_(omega->0) Re G_R^rel(omega)=D_rel/Gamma_rel",
            "uncertainty": "u(K_rel)=K_rel*max(r_radial,r_angular,r_scale)",
        },
        "required_coefficient_fields": [
            "coefficient_name",
            "value",
            "units",
            "hydrodynamic_frame",
            "temperature",
            "chemical_potential",
            "space_response",
            "correlator_formula_id",
            "source_path_or_url",
            "source_hash",
            "evidence_status",
            "uncertainty",
            "uncertainty_scope",
        ],
        "accepted_evidence_statuses": list(ACCEPTED_EVIDENCE_STATUSES),
        "unit_contract": {
            "coefficient": "natural-unit relative-flow response coefficient; not SI conductivity",
            "temperature_chemical_potential": "natural energy",
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state or feedback input",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "derivation_class": "action-derived loop-renormalized condensed contact channel matched to its declared retarded response at one state",
        "observable": "state-matched zero-frequency relative-flow Kubo coefficient in natural units",
        "data_role": "DERIVED_ACTION_KUBO_MATCHED_DECLARED_CHANNEL",
        "scope": "declared condensed relative-flow contact channel only",
        "excluded": [
            "complete condensed 1PI vertex and all scattering channels",
            "full interacting SK/KMS action matching",
            "SI transport coefficient",
            "independent physical vertex anchor",
            "alpha_Phi_K calibration",
            "TTG validation",
            "Full Topic 13 closure",
        ],
        "claim_boundary": (
            "This closes Kubo admission for one declared action-derived condensed "
            "relative-flow contact channel in natural units. It does not claim an "
            "external measurement, a complete interacting transport theory, an SI "
            "coefficient, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "ACCEPTED_EVIDENCE_STATUSES",
    "KUBO_ADMISSION_STATUS",
    "KUBO_EVIDENCE_STATUS",
    "KUBO_FORMULA_ID",
    "CondensedRelativeFlowKuboAdmissionState",
    "condensed_relative_flow_kubo_admission_contract",
    "condensed_relative_flow_kubo_admission_state",
]
