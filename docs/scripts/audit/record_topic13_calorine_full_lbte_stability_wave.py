"""Record the Topic 13 full-LBTE numerical-stability hardening wave."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/artifacts/t13_calorine_full_lbte_stability_boundary_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"
UPDATE_LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-21.md"
AUDIT_SCRIPT_REL = "docs/scripts/audit/audit_topic13_calorine_full_lbte_stability.py"
TEST_REL = "docs/core/test/test_topic13_calorine_full_lbte_stability.py"
MARKER = "## T13-151 - Calorine full-LBTE numerical stability boundary"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def append_once(relative: str, content: str) -> bool:
    path = ROOT / relative
    existing = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    if MARKER in existing:
        return False
    separator = "" if not existing or existing.endswith("\n") else "\n"
    path.write_text(existing + separator + content.rstrip() + "\n", encoding="utf-8")
    return True


def main() -> int:
    audit = load(AUDIT_REL)
    full = load(FULL_REL)
    register = load(REGISTER_REL)
    dependency = load(DEPENDENCY_REL)
    latest_pair = audit["mesh_convergence"]["latest_pair"]
    latest_change = latest_pair["max_relative_change"]
    artifact_hash = sha256(AUDIT_REL)
    full_hash = sha256(FULL_REL)
    register_hash = sha256(REGISTER_REL)
    dependency_hash = sha256(DEPENDENCY_REL)
    method0_negative = audit["checks"]["method0_negative_in_plane_kappa_at_300K"]
    negative_counts = audit["method1_runs"][-1]["collision_eigenvalue_negative_count_by_temperature"]
    report_entry = f"""{MARKER}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for the source-locked full-LBTE numerical-stability boundary; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: A fixed Calorine 4x4x2 force-constant state was rerun with explicit natural-isotope control. The archived `pinv_method=0` and `pinv_method=1` outputs show that the high-mesh collision spectrum is sign-indefinite; the positive method-1 response is therefore recorded as a numerical boundary, not physical transport closure.
