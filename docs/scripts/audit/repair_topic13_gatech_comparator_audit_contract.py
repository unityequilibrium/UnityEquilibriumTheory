"""Repair the standard comparator audit contract before rerunning it."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/scripts/audit/audit_topic13_gatech_standard_transport_comparator.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} not found")
    return text.replace(old, new, 1)


def main() -> int:
    text = AUDIT.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'template["uncertainty_contract"]["status"] == "CONDITIONAL_ENVELOPE_EXCLUDES_DENSITY_UNCERTAINTY"',
        'template["uncertainty_contract"]["status"] == "SOURCE_REPORTED_AND_FIRST_ORDER_PROPAGATED_ENVELOPES_SEPARATE"',
        "uncertainty status check",
    )
    text = replace_once(
        text,
        '{"path": "docs/core/07_artifacts/topic13/t13_gatech_standard_transport_comparator_audit.json", "sha256": sha256(OUT) if OUT.exists() else None},',
        '{"path": "docs/core/07_artifacts/topic13/t13_gatech_standard_transport_comparator_audit.json"},',
        "self-hash evidence entry",
    )
    AUDIT.write_text(text, encoding="utf-8")
    print("PATCHED_T13_GATECH_COMPARATOR_AUDIT_CONTRACT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
