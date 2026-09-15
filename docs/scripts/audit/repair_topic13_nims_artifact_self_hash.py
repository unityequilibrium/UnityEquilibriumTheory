"""Remove the impossible self-referential hash from the NIMS route artifact."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_nims_graphite_ltc_route_no_go.json"


def main() -> int:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    evidence = data["major_result"]["evidence_artifacts"][0]
    if evidence.get("sha256") == "self-referential-after-write":
        evidence.pop("sha256")
        evidence["hash_scope"] = (
            "file hash is recorded by the Topic 13 full gate and central major-result register; "
            "the artifact does not self-embed its own hash"
        )
    ARTIFACT.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print("removed impossible self-referential NIMS artifact hash")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
