"""Audit the page-level content boundary of the archived Ding supplementary PDFs."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_supplementary_content_review_package.json"
OUT = ROOT / "docs/core/artifacts/t13_ding_supplementary_content_review_audit.json"

EXPECTED_SOURCES = {
    "DING2022_MOESM1": {
        "path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_information.pdf",
        "page_count": 23,
        "size_bytes": 1893976,
        "sha256": "a50c1a6347775de72f705f4395507d3136cbf4e5cadfb6638caca2876c52b8f7",
    },
    "DING2022_MOESM2": {
        "path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_materials_2.pdf",
        "page_count": 25,
        "size_bytes": 4537623,
        "sha256": "2f7d1d057df83b8d3408f65c833dad7542fca8b24aeec087e304842fa5aca6e7",
    },
    "DING2022_MOESM3": {
        "path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_materials_3.pdf",
        "page_count": 2,
        "size_bytes": 927333,
        "sha256": "4405683b720a24437d64fe3429d409503fcc91bd33c1e8616a3252cc50d94c5f",
    },
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    package = load(PACKAGE_PATH)
    source_files = package.get("source_files", [])
    by_id = {row.get("source_id"): row for row in source_files}
    checks = {
        "package_schema_matches": package.get("schema_version") == "t13-ding-supplementary-content-review-package-v1",
        "source_set_matches_expected": set(by_id) == set(EXPECTED_SOURCES),
        "review_method_is_read_only": package["review_method"]["figures_digitized"] is False
        and package["review_method"]["machine_readable_rows_created"] is False
        and package["review_method"]["fit_or_parameter_tuning_performed"] is False,
        "equation_contract_present": package["equation_or_mapping"]["ding_mode_sum"] == "C_src(T) = sum_mu c_mu(T)"
        and package["equation_or_mapping"]["ding_temperature_response"] == "Delta_Tq = Delta_u_ph / C_src",
        "acceptance_is_not_promoted": all(value is False for value in package["acceptance"].values()),
        "holdout_and_fit_guards_pass": all(value is False for value in package["holdout_policy"].values()),
    }
    file_checks = {}
    for source_id, expected in EXPECTED_SOURCES.items():
        row = by_id.get(source_id, {})
        path = ROOT / expected["path"]
        exists = path.is_file()
        actual_size = path.stat().st_size if exists else None
        actual_hash = sha256(path) if exists else None
        file_checks[source_id] = {
            "exists": exists,
            "page_count_matches": row.get("page_count") == expected["page_count"],
            "size_matches": actual_size == expected["size_bytes"] and row.get("size_bytes") == expected["size_bytes"],
            "hash_matches": actual_hash == expected["sha256"] and row.get("sha256") == expected["sha256"],
            "findings_have_locators": bool(row.get("content_findings")) and all(item.get("locator") for item in row.get("content_findings", [])),
            "numeric_payload_absent": row.get("numeric_payload_present") is False
            and row.get("machine_readable_rows_present") is False
            and row.get("force_constants_present") is False
            and row.get("scattering_matrix_present") is False
            and row.get("mode_resolved_c_mu_present") is False
            and row.get("uncertainty_or_convergence_payload_present") is False
            and all(item.get("numeric_payload_present") is False for item in row.get("content_findings", [])),
        }
    checks["all_archived_files_match"] = all(all(values.values()) for values in file_checks.values())
    status = (
        "PASS_SCOPED_DING_SUPPLEMENTARY_CONTENT_BOUNDARY_NO_NUMERIC_PAYLOAD"
        if all(checks.values())
        else "FAIL_DING_SUPPLEMENTARY_CONTENT_REVIEW_AUDIT"
    )
    report = {
        "schema_version": "t13-ding-supplementary-content-review-audit-v1",
        "artifact": "t13_ding_supplementary_content_review_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_DING_SUPPLEMENTARY_CONTENT_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "the three archived Ding supplementary PDFs are reviewed at page-level locators with fixed file identity and hashes",
                "MOESM1 is bounded to symbolic PBTE/TTG equations and method context, not a numeric C_src table",
                "MOESM2 is bounded to review and computational clarification, not force constants or scattering payload",
                "MOESM3 is bounded to reporting summary material, not a paired numeric Phi/SI response record",
            ],
            "what_remains_open": [
                "numeric Ding C_src or an accepted same-regime independent reproduction",
                "source-grade uncertainty and convergence payload",
                "base Phi to SI energy/response mapping and independent alpha_Phi_K",
                "Full Topic 13 EOS, transport, SK/KMS, entropy, and dimensional closure",
            ],
            "dependency_unlocked": "page-level public supplementary content boundary only; no C_src, alpha, calibration, transport, Core, or Full Topic 13 dependency unlock",
            "equation_or_mapping": package["equation_or_mapping"],
            "units": package["units"],
            "derivation_class": "page-level source-content review and provenance boundary; no UET derivation",
            "observable": "Ding supplementary-content availability boundary",
            "data_role": "SOURCE_CONTENT_REVIEW_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_supplementary_content_review_package.json"},
                {"path": "docs/scripts/audit/audit_topic13_ding_supplementary_content_review.py"},
            ],
            "verification_status": status,
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "claim_boundary": package["claim_boundary"],
        },
        "source_identity": package["source_identity"],
        "source_files": source_files,
        "file_checks": file_checks,
        "checks": checks,
        "acceptance": package["acceptance"],
        "holdout_policy": package["holdout_policy"],
        "controlling_blocker": package["controlling_blocker"],
        "next_controller": package["next_controller"],
        "claim_boundary": package["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "failed_checks": [key for key, value in checks.items() if not value],
        "file_checks": file_checks,
    }, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
