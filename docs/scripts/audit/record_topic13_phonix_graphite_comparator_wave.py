from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
RAW = TOPIC / "Data/03_Research/raw/phonix_mp47_graphite_summary_row.json"
PACKAGE = TOPIC / "Data/03_Research/phonix_mp47_graphite_source_package.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_phonix_mp47_graphite_comparator_audit.json"
FULL = TOPIC / "Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(path: Path, marker: str, content: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in text:
        return
    separator = "" if not text or text.endswith("\n\n") else "\n"
    path.write_text(text + separator + content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    raw_hash = digest(RAW)
    package_hash = digest(PACKAGE)
    audit_hash = digest(AUDIT)
    full_hash = digest(FULL)
    register_hash = digest(REGISTER)
    dependency_hash = digest(DEPENDENCY)
    report = f"""### 2026-08-13 - Phonix mp-47 graphite harmonic comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_PHONIX_MP47_GRAPHITE_HARMONIC_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The Phonix `mp-47` row is archived with immutable dataset revision `284bddebbd144ae3e3f93474dc05e4658417d09f`, exact row identity, primitive volume, graphite space group, frequency/DOS arrays, q-mesh, and source hashes. Identity, shape, grid, sign, provenance, and holdout-isolation checks pass.
WHAT_REMAINS_OPEN: Phonix reports `phdos` in source arbitrary units and supplies no standard uncertainty for a unitful `c_v`; it is not a Ding natural-graphite TTG/PBTE material match and does not provide Ding mode-resolved `C_src` or an independent `alpha_Phi_K`.
DEPENDENCY_UNLOCKED: Source-locked graphite harmonic comparator only; no Ding source, volumetric `c_v`, alpha, transport, Core, Gravity, or Galaxy dependency unlock.
STATUS: `PASS_SCOPED_PHONIX_GRAPHITE_HARMONIC_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added raw snapshot `{raw_hash}`, source package `{package_hash}`, comparator audit `{audit_hash}`, full-gate projection `{full_hash}`, and register/dependency synchronization `{register_hash}` / `{dependency_hash}`.
EQUATION_OR_MAPPING: Harmonic kernel boundary `c_mu(T)=k_B*x_mu^2*exp(x_mu)/(exp(x_mu)-1)^2`; only `I_DOS=integral[phdos_source(nu)dnu]` in source units is reported. No volumetric `c_v`, Ding `C_src`, `Delta_Tq=alpha_Phi_K*Delta_Phi`, or alpha value is emitted.
VERIFICATION: Immutable revision, exact `mp-47` locator, raw/package hash, P6_3/mmc identity, 51-bin shape/grid, nonnegative DOS, arbitrary-unit boundary, no invented uncertainty, no target/alpha fit, and Xie 2026 holdout isolation pass.
CONTROLLING_BLOCKER: `phonix_summary_dos_units_and_uncertainty_not_sufficient_for_volumetric_cv`; full gate also remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Obtain a unitful uncertainty-grade same-regime `c_v` or authorized Ding PBTE payload/accepted reproduction with material-state mapping; retain Phonix as comparison only.
CLAIM_BOUNDARY: Source-provenance and harmonic-comparator lane only. This is not Ding validation, UET transport validation, alpha calibration, external validation, or global UET closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "Phonix mp-47 graphite harmonic comparator lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - Phonix mp-47 graphite harmonic comparator lane", report)
    manifest = f"""## Phonix mp-47 Graphite Harmonic Comparator (2026-08-13)

Raw snapshot: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/phonix_mp47_graphite_summary_row.json` (`{raw_hash}`).
Source package: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/phonix_mp47_graphite_source_package.json` (`{package_hash}`).
Audit: `docs/core/07_artifacts/topic13/t13_phonix_mp47_graphite_comparator_audit.json` (`{audit_hash}`).

The immutable Phonix `mp-47` summary row is retained as a graphite harmonic
comparison source. Its DOS is source-declared `a.u.` and no standard
uncertainty is supplied, so no unitful volumetric `c_v`, Ding `C_src`, or
alpha calibration is emitted. The material equivalence to Ding's natural
graphite TTG/PBTE sample remains explicitly unestablished.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## Phonix mp-47 Graphite Harmonic Comparator (2026-08-13)", manifest)
    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_text = f"""## Topic 13 Phonix mp-47 harmonic comparator wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: Phonix raw snapshot and source package; comparator audit/script/test; full-gate projection; major-result register/dependency sync; report/update log/manifest
- verifier: `PASS_SCOPED_PHONIX_GRAPHITE_HARMONIC_COMPARATOR`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: source-locked graphite harmonic comparator closed for lane; arbitrary-unit DOS and missing standard uncertainty prevent volumetric `c_v` promotion
- hashes: raw `{raw_hash}`; package `{package_hash}`; audit `{audit_hash}`; full `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`
- remains: Ding numeric `C_src` or accepted reproduction, material-regime mapping, unitful uncertainty-grade `c_v`, base-Phi SI anchor, independent alpha, bridge/beta, physical transport, KMS, entropy, and dissipative balance
- next action: pursue permitted unitful same-regime thermal/PBTE source without Xie 2026 access or target fitting
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 Phonix mp-47 harmonic comparator wave", ledger_text)
    print("recorded Phonix mp-47 graphite comparator wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
