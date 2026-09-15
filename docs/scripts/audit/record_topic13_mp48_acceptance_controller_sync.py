"""Record the post-acceptance MP48 controller synchronization wave."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"
ACCEPTANCE = ROOT / "docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MANIFEST = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
CURRENT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
MARKER = "### 2026-08-13 - MP48 acceptance-controller synchronization"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def append_once(path: Path, marker: str, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + body.strip() + "\n", encoding="utf-8")


def main() -> int:
    mesh = load(ARTIFACT)
    acceptance = load(ACCEPTANCE)
    full_gate = load(FULL_GATE)
    fine_tail = mesh["mesh_policy"]["fine_tail_max_abs_relative_step"]
    contract_state = {
        "force_constant_mesh_pass": acceptance["candidate_evaluations"]["mp48_harmonic_comparator"]["force_constant_mesh_pass"],
        "material_equivalent_to_ding": acceptance["candidate_evaluations"]["mp48_harmonic_comparator"]["material_equivalent_to_ding"],
        "mode_resolved_ding_c_src_ready": acceptance["candidate_evaluations"]["mp48_harmonic_comparator"]["mode_resolved_ding_c_src_ready"],
        "accepted_for_full_topic13": acceptance["acceptance"]["accepted_for_full_topic13"],
    }
    if not contract_state["force_constant_mesh_pass"]:
        raise RuntimeError("MP48 fine-tail mesh pass is not synchronized")
    if contract_state["material_equivalent_to_ding"] or contract_state["mode_resolved_ding_c_src_ready"]:
        raise RuntimeError("MP48 acceptance contract unexpectedly promotes Ding equivalence")
    if contract_state["accepted_for_full_topic13"]:
        raise RuntimeError("MP48 acceptance contract unexpectedly unlocks Topic 13")

    hashes = {
        "mesh_artifact": sha256(ARTIFACT),
        "acceptance_contract": sha256(ACCEPTANCE),
        "full_gate": sha256(FULL_GATE),
        "register": sha256(REGISTER),
        "dependency_gate": sha256(DEPENDENCY),
    }
    status = mesh["status"]
    full_status = full_gate["status"]

    update = f'''{MARKER}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for MP48 fine-tail convergence and `PARTIAL` for `T13_FULL_THERMODYNAMIC_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The complete three-pair MP48 fine tail is accepted at maximum relative step `{fine_tail}` under the unchanged tolerance; the acceptance contract now records `force_constant_mesh_pass=true`.
WHAT_REMAINS_OPEN: MP48 is not material-equivalent to Ding, has no mode-resolved Ding PBTE `C_src` response, and is not accepted for Full Topic 13. `alpha_Phi_K`, base-Phi SI mapping, bridge/beta, EOS/transport/KMS/entropy, and source uncertainty remain open.
DEPENDENCY_UNLOCKED: Only the MP48 numerical acceptance-policy lane; no Ding, alpha, Full Topic 13, Core, Gravity, transport, or Galaxy dependency is unlocked.
STATUS: MP48 `{status}`; Full Topic 13 `{full_status}`.
WHAT_CHANGED: The post-repair acceptance artifact, full gate, closure register, and dependency gate are synchronized in one evidence record.
EQUATION_OR_MAPPING: `C_src^mesh(T)=N_A/N_q*sum_(q,mu)c_mu(q,T)` remains an independent harmonic comparator; it is not relabeled as Ding `C_src` and does not define `alpha_Phi_K`.
VERIFICATION: Mesh pass, non-equivalence guard, no-acceptance guard, hash capture, and holdout exclusion remain true. Xie 2026 numeric data were not read or consumed.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing` remains the source controller; `alpha_Phi_K` remains independently uncalibrated.
NEXT_ACTION: Obtain a permitted Ding-compatible mode-resolved PBTE package or accepted same-regime reproduction; otherwise keep the source route explicitly open without relabeling MP48.
CLAIM_BOUNDARY: This closes evidence synchronization and an internal harmonic convergence lane only. It is not Ding validation, TTG prediction, UET transport validation, `alpha_Phi_K` calibration, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: mesh `{hashes["mesh_artifact"]}`; acceptance `{hashes["acceptance_contract"]}`; full gate `{hashes["full_gate"]}`; register `{hashes["register"]}`; dependency `{hashes["dependency_gate"]}`.'''

    manifest = f'''## MP48 Acceptance Controller Synchronization (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for fine-tail convergence; `PARTIAL` for Full Topic 13.
WHAT_IS_ACTUALLY_CLOSED: `force_constant_mesh_pass=true` under unchanged fine-tail policy.
WHAT_REMAINS_OPEN: `material_equivalent_to_ding=false`, `mode_resolved_ding_c_src_ready=false`, and `accepted_for_full_topic13=false`; source, alpha, bridge, transport, and dimensional blockers remain.
STATUS: `{status}`; Full Topic 13 `{full_status}`.
VERIFICATION: Acceptance guards and evidence hashes are synchronized; no holdout or fit path was used.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.
NEXT_ACTION: Obtain accepted same-regime Ding/PBTE evidence.
CLAIM_BOUNDARY: Internal comparator acceptance-policy synchronization only. Mesh artifact `{hashes["mesh_artifact"]}`; acceptance contract `{hashes["acceptance_contract"]}`; full gate `{hashes["full_gate"]}`.'''

    current = f'''## Latest MP48 Acceptance Controller Synchronization (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for MP48 fine-tail convergence; `PARTIAL` for Full Topic 13.
WHAT_IS_ACTUALLY_CLOSED: The acceptance contract records a passing fine-tail mesh controller.
WHAT_REMAINS_OPEN: Ding material/PBTE equivalence, numeric `C_src`, base-Phi SI anchor, `alpha_Phi_K`, and full bridge closure.
STATUS: `{status}`; Full Topic 13 `{full_status}`.
WHAT_CHANGED: Acceptance, full gate, register, and dependency hashes are synchronized.
EQUATION_OR_MAPPING: Harmonic mesh sum only; no Ding relabeling and no UET dimensional calibration.
VERIFICATION: Contract guards pass; Xie 2026 numeric holdout remains excluded.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.
NEXT_ACTION: Obtain permitted same-regime PBTE evidence.
CLAIM_BOUNDARY: Comparator-only; not Ding validation, alpha calibration, or Full Topic 13 closure. Full gate `{hashes["full_gate"]}`.'''

    ledger = f'''## Topic 13 MP48 acceptance-controller synchronization

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: MP48 mesh audit, independent C_src acceptance contract, full gate, closure register, dependency gate, topic records
- verifier: mesh `{status}`; Full Topic 13 `{full_status}`
- public-safety: `partial`
- result: fine-tail convergence is accepted for the harmonic comparator; Ding equivalence and Full Topic 13 acceptance remain false
- hashes: mesh `{hashes["mesh_artifact"]}`; acceptance `{hashes["acceptance_contract"]}`; full gate `{hashes["full_gate"]}`; register `{hashes["register"]}`; dependency `{hashes["dependency_gate"]}`
- remains: Ding mode-resolved `C_src`, material/state mapping, independent alpha, base-Phi anchor, bridge/beta, physical transport/KMS/entropy
- next action: obtain permitted same-regime Ding/PBTE evidence or retain the explicit source blocker
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree'''

    append_once(UPDATE_LOG, MARKER, update)
    append_once(MANIFEST, "## MP48 Acceptance Controller Synchronization (2026-08-13)", manifest)
    append_once(CURRENT, "## Latest MP48 Acceptance Controller Synchronization (2026-08-13)", current)
    append_once(LEDGER, "## Topic 13 MP48 acceptance-controller synchronization", ledger)
    print(json.dumps({"status": status, "full_status": full_status, "contract_state": contract_state, "hashes": hashes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
