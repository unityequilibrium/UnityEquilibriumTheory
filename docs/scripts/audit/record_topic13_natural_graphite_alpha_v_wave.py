from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json"
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
        TOPIC / "Data/03_Research/raw/argonne_anl_5524_graphite_thermal_expansion_table.pdf"
    )
    report = f"""### 2026-08-13 - official Nelson-Riley natural graphite alpha_V comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The official OSTI/Argonne ANL-5524 report is archived with SHA-256 `{raw_hash}`; Table XIX gives `alpha_a=-1.5e-6 K^-1` over 0-150 deg C and `alpha_c=27.00e-6+3.05e-9*T_C K^-1`. At the declared approximate 27 deg C point, the deterministic family comparator is `alpha_V=24.08235e-6 K^-1`.
WHAT_REMAINS_OPEN: The source provides no row-level statistical uncertainty, does not identify the Hanfland specimen as the same state, and does not establish the Ding TTG material regime. Base-Phi mapping and `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: Official natural/crystalline graphite family alpha_V comparator only; no same-specimen `K_T`, Ding `C_src`, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_NATURAL_GRAPHITE_ALPHA_V_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/07_artifacts/topic13/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json` (SHA-256 `{artifact_hash}`), the ANL-5524 source package, and the archived official report; current full-gate hash is `{full_hash}`.
EQUATION_OR_MAPPING: `alpha_a=-1.5e-6 K^-1`; `alpha_c=27.00e-6+3.05e-9*T_C K^-1`; `alpha_V=2*alpha_a+alpha_c`. No uncertainty was invented where Table XIX gives none.
VERIFICATION: Source hash, Table XIX locator, Celsius/Kelvin scope, formula reconstruction, no-uncertainty boundary, no `K_T`, no target fit, no alpha fit, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `same_specimen_alpha_V_K_T_uncertainty_and_Ding_material_regime_mapping_missing`; full Topic 13 remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Find a same-state/same-specimen alpha_V and K_T source with uncertainty, or a permitted direct volumetric heat-capacity route; do not use this table as calibration.
CLAIM_BOUNDARY: Official natural/crystalline graphite family comparator only. It is not a same-specimen measurement, not a matched Hanfland state, not a Ding TTG material match, not UET transport, not an alpha calibration, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "official Nelson-Riley natural graphite alpha_V comparator lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - official Nelson-Riley natural graphite alpha_V comparator lane", report)

    manifest = f"""## Official Nelson-Riley Natural Graphite Alpha_V Comparator (2026-08-13)

The official Argonne/OSTI ANL-5524 report is archived at
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/argonne_anl_5524_graphite_thermal_expansion_table.pdf`
with SHA-256 `{raw_hash}`. The source package is
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/argonne_anl_5524_nelson_riley_alpha_v_source_package.json`.
The audit artifact is `docs/core/07_artifacts/topic13/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json`
with SHA-256 `{artifact_hash}`.

Table XIX reports the Nelson-Riley crystalline-graphite alpha_a interval and
alpha_c relation. The audit evaluates `alpha_V=2*alpha_a+alpha_c` at an
approximate room-temperature point but deliberately emits no statistical
uncertainty because the table does not provide one.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## Official Nelson-Riley Natural Graphite Alpha_V Comparator (2026-08-13)", manifest)

    formula = f"""## Official Nelson-Riley Natural Graphite Alpha_V Comparator (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-045` | `alpha_a=-1.5e-6 K^-1`; `alpha_c=27.00e-6+3.05e-9*T_C`; `alpha_V=2*alpha_a+alpha_c` | `docs/scripts/audit/audit_topic13_natural_graphite_nelson_riley_alpha_v_source.py`; `docs/core/07_artifacts/topic13/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json` | `T_C` = deg C; expansion coefficients = K^-1; comparison point = 300.15 K | Argonne ANL-5524 Table XIX, Nelson-Riley reported crystalline-graphite route | checked official table comparator; no UET derivation and no row uncertainty | source identity, table locator, temperature scope, formula reconstruction, and explicit uncertainty absence | no same-state uncertainty, no same specimen, and no Ding material mapping | source-lock same-specimen/same-state alpha_V and K_T with uncertainty or direct volumetric heat-capacity evidence |

Artifact hash: `{artifact_hash}`. The lane does not emit `K_T` or `alpha_Phi_K`, does not read Xie 2026, and does not promote `Phi` to temperature.
"""
    append_once(TOPIC / "FORMULA_AUDIT.md", "## Official Nelson-Riley Natural Graphite Alpha_V Comparator (2026-08-13)", formula)

    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_content = f"""## Topic 13 official Nelson-Riley alpha_V comparator wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: archived Argonne/OSTI report; natural graphite source package; alpha_V audit script/artifact/test; full-gate integration; formula audit; data manifest; current report; update log
- verifier: focused source and gate-integration tests passed; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: official crystalline/natural graphite alpha_V family comparator closed for lane without uncertainty or same-specimen promotion
- hashes: raw source `{raw_hash}`; audit artifact `{artifact_hash}`; full gate `{full_hash}`
- remains: matched alpha_V/K_T with uncertainty, Ding material mapping and C_src, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: acquire matched alpha_V/K_T or direct volumetric heat-capacity evidence without using Xie 2026 or target fitting
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 official Nelson-Riley alpha_V comparator wave", ledger_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
