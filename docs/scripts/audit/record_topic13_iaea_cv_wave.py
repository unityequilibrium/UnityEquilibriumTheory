from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
RAW = TOPIC / "Data/03_Research/raw/iaea_graphite_handbook_2017.pdf"
PACKAGE = TOPIC / "Data/03_Research/iaea_graphite_handbook_constant_volume_source_package.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_iaea_graphite_constant_volume_source_audit.json"
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
    report = f"""### 2026-08-13 - IAEA manufactured-graphite table-derived c_v comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The IAEA-hosted Graphite Engineering Handbook is archived with raw PDF SHA-256 `{raw_hash}`. Table 4.11 at 300 K gives `c_p=0.1723`, `Delta c_p=0.0017`, `c_w=0.00069`, and `c_e=0.00009 cal g^-1 K^-1`; the declared table relation `c_v=c_p-c_w-c_e` gives `c_v=0.17152 cal g^-1 K^-1 = 717.63968 J kg^-1 K^-1`.
WHAT_REMAINS_OPEN: The handbook's `Delta c_p` is a probable-error envelope, not a standard uncertainty for `c_v`; `c_w` depends on density, expansion, and compressibility; no same-grade density/volumetric conversion or Ding material match is established.
DEPENDENCY_UNLOCKED: Source-traceable manufactured-graphite mass-specific lattice `c_v` comparator only; no volumetric `c_v`, Ding `C_src`, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_IAEA_TABLE_CV_COMPARATOR_UNCERTAINTY_OPEN`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added IAEA source package `{package_hash}`, audit `{audit_hash}`, full-gate integration `{full_hash}`, and registry/dependency synchronization `{register_hash}` / `{dependency_hash}`.
EQUATION_OR_MAPPING: `c_p=c_v+c_w+c_e`; `c_v=c_p-c_w-c_e`. No volumetric `c_v`, `C_src`, `Delta_Tq=alpha_Phi_K*Delta_Phi`, or alpha calibration is emitted.
VERIFICATION: Raw hash, Table 4.11 locator, 300 K row, formula reconstruction, calorie conversion, uncertainty boundary, material mismatch, holdout non-access, no target fit, and no alpha fit pass.
CONTROLLING_BLOCKER: `cv_uncertainty_density_volumetric_conversion_and_Ding_material_regime_mapping_missing`; the full gate also remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Acquire source-grade `c_v` uncertainty plus same-grade density or direct volumetric `c_v`; keep the table-derived comparator out of calibration and holdout paths.
CLAIM_BOUNDARY: Source-traceable IAEA table-derived manufactured-graphite mass-specific lattice `c_v` comparator only. It is not volumetric `c_v`, not Ding/HOPG validation, not UET transport, not an alpha calibration, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "IAEA manufactured-graphite table-derived c_v comparator lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - IAEA manufactured-graphite table-derived c_v comparator lane", report)
    manifest = f"""## IAEA Manufactured-Graphite Table-Derived c_v Comparator (2026-08-13)

Raw handbook: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/iaea_graphite_handbook_2017.pdf` (`{raw_hash}`).
Source package: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_handbook_constant_volume_source_package.json` (`{package_hash}`).
Audit: `docs/core/07_artifacts/topic13/t13_iaea_graphite_constant_volume_source_audit.json` (`{audit_hash}`).

Table 4.11 supplies a manufactured-graphite table-derived mass-specific
lattice `c_v` at 300 K. The probable error in `c_p` is retained as such;
because `c_w` and the density conversion lack source-grade uncertainty, this
lane does not emit volumetric `c_v` or calibration values.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## IAEA Manufactured-Graphite Table-Derived c_v Comparator (2026-08-13)", manifest)
    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_text = f"""## Topic 13 IAEA table-derived c_v comparator wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: IAEA handbook PDF; source package; audit script/artifact/test; full-gate integration; report; update log; data manifest; registry sync
- verifier: `PASS_SCOPED_IAEA_TABLE_CV_COMPARATOR_UNCERTAINTY_OPEN`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: source-traceable mass-specific lattice `c_v` comparator closed for lane; volumetric `c_v` and uncertainty remain open
- hashes: raw `{raw_hash}`; package `{package_hash}`; audit `{audit_hash}`; full `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`
- remains: source-grade `c_v` uncertainty, density/volumetric conversion, Ding material mapping, C_src, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: acquire uncertainty-grade same-regime volumetric `c_v` or same-state `Cp`/density package without Xie 2026 access or target fitting
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 IAEA table-derived c_v comparator wave", ledger_text)
    print("recorded IAEA c_v comparator wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
