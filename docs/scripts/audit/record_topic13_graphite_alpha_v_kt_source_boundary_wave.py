"""Record the graphite alpha_V/K_T source compatibility boundary wave."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def append_once(relative: str, marker: str, body: str) -> None:
    path = ROOT / relative
    raw = path.read_bytes() if path.exists() else b""
    if marker.encode("utf-8") in raw:
        return
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    text = body.rstrip("\r\n").replace("\n", newline.decode())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw.rstrip(b"\r\n") + newline + text.encode("utf-8") + newline)


def main() -> int:
    audit = digest("docs/core/07_artifacts/topic13/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json")
    full = digest("docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json")
    register = digest("docs/core/07_artifacts/gates/uet_major_result_closure_register.json")
    dependency = digest("docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    integrity = digest("docs/core/07_artifacts/archive/uet_research_room_wave1_integrity.json")

    update = f"""### 2026-08-13 - Graphite alpha_V/K_T source compatibility boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY.
WHAT_IS_ACTUALLY_CLOSED: The current archived graphite source inventory cannot form a same-state, same-grade alpha_V/K_T pair with source-grade uncertainty for the Cp-to-Cv correction. Individual alpha_V and K_T comparator lanes remain separate.
WHAT_REMAINS_OPEN: Same-state alpha_V/K_T with uncertainty, density uncertainty, Ding material mapping, source-grade c_v uncertainty, independent alpha_Phi_K, bridge/beta, physical EOS/transport/KMS/entropy, and dimensional mapping remain open. Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
DEPENDENCY_UNLOCKED: Current source-pair inventory boundary only; no Cp-to-Cv input closure, Ding C_src, alpha, Full Topic 13, Core, Gravity, transport, Galaxy, or external-validation unlock.
STATUS: PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added the source compatibility audit, full-gate projection, major-result registry/dependency link, focused regression test, wave note, manifest record, and update-log record.
EQUATION_OR_MAPPING: c_p^V - c_v^V = T * alpha_V^2 * K_T; c_v^V = rho * c_p - T * alpha_V^2 * K_T. No numeric correction is emitted because the current inputs are not a same-state pair.
VERIFICATION: Source-compatibility checks pass; focused tests pass (10 passed); full gate retains the same 10 blockers; Wave 1 integrity is PASS_WITH_BLOCKED_LANES; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: same_grade_alpha_V_and_K_T_missing.
NEXT_ACTION: Acquire a permitted same-specimen or explicitly state-matched alpha_V and isothermal K_T source with uncertainty and Ding-regime mapping; do not combine current comparator values by assumption.
CLAIM_BOUNDARY: Route-level source compatibility boundary only. This is not a same-state correction, Ding validation, UET calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: boundary audit {audit}; full gate {full}; register {register}; dependency {dependency}; integrity {integrity}.
"""

    manifest = f"""## Graphite alpha_V/K_T Source Compatibility Boundary (2026-08-13)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY.
WHAT_IS_ACTUALLY_CLOSED: The current source inventory cannot form a same-state, same-grade alpha_V/K_T pair with source-grade uncertainty for Cp-to-Cv correction.
WHAT_REMAINS_OPEN: Same-state alpha_V/K_T with uncertainty, density, Ding mapping, source-grade c_v uncertainty, alpha_Phi_K, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Current source-pair inventory boundary only; no downstream Core or Gravity unlock.
STATUS: PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added the compatibility audit, full-gate projection, registry/dependency links, focused test, and wave note.
EQUATION_OR_MAPPING: c_p^V - c_v^V = T * alpha_V^2 * K_T; no numeric correction is emitted.
VERIFICATION: NIST K_T is absent; Hanfland same-state alpha_V is absent; Bosak is dynamic elastic; TPG is not same specimen/temperature; Nelson-Riley lacks row-level statistical uncertainty; focused tests pass (10 passed).
CONTROLLING_BLOCKER: same_grade_alpha_V_and_K_T_missing.
NEXT_ACTION: Obtain a permitted same-state source pair with uncertainty and Ding-regime mapping.
CLAIM_BOUNDARY: Source compatibility boundary only; not thermodynamic correction, Ding C_src, alpha calibration, TTG prediction, external validation, or Core closure.
EVIDENCE_HASHES: boundary audit {audit}; full gate {full}; register {register}; dependency {dependency}; integrity {integrity}.
"""

    ledger = f"""## Topic 13 graphite alpha_V/K_T source compatibility boundary

- area: research-core (secondary: result-artifacts)
- workspace: docs/topics/0.13_Thermodynamic_Bridge
- files/artifacts: source compatibility audit, full-gate integration, closure register/dependency sync, focused test, wave note, manifest, update log
- verifier: PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY_NO_GO; focused tests 10 passed; Wave 1 integrity PASS_WITH_BLOCKED_LANES
- public-safety: partial
- result: current alpha_V/K_T inventory is closed as a scoped no-go for same-state Cp-to-Cv correction; no numeric correction is emitted
- hashes: boundary {audit}; full {full}; register {register}; dependency {dependency}; integrity {integrity}
- remains: same-state alpha_V/K_T with uncertainty, density, Ding mapping, c_v uncertainty, alpha_Phi_K, bridge/beta, transport/KMS/entropy, and dimensional mapping
- next action: acquire a permitted same-state alpha_V/K_T source pair with uncertainty and Ding-regime mapping
- commit/push action: no commit requested; retain scoped changes identifiable in the dirty worktree
"""

    append_once(
        "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md",
        "### 2026-08-13 - Graphite alpha_V/K_T source compatibility boundary",
        update,
    )
    append_once(
        "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md",
        "## Graphite alpha_V/K_T Source Compatibility Boundary (2026-08-13)",
        manifest,
    )
    append_once(
        "WORK_LEDGER/2026/2026-08-13.md",
        "## Topic 13 graphite alpha_V/K_T source compatibility boundary",
        ledger,
    )
    print(
        f"recorded hashes: audit={audit} full={full} register={register} "
        f"dependency={dependency} integrity={integrity}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
