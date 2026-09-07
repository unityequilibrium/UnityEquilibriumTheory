from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
RAW = TOPIC / "Data/03_Research/raw/npl_rsa40_graphite_specific_heat.pdf"
PACKAGE = TOPIC / "Data/03_Research/npl_rsa40_graphite_specific_heat_source_package.json"
AUDIT = ROOT / "docs/core/artifacts/t13_npl_rsa40_graphite_specific_heat_audit.json"
FULL = TOPIC / "Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


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
    report = f"""### 2026-08-22 - NPL IG-11 graphite c_p uncertainty comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NPL_GRAPHITE_CP_UNCERTAINTY_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: NPL RSA(EXT)40 is archived with raw PDF SHA-256 `{raw_hash}`. The source reports Southern Graphite IG-11 graphite, `c_p=710.6 +/- 0.7 J kg^-1 K^-1` at 22 deg C, a 19-25 deg C scope, and a combined relative uncertainty budget of `9.6e-4`.
WHAT_REMAINS_OPEN: This is mass-specific `c_p`, not source-grade volumetric `c_v` or Ding `C_src`; density uncertainty, `alpha_V/K_T`, Ding material mapping, independent `alpha_Phi_K`, and the full thermodynamic bridge remain open.
DEPENDENCY_UNLOCKED: Source-locked IG-11 `c_p` uncertainty comparator only; no `c_v`, Ding, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_NPL_CP_UNCERTAINTY_COMPARATOR_CV_OPEN`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added the NPL source package `{package_hash}`, audit artifact `{audit_hash}`, full-gate projection `{full_hash}`, and register/dependency synchronization `{register_hash}` / `{dependency_hash}`.
EQUATION_OR_MAPPING: `c_p,g(T,H)=710.6+3.0(T-22 deg C) J kg^-1 K^-1`; nominal `rho*c_p` is a cross-check only; `c_v^V=c_p^V-T*alpha_V^2*K_T` remains open.
VERIFICATION: Raw hash, PDF signature, source locators, material identity, units, source-reported uncertainty, no volumetric uncertainty promotion, no target fit, no alpha fit, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `c_v_conversion_density_uncertainty_and_Ding_material_mapping_missing`; globally the independent dimensional/alpha, Ding `C_src`, physical Kubo, EOS/transport/KMS/entropy, and base-Phi mapping blockers remain controlling.
NEXT_ACTION: Acquire same-regime `alpha_V` and `K_T` or direct volumetric `c_v`/Ding `C_src` evidence, plus an independent base-Phi/SI record; keep this comparator outside calibration and holdout paths.
CLAIM_BOUNDARY: Source-traceable NPL IG-11 mass-specific `c_p` comparator only. It is not `c_v`, not Ding/HOPG validation, not UET transport, not an alpha calibration, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "NPL IG-11 graphite c_p uncertainty comparator lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-22 - NPL IG-11 graphite c_p uncertainty comparator lane", report)
    manifest = f"""## NPL IG-11 Graphite c_p Uncertainty Comparator (2026-08-22)

Raw report: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/npl_rsa40_graphite_specific_heat.pdf` (`{raw_hash}`).
Source package: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/npl_rsa40_graphite_specific_heat_source_package.json` (`{package_hash}`).
Audit: `docs/core/artifacts/t13_npl_rsa40_graphite_specific_heat_audit.json` (`{audit_hash}`).

The lane source-locks the NPL IG-11 mass-specific `c_p` relation and its
reported uncertainty. The nominal density product is kept as a cross-check
only because the locked sample description does not provide density uncertainty.
No `c_v`, Ding `C_src`, `alpha_Phi_K`, target fit, or holdout access is emitted.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## NPL IG-11 Graphite c_p Uncertainty Comparator (2026-08-22)", manifest)
    ledger = ROOT / "WORK_LEDGER/2026/2026-08-22.md"
    ledger_text = f"""## Topic 13 NPL IG-11 c_p uncertainty comparator wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: NPL raw PDF; source package; audit script/artifact/test; full-gate integration; report; update log; data manifest; registry sync
- verifier: `PASS_SCOPED_NPL_CP_UNCERTAINTY_COMPARATOR_CV_OPEN`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: source-locked IG-11 mass-specific `c_p` comparator with reported uncertainty closed for lane; `c_v` remains open
- hashes: raw `{raw_hash}`; package `{package_hash}`; audit `{audit_hash}`; full `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`
- remains: density uncertainty, same-grade `alpha_V/K_T`, Ding `C_src`, material mapping, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: acquire a permitted same-regime volumetric `c_v`/Ding `C_src` route and independent paired base-Phi/SI record without Xie 2026 access or target fitting
- commit/push action: keep this wave scoped and committed separately from unrelated worktree changes
"""
    append_once(ledger, "## Topic 13 NPL IG-11 c_p uncertainty comparator wave", ledger_text)
    print("recorded NPL IG-11 c_p comparator wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
