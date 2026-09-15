"""Audit the Peterson legacy-label identity conflict without admitting a row."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/peterson_source_identity_no_go_package.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_peterson_source_identity_no_go.json"


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
    candidates = package["identity_checks"]
    checks = {
        "package_identity_complete": all(package.get(key) for key in ("source_id", "question", "observable")),
        "three_candidate_checks_present": len(candidates) == 3,
        "legacy_doi_mismatch_recorded": candidates[0]["identity_matches_local_peterson_quantum_landauer_label"] is False,
        "peterson_doi_mismatch_recorded": candidates[1]["identity_matches_local_peterson_quantum_landauer_label"] is False,
        "single_atom_doi_mismatch_recorded": candidates[2]["identity_matches_local_peterson_quantum_landauer_label"] is False,
        "numeric_table_not_transcribed": package["preprocessing"]["numeric_table_transcribed"] is False,
        "legacy_row_not_selected": package["preprocessing"]["legacy_row_selected"] is False,
        "numeric_rows_emitted_zero": package["numeric_rows_emitted"] == 0,
        "alpha_not_emitted": package["numeric_alpha_Phi_K_emitted"] is False,
        "target_curve_not_read": package["preprocessing"]["target_curve_read"] is False,
        "holdout_not_read": package["preprocessing"]["holdout_read"] is False,
    }
    blockers = [
        "peterson_legacy_label_demoted_no_admissible_row_until_exact_source_selected",
    ]
    evidence = [
        {
            "path": PACKAGE_REL,
            "sha256": sha256(ROOT / PACKAGE_REL),
            "role": "Peterson identity-conflict package",
        },
        {
            "locator": candidates[0]["resolved_publisher_url"],
            "doi": candidates[0]["candidate"],
            "role": "DOI identity mismatch evidence",
        },
        {
            "locator": candidates[1]["resolved_publisher_url"],
            "doi": candidates[1]["resolved_doi"],
            "role": "actual Peterson paper identity candidate; not selected as a row",
        },
        {
            "locator": candidates[2]["resolved_publisher_url"],
            "doi": candidates[2]["resolved_doi"],
            "role": "separate single-atom identity; not selected as Peterson row",
        },
    ]
    artifact = {
        "schema_version": "t13-peterson-source-identity-no-go-v1",
        "artifact": "t13_peterson_source_identity_no_go",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_PETERSON_SOURCE_IDENTITY_NO_GO",
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_PETERSON_SOURCE_IDENTITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "The local Peterson 2018/Ca-40/DOI label is rejected as a single admissible source identity.",
                "The conflicting DOI, actual Peterson experiment, and separate single-atom experiment are recorded as distinct candidates.",
                "No numeric row is admitted from the conflicted label.",
            ],
            "equation_or_mapping": package["equation_or_mapping"],
            "units": package["units"],
            "derivation_class": "source-identity conflict audit and scoped no-go",
            "observable": package["observable"],
            "data_role": package["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": "PASS_SCOPED_PETERSON_SOURCE_IDENTITY_NO_GO",
            "open_blockers": blockers,
            "dependency_unlocked": "Peterson legacy-label demotion only; no replacement row, Landauer dataset, alpha_Phi_K, Full Topic 13, Core, Gravity, or transport dependency is unlocked.",
            "claim_boundary": package["claim_boundary"],
        },
        "equation_or_mapping": package["equation_or_mapping"],
        "units": package["units"],
        "derivation_class": "external source identity conflict and scoped no-go audit",
        "observable": package["observable"],
        "data_role": package["data_role"],
        "evidence_artifacts": evidence,
        "verification_status": checks,
        "open_blockers": blockers,
        "dependency_unlocked": "none beyond legacy-label demotion",
        "claim_boundary": package["claim_boundary"],
        "numeric_rows_emitted": package["numeric_rows_emitted"],
        "numeric_alpha_Phi_K_emitted": package["numeric_alpha_Phi_K_emitted"],
        "parameter_fitting_performed": package["parameter_fitting_performed"],
        "target_data_used": package["preprocessing"]["target_curve_read"],
        "xie_2026_accessed": package["preprocessing"]["holdout_read"],
        "controlling_blocker": blockers[0],
        "next_action": "Remove or quarantine the legacy Peterson row, or create a separate preregistered source package for exactly one selected paper before any numeric capture.",
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
