"""Record the Calorine/phono3py reproduction wave in topic coordination files."""

from __future__ import annotations

import hashlib
from datetime import date
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
    rendered = body.rstrip("\r\n").replace("\n", newline.decode()).encode("utf-8")
    path.write_bytes(raw.rstrip(b"\r\n") + newline + rendered + newline)


def main() -> int:
    day = date.today().isoformat()
    package = digest("docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_calorine_zenodo_nep_bte_reproduction_source_package.json")
    audit = digest("docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_reproduction_audit.json")
    full = digest("docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json")
    register = digest("docs/core/07_artifacts/gates/uet_major_result_closure_register.json")
    dependency = digest("docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    candidate = digest("docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json")
    isotope = digest("docs/core/07_artifacts/topic13/t13_calorine_isotope_mass_sensitivity_audit.json")
    uncertainty = digest("docs/core/07_artifacts/topic13/t13_calorine_state_uncertainty_decomposition_audit.json")
    acceptance = digest("docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json")

    update = f"""### {day} - Calorine/Zenodo PBTE numeric C_src reproduction

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION.
WHAT_IS_ACTUALLY_CLOSED: A source-locked Calorine/Zenodo graphite NEP route was rerun through phono3py RTA. The fixed 4x4x2 force-constant state produced volumetric C_src rows, and the latest 8x8x4 to 10x10x5 q-mesh pair changed by at most 0.2391%.
WHAT_REMAINS_OPEN: Ding natural-graphite TTG material/state equivalence, source-grade uncertainty, raw Ding C_src acceptance, alpha_Phi_K, non-circular UET bridge/beta, EOS/transport/KMS/entropy, and dimensional Phi mapping remain open.
DEPENDENCY_UNLOCKED: Candidate numeric reproduction lane only; no Full Topic 13, Core, Gravity, constitutive transport, Galaxy, alpha, or external-validation unlock.
STATUS: PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added persistent source inputs, force-constant and kappa payloads, four mesh summaries, source package, reproduction audit, full-gate projection, closure-register entry, focused regression test, and this wave record.
EQUATION_OR_MAPPING: C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive], with c_qmu in eV K^-1 per mode per primitive cell and output in J m^-3 K^-1. This is a candidate source response for Delta_Tq = Delta_u_ph / C_src(T), not a Phi mapping.
VERIFICATION: Input locators and hashes match; force-constant identity is fixed across meshes; SI energy/volume conversion is recorded; latest mesh-pair preflight passes; no fit, target tuning, alpha_Phi_K fitting, or holdout access occurred.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Resolve material/state equivalence and source-grade uncertainty against the independent C_src acceptance contract; do not use this route for alpha_Phi_K calibration or holdout prediction.
CLAIM_BOUNDARY: Candidate harmonic/RTA PBTE reproduction only; not Ding-regime validation, not UET Phi calibration, not TTG prediction, not external validation, and not Full Topic 13 closure.
EVIDENCE_HASHES: package {package}; audit {audit}; full gate {full}; register {register}; dependency {dependency}.
"""

    manifest = f"""## Calorine/Zenodo PBTE numeric C_src reproduction ({day})

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION.
WHAT_IS_ACTUALLY_CLOSED: Public Calorine/Zenodo inputs are hashed and rerun through a fixed 4x4x2 force-constant state with 4x4x2, 6x6x3, 8x8x4, and 10x10x5 q meshes; the latest pair passes the declared candidate numerical preflight.
WHAT_REMAINS_OPEN: Ding material/state mapping, source-grade uncertainty, raw Ding C_src acceptance, alpha_Phi_K, UET bridge/beta, full transport/KMS/entropy, and Phi-to-observable calibration.
DEPENDENCY_UNLOCKED: Candidate C_src reproduction lane only; no downstream Core or application unlock.
STATUS: PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added the source package, persistent summaries and HDF5 payloads, reproduction audit, full-gate projection, registry sync, and focused test.
EQUATION_OR_MAPPING: C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]; output unit J m^-3 K^-1. No Phi, alpha_Phi_K, or holdout mapping is emitted.
VERIFICATION: Source hashes, units, force-constant identity, mesh comparison, no-fit, and no-holdout checks pass.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Close material/state and source-grade uncertainty gates before reconsidering full C_src acceptance.
CLAIM_BOUNDARY: Candidate reproduction only; not Ding-equivalent, not calibration, not prediction, and not Full Topic 13 closure.
EVIDENCE_HASHES: package {package}; audit {audit}; full gate {full}; register {register}; dependency {dependency}.
"""

    wave = f"""# Research Wave: Calorine/Zenodo PBTE Numeric C_src Reproduction ({day})

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE
WHAT_IS_ACTUALLY_CLOSED: T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION. The public Calorine/Zenodo graphite NEP input was rerun with a fixed 4x4x2 force-constant state. The latest 8x8x4 to 10x10x5 q-mesh pair has maximum relative C_src change 0.0023908135.
WHAT_REMAINS_OPEN: Ding material/state equivalence, source-grade uncertainty, Ding C_src acceptance, alpha_Phi_K, non-circular bridge/beta, EOS/transport/KMS/entropy, and dimensional Phi mapping.
DEPENDENCY_UNLOCKED: Candidate numeric reproduction lane only.
STATUS: PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION.
WHAT_CHANGED: Added source package, persistent summaries and HDF5 outputs, machine-readable audit, full-gate source-package projection, registry sync, and regression tests.
EQUATION_OR_MAPPING: C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive], with SI conversion from eV K^-1 per mode per primitive cell to J m^-3 K^-1. No Phi or alpha mapping is inferred.
VERIFICATION: Source hashes, archived payloads, unit conversion, fixed force constants, latest mesh preflight, no-fit, and holdout audit pass.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Resolve material/state equivalence and source-grade uncertainty against the independent C_src acceptance contract.
CLAIM_BOUNDARY: Candidate harmonic/RTA PBTE reproduction only; not Ding validation, alpha calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: package {package}; audit {audit}; full gate {full}; register {register}; dependency {dependency}.
"""

    ledger = f"""## Topic 13 Calorine/Zenodo PBTE numeric C_src reproduction

- area: research-core
- workspace: docs/topics/0.13_Thermodynamic_Bridge
- files/artifacts: source package, persistent PBTE summaries/HDF5 payloads, reproduction audit, full-gate projection, registry sync, focused test, wave note, manifest, update log
- verifier: PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION; latest mesh-pair max relative change 0.0023908135
- public-safety: partial
- result: candidate numeric C_src reproduction lane closed for lane; full Topic 13 remains blocked
- hashes: package {package}; audit {audit}; full {full}; register {register}; dependency {dependency}
- remains: Ding material/state equivalence, source-grade uncertainty, alpha_Phi_K, bridge/beta, EOS/transport/KMS/entropy, and dimensional Phi mapping
- next action: resolve material/state and uncertainty acceptance before promoting C_src
- commit/push action: no commit requested; retain scoped changes identifiable in the dirty worktree
"""

    state_update = f"""### {day} - Calorine provenance and state-uncertainty decomposition

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_CALORINE_ISOTOPE_MASS_SENSITIVITY and T13_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION.
WHAT_IS_ACTUALLY_CLOSED: Zenodo is recorded as the local byte source, GPUMD as the upstream NEP model origin, and record 7811021 as related but not the input source. NIST natural-carbon bounds were propagated through the mass-only C_src lane; the mesh numerical envelope and mass-only state envelope are reported separately.
WHAT_REMAINS_OPEN: Ding natural-graphite material/state equivalence, defect/morphology and isotope-scattering state, source-grade uncertainty, Ding C_src acceptance, alpha_Phi_K, UET bridge/beta, EOS/transport/KMS/entropy, and dimensional Phi mapping.
DEPENDENCY_UNLOCKED: Provenance and Calorine state-sensitivity lanes only; no full Topic 13 or downstream unlock.
STATUS: PASS_SCOPED_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Corrected NEP provenance metadata, regenerated the source package and candidate boundary, added mass-only isotope sensitivity and uncertainty decomposition audits, and synchronized the acceptance/full-gate/registry artifacts.
EQUATION_OR_MAPPING: epsilon_mesh = 0.0023908135; natural-composition mass envelope = 0.0000511973; pure-isotope values are stress bounds only. No Phi, alpha_Phi_K, or holdout mapping is inferred.
VERIFICATION: No fit, target tuning, alpha_Phi_K calibration, threshold adjustment, clipping, padding, or Xie 2026 holdout access occurred. Acceptance remains false.
CONTROLLING_BLOCKER: material_regime_mapping_to_TTG_not_closed; source-grade uncertainty is not inferred from the reported envelopes.
NEXT_ACTION: Source-lock defect/morphology state and response contract, or retain Calorine as a non-Ding comparator; then reassess independent C_src acceptance.
CLAIM_BOUNDARY: Candidate provenance and sensitivity decomposition only; not Ding validation, source-grade uncertainty closure, UET Phi calibration, TTG prediction, or Full Topic 13 closure.
EVIDENCE_HASHES: candidate {candidate}; isotope {isotope}; uncertainty {uncertainty}; acceptance {acceptance}; full gate {full}.
"""

    state_wave_path = ROOT / f"docs/topics/0.13_Thermodynamic_Bridge/RESEARCH_WAVE_{day.replace('-', '')}_CALORINE_PROVENANCE_STATE_UNCERTAINTY.md"
    if not state_wave_path.exists():
        state_wave_path.write_text(state_update, encoding="utf-8")
    append_once("docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md", f"### {day} - Calorine provenance and state-uncertainty decomposition", state_update)
    append_once("docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md", f"### {day} - Calorine provenance and state-uncertainty decomposition", state_update)
    append_once(f"WORK_LEDGER/2026/{day}.md", f"### {day} - Calorine provenance and state-uncertainty decomposition", state_update)
    resync_update = f"""### {day} - Calorine evidence-chain resynchronization

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE evidence chain synchronized for T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION, T13_CALORINE_ISOTOPE_MASS_SENSITIVITY, and T13_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION.
WHAT_IS_ACTUALLY_CLOSED: The final reproduction, acceptance, full-gate, and registry hashes now point to the same corrected provenance and sensitivity artifacts.
WHAT_REMAINS_OPEN: Full Topic 13 remains blocked by Ding-compatible C_src acceptance, material/state mapping, source-grade uncertainty, alpha_Phi_K, bridge/beta, EOS/transport/KMS/entropy, and dimensional mapping.
DEPENDENCY_UNLOCKED: No new dependency; only lane-level evidence-chain consistency.
STATUS: PASS_SCOPED_EVIDENCE_CHAIN_RESYNCHRONIZATION.
WHAT_CHANGED: Refreshed full-gate and registry projections after the final source-package and uncertainty-audit regeneration.
EQUATION_OR_MAPPING: y_TTG = Delta_Tq(t) / Delta_Tq(0); Delta_Tq = alpha_Phi_K * Delta_Phi remains open. The reported C_src envelopes are comparator diagnostics only.
VERIFICATION: Full gate remains BLOCKED_OPEN_T13_FULL_BRIDGE; claim promotion is false; no fit, holdout read, threshold change, clipping, or padding occurred.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Continue with source-locked Ding-regime material/state and uncertainty closure.
CLAIM_BOUNDARY: Hash synchronization is not physical closure, external validation, alpha calibration, or Full Topic 13 closure.
EVIDENCE_HASHES: package {package}; reproduction audit {audit}; candidate {candidate}; isotope {isotope}; uncertainty {uncertainty}; acceptance {acceptance}; full gate {full}; register {register}; dependency {dependency}.
"""
    append_once("docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md", f"### {day} - Calorine evidence-chain resynchronization", resync_update)
    append_once("docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md", f"### {day} - Calorine evidence-chain resynchronization", resync_update)
    append_once(f"WORK_LEDGER/2026/{day}.md", f"### {day} - Calorine evidence-chain resynchronization", resync_update)
    resync_wave_path = ROOT / f"docs/topics/0.13_Thermodynamic_Bridge/RESEARCH_WAVE_{day.replace('-', '')}_CALORINE_EVIDENCE_CHAIN_RESYNC.md"
    if not resync_wave_path.exists():
        resync_wave_path.write_text(resync_update, encoding="utf-8")
    append_once("docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md", f"### {day} - Calorine/Zenodo PBTE numeric C_src reproduction", update)
    append_once("docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md", f"## Calorine/Zenodo PBTE numeric C_src reproduction ({day})", manifest)
    append_once(f"WORK_LEDGER/2026/{day}.md", "## Topic 13 Calorine/Zenodo PBTE numeric C_src reproduction", ledger)
    wave_path = ROOT / f"docs/topics/0.13_Thermodynamic_Bridge/RESEARCH_WAVE_{day.replace('-', '')}_CALORINE_PBTE_NUMERIC_C_SRC.md"
    if not wave_path.exists():
        wave_path.write_text(wave, encoding="utf-8")
    print(f"recorded wave: package={package} audit={audit} full={full} register={register} dependency={dependency}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
