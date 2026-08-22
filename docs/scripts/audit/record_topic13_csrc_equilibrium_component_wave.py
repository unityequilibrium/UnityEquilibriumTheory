"""Record the Topic 13 equilibrium C_src component wave."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DAY = "2026-08-23"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def append_once(relative: str, marker: str, body: str) -> None:
    path = ROOT / relative
    raw = path.read_bytes() if path.exists() else b""
    if marker.encode("utf-8") in raw:
        return
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = body.rstrip("\r\n").replace("\n", newline.decode()).encode("utf-8")
    path.write_bytes(raw.rstrip(b"\r\n") + newline + rendered + newline)


def main() -> int:
    component = digest("docs/core/artifacts/t13_csrc_equilibrium_component_acceptance_audit.json")
    reproduction = digest("docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json")
    state = digest("docs/core/artifacts/t13_calorine_state_uncertainty_decomposition_audit.json")
    isotope = digest("docs/core/artifacts/t13_calorine_isotope_mass_sensitivity_audit.json")
    model = digest("docs/core/artifacts/t13_calorine_model_form_state_spread_comparison_audit.json")
    full_gate = digest("docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json")
    matrix = digest("docs/core/artifacts/t13_topic13_closure_matrix.json")
    register = digest("docs/core/artifacts/uet_major_result_closure_register.json")
    dependency = digest("docs/core/artifacts/uet_major_result_dependency_unlock_gate.json")

    wave = f"""# Research Wave: Topic 13 Equilibrium C_src Component ({DAY})

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE
WHAT_IS_ACTUALLY_CLOSED: T13_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY. The candidate equilibrium C_src denominator is separated from the transport operator under the fixed-volume phonon identity. SI C_src rows at 200, 250, and 300 K, the 10x10x5 to 12x12x6 mesh tail, natural-isotope mass sensitivity, and cross-model/state sensitivity are hash-linked. The qualified global relative sensitivity envelope is 0.044805097064529766 and is explicitly not a standard uncertainty.
WHAT_REMAINS_OPEN: Ding numeric C_src or an accepted same-regime reproduction, Ding TTG material/state mapping, source-grade C_src uncertainty, c_v source uncertainty, and independent alpha_Phi_K remain open. EOS/transport/KMS/entropy and the dimensional Phi map remain open at Full Topic 13 level.
DEPENDENCY_UNLOCKED: Candidate equilibrium C_src component and qualified sensitivity lane only; no Ding source gate, alpha_Phi_K, Phi map, physical transport, Core, Gravity, or external-validation unlock.
STATUS: PASS_SCOPED_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added a machine-readable component acceptance audit, linked it into the full Topic 13 source-package lane as a scoped closure, added a major-result register entry, and retained the strict Ding acceptance contract unchanged.
EQUATION_OR_MAPPING: C_src(T,V) = (partial u_ph / partial T)_V = V^-1 sum_mu c_mu(T,V); Delta_Tq = Delta_u_ph / C_src(T,V). The UET measurement bridge Delta_Tq = alpha_Phi_K * Delta_Phi remains open.
VERIFICATION: Source package hash, SI units, fixed-volume identity, positive C_src rows, latest mesh preflight, no-fit/no-target/no-holdout controls, natural-isotope sensitivity, cross-model sensitivity, and material non-equivalence boundary pass. Xie 2026 remains locked and unconsumed.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing; this scoped component does not satisfy the strict Ding source gate.
NEXT_ACTION: Obtain an authorized Ding numeric package or accepted same-regime PBTE reproduction with material/state mapping and source-grade uncertainty; keep the component outside alpha_Phi_K calibration.
CLAIM_BOUNDARY: Candidate equilibrium C_src component only; not Ding TTG equivalence, not source-grade uncertainty, not alpha_Phi_K calibration, not a Phi prediction, not transport validation, and not Full Topic 13 closure.
EVIDENCE_HASHES: component {component}; reproduction {reproduction}; state {state}; isotope {isotope}; model {model}; full gate {full_gate}; matrix {matrix}; register {register}; dependency {dependency}.
"""

    update = f"""### {DAY} - Equilibrium C_src component acceptance

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY.
WHAT_IS_ACTUALLY_CLOSED: The candidate equilibrium C_src denominator, SI rows, fixed-volume identity, q-mesh tail, natural-isotope sensitivity, and qualified cross-model/state sensitivity envelope are now one machine-readable result. The 0.044805097064529766 global envelope is a max sensitivity bound, not a standard uncertainty.
WHAT_REMAINS_OPEN: Strict Ding C_src acceptance, material/state mapping to the TTG regime, source-grade uncertainty, c_v uncertainty, and independent alpha_Phi_K remain open.
DEPENDENCY_UNLOCKED: Equilibrium C_src component lane only; no Full Topic 13 or downstream unlock.
STATUS: PASS_SCOPED_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY.
WHAT_CHANGED: Added and verified the component audit; full gate, closure matrix, register, and dependency projection now expose the lane without changing the eight Full Topic 13 blockers.
EQUATION_OR_MAPPING: C_src(T,V) = (partial u_ph / partial T)_V = V^-1 sum_mu c_mu(T,V); Delta_Tq = Delta_u_ph / C_src(T,V). No Phi or alpha calibration is inferred.
VERIFICATION: Hash-linked source inputs, SI rows, fixed-volume identity, mesh convergence, sensitivity separation, no-fit, and holdout isolation pass.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Acquire a permitted Ding-compatible numeric source or accepted same-regime PBTE reproduction with source-grade uncertainty and material/state mapping.
CLAIM_BOUNDARY: Component comparator only; not Ding validation, not source-grade uncertainty closure, not alpha_Phi_K, not prediction, and not Full Topic 13 closure.
EVIDENCE_HASHES: component {component}; full gate {full_gate}; matrix {matrix}; register {register}; dependency {dependency}.
"""

    manifest = f"""## Equilibrium C_src component acceptance ({DAY})

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY.
WHAT_IS_ACTUALLY_CLOSED: Candidate equilibrium C_src rows and qualified sensitivity reporting are hash-linked and separated from transport and Phi calibration.
WHAT_REMAINS_OPEN: Ding source acceptance, material/state equivalence, source-grade uncertainty, alpha_Phi_K, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Equilibrium C_src component lane only.
STATUS: PASS_SCOPED_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY.
WHAT_CHANGED: Added the component acceptance audit and full-gate/register/dependency projections.
EQUATION_OR_MAPPING: C_src(T,V) = (partial u_ph / partial T)_V; Delta_Tq = Delta_u_ph / C_src(T,V).
VERIFICATION: Source hashes, units, convergence, qualified sensitivity separation, no-fit, and no-holdout checks pass.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Obtain an authorized Ding numeric package or accepted same-regime PBTE reproduction with material/state mapping and source-grade uncertainty.
CLAIM_BOUNDARY: Candidate component only; no Ding equivalence, alpha calibration, prediction, or Full Topic 13 closure.
EVIDENCE_HASHES: component {component}; full gate {full_gate}; matrix {matrix}.
"""

    ledger = f"""## Topic 13 equilibrium C_src component acceptance

