"""Append the completed c_v source-reconciliation wave to Topic 13's log."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
RECONCILIATION = ROOT / "docs/core/artifacts/t13_cv_source_reconciliation_audit.json"
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
MARKER = "### 2026-08-25 - Topic 13 c_v reconciliation route completeness wave"


ENTRY = f"""\n{MARKER}

- Scope: `Topic 13 source/c_v acceptance boundary`
- Wave type: `source-route completeness`
- Added or changed: included the existing IAEA GR-280 same-state Cp comparator in the canonical c_v reconciliation; projected it through the input-package audit and regenerated closure artifacts.
- Files touched: `docs/core/artifacts/t13_cv_source_reconciliation_audit.json`, `docs/core/artifacts/t13_closure_input_package_audit.json`, `docs/core/artifacts/t13_topic13_closure_matrix.json`, `docs/core/artifacts/t13_full_closure_progress.json`, `docs/topics/0.13_Thermodynamic_Bridge/TOPIC13_FULL_CLOSURE_STATUS.md`
- Verified with: `audit_topic13_cv_source_reconciliation.py`, `run_topic13_cv_source_reconciliation_wave.py`, `audit_topic13_full_bridge_gate.py`, `audit_topic13_closure_matrix.py`, `render_topic13_closure_progress.py`
- Result: `PASS_SCOPED_CV_SOURCE_RECONCILIATION_OPEN`; `candidate_count=8`, `direct_or_derived_cv_count=2`, `source_grade_cv_uncertainty_count=0`, `eligible_for_full_topic13_count=0`.
- Blocker narrowed: the route inventory is now complete for this reconciliation; IAEA GR-280 adds same-state Cp and density availability only and does not supply accepted Cv uncertainty or Ding material equivalence.
- Still open: `c_v_source_uncertainty_not_closed`, Ding-compatible numeric `C_src`, independent base-Phi/SI/alpha/beta, and physical Kubo/SK/KMS/entropy matching.
- Next controller: obtain a same-state direct volumetric c_v or Ding-compatible mode-resolved `C_src(T)` package with source-grade uncertainty and explicit material mapping; do not combine unmatched sources.
- Claim impact: `no change`; no alpha, source row, threshold, equation, or holdout role was promoted.
- Workflow linkage: `n/a`
- Notes: The canonical gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; `36` subresults remain reported as `CLOSED_FOR_LANE=21`, `CLOSED_AS_NO_GO=5`, `OPEN=10`.
"""


def main() -> int:
    log_text = LOG.read_text(encoding="utf-8")
    if MARKER not in log_text:
        LOG.write_text(log_text.rstrip() + "\n" + ENTRY, encoding="utf-8")
        action = "appended"
    else:
        action = "already_present"
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8-sig"))
    input_audit = json.loads(INPUT_AUDIT.read_text(encoding="utf-8-sig"))
    print(json.dumps({
        "status": "PASS_TOPIC13_CV_SOURCE_RECONCILIATION_LOGGED",
        "action": action,
        "reconciliation_status": reconciliation.get("status"),
        "input_audit_status": input_audit.get("status"),
        "log": str(LOG.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
