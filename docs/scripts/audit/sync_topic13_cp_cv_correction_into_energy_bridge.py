"""Attach the cp-cv formula contract to the named Topic 13 energy branch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ENERGY = ROOT / "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json"
CORRECTION = ROOT / "docs/core/07_artifacts/topic13/t13_cp_cv_correction_audit.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(values: list[str], item: str) -> None:
    if item not in values:
        values.append(item)


def main() -> int:
    energy = json.loads(ENERGY.read_text(encoding="utf-8-sig"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8-sig"))
    correction_path = rel(CORRECTION)
    correction_digest = sha256(CORRECTION)
    branch = energy.setdefault("major_result", {})
    what_is_closed = branch.get("what_is_closed", [])
    if isinstance(what_is_closed, str):
        what_is_closed = [what_is_closed]
    append_once(
        what_is_closed,
        "standard c_p-to-c_v correction formula, unit contract, and first-order uncertainty propagation",
    )
    branch["what_is_closed"] = what_is_closed
    open_blockers = branch.setdefault("open_blockers", [])
    for blocker in correction["major_result"]["open_blockers"]:
        append_once(open_blockers, blocker)
    evidence = branch.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != correction_path]
    evidence.append(
        {
            "path": correction_path,
            "sha256": correction_digest,
            "summary": {"status": correction["status"], "numeric_inputs_consumed": False},
        }
    )
    energy["cp_cv_correction_contract"] = {
        "status": correction["status"],
        "major_result_id": correction["major_result"]["major_result_id"],
        "audit": {"path": correction_path, "sha256": correction_digest},
        "c_v_status": "OPEN_SOURCE_INPUTS",
        "numeric_material_inputs_consumed": False,
        "open_blockers": correction["major_result"]["open_blockers"],
    }
    energy["next_controller"] = (
        "source-lock volumetric alpha_V, isothermal K_T, density uncertainty, and material regime; "
        "then independently derive or calibrate e0 and prove base Phi-to-Phi_E without TTG target residuals or Xie 2026"
    )
    ENERGY.write_text(json.dumps(energy, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "energy_audit": rel(ENERGY),
                "correction_status": correction["status"],
                "correction_sha256": correction_digest,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