- area: research-core
- workspace: docs/topics/0.13_Thermodynamic_Bridge and docs/core
- files/artifacts: equilibrium C_src component audit, full gate, closure matrix, major-result register, dependency gate, wave note, update log, and data manifest
- verifier: PASS_SCOPED_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY; qualified global sensitivity envelope 0.044805097064529766
- public-safety: partial
- result: equilibrium component closed for lane; strict Ding source and Full Topic 13 remain blocked
- remains: Ding numeric C_src or accepted same-regime reproduction, material/state mapping, source-grade uncertainty, c_v uncertainty, alpha_Phi_K, and full bridge closure
- next commit, push, PR, or manifest action: commit this scoped evidence wave; next controller is permitted Ding-compatible source and uncertainty closure
- evidence hashes: component {component}; full gate {full_gate}; matrix {matrix}; register {register}; dependency {dependency}
"""

    wave_path = ROOT / f"docs/topics/0.13_Thermodynamic_Bridge/RESEARCH_WAVE_{DAY.replace('-', '')}_CSRC_EQUILIBRIUM_COMPONENT.md"
    if not wave_path.exists():
        wave_path.write_text(wave, encoding="utf-8")
    append_once("docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md", f"### {DAY} - Equilibrium C_src component acceptance", update)
    append_once("docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md", f"## Equilibrium C_src component acceptance ({DAY})", manifest)
    append_once(f"WORK_LEDGER/2026/{DAY}.md", "## Topic 13 equilibrium C_src component acceptance", ledger)
    print(f"PASS_RECORDED_TOPIC13_CSRC_EQUILIBRIUM_COMPONENT component={component} full_gate={full_gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
