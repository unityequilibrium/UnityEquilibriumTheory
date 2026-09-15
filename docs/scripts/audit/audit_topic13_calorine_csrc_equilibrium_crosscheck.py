"""Audit an equilibrium heat-capacity cross-check for the Calorine C_src lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RUN_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "t13_calorine_zenodo_pbte_run_m884_summary.json"
)
IAEA_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "iaea_graphite_handbook_constant_volume_source_package.json"
)
OUT_REL = "docs/core/07_artifacts/topic13/t13_calorine_csrc_equilibrium_crosscheck_audit.json"


def load(relative: str) -> tuple[Path, dict[str, Any]]:
    path = ROOT / relative
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return path, value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_temperature_row(rows: list[dict[str, Any]], temperature: float) -> dict[str, Any]:
    for row in rows:
        if float(row.get("temperature_K")) == temperature:
            return row
    raise KeyError(f"temperature row not found: {temperature} K")


def main() -> int:
    run_path, run = load(RUN_REL)
    iaea_path, iaea = load(IAEA_REL)

    temperature_K = 300.0
    run_row = find_temperature_row(run["c_src_rows"], temperature_K)
    c_src = float(run_row["C_src_J_m^-3_K^-1"])
    volume_A3 = float(run["geometry"]["primitive_volume_A3"])
    atom_count = int(run["geometry"]["primitive_atoms"])
    cv_mass = float(iaea["derived_comparator"]["cv_mass_J_per_kg_K"])
    iaea_temperature = float(iaea["source_row"]["temperature_K"])

    # The density is a derived property of the public primitive-cell model,
    # not a source measurement and not a Ding specimen substitution.
    carbon_standard_atomic_weight_kg_per_mol = 12.011e-3
    avogadro_per_mol = 6.02214076e23
    density_kg_per_m3 = (
        atom_count * carbon_standard_atomic_weight_kg_per_mol
        / (avogadro_per_mol * volume_A3 * 1.0e-30)
    )
    implied_cv_mass = c_src / density_kg_per_m3
    relative_difference = (implied_cv_mass - cv_mass) / cv_mass

    checks = {
        "run_summary_present": run_path.is_file(),
        "iaea_source_package_present": iaea_path.is_file(),
        "temperature_rows_match": temperature_K == iaea_temperature,
        "c_src_unit_is_volumetric_si": run["unit_contract"]["output"] == "J m^-3 K^-1",
        "iaea_cv_unit_is_mass_si": iaea["derived_comparator"]["cv_mass_J_per_kg_K"] > 0.0,
        "primitive_volume_positive": volume_A3 > 0.0,
        "derived_density_positive": density_kg_per_m3 > 0.0,
        "equilibrium_crosscheck_computed": c_src > 0.0 and implied_cv_mass > 0.0,
        "iaea_standard_uncertainty_not_promoted": (
            iaea["derived_comparator"]["cv_standard_uncertainty_J_per_kg_K"]
            is None
        ),
        "target_curve_used": bool(run["run"]["target_curve_used"]),
        "fit_performed": bool(run["run"]["fit_performed"]),
        "alpha_phi_k_fit_performed": bool(run["run"]["alpha_Phi_K_fit_performed"]),
        "holdout_accessed": bool(run["run"]["holdout_accessed"]),
    }
    required_true = {
        key: value
        for key, value in checks.items()
        if key not in {"target_curve_used", "fit_performed", "alpha_phi_k_fit_performed", "holdout_accessed"}
    }
    status = (
        "PASS_SCOPED_CALORINE_C_SRC_EQUILIBRIUM_CROSSCHECK"
        if all(required_true.values())
        and not checks["target_curve_used"]
        and not checks["fit_performed"]
        and not checks["alpha_phi_k_fit_performed"]
        and not checks["holdout_accessed"]
        else "FAIL_CALORINE_C_SRC_EQUILIBRIUM_CROSSCHECK"
    )

    evidence_artifacts = [
        {
            "path": RUN_REL,
            "sha256": sha256(run_path),
            "role": "derived Calorine C_src run summary",
        },
        {
            "path": IAEA_REL,
            "sha256": sha256(iaea_path),
            "role": "independent equilibrium c_v comparator",
        },
    ]
    artifact = {
        "schema_version": "t13-calorine-csrc-equilibrium-crosscheck-v1",
        "artifact": "t13_calorine_csrc_equilibrium_crosscheck_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_CALORINE_C_SRC_EQUILIBRIUM_CROSSCHECK",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the 300 K Calorine C_src row is re-read with its declared volumetric SI unit",
                "the primitive-cell volume is used to derive the candidate model density explicitly",
                "the implied mass-specific heat capacity is compared with an independent 300 K c_v comparator without fitting",
                "the comparator is retained as equilibrium/unit evidence and not promoted to Ding material equivalence",
            ],
            "ontology": {
                "C": "collective system-behaviour coordinate; not the source heat capacity",
                "Phi": "effective response variable; not used by this cross-check",
                "R_gen": "derived history trace; not used by this cross-check",
                "R_obs": "observer record kept separate; no observer data consumed",
            },
            "equation_or_mapping": {
                "model_density": "rho_model = N_C*M_C/(N_A*V_primitive)",
                "implied_mass_cv": "c_v,implied = C_src/rho_model",
                "comparison": "r = (c_v,implied - c_v,IAEA)/c_v,IAEA",
                "result_role": "equilibrium/unit cross-check only; no Phi-to-temperature map",
            },
            "units": {
                "C_src": "J m^-3 K^-1",
                "primitive_volume": "A^3",
                "derived_density": "kg m^-3",
                "implied_c_v": "J kg^-1 K^-1",
            },
            "derivation_class": "derived numerical consistency audit; no UET derivation and no calibration",
            "observable": "equilibrium volumetric heat-capacity scale of the independent candidate lane",
            "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",
            "evidence_artifacts": evidence_artifacts,
            "verification_status": status,
            "open_blockers": [
                "calorine_route_material_regime_mapping_to_ding_missing",
                "calorine_route_source_grade_uncertainty_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "independent_alpha_Phi_K_calibration_missing",
            ],
            "dependency_unlocked": "equilibrium and unit cross-check only; no Ding C_src, alpha, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This result supports only a scoped consistency check for the Calorine candidate. It is not Ding C_src, not an accepted same-regime reproduction, not a Phi calibration, and not external validation of UET.",
        },
        "source": {
            "run_id": run["run_id"],
            "temperature_K": temperature_K,
            "C_src_J_m^-3_K^-1": c_src,
            "primitive_volume_A3": volume_A3,
            "primitive_atoms": atom_count,
            "carbon_standard_atomic_weight_kg_per_mol": carbon_standard_atomic_weight_kg_per_mol,
            "avogadro_per_mol": avogadro_per_mol,
            "iaea_source_id": iaea["source"]["source_id"],
            "iaea_cv_mass_J_per_kg_K": cv_mass,
            "iaea_uncertainty_status": iaea["source_row"]["source_uncertainty_boundary"]["status"],
        },
        "observations": {
            "derived_density_kg_per_m3": density_kg_per_m3,
            "implied_cv_mass_J_per_kg_K": implied_cv_mass,
            "relative_difference_to_iaea_cv": relative_difference,
            "relative_difference_percent": 100.0 * relative_difference,
            "interpretation": "magnitude consistency is recorded; the IAEA manufactured-graphite comparator has no standard uncertainty and is not a Ding equivalence proof",
        },
        "checks": checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "controlling_blocker": "calorine_route_material_regime_mapping_to_ding_and_source_grade_uncertainty_missing",
        "next_action": "Use this cross-check as supporting evidence only; obtain an authorized Ding numeric package or complete a same-regime PBTE reproduction with source-grade uncertainty before changing C_src acceptance.",
        "claim_promotion": False,
    }
    out_path = ROOT / OUT_REL
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT_REL,
                "relative_difference_percent": 100.0 * relative_difference,
                "holdout_accessed": False,
                "claim_promotion": False,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
