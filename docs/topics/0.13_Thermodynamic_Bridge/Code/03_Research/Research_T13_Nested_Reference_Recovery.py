"""Trace historical He-4 composition references through relocated Core files."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
LINEAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_composition_reference_lineage.json"
RECORD = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_funding_nested_reference_recovery.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_value(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _changes(before: object, after: object, prefix: str = "") -> list[str]:
    if isinstance(before, dict) and isinstance(after, dict):
        result = []
        for key in sorted(before.keys() | after.keys()):
            pointer = f"{prefix}/{key}"
            if key not in before or key not in after:
                result.append(pointer)
            else:
                result.extend(_changes(before[key], after[key], pointer))
        return result
    if isinstance(before, list) and isinstance(after, list):
        result = []
        for index in range(max(len(before), len(after))):
            pointer = f"{prefix}/{index}"
            if index >= len(before) or index >= len(after):
                result.append(pointer)
            else:
                result.extend(_changes(before[index], after[index], pointer))
        return result
    return [] if before == after else [prefix]


def audit(source_root: Path) -> dict:
    lineage = json.loads(LINEAGE.read_text(encoding="utf-8"))
    rows = []
    for record in lineage["records"]:
        candidates = record["candidates"]
        if len(candidates) != 1:
            raise ValueError(f"Expected one relocated candidate: {record['recorded_path']}")
        candidate = candidates[0]["path"]
        source_file = source_root / candidate
        clean_file = ROOT / candidate
        if not source_file.is_file() or not clean_file.is_file():
            raise FileNotFoundError(candidate)
        source_json = json.loads(source_file.read_text(encoding="utf-8"))
        clean_json = json.loads(clean_file.read_text(encoding="utf-8"))
        source_hash = sha256(source_file)
        clean_hash = sha256(clean_file)
        rows.append({
            "recorded_path": record["recorded_path"],
            "recorded_path_missing_in_both_worktrees": not (source_root / record["recorded_path"]).exists()
            and not (ROOT / record["recorded_path"]).exists(),
            "relocated_path": candidate,
            "recorded_sha256": record["recorded_sha256"],
            "recorded_status": record["recorded_status"],
            "source_relocated_sha256": source_hash,
            "source_matches_recorded_hash": source_hash == record["recorded_sha256"],
            "clean_relocated_sha256": clean_hash,
            "source_vs_clean_state": "BYTE_IDENTICAL" if source_hash == clean_hash else
            "PARSED_JSON_IDENTICAL" if source_json == clean_json else "FIELD_DELTA",
            "source_status": source_json.get("status"),
            "clean_status": clean_json.get("status"),
            "source_status_matches_recorded": source_json.get("status") == record["recorded_status"],
            "clean_status_matches_recorded": clean_json.get("status") == record["recorded_status"],
            "field_delta_pointers": _changes(source_json, clean_json),
        })
    return {
        "schema_version": "t13-funding-nested-reference-recovery-v1",
        "major_result_id": "T13_FUNDING_NESTED_REFERENCE_RECOVERY",
        "topic": "0.13",
        "closure_level": "PARTIAL",
        "record_class": "NESTED_PROVENANCE_TRIAGE_NOT_CORE_REVALIDATION",
        "source_branch": git_value(source_root, "branch", "--show-current"),
        "source_head_at_observation": git_value(source_root, "rev-parse", "HEAD"),
        "clean_branch": git_value(ROOT, "branch", "--show-current"),
        "clean_head_at_observation": git_value(ROOT, "rev-parse", "HEAD"),
        "evidence_artifacts": [{"path": LINEAGE.relative_to(ROOT).as_posix(), "sha256": sha256(LINEAGE)}],
        "records": rows,
        "counts": {
            "recorded_path_missing_both": sum(row["recorded_path_missing_in_both_worktrees"] for row in rows),
            "source_matches_recorded_hash": sum(row["source_matches_recorded_hash"] for row in rows),
            "source_hash_drift": sum(not row["source_matches_recorded_hash"] for row in rows),
            "source_clean_byte_identical": sum(row["source_vs_clean_state"] == "BYTE_IDENTICAL" for row in rows),
            "source_clean_parsed_json_identical": sum(row["source_vs_clean_state"] == "PARSED_JSON_IDENTICAL" for row in rows),
            "source_clean_field_delta": sum(row["source_vs_clean_state"] == "FIELD_DELTA" for row in rows),
            "source_status_matches_recorded": sum(row["source_status_matches_recorded"] for row in rows),
            "clean_status_matches_recorded": sum(row["clean_status_matches_recorded"] for row in rows),
        },
        "controlling_blocker": "nested_core_reference_source_chain_not_revalidated",
        "dependency_unlocked": [],
        "g0_ready": False,
        "full_core_unlock": False,
        "claim_boundary": "Relocated byte matches or matching status do not validate nested sources or Core physics.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--verify-saved", action="store_true")
    args = parser.parse_args()
    result = audit(args.source_root)
    if args.verify_saved:
        saved = json.loads(RECORD.read_text(encoding="utf-8"))
        head_keys = {"source_head_at_observation", "clean_head_at_observation"}
        match = ({key: value for key, value in result.items() if key not in head_keys}
                 == {key: value for key, value in saved.items() if key not in head_keys})
        print(json.dumps({"saved_record_matches_live_bytes_and_fields": match,
                          "head_changed_since_observation": {
                              key: result[key] != saved[key] for key in head_keys},
                          "g0_ready": result["g0_ready"]}, indent=2))
        if not match:
            raise SystemExit(1)
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
