"""Audit the source-locked graphite elastic bulk-modulus comparator.

The Bosak et al. IXS paper reports the room-temperature elastic tensor and a
bulk-modulus row for single-crystal graphite.  This audit inverts the normal
hexagonal stiffness block and reproduces the reported B value.  It deliberately
does not relabel the elastic/dynamic comparator as isothermal K_T, Ding C_src,
or a UET calibration.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "bosak_2007_graphite_elastic_bulk_source_package.json"
)
RAW_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "bosak_2007_graphite_elasticity.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_graphite_elastic_bulk_modulus_source_audit.json"
EXPECTED_RAW_SHA256 = "5db6247c3dbf48dcbed70d749da96ca61816fe6fed480f32d80a947ead649d7d"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inverse_normal_hexagonal(values_GPa: dict[str, float]) -> dict[str, float]:
    """Return normal-block compliances in Pa^-1 from hexagonal C_ij in GPa."""

    c11 = float(values_GPa["C11"]) * 1.0e9
    c12 = float(values_GPa["C12"]) * 1.0e9
    c13 = float(values_GPa["C13"]) * 1.0e9
    c33 = float(values_GPa["C33"]) * 1.0e9
    x = c33 * (c11 + c12) - 2.0 * c13**2
    if c11 <= c12 or c33 <= 0.0 or x <= 0.0:
        raise ValueError("hexagonal normal stiffness block is not positive in the declared domain")
    return {
        "S11_Pa^-1": (c11 * c33 - c13**2) / ((c11 - c12) * x),
        "S12_Pa^-1": (c13**2 - c12 * c33) / ((c11 - c12) * x),
        "S13_Pa^-1": -c13 / x,
        "S33_Pa^-1": (c11 + c12) / x,
    }


def elastic_bulk_modulus_Pa(compliance: dict[str, float]) -> float:
    """Return the hydrostatic bulk modulus from the normal compliance block."""

    hydrostatic_compliance = (
        2.0 * compliance["S11_Pa^-1"]
        + 2.0 * compliance["S12_Pa^-1"]
        + 4.0 * compliance["S13_Pa^-1"]
        + compliance["S33_Pa^-1"]
    )
    if hydrostatic_compliance <= 0.0:
        raise ValueError("hydrostatic compliance must be positive")
    return 1.0 / hydrostatic_compliance


def main() -> int:
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8-sig"))
    source = package["source"]
    tensor = package["elastic_tensor"]
    reported = package["reported_bulk_modulus"]
    actual_hash = digest(RAW_PATH) if RAW_PATH.is_file() else None
    compliance = inverse_normal_hexagonal(tensor["values_GPa"])
    reconstructed_Pa = elastic_bulk_modulus_Pa(compliance)
    reconstructed_GPa = reconstructed_Pa / 1.0e9
    source_B_GPa = float(reported["value_GPa"])
    relative_difference = (reconstructed_GPa - source_B_GPa) / source_B_GPa

    checks = {
        "source_pdf_present": RAW_PATH.is_file(),
        "source_pdf_hash_matches": actual_hash == EXPECTED_RAW_SHA256,
        "package_source_identity_present": bool(source.get("doi") and source.get("source_locators")),
        "material_and_temperature_declared": bool(source.get("material") and tensor.get("temperature_K")),
        "all_tensor_values_finite": all(
            value == value and abs(float(value)) < float("inf")
            for value in tensor["values_GPa"].values()
        ),
        "reported_uncertainty_present": all(
            float(value) > 0.0 for value in tensor["reported_uncertainty_GPa"].values()
        ),
        "normal_block_positive": True,
        "compliance_formula_explicit": package["major_result"]["equation_or_mapping"]
        == "S=C_normal^-1; B_elastic=1/(2*S11+2*S12+4*S13+S33)",
        "reconstruction_finite": reconstructed_GPa > 0.0,
        "reconstruction_matches_reported_B": abs(relative_difference) <= 0.01,
        "reported_bulk_uncertainty_present": float(reported["uncertainty_GPa"]) > 0.0,
        "dynamic_elastic_not_relabelled_as_K_T": package["isothermal_boundary"][
            "dynamic_elastic_value_is_K_T"
        ] is False,
        "K_T_not_emitted": package["isothermal_boundary"]["K_T_emitted"] is False,
        "same_state_Cp_Cv_not_claimed": package["isothermal_boundary"][
            "same_state_Cp_Cv_available"
        ] is False,
        "Ding_material_mapping_not_claimed": package["isothermal_boundary"][
            "material_regime_mapping_to_Ding"
        ] is False,
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "target_fit_not_performed": package["holdout_policy"]["target_curve_used"] is False,
        "alpha_Phi_K_fit_not_performed": package["holdout_policy"]["alpha_fit_used"] is False,
    }
    passed = all(checks.values())
    result = {
        "schema_version": "t13-graphite-elastic-bulk-modulus-source-audit-v1",
        "artifact": "t13_graphite_elastic_bulk_modulus_source_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_GRAPHITE_ELASTIC_BULK_COMPARATOR" if passed else "FAIL_GRAPHITE_ELASTIC_BULK_AUDIT",
        "major_result": {
            "major_result_id": "T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the Bosak et al. primary PDF is archived with a reproducible local hash",
                "the room-temperature single-crystal graphite elastic tensor and reported B row are source-locked",
                "the normal hexagonal compliance inversion and hydrostatic bulk formula reproduce the reported B within rounding",
                "the dynamic/elastic versus isothermal K_T boundary is explicit",
            ],
            "equation_or_mapping": {
                "compliance": "S=C_normal^-1",
                "hydrostatic_bulk_modulus": "B_elastic=1/(2*S11+2*S12+4*S13+S33)",
                "not_used": "K_T is not assigned from B_elastic; same-state Cp/Cv and measurement-mode identification are required",
            },
            "units": {
                "temperature": "K",
                "stiffness": "GPa",
                "compliance": "Pa^-1",
                "bulk_modulus": "Pa = J m^-3",
            },
            "derivation_class": "source transcription plus unit-aware tensor inversion; no UET derivation",
            "observable": "room-temperature single-crystal graphite elastic bulk-modulus comparator",
            "data_role": "INTERNAL_SOURCE_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": PACKAGE_PATH.relative_to(ROOT).as_posix(), "sha256": digest(PACKAGE_PATH)},
                {"path": RAW_PATH.relative_to(ROOT).as_posix(), "sha256": actual_hash},
            ],
            "verification_status": "PASS_SCOPED_GRAPHITE_ELASTIC_BULK_COMPARATOR" if passed else "FAIL_GRAPHITE_ELASTIC_BULK_AUDIT",
            "open_blockers": [
                "dynamic_or_elastic_bulk_modulus_is_not_an_isothermal_K_T_record",
                "same_state_Cp_Cv_and_thermal_conversion_not_source_locked",
                "single_crystal_kish_graphite_to_Ding_TTG_material_regime_mapping_not_closed",
                "base_Phi_to_thermal_observable_map_and_independent_alpha_Phi_K_missing",
            ] if passed else ["graphite elastic bulk source checks failed"],
            "dependency_unlocked": "source-locked graphite elastic bulk comparator only; no K_T, c_v, alpha_Phi_K, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This is a source-traceable elastic bulk-modulus comparator. It is not an isothermal K_T calibration, not a Ding/HOPG material match, not UET transport, and not an alpha_Phi_K calibration.",
        },
        "source": {
            **source,
            "local_hash_observed": actual_hash,
            "package_path": PACKAGE_PATH.relative_to(ROOT).as_posix(),
            "package_sha256": digest(PACKAGE_PATH),
        },
        "elastic_tensor": tensor,
        "reported_bulk_modulus": reported,
        "reconstruction": {
            "compliance_Pa^-1": compliance,
            "reconstructed_B_elastic_GPa": reconstructed_GPa,
            "reported_B_elastic_GPa": source_B_GPa,
            "reported_B_uncertainty_GPa": float(reported["uncertainty_GPa"]),
            "relative_difference": relative_difference,
            "agreement_interpretation": "central-value agreement within source rounding; reported B uncertainty is retained rather than independently re-propagated",
        },
        "isothermal_boundary": package["isothermal_boundary"],
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "isothermal_K_T_material_regime_and_dynamic_to_thermal_conversion_missing",
        "next_controller": "Source-lock a same-state isothermal K_T or a permitted thermal conversion with Cp/Cv and map it to the Ding TTG material; do not use the elastic B row as alpha_Phi_K.",
        "claim_boundary": "This closes only a source-traceable graphite elastic bulk comparator. It does not close K_T, c_v, C_src, e0, base Phi, alpha_Phi_K, transport, SK/KMS, entropy, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "raw_sha256": actual_hash,
        "reconstructed_B_elastic_GPa": reconstructed_GPa,
        "reported_B_elastic_GPa": source_B_GPa,
        "relative_difference": relative_difference,
        "controlling_blocker": result["controlling_blocker"],
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
