"""Audit existing Topic 13 packages for an admissible independent alpha anchor.

This audit is deliberately a search and eligibility audit.  It does not read
the Xie holdout, fit a target curve, derive a scale from a normalized trace, or
emit a numeric alpha_Phi_K.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
OUTPUT = ROOT / "docs/core/artifacts/t13_alpha_phi_k_calibration_candidate_audit.json"

REQUIRED_FIELDS = (
    "source_identity",
    "locator",
    "matched_material_state_geometry",
    "base_Phi_amplitude",
    "SI_energy_or_response_amplitude",
    "units",
    "uncertainty",
    "preprocessing",
    "row_identity",
    "source_hash",
    "independence_statement",
)

FIELD_ALIASES = {
    "source_identity": ("source_identity",),
    "locator": ("locator", "source_locator"),
    "matched_material_state_geometry": (
        "matched_material_state_geometry",
        "material_state_geometry",
        "material_state_match",
    ),
    "base_Phi_amplitude": ("base_Phi_amplitude", "Phi_base", "base_Phi"),
    "SI_energy_or_response_amplitude": (
        "SI_energy_or_response_amplitude",
        "energy_density",
        "Delta_u",
        "Delta_u_ph",
        "Delta_Tq",
    ),
    "units": ("units",),
    "uncertainty": ("uncertainty", "sigma", "uncertainty_95pct"),
    "preprocessing": ("preprocessing",),
    "row_identity": ("row_identity", "source_row_id"),
    "source_hash": ("source_hash", "sha256", "sha256_hash"),
    "independence_statement": ("independence_statement",),
}

HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
EMPTY_TEXT = {"", "none", "null", "missing", "not available", "not reported", "open"}
UNCERTAINTY_REJECTS = {"not reported", "not available", "missing", "open", "none"}

CANDIDATES = (
    ("ding_2022_pbte_energy_temperature_source_package.json", "PBTE formula and conditional Phi_E bridge"),
    ("ding_2022_fig1d_digitized_manifest.json", "permitted figure-derived normalized TTG comparison"),
    ("matter_space_second_sound_source_package.json", "TTG source intake and normalized comparison"),
    ("graphite_heat_capacity_source_package.json", "heat-capacity source identity and candidate rows"),
    ("gatech_gen3csp_graphite_source_package.json", "independent c_p row with uncertainty"),
    ("mp48_independent_graphite_cv_source_package.json", "independent harmonic c_v comparator"),
    ("oxford_tgs_figure1_source_package.json", "Oxford TGS provenance comparator"),
    ("thermal_closure_derivation_audit.json", "formal thermal bridge derivation contract"),
    ("thermal_closure_source_inventory.json", "thermal source inventory and policy"),
    ("calorine_legacy_nep2_pbte_reproduction_source_package.json", "Calorine C-CX legacy NEP2 PBTE candidate reproduction"),
    ("landauer_source_lock.json", "imported Landauer constraint"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def collect_keys(value: Any, keys: set[str] | None = None) -> set[str]:
    keys = set() if keys is None else keys
    if isinstance(value, dict):
        keys.update(str(key) for key in value)
        for child in value.values():
            collect_keys(child, keys)
    elif isinstance(value, list):
        for child in value:
            collect_keys(child, keys)
    return keys


def collect_text(value: Any, text: list[str] | None = None) -> list[str]:
    text = [] if text is None else text
    if isinstance(value, dict):
        for key, child in value.items():
            text.append(str(key))
            collect_text(child, text)
    elif isinstance(value, list):
        for child in value:
            collect_text(child, text)
    elif isinstance(value, (str, int, float, bool)):
        text.append(str(value))
    return text


def mapping_records(value: Any) -> list[dict[str, Any]]:
    """Return every mapping so eligibility is evaluated within one record."""
    records: list[dict[str, Any]] = []
    if isinstance(value, dict):
        records.append(value)
        for child in value.values():
            records.extend(mapping_records(child))
    elif isinstance(value, list):
        for child in value:
            records.extend(mapping_records(child))
    return records


def field_value(record: dict[str, Any], field: str) -> Any:
    for alias in FIELD_ALIASES[field]:
        if alias in record:
            return record[alias]
    return None


def has_text(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in EMPTY_TEXT
    if isinstance(value, (dict, list)):
        return bool(value)
    return value is not None


def contains_finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    if isinstance(value, dict):
        return any(contains_finite_number(child) for child in value.values())
    if isinstance(value, list):
        return any(contains_finite_number(child) for child in value)
    return False


def has_usable_uncertainty(value: Any) -> bool:
    if not has_text(value):
        return False
    if isinstance(value, str) and value.strip().lower() in UNCERTAINTY_REJECTS:
        return False
    return contains_finite_number(value)


def has_valid_source_hash(value: Any) -> bool:
    return isinstance(value, str) and bool(HASH_RE.fullmatch(value.strip()))


def has_independence_statement(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    text = value.lower()
    return any(
        marker in text
        for marker in ("independent", "separate", "not target", "not holdout", "preregister")
    )


def semantic_record_checks(record: dict[str, Any]) -> dict[str, bool]:
    """Validate values, not just field names, inside one candidate record."""
    checks = {
        "source_identity": has_text(field_value(record, "source_identity")),
        "locator": has_text(field_value(record, "locator")),
        "matched_material_state_geometry": has_text(
            field_value(record, "matched_material_state_geometry")
        ),
        "base_Phi_amplitude_numeric": contains_finite_number(
            field_value(record, "base_Phi_amplitude")
        ),
        "SI_energy_or_response_amplitude_numeric": contains_finite_number(
            field_value(record, "SI_energy_or_response_amplitude")
        ),
        "units": has_text(field_value(record, "units")),
        "uncertainty_numeric": has_usable_uncertainty(field_value(record, "uncertainty")),
        "preprocessing": has_text(field_value(record, "preprocessing")),
        "row_identity": has_text(field_value(record, "row_identity")),
        "source_hash": has_valid_source_hash(field_value(record, "source_hash")),
        "independence_statement": has_independence_statement(
            field_value(record, "independence_statement")
        ),
    }
    return checks


def exact_field_presence(keys: set[str]) -> dict[str, bool]:
    aliases = {
        "base_Phi_amplitude": {"base_Phi_amplitude", "Phi_base", "base_Phi"},
        "SI_energy_or_response_amplitude": {
            "SI_energy_or_response_amplitude",
            "energy_density",
            "Delta_u",
            "Delta_u_ph",
            "Delta_Tq",
        },
        "uncertainty": {"uncertainty", "sigma", "uncertainty_95pct"},
    }
    result = {}
    for field in REQUIRED_FIELDS:
        result[field] = field in keys
    for field, candidates in aliases.items():
        result[field] = bool(keys.intersection(candidates))
    return result


def inspect_candidate(filename: str, description: str) -> dict[str, Any]:
    path = DATA_DIR / filename
    if not path.exists():
        return {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "description": description,
            "present": False,
            "eligible_paired_record": False,
            "controlling_blocker": "candidate_package_missing",
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    keys = collect_keys(payload)
    fields = exact_field_presence(keys)
    text = " ".join(collect_text(payload)).lower()
    holdout_mentions = "xie 2026" in text or "xie_2026" in text
    target_mentions = "target residual" in text or "target_data" in text
    semantic_records = [
        semantic_record_checks(record)
        for record in mapping_records(payload)
    ]
    semantic_eligible = any(
        all(record_checks.values()) for record_checks in semantic_records
    )
    has_all_required = all(fields.values())
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "description": description,
        "present": True,
        "sha256": sha256(path),
        "data_role": payload.get("data_role", payload.get("role")),
        "status": payload.get("status"),
        "required_field_presence": fields,
        "eligible_paired_record": semantic_eligible,
        "key_presence_eligible_paired_record": has_all_required,
        "semantic_candidate_record_count": len(semantic_records),
        "semantic_eligible_record_count": sum(
            all(record_checks.values()) for record_checks in semantic_records
        ),
        "holdout_read_by_audit": False,
        "holdout_policy_mentioned_in_package": holdout_mentions,
        "target_fit_input_detected_by_audit": False,
        "target_fit_language_present_in_package": target_mentions,
        "controlling_blocker": (
            None
            if semantic_eligible
            else "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing"
        ),
    }


def main() -> None:
    candidates = [inspect_candidate(filename, description) for filename, description in CANDIDATES]
    eligible = [item for item in candidates if item.get("eligible_paired_record")]
    artifact = {
        "schema_version": "t13-alpha-phi-k-calibration-candidate-audit-v1",
        "artifact": "t13_alpha_phi_k_calibration_candidate_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_NO_ELIGIBLE_PAIRED_ALPHA_RECORD" if not eligible else "REVIEW_ELIGIBLE_CANDIDATE_RECORD",
        "major_result": {
            "major_result_id": "T13_ALPHA_PHI_K_PAIRED_RECORD_SEARCH",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "the current Topic 13 calibration and source-package inventory was searched",
                "each candidate is evaluated against the declared paired-record acceptance fields",
                "normalized TTG, c_p/c_v, Landauer, and conditional Phi_E packages are not silently promoted to base-Phi calibration",
            ],
            "equation_or_mapping": {
                "normalized": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
                "dimensional": "Delta_Tq = alpha_Phi_K * Delta_Phi",
                "required_anchor": "Phi_E = s_material * Phi_base; alpha_Phi_K = (e0/c_v) * s_material",
            },
            "units": {
                "base_Phi": "dimensionless normalized coordinate",
                "SI_energy_or_response": "J m^-3 or source-defined thermal observable",
                "alpha_Phi_K": "K per normalized base Phi",
            },
            "derivation_class": "provenance and eligibility audit; no numeric calibration",
            "observable": "paired base-Phi amplitude and SI energy/thermal response in one declared material state",
            "data_role": "CALIBRATION_SEARCH_NOT_EVIDENCE",
            "evidence_artifacts": [
                {"path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/")},
                {"path": "docs/core/artifacts/t13_base_phi_independent_calibration_requirement.json"},
                {"path": "docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json"},
                {"path": "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json"},
            ],
            "verification_status": "PASS_SCOPED_NO_ELIGIBLE_PAIRED_ALPHA_RECORD" if not eligible else "REVIEW_ELIGIBLE_CANDIDATE_RECORD",
            "open_blockers": [
                "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
                "base_Phi_to_Phi_E_mapping_not_derived",
                "e0_and_c_v_source_package_with_uncertainty_not_locked_for_base_calibration",
            ] if not eligible else [],
            "dependency_unlocked": "none; full Topic 13 and downstream Core/Gravity gates remain blocked",
            "claim_boundary": "This closes the current candidate-search lane only. It emits no alpha_Phi_K, no prediction, no fit, and no external validation.",
        },
        "acceptance_contract": {
            "required_fields": list(REQUIRED_FIELDS),
            "forbidden_inputs": [
                "Xie 2026 locked holdout",
                "TTG target residuals",
                "post-inspection tuning",
                "synthetic replacement data",
                "Landauer k_B T ln(2) as a UET alpha derivation",
            ],
        },
        "candidate_count": len(candidates),
        "eligible_candidate_count": len(eligible),
        "candidates": candidates,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing" if not eligible else "candidate_record_requires_manual_review",
        "next_controller": "Obtain a permitted paired base-Phi/SI record or derive a coefficient-provenance-backed action-to-SI map; then rerun this audit before any alpha calibration.",
        "claim_boundary": "No current package supplies the independent base-Phi amplitude and SI observable pair required for alpha_Phi_K. Natural-unit action defaults and normalized TTG shapes are not calibration anchors.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["status"],
        "candidate_count": artifact["candidate_count"],
        "eligible_candidate_count": artifact["eligible_candidate_count"],
        "holdout_accessed": artifact["holdout_accessed"],
        "numeric_alpha_Phi_K_emitted": artifact["numeric_alpha_Phi_K_emitted"],
        "controlling_blocker": artifact["controlling_blocker"],
    }, indent=2))


if __name__ == "__main__":
    main()
