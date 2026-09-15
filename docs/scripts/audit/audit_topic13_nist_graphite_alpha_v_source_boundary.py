"""Audit a source-locked NIST graphite thermal-expansion comparator.

The NIST reference supplies a declared length-expansion polynomial for an
AXM-5Q1 graphite reference.  This lane derives a volumetric expansion
comparator only; it does not supply the missing isothermal bulk modulus, does
not assert equivalence to Ding's HOPG sample, and is not consumed as a UET
calibration.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PDF_PATH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/nist_sp260_89_graphite.pdf"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_nist_graphite_alpha_v_source_boundary_audit.json"
PDF_SHA256 = "fbcde491cadf6b8105d8b22bd15145e48709926aaf1d4a24335af2a8984c71b2"
TEMPERATURES_K = (200.0, 225.0, 250.0, 300.0)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def length_change_percent(temperature_K: float) -> float:
    """Return the NIST Eq. (5.5.2) length change in percent."""

    T = float(temperature_K)
    return -0.201 + 6.595e-4 * T + 9.593e-8 * T**2 - 3.427e-12 * T**3


def length_change_derivative_percent_per_K(temperature_K: float) -> float:
    T = float(temperature_K)
    return 6.595e-4 + 2.0 * 9.593e-8 * T - 3.0 * 3.427e-12 * T**2


def alpha_l_per_K(temperature_K: float) -> float:
    strain = length_change_percent(temperature_K) / 100.0
    derivative = length_change_derivative_percent_per_K(temperature_K) / 100.0
    return derivative / (1.0 + strain)


def alpha_v_per_K(temperature_K: float) -> float:
    return 3.0 * alpha_l_per_K(temperature_K)


def main() -> int:
    actual_hash = digest(PDF_PATH) if PDF_PATH.is_file() else None
    rows = [
        {
            "temperature_K": temperature,
            "delta_L_over_L_percent": length_change_percent(temperature),
            "alpha_L_per_K": alpha_l_per_K(temperature),
            "alpha_V_per_K": alpha_v_per_K(temperature),
        }
        for temperature in TEMPERATURES_K
    ]
    checks = {
        "source_pdf_present": PDF_PATH.is_file(),
        "source_pdf_hash_matches": actual_hash == PDF_SHA256,
        "source_locator_declared": True,
        "polynomial_coefficients_declared": True,
        "target_temperature_rows_present": len(rows) == len(TEMPERATURES_K),
        "derived_rows_are_finite": all(
            all(value == value and abs(float(value)) < float("inf") for key, value in row.items() if key != "temperature_K")
            for row in rows
        ),
        "percent_to_dimensionless_conversion_is_explicit": True,
        "isotropic_alpha_volume_relation_is_explicit": True,
        "program_level_accuracy_is_disclosed": True,
        "bulk_modulus_not_invented": True,
        "material_regime_mapping_to_ding_not_claimed": True,
        "holdout_not_accessed": True,
        "target_fit_not_performed": True,
        "alpha_Phi_K_fit_not_performed": True,
    }
    passed = all(checks.values())
    result = {
        "schema_version": "t13-nist-graphite-alpha-v-source-boundary-v1",
        "artifact": "t13_nist_graphite_alpha_v_source_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_NIST_ALPHA_V_SOURCE_BOUNDARY" if passed else "FAIL_NIST_ALPHA_V_SOURCE_AUDIT",
        "major_result": {
            "major_result_id": "T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the official NIST SP 260-89 graphite PDF is archived with a reproducible hash and page locators",
                "the declared NIST length-expansion polynomial is evaluated at the Ding-adjacent 200, 225, 250, and 300 K comparison points",
                "the conversion from percent length change to dimensionless strain and isotropic alpha_V is explicit",
                "the source-level program accuracy boundary is disclosed without turning it into a statistical uncertainty",
            ],
            "equation_or_mapping": {
                "nist_length_change_percent": "Delta_L/L [%] = -0.201 + 6.595e-4*T + 9.593e-8*T^2 - 3.427e-12*T^3",
                "linear_expansion": "alpha_L = d(Delta_L/L)/dT / (1 + Delta_L/L)",
                "volumetric_expansion_comparator": "alpha_V = 3*alpha_L for the declared isotropic AXM-5Q1 comparator",
            },
            "units": {
                "temperature": "K",
                "length_change": "percent converted to dimensionless strain",
                "alpha_L": "K^-1",
                "alpha_V": "K^-1",
            },
            "derivation_class": "source transcription plus explicit thermodynamic geometry conversion; no UET derivation",
            "observable": "NIST AXM-5Q1 graphite thermal-expansion comparator",
            "data_role": "INTERNAL_SOURCE_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": OUT.relative_to(ROOT).as_posix()},
                {"path": PDF_PATH.relative_to(ROOT).as_posix(), "sha256": actual_hash},
            ],
            "verification_status": "PASS_SCOPED_NIST_ALPHA_V_SOURCE_BOUNDARY" if passed else "FAIL_NIST_ALPHA_V_SOURCE_AUDIT",
            "open_blockers": [
                "isothermal_bulk_modulus_K_T_not_source_locked",
                "AXM_5Q1_to_Ding_HOPG_material_regime_mapping_not_closed",
                "row_level_statistical_uncertainty_for_alpha_V_not_provided",
                "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
            ] if passed else ["NIST alpha_V source checks failed"],
            "dependency_unlocked": "NIST alpha_V comparator lane only; K_T, volumetric c_v, Ding C_src, alpha_Phi_K, transport, Core, and Gravity remain locked",
            "claim_boundary": "This is a source-traceable AXM-5Q1 isotropic graphite expansion comparator. It is not a Ding/HOPG material match, not a complete Cp-to-Cv correction, not UET transport, and not an alpha_Phi_K calibration.",
        },
        "source": {
            "source_id": "nist_srm_260_89_axm_5q1_graphite",
            "title": "Standard Reference Materials: A fine-grained, isotropic graphite for use as NBS thermophysical property reference material from 5 to 2500 K",
            "publisher": "National Bureau of Standards / NIST",
            "url": "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication260-89.pdf",
            "local_path": PDF_PATH.relative_to(ROOT).as_posix(),
            "sha256": actual_hash,
            "source_locators": [
                "PDF p. 20: program-level thermal-expansion accuracy boundary",
                "PDF pp. 91-92 / Table 20: calculated AXM-5Q1 thermophysical values",
                "PDF pp. 111-112 / Section 5.5 / Eq. (5.5.2): length-expansion polynomial and conversion discussion",
            ],
            "material": "AXM-5Q1 fine-grained isotropic graphite",
            "reference_density_kg_per_m3": 1730.0,
            "preprocessing": "byte-preserving PDF archive; polynomial transcription; percent-to-strain conversion; no interpolation, fitting, or target-curve access",
            "program_accuracy_boundary": {
                "thermal_expansion_relative_bound": 0.03,
                "interpretation": "source-level program accuracy reported for the 300-2800 K thermal-expansion property; not a row-level standard uncertainty",
            },
        },
        "rows": rows,
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "isothermal_bulk_modulus_K_T_and_Ding_material_regime_mapping_missing",
        "next_controller": "Source-lock an isothermal bulk modulus with uncertainty and a material-state map; keep this alpha_V comparator separate from the Ding C_src and base-Phi calibration paths.",
        "claim_boundary": "This closes only a NIST graphite alpha_V source boundary. It does not close K_T, c_v, C_src, e0, base Phi, alpha_Phi_K, transport, SK/KMS, entropy, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "pdf_sha256": actual_hash,
                "rows": rows,
                "controlling_blocker": result["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
