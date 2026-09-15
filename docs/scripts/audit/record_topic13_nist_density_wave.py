from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

update_block = "\n".join(
    [
        "### 2026-08-13 - NIST AXM-5Q1 same-grade density source boundary",
        "",
        "MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY`.",
        "WHAT_IS_ACTUALLY_CLOSED: NIST SP 260-89 Table 1 specimen `103` is source-locked as AXM-5Q1 density `1.721 g cm^-3 = 1721 kg m^-3` at approximately 20 C, measured by hydrostatic weighing. The report's estimated `+/-0.1%` precision is preserved as a precision boundary, not promoted to a standard uncertainty.",
        "WHAT_REMAINS_OPEN: Density uncertainty, direct volumetric `c_v`, same-state `C_p`/`C_v` uncertainty, same-grade `alpha_V`/`K_T` pairing, Ding material-regime mapping, base-Phi anchor, and independent `alpha_Phi_K` remain open.",
        "DEPENDENCY_UNLOCKED: Same-grade AXM-5Q1 density availability only; no volumetric `c_v`, Ding source, alpha, bridge, transport, Core, Gravity, or Galaxy unlock.",
        "STATUS: `PASS_SCOPED_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.",
        "WHAT_CHANGED: Added `docs/scripts/audit/audit_topic13_nist_axm5q1_density_source_boundary.py`, source package `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/nist_axm5q1_density_source_package.json`, artifact `docs/core/07_artifacts/topic13/t13_nist_axm5q1_density_source_boundary_audit.json` (SHA-256 `7b33b0b2b51be34baa2ee11418d1c8cd389874cc8ceac3f3e3ef06fb8a655092`), focused test, full-gate integration, and register/dependency lane. Package SHA-256 is `9fa91225070b4b6091b0eb7c34295c5e0ab1a0316d282f26bd1f77df23269d5f`; full gate SHA-256 is `2030316aacac4f654b4ead1b1b59d4c034e9cd38596bb3243f16e66f10c1b4f7`; register SHA-256 is `4daf8f2100da208b2db053b575348ea039d2fa8756234a536bf721078a8be380`; dependency gate SHA-256 is `f6f572e999e736c175e24f626c287a5bae79a63d3f1c20ae5b14834796574187`.",
        "EQUATION_OR_MAPPING: `c_p^V = rho*c_p`; `c_v^V = rho*c_p - T*alpha_V^2*K_T`. The density row is an input boundary only; no `c_v`, `C_src`, `e0`, or `alpha_Phi_K` value is emitted.",
        "VERIFICATION: PDF presence/hash, source locators, hydrostatic method, unit conversion, row identity, precision-vs-uncertainty boundary, no direct `c_v`, no fit, no holdout access, and no alpha emission pass. Focused density/register tests pass (`2 passed`).",
        "CONTROLLING_BLOCKER: `density_uncertainty_not_source_locked` now controls this density route; full gate also retains `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`, `c_v_source_uncertainty_not_closed`, `direct_volumetric_c_v_or_same_state_Cp_source_missing`, alpha, bridge/beta, transport/KMS/entropy, dimensional-map, and material-regime blockers.",
        "NEXT_ACTION: Obtain a declared standard uncertainty or direct volumetric `c_v`/same-state `C_p` source, then match alpha_V and K_T to the same specimen/regime; do not use the density row as Ding C_src or alpha calibration.",
        "CLAIM_BOUNDARY: Same-grade density source availability only. It is not a volumetric heat-capacity calibration, Ding/HOPG match, UET transport validation, alpha calibration, TTG prediction, or Full Topic 13 closure.",
        "",
    ]
)

manifest_block = "\n".join(
    [
        "",
        "## NIST AXM-5Q1 Same-Grade Density Source Boundary (2026-08-13)",
        "",
        "MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY`.",
        "WHAT_IS_ACTUALLY_CLOSED: Table 1 specimen 103 is archived as `rho=1721 kg m^-3` at approximately 20 C by hydrostatic weighing, with source-stated estimated precision `+/-0.1%` retained as non-standard-uncertainty metadata.",
        "WHAT_REMAINS_OPEN: Density uncertainty, direct volumetric `c_v`, `C_p`/`C_v` uncertainty, same-state alpha_V/K_T, and Ding mapping remain open.",
        "DEPENDENCY_UNLOCKED: Same-grade density availability only; no downstream unlock.",
        "STATUS: `PASS_SCOPED_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY`; Full Topic 13 remains blocked.",
        "WHAT_CHANGED: Added source package/audit/test and integrated full gate and major-result register. Artifact SHA-256 `7b33b0b2b51be34baa2ee11418d1c8cd389874cc8ceac3f3e3ef06fb8a655092`; full gate SHA-256 `2030316aacac4f654b4ead1b1b59d4c034e9cd38596bb3243f16e66f10c1b4f7`.",
        "EQUATION_OR_MAPPING: Density supplies only the `rho` input to `c_p^V=rho*c_p`; no `c_v` is emitted.",
        "VERIFICATION: Source/hash/unit/precision-boundary checks pass; no fit or holdout access.",
        "CONTROLLING_BLOCKER: `density_uncertainty_not_source_locked`.",
        "NEXT_ACTION: Source-lock a standard uncertainty or direct volumetric `c_v` route with same-state alpha_V/K_T.",
        "CLAIM_BOUNDARY: Density availability boundary only, not Full Topic 13 closure.",
        "",
    ]
)

