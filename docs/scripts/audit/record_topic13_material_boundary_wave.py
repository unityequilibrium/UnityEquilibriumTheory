from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
RAW = TOPIC / "Data/03_Research/raw/ding_2022_supplementary_information.pdf"
PACKAGE = TOPIC / "Data/03_Research/ding_graphite_material_regime_boundary_source_package.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_material_regime_boundary_audit.json"
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
    report = f"""### 2026-08-13 - Ding/comparator material-regime boundary lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_DING_MATERIAL_REGIME_BOUNDARY`.
WHAT_IS_ACTUALLY_CLOSED: Ding's supplementary source locks a natural graphite crystal TTG specimen and reports grain characterization at p. 11 (`382 +/- 270 um^2` average grain area; typical grain size greater than 20 um). The lane compares this target with MP48 ideal AB graphite, NIST AXM-5Q1, BIPM Carbone Lorraine graphite, IAEA manufactured graphite, and Huang isotopically purified ribbons; none is declared equivalent without an explicit material/state/PBTE mapping.
WHAT_REMAINS_OPEN: Numeric Ding `C_src`, same-grade volumetric heat-capacity uncertainty, and an accepted material/state/PBTE equivalence mapping remain open. Comparator `c_v`/`c_p` values remain comparison-only.
DEPENDENCY_UNLOCKED: Material-equivalence no-go only; no Ding `C_src`, alpha calibration, bridge, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_DING_MATERIAL_REGIME_BOUNDARY_NO_GO`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added material-boundary source package `{package_hash}`, audit `{audit_hash}`, full-gate integration `{full_hash}`, and registry/dependency synchronization `{register_hash}` / `{dependency_hash}`.
EQUATION_OR_MAPPING: `C_src(T)=sum_mu c_mu(T)` remains Ding's source PBTE quantity; `material_regime_equivalent_to_Ding` is explicitly `false` for all archived comparator lanes.
VERIFICATION: Ding raw hash and p. 11 locator, comparator package identity, explicit equivalence rule, no silent relabeling, no fit, no alpha calibration, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `material_regime_mapping_to_TTG_not_closed` is now a named no-go boundary; numeric Ding `C_src`, source-grade volumetric uncertainty, independent `alpha_Phi_K`, bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping remain controlling.
NEXT_ACTION: Obtain an authorized Ding mode-resolved PBTE payload or a genuinely matched same-material/state reproduction; do not substitute MP48 or graphite-grade comparators.
CLAIM_BOUNDARY: This closes only the evidence boundary against silent material substitution. It is not a claim that the comparator physics is false, not Ding validation, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "Ding/comparator material-regime boundary lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - Ding/comparator material-regime boundary lane", report)
    manifest = f"""## Ding/Comparator Material-Regime Boundary (2026-08-13)

Target supplementary source: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_information.pdf` (`{raw_hash}`).
Package: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_graphite_material_regime_boundary_source_package.json` (`{package_hash}`).
Audit: `docs/core/07_artifacts/topic13/t13_ding_material_regime_boundary_audit.json` (`{audit_hash}`).

The boundary records why ideal, manufactured, isotopically purified, and
fine-grained graphite comparators cannot be silently promoted to Ding's
natural-graphite TTG/PBTE regime. The lane closes the equivalence question as
not established; it does not create a numeric `C_src`.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## Ding/Comparator Material-Regime Boundary (2026-08-13)", manifest)
    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_text = f"""## Topic 13 Ding material-regime boundary wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: Ding supplementary characterization; material-boundary package; audit script/artifact/test; full-gate integration; report; update log; data manifest; registry sync
- verifier: `PASS_SCOPED_DING_MATERIAL_REGIME_BOUNDARY_NO_GO`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: silent comparator substitution is closed as a scoped no-go; Ding `C_src` remains open
- hashes: Ding raw `{raw_hash}`; package `{package_hash}`; audit `{audit_hash}`; full `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`
- remains: authorized numeric Ding payload or matched reproduction, source-grade volumetric uncertainty, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: obtain matched Ding-regime PBTE inputs or preserve the no-go boundary; no MP48/comparator substitution
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 Ding material-regime boundary wave", ledger_text)
    print("recorded Ding material-regime boundary wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
