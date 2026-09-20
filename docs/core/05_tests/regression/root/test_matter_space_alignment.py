"""API and ontology alignment gates for matter_space_coupled_v1."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

from dataclasses import fields
import json
from pathlib import Path

import numpy as np
import pytest

from docs.core import MATTER_SPACE_OPERATOR_MODE, MatterSpaceConfig, MatterSpaceState
from docs.core.uet_master_equation import (
    LEGACY_OPERATOR_MODE,
    SUPPORTED_OPERATOR_MODES,
    UETMasterEquation,
    dynamics_step_complete,
)
from docs.core.uet_parameters import UETParameters
from docs.core.uet_trace import UETStepResult


def _inputs() -> tuple[np.ndarray, MatterSpaceConfig, float]:
    C = 0.2 + 0.01 * np.cos(np.linspace(0.0, 2.0 * np.pi, 24, endpoint=False))
    cfg = MatterSpaceConfig(
        kappa_matter=0.05,
        kappa_space=0.1,
        mobility_matter=0.2,
        mobility_space=0.3,
        tau_space=0.8,
        coupling_g=0.1,
    )
    return C, cfg, 1e-4


def test_structured_result_preserves_first_five_positional_fields() -> None:
    assert [field.name for field in fields(UETStepResult)] == [
        "C",
        "V",
        "trace_observable",
        "energy_ledger",
        "diagnostics",
        "space_response",
        "space_rate",
    ]


def test_new_mode_is_opt_in_and_exported() -> None:
    assert MATTER_SPACE_OPERATOR_MODE == "matter_space_coupled_v1"
    assert MATTER_SPACE_OPERATOR_MODE in SUPPORTED_OPERATOR_MODES
    assert UETParameters().operator_mode == LEGACY_OPERATOR_MODE


@pytest.mark.parametrize("legacy_name", ["I", "V", "J_in", "J_out", "constraints"])
def test_engine_rejects_ambiguous_legacy_inputs(legacy_name: str) -> None:
    C, cfg, dt = _inputs()
    kwargs: dict[str, object] = {
        "operator_mode": MATTER_SPACE_OPERATOR_MODE,
        "matter_space_config": cfg,
    }
    kwargs[legacy_name] = {} if legacy_name == "constraints" else np.zeros_like(C)
    with pytest.raises(ValueError, match="ambiguous legacy inputs"):
        UETMasterEquation().step(C, dt=dt, dx=0.25, **kwargs)


def test_engine_initializes_ordered_space_reference_and_caches_source_only() -> None:
    C, cfg, dt = _inputs()
    engine = UETMasterEquation()
    result = engine.step(
        C,
        dt=dt,
        dx=0.25,
        operator_mode=MATTER_SPACE_OPERATOR_MODE,
        matter_space_config=cfg,
    )
    assert isinstance(result, UETStepResult)
    np.testing.assert_allclose(result.space_response, 0.0, atol=2e-8)
    assert result.space_rate is not None
    assert engine.I is None
    assert engine.V is None
    assert len(engine.trace_history) == 1
    assert result.trace_observable is None
    assert result.diagnostics["ontology"] == "physical_C_Phi_Pi_with_derived_trace_only"


def test_explicit_entry_point_and_compatibility_function_agree() -> None:
    C, cfg, dt = _inputs()
    state = MatterSpaceState(C, np.zeros_like(C), np.zeros_like(C))
    explicit = UETMasterEquation().step_matter_space(state, dt, 0.25, cfg)
    compatible = dynamics_step_complete(
        C,
        dt=dt,
        dx=0.25,
        operator_mode=MATTER_SPACE_OPERATOR_MODE,
        matter_space_state=state,
        matter_space_config=cfg,
    )
    np.testing.assert_allclose(explicit.C, compatible.C, rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(
        explicit.space_response, compatible.space_response, rtol=0.0, atol=1e-12
    )
    np.testing.assert_allclose(explicit.space_rate, compatible.space_rate, rtol=0.0, atol=1e-12)


def test_compatibility_function_rejects_state_C_mismatch() -> None:
    C, cfg, dt = _inputs()
    state = MatterSpaceState(C + 0.1, np.zeros_like(C), np.zeros_like(C))
    with pytest.raises(ValueError, match="must match"):
        dynamics_step_complete(
            C,
            dt=dt,
            dx=0.25,
            operator_mode=MATTER_SPACE_OPERATOR_MODE,
            matter_space_state=state,
            matter_space_config=cfg,
        )


def test_legacy_default_and_explicit_legacy_mode_are_unchanged() -> None:
    C, _, _ = _inputs()
    params = UETParameters(alpha=0.2, gamma=0.0, kappa=0.1, beta=0.0, W_N=0.0)
    implicit = dynamics_step_complete(C, dt=0.001, dx=0.25, params=params)
    explicit = dynamics_step_complete(
        C, dt=0.001, dx=0.25, params=params, operator_mode=LEGACY_OPERATOR_MODE
    )
    np.testing.assert_allclose(implicit, explicit, rtol=0.0, atol=0.0)



def test_generated_artifacts_keep_failed_controller_machine_readable() -> None:
    verification = json.loads(
        canonical_artifact_path("matter_space_variational_verification.json").read_text(encoding="utf-8")
    )
    dependency = json.loads(
        canonical_artifact_path("matter_space_dependency_gate.json").read_text(encoding="utf-8")
    )
    alignment = json.loads(
        canonical_artifact_path("master_equation_alignment_gate_v2.json").read_text(encoding="utf-8")
    )
    assert verification["status"] in {"PASS", "FAIL"}
    assert dependency["core_verification_status"] == verification["status"]
    assert dependency["claim_promotion"] in {"BLOCKED", "NOT_AUTOMATIC"}
    assert alignment["matter_space_contract"]["implementation_gate"] == "PASS"
    assert alignment["matter_space_contract"]["SI_gate"] == "BLOCKED"
    assert verification["run_contract"]["trace_backreaction"] is False


def test_formula_audit_links_present_implementation_without_si_promotion() -> None:
    artifact = canonical_artifact_path("matter_space_formula_audit.json")
    audit = json.loads(artifact.read_text(encoding="utf-8"))
    assert audit["status"] == "WARN"
    assert audit["implementation_status"] == "PRESENT"
    assert all(entry["implementation_status"] == "PRESENT" for entry in audit["formula_registry"])
    assert all("(target)" not in entry["implementation"] for entry in audit["formula_registry"])
    assert audit["coefficient_policy"]["physical_constant_claim"] is False
