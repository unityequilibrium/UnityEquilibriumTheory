from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_gatech_volumetric_cp_independence_audit.json"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "gatech_gen3csp_graphite_source_package.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_scoped_source_independence_no_go_has_numeric_witness() -> None:
    audit = load(AUDIT)
    witness = audit["numeric_witness"]
    assert audit["status"] == "PASS_SCOPED_SOURCE_INDEPENDENCE_NO_GO"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert math.isclose(
        witness["rho_recovered_kg_per_m3"],
        witness["rho_assumed_kg_per_m3"],
        rel_tol=1.0e-12,
    )
    assert math.isclose(
        witness["cp_volumetric_from_k_over_D_J_per_m3_K"],
        witness["cp_volumetric_from_assumed_rho_J_per_m3_K"],
        rel_tol=1.0e-12,
    )


def test_source_package_discloses_publisher_and_local_preprocessing() -> None:
    package = load(PACKAGE)
    assert "no additional interpolation" in package["source"]["preprocessing"]
    assert (
        package["source"]["publisher_preprocessing"][
            "specific_heat_temperature_alignment"
        ]
        == "SOURCE_PROVIDER_1D_LINEAR_INTERPOLATION_TO_DIFFUSIVITY_TEMPERATURES"
    )
    assert package["property_origin_contract"]["thermal_conductivity"].endswith(
        "NOT_AN_INDEPENDENT_MEASUREMENT"
    )
    assert package["holdout_policy"]["xie_2026_accessed"] is False


def test_full_gate_records_no_go_without_promoting_topic() -> None:
    gate = load(GATE)
    branch = gate["verification_status"]["alpha_Phi_K"][
        "named_energy_response_branch"
    ]
    result = branch["source_independence_no_go"]
    assert result["status"] == "PASS_SCOPED_SOURCE_INDEPENDENCE_NO_GO"
    assert result["same_workbook_density_inversion_allowed"] is False
    assert result["same_workbook_volumetric_cp_inversion_allowed"] is False
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
    assert (
        "independent_same_grade_density_or_direct_volumetric_heat_capacity_missing"
        not in gate["major_result"]["what_remains_open"]
    )
    assert "density_uncertainty_not_source_locked" not in gate["major_result"]["what_remains_open"]
    assert "c_v_source_uncertainty_not_closed" in gate["major_result"]["what_remains_open"]
    assert "direct_volumetric_c_v_or_same_state_Cp_source_missing" not in gate["major_result"]["what_remains_open"]


def test_major_result_register_contains_scoped_no_go_only() -> None:
    register = load(REGISTER)
    entries = {
        entry["major_result_id"]: entry for entry in register["entries"]
    }
    result = entries["T13_GATECH_VOLUMETRIC_CP_INDEPENDENCE_NO_GO"]
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert register["claim_promotion"] is False
    assert register["next_major_result"] == "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"