WHAT_REMAINS_OPEN: Collision-spectrum positivity, full-LBTE mesh convergence, source-grade uncertainty, Calorine-to-Ding material/state mapping, independent `alpha_Phi_K`, dimensional `Phi` mapping, physical Kubo provenance, and EOS/transport/KMS/entropy closure remain open.
DEPENDENCY_UNLOCKED: Full-LBTE numerical-boundary evidence lane only. No physical transport, dimensional calibration, Full Topic 13, Core, Gravity, constitutive transport, or Galaxy dependency is unlocked.
STATUS: `{audit['status']}`; canonical full gate remains `{full['status']}` with {len(full['major_result']['what_remains_open'])} blockers.
WHAT_CHANGED: Added the archived full-LBTE stability audit, method-sensitivity control, collision-eigenvalue diagnostics, focused regression, full-gate source-package projection, and major-result register/dependency synchronization. No source, ontology, thermal leakage threshold, fit, calibration, or holdout policy changed.
EQUATION_OR_MAPPING: `C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]`; candidate `Delta_Tq = Delta_u_ph / C_src(T)`; full-LBTE observable `kappa` is in `W m^-1 K^-1`. `pinv_method=1` treats eigenvalue `< 1e-8` as zero and ignores negative eigenvalues; it is not a proof of positive entropy/transport response.
VERIFICATION: Latest method-1 mesh pair `{latest_change:.12g}` relative change (8x8x4 to 10x10x5), method-0 in-plane `kappa` at 300 K is negative (`{method0_negative}`), and the high-mesh method-1 collision spectrum has negative-mode counts `{negative_counts}`. Fit, target-curve use, `alpha_Phi_K` fit, and holdout access are false.
CONTROLLING_BLOCKER: `full_lbte_numerical_well_posedness_not_closed`, alongside the existing independent dimensional/`alpha_Phi_K`, Ding `C_src`, material, uncertainty, and thermodynamic-transport blockers.
NEXT_ACTION: Resolve the sign-indefinite collision spectrum and obtain a declared source-supported convergence/uncertainty contract before treating full-LBTE output as a physical comparator; do not use it for `alpha_Phi_K` or holdout prediction.
CLAIM_BOUNDARY: This is a numerical-stability boundary for one external candidate route, not a physical UET transport coefficient, Ding TTG validation, `Phi`-to-temperature prediction, Core closure, or global UET closure.
EVIDENCE_PATHS: `{AUDIT_REL}`; `{AUDIT_SCRIPT_REL}`; `{TEST_REL}`; `{FULL_REL}`; `{REGISTER_REL}`; `{DEPENDENCY_REL}`.
EVIDENCE_HASHES: artifact `{artifact_hash}`; full gate `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`.
"""
    formula_entry = f"""{MARKER}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`; this is an external full-LBTE numerical boundary, not a UET transport derivation.
WHAT_IS_ACTUALLY_CLOSED: The source-locked force-constant identity, natural-isotope control, full-LBTE solver-method comparison, collision-spectrum sign diagnostic, and adjacent mesh response record are reproducible from the archived local payload hashes.
WHAT_REMAINS_OPEN: `kappa` is not accepted as a UET coefficient. The collision matrix is not positive semidefinite at the high mesh, method-1 response is not converged, and material/state equivalence, source uncertainty, `alpha_Phi_K`, SI `Phi` mapping, Kubo, EOS, KMS, and entropy closure are absent.
DEPENDENCY_UNLOCKED: None beyond the numerical-boundary lane.
STATUS: `{audit['status']}`.
WHAT_CHANGED: Added formula and solver semantics for `pinv_method=0/1` and kept the source mapping separate from UET variables.
EQUATION_OR_MAPPING: `C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]`; `Delta_Tq = Delta_u_ph/C_src(T)`; `kappa` is a candidate heat-current response. `C_src` is not UET `C`; `Phi` and `R_gen` are not relabeled.
VERIFICATION: `pinv_method=0` yields negative in-plane `kappa` at 300 K; method `1` ignores negative eigenvalues but the latest mesh change is `{latest_change:.12g}`. No fit, calibration, or Xie 2026 holdout access occurred.
CONTROLLING_BLOCKER: `full_lbte_collision_spectrum_positive_semidefinite_missing` and `full_lbte_mesh_convergence_missing`.
NEXT_ACTION: Supply a declared, source-supported collision/transport stability and uncertainty contract before any physical transport comparison.
CLAIM_BOUNDARY: Numerical boundary only; no UET dimensional map, `alpha_Phi_K`, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE: `{AUDIT_REL}` (SHA-256 `{artifact_hash}`).
"""
    update_entry = f"""{MARKER}

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the full-LBTE numerical-stability boundary; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: Full-LBTE source identity, natural-isotope control, pseudoinverse method comparison, collision-spectrum sign diagnostic, and the latest mesh response are now machine-readable.
WHAT_REMAINS_OPEN: Positive-semidefinite collision spectrum, mesh convergence, source-grade uncertainty, Ding material/state mapping, independent alpha_Phi_K, dimensional Phi map, physical Kubo, and EOS/transport/KMS/entropy closure.
DEPENDENCY_UNLOCKED: None beyond the numerical-boundary classification; downstream Core/Gravity/transport/Galaxy remain blocked.
STATUS: {audit['status']}; full gate {full['status']} with {len(full['major_result']['what_remains_open'])} blockers.
WHAT_CHANGED: Added the full-LBTE stability audit, archived local payload hashes, focused regression, full-gate projection, major-result register/dependency sync, and this documentation entry. No holdout or calibration data was used.
EQUATION_OR_MAPPING: C_src(T) = [sum_q w_q sum_mu c_qmu(T)]/[sum_q w_q V_primitive]; Delta_Tq = Delta_u_ph/C_src(T); kappa is a candidate W m^-1 K^-1 response. No Phi-to-temperature map is emitted.
VERIFICATION: The method-0 control has negative in-plane kappa at 300 K; method 1 leaves a sign-indefinite spectrum and its latest adjacent mesh change is {latest_change:.12g}. Xie 2026 was not accessed.
CONTROLLING_BLOCKER: full_lbte_numerical_well_posedness_not_closed, with the existing independent dimensional/alpha and Ding/source/thermodynamic blockers unchanged.
NEXT_ACTION: Resolve the collision-spectrum and convergence boundary without clipping, threshold changes, fit, or holdout access.
CLAIM_BOUNDARY: Scoped numerical boundary only; not a physical UET transport coefficient, alpha calibration, prediction, external validation, Core closure, or global UET closure.
EVIDENCE_PATHS: {AUDIT_REL}; {FULL_REL}; {REGISTER_REL}; {DEPENDENCY_REL}.
EVIDENCE_HASHES: artifact {artifact_hash}; full gate {full_hash}; register {register_hash}; dependency {dependency_hash}.
"""
    ledger_entry = f"""{MARKER}
- Area: `research-core` (secondary: `result-artifacts`)
- Workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- Files/artifacts: full-LBTE stability audit, archived local payload hash records, focused test, full-gate projection, major-result register/dependency gate, report/formula audit/update log
- Verification: artifact `{audit['status']}`; full gate `{full['status']}` with {len(full['major_result']['what_remains_open'])} blockers; latest method-1 mesh change `{latest_change:.12g}`; method-0 300 K response negative; no fit/calibration/holdout
- Public-safety status: `partial`
- Result: numerical-stability boundary is closed for lane; no physical transport or UET dimensional claim is promoted
- Uncommitted/private: HDF5 payloads remain under the repository `*.hdf5` ignored-artifact policy and are represented by local hashes; no raw/private holdout was included
- Next action: resolve collision-spectrum positivity/convergence and source uncertainty before considering physical transport comparison
- Commit/push action: commit this scoped Topic 13 hardening wave separately
"""
    changed = {
        UPDATE_LOG_REL: append_once(UPDATE_LOG_REL, update_entry),
        FORMULA_REL: append_once(FORMULA_REL, formula_entry),
        REPORT_REL: append_once(REPORT_REL, report_entry),
        LEDGER_REL: append_once(LEDGER_REL, ledger_entry),
    }
    print(json.dumps({"status": "PASS_TOPIC13_FULL_LBTE_WAVE_RECORDED", "changed": changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
