"""Keep the closure contract and full gate aligned with scoped no-go results."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_contract.json"
FULL_GATE = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    levels = contract.setdefault("closure_levels", [])
    if "CLOSED_AS_NO_GO" not in levels:
        insert_at = levels.index("CLOSED_FOR_LANE") if "CLOSED_FOR_LANE" in levels else len(levels)
        levels.insert(insert_at, "CLOSED_AS_NO_GO")
        CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    text = FULL_GATE.read_text(encoding="utf-8-sig")
    old = '''            for item in previous_major.get("what_remains_open", [])
            if item not in {
                "formal_conserved_C_no_go_or_explicit_regularization_missing",
                "named finite-cone branch or explicit conserved-C regularization",
                "named_finite_cone_branch_or_explicit_regularization_missing",
            }
'''
    new = '''            for item in previous_major.get("what_remains_open", [])
            if item not in {
                "formal_conserved_C_no_go_or_explicit_regularization_missing",
                "named finite-cone branch or explicit conserved-C regularization",
                "named_finite_cone_branch_or_explicit_regularization_missing",
                "original_conserved_c_gradient_baseline_blocked",
            }
'''
    if new not in text:
        if old not in text:
            raise SystemExit("full-gate historical blocker merge anchor not found")
        text = text.replace(old, new, 1)
        FULL_GATE.write_text(text, encoding="utf-8")
    print("PASS_REPAIRED_TOPIC13_NO_GO_CLOSURE_SCHEMA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
