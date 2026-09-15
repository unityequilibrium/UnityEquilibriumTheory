"""Attach the Topic 0.10 formula-audit artifact to the Wave 1 contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
FORMULA = ROOT / "docs/core/07_artifacts/correspondence/topic_0_10_standard_comparator_formula_audit.json"


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    formula = json.loads(FORMULA.read_text(encoding="utf-8-sig"))
    room = contract["rooms"]["topic_0_10_comparator"]
    room["evidence"].append({"path": "docs/core/07_artifacts/correspondence/topic_0_10_standard_comparator_formula_audit.json", "present": True, "sha256": hashlib.sha256(FORMULA.read_bytes()).hexdigest(), "summary": {"status": formula.get("status"), "benchmark_status": formula.get("benchmark", {}).get("result_status")}})
    room["controlling_blocker"] = formula.get("controlling_blocker")
    contract["integration_blockers"] = sorted(set(contract.get("integration_blockers", []) + [formula.get("controlling_blocker")]))
    CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": formula.get("status"), "benchmark_status": formula.get("benchmark", {}).get("result_status")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
