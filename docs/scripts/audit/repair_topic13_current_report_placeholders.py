from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/"
    "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
)
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"
FULL_GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    text = REPORT.read_text(encoding="utf-8")
    replacements = {
        '{policy["fine_tail_max_abs_relative_step"]}': "0.00653145749584183",
        '{policy["finest_pair_max_abs_relative_step"]}': "0.0007133166616816178",
        '{artifact["max_abs_relative_mesh_step"]}': "0.5134819354919335",
        "{artifact_hash}": digest(ARTIFACT),
        "{full_hash}": digest(FULL_GATE),
        "{register_hash}": digest(REGISTER),
        "{dependency_hash}": digest(DEPENDENCY),
    }
    updated = text
    for old, new in replacements.items():
        updated = updated.replace(old, new)
    if updated == text:
        print("no placeholders changed")
        return 0
    REPORT.write_text(updated, encoding="utf-8")
    remaining = [token for token in replacements if token in updated]
    if remaining:
        raise SystemExit(f"unresolved placeholders: {remaining}")
    print("repaired current Topic 13 report placeholders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
