"""Audit a conditional standard graphite transport comparator."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "gatech_gen3csp_graphite_source_package.json"
)
SOURCE_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_graphite_source_audit.json"
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/gen3csp_graphite.xlsx"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_standard_transport_comparator_audit.json"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float, rel: float = 1.0e-11) -> bool:
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=1.0e-10)


def main() -> int:
    template = load(OUT)
    package = load(PACKAGE)
    source_audit = load(SOURCE_AUDIT)
    reported = package["reported_values"]
    cp = float(reported["average_specific_heat_J_per_g_K"]) * 1.0e3
    sigma_cp = float(reported["uncertainty_95pct_J_per_g_K"]) * 1.0e3
    diffusivity = float(reported["average_thermal_diffusivity_mm2_per_s"]) * 1.0e-6
    sigma_diffusivity = float(reported["uncertainty_thermal_diffusivity_95pct_mm2_per_s"]) * 1.0e-6
    rho = float(package["density_contract"]["value_g_per_cm3"]) * 1.0e3
    cv = cp * rho
    sigma_cv = sigma_cp * rho
    k = diffusivity * cv
    sigma_k = k * math.sqrt((sigma_diffusivity / diffusivity) ** 2 + (sigma_cp / cp) ** 2)
    reported_k = float(reported["average_thermal_conductivity_W_per_m_K"])
    reported_sigma_k = float(reported["uncertainty_thermal_conductivity_95pct_W_per_m_K"])
    checks = {
        "source_audit_passes": source_audit["status"] == "PASS_SOURCE_CP_95CI_CV_OPEN",
        "raw_hash_matches": sha256(RAW) == package["source"]["local_raw_sha256"],
        "temperature_is_declared": close(template["inputs"]["temperature_K"], 573.15),
        "cp_unit_conversion_matches": close(cp, template["inputs"]["cp_mass_J_per_kg_K"]),
        "diffusivity_unit_conversion_matches": close(diffusivity, template["inputs"]["diffusivity_m2_per_s"]),
        "assumed_density_matches": close(rho, template["inputs"]["rho_assumed_kg_per_m3"]),
        "volumetric_cp_conversion_is_explicit": close(cv, cp * rho),
        "conductivity_relation_matches_reported": close(k, reported_k),
        "conditional_sigma_cp_matches": close(sigma_cp, template["inputs"]["sigma_cp_95pct_J_per_kg_K"]),
        "conditional_sigma_diffusivity_matches": close(sigma_diffusivity, template["inputs"]["sigma_diffusivity_95pct_m2_per_s"]),
        "conditional_sigma_k_is_finite": math.isfinite(sigma_k) and sigma_k > 0.0,
        "source_reported_sigma_k_is_recorded": math.isfinite(reported_sigma_k) and reported_sigma_k > 0.0,
        "uncertainty_difference_is_disclosed": template["uncertainty_contract"]["status"] == "SOURCE_REPORTED_AND_FIRST_ORDER_PROPAGATED_ENVELOPES_SEPARATE",
        "density_uncertainty_remains_open": package["density_contract"]["status"] == "ASSUMED_CONSTANT_NO_SOURCE_UNCERTAINTY",
        "k_dependency_is_disclosed": package["property_origin_contract"]["thermal_conductivity"].endswith("NOT_AN_INDEPENDENT_MEASUREMENT"),
        "c_v_regime_remains_open": package["required_quantity_contract"]["conversion_status"] == "OPEN_CP_TO_CV_AND_DENSITY_UNCERTAINTY",
        "standard_comparator_not_uet_calibration": template["major_result"]["data_role"] == "STANDARD_MATERIAL_COMPARATOR_NOT_UET_CALIBRATION",
        "cattaneo_tau_not_source_claimed": template["synthetic_controls"]["cattaneo"]["relaxation_time_source"] != "source-locked",
        "trace_has_no_backreaction": template["synthetic_controls"]["trace_only"]["backreaction"] is False,
        "phi_alpha_not_emitted": template["synthetic_controls"]["phi_response"]["alpha_Phi_K_emitted"] is False,
        "target_curve_not_used": template["holdout_policy"]["target_curve_used"] is False,
        "xie_not_accessed": template["holdout_policy"]["xie_2026_accessed"] is False,
        "alpha_fit_not_used": template["holdout_policy"]["alpha_fit_used"] is False,
    }
    status = "PASS_STANDARD_GRAPHITE_TRANSPORT_COMPARATOR_CONDITIONAL" if all(checks.values()) else "FAIL_STANDARD_GRAPHITE_TRANSPORT_COMPARATOR"
    report = {
        "schema_version": "t13-gatech-standard-transport-comparator-audit-v1",
        "artifact": "t13_gatech_standard_transport_comparator_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": template["major_result"],
        "source_identity": template["source_identity"],
        "inputs": template["inputs"],
        "derived_comparator": {
            "temperature_K": 573.15,
            "cp_mass_J_per_kg_K": cp,
            "sigma_cp_95pct_J_per_kg_K": sigma_cp,
            "rho_assumed_kg_per_m3": rho,
            "cv_conditional_J_per_m3_K": cv,
            "sigma_cv_conditional_95pct_J_per_m3_K": sigma_cv,
            "diffusivity_m2_per_s": diffusivity,
            "sigma_diffusivity_95pct_m2_per_s": sigma_diffusivity,
            "k_reconstructed_W_per_m_K": k,
            "sigma_k_conditional_95pct_W_per_m_K": sigma_k,
            "k_reported_W_per_m_K": reported_k,
            "k_reported_uncertainty_95pct_W_per_m_K": reported_sigma_k,
            "sigma_k_difference_propagated_minus_source_reported_W_per_m_K": sigma_k - reported_sigma_k,
            "sigma_k_ratio_propagated_to_source_reported": sigma_k / reported_sigma_k,
        },
        "uncertainty_contract": template["uncertainty_contract"],
        "synthetic_controls": template["synthetic_controls"],
        "holdout_policy": template["holdout_policy"],
        "checks": checks,
        "controlling_blocker": "standard_comparator_is_not_a_UET_Phi_transport_coefficient_or_Ding_C_src",
        "next_controller": "Source-lock independent density/Cv and a material-regime map if a physical graphite comparator is needed; separately acquire a state-matched UET Kubo coefficient and base-Phi SI anchor.",
        "claim_boundary": template["claim_boundary"],
    }
    report["major_result"]["closure_level"] = "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN"
    report["major_result"]["verification_status"] = status
    report["major_result"]["what_is_closed"] = [
        "conditional standard graphite volumetric heat-capacity conversion from archived cp and assumed density",
        "conditional reconstruction of k from measured diffusivity and source-defined cp",
        "first-order comparator uncertainty envelope with density uncertainty explicitly excluded",
        "separation of Fourier/Cattaneo synthetic controls from UET Phi-response and trace-only lanes",
    ] if status.startswith("PASS") else []
    report["major_result"]["evidence_artifacts"] = [
        {"path": "docs/core/07_artifacts/topic13/t13_gatech_standard_transport_comparator_audit.json"},
        {"path": "docs/core/07_artifacts/topic13/t13_gatech_graphite_source_audit.json", "sha256": sha256(SOURCE_AUDIT)},
        {"path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/gatech_gen3csp_graphite_source_package.json", "sha256": sha256(PACKAGE)},
        {"path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/gen3csp_graphite.xlsx", "sha256": sha256(RAW)},
    ]
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"), "failed_checks": [key for key, value in checks.items() if not value], "cv_conditional_J_per_m3_K": cv, "k_conditional_W_per_m_K": k, "sigma_k_conditional_W_per_m_K": sigma_k}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
