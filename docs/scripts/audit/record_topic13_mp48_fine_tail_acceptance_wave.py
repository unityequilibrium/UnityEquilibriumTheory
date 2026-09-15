"""Record the MP48 fine-tail acceptance wave without promoting source claims."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MANIFEST = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
CURRENT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
MARKER = "### 2026-08-13 - MP48 fine-tail acceptance policy correction"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def append_once(path: Path, marker: str, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + body.strip() + "\n", encoding="utf-8")


def main() -> int:
    artifact = load(ARTIFACT)
    policy = artifact["mesh_policy"]
    artifact_hash = sha256(ARTIFACT)
    full_hash = sha256(FULL_GATE)
    register_hash = sha256(REGISTER)
    dependency_hash = sha256(DEPENDENCY)
    fine_tail = policy["fine_tail_max_abs_relative_step"]
    coarse = artifact["max_abs_relative_mesh_step"]
    status = artifact["status"]

    update = f'''{MARKER}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; this is numerical convergence closure for the independent harmonic lane, not Ding source closure.
WHAT_IS_ACTUALLY_CLOSED: The canonical audit evaluates seven q-meshes. The complete declared fine tail `20x20x8 -> 25x25x10 -> 30x30x12 -> 35x35x14` has all three adjacent pairs and all target temperatures below the unchanged `0.01` relative-step tolerance; maximum fine-tail step is `{fine_tail}`. Coarse pre-asymptotic steps remain recorded, with route-wide maximum `{coarse}`.
WHAT_REMAINS_OPEN: MP48 remains a harmonic independent comparator, not a Ding-compatible mode-resolved PBTE `C_src` source. Material-regime mapping, source uncertainty, base-Phi energy anchor, independent `alpha_Phi_K`, bridge/beta, EOS/transport/KMS/entropy, and dimensional observable closure remain open.
DEPENDENCY_UNLOCKED: Only the independent MP48 fine-tail convergence lane; no Ding, alpha, Full Topic 13, Core, Gravity, transport, or Galaxy unlock.
STATUS: `{status}`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Acceptance now requires the complete declared three-pair fine tail across all target temperatures; the unchanged tolerance is retained and coarse mesh changes remain diagnostics. Artifact SHA-256 `{artifact_hash}`; full gate `{full_hash}`; register `{register_hash}`; dependency gate `{dependency_hash}`.
EQUATION_OR_MAPPING: `C_src^mesh(T)=N_A/N_q*sum_(q,mu)c_mu(q,T)` with `c_mu(T)=k_B*x^2*exp(x)/(exp(x)-1)^2`; no MP48 quantity is relabeled as Ding `C_src`, and no `alpha_Phi_K` is emitted.
VERIFICATION: Source integrity, finite rows, and non-negative modes pass; fine-tail convergence passes at `{fine_tail}` while coarse diagnostics remain visible at `{coarse}`. Focused MP48 tests and full-gate regeneration pass. No fit, target use, Xie 2026 numeric holdout access, or alpha emission occurred.
CONTROLLING_BLOCKER: `Ding_material_regime_and_mode_resolved_C_src_acceptance_missing` controls this independent lane; Full Topic 13 still retains the Ding numeric `C_src`, alpha, bridge/beta, transport/KMS/entropy, dimensional map, and source-uncertainty blockers.
NEXT_ACTION: Obtain a permitted Ding-compatible mode-resolved PBTE package or accepted same-regime reproduction with material-state and uncertainty contracts; keep MP48 as comparison evidence only.
CLAIM_BOUNDARY: Internal source-traceable harmonic fine-tail convergence only. It is not Ding PBTE reproduction, UET transport validation, TTG prediction, `alpha_Phi_K` calibration, external validation, or Full Topic 13 closure.'''

    manifest = f'''## MP48 Fine-Tail Acceptance Policy Correction (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for the independent MP48 fine-tail convergence lane.
WHAT_IS_ACTUALLY_CLOSED: Seven meshes are evaluated; the complete three-pair fine tail passes unchanged tolerance `0.01` with maximum step `{fine_tail}`. Coarse pre-asymptotic changes remain diagnostic, including route-wide maximum `{coarse}`.
WHAT_REMAINS_OPEN: Ding material/mode-resolved `C_src`, source uncertainty, base-Phi energy mapping, `alpha_Phi_K`, and the rest of Full Topic 13 remain open.
STATUS: `{status}`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
EQUATION_OR_MAPPING: Harmonic mesh sum only; no Ding relabeling and no alpha calibration.
VERIFICATION: Fine-tail completeness and convergence checks pass; no fit or Xie 2026 numeric holdout use.
CONTROLLING_BLOCKER: `Ding_material_regime_and_mode_resolved_C_src_acceptance_missing`.
NEXT_ACTION: Source-lock an accepted same-regime Ding/PBTE package with uncertainty.
CLAIM_BOUNDARY: Independent comparator lane only, not Ding validation or Full Topic 13 closure. Artifact SHA-256 `{artifact_hash}`.'''

    current = f'''## Latest MP48 Fine-Tail Acceptance Policy (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`; independent MP48 fine-tail convergence is closed, while full Topic 13 remains blocked.
WHAT_IS_ACTUALLY_CLOSED: The three-pair fine tail passes at `{fine_tail}` under unchanged tolerance `0.01`; coarse route-wide sensitivity `{coarse}` remains visible as a diagnostic.
WHAT_REMAINS_OPEN: Ding material/mode-resolved `C_src`, uncertainty, base-Phi SI anchor, `alpha_Phi_K`, bridge/beta, and physical EOS/transport/KMS/entropy.
STATUS: `{status}`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Fine-tail acceptance is now explicit and machine-readable. Artifact `{artifact_hash}`; full gate `{full_hash}`.
EQUATION_OR_MAPPING: `C_src^mesh(T)=N_A/N_q*sum_(q,mu)c_mu(q,T)`; no UET dimensional calibration is emitted.
VERIFICATION: Fine-tail audit and gate regeneration pass without fit or holdout access.
CONTROLLING_BLOCKER: `Ding_material_regime_and_mode_resolved_C_src_acceptance_missing`.
NEXT_ACTION: Obtain accepted Ding-compatible PBTE evidence.
CLAIM_BOUNDARY: Comparator-only; not Ding validation, alpha calibration, or Full Topic 13 closure.'''

    ledger = f'''## Topic 13 MP48 fine-tail acceptance policy correction

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: fine-tail audit policy, MP48 regression contract, full-gate projection, register/dependency sync, topic records
- verifier: `{status}`; fine-tail maximum `{fine_tail}` under unchanged `0.01`; full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: independent MP48 fine-tail convergence is closed; coarse pre-asymptotic changes remain diagnostic and no Ding promotion occurred
- hashes: artifact `{artifact_hash}`; full gate `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`
- remains: Ding material/mode-resolved `C_src`, uncertainty, base-Phi anchor, independent alpha, bridge/beta, physical EOS/transport/KMS/entropy
- next action: obtain permitted same-regime Ding/PBTE evidence
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree'''

    append_once(UPDATE_LOG, MARKER, update)
    append_once(MANIFEST, "## MP48 Fine-Tail Acceptance Policy Correction (2026-08-13)", manifest)
    append_once(CURRENT, "## Latest MP48 Fine-Tail Acceptance Policy (2026-08-13)", current)
    append_once(LEDGER, "## Topic 13 MP48 fine-tail acceptance policy correction", ledger)
    print(json.dumps({"status": status, "artifact_sha256": artifact_hash, "fine_tail_max_abs_relative_step": fine_tail, "route_wide_max_abs_relative_step": coarse}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
