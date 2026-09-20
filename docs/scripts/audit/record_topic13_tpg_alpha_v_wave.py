from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_tpg_anisotropic_alpha_v_source_audit.json"
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
        TOPIC / "Data/03_Research/raw/ihep_2001_32_tpg_thermal_expansion.pdf"
    )
    report = f"""### 2026-08-13 - IHEP TPG anisotropic alpha_V comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The IHEP 2001-32 report is archived with SHA-256 `{raw_hash}`; its ATOMGRAPH TPG in-plane row `alpha_a=-1.04 +/- 0.11e-6 K^-1` and averaged TPG out-of-plane row `alpha_c=26.84 +/- 0.4e-6 K^-1` are source-locked over the reported near-room-temperature range. The explicit family comparator is `alpha_V=24.76e-6 K^-1` with propagated comparator uncertainty `0.4565085979e-6 K^-1`.
WHAT_REMAINS_OPEN: The two axes are not a same-specimen, same-point pair; same-state density/Cp/Cv, Ding TTG material mapping, base-Phi SI mapping, and `alpha_Phi_K` remain open. This comparator does not close the Hanfland `K_T` lane.
DEPENDENCY_UNLOCKED: Source-locked TPG family-level `alpha_V` comparator only; no same-grade `K_T`, Ding `C_src`, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/07_artifacts/topic13/t13_tpg_anisotropic_alpha_v_source_audit.json` (SHA-256 `{artifact_hash}`), the IHEP source package, and the archived primary report; current full-gate hash is `{full_hash}`.
EQUATION_OR_MAPPING: `alpha_V=2*alpha_a+alpha_c`; uncertainty is propagated only as a zero-covariance comparator assumption. The source scope is approximately 25-60 deg C, not an exact 300 K point.
VERIFICATION: Source hash, report locators, units, sign and range checks, anisotropic reconstruction, uncertainty boundary, mixed-row boundary, no `K_T`, no target fit, no alpha fit, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `same_specimen_alpha_V_K_T_and_Ding_material_regime_mapping_missing`; full Topic 13 is still controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Acquire a same-state/same-specimen `alpha_V` and `K_T` pair or a permitted direct volumetric heat-capacity route; keep this family comparator out of calibration and holdout paths.
CLAIM_BOUNDARY: Internal/source-traceable TPG family-level expansion comparator only. It is not a same-specimen volumetric measurement, not a Ding/HOPG material match, not UET transport, not an alpha calibration, and not Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "IHEP TPG anisotropic alpha_V comparator lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - IHEP TPG anisotropic alpha_V comparator lane", report)

    manifest = f"""## IHEP TPG Anisotropic Alpha_V Comparator (2026-08-13)

The IHEP 2001-32 primary report is archived at
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ihep_2001_32_tpg_thermal_expansion.pdf`
with SHA-256 `{raw_hash}`. The source package is
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ihep_2001_32_tpg_anisotropic_alpha_v_source_package.json`.
The audit artifact is `docs/core/07_artifacts/topic13/t13_tpg_anisotropic_alpha_v_source_audit.json`
with SHA-256 `{artifact_hash}`.

The report supplies separate near-room-temperature in-plane and out-of-plane
TPG slopes. The audit computes the explicitly bounded family comparator
`alpha_V=2*alpha_a+alpha_c`; because the rows are not a same-specimen pair,
the result is not promoted to a same-state volumetric measurement or UET
calibration.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## IHEP TPG Anisotropic Alpha_V Comparator (2026-08-13)", manifest)

    formula = f"""## IHEP TPG Anisotropic Alpha_V Comparator (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-044` | `alpha_V=2*alpha_a+alpha_c`; `u(alpha_V)=sqrt((2*u(alpha_a))^2+u(alpha_c)^2)` | `docs/scripts/audit/audit_topic13_tpg_anisotropic_alpha_v_source.py`; `docs/core/07_artifacts/topic13/t13_tpg_anisotropic_alpha_v_source_audit.json` | `alpha_a`, `alpha_c`, `alpha_V` = K^-1; source scope approximately 25-60 deg C | IHEP 2001-32 TPG linear-expansion rows; zero covariance is an explicit comparator assumption, not source covariance | checked source comparator; not UET derivation and not same-specimen closure | source identity, anisotropic relation, range, sign, and uncertainty-boundary checks | separate axis rows, no same-state `K_T`/`Cp`/`Cv`, and no Ding material mapping | source-lock a same-specimen/same-state alpha_V and K_T pair or permitted direct volumetric heat-capacity route |

Artifact hash: `{artifact_hash}`. The lane does not emit `K_T` or `alpha_Phi_K`, does not read Xie 2026, and does not promote `Phi` to temperature.
"""
    append_once(TOPIC / "FORMULA_AUDIT.md", "## IHEP TPG Anisotropic Alpha_V Comparator (2026-08-13)", formula)

    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_content = f"""## Topic 13 IHEP TPG alpha_V comparator wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: archived IHEP/CERN report; TPG source package; alpha_V audit script/artifact/test; full-gate integration; formula audit; data manifest; current report; update log
- verifier: focused source and gate-integration tests passed; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: source-locked TPG family-level anisotropic alpha_V comparator closed for lane; same-specimen alpha_V/K_T remains open
- hashes: raw source `{raw_hash}`; audit artifact `{artifact_hash}`; full gate `{full_hash}`
- remains: same-specimen/same-state alpha_V and K_T, Ding material mapping and C_src, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: acquire matched alpha_V/K_T or direct volumetric heat-capacity evidence without using Xie 2026 or target fitting
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 IHEP TPG alpha_V comparator wave", ledger_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
