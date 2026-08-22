"""Run the Topic 13 full-bridge hardening packet in dependency order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
COMMANDS = [
    "docs/scripts/audit/repair_topic13_runner_alias_idempotence_order_v2.py",
    "docs/scripts/audit/repair_topic13_full_gate_remaining_compatibility_idempotence.py",
    "docs/scripts/audit/repair_topic13_full_gate_alias_repair_idempotence.py",
    "docs/scripts/audit/repair_topic13_full_gate_backward_compat_aliases.py",
    "docs/scripts/audit/repair_topic13_full_gate_remaining_compatibility.py",
    # The full gate composes causal evidence, so create the no-go record first.
    "docs/scripts/audit/repair_topic13_full_gate_final_compatibility_fields.py",
    "docs/scripts/audit/repair_topic13_full_gate_preserve_subresult_blockers.py",
    "docs/scripts/audit/repair_topic13_full_gate_merge_subresult_blockers.py",
    "docs/scripts/audit/repair_topic13_full_gate_compatibility_projection.py",
    "docs/scripts/audit/audit_conserved_c_finite_cone_no_go.py",
    "docs/scripts/audit/audit_topic13_farooqui_ig210_volumetric_cp_uncertainty.py",
    "docs/scripts/audit/audit_topic13_full_bridge_gate.py",
    "docs/scripts/audit/sync_topic13_no_go_gate.py",
    "docs/scripts/audit/audit_major_result_closure.py",
    "docs/scripts/audit/sync_major_result_wave1_contract.py",
]


def main() -> int:
    for relative in COMMANDS:
        command = [sys.executable, str(ROOT / relative)]
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
