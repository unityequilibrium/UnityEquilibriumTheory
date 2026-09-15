"""Prove the scoped Georgia Tech volumetric-heat-capacity source no-go.

The archived row reports k, diffusivity, and c_p, but the publisher defines k
from those measured quantities and an assumed density. Inverting that identity
therefore cannot create an independent density or volumetric heat capacity.
"""

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
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_volumetric_cp_independence_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def close(a: float, b: float) -> bool:
    return math.isclose(float(a), float(b), rel_tol=1.0e-12, abs_tol=1.0e-12)


def main() -> int:
    package = load(PACKAGE)
    source_audit = load(SOURCE_AUDIT)
    reported = package["reported_values"]

    diffusivity_m2_per_s = reported["average_thermal_diffusivity_mm2_per_s"] * 1.0e-6
    cp_mass_J_per_kg_K = reported["average_specific_heat_J_per_g_K"] * 1.0e3
    rho_assumed_kg_per_m3 = package["density_contract"]["value_g_per_cm3"] * 1.0e3
    k_reported_W_per_m_K = reported["average_thermal_conductivity_W_per_m_K"]

    k_reconstructed_W_per_m_K = (
        diffusivity_m2_per_s * cp_mass_J_per_kg_K * rho_assumed_kg_per_m3
    )
    rho_recovered_kg_per_m3 = k_reported_W_per_m_K / (
        diffusivity_m2_per_s * cp_mass_J_per_kg_K
    )
    cp_volumetric_from_k_over_D_J_per_m3_K = (
        k_reported_W_per_m_K / diffusivity_m2_per_s
    )
    cp_volumetric_from_assumed_rho_J_per_m3_K = (
        rho_assumed_kg_per_m3 * cp_mass_J_per_kg_K
    )

    origins = package["property_origin_contract"]
    checks = {
        "upstream_source_audit_passes": source_audit["status"]
        == "PASS_SOURCE_CP_95CI_CV_OPEN",
        "raw_hash_remains_locked": sha256(RAW)
        == package["source"]["local_raw_sha256"],
        "diffusivity_is_measured": origins["thermal_diffusivity"]
        == "MEASURED_INDEPENDENTLY_BY_LFA",
        "cp_is_measured_then_publisher_interpolated": origins["specific_heat"]
        == "MEASURED_INDEPENDENTLY_BY_STA_THEN_SOURCE_INTERPOLATED_TO_DIFFUSIVITY_GRID",
        "density_is_assumed_not_measured": origins["density"]
        == "ASSUMED_CONSTANT_NOT_MEASURED_IN_THIS_PACKAGE",
        "conductivity_is_derived_not_independent": origins["thermal_conductivity"]
        == "DERIVED_FROM_DIFFUSIVITY_CP_AND_ASSUMED_DENSITY_NOT_AN_INDEPENDENT_MEASUREMENT",
        "reported_k_matches_declared_dependency": close(
            k_reported_W_per_m_K, k_reconstructed_W_per_m_K
        ),
        "inverse_density_recovers_assumption": close(
            rho_recovered_kg_per_m3, rho_assumed_kg_per_m3
        ),
        "k_over_D_recovers_assumed_rho_times_cp": close(
            cp_volumetric_from_k_over_D_J_per_m3_K,
            cp_volumetric_from_assumed_rho_J_per_m3_K,
        ),
        "density_uncertainty_is_not_source_locked": package["density_contract"][
            "status"
        ]
        == "ASSUMED_CONSTANT_NO_SOURCE_UNCERTAINTY",
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"]
        is False,
        "holdout_not_consumed": package["holdout_policy"][
            "xie_2026_source_data_consumed"
        ]
        is False,
    }
    status = (
        "PASS_SCOPED_SOURCE_INDEPENDENCE_NO_GO"
        if all(checks.values())
        else "FAIL_SOURCE_INDEPENDENCE_AUDIT"
    )
    open_blockers = [
        "independent_same_grade_density_or_direct_volumetric_heat_capacity_missing",
        "same_grade_alpha_V_and_K_T_missing",
        "material_regime_mapping_to_TTG_not_closed",
    ]
    equation = (
        "k_src := D_src * c_p,src * rho_assumed; "
        "rho_inverse := k_src/(D_src*c_p,src) = rho_assumed; "
        "C_p,V_inverse := k_src/D_src = rho_assumed*c_p,src"
    )
    report = {
        "schema_version": "t13-gatech-volumetric-cp-independence-audit-v1",
        "artifact": "t13_gatech_volumetric_cp_independence_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_GATECH_VOLUMETRIC_CP_INDEPENDENCE_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "The Georgia Tech row cannot independently identify density by inverting its reported conductivity.",
                "The Georgia Tech row cannot independently identify volumetric c_p through k/D because k already imports the assumed density.",
            ],
            "equation_or_mapping": equation,
            "units": {
                "D_src": "m^2 s^-1",
                "c_p_src": "J kg^-1 K^-1",
                "rho_assumed": "kg m^-3",
                "k_src": "W m^-1 K^-1",
                "C_p_V": "J m^-3 K^-1",
            },
            "derivation_class": "source-dependency algebra and scoped structural no-go",
            "observable": "independence of the material-property source inputs",
            "data_role": "SOURCE_PROVENANCE_AUDIT_ONLY; no calibration values consumed",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(PACKAGE), "sha256": sha256(PACKAGE)},
                {"path": rel(SOURCE_AUDIT), "sha256": sha256(SOURCE_AUDIT)},
                {"path": rel(RAW), "sha256": sha256(RAW)},
            ],
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "Rejects the circular same-workbook inversion route and permits an independent direct-c_v or same-grade density/thermoelastic source-acquisition wave.",
            "claim_boundary": "CLOSED_FOR_LANE applies only to the information dependency of this Georgia Tech package. It is not a no-go for all graphite sources and does not close c_v, alpha_Phi_K, or Topic 13.",
        },
        "equation_or_mapping": equation,
        "source_method_locators": {
            "graphite_page": "https://gen3csp.gatech.edu/graphite/ ; Thermal Conductivity and density notes",
            "uncertainty_page": "https://gen3csp.gatech.edu/uncertainty/ ; specific-heat interpolation and thermal-conductivity propagation sections",
        },
        "numeric_witness": {
            "diffusivity_m2_per_s": diffusivity_m2_per_s,
            "cp_mass_J_per_kg_K": cp_mass_J_per_kg_K,
            "rho_assumed_kg_per_m3": rho_assumed_kg_per_m3,
            "k_reported_W_per_m_K": k_reported_W_per_m_K,
            "k_reconstructed_W_per_m_K": k_reconstructed_W_per_m_K,
            "rho_recovered_kg_per_m3": rho_recovered_kg_per_m3,
            "cp_volumetric_from_k_over_D_J_per_m3_K": cp_volumetric_from_k_over_D_J_per_m3_K,
            "cp_volumetric_from_assumed_rho_J_per_m3_K": cp_volumetric_from_assumed_rho_J_per_m3_K,
        },
        "checks": checks,
        "what_changed": "The source dependency graph is now explicit and the same-workbook inverse-density route is closed as circular.",
        "verification": "Publisher method roles, archived row identity, exact unit conversions, algebraic reconstruction, source hashes, and holdout non-access are checked.",
        "controlling_blocker": "independent_same_grade_density_or_direct_volumetric_heat_capacity_missing",
        "next_action": "Acquire a permitted direct volumetric c_v source or independently measured EMS-5000/same-specimen density with uncertainty, then source-lock same-regime alpha_V and K_T; do not infer these from the reported k/D/c_p identity.",
        "claim_boundary": "This is a scoped source-independence no-go, not thermodynamic closure or external validation.",
    }
    OUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": status,
                "artifact": rel(OUT),
                "rho_recovered_kg_per_m3": rho_recovered_kg_per_m3,
            },
            indent=2,
        )
    )
    return 0 if status == "PASS_SCOPED_SOURCE_INDEPENDENCE_NO_GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
