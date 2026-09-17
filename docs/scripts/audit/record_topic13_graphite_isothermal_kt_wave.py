from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_graphite_isothermal_kt_source_audit.json"
FULL_GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
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
    artifact_hash = sha256(ARTIFACT)
    full_hash = sha256(FULL_GATE)
    raw_hash = sha256(
        TOPIC / "Data/03_Research/raw/hanfland_1989_graphite_equation_of_state.pdf"
    )
    report = f"""### 2026-08-13 - Hanfland graphite isothermal K_T source lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_GRAPHITE_ISOTHERMAL_KT_SOURCE`.
WHAT_IS_ACTUALLY_CLOSED: The Hanfland et al. primary XRD equation-of-state PDF is archived with SHA-256 `{raw_hash}`; its fixed-temperature `T=300 K` ambient-pressure graphite EOS row is source-locked as `K_T=33.8 +/- 3.0 GPa` with the reported reference volume and pressure derivative.
WHAT_REMAINS_OPEN: Same-grade alpha_V and density uncertainty, mapping from natural graphite powder to the Ding TTG material, temperature-resolved K_T, matched Cp/Cv, base-Phi mapping, and independent `alpha_Phi_K` remain open. No local pressure-volume refit was performed.
DEPENDENCY_UNLOCKED: Declared 300 K natural-graphite isothermal K_T source lane only; no same-grade Cp-to-Cv, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_ISOTHERMAL_GRAPHITE_K_T_SOURCE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/07_artifacts/topic13/t13_graphite_isothermal_kt_source_audit.json` (SHA-256 `{artifact_hash}`), the Hanfland source package, and the archived primary PDF; current full-gate hash is `{full_hash}`.
EQUATION_OR_MAPPING: `K_T=-V*(partial P/partial V)_T=dP/d(-ln V)`; source Murnaghan fit at `T=300 K`, `P=0` gives `33.8 +/- 3.0 GPa`; this is not inferred from `C33`.
VERIFICATION: Source hash, page locators, fixed-temperature XRD method, isothermal derivative definition, scalar row identity, uncertainty, no figure refit, no target fit, no alpha fit, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `same_grade_alpha_V_K_T_and_Ding_material_regime_mapping_missing` for this lane; the full gate still requires Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Match this `K_T` to the Ding TTG material and acquire same-state alpha_V/density/Cp/Cv uncertainty; do not combine it with NIST AXM-5Q1 alpha_V without a material-state map.
CLAIM_BOUNDARY: Source-traceable 300 K natural-graphite K_T input only. It is not a Ding/HOPG match, not complete Cp-to-Cv closure, not UET transport, not an alpha calibration, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "Hanfland graphite isothermal K_T source lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - Hanfland graphite isothermal K_T source lane", report)

    manifest = f"""## Hanfland Graphite Isothermal K_T Source (2026-08-13)

The primary Hanfland et al. EOS PDF is archived at
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/hanfland_1989_graphite_equation_of_state.pdf`
with SHA-256 `{raw_hash}`. The source package is
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/hanfland_1989_graphite_isothermal_kt_source_package.json`.
The audit artifact is `docs/core/07_artifacts/topic13/t13_graphite_isothermal_kt_source_audit.json`
with SHA-256 `{artifact_hash}`.

The scalar row is the fixed-temperature 300 K ambient-pressure EOS input
`K_T=33.8 +/- 3.0 GPa`. It is source-locked as a declared standard comparator,
but material matching and same-state alpha_V/Cp/Cv remain open.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## Hanfland Graphite Isothermal K_T Source (2026-08-13)", manifest)

    formula = f"""## Hanfland Graphite Isothermal K_T Source (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-044` | `K_T(T0,P0)=-V*(partial P/partial V)_T=dP/d(-ln V)`; source row `K_T(300 K,0)=33.8 +/- 3.0 GPa` | `docs/scripts/audit/audit_topic13_graphite_isothermal_kt_source.py`; `docs/core/07_artifacts/topic13/t13_graphite_isothermal_kt_source_audit.json` | `T` = K; `P` = GPa; `V` = Angstrom^3 per cell; `K_T` = GPa = 10^9 Pa | Hanfland et al. 1989 fixed-temperature powder-XRD Murnaghan EOS, archived PDF | source-locked standard thermodynamic input; no local refit and no UET derivation | source provenance, isothermal definition, scalar row identity, uncertainty, and unit boundary | natural graphite powder is not shown to be the Ding TTG sample; same-state alpha_V/density/Cp/Cv and temperature dependence remain open | map the K_T state to Ding, source-lock same-state alpha_V/density/Cp/Cv, then run Cp-to-Cv with uncertainty |

Artifact hash: `{artifact_hash}`. The lane emits the declared standard `K_T` input but no `alpha_Phi_K`, does not read Xie 2026, and does not promote `Phi` to temperature.
"""
    append_once(TOPIC / "FORMULA_AUDIT.md", "## Hanfland Graphite Isothermal K_T Source (2026-08-13)", formula)

    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_content = f"""## Topic 13 Hanfland isothermal K_T source wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: archived Hanfland PDF; isothermal K_T source package; audit script/artifact/test; full-gate integration; formula audit; data manifest; current report; update log
- verifier: focused K_T source and integration tests passed; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: 300 K natural-graphite isothermal K_T scalar source closed for lane; same-grade/material mapping and Cp-to-Cv remain open
- hashes: raw source `{raw_hash}`; audit artifact `{artifact_hash}`; full gate `{full_hash}`
- remains: Ding material mapping, same-state alpha_V/density/Cp/Cv, temperature-resolved K_T, C_src, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: establish same-state material correspondence and run the Cp-to-Cv contract only after all inputs are source-locked
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 Hanfland isothermal K_T source wave", ledger_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
