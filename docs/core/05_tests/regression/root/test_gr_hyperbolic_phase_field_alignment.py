"""Alignment tests for the sourced hyperbolic phase-field comparator wave."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

from docs.core.core_paths import canonical_existing_path, repo_root

from docs.core.uet_hyperbolic_phase_field import (
    HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV,
    HYPERBOLIC_PHASE_FIELD_SOURCE_DOI,
    HYPERBOLIC_PHASE_FIELD_STATUS,
    HyperbolicPhaseFieldState,
    hyperbolic_phase_field_contract,
    hyperbolic_phase_field_rhs,
)

ROOT = repo_root()
ARTIFACTS = ROOT / "docs/core/artifacts"
SOURCE_RECORD = (
    ROOT
    / "docs/data/external/condensed_matter/phase_transitions"
    / "hyperbolic_cahn_hilliard/dhaouadi_dumbser_gavrilyuk_2025"
    / "source_record.json"
)


def _load(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_generated_verification_is_partial_external_comparator() -> None:
    artifact = _load(
        "hyperbolic_phase_field_external_comparator_verification.json"
    )
    assert artifact["audit_status"] == "PASS"
    assert artifact["evidence_status"] == "PARTIAL_EXTERNAL_COMPARATOR"
    assert set(artifact["achieved_gates"].values()) == {"PASS"}
    assert set(artifact["blocked_gates"].values()) == {"BLOCKED"}


def test_formula_audit_separates_transcription_from_uet_derivation() -> None:
    artifact = _load("hyperbolic_phase_field_formula_audit.json")
    assert artifact["status"] == "WARN"
    assert artifact["transcription_status"] == "PASS"
    assert artifact["uet_derivation_status"] == "BLOCKED"


def test_source_contract_keeps_external_auxiliary_phase_separate() -> None:
    artifact = _load("hyperbolic_phase_field_source_contract.json")
    assert artifact["provenance_status"] == "PASS"
    assert artifact["status"] == HYPERBOLIC_PHASE_FIELD_STATUS
    assert "auxiliary_phase_is_not_UET_space_response" in artifact[
        "forbidden_identifications"
    ]
    assert artifact["trace_backreaction"] is False


def test_source_record_has_required_identity_and_no_committed_raw_copy() -> None:
    source = json.loads(SOURCE_RECORD.read_text(encoding="utf-8"))
    assert source["doi"] == HYPERBOLIC_PHASE_FIELD_SOURCE_DOI
    assert source["arxiv_id"] == HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV
    assert source["local_path"] is None
    assert source["local_copy_status"] == (
        "TEMPORARY_INSPECTION_ONLY_NOT_REDISTRIBUTED"
    )
    assert len(source["upstream_source_archive_sha256"]) == 64
    assert source["benchmark_role"] == (
        "EXTERNAL_MATHEMATICAL_COMPARATOR_NOT_PHYSICAL_VALIDATION"
    )


def test_source_record_has_all_formula_locators() -> None:
    source = json.loads(SOURCE_RECORD.read_text(encoding="utf-8"))
    identifiers = {item["id"] for item in source["formula_locators"]}
    assert {
        "first_order_hyperbolic_system",
        "augmented_lyapunov_functional",
        "characteristic_speeds",
        "formal_cahn_hilliard_scaling",
    } <= identifiers


def test_artifact_source_hashes_match_current_inputs() -> None:
    artifact = _load(
        "hyperbolic_phase_field_external_comparator_verification.json"
    )
    for relative, expected in artifact["source_hashes"].items():
        assert _sha(canonical_existing_path(ROOT / relative)) == expected


def test_public_rhs_has_no_trace_or_space_response_input() -> None:
    parameters = inspect.signature(hyperbolic_phase_field_rhs).parameters
    assert "trace" not in parameters
    assert "space_response" not in parameters
    assert list(HyperbolicPhaseFieldState.__dataclass_fields__) == [
        "C",
        "flux_impulse",
        "auxiliary_rate",
        "gradient_proxy",
        "auxiliary_phase",
    ]


def test_program_gate_advances_stage_without_promotion() -> None:
    program = _load("uet_gr_research_program_gate.json")
    assert program["status"] == "BLOCKED"
    assert program["program_stage"] == (
        "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED"
    )
    assert program["controlling_blocker"] == (
        "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing"
    )
    assert program["sector_status"]["gradient_phase_field_causality"] == (
        "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY"
    )
    assert program["sector_status"]["uniform_subluminal_phase_field_limit"] == (
        "NO_GO_FOR_EXACT_PARABOLIC_LIMIT"
    )
    assert program["sector_status"]["fixed_light_cone_parameter_domain"] == (
        "PASS_NORMALIZED_ANALYTIC"
    )
    assert program["claim_promotion"] == "BLOCKED"


def test_topic_and_global_closure_boundaries_remain_unchanged() -> None:
    program = _load("uet_gr_research_program_gate.json")
    contract = hyperbolic_phase_field_contract()
    assert program["global_universe_closure"] == "UNRESOLVED"
    assert program["topic_0_11_status_impact"] == "NONE"
    assert program["topic_0_19_status_impact"] == "NONE"
    assert contract["topic_0_11_status_impact"] == "NONE"
    assert contract["topic_0_19_status_impact"] == "NONE"