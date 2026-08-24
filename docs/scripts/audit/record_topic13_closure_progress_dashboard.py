"""Record the generated Topic 13 closure-progress handoff once."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROGRESS_REL = "docs/core/artifacts/t13_full_closure_progress.json"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MARKER = "### 2026-08-24 - Topic 13 closure progress dashboard"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    progress = json.loads((ROOT / PROGRESS_REL).read_text(encoding="utf-8"))
    counts = progress["closure_counts"]
    status = progress["canonical_status"]
    open_ids = [item["subresult_id"] for item in progress["open_subresults"]]
    if MARKER in UPDATE_LOG.read_text(encoding="utf-8"):
        print(json.dumps({"status": "PASS_T13_CLOSURE_PROGRESS_ALREADY_LOGGED"}))
        return 0

    entry = f"""{MARKER}

MAJOR_RESULT_CLOSURE:
- Full Topic 13 remains `{status['full_topic_closure_level']}`; this wave adds a generated progress handoff only.

WHAT_IS_ACTUALLY_CLOSED:
- The canonical matrix is rendered as `CLOSED_FOR_LANE={counts.get('CLOSED_FOR_LANE', 0)}`, `CLOSED_AS_NO_GO={counts.get('CLOSED_AS_NO_GO', 0)}`, `CLOSED_FOR_CORE={counts.get('CLOSED_FOR_CORE', 0)}`, and `OPEN={counts.get('OPEN', 0)}` across `{progress['required_subresult_count']}` required subresults.
- The bounded named causal branch remains the only causal `CLOSED_FOR_CORE` input; no Full Topic 13 input package is accepted.

WHAT_REMAINS_OPEN:
- `{', '.join(open_ids)}`.

DEPENDENCY_UNLOCKED:
- None beyond the bounded causal branch. `full_core_unlock=false` and downstream Core/Gravity/transport remain locked.

STATUS:
- `{status['full_topic_status']}`; `claim_promotion=false`.

WHAT_CHANGED:
- Added `docs/core/artifacts/t13_full_closure_progress.json` and `docs/topics/0.13_Thermodynamic_Bridge/TOPIC13_FULL_CLOSURE_STATUS.md`, generated from the canonical matrix, full gate, and input audit.

EQUATION_OR_MAPPING:
- Existing operators remain `y_TTG=Delta_Tq(t)/Delta_Tq(0)`, `y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)`, and `Delta_Tq=alpha_Phi_K*Delta_Phi`; no numeric alpha or SI map was emitted.

VERIFICATION:
- The renderer completed with `{progress['required_subresult_count']}` required subresults and `{len(open_ids)}` open subresults.
- Holdout policy remains `{progress['holdout_policy']}`; no target fit or threshold change was introduced.

CONTROLLING_BLOCKER:
- `{status['controlling_blocker']}`; the three grouped external input packages remain blocked.

NEXT_ACTION:
- Do not rerun the same gates without an input change. Obtain an authorized Ding-compatible payload, an independent base-Phi/SI anchor with alpha record, and a physical Kubo/SK/KMS/entropy record; rerun acceptance and full integration only after a source hash changes.

CLAIM_BOUNDARY:
- Progress reporting only. This wave does not close Full Topic 13, consume Xie 2026, or unlock downstream claims.

EVIDENCE_PATHS:
- `{PROGRESS_REL}`
- `docs/topics/0.13_Thermodynamic_Bridge/TOPIC13_FULL_CLOSURE_STATUS.md`

EVIDENCE_HASH:
- `{digest(PROGRESS_REL)}`
"""
    current = UPDATE_LOG.read_text(encoding="utf-8")
    UPDATE_LOG.write_text(current.rstrip() + "\n\n" + entry.rstrip() + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "PASS_T13_CLOSURE_PROGRESS_RECORDED",
                "open_subresults": len(open_ids),
                "progress_sha256": digest(PROGRESS_REL),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
