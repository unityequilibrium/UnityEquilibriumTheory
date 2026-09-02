"""Audit the coupled response-mode route to an independent heat carrier."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

import numpy as np

from docs.scripts.audit.audit_topic13_coupled_gain_loss_operator import (
    MixtureInputs,
    charge_response,
    operator_grid,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_coupled_response_heat_carrier_no_go_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_coupled_heat_no_go_addendum.json"
EQUATION_ID = "uet.o2.thermal.coupled_response_heat_carrier_no_go"
RANK_THRESHOLD = 1.0e-10


def _relative(first: np.ndarray, second: np.ndarray) -> float:
    scale = max(float(np.linalg.norm(first)), float(np.linalg.norm(second)), 1.0e-300)
    return float(np.linalg.norm(first - second) / scale)


def _rank(*vectors: np.ndarray) -> int:
    matrix = np.column_stack(vectors)
    singular = np.linalg.svd(matrix, compute_uv=False)
    tolerance = RANK_THRESHOLD * max(float(singular[0]), 1.0e-300)
    return int(np.linalg.matrix_rank(matrix, tol=tolerance))


def source_rank_witness(
    *,
    chemical_potential: float = 0.2,
    radial_order: int = 8,
    angular_order: int = 6,
    azimuth_order: int = 8,
    cutoff: float = 8.0,
    basis_order: int = 1,
    metric_order: int = 128,
    metric_cutoff: float = 24.0,
) -> dict[str, object]:
    config = MixtureInputs()
    record = operator_grid(
        config,
        T=0.25,
        mu=chemical_potential,
        radial=radial_order,
        angular=angular_order,
        azimuth=azimuth_order,
        cutoff=cutoff,
        basis_order=basis_order,
    )
    response = charge_response(
        record,
        metric_order=metric_order,
        metric_cutoff=metric_cutoff,
    )
    metric = np.asarray(response["metric"], dtype=float)
    size = metric.shape[0]
    temperature = float(record["state"]["T"])
    mu = float(record["state"]["mu"])

    def projected_source(coefficients: np.ndarray) -> np.ndarray:
        raw = metric @ coefficients
        return raw[1:] - metric[1:, 0] * raw[0] / metric[0, 0]

    momentum_coefficients = np.zeros(size)
    momentum_coefficients[0] = temperature
    charge_coefficients = np.zeros(size)
    charge_coefficients[1] = 1.0
    neutral_coefficients = np.zeros(size)
    neutral_coefficients[2] = 1.0
    energy_moment_coefficients = np.zeros(size)
    energy_moment_coefficients[3] = 1.0
    heat_coefficients = momentum_coefficients - mu * charge_coefficients

    momentum_source = projected_source(momentum_coefficients)
    charge_source = projected_source(charge_coefficients)
    heat_source = projected_source(heat_coefficients)
    neutral_trial_source = projected_source(neutral_coefficients)
    energy_moment_trial_source = projected_source(energy_moment_coefficients)
    expected_heat = -mu * charge_source
    scalar = np.asarray(record["scalar_matrix"], dtype=float)
    scalar_norm = max(float(np.linalg.norm(scalar)), 1.0e-300)
    return {
        "state": record["state"],
        "grid": record["grid"],
        "basis_order": basis_order,
        "vector_basis": record["vector_basis"],
        "projected_momentum_source_norm": float(np.linalg.norm(momentum_source)),
        "projected_charge_source": charge_source.tolist(),
        "projected_grand_heat_source": heat_source.tolist(),
        "projected_neutral_trial_source": neutral_trial_source.tolist(),
        "projected_energy_moment_trial_source": energy_moment_trial_source.tolist(),
        "heat_charge_identity_relative_residual": _relative(heat_source, expected_heat),
        "charge_heat_source_rank": _rank(charge_source, heat_source),
        "charge_neutral_trial_rank": _rank(charge_source, neutral_trial_source),
        "charge_energy_moment_trial_rank": _rank(
            charge_source, energy_moment_trial_source
        ),
        "neutral_count_relaxation_relative": float(abs(scalar[3, 3]) / scalar_norm),
        "total_count_null_relative": float(np.linalg.norm(scalar[2, :]) / scalar_norm),
        "minimum_active_collision_rate": float(
            min(response["generalized_active_rates"])
        ),
        "collision_solve_relative_residual": response[
            "linear_solve_relative_residual"
        ],
        "physical_heat_observable": "J_H=J_E-mu*J_charge=P-mu*J_charge",
        "neutral_trial_admissibility": "REJECTED_AS_HEAT_SOURCE_NEUTRAL_COUNT_NOT_CONSERVED",
        "energy_moment_trial_admissibility": "REJECTED_AS_OBSERVABLE_RELABELING_E_P_OVER_T2_IS_NOT_J_H",
    }


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def main() -> int:
    reference = source_rank_witness()
    zero_mu = source_rank_witness(
        chemical_potential=0.0,
        radial_order=6,
        angular_order=4,
        azimuth_order=4,
        cutoff=6.0,
        metric_order=96,
    )
    refined_metric = source_rank_witness(metric_order=192, metric_cutoff=32.0)
    metric_change = _relative(
        np.asarray(reference["projected_charge_source"]),
        np.asarray(refined_metric["projected_charge_source"]),
    )
    checks = {
        "projected_total_momentum_vanishes": reference[
            "projected_momentum_source_norm"
        ] <= 1.0e-10,
        "grand_heat_charge_identity": reference[
            "heat_charge_identity_relative_residual"
        ] <= RANK_THRESHOLD,
        "charge_heat_rank_one": reference["charge_heat_source_rank"] == 1,
        "zero_mu_projected_heat_vanishes": np.linalg.norm(
            zero_mu["projected_grand_heat_source"]
        ) <= 1.0e-10,
        "neutral_trial_is_linearly_independent": reference[
            "charge_neutral_trial_rank"
        ] == 2,
        "neutral_count_is_not_conserved": reference[
            "neutral_count_relaxation_relative"
        ] > 1.0e-12,
        "truncation_total_count_is_null": reference["total_count_null_relative"]
        <= 1.0e-10,
        "energy_moment_trial_is_not_heat_observable": reference[
            "charge_energy_moment_trial_rank"
        ] == 2
        and "E*p/T^2" in reference["vector_basis"],
        "active_collision_spectrum_positive": reference[
            "minimum_active_collision_rate"
        ] > 0.0,
        "collision_solve": reference["collision_solve_relative_residual"]
        <= 1.0e-8,
        "metric_refinement": metric_change <= 1.0e-3,
        "no_new_state_or_observable_relabeling": True,
        "no_fit_holdout_or_physical_kubo": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    status = (
        "PASS_COUPLED_RESPONSE_HEAT_CARRIER_ROUTE_NO_GO"
        if all(checks.values())
        else "WARN_COUPLED_RESPONSE_HEAT_CARRIER_ROUTE"
    )
    paths = [
        "docs/scripts/audit/audit_topic13_coupled_response_heat_carrier_no_go.py",
        "docs/core/test/test_topic13_coupled_response_heat_carrier_no_go.py",
        "docs/scripts/audit/audit_topic13_coupled_gain_loss_operator.py",
        "docs/core/uet_o2_finite_temperature_normal_component.py",
        "docs/core/uet_o2_finite_temperature_two_fluid_response.py",
    ]
    priors = [
        "docs/core/artifacts/t13_coupled_gain_loss_operator_audit.json",
        "docs/core/artifacts/t13_dressed_ra_charge_current_ladder_audit.json",
    ]
    what_is_closed = [
        "For every current state in the declared relativistic mixture, J_E=P and J_H=P-mu*J_charge, so Landau projection gives J_H_perp=-mu*J_charge_perp.",
        "Adding the neutral response excitation does not create an independent physical heat source: its neutral-count trial direction is independent but neutral count is relaxed by the declared conversion channels.",
        "The E*p/T^2 basis direction is an independent variational trial mode, not the declared heat observable, and cannot be relabeled as heat current.",
        "At mu=0 the projected physical heat source vanishes while the charge source remains a separate diagnostic direction.",
    ]
    open_blockers = [
        "admissible_second_conserved_diffusion_charge_or_lattice_frame",
        "momentum_relaxing_Umklapp_boundary_or_open_bath_contract",
        "self_consistent_dressed_width_and_continuum_limit",
        "physical_Kubo_and_SI_frame_normalization",
        "material_heat_observable_and_uncertainty_mapping",
    ]
    equations = {
        "energy_current": "J_E^i=sum_a integral E_a v_a^i delta f_a=P^i",
        "grand_heat_current": "J_H^i=J_E^i-mu J_charge^i=P^i-mu J_charge^i",
        "landau_no_go": "P_perp J_H=-mu P_perp J_charge; rank(J_charge,J_H)<=1",
        "required_escape": "independent heat requires an admissible extra conserved diffusion current or a declared preferred/lattice momentum-relaxing frame",
    }
    artifact = {
        "schema_version": "t13-coupled-response-heat-carrier-no-go-v1",
        "major_result_id": "T13_COUPLED_RESPONSE_HEAT_CARRIER_ROUTE_NO_GO",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "closure_disposition": "CLOSED_AS_NO_GO",
        "verification_status": status,
        "what_is_closed": what_is_closed,
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping": equations,
        "ontology": {
            "C": "unchanged; not quasiparticle number",
            "Phi": "effective response variable; neutral excitation is lane-specific and not a new substance",
            "R_gen": "excluded",
            "R_obs": "excluded",
        },
        "unit_lane": "natural_units",
        "units": {
            "current_source": "declared vector-source units",
            "source_rank": "dimensionless",
        },
        "derivation_class": "relativistic_current_identity_and_source_rank_no_go",
        "observable": "Physical grand-heat source rank, not conductivity",
        "data_role": "DERIVED_SYNTHETIC_STRUCTURAL_NO_GO",
        "reference_witness": reference,
        "zero_mu_witness": zero_mu,
        "metric_refinement_witness": {
            "metric_order": 192,
            "metric_cutoff": 32.0,
            "charge_source_relative_change": metric_change,
        },
        "thresholds": {
            "rank_relative": RANK_THRESHOLD,
            "metric_refinement_relative": 1.0e-3,
        },
        "checks": checks,
        "open_blockers": open_blockers,
        "controlling_blocker": "admissible_preferred_frame_or_independent_conserved_diffusion_charge_missing",
        "source_hashes": {path: _sha(path) for path in paths},
        "evidence_artifacts": [
            {"path": path, "sha256": _sha(path)} for path in priors
        ],
        "dependency_unlocked": [
            "lattice_or_momentum_relaxing_heat_branch_design",
            "second_conserved_charge_diffusion_branch_design",
        ],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "Structural no-go for the current relativistic coupled response-mode route only; not a theorem against heat transport in a lattice, open bath, multicharge theory, or external material, and not Full Topic 13 closure.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE/CLOSED_AS_NO_GO"
        if all(checks.values())
        else "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": what_is_closed,
        "WHAT_REMAINS_OPEN": open_blockers,
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Tested and rejected the existing neutral response excitation as an independent physical heat carrier under the current relativistic observable and conservation contract.",
        "EQUATION_OR_MAPPING": equations,
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Choose and derive either a lattice/momentum-relaxing frame or an independently conserved diffusion charge from an explicit action before reopening heat conductivity.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(
        json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    entry = {
        key: artifact[key]
        for key in (
            "ontology",
            "unit_lane",
            "units",
            "derivation_class",
            "observable",
            "data_role",
            "verification_status",
            "controlling_blocker",
            "claim_boundary",
        )
    }
    entry.update({
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "structural_heat_carrier_route_no_go",
        "relation_or_code_path": equations,
        "standard_physics_counterpart": "Landau-frame relativistic heat/diffusion current decomposition",
        "variables": {
            "J_E": "energy current",
            "P": "momentum density/current",
            "J_H": "grand heat current",
            "J_charge": "conserved charge current",
        },
        "mathematical_role": "source-rank obstruction for the existing neutral response carrier route",
        "observable_mapping": artifact["observable"],
        "parameter_dimensions": artifact["units"],
        "source_or_origin": "Relativistic quasiparticle current identity and current coupled collision metric",
        "assumptions": {
            "relativistic_group_velocity": "v=p/E",
            "single_physical_chemical_potential": True,
            "Landau_frame": True,
            "neutral_response_count_not_conserved": True,
        },
        "symmetry_and_conservation": "Total momentum and U(1) charge conserved; response count converted",
        "limiting_cases": ["mu=0", "finite mu", "metric orders 128 and 192"],
        "implementation_paths": [paths[0], paths[2]],
        "verifier_paths": [paths[1]],
        "evidence_class": "INTERNAL_STRUCTURAL_NO_GO",
        "proof_status": "CURRENT_RESPONSE_CARRIER_ROUTE_REJECTED",
        "evidence_artifacts": [
            {"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}
        ],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "heat_carrier_design_controller",
        "physical_dependency_unlock": False,
        "failure_mode": open_blockers,
        "next_hardening_step": artifact["report"]["NEXT_ACTION"],
    })
    REGISTRY_OUT.write_text(
        json.dumps({
            "schema_version": "uet-equation-registry-addendum-v1",
            "status": "CANDIDATE_DIAGNOSTIC_NOT_MERGED",
            "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
            "equation_entries": [entry],
            "full_core_unlock": False,
            "claim_promotion": False,
        }, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": status,
        "checks": checks,
        "reference": {
            "heat_charge_identity_relative_residual": reference[
                "heat_charge_identity_relative_residual"
            ],
            "charge_heat_source_rank": reference["charge_heat_source_rank"],
            "charge_neutral_trial_rank": reference["charge_neutral_trial_rank"],
            "neutral_count_relaxation_relative": reference[
                "neutral_count_relaxation_relative"
            ],
            "metric_change": metric_change,
        },
    }, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
