"""Prediction-invariant interpretation adapters for operational QM.

QBism and relational QM are represented only as metadata views over one
preparation/POVM probability contract.  They introduce no physical dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .uet_quantum_measurement import DensityOperator, POVMRecord, born_probabilities


INTERPRETATION_STATUS = "PREDICTION_INVARIANT_COMPARISON_V1"


@dataclass(frozen=True)
class AgentBeliefRecord:
    agent_id: str
    preparation_id: str
    instrument_id: str
    probabilities: Mapping[str, float]
    interpretation: str = "QBism"


@dataclass(frozen=True)
class RelationalStateRecord:
    system_id: str
    reference_system_id: str
    preparation_id: str
    instrument_id: str
    probabilities: Mapping[str, float]
    interpretation: str = "RQM"


@dataclass(frozen=True)
class OperationalViewRecord:
    preparation_id: str
    instrument_id: str
    probabilities: Mapping[str, float]
    interpretation: str = "Operational_QM"


@dataclass(frozen=True)
class InterpretationComparison:
    operational: OperationalViewRecord
    qbist: AgentBeliefRecord
    relational: RelationalStateRecord
    maximum_probability_residual: float
    physical_dynamics_changed: bool
    generated_trace_changed: bool
    empirical_status: str


def operational_view(state: DensityOperator, povm: POVMRecord) -> OperationalViewRecord:
    return OperationalViewRecord(state.preparation_id, povm.instrument_id, born_probabilities(state, povm))


def qbist_view(state: DensityOperator, povm: POVMRecord, agent_id: str) -> AgentBeliefRecord:
    if not agent_id.strip():
        raise ValueError("agent_id is required")
    return AgentBeliefRecord(agent_id, state.preparation_id, povm.instrument_id, born_probabilities(state, povm))


def relational_view(state: DensityOperator, povm: POVMRecord, system_id: str, reference_system_id: str) -> RelationalStateRecord:
    if not system_id.strip() or not reference_system_id.strip():
        raise ValueError("system and reference-system ids are required")
    return RelationalStateRecord(system_id, reference_system_id, state.preparation_id, povm.instrument_id, born_probabilities(state, povm))


def compare_empirical_predictions(
    state: DensityOperator, povm: POVMRecord,
    agent_id: str = "agent-A", system_id: str = "system-S",
    reference_system_id: str = "reference-R",
) -> InterpretationComparison:
    operational = operational_view(state, povm)
    qbist = qbist_view(state, povm, agent_id)
    relational = relational_view(state, povm, system_id, reference_system_id)
    residual = max(
        abs(operational.probabilities[outcome] - view.probabilities[outcome])
        for outcome in operational.probabilities
        for view in (qbist, relational)
    )
    return InterpretationComparison(
        operational, qbist, relational, float(residual),
        physical_dynamics_changed=False, generated_trace_changed=False,
        empirical_status="IDENTICAL_OPERATIONAL_PREDICTIONS" if residual <= 1e-12 else "FAIL",
    )


def interpretation_contract() -> dict[str, Any]:
    return {
        "status": INTERPRETATION_STATUS,
        "operational_qm": "baseline preparation-channel-instrument-outcome contract",
        "qbism": "agent-indexed probability-assignment metadata",
        "rqm": "system-relation-indexed outcome metadata",
        "new_dynamics": False,
        "physical_state_inputs": False,
        "generated_trace_input": False,
        "prediction_rule": "shared Born probabilities",
        "claim_boundary": "comparison adapters only; prediction changes require a separately declared physical model",
    }


__all__ = ["INTERPRETATION_STATUS", "AgentBeliefRecord", "RelationalStateRecord", "OperationalViewRecord", "InterpretationComparison", "operational_view", "qbist_view", "relational_view", "compare_empirical_predictions", "interpretation_contract"]
