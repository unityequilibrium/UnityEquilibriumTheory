"""Add the explicit Wave 1 TTG lane to the generated active-lane register."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "docs/core/07_artifacts/archive/uet_active_lane_units_observable_register.json"


def main() -> int:
    register = json.loads(PATH.read_text(encoding="utf-8-sig"))
    lanes = list(register.get("lanes", []))
    lane = {
        "lane_id": "thermal_ttg_observable_bridge",
        "variables": {
            "Phi": "normalized effective response variable",
            "Delta_Phi": "normalized response difference",
            "Delta_Tq": "source-defined quasi-temperature difference in K only after independent mapping",
            "alpha_Phi_K": "open scale in K per normalized Phi",
            "y_TTG": "dimensionless normalized TTG signal",
            "R_gen": "derived trace/history variable; not a direct TTG observable",
        },
        "unit_lane": "normalized_plus_external_K_contract_open",
        "standard_counterpart": "TTG quasi-temperature response with Fourier and Cattaneo controls",
        "observable_operator": "y_TTG^UET(t)=Delta_Phi(t)/Delta_Phi(0); Delta_Tq=alpha_Phi_K*Delta_Phi",
        "observable_status": "SIMULATION_ONLY_OPEN_DIMENSIONAL_MAP",
        "units_status": "BLOCKED_INDEPENDENT_ALPHA_Phi_K",
        "uncertainty_status": "PROVISIONAL_FIGURE_DIGITIZATION_PLUS_OPEN_ALPHA_UNCERTAINTY",
        "open_items": [
            "full coupled pre-arrival leakage remains above 1e-6",
            "independent alpha_Phi_K derivation or calibration with uncertainty",
            "heat-flux and entropy maps are downstream and not direct TTG observables",
            "Xie 2026 remains locked holdout",
        ],
        "evidence": [
            "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json",
            "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_observable_map_readiness.json",
            "docs/core/07_artifacts/topic13/thermal_dimensional_calibration_contract.json",
        ],
        "claim_boundary": "normalized observable/control lane only; no temperature prediction or external validation",
        "wave1_status": "BLOCKED_OPEN_CALIBRATION",
        "generated_by": "sync_uet_active_lane_wave1.py",
    }
    lanes = [item for item in lanes if item.get("lane_id") != lane["lane_id"]]
    lanes.append(lane)
    register["lanes"] = lanes
    register["lane_count"] = len(lanes)
    register["generated_at"] = date.today().isoformat()
    register["wave1_extension"] = {
        "status": "CANDIDATE_LANE_ADDED_WITH_BLOCKED_DIMENSIONAL_MAP",
        "claim_promotion": False,
        "selected_reference_branch": "frozen_C_normalized_control_only",
        "full_candidate_gate": "preserved_separately",
    }
    PATH.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": register["wave1_extension"]["status"], "lane_count": len(lanes)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
