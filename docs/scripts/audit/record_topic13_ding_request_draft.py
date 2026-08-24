"""Record preparation of the bounded Ding author-request draft."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DRAFT_REL = "docs/topics/0.13_Thermodynamic_Bridge/DING_PBTE_AUTHOR_REQUEST_DRAFT.md"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MARKER = "### 2026-08-24 - Ding PBTE author-request draft prepared"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    text = UPDATE_LOG.read_text(encoding="utf-8")
    if MARKER in text:
        print({"status": "PASS_T13_DING_REQUEST_DRAFT_ALREADY_LOGGED"})
        return 0

    draft_hash = digest(DRAFT_REL)
    entry = f"""{MARKER}

MAJOR_RESULT_CLOSURE:
- `T13_DING_PBTE_AUTHOR_REQUEST_PACKAGE` remains `CLOSED_FOR_LANE`; no source payload has been received.

WHAT_IS_ACTUALLY_CLOSED:
- A human-reviewable, bounded request draft now mirrors the existing machine-readable request manifest.
- The draft asks for material state, force-constant/PBTE inputs, mode-resolved `c_mu(T)`, aggregate `C_src(T)`, uncertainty/convergence, response outputs, hashes, and permission terms.

WHAT_REMAINS_OPEN:
- `accepted_numeric_csrc`, `material_and_uncertainty_closure`, and every downstream physical SI bridge result remain open.

DEPENDENCY_UNLOCKED:
- None. The draft is not evidence and has not been sent.

STATUS:
- `REQUEST_PACKAGE_READY_NOT_SENT`.

WHAT_CHANGED:
- Added `{DRAFT_REL}` for project-authorized external communication. No email was sent and no source data were imported.

EQUATION_OR_MAPPING:
- The request preserves `C_src(T)=sum_mu c_mu(T)` and keeps `Delta_Tq=alpha_Phi_K*Delta_Phi` uncalibrated.

VERIFICATION:
- Draft fields match the existing request manifest and acceptance contract; Xie 2026, target fitting, and alpha fitting remain excluded.

CONTROLLING_BLOCKER:
- `author_data_or_independent_reproduction_payload_not_received`.

NEXT_ACTION:
- Obtain project authorization, send the draft through an approved channel, and audit any response before changing the manifest response state.

CLAIM_BOUNDARY:
- Request preparation only; not source receipt, numeric C_src, alpha calibration, external validation, or Full Topic 13 closure.

EVIDENCE_PATHS:
- `{DRAFT_REL}`
- `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_pbte_author_request_manifest.json`

EVIDENCE_HASH:
- `{draft_hash}`
"""
    UPDATE_LOG.write_text(text.rstrip() + "\n\n" + entry.rstrip() + "\n", encoding="utf-8")
    print({"status": "PASS_T13_DING_REQUEST_DRAFT_RECORDED", "draft_sha256": draft_hash})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
