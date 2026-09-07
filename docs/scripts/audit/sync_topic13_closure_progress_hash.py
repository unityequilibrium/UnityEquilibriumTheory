"""Synchronize the evidence hash in the latest closure-progress log entry."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROGRESS = ROOT / "docs/core/artifacts/t13_full_closure_progress.json"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MARKER = "### 2026-08-24 - Topic 13 closure progress dashboard"
HASH_BLOCK = re.compile(r"(EVIDENCE_HASH:\n- `)[0-9a-fA-F]{64}(`)")


def main() -> int:
    current_hash = hashlib.sha256(PROGRESS.read_bytes()).hexdigest()
    text = UPDATE_LOG.read_text(encoding="utf-8")
    start = text.find(MARKER)
    if start < 0:
        raise SystemExit("closure progress marker is missing")
    end = text.find("\n### ", start + len(MARKER))
    if end < 0:
        end = len(text)
    prefix, entry, suffix = text[:start], text[start:end], text[end:]
    updated, count = HASH_BLOCK.subn(rf"\g<1>{current_hash}\g<2>", entry, count=1)
    if count != 1:
        raise SystemExit("closure progress evidence hash block is missing")
    if updated != entry:
        UPDATE_LOG.write_text(prefix + updated + suffix, encoding="utf-8")
    print(
        {
            "status": "PASS_T13_CLOSURE_PROGRESS_HASH_SYNCHRONIZED",
            "progress_sha256": current_hash,
            "changed": updated != entry,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
