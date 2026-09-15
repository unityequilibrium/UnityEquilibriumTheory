"""Wire the canonical Topic 13 holdout access audit into active verifiers."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one replacement in {path}, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def repair_full_gate() -> None:
    path = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
    replace_once(
        path,
        (
            '    calorine_candidate_path, calorine_candidate = load(\n'
            '        "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"\n'
            '    )\n'
        ),
        (
            '    calorine_candidate_path, calorine_candidate = load(\n'
            '        "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"\n'
            '    )\n'
            '    holdout_audit_path, holdout_audit = load(\n'
            '        "docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json"\n'
            '    )\n'
        ),
    )
    replace_once(
        path,
        '    holdout_not_consumed = bool(source_contract.get("holdout_consumed") is False)\n',
        (
            '    holdout_controls = holdout_audit.get("audit", {})\n'
            '    holdout_not_consumed = (\n'
            '        holdout_audit.get("status") == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY"\n'
            '        and holdout_controls.get("numeric_payload_consumed") is False\n'
            '        and holdout_controls.get("numeric_rows_consumed") is False\n'
            '        and holdout_controls.get("source_data_payload_observed") is False\n'
            '        and holdout_controls.get("audit_path_read_source_data") is False\n'
            '        and holdout_controls.get("used_for_fit") is False\n'
            '        and holdout_controls.get("used_for_tuning") is False\n'
            '        and holdout_controls.get("used_for_calibration") is False\n'
            '        and holdout_controls.get("used_for_threshold_adjustment") is False\n'
            '        and holdout_controls.get("locked_holdout_remains_unconsumed") is True\n'
            '    )\n'
        ),
    )
    replace_once(
        path,
        (
            '        "holdout_integrity": {\n'
            '            "status": "PASS" if holdout_not_consumed and source_fit_forbidden else "FAIL",\n'
            '            "holdout_consumed": not holdout_not_consumed,\n'
            '            "numeric_fitting_disabled": source_fit_forbidden,\n'
            '            "xie_2026_policy": source_contract.get("xie_2026_policy"),\n'
            '        },\n'
        ),
        (
            '        "holdout_integrity": {\n'
            '            "status": "PASS" if holdout_not_consumed and source_fit_forbidden else "BLOCKED",\n'
            '            "holdout_consumed": not holdout_not_consumed,\n'
            '            "numeric_fitting_disabled": source_fit_forbidden,\n'
            '            "metadata_only_observed": holdout_controls.get("metadata_only_observed"),\n'
            '            "numeric_payload_consumed": holdout_controls.get("numeric_payload_consumed"),\n'
            '            "source_data_payload_observed": holdout_controls.get("source_data_payload_observed"),\n'
            '            "used_for_fit": holdout_controls.get("used_for_fit"),\n'
            '            "used_for_tuning": holdout_controls.get("used_for_tuning"),\n'
            '            "used_for_calibration": holdout_controls.get("used_for_calibration"),\n'
            '            "used_for_threshold_adjustment": holdout_controls.get("used_for_threshold_adjustment"),\n'
            '            "canonical_access_audit": {"path": rel(holdout_audit_path), "sha256": sha256(holdout_audit_path)},\n'
            '            "xie_2026_policy": source_contract.get("xie_2026_policy"),\n'
            '            "controlling_blocker": None if holdout_not_consumed and source_fit_forbidden else "xie_2026_holdout_data_consumption_or_fit_audit_failed",\n'
            '        },\n'
        ),
    )
    replace_once(
        path,
        (
            '            evidence(rel(calorine_candidate_path), calorine_candidate, {\n'
            '                "status": calorine_candidate.get("status"),\n'
            '                "accepted_for_full_topic13": calorine_candidate.get("acceptance", {}).get("accepted_for_full_topic13"),\n'
            '                "controlling_blocker": calorine_candidate.get("controlling_blocker"),\n'
            '            }),\n'
        ),
        (
            '            evidence(rel(calorine_candidate_path), calorine_candidate, {\n'
            '                "status": calorine_candidate.get("status"),\n'
            '                "accepted_for_full_topic13": calorine_candidate.get("acceptance", {}).get("accepted_for_full_topic13"),\n'
            '                "controlling_blocker": calorine_candidate.get("controlling_blocker"),\n'
            '            }),\n'
            '            evidence(rel(holdout_audit_path), holdout_audit, {\n'
            '                "status": holdout_audit.get("status"),\n'
            '                "metadata_only_observed": holdout_controls.get("metadata_only_observed"),\n'
            '                "numeric_payload_consumed": holdout_controls.get("numeric_payload_consumed"),\n'
            '                "used_for_fit": holdout_controls.get("used_for_fit"),\n'
            '                "used_for_tuning": holdout_controls.get("used_for_tuning"),\n'
            '                "used_for_calibration": holdout_controls.get("used_for_calibration"),\n'
            '            }),\n'
        ),
    )


def repair_ding_mapping() -> None:
    path = ROOT / "docs/scripts/audit/audit_ding_2022_source_mapping.py"
    replace_once(
        path,
        'MAPPING = ROOT / "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json"\nOUT = ROOT / "docs/core/07_artifacts/provenance/ding_2022_source_mapping_audit.json"\n',
        'MAPPING = ROOT / "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json"\nHOLDOUT_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json"\nOUT = ROOT / "docs/core/07_artifacts/provenance/ding_2022_source_mapping_audit.json"\n',
    )
    replace_once(
        path,
        '    mapping = json.loads(MAPPING.read_text(encoding="utf-8-sig"))\n',
        '    mapping = json.loads(MAPPING.read_text(encoding="utf-8-sig"))\n    holdout_audit = json.loads(HOLDOUT_AUDIT.read_text(encoding="utf-8-sig"))\n    holdout_controls = holdout_audit.get("audit", {})\n',
    )
    replace_once(
        path,
        '        "holdout_not_accessed": "Xie 2026" in manifest.get("holdout_policy", ""),\n',
        (
            '        # Compatibility field: the canonical distinction between metadata\n'
            '        # observation and source-data consumption lives in the holdout audit.\n'
            '        "holdout_not_accessed": holdout_controls.get("numeric_payload_consumed") is False,\n'
            '        "holdout_metadata_only_observed": holdout_controls.get("metadata_only_observed") is True,\n'
            '        "holdout_source_data_consumed": holdout_controls.get("source_data_payload_observed") is True,\n'
            '        "holdout_source_data_unconsumed": holdout_controls.get("source_data_payload_observed") is False,\n'
            '        "holdout_audit_pass": holdout_audit.get("status") == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY",\n'
        ),
    )


def main() -> int:
    repair_full_gate()
    repair_ding_mapping()
    print("repaired Topic 13 canonical holdout access wiring")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
