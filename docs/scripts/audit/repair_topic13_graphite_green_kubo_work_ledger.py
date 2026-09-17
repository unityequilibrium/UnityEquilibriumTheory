"""Record the Topic 13 Green-Kubo source-boundary wave in the daily ledger."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_graphite_green_kubo_source_boundary_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
MARKER = "## Topic 13 public Green-Kubo source-boundary wave"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    text = LEDGER.read_text(encoding="utf-8-sig")
    if MARKER not in text:
        entry = """
## Topic 13 public Green-Kubo source-boundary wave

- area: research-core (secondary: result-artifacts)
- workspace: docs/topics/0.13_Thermodynamic_Bridge
- files/artifacts: Green-Kubo source-boundary audit; full-gate projection; major-result register/dependency sync; Topic 13 update log
- verifier: PASS_SCOPED_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY; focused tests 2 passed; full gate remains BLOCKED_OPEN_T13_FULL_BRIDGE
- public-safety: partial
- result: primary graphite/graphene Green-Kubo candidates are source-identified, but no base-Phi/UET space-response mapping permits physical Kubo acceptance
- hashes: audit """ + digest(AUDIT) + """; full """ + digest(FULL) + """; register """ + digest(REGISTER) + """; dependency """ + digest(DEPENDENCY) + """
- remains: physical Kubo record, UET state mapping, Ding material match, source hash/uncertainty contract, base-Phi SI anchor, independent alpha, and full transport/SK/KMS/entropy closure
- next action: obtain a permitted state-matched correlator or retain the comparator boundary; no silent relabeling or holdout use
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
        LEDGER.write_text(text.rstrip() + "\n" + entry.lstrip(), encoding="utf-8")
        changed = True
    else:
        changed = False
    print({"status": "PASS_TOPIC13_GREEN_KUBO_WORK_LEDGER", "changed": changed})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

