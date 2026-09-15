from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
RAW = TOPIC / "Data/03_Research/raw/bipm_2006_01_graphite_specific_heat.pdf"
PACKAGE = TOPIC / "Data/03_Research/bipm_2006_01_graphite_specific_heat_source_package.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_bipm_specific_heat_source_audit.json"
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
    report = f"""### 2026-08-13 - BIPM graphite specific-heat comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: BIPM-2006/01 is archived from the OSTI mirror with raw PDF SHA-256 `{raw_hash}`. The report's sample-H relation gives `c_p=710.6 +/- 0.7 J kg^-1 K^-1` at 22 deg C, and the same report gives bulk density `1780 +/- 2 kg m^-3`; the source-locked volumetric comparator is `c_p^V=1264868 +/- 1890.0596392706766 J m^-3 K^-1` under independent first-order propagation.
WHAT_REMAINS_OPEN: This is `c_p^V`, not `c_v^V`; the `T*alpha_V^2*K_T` correction, Ding TTG material-regime mapping, numeric Ding `C_src`, base-Phi SI anchor, and independent `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: Source-locked ultra-pure graphite volumetric `c_p` comparator only; no `c_v`, Ding, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_BIPM_CP_COMPARATOR_CV_OPEN`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added the BIPM source package `{package_hash}`, audit artifact `{audit_hash}`, full-gate integration `{full_hash}`, and register/dependency synchronization `{register_hash}` / `{dependency_hash}`.
EQUATION_OR_MAPPING: `c_p^V=rho*c_p`; `c_v^V=c_p^V-T*alpha_V^2*K_T`. No `c_v`, `C_src`, `Delta_Tq=alpha_Phi_K*Delta_Phi`, or alpha calibration is emitted from this comparator.
VERIFICATION: Raw hash, source locators, units, 22 deg C scope, density and `c_p` uncertainty, volumetric conversion, holdout non-access, no target fit, and no alpha fit pass.
CONTROLLING_BLOCKER: `alpha_V_K_T_c_v_and_Ding_material_regime_mapping_missing`; the full gate also remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Acquire same-regime `alpha_V` and `K_T` or a direct volumetric `c_v` source with uncertainty; keep this comparator out of calibration and holdout paths.
CLAIM_BOUNDARY: Source-traceable BIPM ultra-pure graphite `c_p^V` comparator only. It is not `c_v`, not Ding/HOPG validation, not UET transport, not an alpha calibration, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "BIPM graphite specific-heat comparator lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - BIPM graphite specific-heat comparator lane", report)
    manifest = f"""## BIPM Graphite Specific-Heat Comparator (2026-08-13)

Raw report: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/bipm_2006_01_graphite_specific_heat.pdf` (`{raw_hash}`).
Source package: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/bipm_2006_01_graphite_specific_heat_source_package.json` (`{package_hash}`).
Audit: `docs/core/07_artifacts/topic13/t13_bipm_specific_heat_source_audit.json` (`{audit_hash}`).

The lane source-locks the report's sample-H mass-specific `c_p` and same-report
density, then computes a volumetric `c_p` comparator with uncertainty. It does
not emit `c_v`; `alpha_V`, `K_T`, and Ding material equivalence remain open.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## BIPM Graphite Specific-Heat Comparator (2026-08-13)", manifest)
    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_text = f"""## Topic 13 BIPM specific-heat comparator wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: BIPM raw PDF; source package; audit script/artifact/test; full-gate integration; report; update log; data manifest; registry sync
- verifier: `PASS_SCOPED_BIPM_CP_COMPARATOR_CV_OPEN`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: source-locked ultra-pure graphite volumetric `c_p` comparator closed for lane; `c_v` remains open
- hashes: raw `{raw_hash}`; package `{package_hash}`; audit `{audit_hash}`; full `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`
- remains: same-regime `alpha_V`/`K_T`, direct or corrected `c_v`, Ding `C_src`, material mapping, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: acquire uncertainty-grade same-regime `c_v` route without Xie 2026 access or target fitting
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 BIPM specific-heat comparator wave", ledger_text)
    print("recorded BIPM comparator wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
