"""Audit the source-locked 300 K graphite isothermal bulk-modulus route.

Hanfland et al. report a fixed-temperature pressure-volume equation of state
for natural graphite powder and give the ambient-pressure bulk modulus.  This
audit locks the scalar row and its units/provenance.  It does not digitize the
figure or refit the source, and it does not claim a Ding material match.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "hanfland_1989_graphite_isothermal_kt_source_package.json"
)
RAW_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "hanfland_1989_graphite_equation_of_state.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_graphite_isothermal_kt_source_audit.json"
EXPECTED_RAW_SHA256 = "300a6b03af667f71a27fc7c269e7a928af57d4b846bded25feaefa0e37b1089e"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8-sig"))
    source = package["source"]
    row = package["source_row"]
    contract = package["thermodynamic_contract"]
    actual_hash = digest(RAW_PATH) if RAW_PATH.is_file() else None
    checks = {
        "source_pdf_present": RAW_PATH.is_file(),
        "source_pdf_hash_matches": actual_hash == EXPECTED_RAW_SHA256,
        "package_source_identity_present": bool(source.get("doi") and source.get("source_locators")),
        "fixed_temperature_declared": float(source.get("temperature_K", 0.0)) == 300.0,
        "pressure_volume_method_declared": "X-ray diffraction" in source.get("measurement_method", ""),
        "isothermal_definition_explicit": "_T" in contract.get("definition", "") and "partial P" in contract.get("definition", ""),
        "source_row_identity_present": bool(row.get("row_id") and row.get("row_identity")),
        "K_T_value_positive": float(row.get("K_T_GPa", 0.0)) > 0.0,
        "K_T_uncertainty_positive": float(row.get("K_T_uncertainty_GPa", 0.0)) > 0.0,
        "reference_volume_positive": float(row.get("volume_at_reference_A3_per_unit_cell", 0.0)) > 0.0,
        "no_figure_refit_performed": "no figure digitization" in row.get("preprocessing", ""),
        "same_state_alpha_not_claimed": contract["same_state_alpha_V_available"] is False,
        "same_state_density_uncertainty_not_claimed": contract["same_state_density_uncertainty_available"] is False,
        "same_state_Cp_Cv_not_claimed": contract["same_state_Cp_Cv_available"] is False,
        "Ding_material_mapping_not_claimed": contract["Ding_material_regime_mapping_closed"] is False,
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "target_fit_not_performed": package["holdout_policy"]["target_curve_used"] is False,
        "alpha_Phi_K_fit_not_performed": package["holdout_policy"]["alpha_fit_used"] is False,
    }
    passed = all(checks.values())
    result = {
        "schema_version": "t13-graphite-isothermal-kt-source-audit-v1",
        "artifact": "t13_graphite_isothermal_kt_source_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_ISOTHERMAL_GRAPHITE_K_T_SOURCE" if passed else "FAIL_GRAPHITE_ISOTHERMAL_K_T_AUDIT",
        "major_result": {
            "major_result_id": "T13_GRAPHITE_ISOTHERMAL_KT_SOURCE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the Hanfland et al. primary graphite EOS PDF is archived with a reproducible local hash",
                "the fixed-temperature 300 K ambient-pressure K_T row is source-locked with volume, uncertainty, locator, and material identity",
                "the isothermal derivative definition is explicit and is not inferred from C33 or the Bosak dynamic elastic row",
                "the scalar input is admissible as a declared standard-thermodynamic comparator for the Cp-to-Cv contract",
            ],
            "equation_or_mapping": {
                "isothermal_bulk_modulus": "K_T(T0,P0) = -V*(partial P/partial V)_T = dP/d(-ln V)",
                "source_fit": "Murnaghan EOS at T0=300 K and P0=0: K_T=33.8 +/- 3.0 GPa",
            },
            "units": {
                "temperature": "K",
                "pressure": "GPa",
                "volume": "Angstrom^3 per unit cell",
                "K_T": "GPa = 10^9 Pa = 10^9 J m^-3",
            },
            "derivation_class": "source transcription of fixed-temperature XRD EOS fit; no local refit and no UET derivation",
            "observable": "ambient-pressure room-temperature graphite isothermal bulk modulus",
            "data_role": "EXTERNAL_INPUT_STANDARD_THERMODYNAMIC_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": PACKAGE_PATH.relative_to(ROOT).as_posix(), "sha256": digest(PACKAGE_PATH)},
                {"path": RAW_PATH.relative_to(ROOT).as_posix(), "sha256": actual_hash},
            ],
            "verification_status": "PASS_SCOPED_ISOTHERMAL_GRAPHITE_K_T_SOURCE" if passed else "FAIL_GRAPHITE_ISOTHERMAL_K_T_AUDIT",
            "open_blockers": [
                "natural_graphite_powder_to_Ding_TTG_material_regime_mapping_not_closed",
                "same_state_alpha_V_and_density_uncertainty_not_source_locked",
                "temperature_resolved_K_T_and_matched_Cp_Cv_not_available",
                "base_Phi_to_thermal_observable_map_and_independent_alpha_Phi_K_missing",
            ] if passed else ["Hanfland graphite K_T source checks failed"],
            "dependency_unlocked": "declared 300 K natural-graphite isothermal K_T source lane only; no same-grade Cp-to-Cv, alpha_Phi_K, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This is a source-traceable 300 K natural-graphite isothermal bulk-modulus input. It is not a Ding TTG material match, not a full Cp-to-Cv closure, not UET transport, and not an alpha_Phi_K calibration.",
        },
        "source": {
            **source,
            "local_hash_observed": actual_hash,
            "package_path": PACKAGE_PATH.relative_to(ROOT).as_posix(),
            "package_sha256": digest(PACKAGE_PATH),
        },
        "source_row": row,
        "thermodynamic_contract": contract,
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "same_grade_alpha_V_K_T_and_Ding_material_regime_mapping_missing",
        "next_controller": "Map the 300 K natural-graphite K_T to the Ding TTG material and source-lock same-state alpha_V, density, and Cp/Cv uncertainty before using the correction numerically.",
        "claim_boundary": "This closes only a source-traceable 300 K graphite K_T lane. It does not close same-grade Cp-to-Cv, C_src, e0, base Phi, alpha_Phi_K, transport, SK/KMS, entropy, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "raw_sha256": actual_hash,
        "K_T_GPa": row["K_T_GPa"],
        "K_T_uncertainty_GPa": row["K_T_uncertainty_GPa"],
        "controlling_blocker": result["controlling_blocker"],
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
