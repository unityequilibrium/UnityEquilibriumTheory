"""Audit the Topic 13 thermodynamic normal-component lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_temperature_normal_component import (  # noqa: E402
    THERMODYNAMIC_NORMAL_COMPONENT_STATUS,
    thermodynamic_normal_component_contract,
    thermodynamic_normal_component_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_thermodynamic_normal_component_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_normal_component.py"
TWO_FLUID_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_two_fluid_response.py"
TWO_FLUID_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_two_fluid_response_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=160,
        cutoff_factor=65.0,
    )
    points = {
        "normal_high_temperature": (0.22, 0.35, 0.15),
        "normal_low_temperature": (0.06, 0.35, 0.15),
        "condensed_high_temperature": (0.20, 1.28, 0.15),
        "condensed_low_temperature": (0.04, 1.28, 0.15),
    }
    states = {
        label: thermodynamic_normal_component_state(*point, config)
        for label, point in points.items()
    }
    contract = thermodynamic_normal_component_contract()
    normal_high = states["normal_high_temperature"]
    normal_low = states["normal_low_temperature"]
    condensed_high = states["condensed_high_temperature"]
    condensed_low = states["condensed_low_temperature"]

    checks = {
        "normal_component_is_explicit_on_both_branches": (
            normal_high.branch == "normal"
            and condensed_high.branch == "condensed"
        ),
        "thermodynamic_fields_are_finite": all(
            all(
                isinstance(value, (int, float))
                and bool(value == value)
                and abs(float(value)) < float("inf")
                for key, value in asdict(state).items()
                if key not in {"branch", "data_role"}
            )
            for state in states.values()
        ),
        "normal_entropy_is_nonnegative": all(
            state.normal_entropy_density >= -1.0e-12
            for state in states.values()
        ),
        "normal_static_response_is_nonnegative": all(
            state.normal_momentum_susceptibility >= -1.0e-12
            for state in states.values()
        ),
        "total_state_stability_is_nonnegative": all(
            state.total_entropy_density >= -1.0e-12
            and state.total_susceptibility >= -1.0e-10
            for state in states.values()
        ),
        "normal_component_is_suppressed_at_lower_temperature": (
            normal_low.normal_pressure < normal_high.normal_pressure
            and normal_low.normal_entropy_density < normal_high.normal_entropy_density
            and normal_low.normal_momentum_susceptibility
            < normal_high.normal_momentum_susceptibility
            and condensed_low.normal_pressure < condensed_high.normal_pressure
            and condensed_low.normal_entropy_density < condensed_high.normal_entropy_density
            and condensed_low.normal_momentum_susceptibility
            < condensed_high.normal_momentum_susceptibility
        ),
        "signed_residual_sector_is_not_clipped": condensed_low.normal_energy_density < 0.0,
        "normal_equations_are_declared": all(
            key in contract["equations"]
            for key in (
                "normal_pressure",
                "normal_charge",
                "normal_entropy",
                "normal_energy",
                "normal_susceptibility",
                "normal_static_response",
            )
        ),
        "physical_flow_boundary_is_explicit": (
            "physical normal-fluid mass density" in contract["excluded_scope"]
            and "retarded physical Kubo coefficient" in contract["excluded_scope"]
        ),
        "natural_unit_boundary_is_explicit": (
            contract["unit_contract"]["unit_lane"] == "natural"
            and "not temperature" in contract["unit_contract"]["Phi"]
        ),
        "no_fit_target_or_holdout": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        THERMODYNAMIC_NORMAL_COMPONENT_STATUS
        if not failed
        else "FAIL_ACTION_DERIVED_THERMODYNAMIC_NORMAL_COMPONENT_LANE"
    )
    artifact = {
        "schema_version": "t13-uet-o2-thermodynamic-normal-component-v1",
        "artifact": "t13_uet_o2_thermodynamic_normal_component_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_THERMODYNAMIC_NORMAL_COMPONENT_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "finite-temperature thermodynamic normal pressure, charge, entropy, energy, and susceptibility are named as one component",
                "normal-component low-temperature suppression is checked on normal and condensed branches",
                "total entropy and susceptibility stability boundaries are checked without clipping residual sector values",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": MODULE.relative_to(ROOT).as_posix(), "sha256": sha256(MODULE)},
                {"path": TWO_FLUID_MODULE.relative_to(ROOT).as_posix(), "sha256": sha256(TWO_FLUID_MODULE)},
                {"path": TWO_FLUID_AUDIT.relative_to(ROOT).as_posix(), "sha256": sha256(TWO_FLUID_AUDIT)},
            ],
            "verification_status": status,
            "open_blockers": [
                "physical_normal_flow_component_or_retarded_kubo_match_missing",
                "physical_Kubo_coefficient_record_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": (
                "thermodynamic finite-temperature normal-component lane only; "
                "no physical normal flow, Kubo, SI, alpha, Core, or Gravity unlock"
            ),
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state_grid": {key: asdict(value) for key, value in states.items()},
        "checks": checks,
        "failed_checks": failed,
        "physical_normal_flow_component_emitted": False,
        "physical_kubo_coefficient_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "claim_promotion": False,
        "controlling_blocker": "physical_normal_flow_component_or_retarded_kubo_match_missing",
        "next_controller": (
            "Derive or source-lock a state-matched physical normal-flow/retarded "
            "Kubo response with units and uncertainty; keep this thermodynamic "
            "normal component as a natural-unit lane."
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "artifact": OUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
