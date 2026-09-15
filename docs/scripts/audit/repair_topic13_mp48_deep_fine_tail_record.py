"""Resolve literal placeholders in the deep fine-tail wave records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    policy = artifact["mesh_policy"]
    values = {
        '{policy["fine_tail_max_abs_relative_step"]}': str(policy["fine_tail_max_abs_relative_step"]),
        '{policy["finest_pair_meshes"][0]}': str(policy["finest_pair_meshes"][0]),
        '{policy["finest_pair_meshes"][1]}': str(policy["finest_pair_meshes"][1]),
        '{policy["finest_pair_max_abs_relative_step"]}': str(policy["finest_pair_max_abs_relative_step"]),
        '{artifact["max_abs_relative_mesh_step"]}': str(artifact["max_abs_relative_mesh_step"]),
        '{artifact["status"]}': str(artifact["status"]),
        '{artifact_hash}': sha256(ARTIFACT),
        '{full_hash}': sha256(FULL_GATE),
        '{register_hash}': sha256(REGISTER),
        '{dependency_hash}': sha256(DEPENDENCY),
    }
    targets = (
        ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md",
        ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md",
        ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md",
        ROOT / "WORK_LEDGER/2026/2026-08-13.md",
    )
    marker = "MP48 deep fine-tail"
    for target in targets:
        text = target.read_text(encoding="utf-8")
        index = text.rfind(marker)
        if index < 0:
            raise SystemExit(f"record marker not found in {target}")
        prefix, suffix = text[:index], text[index:]
        for old, new in values.items():
            suffix = suffix.replace(old, new)
        target.write_text(prefix + suffix, encoding="utf-8")


if __name__ == "__main__":
    main()
