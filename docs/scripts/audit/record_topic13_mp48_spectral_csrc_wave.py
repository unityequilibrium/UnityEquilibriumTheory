from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_spectral_csrc_reproduction_audit.json"
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
    report = f"""### 2026-08-13 - MP48 harmonic spectral C_src-like cross-file lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_MP48_SPECTRAL_C_SRC_REPRODUCTION`.
WHAT_IS_ACTUALLY_CLOSED: The archived MP48 total DOS and deposited harmonic thermal-properties file reproduce a C_src-like spectral heat-capacity row at 200, 250, and 300 K with explicit quadrature and source hashes.
WHAT_REMAINS_OPEN: This is not Ding PBTE `C_src`, does not establish Ding material-regime equivalence, does not provide PBTE mode-resolved uncertainty/convergence, and does not supply the base-Phi energy anchor or `alpha_Phi_K`.
DEPENDENCY_UNLOCKED: MP48 harmonic spectral consistency lane only; no source, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_HARMONIC_DOS_CROSS_FILE_REPRODUCTION`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/07_artifacts/topic13/t13_mp48_spectral_csrc_reproduction_audit.json` (SHA-256 `{artifact_hash}`) and linked it into the Topic 13 full gate (SHA-256 `{full_hash}`).
EQUATION_OR_MAPPING: `c_mu(T) = k_B x_mu^2 exp(x_mu)/(exp(x_mu)-1)^2`, `C_src^DOS = N_A integral[g(nu)c(nu,T)dnu]`; this is the harmonic MP48 comparator and is not relabeled as Ding `C_src`.
VERIFICATION: 201-row uniform DOS grid, deposited rows at 200/250/300 K, finite kernel values, trapezoid/Simpson/every-second-bin envelope, source hashes, no target fit, no alpha fit, and no holdout access. Maximum trapezoid residual is `0.009992863239339345`; maximum coarse-grid difference is `0.014787789991730582`.
CONTROLLING_BLOCKER: `Ding_material_regime_and_mode_resolved_C_src_acceptance_missing` for this lane; the full gate remains controlled by the existing Ding source, dimensional alpha, bridge/beta, EOS/transport/KMS/entropy, and SI-map blockers.
NEXT_ACTION: Obtain Ding-compatible mode-resolved `C_src(T)` or an accepted same-regime PBTE reproduction with volume, convergence, uncertainty, and material-state contracts; separately obtain a declared base-Phi SI anchor or independent paired calibration.
CLAIM_BOUNDARY: Internal/cross-file harmonic MP48 reproduction only. It is not Ding PBTE reproduction, UET transport validation, a temperature prediction, an `alpha_Phi_K` calibration, or Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "MP48 harmonic spectral C_src-like cross-file lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - MP48 harmonic spectral C_src-like cross-file lane", report)

    manifest = f"""## MP48 Harmonic Spectral C_src-like Cross-file Reproduction (2026-08-13)

The permitted MP48 archive now has a deterministic harmonic DOS cross-file reproduction
lane. The raw DOS, thermal-properties, and Phonopy metadata files remain source-locked;
the reproduction artifact is `{ARTIFACT.relative_to(ROOT).as_posix()}` with SHA-256
`{artifact_hash}`. The full Topic 13 gate consumes this as a source-package lane only;
the current full-gate hash is `{full_hash}`.

The calculation uses `C_src^DOS(T) = N_A integral[g(nu)c(nu,T)dnu]` and reports J K^-1
mol^-1 primitive-cell values at 200, 250, and 300 K. It is an internal cross-file
harmonic comparator, not Ding PBTE `C_src`, not an accepted Ding-regime reproduction,
and not a UET or alpha calibration. No Xie 2026 holdout, target curve, or fitted
coefficient was accessed.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## MP48 Harmonic Spectral C_src-like Cross-file Reproduction (2026-08-13)", manifest)

    formula = f"""## MP48 Harmonic Spectral C_src-like Reproduction (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-039` | `c_mu(T)=k_B*x_mu^2*exp(x_mu)/(exp(x_mu)-1)^2`, `C_src^DOS=N_A*integral[g(nu)c(nu,T)dnu]` | `docs/scripts/audit/audit_topic13_mp48_spectral_csrc_reproduction.py`; `docs/core/07_artifacts/topic13/t13_mp48_spectral_csrc_reproduction_audit.json` | `nu` = THz; `g(nu)` = modes THz^-1 per primitive cell; `c_mu` = J K^-1 per mode; result = J K^-1 mol^-1 primitive cell | source-locked CODATA constants plus MP48 deposited DOS and thermal-properties files | checked local harmonic cross-file reproduction; not Ding PBTE derivation | source-package comparator and quadrature diagnostic only | DOS grid, harmonic approximation, material volume, and source-regime mismatch can prevent equivalence to Ding `C_src`; no uncertainty is silently promoted | obtain Ding-compatible mode-resolved PBTE inputs or an accepted same-regime independent reproduction with convergence and uncertainty; keep base-Phi SI anchor and alpha open |

The lane is `CLOSED_FOR_LANE` only. Its maximum trapezoid residual against the deposited
MP48 thermal-properties rows is `0.009992863239339345`, and the maximum every-second-bin
quadrature difference is `0.014787789991730582`; these are reported envelopes, not
physical acceptance thresholds. The artifact hash is `{artifact_hash}`. The result does
not emit `alpha_Phi_K`, does not use Xie 2026, and does not promote `Phi` to temperature.
"""
    append_once(TOPIC / "FORMULA_AUDIT.md", "## MP48 Harmonic Spectral C_src-like Reproduction (2026-08-13)", formula)

    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_content = f"""# 2026-08-13 Work Ledger

## Topic 13 MP48 spectral hardening wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: MP48 spectral audit script/test/artifact; Topic 13 full gate integration; formula audit; data manifest; current report; update log; major-result register and dependency hash sync
- verifier: Topic 13 focused suite `156 passed`; full gate `BLOCKED_OPEN_T13_FULL_BRIDGE`; closure register `55` entries; downstream dependency unlock remains blocked
- public-safety: `partial`
- result: harmonic MP48 DOS/thermal-properties cross-file lane closed for lane; no Ding PBTE or UET alpha claim
- hashes: spectral artifact `{artifact_hash}`; full gate after integration `{full_hash}`
- remains: Ding-compatible mode-resolved `C_src`, material-regime/volume contract, PBTE uncertainty/convergence, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: pursue the next source-backed or derivation-backed closure wave without reading Xie 2026 or fitting a target curve
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 MP48 spectral hardening wave", ledger_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
