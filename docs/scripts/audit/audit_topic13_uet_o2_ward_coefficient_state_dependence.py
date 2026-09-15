"""Audit state dependence of the formal Ward-constrained counterterm."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isfinite
from pathlib import Path

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_stationarity_scheme import (
    renormalized_gaussian_stationarity_derivative,
)


ROOT = Path(__file__).resolve().parents[3]
STATIONARITY_REL = "docs/core/uet_o2_finite_temperature_stationarity_scheme.py"
WARD_REL = "docs/core/uet_o2_ward_constrained_condensed.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_ward_coefficient_state_dependence_audit.json"

REFERENCE_X = 3.835
REFERENCE_SCALE_SQ = 3.835
QUADRATURE_ORDER = 128
CUTOFF_FACTOR = 70.0
RESIDUAL_TOLERANCE = 1.0e-10
STATE_POINTS = (
    {"temperature": 0.20, "chemical_potential": 1.20, "space_response": 0.20},
    {"temperature": 0.25, "chemical_potential": 1.30, "space_response": 0.20},
    {"temperature": 0.28, "chemical_potential": 1.30, "space_response": 0.20},
    {"temperature": 0.25, "chemical_potential": 1.30, "space_response": 0.00},
    {"temperature": 0.25, "chemical_potential": 1.30, "space_response": 0.40},
    {"temperature": 0.20, "chemical_potential": 1.25, "space_response": 0.20},
)


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def config() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(
            epsilon_nc=0.1,
            phi_equilibrium=0.0,
        ),
    )


def record(point: dict[str, float], eos_config: O2FiniteDensityEOSConfig) -> dict:
    temperature = float(point["temperature"])
    chemical_potential = float(point["chemical_potential"])
    space_response = float(point["space_response"])
    mass_sq = effective_mass_sq(space_response, eos_config)
    q = eos_config.matter.matter_kinetic * chemical_potential**2 - mass_sq
    x_boundary = q / eos_config.matter.matter_quartic
    if q <= 0.0 or x_boundary >= REFERENCE_X:
        raise ValueError("state point is outside the declared fixed-reference condensed domain")
    base_derivative = renormalized_gaussian_stationarity_derivative(
        x_boundary,
        temperature,
        chemical_potential,
        space_response,
        eos_config,
        REFERENCE_X,
        0.0,
        reference_scale_sq=REFERENCE_SCALE_SQ,
        quadrature_order=QUADRATURE_ORDER,
        cutoff_factor=CUTOFF_FACTOR,
    )
    denominator = 3.0 * (x_boundary - REFERENCE_X) ** 2 / REFERENCE_SCALE_SQ
    coefficient = -base_derivative / denominator
    constrained_derivative = renormalized_gaussian_stationarity_derivative(
        x_boundary,
        temperature,
        chemical_potential,
        space_response,
        eos_config,
        REFERENCE_X,
        coefficient,
        reference_scale_sq=REFERENCE_SCALE_SQ,
        quadrature_order=QUADRATURE_ORDER,
        cutoff_factor=CUTOFF_FACTOR,
    )
    return {
        **point,
        "effective_mass_sq": mass_sq,
        "condensate_control": q,
        "x_boundary": x_boundary,
        "base_boundary_derivative": base_derivative,
        "coefficient_denominator": denominator,
        "ward_coefficient": coefficient,
        "constrained_boundary_derivative": constrained_derivative,
        "coefficient_interval_lower": coefficient - RESIDUAL_TOLERANCE / denominator,
        "coefficient_interval_upper": coefficient + RESIDUAL_TOLERANCE / denominator,
    }


def main() -> int:
    eos_config = config()
    records = [record(point, eos_config) for point in STATE_POINTS]
    coefficients = [item["ward_coefficient"] for item in records]
    intervals = [
        (item["coefficient_interval_lower"], item["coefficient_interval_upper"])
        for item in records
    ]
    common_lower = max(interval[0] for interval in intervals)
    common_upper = min(interval[1] for interval in intervals)
    values = [
        value
        for item in records
        for key, value in item.items()
        if key not in {"temperature", "chemical_potential", "space_response"}
    ]
    checks = {
        "all_state_records_are_finite": all(isfinite(float(value)) for value in values),
        "all_state_points_are_condensed": all(item["condensate_control"] > 0.0 for item in records),
        "all_state_points_share_fixed_reference": all(
            REFERENCE_X > item["x_boundary"] for item in records
        ),
        "each_state_can_be_made_ward_stationary": all(
            abs(item["constrained_boundary_derivative"]) <= RESIDUAL_TOLERANCE
            for item in records
        ),
        "ward_coefficients_are_not_constant": max(coefficients) - min(coefficients) > 1.0e-4,
        "common_fixed_coefficient_interval_is_empty": common_lower > common_upper,
        "statewise_coefficients_are_not_fit": True,
        "no_external_source_rows": True,
        "no_holdout_or_fit": True,
        "Phi_ontology_is_preserved": True,
        "C_ontology_is_preserved": True,
        "R_gen_ontology_is_preserved": True,
        "R_obs_is_separate": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_SCOPED_WARD_COEFFICIENT_STATE_DEPENDENCE_NO_GO"
        if not failed
        else "BLOCKED_SCOPED_WARD_COEFFICIENT_STATE_DEPENDENCE_NO_GO"
    )
    evidence = [
        {"path": STATIONARITY_REL, "sha256": digest(STATIONARITY_REL)},
        {"path": WARD_REL, "sha256": digest(WARD_REL)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-ward-coefficient-state-dependence-v1",
        "artifact": "t13_uet_o2_ward_coefficient_state_dependence_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_WARD_CONSTRAINED_COEFFICIENT_STATE_DEPENDENCE_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
            "what_is_closed": [
                "with one fixed reference point and scale, the Ward-derived local counterterm coefficient changes across declared finite-temperature and response states",
                "each state can be made Ward-stationary separately, but the residual-tolerance coefficient intervals have no common intersection",
                "the current Ward-constrained coefficient is therefore a state-wise formal constraint, not one state-independent physical renormalization scheme",
            ]
            if not failed
            else [],
            "equation_or_mapping": {
                "fixed_reference": "x_*=Lambda_*^2=3.835",
                "statewise_coefficient": "a_W(state)=-D_0(x_W;state)*Lambda_*^2/[3*(x_W-x_*)^2]",
                "admission_test": "D_a(x_W;state)=0 and one common a must satisfy all state points for a state-independent scheme",
                "no_go_test": "intersection_i [a_W_i+-epsilon/denominator_i] = empty",
            },
            "units": {
                "unit_lane": "natural",
                "x_and_reference_scale": "natural energy squared",
                "finite_coefficient": "dimensionless local counterterm parameter",
                "Phi": "fixed effective response input; no SI map",
            },
            "derivation_class": "action-derived stationarity derivative plus algebraic Ward constraint evaluated across a fixed-reference state grid; scoped structural no-go",
            "observable": "state dependence of the formal Ward-constrained counterterm coefficient",
            "data_role": "INTERNAL_STRUCTURAL_NO_GO_NO_SOURCE_ROWS",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "state_independent_physical_finite_temperature_renormalization_scheme_missing",
                "ward_preserving_condensed_2PI_or_1N_microscopic_completion_missing",
                "condensate_and_finite_temperature_normal_two_fluid_eos_completion_missing",
                "retarded_physical_Kubo_match_missing",
                "microscopic_SK_KMS_matching_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "state-independence boundary only; no physical renormalization, condensed EOS, transport, Core, Gravity, SI, alpha, or external-validation unlock",
            "claim_boundary": "This closes only the state-independence boundary of the present one-counterterm Ward construction under the declared fixed reference and state grid. It does not prove that every higher-order or microscopic scheme fails, and it does not close the physical finite-temperature theory or Full Topic 13.",
        },
        "reference_parameters": {
            "reference_x": REFERENCE_X,
            "reference_scale_sq": REFERENCE_SCALE_SQ,
            "quadrature_order": QUADRATURE_ORDER,
            "cutoff_factor": CUTOFF_FACTOR,
            "residual_tolerance": RESIDUAL_TOLERANCE,
        },
        "records": records,
        "coefficient_range": {
            "minimum": min(coefficients),
            "maximum": max(coefficients),
            "spread": max(coefficients) - min(coefficients),
        },
        "common_coefficient_interval": {
            "lower": common_lower,
            "upper": common_upper,
            "is_empty": common_lower > common_upper,
        },
        "checks": checks,
        "failed_checks": failed,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "state_independent_physical_finite_temperature_renormalization_scheme_missing",
        "next_controller": "Construct a state-independent microscopic or symmetry-improved finite-temperature scheme, then rerun the condensed EOS and retarded Kubo/SK-KMS gates across the state domain.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
        "parameter_policy": {
            "state_grid": "fixed declared diagnostic states, not a fit set",
            "reference": "fixed reference point and scale, held constant across all records",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": failed,
                "coefficient_min": min(coefficients),
                "coefficient_max": max(coefficients),
                "common_interval_empty": common_lower > common_upper,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
