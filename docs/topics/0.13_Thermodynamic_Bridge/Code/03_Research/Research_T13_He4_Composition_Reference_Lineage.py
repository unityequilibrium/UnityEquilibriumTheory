"""Audit migrated Core composition references without promoting their claims."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
COMPOSITION = ROOT / "docs/core/07_artifacts/topic13/t13_he4_core_thermodynamic_bridge_composition_audit.json"
CURRENT_ARTIFACTS = ROOT / "docs/core/07_artifacts"
PLAN = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/funding_portfolio_14d_plan.json"
OUTPUT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_composition_reference_lineage.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve(row: dict, root: Path, current_artifacts: Path) -> dict:
    original = root / row["path"]
    if original.is_file():
        candidates = [original]
    else:
        candidates = sorted(current_artifacts.rglob(Path(row["path"]).name))
    resolved = []
    for path in candidates:
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        actual_hash = _sha256(path)
        resolved.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": actual_hash,
            "status": data.get("status"),
            "status_matches_record": data.get("status") == row["status"],
            "hash_matches_record": actual_hash == row["sha256"],
        })
    if not resolved:
        classification = "MISSING"
    elif len(resolved) > 1:
        classification = "AMBIGUOUS"
    elif resolved[0]["path"] == row["path"]:
        classification = "EXACT" if resolved[0]["hash_matches_record"] else "IN_PLACE_HASH_DRIFT"
    else:
        classification = "RELOCATED_SAME_HASH" if resolved[0]["hash_matches_record"] else "RELOCATED_HASH_DRIFT"
    return {
        "recorded_path": row["path"],
        "recorded_sha256": row["sha256"],
        "recorded_status": row["status"],
        "classification": classification,
        "candidates": resolved,
    }


def _field_deltas(before, after, pointer: str = "") -> list[dict]:
    if isinstance(before, dict) and isinstance(after, dict):
        changes = []
        for key in sorted(before.keys() | after.keys()):
            part = key.replace("~", "~0").replace("/", "~1")
            path = f"{pointer}/{part}"
            if key not in before or key not in after:
                changes.append({"path": path, "before": before.get(key), "after": after.get(key)})
            else:
                changes.extend(_field_deltas(before[key], after[key], path))
        return changes
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        changes = []
        for index, (old, new) in enumerate(zip(before, after)):
            changes.extend(_field_deltas(old, new, f"{pointer}/{index}"))
        return changes
    return [] if before == after else [{"path": pointer or "/", "before": before, "after": after}]


def _committed_comparison(commit: str, records: list[dict]) -> dict:
    compared = []
    for record in records:
        if len(record["candidates"]) != 1:
            compared.append({"path": record["recorded_path"], "state": "NO_UNIQUE_CURRENT_FILE"})
            continue
        current = record["candidates"][0]
        path = current["path"]
        try:
            historical = subprocess.run(
                ["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, check=False
            )
        except FileNotFoundError:
            historical = None
        if historical is None or historical.returncode != 0:
            compared.append({"path": path, "state": "COMMITTED_OBJECT_UNAVAILABLE"})
            continue
        prior_sha = hashlib.sha256(historical.stdout).hexdigest()
        current_sha = current["sha256"]
        old_data = json.loads(historical.stdout)
        new_data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        compared.append({
            "path": path,
            "state": "BYTE_IDENTICAL_TO_COMMIT" if prior_sha == current_sha else "CHANGED_SINCE_COMMIT",
            "committed_sha256": prior_sha,
            "current_sha256": current_sha,
            "field_deltas": _field_deltas(old_data, new_data),
        })
    counts = {state: sum(item["state"] == state for item in compared) for state in (
        "BYTE_IDENTICAL_TO_COMMIT", "CHANGED_SINCE_COMMIT", "NO_UNIQUE_CURRENT_FILE", "COMMITTED_OBJECT_UNAVAILABLE"
    )}
    return {
        "commit": commit,
        "comparison_scope": "committed tree only; historical dirty-worktree contents are not reconstructed",
        "records": compared,
        "counts": counts,
    }


def audit() -> dict:
    composition = json.loads(COMPOSITION.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    records = [_resolve(row, ROOT, CURRENT_ARTIFACTS) for row in composition["major_result"]["evidence_artifacts"]]
    classes = ("EXACT", "IN_PLACE_HASH_DRIFT", "RELOCATED_SAME_HASH", "RELOCATED_HASH_DRIFT", "AMBIGUOUS", "MISSING")
    counts = {key: sum(record["classification"] == key for record in records) for key in classes}
    status_matches = sum(len(record["candidates"]) == 1 and record["candidates"][0]["status_matches_record"] for record in records)
    return {
        "schema_version": "t13-he4-composition-reference-lineage-v1",
        "major_result_id": "T13_HE4_COMPOSITION_REFERENCE_LINEAGE_SCREEN",
        "topic": "0.13",
        "closure_level": "PARTIAL",
        "what_is_closed": "The current location, byte identity, and recorded-status match of every composition evidence reference are enumerated",
        "equation_or_mapping": "reference path + SHA-256 + status; equal status is not semantic or physical equivalence",
        "units": "not applicable to reference identity",
        "derivation_class": "deterministic provenance reconciliation",
        "observable": "traceability of the bounded He-4 Core composition reference graph",
        "data_role": "PROVENANCE_AUDIT_NOT_PHYSICAL_VALIDATION",
        "composition_path": COMPOSITION.relative_to(ROOT).as_posix(),
        "composition_sha256": _sha256(COMPOSITION),
        "composition_claim": composition["major_result"]["closure_level"],
        "composition_claim_boundary": composition["major_result"]["claim_boundary"],
        "records": records,
        "counts": counts,
        "recorded_status_matches": status_matches,
        "committed_snapshot_comparison": _committed_comparison(plan["baseline"]["head"], records),
        "verification_status": "REFERENCE_DRIFT_CLASSIFIED_NOT_REVALIDATED",
        "open_blockers": ["composition_evidence_paths_and_hashes_stale", "clean_equivalence_and_upstream_provenance_not_revalidated"],
        "controlling_blocker": "clean_equivalence_and_upstream_provenance_not_revalidated",
        "g0_baseline_ready": False,
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_boundary": "This screen does not change the recorded bounded Core composition claim or establish that relocated files are semantically equivalent. It does not close G0, predict He-II response, consume Xie 2026 data, or validate UET externally.",
    }


if __name__ == "__main__":
    OUTPUT.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(OUTPUT)
