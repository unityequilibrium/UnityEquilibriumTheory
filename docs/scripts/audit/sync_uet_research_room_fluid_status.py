"""Attach the latest Topic 0.10 comparator result to the Wave 1 contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
ARTIFACT = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/fluid_benchmark_validation.json"


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    result = artifact.get("results", {})
    status = "PASS_INTERNAL_SIMPLIFIED_BENCHMARK" if result.get("status") == "PASS" else "FAIL_INTERNAL_SIMPLIFIED_BENCHMARK"
    room = contract["rooms"]["topic_0_10_comparator"]
    room["verification_status"] = status
    room["controlling_blocker"] = "simplified comparator speed/stability gate is not a physical validation gate; current speed threshold result remains FAIL" if status.startswith("FAIL") else "full_UET_constitutive_transport_deferred_until_post_Gravity_dependency_gate"
    room["evidence"] = [{"path": "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/fluid_benchmark_validation.json", "present": True, "sha256": hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), "summary": {"status": result.get("status"), "speedup": result.get("speedup"), "thresholds": artifact.get("thresholds")}}]
    contract["integration_blockers"] = sorted(set(contract.get("integration_blockers", []) + (["Topic 0.10 latest simplified comparator run is below its internal speed threshold"] if status.startswith("FAIL") else [])))
    CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "speedup": result.get("speedup")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
