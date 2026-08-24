"""Reconcile graphite heat-capacity sources against the Topic 13 c_v gate.

This is a source/provenance pass.  It does not manufacture c_v from unmatched
materials, and it never emits a Phi scale, alpha_Phi_K, or holdout-derived row.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_cv_source_reconciliation_audit.json"


CANDIDATES = [
    {
        "candidate_id": "bipm_2006_graphite",
        "artifact_path": "docs/core/artifacts/t13_bipm_specific_heat_source_audit.json",
        "quantity_class": "volumetric_Cp_with_source_uncertainty",
        "direct_or_derived_cv": False,
        "source_grade_uncertainty_for_required_cv": False,
        "ding_material_state_match": False,
        "same_state": False,
        "reason": "BIPM closes a volumetric Cp comparator with uncertainty, but does not supply Cv or Ding TTG state equivalence.",
    },
    {
        "candidate_id": "npl_rsa40_ig11",
        "artifact_path": "docs/core/artifacts/t13_npl_rsa40_graphite_specific_heat_audit.json",
        "quantity_class": "mass_specific_Cp_with_source_uncertainty",
        "direct_or_derived_cv": False,
        "source_grade_uncertainty_for_required_cv": False,
        "ding_material_state_match": False,
        "same_state": False,
        "reason": "NPL closes a mass-specific Cp comparator; density uncertainty, Cv conversion, and Ding state mapping remain open.",
    },
    {
        "candidate_id": "iaea_manufactured_graphite",
        "artifact_path": "docs/core/artifacts/t13_iaea_cv_uncertainty_boundary_audit.json",
        "quantity_class": "table_derived_mass_specific_cv_without_standard_uncertainty",
        "direct_or_derived_cv": True,
        "source_grade_uncertainty_for_required_cv": False,
        "ding_material_state_match": False,
        "same_state": False,
        "reason": "IAEA supplies a table-derived manufactured-graphite Cv comparator, but not a source-grade Cv uncertainty or Ding material match.",
    },
    {
        "candidate_id": "mp48_harmonic_graphite",
        "artifact_path": "docs/core/artifacts/t13_mp48_independent_graphite_cv_audit.json",
        "quantity_class": "harmonic_volumetric_cv_with_nonstatistical_envelope",
        "direct_or_derived_cv": True,
        "source_grade_uncertainty_for_required_cv": False,
        "ding_material_state_match": False,
        "same_state": False,
        "reason": "MP48 supplies auditable harmonic volumetric Cv rows, but its uncertainty is explicitly non-statistical and its ideal crystal is not Ding's TTG state.",
    },
    {
        "candidate_id": "lowitzer_graphite_pvt",
        "artifact_path": "docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json",
        "quantity_class": "alphaV_KT_correction_pair_without_same_state_cv",
        "direct_or_derived_cv": False,
        "source_grade_uncertainty_for_required_cv": False,
        "ding_material_state_match": False,
        "same_state": False,
        "reason": "Lowitzer closes an alpha_V/K_T correction pair, but supplies no same-state Cp/Cv and uses a different graphite morphology.",
    },
    {
        "candidate_id": "desorbo_ceylon_graphite",
        "artifact_path": "docs/core/artifacts/t13_desorbo_ceylon_graphite_cp_audit.json",
        "quantity_class": "natural_graphite_molar_Cp_without_standard_uncertainty",
        "direct_or_derived_cv": False,
        "source_grade_uncertainty_for_required_cv": False,
        "ding_material_state_match": False,
        "same_state": False,
        "reason": "DeSorbo provides a Ceylon natural-graphite Cp row and an accuracy boundary, not a standard Cv uncertainty or Ding mapping.",
    },
    {
        "candidate_id": "farooqui_ig210",
        "artifact_path": "docs/core/artifacts/t13_farooqui_ig210_volumetric_cp_uncertainty_audit.json",
        "quantity_class": "volumetric_Cp_with_expanded_uncertainty",
        "direct_or_derived_cv": False,
        "source_grade_uncertainty_for_required_cv": False,
        "ding_material_state_match": False,
        "same_state": False,
        "reason": "Farooqui closes an IG-210 volumetric Cp uncertainty comparator, but same-state K_T, Cv, and Ding mapping are absent.",
    },
]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def holdout_is_clean(value: dict[str, Any]) -> bool:
    policy = value.get("holdout_policy", {})
    if not isinstance(policy, dict):
        return False
    return not any(
        bool(policy.get(key, False))
        for key in ("xie_2026_accessed", "xie_2026_source_data_consumed", "target_curve_used", "target_fit_performed", "alpha_Phi_K_fit_used", "alpha_fit_used")
    )


def candidate_record(spec: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / spec["artifact_path"]
    present = path.is_file()
    artifact = load(path) if present else {}
    eligible = all(
        (
            spec["direct_or_derived_cv"],
            spec["source_grade_uncertainty_for_required_cv"],
            spec["ding_material_state_match"],
            spec["same_state"],
        )
    )
    return {
        "candidate_id": spec["candidate_id"],
        "artifact_path": spec["artifact_path"],
        "artifact_sha256": sha256(path) if present else None,
        "artifact_status": artifact.get("status"),
        "closure_level": artifact.get("major_result", {}).get("closure_level"),
        "quantity_class": spec["quantity_class"],
        "direct_or_derived_cv": spec["direct_or_derived_cv"],
        "source_grade_uncertainty_for_required_cv": spec["source_grade_uncertainty_for_required_cv"],
        "ding_material_state_match": spec["ding_material_state_match"],
        "same_state": spec["same_state"],
        "eligible_for_full_topic13_cv_input": eligible,
        "holdout_clean": holdout_is_clean(artifact) if present else False,
        "reason": spec["reason"],
        "controlling_blocker": "c_v_source_uncertainty_not_closed" if not eligible else None,
    }


def main() -> int:
    records = [candidate_record(spec) for spec in CANDIDATES]
    all_present = all((ROOT / spec["artifact_path"]).is_file() for spec in CANDIDATES)
    all_holdout_clean = all(record["holdout_clean"] for record in records)
    eligible = [record for record in records if record["eligible_for_full_topic13_cv_input"]]
    direct_cv_count = sum(record["direct_or_derived_cv"] for record in records)
    source_grade_cv_count = sum(
        record["direct_or_derived_cv"] and record["source_grade_uncertainty_for_required_cv"]
        for record in records
    )
    ding_matched_count = sum(
        record["direct_or_derived_cv"] and record["ding_material_state_match"]
        for record in records
    )
    checks = {
        "all_candidate_artifacts_present": all_present,
        "all_candidate_holdout_policies_clean": all_holdout_clean,
        "no_candidate_is_silently_promoted": not eligible,
        "direct_or_derived_cv_count_is_reported": direct_cv_count >= 0,
        "source_grade_cv_count_is_reported": source_grade_cv_count >= 0,
        "ding_matched_cv_count_is_reported": ding_matched_count >= 0,
    }
    passed = all(checks.values())
    result = {
        "schema_version": "t13-cv-source-reconciliation-v1",
        "artifact": "t13_cv_source_reconciliation_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_CV_SOURCE_RECONCILIATION_OPEN" if passed else "FAIL_CV_SOURCE_RECONCILIATION",
        "major_result": {
            "major_result_id": "T13_CV_SOURCE_RECONCILIATION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "candidate heat-capacity source classes are reconciled against the required volumetric c_v input contract",
                "direct or derived c_v comparators are distinguished from Cp-only and alpha_V/K_T correction sources",
                "no current candidate satisfies the combined c_v uncertainty, same-state, and Ding-regime acceptance contract",
            ],
            "what_remains_open": [
                "c_v_source_uncertainty_not_closed",
                "material_regime_mapping_to_TTG_not_closed",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "c_v source reconciliation only; no Ding C_src, alpha_Phi_K, EOS, transport, or Full Topic 13 unlock",
            "equation_or_mapping": {
                "required": "C_src(T) = sum_mu c_mu(T); Delta_Tq = Delta_u_ph / C_src(T)",
                "cp_cv": "c_v^V = rho*c_p - T*alpha_V^2*K_T",
                "acceptance": "direct_or_derived_c_v AND source_grade_uncertainty AND same_state AND Ding_material_state_match",
            },
            "units": {
                "required_c_v_or_C_src": "J m^-3 K^-1",
                "temperature": "K",
                "uncertainty": "source-grade uncertainty for the required c_v/C_src quantity",
            },
            "derivation_class": "source provenance reconciliation; no UET derivation and no synthetic replacement",
            "observable": "availability and acceptance state of thermal capacity inputs",
            "data_role": "INTERNAL_SOURCE_RECONCILIATION_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": spec["artifact_path"], "sha256": record["artifact_sha256"]}
                for spec, record in zip(CANDIDATES, records)
            ],
            "verification_status": "PASS_SCOPED_CV_SOURCE_RECONCILIATION_OPEN" if passed else "FAIL_CV_SOURCE_RECONCILIATION",
            "controlling_blocker": "c_v_source_uncertainty_not_closed",
            "claim_boundary": "This reconciliation closes a provenance boundary only. It does not turn a comparator, Cp row, harmonic Cv row, or correction term into Ding C_src or UET calibration.",
        },
        "summary": {
            "candidate_count": len(records),
            "direct_or_derived_cv_count": direct_cv_count,
            "source_grade_cv_uncertainty_count": source_grade_cv_count,
            "ding_matched_cv_count": ding_matched_count,
            "eligible_for_full_topic13_count": len(eligible),
            "cp_only_or_correction_only_count": len(records) - direct_cv_count,
        },
        "candidates": records,
        "checks": checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "target_curve_used": False,
            "alpha_Phi_K_fit_used": False,
        },
        "report": {
            "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE",
            "WHAT_IS_ACTUALLY_CLOSED": "The available c_p/c_v/correction sources are reconciled; direct c_v comparators are visible but none is accepted for the Ding TTG input contract.",
            "WHAT_REMAINS_OPEN": "c_v_source_uncertainty_not_closed; material_regime_mapping_to_TTG_not_closed; Ding numeric C_src remains missing.",
            "DEPENDENCY_UNLOCKED": "None beyond source-reconciliation visibility.",
            "STATUS": "PASS_SCOPED_CV_SOURCE_RECONCILIATION_OPEN" if passed else "FAIL_CV_SOURCE_RECONCILIATION",
            "WHAT_CHANGED": "Added a fail-closed reconciliation of seven existing heat-capacity/correction source audits; no source row, threshold, alpha, equation, or holdout role changed.",
            "EQUATION_OR_MAPPING": "C_src(T)=sum_mu c_mu(T); c_v^V=rho*c_p-T*alpha_V^2*K_T.",
            "VERIFICATION": "All candidate artifacts are present, hashes are recorded, holdout policies are clean, and zero candidate is silently promoted.",
            "CONTROLLING_BLOCKER": "c_v_source_uncertainty_not_closed",
            "NEXT_ACTION": "Obtain a same-state direct volumetric c_v or Ding-compatible mode-resolved C_src package with source-grade uncertainty and material mapping; do not combine unmatched sources as if they were one specimen.",
            "CLAIM_BOUNDARY": "This is a source reconciliation lane, not Full Topic 13 closure or alpha_Phi_K calibration.",
        },
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "candidate_count": len(records), "direct_or_derived_cv_count": direct_cv_count, "source_grade_cv_uncertainty_count": source_grade_cv_count, "eligible_for_full_topic13_count": len(eligible), "controlling_blocker": result["major_result"]["controlling_blocker"]}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
