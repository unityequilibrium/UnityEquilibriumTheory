"""Build a deterministic review queue for generated core-artifact migration.

This is a control-plane artifact, not a physics result.  It reads the current
artifact migration manifest and records which pending artifacts still need a
generator identity, a generator-path switch, consumer rewrites, or a bounded
preflight.  It deliberately does not execute generators and does not modify
legacy research payloads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_artifact_path  # noqa: E402


MANIFEST = ROOT / "docs/core/00_governance/uet_core_artifact_migration_manifest.json"
OUTPUT = ROOT / canonical_artifact_path(
    "uet_core_artifact_generator_review_queue.json", "gates"
)
GENERATOR = "docs/scripts/audit/build_uet_core_artifact_generator_review_queue_v3.py"
SCHEMA_VERSION = "uet-core-artifact-generator-review-queue-v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def generator_status(record: dict[str, Any]) -> dict[str, Any]:
    generator_path = record.get("generator_path")
    if not generator_path:
        return {
            "status": "UNRESOLVED",
            "path_exists": False,
            "uses_canonical_path_authority": False,
            "contains_legacy_output_literal": False,
        }

    path = ROOT / str(generator_path)
    if not path.exists():
        return {
            "status": "MISSING",
            "path_exists": False,
            "uses_canonical_path_authority": False,
            "contains_legacy_output_literal": False,
        }

    text = path.read_text(encoding="utf-8", errors="replace")
    uses_authority = "canonical_artifact_path" in text
    contains_legacy = str(record.get("legacy_path", "")) in text
    if contains_legacy:
        status = "LEGACY_OUTPUT_LITERAL_REMAINS"
    elif uses_authority:
        status = "CANONICAL_PATH_AUTHORITY_PRESENT"
    else:
        status = "LEGACY_OUTPUT_PATH_OR_UNDECLARED"
    return {
        "status": status,
        "path_exists": True,
        "uses_canonical_path_authority": uses_authority,
        "contains_legacy_output_literal": contains_legacy,
    }


def category(record: dict[str, Any]) -> tuple[str, str, str, bool]:
    state = str(record.get("migration_state", "NOT_STARTED"))
    generator_count = int(record.get("generator_count") or 0)
    consumer_count = int(record.get("consumer_count") or 0)
    disposition = str(record.get("disposition", ""))

    if state == "MIGRATED":
        return (
            "MIGRATED",
            "no pending migration action",
            "retain legacy index boundary and verify canonical consumers",
            False,
        )
    if generator_count == 0:
        return (
            "GENERATOR_IDENTITY_UNRESOLVED",
            "no unique generator identity is recorded",
            "identify and source-lock the sole artifact generator before any move",
            False,
        )
    if consumer_count > 0:
        return (
            "GENERATOR_AND_CONSUMER_REWRITE_REQUIRED",
            "active consumers still reference the legacy artifact boundary",
            "switch the generator and every active consumer through the path authority",
            True,
        )
    if disposition == "generator_switch_required_before_move" or generator_count == 1:
        return (
            "GENERATOR_SWITCH_REQUIRED",
            "the unique generator must write the canonical path before preflight",
            "switch the generator, run a bounded semantic preflight, then decide move or block",
            True,
        )
    return (
        "REVIEW_REQUIRED",
        "migration disposition is not covered by an automatic safe category",
        "assign an owner and record an explicit migration disposition",
        False,
    )


def review_record(record: dict[str, Any]) -> dict[str, Any]:
    review_category, blocker, next_action, preflight_required = category(record)
    generator = generator_status(record)
    return {
        "asset_id": record.get("asset_id"),
        "artifact_name": Path(str(record.get("legacy_path", ""))).name,
        "legacy_path": record.get("legacy_path"),
        "canonical_path": record.get("canonical_path"),
        "logical_area": record.get("logical_area"),
        "owner_id": record.get("owner_id"),
        "room_id": record.get("room_id"),
        "evidence_status": record.get("evidence_status"),
        "migration_state": record.get("migration_state"),
        "disposition": record.get("disposition"),
        "generator_count": record.get("generator_count", 0),
        "generator_path": record.get("generator_path"),
        "generator_candidates": record.get("generator_candidates", []),
        "generator_status": generator,
        "consumer_count": record.get("consumer_count", 0),
        "active_consumers": record.get("downstream_dependencies", []),
        "review_category": review_category,
        "blocker": blocker,
        "next_action": next_action,
        "preflight_required": preflight_required,
        "legacy_reference_paths": record.get("legacy_reference_paths", []),
        "sha256_before": record.get("sha256_before"),
        "claim_boundary": "organization control only; no physics evidence or claim promotion",
    }


def build_payload() -> dict[str, Any]:
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    manifest = load_json(MANIFEST)
    records = manifest.get("records")
    if not isinstance(records, list):
        raise ValueError("artifact migration manifest records must be a list")

    rows = [review_record(dict(record)) for record in records]
    rows.sort(key=lambda item: str(item.get("legacy_path", "")))
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row["review_category"])
        counts[key] = counts.get(key, 0) + 1

    pending = [row for row in rows if row["review_category"] != "MIGRATED"]
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact": "uet_core_artifact_generator_review_queue",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "canonical_path_authority": "docs/core/core_paths.py",
        "source_manifest": {
            "path": repo_path(MANIFEST),
            "sha256": sha256(MANIFEST),
            "record_count": len(records),
        },
        "scope": {
            "legacy_boundary": "docs/core/artifacts",
            "canonical_boundary": "docs/core/07_artifacts",
            "execution_policy": "review-only; generators are not executed by this builder",
            "payload_policy": "legacy artifact payloads are never overwritten by this queue",
        },
        "summary": {
            "records_total": len(rows),
            "pending_records": len(pending),
            "migrated_records": counts.get("MIGRATED", 0),
            "category_counts": counts,
            "status": "PASS_WITH_REVIEW_REQUIRED" if pending else "PASS",
            "controlling_blocker": (
                "generator_identity_or_consumer_path_not_closed" if pending else None
            ),
            "next_wave": (
                "resolve one bounded generator/consumer family and run semantic preflight"
                if pending
                else "refresh indexes and run full migration verification"
            ),
            "claim_boundary": "organization control only; this artifact cannot promote physics status",
        },
        "records": rows,
    }


def comparable(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(payload))
    normalized.pop("generated_at", None)
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the committed queue is current")
    args = parser.parse_args()
    payload = build_payload()
    if args.check:
        if not OUTPUT.exists():
            print(f"missing generated queue: {repo_path(OUTPUT)}")
            return 1
        current = load_json(OUTPUT)
        if comparable(current) != comparable(payload):
            print(f"stale generated queue: {repo_path(OUTPUT)}")
            return 1
        print(json.dumps({"status": "PASS", "output": repo_path(OUTPUT)}, indent=2))
        return 0

    write_json(OUTPUT, payload)
    print(
        json.dumps(
            {
                "status": payload["summary"]["status"],
                "output": repo_path(OUTPUT),
                "pending_records": payload["summary"]["pending_records"],
                "category_counts": payload["summary"]["category_counts"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
