"""Mark the narrow housekeeping drift items after their owner audits run."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/core/07_artifacts/gates/uet_research_room_wave1_integration_gate.json"
INDEX = ROOT / "docs/topics/README.md"


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    text = INDEX.read_text(encoding="utf-8")
    synced = "latest scalar Hubble artifact" in text and "full cosmology remains blocked" in text
    gate["housekeeping"]["topic_0_3_index"].update(
        {
            "status": "SYNCED_SCALAR_PASS_FULL_COSMOLOGY_BLOCKED" if synced else "REQUIRES_INDEX_SYNC",
            "index_sync_verified": synced,
        }
    )
    gate["housekeeping"]["inbox_alignment"]["claim_boundary"] = "housekeeping only; stale source-path drift remains blocked until the old artifact is rebuilt from current checkout paths"
    gate["housekeeping"]["topic_0_22_separate_checkpoint"]["status"] = "SEPARATE_PREEXISTING_CHECKPOINT"
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"topic_0_3_index_sync_verified": synced, "inbox_status": gate["housekeeping"]["inbox_alignment"].get("status")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
