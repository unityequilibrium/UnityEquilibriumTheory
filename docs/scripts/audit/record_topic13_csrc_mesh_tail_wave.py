"""Record the Topic 13 C_src mesh-tail extension without promoting claims."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WAVE_DATE = "2026-08-23"
MARKER = "### 2026-08-23 - C_src mesh-tail extension (T13-171)"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def append_once(relative: str, marker: str, body: str) -> None:
    path = ROOT / relative
    raw = path.read_bytes() if path.is_file() else b""
    marker_bytes = marker.encode("utf-8")
    if marker_bytes in raw:
        return
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    rendered = body.strip().replace("\n", newline.decode()).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw.rstrip(b"\r\n") + newline + rendered + newline)


def main() -> int:
    package = digest(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
        "t13_calorine_zenodo_nep_bte_reproduction_source_package.json"
    )
    audit = digest("docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json")
    decomposition = digest(
        "docs/core/artifacts/t13_csrc_thermodynamic_transport_regime_decomposition_audit.json"
    )
    full_gate = digest(
        "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
        "topic13_full_thermodynamic_bridge_core_ready_gate.json"
    )
    matrix = digest("docs/core/artifacts/t13_topic13_closure_matrix.json")
    register = digest("docs/core/artifacts/uet_major_result_closure_register.json")
    dependency = digest("docs/core/artifacts/uet_major_result_dependency_unlock_gate.json")
    summary = digest(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
        "t13_calorine_zenodo_pbte_run_m12x12x6_summary.json"
    )
    wave = digest("docs/topics/0.13_Thermodynamic_Bridge/RESEARCH_WAVE_20260823_C_SRC_MESH_12.md")

    update = f"""{MARKER}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for the numerical mesh-tail sub-lane of `T13_C_SRC_THERMODYNAMIC_TRANSPORT_REGIME_DECOMPOSITION`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: A fifth `12x12x6` q-mesh run reuses the hash-locked `4x4x2` force-constant state. The latest `10x10x5 -> 12x12x6` C_src tail is quantified at `0.106554%`, while the in-plane RTA kappa tail is `12.851119%`.
