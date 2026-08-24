from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MATRIX = ROOT / "docs/core/artifacts/t13_topic13_closure_matrix.json"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_topic13_closure_matrix_reports_full_topic_contract_without_promotion() -> None:
    matrix = load(MATRIX)
    gate = load(GATE)
    required = {
        "causal_structure",
        "dimensional_phi_to_thermal_observable_map",
        "independent_alpha_Phi_K",
        "beta_and_si_correspondence",
        "charge_density_eos",
        "covariant_thermal_transport",
        "sk_kms_matching",
        "entropy_current_and_dissipative_balance",
        "source_and_uncertainty",
        "heat_flux_entropy_production_mapping",
    }
    required_record_fields = {
        "major_result_id",
        "topic",
        "closure_level",
        "what_is_closed",
        "equation_or_mapping",
        "units",
        "derivation_class",
        "observable",
        "data_role",
        "evidence_artifacts",
        "verification_status",
        "open_blockers",
        "dependency_unlocked",
        "claim_boundary",
    }
    assert matrix["schema_version"] == "t13-topic13-closure-matrix-v2"
    assert matrix["major_result"]["major_result_id"] == "T13_TOPIC13_CLOSURE_MATRIX"
    assert {item["requirement_id"] for item in matrix["requirements"]} == required
    assert matrix["status"] == gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert matrix["major_result"]["closure_level"] == "PARTIAL"
    assert matrix["claim_promotion"] is False
    assert matrix["full_core_unlock"] is False
    assert matrix["holdout_policy"]["xie_2026_accessed"] is False
    assert matrix["holdout_policy"]["calibration_path_may_read_holdout"] is False
    assert matrix["major_result"]["open_blockers"] == gate["major_result"]["what_remains_open"]
    assert matrix["closure_summary"]["open_blocker_groups"] == gate["major_result"]["closure_summary"]["open_blocker_groups"]
    assert matrix["full_topic_closure_contract"]["required_major_result_count"] == 10
    assert matrix["full_topic_closure_contract"]["required_subresult_count"] == 36
    assert matrix["full_topic_closure_contract"]["required_input_package_count"] == 3
    assert (
        matrix["full_topic_closure_contract"]["input_package_audit"]["path"]
        == "docs/core/artifacts/t13_closure_input_package_audit.json"
    )
    assert (
        matrix["full_topic_closure_contract"]["input_package_audit"]["summary"]["status"]
        == "PASS_SCOPED_T13_CLOSURE_INPUT_AUDIT_OPEN"
    )
    assert {
        item["package_id"] for item in matrix["full_topic_closure_contract"]["closure_input_packages"]
    } == {
        "T13_INPUT_DING_TTG_SOURCE",
        "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
        "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
    }
    assert matrix["closure_summary"]["current_subresult_counts"] == {
        "CLOSED_AS_NO_GO": 5,
        "CLOSED_FOR_LANE": 21,
        "OPEN": 10,
    }
    assert matrix["closure_summary"]["closure_count_unit"] == "required_subresults"
    assert matrix["closure_summary"]["closed_as_no_go_count"] == 5
    assert matrix["closure_summary"]["closed_lane_count"] == 21
    assert matrix["closure_summary"]["closed_for_core_count"] == 0
    assert matrix["closure_summary"]["open_subresult_count"] == 10
    assert matrix["closure_summary"]["reported_subresult_count"] == 36
    assert set(matrix["closure_summary"]["source_gate_projection_counts"]) == {
        "closed_lane_result_count",
        "closed_as_no_go_result_count",
    }
    for item in matrix["requirements"]:
        assert required_record_fields <= set(item)
        assert item["subresult_summary"]["required_count"] == len(item["required_subresults"])
        for subresult in item["required_subresults"]:
            assert {"subresult_id", "label", "status", "acceptance"} <= set(subresult)
            if subresult["status"] == "OPEN":
                assert subresult["required_closure_level"] == "CLOSED_FOR_CORE"
    causal = next(item for item in matrix["requirements"] if item["requirement_id"] == "causal_structure")
    assert causal["closure_level"] == "CLOSED_AS_NO_GO"
    assert causal["gate_status"] == "PASS"
    assert causal["gate_lane_closure_level"] == "CLOSED_FOR_LANE"
    alpha = next(item for item in matrix["requirements"] if item["requirement_id"] == "independent_alpha_Phi_K")
    assert alpha["closure_level"] == "OPEN"
    assert alpha["gate_status"] == "BLOCKED"
    assert "alpha_Phi_K" in alpha["what_remains_open"]
    transport = next(item for item in matrix["requirements"] if item["requirement_id"] == "covariant_thermal_transport")
    assert transport["gate_status"] == "BLOCKED"
    assert transport["component_lane_status"] == "PASS_SCOPED_T13_FLAT_COMPONENTS_WITH_EXTERNAL_INPUT"
    assert transport["component_lane_closure_level"] == "CLOSED_FOR_LANE"
    assert transport["component_lane_controlling_blocker"] == "physical_Kubo_coefficient_record_missing"


def test_topic13_closure_matrix_is_projected_into_register_and_dependency_gate() -> None:
    matrix = load(MATRIX)
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_TOPIC13_CLOSURE_MATRIX")
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    projection = dependency["topic13_partial_evidence"]["closure_matrix"]
    assert entry["closure_level"] == "PARTIAL"
    assert entry["claim_promotion"] is False
    assert entry["evidence_artifacts"][0]["path"] == "docs/core/artifacts/t13_topic13_closure_matrix.json"
    assert entry["evidence_artifacts"][0]["sha256"] == digest(MATRIX)
    assert full_entry["closure_matrix"]["sha256"] == digest(MATRIX)
    assert full_entry["closure_matrix"]["required_major_result_count"] == 10
    assert full_entry["closure_matrix"]["required_subresult_count"] == 36
    assert projection["path"] == "docs/core/artifacts/t13_topic13_closure_matrix.json"
    assert projection["sha256"] == digest(MATRIX)
    assert projection["full_core_unlock"] is False
    assert dependency["topic13_partial_evidence"]["full_topic_closure_contract"]["full_topic_ready"] is False