current_block = "\n".join(
    [
        "",
        "## NIST AXM-5Q1 Same-Grade Density Boundary (2026-08-13)",
        "",
        "MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY`.",
        "WHAT_IS_ACTUALLY_CLOSED: A same-grade AXM-5Q1 density row is source-locked at `1721 kg m^-3` (approximately 20 C, hydrostatic weighing), and its `+/-0.1%` source precision is explicitly kept separate from standard uncertainty.",
        "WHAT_REMAINS_OPEN: Density uncertainty, direct volumetric `c_v`, same-state `C_p/C_v`, alpha_V/K_T pairing, Ding material mapping, base-Phi, and independent alpha remain open.",
        "DEPENDENCY_UNLOCKED: Same-grade density availability only; no downstream dependency unlock.",
        "STATUS: `PASS_SCOPED_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.",
        "WHAT_CHANGED: Added and integrated the NIST density package/audit; full gate SHA-256 `2030316aacac4f654b4ead1b1b59d4c034e9cd38596bb3243f16e66f10c1b4f7`.",
        "EQUATION_OR_MAPPING: `c_p^V=rho*c_p`; density is an input boundary, not `c_v`, `C_src`, or alpha.",
        "VERIFICATION: Focused tests `2 passed`; source/hash/precision boundary pass; no fit or Xie 2026 access.",
        "CONTROLLING_BLOCKER: `density_uncertainty_not_source_locked` and the remaining `c_v`, Ding, alpha, bridge, transport, and mapping blockers.",
        "NEXT_ACTION: Obtain uncertainty-grade density or direct volumetric `c_v`/same-state `C_p` evidence.",
        "CLAIM_BOUNDARY: Same-grade density source availability only; not calibration, prediction, external validation, or Full Topic 13 closure.",
        "",
    ]
)

ledger_block = "\n".join(
    [
        "",
        "## Topic 13 NIST AXM-5Q1 same-grade density boundary wave",
        "",
        "- area: `research-core` (secondary: `result-artifacts`)",
        "- workspace: `docs/topics/0.13_Thermodynamic_Bridge`",
        "- files/artifacts: NIST density source package/audit/test; full gate; major-result register and dependency gate; topic records",
        "- verifier: focused density/register tests passed (`2 passed`); full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`",
        "- public-safety: `partial`",
        "- result: independent same-grade density availability closed for lane; source precision is not promoted to standard uncertainty; full blocker narrowed",
        "- hashes: density artifact `7b33b0b2b51be34baa2ee11418d1c8cd389874cc8ceac3f3e3ef06fb8a655092`; package `9fa91225070b4b6091b0eb7c34295c5e0ab1a0316d282f26bd1f77df23269d5f`; full gate `2030316aacac4f654b4ead1b1b59d4c034e9cd38596bb3243f16e66f10c1b4f7`; register `4daf8f2100da208b2db053b575348ea039d2fa8756234a536bf721078a8be380`; dependency gate `f6f572e999e736c175e24f626c287a5bae79a63d3f1c20ae5b14834796574187`",
        "- remains: density uncertainty, direct volumetric `c_v`, same-state Cp/Cv, alpha_V/K_T, Ding source/material mapping, base-Phi, alpha, bridge/beta, transport/KMS/entropy, and dimensional closure",
        "- next action: obtain uncertainty-grade density or direct volumetric heat-capacity evidence; no relabeling or holdout access",
        "- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree",
        "",
    ]
)


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")


append_once(ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md", "### 2026-08-13 - NIST AXM-5Q1 same-grade density source boundary", update_block)
append_once(ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md", "## NIST AXM-5Q1 Same-Grade Density Source Boundary (2026-08-13)", manifest_block)
append_once(ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "## NIST AXM-5Q1 Same-Grade Density Boundary (2026-08-13)", current_block)
append_once(ROOT / "WORK_LEDGER/2026/2026-08-13.md", "## Topic 13 NIST AXM-5Q1 same-grade density boundary wave", ledger_block)
print("recorded")
