"""Record the MP48 full-gate narrative drift repair."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PATHS = {
    "mesh": ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json",
    "acceptance": ROOT / "docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json",
    "full_gate": ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json",
    "register": ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json",
    "dependency": ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json",
    "update_log": ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md",
    "manifest": ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md",
    "current": ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md",
    "ledger": ROOT / "WORK_LEDGER/2026/2026-08-13.md",
}
MARKER = "### 2026-08-13 - MP48 full-gate narrative drift repair"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def append_once(path: Path, marker: str, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + body.strip() + "\n", encoding="utf-8")


def main() -> int:
    mesh = load(PATHS["mesh"])
    acceptance = load(PATHS["acceptance"])
    full_gate = load(PATHS["full_gate"])
    old_phrase = "mesh-convergence question is closed as a scoped no-go"
    if old_phrase in PATHS["full_gate"].read_text(encoding="utf-8"):
        raise RuntimeError("stale MP48 phrase remains in full gate")
    if acceptance["candidate_evaluations"]["mp48_harmonic_comparator"]["accepted_for_full_topic13"]:
        raise RuntimeError("MP48 must remain rejected for Full Topic 13")

    hashes = {key: sha256(PATHS[key]) for key in ("mesh", "acceptance", "full_gate", "register", "dependency")}
    fine_tail = mesh["mesh_policy"]["fine_tail_max_abs_relative_step"]
    status = mesh["status"]
    full_status = full_gate["status"]
    update = f'''{MARKER}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for MP48 fine-tail convergence; `PARTIAL` for `T13_FULL_THERMODYNAMIC_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The generated full gate now describes MP48 as a convergence pass for the independent harmonic lane, with fine-tail maximum `{fine_tail}` under the unchanged policy.
WHAT_REMAINS_OPEN: Ding material/PBTE equivalence, numeric `C_src`, source uncertainty, base-Phi SI mapping, `alpha_Phi_K`, bridge/beta, and physical EOS/transport/KMS/entropy remain open.
DEPENDENCY_UNLOCKED: None beyond the internal MP48 convergence lane.
STATUS: MP48 `{status}`; Full Topic 13 `{full_status}`.
WHAT_CHANGED: Removed stale “mesh no-go” wording from the full-gate generator and regenerated the gate/register/dependency artifacts.
EQUATION_OR_MAPPING: `C_src^mesh(T)=N_A/N_q*sum_(q,mu)c_mu(q,T)` remains a harmonic comparator and is not Ding `C_src`.
VERIFICATION: Stale-phrase scan is clean; MP48 acceptance remains false; no fit, target tuning, or Xie 2026 numeric holdout access occurred.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.
NEXT_ACTION: Obtain permitted same-regime Ding/PBTE evidence; do not promote the comparator.
CLAIM_BOUNDARY: Narrative synchronization only plus the existing internal harmonic convergence result; not Ding validation, alpha calibration, or Full Topic 13 closure.
EVIDENCE_HASHES: mesh `{hashes["mesh"]}`; acceptance `{hashes["acceptance"]}`; full gate `{hashes["full_gate"]}`; register `{hashes["register"]}`; dependency `{hashes["dependency"]}`.'''

    manifest = f'''## MP48 Full-Gate Narrative Drift Repair (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for harmonic fine-tail convergence; `PARTIAL` for Full Topic 13.
WHAT_IS_ACTUALLY_CLOSED: The full gate uses the current convergence-pass wording.
WHAT_REMAINS_OPEN: Ding-compatible `C_src`, material mapping, alpha, SI bridge, and physical transport closure.
STATUS: `{status}`; Full Topic 13 `{full_status}`.
VERIFICATION: Obsolete no-go phrase absent; acceptance contract still rejects MP48 for Full Topic 13.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.
NEXT_ACTION: Obtain accepted same-regime PBTE evidence.
CLAIM_BOUNDARY: Narrative drift repair only. Full gate SHA `{hashes["full_gate"]}`.'''

    current = f'''## Latest MP48 Full-Gate Narrative Drift Repair (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for MP48 convergence; `PARTIAL` for Full Topic 13.
WHAT_IS_ACTUALLY_CLOSED: MP48 is described as a convergence pass, not a mesh no-go.
WHAT_REMAINS_OPEN: Ding source acceptance, alpha, dimensional map, bridge/beta, and physical transport.
STATUS: `{status}`; Full Topic 13 `{full_status}`.
WHAT_CHANGED: Full-gate narrative and generated register were synchronized.
EQUATION_OR_MAPPING: Harmonic mesh sum only; no Ding relabeling.
VERIFICATION: Obsolete phrase scan clean; holdout and fit guards unchanged.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.
NEXT_ACTION: Obtain permitted same-regime PBTE evidence.
CLAIM_BOUNDARY: Comparator-only; not Ding validation or Full Topic 13 closure. Full gate `{hashes["full_gate"]}`.'''

    ledger = f'''## Topic 13 MP48 full-gate narrative drift repair

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: full-gate generator, Topic 13 full gate, major-result register, dependency gate, topic records
- verifier: stale phrase scan clean; MP48 `{status}`; Full Topic 13 `{full_status}`
- public-safety: `partial`
- result: corrected “mesh no-go” narrative to the current harmonic convergence-pass result without changing acceptance or claim boundary
- hashes: mesh `{hashes["mesh"]}`; acceptance `{hashes["acceptance"]}`; full gate `{hashes["full_gate"]}`; register `{hashes["register"]}`; dependency `{hashes["dependency"]}`
- remains: Ding C_src, material matching, alpha, SI bridge, beta, and physical transport/KMS/entropy
- next action: obtain permitted same-regime PBTE evidence
- commit/push action: no commit requested; retain scoped changes in the dirty worktree'''

    append_once(PATHS["update_log"], MARKER, update)
    append_once(PATHS["manifest"], "## MP48 Full-Gate Narrative Drift Repair (2026-08-13)", manifest)
    append_once(PATHS["current"], "## Latest MP48 Full-Gate Narrative Drift Repair (2026-08-13)", current)
    append_once(PATHS["ledger"], "## Topic 13 MP48 full-gate narrative drift repair", ledger)
    print(json.dumps({"status": status, "full_status": full_status, "hashes": hashes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
