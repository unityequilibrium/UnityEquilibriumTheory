"""Repair generated Wave 1 registry paths after a real path-existence audit."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
ADDENDUM = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_wave1_research_rooms_addendum.json"


def main() -> int:
    replacements = {
        "uet.thermal.ttg_normalized_observable": [
            "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_observable_map_readiness.json",
            "docs/core/07_artifacts/topic13/thermal_dimensional_calibration_contract.json",
        ],
        "uet.phase.structure_factor_estimator_policy": [
            "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_structure_factor_source_archive_policy_gate.json",
            "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_structure_factor_full_text_formula_readiness_gate.json",
            "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_structure_factor_ch_finite_k_next_path_decision_gate.json",
        ],
    }
    addendum = json.loads(ADDENDUM.read_text(encoding="utf-8-sig"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8-sig"))
    for entry in addendum.get("entries", []):
        if entry.get("equation_id") in replacements:
            entry["verifier_paths"] = replacements[entry["equation_id"]]
    for entry in registry.get("entries", []):
        if entry.get("equation_id") in replacements:
            entry["verifier_paths"] = replacements[entry["equation_id"]]
    ADDENDUM.write_text(json.dumps(addendum, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("status=PASS_WAVE1_REGISTRY_PATHS_REPAIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
