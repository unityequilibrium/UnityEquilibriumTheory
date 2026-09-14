"""Backfill semantic hashes for completed generated-artifact migrations.

This maintenance operation updates only migration-history metadata. It hashes
JSON artifacts after removing the same declared volatile metadata used by the
bounded migration runner, so a later generator refresh cannot turn a timestamp
change into a false content-drift failure.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
HISTORY = CORE / "00_governance" / "uet_core_artifact_migration_history.json"
VOLATILE_JSON_KEYS = frozenset({"generated_at"})


def normalize_json_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalize_json_payload(item)
            for key, item in value.items()
            if key not in VOLATILE_JSON_KEYS
        }
    if isinstance(value, list):
        return [normalize_json_payload(item) for item in value]
    return value


def semantic_payload_sha256(path: Path) -> str:
    if path.suffix.lower() == ".json":
        payload = normalize_json_payload(json.loads(path.read_text(encoding="utf-8")))
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    else:
        encoded = path.read_bytes()
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    payload = json.loads(HISTORY.read_text(encoding="utf-8"))
    updated = 0
    skipped: list[str] = []
    for record in payload.get("records", []):
        if record.get("migration_state") != "MIGRATED":
            continue
        if record.get("semantic_payload_sha256"):
            continue
        target = ROOT / str(record["canonical_path"])
        if not target.exists():
            skipped.append(str(record["canonical_path"]))
            continue
        record["semantic_payload_sha256"] = semantic_payload_sha256(target)
        record.setdefault("semantic_ignored_paths", [])
        updated += 1

    if updated:
        HISTORY.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({"status": "PASS" if not skipped else "BLOCKED", "updated": updated, "skipped": skipped}, ensure_ascii=False))
    return 0 if not skipped else 1


if __name__ == "__main__":
    raise SystemExit(main())