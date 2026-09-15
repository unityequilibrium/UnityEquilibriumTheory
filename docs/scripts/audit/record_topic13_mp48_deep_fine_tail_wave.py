"""Record the verified MP48 deep fine-tail convergence wave."""

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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def append_once(path: Path, marker: str, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    path.write_text(text.rstrip() + "\n\n" + body.strip() + "\n", encoding="utf-8")


def main() -> None:
    artifact = load(ARTIFACT)
    policy = artifact["mesh_policy"]
    artifact_hash = sha256(ARTIFACT)
    full_hash = sha256(FULL_GATE)
    register_hash = sha256(REGISTER)
    dependency_hash = sha256(DEPENDENCY)
    today = date.today().isoformat()

    update = f'''### {today} - MP48 deep fine-tail convergence refinement

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` refinement for `T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; complete MP48 route remains `BLOCKED`.
WHAT_IS_ACTUALLY_CLOSED: The canonical audit now evaluates `5x5x2`, `10x10x4`, `15x15x6`, `20x20x8`, `25x25x10`, `30x30x12`, and `35x35x14`. The declared fine-tail `20x20x8 -> 25x25x10 -> 30x30x12 -> 35x35x14` passes the unchanged absolute relative-step tolerance `0.01`, with maximum `{{policy["fine_tail_max_abs_relative_step"]}}`; the finest pair is `{{policy["finest_pair_meshes"][0]}} -> {{policy["finest_pair_meshes"][1]}}` at `{{policy["finest_pair_max_abs_relative_step"]}}`.
WHAT_REMAINS_OPEN: The complete route still has maximum adjacent-mesh change `{{artifact["max_abs_relative_mesh_step"]}}` from the native/coarse transition, so MP48 is not accepted as Ding PBTE `C_src`. Material-regime mapping, uncertainty, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, EOS/transport/KMS/entropy, and dimensional observable closure remain open.
DEPENDENCY_UNLOCKED: Fine-tail convergence diagnostic only; no Ding source, alpha, Core, Gravity, transport, or Galaxy dependency unlock.
STATUS: `{{artifact["status"]}}`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Canonical MP48 mesh audit was rerun with a batch-equivalent dynamical-matrix evaluator that preserves the original equation and tolerance. Artifact SHA-256 `{{artifact_hash}}`; full-gate SHA-256 `{{full_hash}}`; register SHA-256 `{{register_hash}}`; dependency-gate SHA-256 `{{dependency_hash}}`.
EQUATION_OR_MAPPING: `C_src^mesh(T) = N_A/N_q * sum_(q,mu) c_mu(q,T)` with `c_mu(T)=k_B*x^2*exp(x)/(exp(x)-1)^2`; no quantity is relabeled as Ding `C_src` and no `Delta_Tq = alpha_Phi_K * Delta_Phi` calibration is emitted.
VERIFICATION: Source integrity, finite rows, and zero negative modes pass for all seven meshes; fine-tail and finest-pair metrics pass, but route-wide convergence remains false. Focused MP48/register tests pass (`2 passed`); full Topic 13 regression passes (`177 passed, 625 deselected`). No fit, target access, Xie 2026 holdout access, or alpha emission.
CONTROLLING_BLOCKER: `mp48_force_constant_C_src_mesh_convergence_missing` for the complete independent route; the full gate retains Ding numeric `C_src`, material mapping, uncertainty, alpha, bridge, and physical transport blockers.
NEXT_ACTION: Treat the fine-tail branch as a named comparator only. Obtain an authorized Ding-compatible mode-resolved PBTE payload or an accepted same-regime reproduction with material-state, convergence, and uncertainty contracts; do not promote the fine-tail result to Ding source data.
CLAIM_BOUNDARY: Source-traceable harmonic fine-tail convergence diagnostic only. It is not Ding PBTE reproduction, UET transport validation, TTG prediction, `alpha_Phi_K` calibration, external validation, or Full Topic 13 closure.'''

    manifest = f'''## MP48 Deep Fine-Tail Mesh Convergence (2026-08-13)

The source-locked MP48 force-constant audit now includes seven meshes through `35x35x14`. The unchanged acceptance tolerance is `0.01` absolute relative adjacent-mesh step. The declared fine-tail `20x20x8` through `35x35x14` passes with maximum `{{policy["fine_tail_max_abs_relative_step"]}}`, while the complete route remains blocked at `{{artifact["max_abs_relative_mesh_step"]}}` because the native/coarse transition is not converged. The audit artifact is `docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json` with SHA-256 `{{artifact_hash}}`; this is not Ding `C_src`, not a measurement uncertainty, and not an alpha calibration. Full-gate SHA-256 is `{{full_hash}}` and downstream unlock remains false.'''

    current = f'''## Latest Source-Route Boundary: MP48 Deep Fine-Tail Convergence (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` refinement for `T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; complete route remains blocked.
WHAT_IS_ACTUALLY_CLOSED: Seven source-traceable MP48 meshes are now evaluated. The fine-tail `20x20x8 -> 25x25x10 -> 30x30x12 -> 35x35x14` passes the unchanged `0.01` criterion at maximum `{{policy["fine_tail_max_abs_relative_step"]}}`; the finest pair passes at `{{policy["finest_pair_max_abs_relative_step"]}}`.
WHAT_REMAINS_OPEN: Route-wide adjacent-mesh convergence still fails at `{{artifact["max_abs_relative_mesh_step"]}}`, so the independent route is not accepted as Ding PBTE `C_src`. Material mapping, uncertainty, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, EOS/transport/KMS/entropy, and dimensional observable closure remain open.
DEPENDENCY_UNLOCKED: Fine-tail diagnostic only; no downstream dependency unlock.
STATUS: `{{artifact["status"]}}`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Canonical artifact SHA-256 `{{artifact_hash}}`; full gate SHA-256 `{{full_hash}}`; major-result register SHA-256 `{{register_hash}}`; dependency gate SHA-256 `{{dependency_hash}}`.
EQUATION_OR_MAPPING: `C_src^mesh(T) = N_A/N_q * sum_(q,mu) c_mu(q,T)`; no UET base-Phi calibration is emitted.
VERIFICATION: Seven-mesh source audit and zero-negative-mode checks pass; route-wide convergence remains false. Focused tests `2 passed`; Topic 13 regression `177 passed, 625 deselected`; no fit, target, holdout, or alpha access.
CONTROLLING_BLOCKER: `mp48_force_constant_C_src_mesh_convergence_missing` for the complete route, plus the full bridge blockers.
NEXT_ACTION: Keep the fine-tail result as a comparator and obtain a Ding-compatible PBTE payload or accepted same-regime reproduction with uncertainty.
CLAIM_BOUNDARY: Internal harmonic convergence diagnostic only; not Ding validation, UET transport, alpha calibration, external validation, or Full Topic 13 closure.'''

    ledger = f'''## Topic 13 MP48 deep fine-tail convergence refinement

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: canonical seven-mesh MP48 audit, regression contract, full gate/register/dependency projections, topic manifest/current report/update log
- verifier: focused MP48/register tests `2 passed`; Topic 13 regression `177 passed, 625 deselected`; full gate `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: fine-tail `20x20x8` through `35x35x14` converged under unchanged `0.01` criterion; complete route remains blocked at `{{artifact["max_abs_relative_mesh_step"]}}`; no source promotion
- hashes: MP48 artifact `{{artifact_hash}}`; full gate `{{full_hash}}`; register `{{register_hash}}`; dependency gate `{{dependency_hash}}`
- remains: Ding-compatible numeric `C_src`, material/regime mapping, uncertainty, base-Phi SI anchor, independent alpha, bridge/beta, physical EOS/transport/KMS/entropy, and dimensional closure
- next action: pursue accepted Ding-compatible or same-regime PBTE route; keep fine-tail branch separate from Ding and UET claims
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree'''

    append_once(UPDATE_LOG, "### 2026-08-13 - MP48 deep fine-tail convergence refinement", update)
    append_once(MANIFEST, "## MP48 Deep Fine-Tail Mesh Convergence (2026-08-13)", manifest)
    append_once(CURRENT, "## Latest Source-Route Boundary: MP48 Deep Fine-Tail Convergence (2026-08-13)", current)
    append_once(LEDGER, "## Topic 13 MP48 deep fine-tail convergence refinement", ledger)


if __name__ == "__main__":
    main()
