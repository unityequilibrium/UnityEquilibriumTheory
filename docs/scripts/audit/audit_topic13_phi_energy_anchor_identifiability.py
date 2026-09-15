"""Audit the structural identifiability boundary for the Phi energy anchor."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
UNITS_REL = "docs/core/07_artifacts/archive/uet_active_lane_units_observable_register.json"
BRIDGE_REL = "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_phi_energy_anchor_identifiability_no_go.json"


def load(rel: str) -> dict[str, Any]:
    with (ROOT / rel).open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def close(a: float, b: float) -> bool:
    return math.isclose(float(a), float(b), rel_tol=1.0e-12, abs_tol=1.0e-12)


def normalized(values: list[float]) -> list[float]:
    return [value / values[0] for value in values]


def main() -> int:
    units = load(UNITS_REL)
    bridge = load(BRIDGE_REL)
    lanes = units["lanes"]
    ttg = next(item for item in lanes if item.get("lane_id") == "thermal_ttg_observable_bridge")
    characteristic = next(item for item in lanes if item.get("lane_id") == "matter_space_characteristic_cone_v1")

    phi_a = [0.2, 0.5, -0.1]
    phi_b = [2.0, 5.0, -1.0]
    alpha_a = 4.0
    alpha_b = 0.4
    delta_t_a = [alpha_a * value for value in phi_a]
    delta_t_b = [alpha_b * value for value in phi_b]
    e0_a = 1.0e4
    e0_b = 1.0e6
    cv = 1.0e6
    alpha_e0_a = e0_a / cv
    alpha_e0_b = e0_b / cv

    checks = {
        "characteristic_phi_is_dimensionless_normalized": characteristic["variables"]["Phi"] == "dimensionless normalized response",
        "ttg_phi_is_normalized": ttg["variables"]["Phi"] == "normalized effective response variable",
        "ttg_alpha_is_open": ttg["variables"]["alpha_Phi_K"] == "open scale in K per normalized Phi",
        "ttg_units_are_blocked": ttg["units_status"] == "BLOCKED_INDEPENDENT_ALPHA_Phi_K",
        "ttg_observable_is_normalized_operator": ttg["observable_operator"] == "y_TTG^UET(t)=Delta_Phi(t)/Delta_Phi(0); Delta_Tq=alpha_Phi_K*Delta_Phi",
        "base_phi_to_named_branch_open": bridge["conditional_inputs"]["base_Phi_to_Phi_E"]["status"] == "OPEN_DERIVATION_OR_CALIBRATION",
        "e0_open": bridge["conditional_inputs"]["e0"]["status"] == "OPEN_NOT_SOURCE_LOCKED",
        "numeric_alpha_not_emitted": bridge["numeric_calibration"]["alpha_Phi_K"] is None and bridge["numeric_calibration"]["alpha_Phi_E_K"] is None,
        "normalized_observable_invariant_under_phi_scale": all(close(a, b) for a, b in zip(normalized(phi_a), normalized(phi_b))),
        "dimensional_temperature_witness_invariant": all(close(a, b) for a, b in zip(delta_t_a, delta_t_b)),
        "alpha_values_are_distinct": not close(alpha_a, alpha_b),
        "e0_values_are_distinct": not close(e0_a, e0_b),
        "e0_to_alpha_values_are_distinct": not close(alpha_e0_a, alpha_e0_b),
        "no_holdout_or_target_in_witness": True,
    }
    status = "PASS_SCOPED_NO_GO_NORMALIZED_PHI_ENERGY_ANCHOR" if all(checks.values()) else "FAIL_PHI_ENERGY_ANCHOR_NO_GO_AUDIT"
    report = {
        "schema_version": "t13-phi-energy-anchor-identifiability-no-go-v1",
        "artifact": "t13_phi_energy_anchor_identifiability_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "normalized Phi and y_TTG cannot identify a numeric alpha_Phi_K without an additional dimensional anchor",
                "the existing normalized Core lane cannot identify e0 or base Phi-to-Phi_E correspondence",
                "a material c_v source alone cannot supply the missing Phi energy amplitude",
                "two explicit rescaled witnesses produce the same normalized observable and the same Delta_Tq while alpha values differ",
                "the no-go scope is separated from future action-derived or independently calibrated energy anchors"
            ],
            "equation_or_mapping": {
                "normalized": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
                "dimensional": "Delta_Tq = alpha_Phi_K * Delta_Phi",
                "scale_transformation": "Delta_Phi' = s Delta_Phi; alpha_Phi_K' = alpha_Phi_K/s",
                "named_energy_branch": "Phi_E = Delta_u/e0; alpha_Phi_E_K = e0/c_v",
                "anchor_invariance": "e0 and Delta_u can be jointly rescaled while Phi_E and the normalized lane remain unchanged when no base Phi-to-Phi_E map is declared"
            },
            "units": {
                "Phi": "dimensionless normalized response",
                "alpha_Phi_K": "K per normalized Phi; no numeric value identified",
                "e0": "J m^-3; open input",
                "c_v": "J m^-3 K^-1",
                "Delta_Tq": "K"
            },
            "derivation_class": "algebraic structural identifiability no-go with explicit scale witnesses",
            "observable": "normalized TTG operator and conditional dimensional response operator",
            "data_role": "INTERNAL_STRUCTURAL_AUDIT_NO_TARGET_OR_HOLDOUT",
            "evidence_artifacts": [
                {"path": UNITS_REL, "sha256": sha256(UNITS_REL)},
                {"path": BRIDGE_REL, "sha256": sha256(BRIDGE_REL)},
                {"path": "docs/core/07_artifacts/topic13/t13_phi_energy_anchor_identifiability_no_go.json"}
            ],
            "verification_status": status,
            "open_blockers": [
                "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
                "source-locked temperature-dependent UET free-energy coefficients missing",
                "regular equilibrium Phi branch with SI correspondence missing"
            ],
            "dependency_unlocked": "none; this closes a structural no-go lane and does not unlock full Topic 13 or Gravity",
            "claim_boundary": "The no-go applies only to deriving a numeric dimensional Phi-energy anchor from the current normalized lane and its material c_v comparator. It does not prove that an action-derived or independently measured anchor is impossible."
        },
        "witness": {
            "normalized_phi_a": phi_a,
            "normalized_phi_b": phi_b,
            "alpha_phi_k_a_K_per_normalized_phi": alpha_a,
            "alpha_phi_k_b_K_per_normalized_phi": alpha_b,
            "delta_tq_a_K": delta_t_a,
            "delta_tq_b_K": delta_t_b,
            "e0_a_J_per_m3": e0_a,
            "e0_b_J_per_m3": e0_b,
            "c_v_witness_J_per_m3_K": cv,
            "alpha_phi_e_a_K_per_normalized_phi_e": alpha_e0_a,
            "alpha_phi_e_b_K_per_normalized_phi_e": alpha_e0_b,
            "target_or_holdout_used": False
        },
        "checks": checks,
        "controlling_blocker": "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
        "next_controller": "Either derive e0 and the base Phi-to-Delta_u_ph correspondence from a declared dimensionful UET action/free-energy origin, or obtain an independent response calibration with measured energy density and Phi amplitude. Do not fit this anchor to TTG residuals or read Xie 2026.",
        "claim_boundary": "Scoped structural no-go only; no numeric e0 or alpha_Phi_K is emitted."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"), "failed_checks": [key for key, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
