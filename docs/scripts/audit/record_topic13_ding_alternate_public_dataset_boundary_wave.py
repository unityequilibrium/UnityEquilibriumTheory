"""Record the Ding alternate public dataset source boundary wave."""

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
    path.parent.mkdir(parents=True, exist_ok=True)
    content = raw.rstrip(b"\r\n") + newline + body.rstrip("\r\n").replace("\n", newline.decode()).encode("utf-8") + newline
    path.write_bytes(content)


def main() -> int:
    audit = digest("docs/core/07_artifacts/topic13/t13_ding_alternate_public_dataset_discovery_boundary_audit.json")
    package = digest("docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_ding_alternate_public_dataset_discovery_package.json")
    full = digest("docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json")
    register = digest("docs/core/07_artifacts/gates/uet_major_result_closure_register.json")
    dependency = digest("docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    integrity = digest("docs/core/07_artifacts/archive/uet_research_room_wave1_integrity.json")

    update = f"""### 2026-08-13 - Ding alternate public dataset boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_DING_ALTERNATE_PUBLIC_DATASET_DISCOVERY_BOUNDARY.
WHAT_IS_ACTUALLY_CLOSED: The current two-route public inventory is bounded: ISIS exposes a Bi2Te3/Graphite nanocomposite PDOS route and Caltech exposes graphite c-axis mean-free-path spectra. Neither satisfies the Ding mode-resolved volumetric C_src(T) contract.
WHAT_REMAINS_OPEN: Authorized Ding numeric C_src or accepted same-regime reproduction, source-grade uncertainty/convergence, material mapping, independent alpha_Phi_K, bridge/beta, EOS/transport/KMS/entropy, and dimensional mapping remain open. Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
DEPENDENCY_UNLOCKED: Public source-discovery boundary only; no C_src, alpha, Full Topic 13, Core, Gravity, transport, Galaxy, or external-validation unlock.
STATUS: PASS_SCOPED_DING_ALTERNATE_PUBLIC_DATASET_BOUNDARY_NO_GO.
WHAT_CHANGED: Added the alternate-route package, audit, full-gate projection, registry/dependency links, focused test, wave note, manifest, and update-log record.
EQUATION_OR_MAPPING: Required route remains C_src(T)=sum_mu c_mu(T); Delta_Tq=Delta_u_ph/C_src(T). No numeric C_src or alpha_Phi_K is emitted.
VERIFICATION: Candidate provenance and mismatch checks pass; no candidate payload was imported; no fit or calibration was performed; holdout remains unconsumed. Full gate retains the same 10 blockers.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Obtain an authorized Ding numeric package or permitted same-regime PBTE reproduction with mode-resolved C_src(T), SI units, uncertainty, convergence, and material-state mapping.
CLAIM_BOUNDARY: Source-discovery boundary only; not Ding validation, alpha calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: package {package}; boundary audit {audit}; full gate {full}; register {register}; dependency {dependency}; integrity {integrity}.
"""

    manifest = f"""## Ding Alternate Public Dataset Boundary (2026-08-13)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_DING_ALTERNATE_PUBLIC_DATASET_DISCOVERY_BOUNDARY.
WHAT_IS_ACTUALLY_CLOSED: The current public candidate inventory is bounded. ISIS is a Bi2Te3/Graphite nanocomposite PDOS route and Caltech is a graphite c-axis mean-free-path route; neither supplies Ding-compatible mode-resolved volumetric C_src(T).
WHAT_REMAINS_OPEN: Authorized Ding numeric C_src or accepted same-regime reproduction, material mapping, source-grade uncertainty/convergence, alpha_Phi_K, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Public route inventory boundary only; no downstream Core, Gravity, transport, or Galaxy unlock.
STATUS: PASS_SCOPED_DING_ALTERNATE_PUBLIC_DATASET_BOUNDARY_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added the candidate package, audit, full-gate projection, registry/dependency links, focused test, and wave note.
EQUATION_OR_MAPPING: C_src(T)=sum_mu c_mu(T); Delta_Tq=Delta_u_ph/C_src(T). No numeric C_src or alpha is emitted.
VERIFICATION: ISIS public RAW/Nexus metadata and Caltech public MFP metadata are recorded, but neither route passes material/observable/regime acceptance; no payload import, fitting, or holdout use occurred.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Acquire an authorized Ding numeric package or accepted same-regime PBTE reproduction with mode-resolved rows and source-grade uncertainty.
CLAIM_BOUNDARY: Source-discovery boundary only; not C_src evidence, alpha calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: package {package}; boundary audit {audit}; full gate {full}; register {register}; dependency {dependency}; integrity {integrity}.
"""

    ledger = f"""## Topic 13 Ding alternate public dataset boundary

- area: research-core (secondary: result-artifacts)
- workspace: docs/topics/0.13_Thermodynamic_Bridge
- files/artifacts: alternate source package, source-discovery audit, full-gate integration, closure register/dependency sync, focused test, wave note, manifest, update log
- verifier: PASS_SCOPED_DING_ALTERNATE_PUBLIC_DATASET_BOUNDARY_NO_GO; no candidate payload imported; no fit/calibration; holdout unconsumed
- public-safety: partial
- result: current public candidate inventory is closed as a route-level boundary; neither candidate satisfies Ding mode-resolved C_src(T)
- hashes: package {package}; boundary {audit}; full {full}; register {register}; dependency {dependency}; integrity {integrity}
- remains: authorized Ding C_src or accepted independent reproduction, material mapping, uncertainty/convergence, alpha_Phi_K, bridge/beta, EOS/transport/KMS/entropy, and dimensional mapping
- next action: obtain a permitted Ding-compatible numeric package or same-regime PBTE reproduction
- commit/push action: no commit requested; retain scoped changes identifiable in the dirty worktree
"""

    append_once("docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md", "### 2026-08-13 - Ding alternate public dataset boundary", update)
    append_once("docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md", "## Ding Alternate Public Dataset Boundary (2026-08-13)", manifest)
    append_once("WORK_LEDGER/2026/2026-08-13.md", "## Topic 13 Ding alternate public dataset boundary", ledger)
    print(f"recorded hashes: package={package} audit={audit} full={full} register={register} dependency={dependency} integrity={integrity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
