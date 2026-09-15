"""Record the DeSorbo Ceylon graphite Cp comparator hardening wave."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
RAW = TOPIC / "Data/03_Research/raw/nist_srd69_graphite_desorbo_1955.html"
PACKAGE = TOPIC / "Data/03_Research/desorbo_1955_ceylon_graphite_cp_source_package.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_desorbo_ceylon_graphite_cp_audit.json"
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
    report = f"""### 2026-08-13 - DeSorbo Ceylon graphite numeric Cp comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The official NIST SRD 69 graphite table is archived with raw HTML SHA-256 `{raw_hash}`. The row attributed to DeSorbo 1955 records Ceylon natural graphite `Cp=7.841 J mol^-1 K^-1` at `298.15 K`; the primary paper identity, locator, and reported accuracy boundary are preserved.
WHAT_REMAINS_OPEN: The reported accuracy is not promoted to standard uncertainty; no source-locked density, volumetric `c_v`, `C_src`, or Ding TTG material equivalence is available from this lane.
DEPENDENCY_UNLOCKED: Ceylon natural-graphite numeric `Cp` comparator only; no `c_v`, Ding, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_DESORBO_CEYLON_GRAPHITE_CP_SOURCE_LOCKED_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added source package `{package_hash}`, audit artifact `{audit_hash}`, full-gate projection `{full_hash}`, and register/dependency synchronization `{register_hash}` / `{dependency_hash}`.
EQUATION_OR_MAPPING: `Cp,solid^m(298.15 K)=7.841 J mol^-1 K^-1`; downstream `c_v^V` conversion remains open. No `Delta_Tq=alpha_Phi_K*Delta_Phi` calibration is emitted.
VERIFICATION: Raw hash, NIST row identity, source locator, units, no-fit/no-target policy, no-Xie policy, no-alpha policy, and non-promotion of accuracy to standard uncertainty pass.
CONTROLLING_BLOCKER: `standard_uncertainty_density_and_Ding_material_mapping_missing`; full Topic 13 is still controlled additionally by Ding `C_src`, independent `alpha_Phi_K`, physical bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Acquire source-grade density and standard uncertainty for a material regime demonstrably compatible with Ding TTG, or retain this row as comparison-only evidence.
CLAIM_BOUNDARY: Source-traceable natural-graphite molar `Cp` comparator only. It is not volumetric `c_v`, not Ding/PBTE validation, not UET calibration, not external validation, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "DeSorbo Ceylon graphite numeric Cp comparator lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - DeSorbo Ceylon graphite numeric Cp comparator lane", report)
    manifest = f"""## DeSorbo Ceylon Graphite Numeric Cp Comparator (2026-08-13)

Raw archive: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/nist_srd69_graphite_desorbo_1955.html` (`{raw_hash}`).
Source package: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/desorbo_1955_ceylon_graphite_cp_source_package.json` (`{package_hash}`).
Audit: `docs/core/07_artifacts/topic13/t13_desorbo_ceylon_graphite_cp_audit.json` (`{audit_hash}`).

The lane source-locks the NIST row attributed to DeSorbo 1955 Ceylon natural
graphite at 298.15 K. It preserves the reported accuracy boundary without
relabeling it as standard uncertainty and emits no volumetric c_v or alpha.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## DeSorbo Ceylon Graphite Numeric Cp Comparator (2026-08-13)", manifest)
    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_text = f"""## Topic 13 DeSorbo Ceylon graphite Cp comparator wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: NIST HTML raw archive; source package; audit script/artifact/test; full-gate integration; report; update log; data manifest; register sync
- verifier: `PASS_DESORBO_CEYLON_GRAPHITE_CP_SOURCE_LOCKED_COMPARATOR`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: Ceylon natural-graphite numeric molar `Cp` comparator closed for lane; standard uncertainty, density, `c_v`, and Ding mapping remain open
- hashes: raw `{raw_hash}`; package `{package_hash}`; audit `{audit_hash}`; full `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`
- remains: Ding `C_src`, independent `alpha_Phi_K`, base-Phi SI anchor, source-grade density/uncertainty, material mapping, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: acquire a compatible uncertainty-grade volumetric `c_v` or same-regime Cp/density route without Xie 2026 access or target fitting
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 DeSorbo Ceylon graphite Cp comparator wave", ledger_text)
    print("recorded DeSorbo Ceylon graphite Cp comparator wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
