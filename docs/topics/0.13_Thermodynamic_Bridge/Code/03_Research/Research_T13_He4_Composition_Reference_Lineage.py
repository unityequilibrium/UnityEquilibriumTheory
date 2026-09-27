"""Audit migrated Core composition references without promoting their claims."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
COMPOSITION = ROOT / "docs/core/07_artifacts/topic13/t13_he4_core_thermodynamic_bridge_composition_audit.json"
CURRENT_ARTIFACTS = ROOT / "docs/core/07_artifacts"
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


def audit() -> dict:
    composition = json.loads(COMPOSITION.read_text(encoding="utf-8"))
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
        "verification_status": "REFERENCE_DRIFT_CLASSIFIED_NOT_REVALIDATED",
        "open_blockers": ["composition_evidence_paths_and_hashes_stale", "clean_equivalence_and_upstream_provenance_not_revalidated"],
        "controlling_blocker": "clean_equivalence_and_upstream_provenance_not_revalidated",
        "g0_baseline_ready": False,
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_boundary": "This screen does not change the recorded bounded Core composition claim or establish that relocated files are semantically equivalent. It does not close G0, predict He-II response, consume Xie 2026 data, or validate UET externally.",
    }


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(audit(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(OUTPUT)
