"""Audit the standard Topic 13 ``c_p`` to ``c_v`` correction contract."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.thermal_cp_cv_correction import (  # noqa: E402
    CpCvCorrectionInputs,
    cp_cv_correction_contract,
    cp_minus_cv_mass_J_per_kg_K,
    cp_minus_cv_volumetric_J_per_m3_K,
    cv_mass_from_cp_J_per_kg_K,
    cv_volumetric_from_cp_J_per_m3_K,
    cv_volumetric_uncertainty_J_per_m3_K,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_cp_cv_correction_audit.json"
MODULE = ROOT / "docs/core/thermal_cp_cv_correction.py"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    # This witness is deliberately synthetic.  It exercises algebra and units
    # without supplying a material calibration for graphite or the TTG target.
    witness = CpCvCorrectionInputs(
        temperature_K=573.15,
        cp_mass_J_per_kg_K=1259.81694473522,
        density_kg_per_m3=1780.0,
        alpha_volume_per_K=2.0e-5,
        bulk_modulus_Pa=3.0e10,
        sigma_temperature_K=0.1,
        sigma_cp_mass_J_per_kg_K=69.8470681678102,
        sigma_density_kg_per_m3=20.0,
        sigma_alpha_volume_per_K=1.0e-6,
        sigma_bulk_modulus_Pa=1.0e9,
    )
    contract = cp_cv_correction_contract()
    correction_mass = cp_minus_cv_mass_J_per_kg_K(witness)
    correction_volume = cp_minus_cv_volumetric_J_per_m3_K(witness)
    cv_mass = cv_mass_from_cp_J_per_kg_K(witness)
    cv_volume = cv_volumetric_from_cp_J_per_m3_K(witness)
    sigma_cv_volume = cv_volumetric_uncertainty_J_per_m3_K(witness)

    checks = {
        "mass_formula_is_explicit": contract["formula_mass_specific"]
        == "c_p - c_v = T * alpha_V^2 * K_T / rho",
        "volumetric_formula_is_explicit": contract["formula_volumetric"]
        == "c_p^V - c_v^V = T * alpha_V^2 * K_T",
        "mass_and_volume_corrections_are_consistent": abs(
            correction_volume - witness.density_kg_per_m3 * correction_mass
        )
        <= 1.0e-9,
        "mass_cv_map_is_consistent": abs(
            cv_mass - cv_volume / witness.density_kg_per_m3
        )
        <= 1.0e-12,
        "volumetric_cv_is_positive": cv_volume > 0.0,
        "uncertainty_propagation_is_finite": sigma_cv_volume > 0.0,
        "cp_unit_is_mass_specific": contract["c_p_mass"] == "mass-specific constant-pressure heat capacity [J kg^-1 K^-1]",
        "cv_unit_is_volumetric": contract["c_v_volumetric"] == "constant-volume heat capacity density [J m^-3 K^-1]",
        "alpha_requires_volumetric_definition": contract["alpha_V"] == "volumetric thermal expansion coefficient [K^-1]",
        "bulk_modulus_is_isothermal": contract["K_T"] == "isothermal bulk modulus [Pa = J m^-3]",
        "uncertainty_policy_is_explicit": contract["uncertainty_method"]
        == "independent first-order propagation; no covariance supplied",
        "base_phi_identity_is_not_asserted": contract["base_Phi_identity"] == "not asserted",
        "r_gen_boundary_is_preserved": contract["R_gen_identity"]
        == "unchanged derived history trace; no new physical state",
    }

    artifact = {
        "schema_version": "t13-cp-cv-correction-audit-v1",
        "artifact": "t13_cp_cv_correction_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_FORMULA_UNIT_CONTRACT_OPEN_INPUTS" if all(checks.values()) else "FAIL",
        "major_result": {
            "major_result_id": "T13_CP_CV_CORRECTION_CONTRACT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": "The standard c_p-to-c_v correction, mass-to-volume conversion, unit contract, and first-order uncertainty propagation are explicit and tested; no material calibration is emitted.",
            "equation_or_mapping": {
                "mass_specific": contract["formula_mass_specific"],
                "volumetric": contract["formula_volumetric"],
                "volumetric_cp": contract["volumetric_cp_map"],
                "volumetric_cv": contract["volumetric_cv_map"],
                "uncertainty": "sigma_cvV from independent first-order input propagation; covariance is not supplied",
            },
            "units": {
                "T": "K",
                "alpha_V": "K^-1",
                "K_T": "Pa = J m^-3",
                "rho": "kg m^-3",
                "c_p_mass": "J kg^-1 K^-1",
                "c_v_volumetric": "J m^-3 K^-1",
            },
            "derivation_class": "standard thermodynamic identity with unit-checked implementation and first-order uncertainty propagation",
            "observable": "volumetric c_v input to the named Phi_E response branch",
            "data_role": "FORMULA_CONTRACT_ONLY; synthetic witness not calibration",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(MODULE), "sha256": sha256(MODULE)},
            ],
            "verification_status": "PASS_FORMULA_UNIT_CONTRACT_OPEN_INPUTS",
            "open_blockers": [
                "volumetric_alpha_V_not_source_locked",
                "isothermal_bulk_modulus_K_T_not_source_locked",
                "density_uncertainty_not_source_locked",
                "c_v_source_uncertainty_not_closed",
                "material_regime_mapping_to_TTG_not_closed",
            ],
            "dependency_unlocked": "c_p-to-c_v formula contract only; no volumetric c_v calibration or base Phi Kelvin prediction",
            "claim_boundary": "This closes the standard correction equation as a named formula lane. It does not provide graphite alpha_V, K_T, density uncertainty, c_v, e0, alpha_Phi_K, or any TTG prediction.",
        },
        "source_anchor": {
            "source_id": "nist_sp960_11_materials_properties",
            "source_url": "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication960-11.pdf",
            "locator": "Section 6.3.1.5, pp. 69-70, Eq. (21)",
            "role": "standard thermodynamic relation and units guidance",
            "numeric_graphite_inputs_consumed": False,
        },
        "contract": contract,
        "checks": checks,
        "witness": {
            "role": "synthetic algebra and unit witness only",
            "temperature_K": witness.temperature_K,
            "cp_mass_J_per_kg_K": witness.cp_mass_J_per_kg_K,
            "density_kg_per_m3": witness.density_kg_per_m3,
            "alpha_volume_per_K": witness.alpha_volume_per_K,
            "bulk_modulus_Pa": witness.bulk_modulus_Pa,
            "cp_minus_cv_mass_J_per_kg_K": correction_mass,
            "cp_minus_cv_volumetric_J_per_m3_K": correction_volume,
            "cv_mass_J_per_kg_K": cv_mass,
            "cv_volumetric_J_per_m3_K": cv_volume,
            "sigma_cv_volumetric_J_per_m3_K": sigma_cv_volume,
            "not_a_source_value": True,
        },
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "controlling_blocker": "alpha_V_K_T_density_uncertainty_and_material_regime_inputs_not_source_locked",
        "next_controller": "source-lock volumetric alpha_V, isothermal K_T, density uncertainty, and TTG material-regime correspondence before producing c_v",
        "claim_boundary": "Formula closure only; Topic 13 full bridge remains blocked and global claim promotion remains false.",
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "artifact": rel(OUT), "checks": len(checks)}, indent=2))
    return 0 if artifact["status"] == "PASS_FORMULA_UNIT_CONTRACT_OPEN_INPUTS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
