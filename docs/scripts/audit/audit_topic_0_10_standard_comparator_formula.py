"""Audit the declared Topic 0.10 standard-comparator formula boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FORMULA = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos/FORMULA_AUDIT.md"
BENCHMARK = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/fluid_benchmark_validation.json"
OUT = ROOT / "docs/core/07_artifacts/correspondence/topic_0_10_standard_comparator_formula_audit.json"


def main() -> int:
    text = FORMULA.read_text(encoding="utf-8")
    artifact = json.loads(BENCHMARK.read_text(encoding="utf-8-sig"))
    required_tokens = ["FD-NS-DIFFUSION", "proof_status", "failure_mode", "next_hardening_step", "simplified", "not a full CFD solver"]
    formula_gate = all(token in text for token in required_tokens)
    result_status = artifact.get("results", {}).get("status")
    status = "PASS_WITH_INTERNAL_BENCHMARK_BOUNDARY" if formula_gate else "BLOCKED_FORMULA_AUDIT"
    report = {
        "schema_version": "1.0",
        "artifact": "topic_0_10_standard_comparator_formula_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "formula_audit": {"path": str(FORMULA.relative_to(ROOT)).replace("\\", "/"), "sha256": hashlib.sha256(FORMULA.read_bytes()).hexdigest(), "required_tokens_present": formula_gate, "formula_role": "standard simplified comparator only"},
        "benchmark": {"path": str(BENCHMARK.relative_to(ROOT)).replace("\\", "/"), "sha256": hashlib.sha256(BENCHMARK.read_bytes()).hexdigest(), "result_status": result_status, "speedup": artifact.get("results", {}).get("speedup"), "thresholds": artifact.get("thresholds")},
        "gates": {"formula_fields_present": formula_gate, "benchmark_boundary_explicit": "external CFD" in artifact.get("claim_boundary", "") and "Navier-Stokes theorem" in artifact.get("claim_boundary", ""), "full_constitutive_transport_deferred": True},
        "controlling_blocker": "current simplified comparator result is below its internal speed threshold" if result_status != "PASS" else "full constitutive transport remains deferred",
        "next_action": "retain the comparator as internal evidence and defer full UET constitutive transport until after Gravity/observable mapping",
        "claim_boundary": "internal simplified comparator/formula audit only; no external CFD validation, physical transport proof, or UET closure",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "benchmark_status": result_status, "formula_gate": formula_gate}, indent=2))
    return 0 if status != "BLOCKED_FORMULA_AUDIT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
