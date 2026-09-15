"""Record the Topic 13 holdout-access correction in current research docs."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if marker in text:
        return
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + block.rstrip() + "\n", encoding="utf-8")


CURRENT_BLOCK = """
### 2026-08-13 - Xie 2026 holdout access-semantics correction

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_XIE_2026_HOLDOUT_ACCESS_CONTROL`.
WHAT_IS_ACTUALLY_CLOSED: The current audit now distinguishes metadata-only observation from source-data consumption. No numeric holdout payload, source rows, curves, or source bytes were consumed by Topic 13 research paths, and no holdout-derived fit, tuning, calibration, threshold adjustment, or claim promotion occurred.
WHAT_REMAINS_OPEN: Xie 2026 remains a locked holdout and must not be used for calibration, tuning, fitting, or threshold adjustment.
DEPENDENCY_UNLOCKED: Holdout-integrity reporting may proceed from the canonical access audit; no thermal-bridge, alpha, prediction, or external-validation dependency is unlocked.
STATUS: `PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json` (SHA-256 `c3185da0a233894d7f338138bbe6acee287194e1852a80e40b0b5f6f2134e21b`), wired it into the active full-gate and Ding source-mapping verifiers, and synchronized the major-result register/dependency gate.
EQUATION_OR_MAPPING: Access contract is `metadata_only_observed != numeric_payload_consumed`; the locked rule is `numeric_payload_consumed = used_for_fit = used_for_tuning = used_for_calibration = used_for_threshold_adjustment = false`.
VERIFICATION: Canonical holdout audit and full-gate evidence hash agree; full-gate holdout integrity is `PASS` with metadata-only observation recorded and all numeric-consumption controls false. Focused holdout/acceptance/KMS tests pass (`7 passed`).
CONTROLLING_BLOCKER: No blocker remains in the access-control lane. Full Topic 13 remains controlled by Ding-regime `C_src`, independent `alpha_Phi_K`, dimensional/base-Phi anchor, bridge/beta, EOS/transport/KMS/entropy, and source uncertainty blockers.
NEXT_ACTION: Keep Xie 2026 locked and continue only with an authorized Ding numeric package or an accepted independent same-regime PBTE reproduction, plus an independent base-Phi SI anchor/calibration.
CLAIM_BOUNDARY: This closes an access-control audit only. It is not evidence for `C_src`, `alpha_Phi_K`, temperature prediction, external validation, or global UET closure.
"""

MANIFEST_BLOCK = """
## Xie 2026 Holdout Access Control (2026-08-13)

Canonical audit: `docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json` (`c3185da0a233894d7f338138bbe6acee287194e1852a80e40b0b5f6f2134e21b`).

The current record is explicit that metadata/article identity was observed during
source discovery, while no numeric holdout payload, rows, curves, or source bytes
were consumed. The holdout was not used for fitting, tuning, calibration, threshold
adjustment, candidate selection, or claim promotion. The canonical access audit
replaces ambiguous interpretation of legacy boolean compatibility fields; Xie 2026
remains locked.
"""

LOG_BLOCK = """
### 2026-08-13 - Topic 13 holdout access-semantics correction

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_XIE_2026_HOLDOUT_ACCESS_CONTROL`.
WHAT_IS_ACTUALLY_CLOSED: The holdout controller now records metadata-only observation separately from numeric source-data consumption. No numeric payload, source rows, curves, or source bytes were consumed by Topic 13 research paths, and no fit, tuning, calibration, threshold adjustment, or claim promotion used the holdout.
WHAT_REMAINS_OPEN: Xie 2026 remains locked; the independent `alpha_Phi_K` calibration remains open. :codex-annotation{index="1"}
DEPENDENCY_UNLOCKED: Canonical holdout-integrity auditing only; no thermal bridge, source `C_src`, alpha, Core, Gravity, or Galaxy dependency unlock.
STATUS: `PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with the same ten scientific blockers.
WHAT_CHANGED: Added the canonical access audit (`c3185da0a233894d7f338138bbe6acee287194e1852a80e40b0b5f6f2134e21b`), wired the full-gate and Ding source-mapping verifiers, and synchronized the major-result register/dependency gate.
EQUATION_OR_MAPPING: `metadata_only_observed` is distinct from `numeric_payload_consumed`; the locked rule sets numeric consumption, fit, tuning, calibration, and threshold adjustment to false.
VERIFICATION: Full-gate holdout integrity is `PASS`; canonical audit evidence is hash-linked; focused holdout/acceptance/KMS tests pass (`7 passed`).
CONTROLLING_BLOCKER: Access control is closed for lane. The next scientific controller remains Ding-compatible mode-resolved `C_src` or accepted independent reproduction, followed by the independent base-Phi SI anchor/`alpha_Phi_K` route.
NEXT_ACTION: Preserve the holdout lock and pursue only source-authorized Ding/PBTE evidence and independent Phi/SI calibration; do not reinterpret metadata-only observation as source-data access.
CLAIM_BOUNDARY: Access-control result only; no `C_src`, `alpha_Phi_K`, temperature prediction, external validation, or Full Topic 13 closure is claimed.
"""

LEDGER_BLOCK = """
## Topic 13 holdout access-semantics correction wave

- area: `research-core` (secondary: `research-standards`, `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: canonical Xie 2026 holdout access audit; holdout audit test; full-gate and Ding source-mapping verifier wiring; current report; data manifest; update log; major-result register/dependency sync
- verifier: `PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY`; full gate `BLOCKED_OPEN_T13_FULL_BRIDGE`; focused holdout/acceptance/KMS tests `7 passed`
- public-safety: `partial`
- result: metadata-only observation is recorded transparently while numeric holdout data remains unconsumed and locked; no scientific claim was promoted
- hashes: holdout `c3185da0a233894d7f338138bbe6acee287194e1852a80e40b0b5f6f2134e21b`; full `093745ba4aabaad9b315a470ee0285fee86bae0c897dd3ac7e94764e01b6b147`; register `f83d4cda8a87f78ef073bf680b7ee9ba2eb7430e60e10b32ec0cb9f32fcd5a11`; dependency `88319f7a1c37eb631ae7db1f4c53a8c42a39890451c736be58c07c691a9e150e`
- remains: Ding-compatible numeric `C_src` or accepted independent reproduction, independent `alpha_Phi_K`, base-Phi SI anchor, bridge/beta, physical transport/KMS/entropy closure, and source-grade uncertainty
- next action: keep Xie 2026 locked and continue source/calibration hardening without holdout fit, tuning, calibration, or threshold adjustment
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""


def main() -> int:
    append_once(
        ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md",
        "### 2026-08-13 - Xie 2026 holdout access-semantics correction",
        CURRENT_BLOCK,
    )
    append_once(
        ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md",
        "## Xie 2026 Holdout Access Control (2026-08-13)",
        MANIFEST_BLOCK,
    )
    append_once(
        ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md",
        "### 2026-08-13 - Topic 13 holdout access-semantics correction",
        LOG_BLOCK,
    )
    append_once(ROOT / "WORK_LEDGER/2026/2026-08-13.md", "## Topic 13 holdout access-semantics correction wave", LEDGER_BLOCK)
    print("recorded Topic 13 holdout access-semantics correction wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
