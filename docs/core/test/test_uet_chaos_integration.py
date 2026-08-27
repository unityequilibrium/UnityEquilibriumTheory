from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8-sig"))


def test_core_and_topic_method_results_are_registered_without_claim_promotion() -> None:
    core = load("docs/core/artifacts/uet_dynamical_stability_diagnostic.json")
    method = load(
        "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/chaos_method_validation.json"
    )
    register = load("docs/core/artifacts/uet_major_result_closure_register.json")
    entries = {item["major_result_id"]: item for item in register["entries"]}

    assert core["status"] == "PASS_CORE_DYNAMICAL_STABILITY_DIAGNOSTIC"
    assert core["claim_promotion"] is False
    assert method["status"] == "PASS_CHAOS_METHOD_VALIDATION"
    assert method["claim_promotion"] is False
    assert entries["CORE_DYNAMICAL_STABILITY_DIAGNOSTIC_READY"]["closure_level"] == "CLOSED_FOR_CORE"
    assert entries["T010_CHAOS_METHOD_VALIDATED"]["closure_level"] == "CLOSED_FOR_LANE"


def test_equation_registry_separates_lyapunov_function_and_exponent() -> None:
    registry = load("docs/core/artifacts/uet_equation_correspondence_registry.json")
    entries = {item["equation_id"]: item for item in registry["entries"]}
    required = {
        "uet.dynamics.tangent_map",
        "uet.dynamics.lyapunov_spectrum",
        "uet.dynamics.regime_classifier",
        "uet.dynamics.closed_gradient_no_sustained_chaos_boundary",
    }
    assert required <= set(entries)
    spectrum = entries["uet.dynamics.lyapunov_spectrum"]
    assert "distinct from the free-energy Lyapunov function" in spectrum["mathematical_role"]
    assert spectrum["unit_lane"] == "inverse normalized time"


def test_topic13_pilot_does_not_change_full_topic_or_holdout_state() -> None:
    pilot = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_thermal_dynamical_regime_audit.json"
    )
    matrix = load("docs/core/artifacts/t13_topic13_closure_matrix.json")
    full_gate = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
    )
    fluid = load(
        "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/fluid_benchmark_validation.json"
    )

    assert pilot["status"] == "PASS_SCOPED_THERMAL_DYNAMICAL_REGIME_PILOT"
    assert pilot["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert pilot["full_core_unlock"] is False
    assert pilot["holdout_access"]["holdout_consumed"] is False
    assert pilot["branches"]["trace_only"]["classification"] == "NOT_APPLICABLE_AS_DYNAMICAL_STATE"
    assert pilot["branches"]["open_kms"]["classification"] == "BLOCKED_INPUT_NOT_EVALUATED"
    for name in ("closed_matter_space", "periodically_driven_matter_space"):
        branch = pilot["branches"][name]
        assert branch["ledger_status"] == "PASS"
        assert branch["method_agreement"] is True
        assert branch["classification"] != "NUMERICAL_INSTABILITY"

    counts = matrix["closure_summary"]["current_subresult_counts"]
    assert matrix["closure_summary"]["required_subresult_count"] == 37
    assert counts == {"CLOSED_FOR_LANE": 21, "CLOSED_AS_NO_GO": 6, "OPEN": 10}
    assert matrix["full_core_unlock"] is False
    assert full_gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full_gate["verification_status"]["alpha_Phi_K"]["status"] == "BLOCKED"
    assert full_gate["verification_status"]["holdout_integrity"]["holdout_consumed"] is False
    assert fluid["results"]["status"] == "FAIL"
    assert fluid["results"]["speedup"] < fluid["thresholds"]["min_speedup"]


def test_only_diagnostic_rollout_is_unlocked() -> None:
    dependency = load("docs/core/artifacts/uet_major_result_dependency_unlock_gate.json")
    decisions = dependency["decisions"]
    assert decisions["TOPIC_0_11_CHAOS_DIAGNOSTIC_ROLLOUT"]["status"] == "UNLOCKED"
    assert decisions["CORE_O2_CHAOS_DIAGNOSTIC_ROLLOUT"]["status"] == "UNLOCKED"
    assert decisions["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"]["status"] == "UNLOCKED"
    assert decisions["GR_CLASSICAL_COMPATIBILITY_LANE"]["status"] == "BLOCKED_DEPENDENCY"
    assert dependency["claim_promotion"] is False
