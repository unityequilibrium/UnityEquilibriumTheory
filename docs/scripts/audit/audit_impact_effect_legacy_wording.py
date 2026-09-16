"""Inventory legacy wording that can conflate C, I, mass, vacuum, and carriers."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/07_artifacts/verification/impact_effect_legacy_wording_audit.json"
TEXT_SUFFIXES = {".md", ".py", ".txt"}
EXCLUDED_PARTS = {".git", "__pycache__", "Result", "_Logs", "artifacts"}
PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("information_field", re.compile(r"information\s*(?:-|_)??field|I[- ]field|I\s+field", re.I), "legacy_or_ambiguous_information_field"),
    ("neutrino_pure_i_field", re.compile(r"neutrino\s*=.{0,80}pure\s+I(?:[- ]field|\s+field)?", re.I), "legacy_particle_identity"),
    ("c_mass_identity", re.compile(r"(?:\bC\b|`C`).{0,40}(?:=|is|means|คือ).{0,30}(?:mass|มวล|density|ความหนาแน่น)", re.I), "lane_mapping_required"),
    ("vacuum_empty", re.compile(r"(?:vacuum|สูญญากาศ).{0,50}(?:empty|ว่างเปล่า|ไม่มีอะไร)|(?:empty|ว่างเปล่า|ไม่มีอะไร).{0,50}(?:vacuum|สูญญากาศ)", re.I), "vacuum_wording_review"),
    ("trace_feedback", re.compile(r"R[_ ]?gen.{0,60}feedback|I[_ ]?trace.{0,60}feedback|feedback.{0,60}R[_ ]?gen", re.I), "explicit_feedback_boundary_review"),
)


CANONICAL_CONTRACT_PATHS = {
    "docs/core/AGENTS.md",
    "docs/core/01_contracts/COSMOLOGICAL_OPEN_SYSTEM_AND_CAUSAL_TRACE_SPEC.md",
    "docs/core/01_contracts/IMPACT_EFFECT_AND_INFORMATION_FLOW_SPEC.md",
    "docs/core/08_history/research_notes/MATTER_SPACE_RESEARCH_REPORT.md",
    "docs/core/01_contracts/RELATIONAL_TWO_BODY_BASELINE_SPEC.md",
    "docs/core/01_contracts/TRACE_RESEARCH_SPEC.md",
    "docs/core/08_history/research_notes/UET_FOUNDATION_COMPATIBILITY_AUDIT.md",
    "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md",
    "docs/core/08_history/research_notes/UET_INFORMATION_FIELD_THERMODYNAMIC_TRACE_AUDIT.md",
}


def wording_disposition(rel: str) -> tuple[str, str]:
    """Route an occurrence without changing the source wording."""
    normalized = rel.replace("\\", "/")
    lower = normalized.lower()
    if normalized in CANONICAL_CONTRACT_PATHS:
        return (
            "CANONICAL_CONTRACT_LITERAL",
            "canonical core contract; occurrence is retained as explicit boundary/legacy wording and is not a universal identity",
        )
    if (
        "legacy_reports/" in lower
        or "/legacy/" in lower
        or "/keed/" in lower
        or "/doc/03_legacy" in lower
        or "/code/03_legacy" in lower
        or "/code/03_legacy_opt" in lower
    ):
        return (
            "LEGACY_ARCHIVE_QUARANTINED",
            "legacy/archive path; retained for history and excluded from active claim promotion",
        )
    if normalized.endswith(".py"):
        return (
            "CODE_OR_TEST_LITERAL",
            "implementation/test/audit literal; source code requires separate semantic review before any prose claim",
        )
    return (
        "ACTIVE_PROSE_MANUAL_REVIEW",
        "active topic or documentation prose; no automatic rewrite or promotion is permitted",
    )


def is_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES and not any(part in EXCLUDED_PARTS for part in path.parts)


def scan() -> dict[str, Any]:
    occurrences: list[dict[str, Any]] = []
    files_scanned = 0
    for path in sorted((ROOT / "docs").rglob("*")):
        if not path.is_file() or not is_candidate(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        files_scanned += 1
        rel = path.relative_to(ROOT).as_posix()
        for line_number, line in enumerate(lines, start=1):
            for marker, pattern, reason in PATTERNS:
                if pattern.search(line):
                    disposition, disposition_basis = wording_disposition(rel)
                    occurrences.append(
                        {
                            "marker": marker,
                            "status": "LEGACY_REVIEW_REQUIRED",
                            "disposition": disposition,
                            "disposition_basis": disposition_basis,
                            "reason": reason,
                            "path": rel,
                            "line": line_number,
                            "snippet": line.strip()[:240],
                        }
                    )
    by_marker: dict[str, int] = {}
    by_path: dict[str, int] = {}
    for item in occurrences:
        by_marker[item["marker"]] = by_marker.get(item["marker"], 0) + 1
        by_path[item["path"]] = by_path.get(item["path"], 0) + 1
    by_disposition: dict[str, int] = {}
    for item in occurrences:
        disposition = item["disposition"]
        by_disposition[disposition] = by_disposition.get(disposition, 0) + 1
    return {
        "schema_version": "impact-effect-legacy-wording-audit-v2",
        "artifact": "impact_effect_legacy_wording_audit",
        "generated_at": date.today().isoformat(),
        "status": "SCOPED_DISPOSITIONS_WITH_ACTIVE_PROSE_OPEN" if occurrences else "NO_MARKERS_FOUND",
        "scope": {
            "root": "docs/",
            "files_scanned": files_scanned,
            "excluded_directory_names": sorted(EXCLUDED_PARTS),
            "rule": "inventory plus deterministic routing disposition; no legacy wording is rewritten or promoted automatically",
        },
        "summary": {
            "occurrence_count": len(occurrences),
            "by_marker": by_marker,
            "by_path": by_path,
            "by_disposition": by_disposition,
            "active_prose_open": by_disposition.get("ACTIVE_PROSE_MANUAL_REVIEW", 0),
        },
        "claim_boundary": "legacy/candidate wording is not evidence for a universal identity of C, I_trace, mass, vacuum, photon, neutrino, or positron",
        "occurrences": occurrences,
        "next_controller": "manually review ACTIVE_PROSE_MANUAL_REVIEW occurrences; canonical and archive routes are dispositioned but remain non-promotional",
    }


def main() -> int:
    artifact = scan()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"status={artifact['status']}")
    print(f"files_scanned={artifact['scope']['files_scanned']}")
    print(f"occurrences={artifact['summary']['occurrence_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
