"""Record the completed Calorine candidate-boundary hardening section."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    marker = "## Topic 13 Calorine/Zenodo NEP BTE candidate-boundary wave"
    text = LEDGER.read_text(encoding="utf-8-sig")
    if marker in text:
        print({"changed": False, "reason": "already_logged"})
        return 0
    block = f"""

{marker}

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: Calorine/Zenodo candidate-boundary artifact; focused test; full-gate integration; manifest/update-log synchronization; runner idempotence repair
- verifier: `PASS_SCOPED_CALORINE_NEP_BTE_CANDIDATE_BOUNDARY`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; focused test `2 passed`; complete Topic 13 runner passed
- public-safety: `partial`
- result: public graphite NEP/BTE candidate route is source-located but not accepted as Ding `C_src` or an independent `alpha_Phi_K` calibration
- hashes: candidate artifact `{sha256(ARTIFACT)}`; full gate `{sha256(FULL_GATE)}`
- remains: deposited mode-resolved `C_src(T)` with units/uncertainty/convergence, Ding material-state mapping, base-Phi SI anchor, independent `alpha_Phi_K`, and full bridge/EOS/transport/KMS/entropy closure
- next action: pursue a source-locked PBTE rerun only if the route can satisfy the strict material-state, convergence, uncertainty, no-fit, and no-holdout contract; otherwise preserve the candidate boundary
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    LEDGER.write_text(text.rstrip() + block, encoding="utf-8")
    print({"changed": True})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
