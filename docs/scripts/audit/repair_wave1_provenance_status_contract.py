"""Repair Wave 1 provenance-status drift and use the canonical holdout audit."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if text.count(old) != 1:
        raise RuntimeError(f"unexpected replacement count in {path}: {text.count(old)}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def repair_integrity_audit() -> None:
    path = ROOT / "docs/scripts/audit/audit_uet_research_room_wave1_integrity.py"
    replace_once(
        path,
        'PROVENANCE = ROOT / "docs/core/07_artifacts/topic13/thermal_source_provenance_gate.json"\n',
        'PROVENANCE = ROOT / "docs/core/07_artifacts/topic13/thermal_source_provenance_gate.json"\nHOLDOUT_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json"\n',
    )
    replace_once(
        path,
        '    provenance = load(PROVENANCE)\n',
        '    provenance = load(PROVENANCE)\n    holdout_audit = load(HOLDOUT_AUDIT)\n    holdout_controls = holdout_audit.get("audit", {})\n',
    )
    replace_once(
        path,
        '        PROVENANCE,\n',
        '        PROVENANCE,\n        HOLDOUT_AUDIT,\n',
    )
    replace_once(
        path,
        '        "provenance_passes": provenance.get("status") == "PASS_WITH_PROVISIONAL_DIGITIZATION",\n',
        '        "provenance_passes": provenance.get("status") in {"PASS_WITH_PROVISIONAL_DIGITIZATION", "PASS_WITH_FIGURE_DERIVED_NORMALIZED_COMPARISON"} and provenance.get("metrics", {}).get("provenance_complete") is True,\n',
    )
    replace_once(
        path,
        '        "holdout_not_consumed": branch["source_contract"]["holdout_consumed"] is False and holdout.get("local_numeric_path") is None,\n',
        '        "holdout_not_consumed": holdout_controls.get("numeric_payload_consumed") is False and holdout_controls.get("numeric_rows_consumed") is False and holdout_controls.get("used_for_fit") is False and holdout_controls.get("used_for_tuning") is False and holdout_controls.get("used_for_calibration") is False and holdout_controls.get("used_for_threshold_adjustment") is False and holdout_controls.get("locked_holdout_remains_unconsumed") is True,\n',
    )


def repair_test() -> None:
    path = ROOT / "docs/core/test/test_uet_research_room_wave1.py"
    replace_once(
        path,
        '    assert provenance["status"] == "PASS_WITH_PROVISIONAL_DIGITIZATION"\n',
        '    assert provenance["status"] in {"PASS_WITH_PROVISIONAL_DIGITIZATION", "PASS_WITH_FIGURE_DERIVED_NORMALIZED_COMPARISON"}\n    assert provenance["metrics"]["provenance_complete"] is True\n',
    )


def main() -> int:
    repair_integrity_audit()
    repair_test()
    print("repaired Wave 1 provenance status and canonical holdout contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
