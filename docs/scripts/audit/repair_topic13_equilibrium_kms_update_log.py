"""Append the Topic 13 equilibrium KMS wave to its update log."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
KMS = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_equilibrium_kms_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
MARKER = "### 2026-08-13 - Topic 13 equilibrium KMS/FDT lane"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    text = LOG.read_text(encoding="utf-8-sig")
    if MARKER not in text:
        entry = f"""
{MARKER}

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_EQUILIBRIUM_KMS_LANE.
WHAT_IS_ACTUALLY_CLOSED: The declared positive-frequency O(2) normal and condensed mode witnesses satisfy the action-derived equilibrium Bose KMS ratio, spectral difference, fluctuation-dissipation noise identity, nonnegative single-mode entropy witness, and zero entropy-production identity for uniform equilibrium.
WHAT_REMAINS_OPEN: Interacting SK/KMS matching, collision/noise kernel, retarded-correlator Kubo provenance, spatial entropy current, dissipative balance, finite-temperature normal-component transport, dimensional Phi to thermal-observable mapping, and independent alpha_Phi_K remain open. Full Topic 13 remains blocked.
DEPENDENCY_UNLOCKED: Equilibrium KMS/FDT identity lane only; no dissipative transport, physical Kubo, SI, alpha, Core, Gravity, Galaxy, or external-validation unlock.
STATUS: PASS_ACTION_DERIVED_EQUILIBRIUM_KMS_FDT_LANE; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added the action-derived KMS/FDT module, focused test, audit artifact {digest(KMS)}, full-gate lane/evidence projection {digest(FULL)}, major-result register {digest(REGISTER)}, and dependency record {digest(DEPENDENCY)}. The full gate still reports its existing source, alpha, bridge/beta, transport, dimensional-map, material, and uncertainty blockers.
EQUATION_OR_MAPPING: G^>(E)=(1+n_B(E))*rho(E); G^<(E)=n_B(E)*rho(E); G^>(E)=exp(beta_th*E)*G^<(E); G^>-G^<=rho; N(E)=coth(beta_th*E/2)*rho; s_mode=(1+n)ln(1+n)-n ln(n)>=0. This is not Delta_Tq=alpha_Phi_K*Delta_Phi and does not assign temperature to Phi.
VERIFICATION: Focused KMS tests pass (3 passed); audit passes for 16 positive-frequency records with no failed checks; full gate remains BLOCKED_OPEN_T13_FULL_BRIDGE. No parameter fitting, target data, or holdout data was used.
CONTROLLING_BLOCKER: interacting_SK_action_and_physical_Kubo_provenance_missing controls the next KMS/transport wave; the full Topic 13 controller remains dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing.
NEXT_ACTION: Declare an interacting SK/KMS collision-noise kernel and obtain a state-matched physical Kubo source before attempting dissipative transport or entropy-current closure; retain the equilibrium lane as a named internal result.
CLAIM_BOUNDARY: This closes only an action-derived equilibrium KMS/FDT identity lane for declared positive-energy O(2) modes. It is not microscopic interacting SK/KMS closure, physical transport, SI calibration, alpha_Phi_K, TTG prediction, external validation, Core closure, or global UET closure.
"""
        LOG.write_text(text.rstrip() + "\n" + entry.lstrip(), encoding="utf-8")
        changed = True
    else:
        changed = False
    print(
        {
            "status": "PASS_TOPIC13_EQUILIBRIUM_KMS_UPDATE_LOG",
            "changed": changed,
            "log": str(LOG.relative_to(ROOT)).replace("\\", "/"),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

