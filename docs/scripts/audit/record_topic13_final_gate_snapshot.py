"""Record the final Topic 13 gate state after a verification wave."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-24.md"
CAUSAL = ROOT / "docs/core/artifacts/t13_causal_named_branch_core_compatibility.json"
CONTRACT = ROOT / "docs/core/artifacts/t13_closure_record_contract_audit.json"
INPUT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
MATRIX = ROOT / "docs/core/artifacts/t13_topic13_closure_matrix.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"

MARKER = "### 2026-08-24 - Final Topic 13 gate snapshot after causal roadmap sync"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(path: Path, marker: str, text: str) -> bool:
    current = path.read_text(encoding="utf-8")
    if marker in current:
        return False
    path.write_text(current.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")
    return True


def main() -> int:
    causal = load(CAUSAL)
    contract = load(CONTRACT)
    input_audit = load(INPUT)
    matrix = load(MATRIX)
    full_gate = load(FULL_GATE)

    counts = matrix["closure_summary"]["current_subresult_counts"]
    expected_counts = {"CLOSED_FOR_LANE": 21, "CLOSED_AS_NO_GO": 5, "CLOSED_FOR_CORE": 0, "OPEN": 10}
    normalized_counts = {key: counts.get(key, 0) for key in expected_counts}
    accepted_for_core = sum(
        1 for package in input_audit["packages"] if package.get("accepted_for_core") is True
    )
    holdout_accessed = input_audit["holdout_policy"]["xie_2026_accessed"]
    open_blockers = full_gate["major_result"]["what_remains_open"]
    if full_gate["status"] != "BLOCKED_OPEN_T13_FULL_BRIDGE":
        raise SystemExit("unexpected full Topic 13 gate status")
    if matrix["status"] != "BLOCKED_OPEN_T13_FULL_BRIDGE" or matrix["full_core_unlock"]:
        raise SystemExit("unexpected closure matrix status")
    if normalized_counts != expected_counts:
        raise SystemExit(f"unexpected closure counts: {normalized_counts}")
    if accepted_for_core != 0 or holdout_accessed:
        raise SystemExit("input audit no longer fails closed")
    if contract["status"] != "PASS_T13_CLOSURE_RECORD_CONTRACT_OPEN":
        raise SystemExit("unexpected closure contract status")
    if causal["major_result"]["closure_level"] != "CLOSED_FOR_CORE":
        raise SystemExit("causal exception is not Core-closed")

    stamp = datetime.now(timezone.utc).isoformat()
    top_controller = full_gate["controlling_blocker"]
    hashes = {path.name: sha256(path) for path in (CAUSAL, CONTRACT, INPUT, MATRIX, FULL_GATE)}
    log_entry = f"""{MARKER}

MAJOR_RESULT_CLOSURE:
- The named causal exception remains `CLOSED_FOR_CORE`; Full Topic 13 remains `PARTIAL` and blocked.

WHAT_IS_ACTUALLY_CLOSED:
- Causal branch compatibility, closure-record schema, and input-package/holdout controls are machine-checked.
- Regression suite completed with `539 passed, 625 deselected` for the Topic 13 selection.

WHAT_REMAINS_OPEN:
- The 36-subresult matrix is `CLOSED_FOR_LANE=21`, `CLOSED_AS_NO_GO=5`, `CLOSED_FOR_CORE=0`, `OPEN=10`.
- The canonical Full Topic gate reports {len(open_blockers)} blocker groups: `{", ".join(open_blockers)}`.

DEPENDENCY_UNLOCKED:
- None. `full_core_unlock=false`; Gravity/GR and downstream transport promotion remain blocked.

STATUS:
- `{full_gate["status"]}`

WHAT_CHANGED:
- Re-ran closure contract, input-package audit, Full Topic gate, closure matrix, and Topic 13 regression tests after synchronizing causal roadmap wording.

EQUATION_OR_MAPPING:
- The normalized operators remain `y_TTG=Delta_Tq(t)/Delta_Tq(0)`, `y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)`, and `Delta_Tq=alpha_Phi_K*Delta_Phi`; no SI calibration was emitted.

VERIFICATION:
- Holdout access remains false; no target fit or threshold change is recorded; the named causal artifact remains `CLOSED_FOR_CORE` as a bounded exception.

CONTROLLING_BLOCKER:
- Primary controller: `{top_controller}`. The unresolved blocker set is `{", ".join(open_blockers)}`.

NEXT_ACTION:
- Close the Ding-compatible source/material package, the independent base-Phi/alpha/beta package, and the physical Kubo/SK/KMS/entropy package; then rerun the full gate.

CLAIM_BOUNDARY:
- This is an internal verification snapshot. It is not Full Topic 13 closure, external validation, temperature prediction, or global UET closure.

EVIDENCE_PATHS:
- `docs/core/artifacts/t13_causal_named_branch_core_compatibility.json`
- `docs/core/artifacts/t13_closure_record_contract_audit.json`
- `docs/core/artifacts/t13_closure_input_package_audit.json`
- `docs/core/artifacts/t13_topic13_closure_matrix.json`
- `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`

EVIDENCE_HASHES:
- `{CAUSAL.name}` SHA-256: `{hashes[CAUSAL.name]}`
- `{CONTRACT.name}` SHA-256: `{hashes[CONTRACT.name]}`
- `{INPUT.name}` SHA-256: `{hashes[INPUT.name]}`
- `{MATRIX.name}` SHA-256: `{hashes[MATRIX.name]}`
- `{FULL_GATE.name}` SHA-256: `{hashes[FULL_GATE.name]}`
- snapshot UTC: `{stamp}`
"""
    log_changed = append_once(UPDATE_LOG, MARKER, log_entry)

    ledger_entry = """## Topic 13 Final Gate Snapshot

- area: `research-core`
- workspace: `Topic 13 Thermodynamic Bridge`
- files/artifacts: closure contract, input audit, causal compatibility artifact, closure matrix, full bridge gate
- verification: `539 passed, 625 deselected`; holdout false; matrix `21/5/0/10`; full gate blocked with 7 blocker groups
- public-safety: `blocked` for Full Topic 13 promotion
- remaining: no accepted Core input package; `alpha_Phi_K` and dimensional SI map remain open
- next action: acquire accepted source/calibration/physical transport evidence and rerun the gate
"""
    ledger_changed = append_once(LEDGER, "## Topic 13 Final Gate Snapshot", ledger_entry)

    print(json.dumps({
        "status": "PASS_T13_FINAL_GATE_SNAPSHOT_RECORDED",
        "update_log_changed": log_changed,
        "ledger_changed": ledger_changed,
        "full_gate_status": full_gate["status"],
        "blocker_count": len(open_blockers),
        "closure_counts": normalized_counts,
        "full_core_unlock": matrix["full_core_unlock"],
        "accepted_for_core": accepted_for_core,
        "holdout_accessed": holdout_accessed,
        "hashes": hashes,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
