from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json"
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
    report = f"""### 2026-08-13 - MP48 force-constant harmonic reconstruction lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION`.
WHAT_IS_ACTUALLY_CLOSED: The archived 200x200 MP48 force-constant matrix parses with every pair present once; its primitive-to-supercell mapping reconstructs a 12-mode dynamical matrix, satisfies acoustic/Hermitian roundoff checks, and reaches the deposited frequency envelope on a declared 5x5x2 q-grid.
WHAT_REMAINS_OPEN: This does not reproduce Ding PBTE `C_src`, third-order PBTE transport, the Ding material regime, the base-Phi energy anchor, or independent `alpha_Phi_K`.
DEPENDENCY_UNLOCKED: MP48 harmonic force-constant source lane only; no Ding source, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json` (SHA-256 `{artifact_hash}`) and linked it into the Topic 13 full gate (SHA-256 `{full_hash}`).
EQUATION_OR_MAPPING: `D_ij(q) = sum_R Phi_ij(R) exp(2*pi*i*q.R)/sqrt(m_i*m_j)` and `nu_mu = sign(lambda_mu)*sqrt(abs(lambda_mu))*conversion_factor`; mapping is from supercell Cartesian coordinates to primitive atom plus integer translation.
VERIFICATION: Force-constant shape `200x200x3x3`, pair symmetry residual `1.1e-14`, acoustic-sum residual `9.5e-14`, Gamma acoustic maximum `8.17e-7 THz`, no q-grid negative eigenvalue beyond roundoff, and q-grid maximum `48.41862978666018 THz` versus deposited summary `48.4370817598 THz` (relative gap `-0.0003809472509372913`). No fit, target access, holdout access, or alpha emission.
CONTROLLING_BLOCKER: `Ding_material_regime_and_mode_resolved_C_src_acceptance_missing` for this lane; the full gate remains controlled by the existing Ding source, dimensional alpha, bridge/beta, EOS/transport/KMS/entropy, and SI-map blockers.
NEXT_ACTION: Obtain Ding-compatible mode-resolved `C_src(T)` or an accepted same-regime PBTE reproduction with volume, convergence, uncertainty, and material-state contracts; separately obtain a declared base-Phi SI anchor or independent paired calibration.
CLAIM_BOUNDARY: Internal/source-traceable MP48 harmonic reconstruction only. It is not Ding PBTE reproduction, UET transport validation, a temperature prediction, an `alpha_Phi_K` calibration, or Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "MP48 force-constant harmonic reconstruction lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - MP48 force-constant harmonic reconstruction lane", report)

    manifest = f"""## MP48 Force-constant Harmonic Reconstruction (2026-08-13)

The permitted MP48 archive now has a deterministic source-level harmonic
reconstruction lane. The raw force constants, Phonopy metadata, and summary
remain source-locked; the result artifact is
`{ARTIFACT.relative_to(ROOT).as_posix()}` with SHA-256 `{artifact_hash}`.
The Topic 13 full gate consumes this as a source-package lane only; its current
hash is `{full_hash}`.

The calculation reconstructs `D_ij(q)` from the 200-atom supercell force
constants, checks the primitive mapping, acoustic sum rule, pair symmetry,
Gamma acoustic modes, and a declared 5x5x2 q-grid. It is an internal harmonic
source comparator, not Ding PBTE `C_src`, not UET transport, and not an alpha
calibration. No Xie 2026 holdout, target curve, or fitted coefficient was used.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## MP48 Force-constant Harmonic Reconstruction (2026-08-13)", manifest)

    formula = f"""## MP48 Force-constant Harmonic Reconstruction (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-041` | `D_ij(q)=sum_R Phi_ij(R) exp(2*pi*i*q.R)/sqrt(m_i*m_j)`, `nu_mu=sign(lambda_mu)*sqrt(abs(lambda_mu))*conversion_factor` | `docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py`; `docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json` | force constants = eV Angstrom^-2; masses = amu; q = dimensionless reciprocal fractional; frequency = THz | source-locked MP48 force constants and Phonopy metadata | checked harmonic reconstruction; not Ding PBTE or UET derivation | source-integrity, acoustic, Hermitian, and limited q-grid comparator | finite supercell, harmonic approximation, q-grid choice, and material-regime mismatch can prevent Ding `C_src` equivalence; no uncertainty is silently promoted | obtain Ding-compatible mode-resolved PBTE inputs or an accepted same-regime reproduction with convergence and uncertainty; keep base-Phi SI anchor and alpha open |

The lane is `CLOSED_FOR_LANE` only. The artifact hash is `{artifact_hash}` and the
full-gate hash after integration is `{full_hash}`. The q-grid comparison is a
declared metadata envelope rather than an external-validation threshold. The
result does not emit `alpha_Phi_K`, does not use Xie 2026, and does not promote
`Phi` to temperature.
"""
    append_once(TOPIC / "FORMULA_AUDIT.md", "## MP48 Force-constant Harmonic Reconstruction (2026-08-13)", formula)

    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_content = f"""## Topic 13 MP48 force-constant harmonic reconstruction wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: force-constant reconstruction audit script/test/artifact; Topic 13 full-gate integration; formula audit; data manifest; current report; update log; closure register/dependency hash sync
- verifier: focused MP48 reconstruction/spectral/Phi_E tests `5 passed`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: MP48 force-constant harmonic source lane closed for lane; no Ding PBTE, UET transport, or alpha claim
- hashes: reconstruction artifact `{artifact_hash}`; full gate after integration `{full_hash}`
- remains: Ding-compatible mode-resolved `C_src`, material-regime contract, PBTE uncertainty/convergence, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, physical Kubo, finite-T transport, SK/KMS, entropy, and dissipative balance
- next action: pursue the next source-backed or derivation-backed closure wave without reading Xie 2026 or fitting a target curve
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 MP48 force-constant harmonic reconstruction wave", ledger_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
