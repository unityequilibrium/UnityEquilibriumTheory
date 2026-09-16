"""Write one factual Wave 1 entry to the owning room logs."""

from __future__ import annotations

from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MARKER = "## Wave 1 Research Room Checkpoint"
ENTRY = f"""{MARKER} ({date.today().isoformat()})

STATUS: Wave 1 coordination checkpoint recorded; claim promotion remains disabled.

WHAT_CHANGED: Core room contract now links Topic 0.13, Topic 0.11, Core O(2), and Topic 0.10 comparator evidence with explicit blockers and next actions.

EQUATION_OR_MAPPING: The declared TTG mapping remains `y_TTG = Delta_Tq(t)/Delta_Tq(0)`, `y_TTG^UET = Delta_Phi(t)/Delta_Phi(0)`, and `Delta_Tq = alpha_Phi_K * Delta_Phi`; `alpha_Phi_K` remains open.

VERIFICATION: Wave 1 contract and integration gate were regenerated from local artifacts. The selected frozen-C causal reference is kept separate from the full coupled leakage gate.

CONTROLLING_BLOCKER: Full coupled pre-arrival leakage, independent thermal calibration, and Topic 0.11 source/estimator acceptance remain open.

NEXT_ACTION: Resolve the owning room blocker and rerun its machine-readable gate before expanding scope.

CLAIM_BOUNDARY: Internal/provisional evidence only; no proof, prediction, external validation, or theory closure.

"""


def prepend(path: Path) -> None:
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    if MARKER not in existing:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ENTRY + existing, encoding="utf-8")


def main() -> int:
    prepend(ROOT / "docs/topics/0.11_Phase_Transitions/UPDATE_LOG.md")
    prepend(ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos/UPDATE_LOG.md")
    prepend(ROOT / "docs/core/08_history/update_logs/UET_RESEARCH_ROOM_WAVE1_UPDATE_LOG.md")
    print("status=PASS_UPDATE_LOGS_SYNCED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
