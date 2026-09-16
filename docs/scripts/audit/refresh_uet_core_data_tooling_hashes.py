"""Refresh data-tooling canonical hashes after an intentional path rewrite."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "docs" / "core" / "00_governance" / "uet_core_data_tooling_migration_manifest.json"
GENERATOR = "docs/scripts/audit/refresh_uet_core_data_tooling_hashes.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed = 0
    for row in payload.get("records", []):
        if not row.get("physical_compatibility_removed"):
            continue
        target = ROOT / str(row["canonical_path"])
        if not target.exists():
            continue
        old = row.get("sha256_after")
        new = sha256(target)
        if old != new:
            row["sha256_before_reference_rewrite"] = old
            row["sha256_after"] = new
            row["hash_refresh_reason"] = "canonical source received intended import/path reference repair during compatibility consolidation"
            changed += 1
    payload["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload["generator"] = GENERATOR
    payload["canonical_hashes_refreshed"] = changed
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "hashes_refreshed": changed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
