from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_phi_e_dimensional_comparator_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(path: Path, marker: str, content: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in text:
        print(f"skip existing section: {path}")
        return
    separator = "\n" if text.endswith("\n") else "\n\n"
    path.write_text(text + separator + content.rstrip() + "\n", encoding="utf-8")
    print(f"appended: {path}")


def main() -> int:
    lane_hash = sha256(LANE)
    full_hash = sha256(FULL)
    register_hash = sha256(REGISTER)
    report = f"""### 2026-08-13 - MP48 named Phi_E dimensional comparator

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: A standard harmonic energy-to-temperature comparator is source-locked at MP48 reference temperature `T0=300 K`; `Phi_E := Delta_u_ph/e0(T0)` and `alpha_Phi_E_K := e0(T0)/c_v(T0)` are numerically evaluated without target fitting.
WHAT_REMAINS_OPEN: The mapping from base UET `Phi` to named `Phi_E` is not derived, so this does not close base `alpha_Phi_K`; Ding PBTE material matching, physical transport, SK/KMS, entropy, and dissipative balance remain open.
DEPENDENCY_UNLOCKED: Named `Phi_E` standard dimensional comparator only; no base-Phi, Full Topic 13, Core, Gravity, or transport unlock.
STATUS: `PASS_SCOPED_PHI_E_DIMENSIONAL_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/core/07_artifacts/topic13/t13_mp48_phi_e_dimensional_comparator_audit.json` (SHA-256 `{lane_hash}`), integrated it under the dimensional-observable map, and refreshed the register (`{register_hash}`) and full gate (`{full_hash}`).
EQUATION_OR_MAPPING: `u_th(T)=N_A integral[g(nu) h nu/(exp(h nu/(k_B T))-1)dnu]`; `Phi_E=Delta_u_ph/e0(T0)`; `Delta_Tq=(e0(T0)/c_v(T0))*Phi_E`; at `300 K`, conditional `alpha_Phi_E_K=126.72529975005031 K`.
VERIFICATION: DOS source identity, zero negative-frequency weight, uniform grid, source volume, finite energy/capacity rows at `200/250/300 K`, volume cancellation in `e0/c_v`, no base-alpha emission, no target fit, and no Xie 2026 access. Focused Phi_E/spectral tests: `4 passed`.
CONTROLLING_BLOCKER: `base_Phi_to_Phi_E_mapping_and_independent_alpha_Phi_K_missing` for this lane; full gate retains the existing dimensional and source/transport blockers.
NEXT_ACTION: Derive or source-lock a physical base-Phi-to-Phi_E amplitude map, or obtain a paired base-Phi/SI record. Do not relabel `alpha_Phi_E_K` as `alpha_Phi_K`.
CLAIM_BOUNDARY: Standard harmonic comparator only. It is not a base-Phi calibration, not Ding PBTE validation, not a UET temperature prediction, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "MP48 named Phi_E dimensional comparator", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - MP48 named Phi_E dimensional comparator", report)

    manifest = f"""## MP48 Named Phi_E Dimensional Comparator (2026-08-13)

The MP48 harmonic package now supports a named standard-physics energy-response
comparator. At the declared reference `T0=300 K`, the source-derived thermal energy
density is used as `e0(T0)` and the same-source harmonic volumetric heat capacity as
`c_v(T0)`, yielding the conditional relation `alpha_Phi_E_K=e0/c_v`.

The machine-readable artifact is
`docs/core/07_artifacts/topic13/t13_mp48_phi_e_dimensional_comparator_audit.json` with SHA-256
`{lane_hash}`. The result emits no `alpha_Phi_K`: `Phi_E` is a named standard-physics
coordinate and the base UET `Phi -> Phi_E` map remains open. No target curve, fitting,
or Xie 2026 holdout was used.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## MP48 Named Phi_E Dimensional Comparator (2026-08-13)", manifest)

    formula = f"""## MP48 Named Phi_E Dimensional Comparator (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-040` | `u_th(T)=N_A integral[g(nu) h nu/(exp(h nu/(k_B T))-1)dnu]`; `Phi_E=Delta_u_ph/e0(T0)`; `Delta_Tq=(e0(T0)/c_v(T0))*Phi_E` | `docs/scripts/audit/audit_topic13_mp48_phi_e_dimensional_comparator.py`; `docs/core/07_artifacts/topic13/t13_mp48_phi_e_dimensional_comparator_audit.json` | `u_th,e0` = J m^-3; `c_v` = J m^-3 K^-1; `Phi_E` = dimensionless; `alpha_Phi_E_K` = K per normalized Phi_E | source-locked CODATA constants plus MP48 deposited DOS, source volume, and harmonic heat-capacity package | checked local standard-physics comparator; base UET map open | dimensional-map diagnostic and named-coordinate boundary only | the base `Phi` may not equal `Phi_E`; harmonic energy is not a UET free-energy anchor; material/source regime mismatch remains possible | derive/source-lock `Phi_base -> Phi_E` with units and uncertainty or acquire a paired base-Phi/SI record; keep `alpha_Phi_K` blocked |

At `T0=300 K`, the conditional comparator gives `alpha_Phi_E_K=126.72529975005031 K`.
This number is not a UET coefficient and is not allowed to enter the `alpha_Phi_K`
gate. Artifact SHA-256: `{lane_hash}`.
"""
    append_once(TOPIC / "FORMULA_AUDIT.md", "## MP48 Named Phi_E Dimensional Comparator (2026-08-13)", formula)

    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_content = f"""## Topic 13 Phi_E dimensional hardening wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: Phi_E comparator script/test/artifact; full-gate dimensional-map integration; formula audit; data manifest; current report; update log; closure register/dependency hash sync
- verifier: focused Phi_E and spectral tests `4 passed`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; closure register now has `56` entries
- public-safety: `partial`
- result: named standard harmonic Phi_E dimensional comparator closed for lane; base Phi and alpha_Phi_K not promoted
- hashes: Phi_E artifact `{lane_hash}`; full gate `{full_hash}`; closure register `{register_hash}`
- remains: base-Phi-to-Phi_E map, independent alpha_Phi_K, Ding PBTE C_src/material matching, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: source-lock or derive the base-Phi amplitude map; do not use the conditional Phi_E coefficient as UET calibration
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 Phi_E dimensional hardening wave", ledger_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
