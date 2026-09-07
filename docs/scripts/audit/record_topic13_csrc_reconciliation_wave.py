"""Append the completed C_src reconciliation wave to Topic 13's log."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
RECONCILIATION = ROOT / "docs/core/artifacts/t13_csrc_reconciliation_audit.json"
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
MARKER = "### 2026-08-25 - Topic 13 C_src public boundary completeness wave"

ENTRY = f"""
{MARKER}

- Scope: `Topic 13 Ding C_src/material/uncertainty source boundary`
- Wave type: `source-route reconciliation`
- Added or changed: included the source-locked Ding 2017 supplementary and Figshare DFT force-data boundaries in `t13_csrc_reconciliation_audit.json`; projected the route inventory into `t13_closure_input_package_audit.json` after replaying c_v, transport, and base-Phi projections.
- Files touched: `docs/core/artifacts/t13_csrc_reconciliation_audit.json`, `docs/core/artifacts/t13_closure_input_package_audit.json`, `docs/core/artifacts/t13_topic13_closure_matrix.json`, `docs/core/artifacts/t13_full_closure_progress.json`, `docs/topics/0.13_Thermodynamic_Bridge/TOPIC13_FULL_CLOSURE_STATUS.md`
- Verified with: `audit_topic13_csrc_reconciliation.py`, `run_topic13_csrc_reconciliation_wave_composed.py`, `audit_topic13_full_bridge_gate.py`, `audit_topic13_closure_matrix.py`, `render_topic13_closure_progress.py`
- Result: `PASS_SCOPED_CSRC_RECONCILIATION_OPEN`; `route_count=10`, `numeric_csrc_candidate_count=3`, `source_grade_uncertainty_count=0`, `ding_material_state_match_count=0`, `accepted_independent_reproduction_count=0`.
- Blocker narrowed: the public Ding 2017 supplementary and Figshare DFT force archive are now explicitly classified as no-payload boundaries; the only remaining C_src closure routes are an authorized Ding payload or an accepted same-regime reproduction.
- Still open: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`, material mapping, c_v uncertainty, and author response.
- Next controller: send the prepared Ding author request only with project authorization, or complete an independent same-regime reproduction with source-grade uncertainty and material mapping; do not promote Calorine/MP48 values.
- Claim impact: `no_change`; no C_src, alpha, threshold, equation, or holdout role was promoted.
- Workflow linkage: `n/a`
- Notes: The canonical gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; this reconciliation is `CLOSED_FOR_LANE` only.
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
        "status": "PASS_TOPIC13_CSRC_RECONCILIATION_LOGGED",
        "action": action,
        "reconciliation_status": reconciliation.get("status"),
        "input_audit_status": input_audit.get("status"),
        "log": str(LOG.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
