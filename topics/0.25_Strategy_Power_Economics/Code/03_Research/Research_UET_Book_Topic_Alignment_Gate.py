"""Verify Book 1, Section, and Topic 0.25 version/ontology alignment."""

from __future__ import annotations

from pathlib import Path

from economic_hardening_common import (
    ARTIFACT_DIR,
    CLAIM_MATRIX,
    FORMULA_GATE,
    RESEARCH_REGISTER,
    ROOT,
    WARN_GATE_REGISTRY,
    load_json,
    relative,
    sha256,
    utc_now,
    write_json,
)

SECTION = ROOT / "uet_history/3_publish/books/economics_ai_energy"
BOOK = SECTION / "01_economics"
ARTIFACT = ARTIFACT_DIR / "0_25_book_topic_alignment_gate.json"
AGGREGATE = ARTIFACT_DIR / "0_25_uet_economics_verification.json"
BLUEPRINT_VERSION = "book1-economics-v2-research-reset"
SECTION_VERSION = "economics-ai-energy-v2-research-reset"
REQUIRED_SECTION_FILES = [
    SECTION / "SECTION_MANIFEST.json",
    SECTION / "SECTION_RESEARCH_DESIGN.md",
    SECTION / "SECTION_LITERATURE_REVIEW.md",
    SECTION / "SECTION_CLAIM_MAP.md",
    SECTION / "VOLUME_MATRIX.md",
    SECTION / "DEPENDENCY_MAP.md",
    SECTION / "SHARED_TERMS.md",
]
REQUIRED_BOOK_FILES = [
    BOOK / "BOOK_MANIFEST.json",
    BOOK / "book_1_blueprint.md",
    BOOK / "RESEARCH_SPECIFICATION.md",
    BOOK / "REFERENCE_REGISTER.md",
    BOOK / "SOURCE_DIGEST.md",
    BOOK / "CLAIM_MAP.md",
    BOOK / "VERIFICATION_SPEC.md",
    BOOK / "UPDATE_LOG.md",
]


def file_record(path: Path) -> dict:
    return {
        "path": relative(path),
        "exists": path.exists(),
        "sha256": sha256(path) if path.exists() else None,
    }


def main() -> int:
    section_manifest = load_json(SECTION / "SECTION_MANIFEST.json")
    book_manifest = load_json(BOOK / "BOOK_MANIFEST.json")
    formula = load_json(FORMULA_GATE)
    claims = load_json(CLAIM_MATRIX)
    register = load_json(RESEARCH_REGISTER)
    warn = load_json(WARN_GATE_REGISTRY)
    required = [file_record(path) for path in [*REQUIRED_SECTION_FILES, *REQUIRED_BOOK_FILES]]
    formula_rows = {row.get("formula_id"): row for row in formula.get("formulae", [])}
    heuristic = formula_rows.get("BOOK-HEURISTIC-001", {})
    checks = {
        "all_required_control_files_exist": all(row["exists"] for row in required),
        "section_version_matches": section_manifest.get("blueprint_version") == SECTION_VERSION,
        "book_section_version_matches": book_manifest.get("section_blueprint_version") == SECTION_VERSION,
        "book_blueprint_version_matches": book_manifest.get("blueprint_version") == BLUEPRINT_VERSION,
        "topic_register_version_matches": register.get("book_blueprint_version") == BLUEPRINT_VERSION,
        "topic_claim_matrix_version_matches": claims.get("book_blueprint_version") == BLUEPRINT_VERSION,
        "topic_formula_registry_version_matches": formula.get("book_blueprint_version") == BLUEPRINT_VERSION,
        "topic_warn_registry_version_matches": warn.get("book_blueprint_version") == BLUEPRINT_VERSION,
        "retired_identity_is_explicit": heuristic.get("status") == "RETIRED_AS_IDENTITY" and heuristic.get("unit_closure_status") == "FAIL",
        "twenty_warn_gates_declared": warn.get("gate_count") == 20 and len(warn.get("gates", [])) == 20,
        "claim_wording_contract_present": bool(claims.get("claims")) and all(row.get("allowed_wording") and row.get("blocked_wording") for row in claims.get("claims", [])),
    }
    previous = load_json(AGGREGATE)
    previous_coverage = "CURRENT" if previous.get("book_blueprint_version") == BLUEPRINT_VERSION else "STALE_BLUEPRINT_COVERAGE"
    status = "PASS_WITH_BOUNDARY" if all(checks.values()) else "BLOCKED"
    blockers = [name for name, passed in checks.items() if not passed]
    artifact = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "generated_at_utc": utc_now(),
        "section_version": SECTION_VERSION,
        "book_blueprint_version": BLUEPRINT_VERSION,
        "book_blueprint": file_record(BOOK / "book_1_blueprint.md"),
        "research_specification": file_record(BOOK / "RESEARCH_SPECIFICATION.md"),
        "required_control_files": required,
        "checks": checks,
        "previous_aggregate": {
            "path": relative(AGGREGATE),
            "sha256": sha256(AGGREGATE) if AGGREGATE.exists() else None,
            "generated_at_utc": previous.get("generated_at_utc"),
            "book_blueprint_version": previous.get("book_blueprint_version"),
            "coverage_status": previous_coverage,
        },
        "blockers": blockers,
        "controlling_blocker": "SYSTEMATIC_LITERATURE_REVIEW_INCOMPLETE" if status == "PASS_WITH_BOUNDARY" else "HYPOTHESIS_ONTOLOGY_AND_VERSION_NOT_LOCKED",
        "literature_status": "IN_PROGRESS",
        "claim_boundary": "Version/ontology alignment does not validate any economic claim; S03/W03 literature review remains open.",
    }
    write_json(ARTIFACT, artifact)
    print(f"Book/Topic alignment gate: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