WHAT_REMAINS_OPEN: Ding-compatible material/state mapping, source-grade uncertainty, accepted Ding `C_src`, independent `alpha_Phi_K`, dimensional Phi mapping, physical transport/KMS/entropy closure, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Numerical C_src mesh-tail evidence only; no Ding, alpha, physical transport, Core, Gravity, Galaxy, or external-validation unlock.
STATUS: `PASS_SCOPED_C_SRC_THERMODYNAMIC_TRANSPORT_DECOMPOSITION`; `claim_promotion=false`; `holdout_accessed=false`.
WHAT_CHANGED: Added the persistent `12x12x6` summary and HDF5 output, regenerated the Calorine source package and audit, and refreshed the full gate, closure matrix, major-result register, and dependency gate.
EQUATION_OR_MAPPING: `C_src(T,V) = (partial u_ph / partial T)_V = V^-1 sum_mu c_mu(T,V)`; `Delta_Tq = Delta_u_ph / C_src`; `Delta_Tq = alpha_Phi_K * Delta_Phi` remains uncalibrated.
VERIFICATION: Source hashes and force-constant identity remain fixed; the new candidate mesh preflight passes; no fit, target tuning, alpha calibration, threshold change, or Xie 2026 holdout access occurred.
CONTROLLING_BLOCKER: `ding_C_src_mode_state_and_source_grade_uncertainty_missing` controls this decomposition; `alpha_Phi_K_independent_calibration_missing` and Ding-compatible `C_src` remain independent full-topic controllers.
NEXT_ACTION: Obtain an authorized Ding numeric package or accepted same-regime PBTE reproduction with source-grade uncertainty and material/state mapping; keep RTA transport outside the Phi calibration path.
CLAIM_BOUNDARY: Numerical convergence sub-lane only; not Ding-regime validation, source-grade uncertainty closure, alpha calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_PATHS: `docs/topics/0.13_Thermodynamic_Bridge/RESEARCH_WAVE_20260823_C_SRC_MESH_12.md`; `docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json`; `docs/core/artifacts/t13_csrc_thermodynamic_transport_regime_decomposition_audit.json`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`.
EVIDENCE_HASHES: package `{package}`; reproduction audit `{audit}`; decomposition `{decomposition}`; full gate `{full_gate}`; matrix `{matrix}`; register `{register}`; dependency `{dependency}`; mesh summary `{summary}`; wave brief `{wave}`.
"""
    manifest = f"""## C_src mesh-tail extension ({WAVE_DATE})

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the numerical mesh-tail sub-lane of T13_C_SRC_THERMODYNAMIC_TRANSPORT_REGIME_DECOMPOSITION.
WHAT_IS_ACTUALLY_CLOSED: The Calorine candidate now includes a persistent 12x12x6 q-mesh summary using the existing 4x4x2 force-constant state. The 10x10x5 -> 12x12x6 C_src tail is 0.106554%, while the in-plane RTA kappa tail is 12.851119%.
WHAT_REMAINS_OPEN: Ding-compatible material/state mapping, source-grade uncertainty, accepted Ding C_src, alpha_Phi_K, dimensional Phi mapping, and full physical transport/KMS/entropy closure.
DEPENDENCY_UNLOCKED: Numerical C_src convergence evidence only; no Full Topic 13, Core, Gravity, transport, Galaxy, alpha, or external-validation unlock.
STATUS: PASS_SCOPED_C_SRC_THERMODYNAMIC_TRANSPORT_DECOMPOSITION.
WHAT_CHANGED: Added the 12x12x6 run summary and kappa payload, regenerated the source package and audit, and refreshed full-gate/closure/dependency projections.
EQUATION_OR_MAPPING: C_src(T,V) = (partial u_ph / partial T)_V = V^-1 sum_mu c_mu(T,V); Delta_Tq = Delta_u_ph / C_src(T). No Phi or alpha mapping is emitted.
VERIFICATION: Fixed force-constant identity, SI units, candidate mesh preflight, no-fit, and no-holdout checks pass.
CONTROLLING_BLOCKER: ding_C_src_mode_state_and_source_grade_uncertainty_missing.
NEXT_ACTION: Acquire authorized Ding numeric C_src or an accepted same-regime PBTE package with material/state mapping and source-grade uncertainty.
CLAIM_BOUNDARY: Numerical convergence sub-lane only; not Ding-equivalent, not source-grade uncertainty closure, not calibration, not prediction, and not Full Topic 13 closure.
EVIDENCE_PATHS: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_calorine_zenodo_pbte_run_m12x12x6_summary.json`; `docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json`; `docs/core/artifacts/t13_csrc_thermodynamic_transport_regime_decomposition_audit.json`.
EVIDENCE_HASHES: package `{package}`; audit `{audit}`; decomposition `{decomposition}`; full gate `{full_gate}`.
"""
    ledger = f"""## Topic 13 C_src mesh-tail extension

- area: research-core
- workspace: docs/topics/0.13_Thermodynamic_Bridge and docs/core
- files or artifacts changed: 12x12x6 PBTE summary/HDF5 output, Calorine source package and audit, C_src/transport decomposition audit, full gate, closure matrix, major-result register, dependency gate, research-wave brief, Topic 13 update log, and data manifest
- verifier or audit run: Calorine record wave; C_src/transport decomposition; full bridge gate; closure matrix; major-result closure/dependency audits
- public-safety: partial
- remains uncommitted, private, or unsafe to publish: no holdout payload; candidate remains non-Ding and source-grade uncertainty remains open
- next commit, push, PR, or manifest action: commit this scoped mesh-tail wave; next controller is Ding-compatible source/material-state mapping plus source-grade uncertainty, while alpha_Phi_K remains independently open
- evidence hashes: package `{package}`; audit `{audit}`; decomposition `{decomposition}`; full `{full_gate}`; matrix `{matrix}`; register `{register}`; dependency `{dependency}`
"""

    append_once("docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md", MARKER, update)
    append_once("docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md", f"## C_src mesh-tail extension ({WAVE_DATE})", manifest)
    append_once("WORK_LEDGER/2026/2026-08-23.md", "## Topic 13 C_src mesh-tail extension", ledger)
    print("PASS_RECORDED_TOPIC13_C_SRC_MESH_TAIL_WAVE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
