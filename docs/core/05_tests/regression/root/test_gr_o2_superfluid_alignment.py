from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

import docs.core as core

from docs.scripts.audit.audit_uet_o2_superfluid_transport import build_artifacts

ROOT = repo_root()
OUT = ROOT / "docs/core/artifacts"


def _load(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_generated_wave10_artifacts_match_the_committed_payloads() -> None:
    stored = (
        _load("o2_finite_density_eos_verification.json"),
        _load("o2_eos_formula_audit.json"),
        _load("covariant_superfluid_transport_verification.json"),
        _load("covariant_superfluid_transport_contract.json"),
        _load("uet_gr_research_program_gate.json"),
    )
    generated = build_artifacts(generated_at=stored[0]["generated_at"])
    assert stored == generated


def test_eos_and_ideal_transport_pass_without_promoting_physical_transport() -> None:
    eos = _load("o2_finite_density_eos_verification.json")
    formula = _load("o2_eos_formula_audit.json")
    transport = _load("covariant_superfluid_transport_verification.json")
    contract = _load("covariant_superfluid_transport_contract.json")
    assert eos["audit_status"] == "PASS"
    assert all(eos["gates"].values())
    assert formula["status"] == "WARN"
    assert transport["audit_status"] == "PASS"
    assert all(transport["gates"].values())
    assert transport["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED"
    assert contract["status"] == "BLOCKED"
    assert contract["interface_status"] == "PASS"
    assert contract["core_contract"]["normal_component"] == "OPEN_NOT_DERIVED"


def test_double_well_stays_a_rejected_constitutive_comparator() -> None:
    eos = _load("o2_finite_density_eos_verification.json")
    reduction = eos["double_well_reduction"]
    assert reduction["status"] == "REJECTED_REMAINS_CONSTITUTIVE_COMPARATOR"
    assert reduction["fitted_parameters"] is False
    assert (
        eos["metrics"]["double_well_reduction_relative_residual"]
        > eos["thresholds"]["double_well_reduction_relative_max"]
    )


def test_program_gate_advances_monotonically_but_remains_blocked() -> None:
    program = _load("uet_gr_research_program_gate.json")
    assert program["version"] == "wave10_v1"
    assert (
        program["program_stage"]
        == "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED"
    )
    assert program["sector_status"]["equation_of_state_from_matter_action"] == "PASS_TREE_LEVEL_T0"
    assert program["sector_status"]["covariant_T0_superfluid_constitutive"] == "PASS_PURE_SUPERFLUID"
    assert program["sector_status"]["physical_Kubo_coefficients"] == "BLOCKED"
    assert program["status"] == "BLOCKED"
    assert program["claim_promotion"] == "BLOCKED"
    assert program["global_universe_closure"] == "UNRESOLVED"
    assert program["topic_0_11_status_impact"] == "NONE"
    assert program["topic_0_19_status_impact"] == "NONE"
    assert (
        program["controlling_blocker"]
        == "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing"
    )


def test_public_api_exports_new_opt_in_contract_without_legacy_replacement() -> None:
    assert core.O2_SUPERFLUID_TRANSPORT_OPERATOR_MODE == "o2_superfluid_transport_v1"
    assert core.o2_finite_density_eos_contract()["trace_input"] is False
    assert core.covariant_superfluid_transport_contract()["trace_backreaction"] is False
    assert core.covariant_superfluid_transport_contract()["si_lane"] == "BLOCKED"


def test_source_records_are_role_sources_not_validation_data() -> None:
    eos = _load("o2_finite_density_eos_verification.json")
    assert eos["source_provenance"]["status"] == "PASS"
    for record in eos["source_provenance"]["records"]:
        assert "NOT_UET_DERIVATION" in record["benchmark_role"] or "NOT_COEFFICIENT_DATA" in record["benchmark_role"]
        assert record["checks"]["claim_boundary_present"] is True
