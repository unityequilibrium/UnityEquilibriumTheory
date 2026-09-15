"""Audit the Ding 2022 PBTE energy-density-to-temperature source mapping."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_energy_temperature_source_package.json"
)
PDF = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "ding_2022_supplementary_information.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_pbte_energy_temperature_mapping_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    value.update(path.read_bytes())
    return value.hexdigest()


def sha256(path: Path) -> str:
    return digest(path, "sha256")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def by_id(records: list[dict], formula_id: str) -> dict:
    return next(item for item in records if item["formula_id"] == formula_id)


def main() -> int:
    package = load(PACKAGE)
    source = package["source"]
    formulas = package["formula_records"]
    ontology = package["ontology_contract"]
    mapping = package["mapping_contract"]
    units = package["units_contract"]
    numeric = package["numeric_input_contract"]
    holdout = package["holdout_policy"]
    s4 = by_id(formulas, "DING_2022_S4_ENERGY_TEMPERATURE_RESPONSE")
    s10 = by_id(formulas, "DING_2022_S10_TTG_OBSERVABLE")

    checks = {
        "raw_pdf_present": PDF.is_file(),
        "raw_pdf_size_matches": PDF.is_file() and PDF.stat().st_size == source["local_raw_bytes"],
        "raw_pdf_sha256_matches": PDF.is_file()
        and sha256(PDF) == source["local_raw_sha256"],
        "raw_pdf_md5_matches_official_metadata": PDF.is_file()
        and digest(PDF, "md5")
        == source["local_raw_md5"]
        == source["official_metadata_md5"],
        "source_identity_locked": source["doi"] == "10.1038/s41467-021-27907-z"
        and source["pmcid"] == "PMC8755757",
        "license_declared": "CC BY 4.0" in source["license_or_terms"],
        "formula_locators_declared": len(source["source_locator"]) >= 4,
        "s4_energy_temperature_formula_locked": s4["canonical_notation"]
        == "Delta_u_ph_tilde := sum_mu(g_mu_tilde); Delta_T_tilde = Delta_u_ph_tilde / C_src",
        "s10_ttg_observable_locked": "peak-to-null" in s10["canonical_notation"],
        "unit_closure_is_kelvin": units["Delta_u_ph"] == "J m^-3"
        and units["C_src"] == "J m^-3 K^-1"
        and units["Delta_Tq"] == "K"
        and units["unit_closure"] == "PASS_FORMULA_ONLY",
        "source_C_is_not_uet_C": ontology["C_src_is_uet_C"] is False
        and ontology["uet_C"].startswith("collective system-behaviour"),
        "base_phi_identity_not_asserted": mapping["base_Phi_identity"] == "NOT_ASSERTED",
        "base_phi_energy_map_remains_open": mapping["base_Phi_to_Delta_u_ph"]
        == "OPEN_DERIVATION_OR_INDEPENDENT_CALIBRATION",
        "numeric_C_not_fabricated": numeric["numeric_C_src_value"] is None
        and numeric["numeric_C_src_uncertainty"] is None,
        "numeric_alpha_not_emitted": numeric["numeric_alpha_Phi_K"] is None
        and numeric["numeric_alpha_Phi_E_K"] is None,
        "gatech_material_not_silently_pooled": package["regime_contract"][
            "gatech_same_material_or_specimen"
        ]
        is False,
        "landauer_not_used": package["regime_contract"]["landauer_used"] is False,
        "ding_curve_not_consumed": holdout[
            "ding_2022_digitized_curve_consumed_by_this_mapping"
        ]
        is False,
        "xie_holdout_not_accessed": holdout["xie_2026_accessed"] is False,
        "xie_holdout_not_consumed": holdout["xie_2026_source_data_consumed"] is False,
        "calibration_path_excludes_holdout": holdout[
            "calibration_path_may_read_holdout"
        ]
        is False,
    }
    status = (
        "PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN"
        if all(checks.values())
        else "FAIL_DING_PBTE_SOURCE_MAPPING"
    )
    open_blockers = [
        "ding_pbte_numeric_C_src_T_not_packaged",
        "ding_pbte_mode_resolved_c_mu_or_reproducible_inputs_missing",
        "ding_pbte_C_src_uncertainty_or_convergence_contract_missing",
        "ding_pbte_C_src_to_thermodynamic_c_v_regime_not_closed",
        "base_Phi_to_Delta_u_ph_mapping_not_derived",
        "e0_energy_density_scale_not_source_locked",
        "independent_alpha_Phi_K_calibration_missing",
    ]
    equation = {
        "source_energy_density": "Delta_u_ph = sum_mu(g_mu)",
        "source_temperature_response": "Delta_Tq = Delta_u_ph / C_src",
        "named_energy_response": "Phi_E = Delta_u_ph/e0",
        "conditional_named_bridge": "Delta_Tq = (e0/C_src) * Phi_E",
        "conditional_alpha": "alpha_Phi_E_K = e0/C_src",
    }
    report = {
        "schema_version": "t13-ding-pbte-energy-temperature-mapping-audit-v1",
        "artifact": "t13_ding_pbte_energy_temperature_mapping_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_DING_PBTE_ENERGY_TEMPERATURE_MAPPING",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "The Ding 2022 source formula maps mode-summed deviational phonon energy density to the source temperature response through C_src.",
                "The Ding TTG observable is source-located as a peak-to-null temperature-response difference before normalization.",
                "C_src is explicitly separated from the UET collective coordinate C, and the source mapping is separated from base Phi.",
            ],
            "equation_or_mapping": equation,
            "units": {
                "g_mu": "J m^-3",
                "Delta_u_ph": "J m^-3",
                "C_src": "J m^-3 K^-1",
                "Delta_Tq": "K",
                "Phi_E": "dimensionless",
                "alpha_Phi_E_K": "K per normalized Phi_E",
            },
            "derivation_class": "source-backed standard linearized PBTE mapping plus conditional UET named-branch correspondence",
            "observable": "Ding TTG peak-to-null temperature-response difference and its normalized trace",
            "data_role": "DERIVED_STANDARD_PHYSICS_MAPPING; no numeric calibration or holdout data consumed",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(PACKAGE), "sha256": sha256(PACKAGE)},
                {
                    "path": rel(PDF),
                    "sha256": sha256(PDF),
                    "md5": digest(PDF, "md5"),
                    "bytes": PDF.stat().st_size,
                },
            ],
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "The standard Ding energy-density-to-temperature formula lane and a non-circular route for acquiring C_src(T) are available; no base-Phi or downstream Core dependency is unlocked.",
            "claim_boundary": "CLOSED_FOR_LANE applies to the source formula, units, ontology separation, and TTG observable locator only. It is not a numeric heat-capacity calibration, a base-Phi mapping, external validation, or Topic 13 closure.",
        },
        "source_formula_witness": {
            "locator_S4": s4["locator"],
            "locator_S10": s10["locator"],
            "equation_or_mapping": equation,
            "unit_quotient": "(J m^-3)/(J m^-3 K^-1) = K",
            "source_C_symbol_policy": "renamed C_src in the UET package to prevent collision with UET C",
        },
        "source_integrity": {
            "package": {"path": rel(PACKAGE), "sha256": sha256(PACKAGE)},
            "raw_pdf": {
                "path": rel(PDF),
                "sha256": sha256(PDF),
                "md5": digest(PDF, "md5"),
                "bytes": PDF.stat().st_size,
            },
            "official_supplement_url": source["official_supplement_url"],
        },
        "checks": checks,
        "what_changed": "The direct Ding PBTE energy-density-to-temperature formula route is now source-locked, unit-closed, and separated from UET ontology and numeric calibration.",
        "verification": "The official PDF byte identity, DOI/PMC identity, formula locators, unit quotient, ontology separation, material non-pooling, and holdout non-access are checked.",
        "controlling_blocker": "ding_pbte_numeric_C_src_and_uet_energy_anchor_missing",
        "next_action": "Package or reproducibly regenerate Ding-compatible C_src(T)=sum_mu(c_mu) with unit-cell volume and convergence/uncertainty, then derive e0 and base Phi-to-Delta_u_ph independently of TTG residuals and Xie 2026.",
        "claim_boundary": "This closes a standard-physics source mapping only; Full Topic 13 remains blocked and global claim promotion remains false.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": status,
                "artifact": rel(OUT),
                "controlling_blocker": report["controlling_blocker"],
                "checks_passed": sum(checks.values()),
                "checks_total": len(checks),
            },
            indent=2,
        )
    )
    return 0 if status == "PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
