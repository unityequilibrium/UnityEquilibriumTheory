"""Record the MP48 temperature-volume uncertainty boundary wave."""

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
    content = raw.rstrip(b"\r\n") + newline + body.rstrip("\r\n").replace("\n", newline.decode()).encode("utf-8") + newline
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def main() -> int:
    audit = digest("docs/core/07_artifacts/topic13/t13_mp48_temperature_volume_uncertainty_boundary_audit.json")
    package = digest("docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json")
    source_audit = digest("docs/core/07_artifacts/topic13/t13_mp48_independent_graphite_cv_audit.json")
    full = digest("docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json")
    register = digest("docs/core/07_artifacts/gates/uet_major_result_closure_register.json")
    dependency = digest("docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    integrity = digest("docs/core/07_artifacts/archive/uet_research_room_wave1_integrity.json")

    update = f"""### 2026-08-13 - MP48 temperature-volume uncertainty boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY.
WHAT_IS_ACTUALLY_CLOSED: The current MP48 route is closed as a scoped boundary: its room-temperature volume anchor and non-statistical display envelope cannot be promoted to source-grade, temperature-resolved volumetric c_v uncertainty.
WHAT_REMAINS_OPEN: Temperature-resolved graphite volume with uncertainty, source-grade statistical c_v uncertainty, Ding material/mode-resolved C_src, independent alpha_Phi_K, bridge/beta, physical EOS/transport/KMS/entropy, and dimensional mapping remain open. Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
DEPENDENCY_UNLOCKED: MP48 comparator-boundary reporting only; no Ding, alpha, Full Topic 13, Core, Gravity, transport, Galaxy, or external-validation unlock.
STATUS: PASS_SCOPED_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added the machine-readable boundary audit, full-gate projection, major-result registry entry, dependency synchronization, focused regression test, wave note, and manifest/log records.
EQUATION_OR_MAPPING: C_v^vol(T) = C_v^mol,cell(T) / V_mol,cell(T); the current comparator uses the room-temperature volume anchor as a declared fixed-volume approximation. Delta_Tq = Delta_u / C_v^vol(T) remains comparator-only.
VERIFICATION: Boundary checks pass; MP48 source audit and focused adjacent regression tests pass (8 passed). Full gate remains at the same 10 blockers, Wave 1 integrity is PASS_WITH_BLOCKED_LANES, and Xie 2026 was not accessed or consumed.
CONTROLLING_BLOCKER: temperature_resolved_graphite_volume_and_source_grade_c_v_uncertainty_missing.
NEXT_ACTION: Obtain a permitted same-state temperature-resolved graphite volume source with uncertainty or a source-backed equivalent; keep MP48 comparator-only and resolve alpha_Phi_K independently without the locked holdout.
CLAIM_BOUNDARY: Route-level source/uncertainty boundary only. This is not Ding PBTE C_src, an UET energy anchor, an alpha_Phi_K calibration, a TTG prediction, physical transport validation, external validation, Core closure, or global UET closure.
EVIDENCE_HASHES: boundary audit {audit}; source package {package}; source audit {source_audit}; full gate {full}; register {register}; dependency {dependency}; integrity {integrity}.
"""

    manifest = f"""## MP48 Temperature-Volume Uncertainty Boundary (2026-08-13)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY.
WHAT_IS_ACTUALLY_CLOSED: The MP48 room-temperature volume anchor and non-statistical display envelope are bounded to comparator use; they are not a source-grade temperature-resolved volumetric c_v uncertainty contract.
WHAT_REMAINS_OPEN: Temperature-resolved volume uncertainty, source statistical c_v uncertainty, Ding C_src/material mapping, alpha_Phi_K, and Full Topic 13 closure remain open.
DEPENDENCY_UNLOCKED: MP48 comparator-boundary reporting only; no downstream Core or Gravity unlock.
STATUS: PASS_SCOPED_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added the boundary audit, full-gate projection, registry/dependency links, focused test, and wave note.
EQUATION_OR_MAPPING: C_v^vol(T) = C_v^mol,cell(T) / V_mol,cell(T); fixed room-temperature volume is an explicit comparator approximation.
VERIFICATION: temperature_resolved_volume_status is OPEN; source statistical uncertainty is NOT_REPORTED_BY_DEPOSIT; combined display envelope is NON_STATISTICAL_DISPLAY_ONLY; focused tests pass (8 passed); holdout remains unconsumed.
CONTROLLING_BLOCKER: temperature_resolved_graphite_volume_and_source_grade_c_v_uncertainty_missing.
NEXT_ACTION: Obtain a permitted same-state temperature-resolved volume source with uncertainty and rerun the contract.
CLAIM_BOUNDARY: Comparator source/uncertainty boundary only; not Ding C_src, alpha calibration, TTG prediction, external validation, or Core closure.
EVIDENCE_HASHES: boundary audit {audit}; package {package}; full gate {full}; register {register}; dependency {dependency}; integrity {integrity}.
"""

    ledger = f"""## Topic 13 MP48 temperature-volume uncertainty boundary

- area: research-core (secondary: result-artifacts)
- workspace: docs/topics/0.13_Thermodynamic_Bridge
- files/artifacts: boundary audit, full-gate generator integration, closure register/dependency sync, focused test, wave note, manifest, update log
- verifier: PASS_SCOPED_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY_NO_GO; focused tests 8 passed; Wave 1 integrity PASS_WITH_BLOCKED_LANES
- public-safety: partial
- result: MP48 temperature-resolved source-grade volumetric c_v uncertainty is closed as a scoped route boundary; comparator-only status is preserved
- hashes: boundary {audit}; source package {package}; source audit {source_audit}; full {full}; register {register}; dependency {dependency}; integrity {integrity}
- remains: temperature-resolved volume uncertainty, source statistical c_v uncertainty, Ding C_src/material mapping, alpha_Phi_K, bridge/beta, physical EOS/transport/KMS/entropy, and dimensional mapping
- next action: obtain a permitted same-state temperature-resolved volume source with uncertainty; keep MP48 comparator-only
- commit/push action: no commit requested; retain scoped changes identifiable in the dirty worktree
"""

    append_once(
        "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md",
        "### 2026-08-13 - MP48 temperature-volume uncertainty boundary",
        update,
    )
    append_once(
        "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md",
        "## MP48 Temperature-Volume Uncertainty Boundary (2026-08-13)",
        manifest,
    )
    append_once("WORK_LEDGER/2026/2026-08-13.md", "## Topic 13 MP48 temperature-volume uncertainty boundary", ledger)
    print(
        f"recorded hashes: audit={audit} full={full} register={register} "
        f"dependency={dependency} integrity={integrity}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
