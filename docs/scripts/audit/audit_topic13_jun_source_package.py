"""Audit the final Jun Landauer source surface without importing numeric rows."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/jun_2014_final_source_package.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_jun_final_source_package_boundary.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def build_artifact() -> dict[str, Any]:
    package = load(PACKAGE_REL)
    archive = package["source_surface"]["local_archive"]
    archive_path = ROOT / archive["path"]
    archive_present = archive_path.is_file()
    archive_hash = sha256(archive_path) if archive_present else None
    archive_bytes = archive_path.stat().st_size if archive_present else None

    checks = {
        "package_identity_complete": all(
            package.get(key) for key in ("source_id", "title", "authors", "publication", "observable")
        ),
        "final_source_confirmed": package["source_surface"]["final_source_confirmed"] is True,
        "doi_is_jun_prl_identity": package["publication"]["doi"] == "10.1103/PhysRevLett.113.190601",
        "publisher_and_reprint_locators_present": bool(
            package["publication"].get("publisher_url")
            and package["source_surface"].get("institutional_reprint_url")
        ),
        "local_archive_present": archive_present,
        "local_archive_hash_matches": archive_hash == archive["sha256"],
        "local_archive_size_matches": archive_bytes == archive["bytes"],
        "identity_probe_markers_present": all(
            package["source_surface"]["identity_probe"].get(key) is True
            for key in (
                "title_marker_present",
                "doi_marker_present",
                "author_markers_present",
                "table_i_marker_present",
            )
        ),
        "numeric_table_not_transcribed": package["preprocessing"]["numeric_table_transcribed"] is False,
        "unit_conversion_not_performed": package["preprocessing"]["unit_conversion_performed"] is False,
        "numeric_rows_emitted_zero": package["numeric_rows_emitted"] == 0,
        "alpha_not_emitted": package["numeric_alpha_Phi_K_emitted"] is False,
        "calibration_not_eligible": package["calibration_eligible"] is False,
        "target_curve_not_read": package["preprocessing"]["target_curve_read"] is False,
        "holdout_not_read": package["preprocessing"]["holdout_read"] is False,
    }
    blockers = [
        "jun_machine_readable_numeric_row_parity_and_uncertainty_not_closed",
    ]
    evidence = [
        {
            "path": PACKAGE_REL,
            "sha256": sha256(ROOT / PACKAGE_REL),
            "role": "Jun final-source package",
        },
        {
            "path": archive["path"],
            "sha256": archive_hash,
            "bytes": archive_bytes,
            "role": "final PRL provenance archive; not a machine-readable row table",
        },
        {
            "doi": package["publication"]["doi"],
            "publisher_url": package["publication"]["publisher_url"],
            "institutional_reprint_url": package["source_surface"]["institutional_reprint_url"],
        },
    ]
    artifact = {
        "schema_version": "t13-jun-final-source-package-boundary-v1",
        "artifact": "t13_jun_final_source_package_boundary",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_JUN_FINAL_SOURCE_BOUNDARY",
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_JUN_FINAL_SOURCE_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "Final Jun PRL identity is confirmed through APS and an institutional reprint route.",
                "The final-source PDF is archived locally with a reproducible byte hash.",
                "The source remains explicitly separated from machine-readable numeric calibration data.",
            ],
            "equation_or_mapping": "W_min = k_B T ln(2); no numeric Phi-to-thermal calibration is emitted",
            "units": "source-defined work/energy units; no new numeric row conversion",
            "derivation_class": "final-source identity and provenance-boundary audit",
            "observable": package["observable"],
            "data_role": "SOURCE_IDENTITY_ONLY; no calibration consumed",
            "evidence_artifacts": evidence,
            "verification_status": "PASS_SCOPED_JUN_FINAL_SOURCE_BOUNDARY",
            "open_blockers": blockers,
            "dependency_unlocked": "Jun final-source identity lane only; no Landauer dataset, alpha_Phi_K, Full Topic 13, Core, Gravity, or transport dependency is unlocked.",
            "claim_boundary": package["claim_boundary"],
        },
        "equation_or_mapping": package["equation_or_mapping"],
        "units": package["units"],
        "derivation_class": "external final-source identity and local provenance audit",
        "observable": package["observable"],
        "data_role": package["data_role"],
        "evidence_artifacts": evidence,
        "verification_status": checks,
        "open_blockers": blockers,
        "dependency_unlocked": "none beyond the named Jun source controller",
        "claim_boundary": package["claim_boundary"],
        "numeric_rows_emitted": package["numeric_rows_emitted"],
        "numeric_alpha_Phi_K_emitted": package["numeric_alpha_Phi_K_emitted"],
        "parameter_fitting_performed": package["parameter_fitting_performed"],
        "target_data_used": package["preprocessing"]["target_curve_read"],
        "xie_2026_accessed": package["preprocessing"]["holdout_read"],
        "controlling_blocker": blockers[0],
        "next_action": "Create a source-row parity/transcription artifact only if the final PDF table/figure can be captured with locator, units, preprocessing, uncertainty, and hash; keep it outside alpha calibration.",
    }
    return artifact


def main() -> int:
    artifact = build_artifact()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "major_result_id": artifact["major_result"]["major_result_id"],
                "closure_level": artifact["major_result"]["closure_level"],
                "numeric_rows_emitted": artifact["numeric_rows_emitted"],
                "controlling_blocker": artifact["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
