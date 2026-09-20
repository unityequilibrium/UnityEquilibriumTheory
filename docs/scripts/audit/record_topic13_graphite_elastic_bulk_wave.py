from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_graphite_elastic_bulk_modulus_source_audit.json"
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
        TOPIC / "Data/03_Research/raw/bosak_2007_graphite_elasticity.pdf"
    )
    report = f"""### 2026-08-13 - Bosak graphite elastic bulk comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE`.
WHAT_IS_ACTUALLY_CLOSED: The Bosak et al. IXS primary PDF is archived with SHA-256 `{raw_hash}`; its room-temperature single-crystal graphite elastic tensor and reported `B=36.4 +/- 1.1 GPa` are transcribed, and the hexagonal compliance inversion reproduces `B_elastic=36.44001810774106 GPa`.
WHAT_REMAINS_OPEN: The IXS result is an elastic/dynamic comparator rather than a source-locked isothermal `K_T`; same-state `Cp/Cv`, Ding TTG material mapping, `Cp -> Cv`, base-Phi mapping, and `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: Source-locked graphite elastic bulk comparator only; no `K_T`, volumetric `c_v`, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_GRAPHITE_ELASTIC_BULK_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/07_artifacts/topic13/t13_graphite_elastic_bulk_modulus_source_audit.json` (SHA-256 `{artifact_hash}`), the Bosak source package, and the archived primary PDF; current full-gate hash is `{full_hash}`.
EQUATION_OR_MAPPING: `S=C_normal^-1`; `B_elastic=1/(2*S11+2*S12+4*S13+S33)`; no `C33 -> K_T` relabeling.
VERIFICATION: Source hash, page locators, tensor positivity, compliance inversion, central-value agreement, uncertainty declaration, no `K_T` emission, no target fit, no alpha fit, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `isothermal_K_T_material_regime_and_dynamic_to_thermal_conversion_missing` for this lane; the full gate remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Obtain a same-state isothermal `K_T` or a permitted dynamic-to-thermal conversion with matched `Cp/Cv` and material-state uncertainty; do not use the elastic comparator as `alpha_Phi_K`.
CLAIM_BOUNDARY: Internal/source-traceable single-crystal graphite elastic bulk comparator only. It is not `K_T`, not a Ding/HOPG material match, not UET transport, not an alpha calibration, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "Bosak graphite elastic bulk comparator lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - Bosak graphite elastic bulk comparator lane", report)

    manifest = f"""## Bosak Graphite Elastic Bulk Comparator (2026-08-13)

The primary Bosak et al. IXS PDF is archived at
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/bosak_2007_graphite_elasticity.pdf`
with SHA-256 `{raw_hash}`. The source package is
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/bosak_2007_graphite_elastic_bulk_source_package.json`.
The audit artifact is `docs/core/07_artifacts/topic13/t13_graphite_elastic_bulk_modulus_source_audit.json`
with SHA-256 `{artifact_hash}`.

The source reports the room-temperature single-crystal graphite tensor and
`B=36.4 +/- 1.1 GPa`; the audit independently reconstructs the hydrostatic
elastic comparator from the normal compliance block. This is not an isothermal
`K_T`, not a Ding/HOPG match, and not a UET calibration.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## Bosak Graphite Elastic Bulk Comparator (2026-08-13)", manifest)

    formula = f"""## Bosak Graphite Elastic Bulk Comparator (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-043` | `S=C_normal^-1`; `B_elastic=1/(2*S11+2*S12+4*S13+S33)` | `docs/scripts/audit/audit_topic13_graphite_elastic_bulk_modulus_source.py`; `docs/core/07_artifacts/topic13/t13_graphite_elastic_bulk_modulus_source_audit.json` | `C_ij` = GPa; `S_ij` = Pa^-1; `B_elastic` = Pa = J m^-3; source state = room-temperature single-crystal graphite | Bosak et al. 2007 IXS tensor, archived PDF, Table II | checked source comparator; not UET derivation and not isothermal `K_T` | source identity, unit-aware tensor inversion, and bulk-modulus reconstruction | dynamic/elastic B may not equal thermal isothermal `K_T`; no same-state `Cp/Cv` or Ding material mapping | source-lock same-state isothermal `K_T`, or derive a permitted dynamic-to-thermal conversion with matched `Cp/Cv` and uncertainty |

Artifact hash: `{artifact_hash}`. The lane does not emit `K_T` or `alpha_Phi_K`, does not read Xie 2026, and does not promote `Phi` to temperature.
"""
    append_once(TOPIC / "FORMULA_AUDIT.md", "## Bosak Graphite Elastic Bulk Comparator (2026-08-13)", formula)

    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_content = f"""## Topic 13 Bosak elastic bulk comparator wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: archived Bosak PDF; source package; elastic bulk audit script/artifact/test; full-gate integration; formula audit; data manifest; current report; update log
- verifier: focused elastic-bulk test passed; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: source-locked room-temperature elastic/dynamic bulk comparator closed for lane; isothermal `K_T` remains open
- hashes: raw source `{raw_hash}`; audit artifact `{artifact_hash}`; full gate `{full_hash}`
- remains: same-state isothermal `K_T` or dynamic-to-thermal conversion, Ding material mapping, C_src, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: acquire matched isothermal `K_T`/`Cp`/`Cv` evidence without using Xie 2026 or target fitting
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 Bosak elastic bulk comparator wave", ledger_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
