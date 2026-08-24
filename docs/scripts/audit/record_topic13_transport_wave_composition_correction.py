"""Record the composed replay command that preserves prior Topic 13 waves."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MARKER = "### 2026-08-24 - Topic 13 transport wave composition correction"

ENTRY = f"""
{MARKER}

- Scope: `Topic 13 sequential input-package projections`
- Wave type: `workflow correction`
- Added or changed: `run_topic13_physical_transport_reconciliation_wave_composed.py` replays the c_v projection before the physical transport projection.
- Verified with: the composed runner plus the c_v and physical transport integration tests.
- Result: prior c_v evidence and the new physical transport evidence remain visible in one input audit; no scientific claim or gate threshold changed.
- Blocker: `physical_Kubo_coefficient_record_missing` remains the transport controller; c_v remains `c_v_source_uncertainty_not_closed`.
- Next action: use the composed runner when replaying these sequential waves; do not call the base input audit alone after a projection wave.
- Claim impact: `no_change`.
"""


def main() -> int:
    log_text = LOG.read_text(encoding="utf-8")
    if MARKER not in log_text:
        LOG.write_text(log_text.rstrip() + "\n" + ENTRY, encoding="utf-8")
        action = "appended"
    else:
        action = "already_present"
    print(json.dumps({
        "status": "PASS_TOPIC13_WAVE_COMPOSITION_RECORDED",
        "action": action,
        "log": str(LOG.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
