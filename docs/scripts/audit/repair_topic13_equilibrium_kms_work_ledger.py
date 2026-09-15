"""Record the Topic 13 equilibrium KMS wave in the daily work ledger."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
KMS = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_equilibrium_kms_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
MARKER = "## Topic 13 equilibrium KMS/FDT identity wave"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    text = LEDGER.read_text(encoding="utf-8-sig")
    if MARKER not in text:
        entry = f"""
{MARKER}

- area: research-core (secondary: result-artifacts)
- workspace: docs/topics/0.13_Thermodynamic_Bridge
- files/artifacts: equilibrium KMS module; focused test; KMS audit artifact; full-gate lane/evidence projection; major-result register/dependency sync; Topic 13 update log
- verifier: PASS_ACTION_DERIVED_EQUILIBRIUM_KMS_FDT_LANE; focused tests 3 passed; full gate remains BLOCKED_OPEN_T13_FULL_BRIDGE
- public-safety: partial
- result: equilibrium mode-level KMS/FDT and entropy identity lane closed; interacting SK/KMS, physical Kubo, transport, SI, and alpha remain open
- hashes: KMS {digest(KMS)}; full {digest(FULL)}; register {digest(REGISTER)}; dependency {digest(DEPENDENCY)}
- remains: interacting SK/KMS collision-noise kernel, physical retarded-correlator Kubo record, spatial entropy current, dissipative balance, dimensional Phi observable map, independent alpha_Phi_K, Ding C_src, and source-grade thermal uncertainties
- next action: declare the interacting open-system kernel and obtain state-matched Kubo evidence; keep equilibrium KMS as a lane result and do not promote full Topic 13
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
        LEDGER.write_text(text.rstrip() + "\n" + entry.lstrip(), encoding="utf-8")
        changed = True
    else:
        changed = False
    print({"status": "PASS_TOPIC13_EQUILIBRIUM_KMS_WORK_LEDGER", "changed": changed})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

