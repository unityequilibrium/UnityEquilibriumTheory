from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
RAW = TOPIC / "Data/03_Research/raw/iaea_graphite_handbook_2017.pdf"
PACKAGE = TOPIC / "Data/03_Research/iaea_graphite_cv_uncertainty_boundary_source_package.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_iaea_cv_uncertainty_boundary_audit.json"
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
    report = f"""### 2026-08-13 - IAEA c_v uncertainty and volumetric boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_IAEA_CV_UNCERTAINTY_BOUNDARY`.
WHAT_IS_ACTUALLY_CLOSED: The IAEA Table 4.11 comparator remains source-traceable, but its `Delta c_p` is a probable-error envelope rather than a standard uncertainty for derived `c_v`; the thermoelastic correction and volumetric conversion have no source-locked same-row uncertainty contract.
WHAT_REMAINS_OPEN: Uncertainty-grade volumetric `c_v` or Ding `C_src` is still missing; the comparator cannot be used as a Ding material substitution or alpha calibration.
DEPENDENCY_UNLOCKED: The IAEA uncertainty route is closed as a scoped no-go; no Core, Gravity, transport, or alpha dependency is unlocked.
STATUS: `PASS_SCOPED_IAEA_CV_UNCERTAINTY_BOUNDARY_NO_GO`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added source package `{package_hash}`, boundary audit `{audit_hash}`, full-gate projection `{full_hash}`, and registry/dependency synchronization `{register_hash}` / `{dependency_hash}`.
EQUATION_OR_MAPPING: `c_p=c_v+c_w+c_e`; `c_v^V=rho*c_v` requires same-regime density and uncertainty. No uncertainty is inferred from `Delta c_p`.
VERIFICATION: Raw hash, source locators, uncertainty boundary, no volumetric emission, Ding non-substitution, holdout non-access, and no fitting pass.
CONTROLLING_BLOCKER: `iaea_table_derived_cv_uncertainty_and_volumetric_conversion_not_source_locked`.
NEXT_ACTION: Acquire direct uncertainty-grade same-regime volumetric `c_v` or a same-state `Cp`/density/thermoelastic package; keep this comparator out of calibration and Ding `C_src` paths.
CLAIM_BOUNDARY: Scoped source no-go only; this does not close `alpha_Phi_K`, the UET bridge, EOS/transport/KMS/entropy, or Full Topic 13.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "IAEA c_v uncertainty and volumetric boundary", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - IAEA c_v uncertainty and volumetric boundary", report)
    manifest = f"""## IAEA c_v Uncertainty and Volumetric Boundary (2026-08-13)

Raw handbook: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/iaea_graphite_handbook_2017.pdf` (`{raw_hash}`).
Boundary package: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_cv_uncertainty_boundary_source_package.json` (`{package_hash}`).
Audit: `docs/core/07_artifacts/topic13/t13_iaea_cv_uncertainty_boundary_audit.json` (`{audit_hash}`).

The handbook table is retained as a mass-specific manufactured-graphite
comparator. Its probable-error `Delta c_p` is not promoted to a standard
uncertainty for `c_v`, and no same-row uncertainty-grade density/thermoelastic
package is emitted for a volumetric conversion or Ding substitution.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## IAEA c_v Uncertainty and Volumetric Boundary (2026-08-13)", manifest)
    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_text = f"""## Topic 13 IAEA c_v uncertainty boundary wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: IAEA uncertainty-boundary package; audit script/artifact/test; full-gate integration; report; update log; data manifest; registry sync
- verifier: `PASS_SCOPED_IAEA_CV_UNCERTAINTY_BOUNDARY_NO_GO`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: uncertainty-grade volumetric conversion route closed as a scoped no-go; no unsupported uncertainty was created
- hashes: raw `{raw_hash}`; package `{package_hash}`; audit `{audit_hash}`; full `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`
- remains: direct volumetric c_v or accepted same-state Cp/density/thermoelastic source, Ding C_src, base-Phi SI anchor, independent alpha, bridge/beta, physical transport, KMS, entropy, and dissipative balance
- next action: pursue direct uncertainty-grade same-regime volumetric c_v without Xie 2026 access or target fitting
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 IAEA c_v uncertainty boundary wave", ledger_text)
    print("recorded IAEA c_v uncertainty boundary wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
