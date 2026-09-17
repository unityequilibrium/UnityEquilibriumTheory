from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_nist_graphite_alpha_v_source_boundary_audit.json"
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
    report = f"""### 2026-08-13 - NIST graphite alpha_V source boundary lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY`.
WHAT_IS_ACTUALLY_CLOSED: Official NIST SP 260-89 AXM-5Q1 graphite source is archived with SHA-256 `{sha256(ARTIFACT.parent.parent.parent / 'topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/nist_sp260_89_graphite.pdf')}`; its declared length-expansion polynomial is evaluated at 200, 225, 250, and 300 K and converted explicitly to an isotropic `alpha_V` comparator.
WHAT_REMAINS_OPEN: `K_T` is not source-locked, the AXM-5Q1 comparator is not established as Ding/HOPG material equivalence, row-level statistical uncertainty is absent, and `Cp -> Cv`, Ding `C_src`, base-Phi mapping, and `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: NIST alpha_V source-comparator lane only; no `K_T`, volumetric `c_v`, Ding source, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_NIST_ALPHA_V_SOURCE_BOUNDARY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/07_artifacts/topic13/t13_nist_graphite_alpha_v_source_boundary_audit.json` (SHA-256 `{artifact_hash}`) and linked it into the Topic 13 full gate (SHA-256 `{full_hash}`).
EQUATION_OR_MAPPING: `Delta_L/L[%] = -0.201 + 6.595e-4*T + 9.593e-8*T^2 - 3.427e-12*T^3`, `alpha_L = d(Delta_L/L)/dT/(1+Delta_L/L)`, and comparator `alpha_V=3 alpha_L`.
VERIFICATION: PDF presence and hash, source locators, explicit percent-to-strain conversion, finite rows, NIST program accuracy boundary, no invented `K_T`, no target fit, no alpha fit, and no Xie 2026 access. At 300 K the comparator gives `alpha_V = 2.1482823124269745e-5 K^-1`.
CONTROLLING_BLOCKER: `isothermal_bulk_modulus_K_T_and_Ding_material_regime_mapping_missing` for this lane; full Topic 13 remains controlled by the existing Ding source, alpha, bridge/beta, EOS/transport/KMS/entropy, and SI-map blockers.
NEXT_ACTION: Obtain source-locked `K_T` with uncertainty for a declared material state and explicit mapping to the TTG sample; do not combine this comparator with Ding `C_src` or use it as a base-Phi calibration.
CLAIM_BOUNDARY: Internal/source-traceable AXM-5Q1 alpha_V comparator only. It is not a Ding/HOPG material match, complete `Cp -> Cv` closure, UET transport validation, `alpha_Phi_K`, or Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "NIST graphite alpha_V source boundary lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - NIST graphite alpha_V source boundary lane", report)

    manifest = f"""## NIST Graphite alpha_V Source Boundary (2026-08-13)

The official NIST SP 260-89 PDF is archived at
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/nist_sp260_89_graphite.pdf`.
The audit artifact is `{ARTIFACT.relative_to(ROOT).as_posix()}` with SHA-256
`{artifact_hash}` and the current full-gate hash is `{full_hash}`.

The lane evaluates the declared AXM-5Q1 length-expansion polynomial and reports
an explicit isotropic `alpha_V` comparator at 200, 225, 250, and 300 K. It is a
source boundary only: no `K_T`, Ding/HOPG material equivalence, volumetric
`c_v`, `alpha_Phi_K`, or Xie 2026 holdout claim is made.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## NIST Graphite alpha_V Source Boundary (2026-08-13)", manifest)

    formula = f"""## NIST Graphite alpha_V Source Boundary (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-042` | `Delta_L/L[%] = -0.201 + 6.595e-4*T + 9.593e-8*T^2 - 3.427e-12*T^3`; `alpha_L=d(Delta_L/L)/dT/(1+Delta_L/L)`; `alpha_V=3 alpha_L` | `docs/scripts/audit/audit_topic13_nist_graphite_alpha_v_source_boundary.py`; `docs/core/07_artifacts/topic13/t13_nist_graphite_alpha_v_source_boundary_audit.json` | `T` = K; strain dimensionless; `alpha_L`, `alpha_V` = K^-1 | NIST SP 260-89 Eq. (5.5.2), Table 20 and archived PDF | checked source-boundary comparator; not UET derivation | source/provenance and standard thermodynamic geometry comparator | AXM-5Q1 state, isotropy assumption, program-level accuracy, missing `K_T`, and missing Ding sample mapping prevent `Cp -> Cv` promotion | source-lock `K_T` and material-state correspondence with uncertainty; keep alpha and base-Phi calibration separate |

Artifact hash: `{artifact_hash}`. Full-gate hash after integration: `{full_hash}`. The lane does not emit `alpha_Phi_K` and does not read Xie 2026.
"""
    append_once(TOPIC / "FORMULA_AUDIT.md", "## NIST Graphite alpha_V Source Boundary (2026-08-13)", formula)

    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_content = f"""## Topic 13 NIST alpha_V source-boundary wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: NIST PDF source archive; alpha_V audit script/test/artifact; Topic 13 full-gate integration; formula audit; data manifest; current report; update log
- verifier: NIST focused test passed; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; Topic 13 regression rerun is required after this wave
- public-safety: `partial`
- result: source-traceable AXM-5Q1 alpha_V comparator closed for lane; `K_T`, Ding/HOPG mapping, `c_v`, and alpha remain open
- hashes: alpha_V artifact `{artifact_hash}`; full gate `{full_hash}`
- remains: source-locked `K_T`, same-grade/matched material contract, Ding mode-resolved `C_src`, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: source-lock `K_T` with uncertainty and explicit material mapping without using Xie 2026 or target fitting
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 NIST alpha_V source-boundary wave", ledger_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
