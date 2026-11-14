"""Compare recovered historical baseline bytes with clean-checkout candidates, read-only."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
RECOVERY = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_funding_historical_snapshot_recovery.json"
RECORD = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_funding_clean_admission_triage.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_value(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def git_file_state(root: Path, path: str) -> str:
    status = git_value(root, "status", "--porcelain=v1", "--", path)
    return "UNTRACKED" if status.startswith("?? ") else "MODIFIED" if status else "TRACKED_CLEAN"


def changes(before: object, after: object, pointer: str = "") -> list[str]:
    if isinstance(before, dict) and isinstance(after, dict):
        result = []
        for key in sorted(before.keys() | after.keys()):
            child = f"{pointer}/{key}"
            if key not in before or key not in after:
                result.append(child)
            else:
                result.extend(changes(before[key], after[key], child))
        return result
    if isinstance(before, list) and isinstance(after, list):
        result = []
        for index in range(max(len(before), len(after))):
            child = f"{pointer}/{index}"
            if index >= len(before) or index >= len(after):
                result.append(child)
            else:
                result.extend(changes(before[index], after[index], child))
        return result
    return [] if before == after else [pointer]


def classify(pointer: str) -> str:
    key = pointer.rsplit("/", 1)[-1]
    if key in {"path", "sha256"}:
        return "REFERENCE_TOKEN"
    if key in {
        "status", "closure_level", "claim_boundary", "controlling_blocker",
        "verification_status", "full_core_unlock", "g0_baseline_ready", "dependency_unlocked",
        "acceptance_decision", "route_class", "current_state", "audit_status",
        "field_coverage_count", "rejection_reasons", "open_blockers",
    } or "claim" in key or any(marker in pointer for marker in (
        "/major_result/what_is_closed", "/major_result/open_blockers", "/requirements/",
        "/rejection_reasons/",
    )):
        return "CLAIM_OR_GATE"
    return "OTHER_CONTENT"


def triage(source_root: Path) -> dict:
    record = json.loads(RECOVERY.read_text(encoding="utf-8"))
    rows = []
    for item in record["records"]:
        relative_path = item["path"]
        source = source_root / relative_path
        clean = ROOT / relative_path
        source_digest = sha256(source) if source.is_file() else None
        if source_digest != item["observed_sha256"]:
            raise ValueError(f"Historical source changed or disappeared: {relative_path}")
        clean_digest = sha256(clean) if clean.is_file() else None
        if clean_digest is None:
            state, pointers = "MISSING_AT_RECORDED_PATH", []
        elif clean_digest == source_digest:
            state, pointers = "BYTE_IDENTICAL", []
        elif source.suffix.lower() == ".json":
            source_json = json.loads(source.read_text(encoding="utf-8"))
            clean_json = json.loads(clean.read_text(encoding="utf-8"))
            pointers = changes(source_json, clean_json)
            state = "JSON_FIELD_DIFFERENCE" if pointers else "SERIALIZATION_ONLY_DIFFERENCE"
        else:
            state, pointers = "NON_JSON_BYTE_DIFFERENCE", []
        classes = {name: [pointer for pointer in pointers if classify(pointer) == name]
                   for name in ("REFERENCE_TOKEN", "CLAIM_OR_GATE", "OTHER_CONTENT")}
        rows.append({
            "path": relative_path,
            "source_sha256": source_digest,
            "source_git_worktree_state_at_observation": item["git_worktree_state"],
            "clean_sha256": clean_digest,
            "clean_state": state,
            "difference_counts": {name: len(items) for name, items in classes.items()},
            "claim_or_gate_pointers": classes["CLAIM_OR_GATE"],
            "other_content_pointers": classes["OTHER_CONTENT"],
            "reference_token_pointers": classes["REFERENCE_TOKEN"],
            "admission_decision": "REVIEW_REQUIRED_NOT_AUTO_ADMITTED",
        })
    return {
        "schema_version": "t13-clean-admission-triage-v1",
        "record_class": "CROSS_WORKTREE_FIELD_DIFF_NOT_SEMANTIC_EQUIVALENCE",
        "records": rows,
        "counts": {state: sum(row["clean_state"] == state for row in rows) for state in (
            "MISSING_AT_RECORDED_PATH", "BYTE_IDENTICAL", "JSON_FIELD_DIFFERENCE",
            "SERIALIZATION_ONLY_DIFFERENCE", "NON_JSON_BYTE_DIFFERENCE")},
        "g0_ready": False,
        "full_core_unlock": False,
        "claim_boundary": "A field-level diff only triages owner review. It does not establish source-chain equivalence, revalidate Core, or admit a physical observable.",
    }


def verify_saved(record: dict, source_root: Path | None = None) -> dict[str, bool]:
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    old_by_path = {row["path"]: row for row in recovery["records"]}
    rows = record["records"]
    paths = [row["path"] for row in rows]
    checks = {
        "paths_unique_and_complete": len(paths) == len(set(paths)) == len(old_by_path)
        and set(paths) == set(old_by_path),
        "source_hashes_and_states_match_recovery": all(
            row["source_sha256"] == old_by_path[row["path"]]["observed_sha256"]
            and row["source_git_state"] == old_by_path[row["path"]]["git_worktree_state"]
            for row in rows if row["path"] in old_by_path
        ),
        "clean_hashes_current": all(
            row["clean_sha256"] == (sha256(ROOT / row["path"])
                                     if (ROOT / row["path"]).is_file() else None)
            for row in rows
        ),
        "counts_match_rows": all(
            count == sum(row["clean_state"] == state for row in rows)
            for state, count in record["counts"].items()
        ),
        "recovery_hash_current": sha256(RECOVERY) == record["evidence_artifacts"][0]["sha256"],
        "no_automatic_admission": record["g0_ready"] is False
        and record["full_core_unlock"] is False and record["dependency_unlocked"] == [],
    }
    if source_root is not None:
        live_by_path = {row["path"]: row for row in triage(source_root)["records"]}
        checks["live_source_branch_and_head_match_snapshot"] = (
            git_value(source_root, "branch", "--show-current") == record["source_branch"]
            and git_value(source_root, "rev-parse", "HEAD") == record["source_head_at_observation"]
        )
        checks["live_source_git_states_match_snapshot"] = all(
            git_file_state(source_root, row["path"]) == row["source_git_state"]
            for row in rows
        )
        checks["live_field_diff_matches_record"] = all(
            row["clean_state"] == live_by_path[row["path"]]["clean_state"]
            and row["difference_counts"] == live_by_path[row["path"]]["difference_counts"]
            and row["source_sha256"] == live_by_path[row["path"]]["source_sha256"]
            and row["clean_sha256"] == live_by_path[row["path"]]["clean_sha256"]
            for row in rows
        )
        checks["parsed_json_equality_checked"] = all(
            row["parsed_json_equal"] == (live_by_path[row["path"]]["clean_state"]
                                          == "SERIALIZATION_ONLY_DIFFERENCE")
            for row in rows if row["parsed_json_equal"] is not None
        )
        source_route = next(row for row in rows if row["path"].endswith("t13_csrc_source_route_priority_audit.json"))
        source_data = json.loads((source_root / source_route["path"]).read_text(encoding="utf-8"))["routes"][5]
        clean_data = json.loads((ROOT / source_route["path"]).read_text(encoding="utf-8"))["routes"][5]
        delta = source_route["decision_delta"]
        checks["source_route_decision_delta_checked"] = (
            delta["source_route_class"] == source_data["route_class"]
            and delta["source_acceptance"] == source_data["acceptance_decision"]
            and delta["source_raw_numeric_status"] == source_data["field_coverage"]["raw_numeric_or_reproduction_payload"]["status"]
            and delta["clean_route_class"] == clean_data["route_class"]
            and delta["clean_acceptance"] == clean_data["acceptance_decision"]
            and delta["clean_raw_numeric_status"] == clean_data["field_coverage"]["raw_numeric_or_reproduction_payload"]["status"]
        )
        curved = next(row for row in rows if row["path"].endswith("core_curved_3p1_parent_gate.json"))
        source_gate = json.loads((source_root / curved["path"]).read_text(encoding="utf-8"))
        clean_gate = json.loads((ROOT / curved["path"]).read_text(encoding="utf-8"))
        delta = curved["decision_delta"]
        checks["curved_gate_decision_delta_checked"] = (
            delta["source_status"] == source_gate["status"]
            and delta["clean_status"] == clean_gate["status"]
            and delta["source_open_blockers"] == source_gate["major_result"]["open_blockers"]
            and delta["clean_open_blockers"] == clean_gate["major_result"]["open_blockers"]
            and delta["source_dependency_unlocked_differs"]
            == (source_gate["major_result"]["dependency_unlocked"]
                != clean_gate["major_result"]["dependency_unlocked"])
        )
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, help="Read-only source worktree for live diff")
    args = parser.parse_args()
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    checks = verify_saved(record, args.source_root)
    print(json.dumps(checks, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
