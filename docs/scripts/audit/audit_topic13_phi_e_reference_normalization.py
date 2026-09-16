"""Audit the source-backed reference normalization of the named Phi_E lane."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.thermal_phi_e_reference_normalization import (
    PhiEReferenceInputs,
    alpha_phi_e_K,
    phi_e_from_delta_u,
    phi_e_reference_contract,
    reference_energy_density_J_per_m3,
)


SOURCE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json"
ENERGY_REL = "docs/core/03_lanes/thermal/thermal_energy_response_bridge.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_phi_e_reference_normalization_audit.json"


def load(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def main() -> int:
    source = load(SOURCE_REL)
    row = next(item for item in source["representative_rows"] if item["temperature_K"] == 300.0)
    inputs = PhiEReferenceInputs(300.0, float(row["volumetric_cv_J_per_m3_K"]))
    e0 = reference_energy_density_J_per_m3(inputs)
    delta_u = 0.25 * e0
    phi_e = phi_e_from_delta_u(delta_u, inputs)
    alpha = alpha_phi_e_K(inputs.reference_cv_J_per_m3_K, inputs)
    contract = phi_e_reference_contract()
    checks = {
        "source_is_independent_cv_comparator": source["status"] == "SOURCE_LOCKED_INDEPENDENT_HARMONIC_CV_COMPARATOR",
        "reference_row_is_source_grid": row["row_identity"] == "source_grid",
        "reference_identity": abs(alpha - inputs.reference_temperature_K) <= 1.0e-12,
        "energy_normalization_round_trip": abs(phi_e - 0.25) <= 1.0e-14,
        "base_phi_map_remains_open": contract["base_Phi_identity"] == "not asserted; base Phi-to-Phi_E remains open",
        "no_target_or_holdout": source["holdout_policy"]["xie_2026_accessed"] is False and source["holdout_policy"]["target_curve_used"] is False,
    }
    status = "PASS_NAMED_PHI_E_REFERENCE_NORMALIZATION" if all(checks.values()) else "FAIL_T13_PHI_E_REFERENCE_NORMALIZATION"
    report = {
        "schema_version": "t13-phi-e-reference-normalization-v1",
        "artifact": "t13_phi_e_reference_normalization_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_PHI_E_REFERENCE_NORMALIZATION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": ["a source-backed reference energy density convention e0_ref=c_v(T_ref)*T_ref for named Phi_E", "a dimensional Phi_E-to-quasi-temperature operator with alpha(T_ref)=T_ref by convention", "an explicit uncertainty boundary and non-identity with base Phi"],
            "equation_or_mapping": contract,
            "units": {"e0_ref": "J m^-3", "c_v": "J m^-3 K^-1", "T_ref": "K", "Phi_E": "dimensionless", "alpha_Phi_E_K": "K per normalized Phi_E"},
            "derivation_class": "source-backed coordinate convention and standard energy/heat-capacity dimensional map",
            "observable": "named Phi_E energy-response/quasi-temperature operator only",
            "data_role": "INDEPENDENT_REFERENCE_NORMALIZATION_NOT_BASE_PHI_CALIBRATION",
            "evidence_artifacts": [{"path": SOURCE_REL, "sha256": sha256(SOURCE_REL)}, {"path": ENERGY_REL, "sha256": sha256(ENERGY_REL)}, {"path": "docs/core/07_artifacts/topic13/t13_phi_e_reference_normalization_audit.json"}],
            "verification_status": status,
            "open_blockers": ["base_Phi_to_Phi_E_mapping_missing", "Ding_specific_PBTE_C_src_and_material_matching_missing", "physical_field_normalization_and_independent_base_alpha_Phi_K_missing", "EOS_transport_SK_KMS_entropy_and_dissipative_closure_missing"],
            "dependency_unlocked": "named Phi_E dimensional operator only; no base-Phi bridge, full Topic 13, Core, or external-validation unlock",
            "claim_boundary": "The reference alpha is a coordinate convention in Phi_E, not a derived or calibrated alpha_Phi_K for base UET Phi."},
        "reference_row": row,
        "reference_energy_density_J_per_m3": e0,
        "witness": {"delta_u_J_per_m3": delta_u, "Phi_E": phi_e, "alpha_Phi_E_K_at_reference": alpha},
        "checks": checks,
        "numeric_base_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "base_Phi_to_Phi_E_mapping_and_independent_base_alpha_Phi_K_missing",
        "next_controller": "Obtain an independent physical amplitude mapping from base Phi to Phi_E or retain Phi_E as a separate lane; do not use the coordinate convention as a base-Phi calibration.",
        "claim_boundary": "No base-Phi alpha, TTG fit, physical field normalization, or external validation is emitted."}
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": [key for key,value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
