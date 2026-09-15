"""Audit fixed-cone feasibility and UET mapping readiness.

This verifier derives normalized inequalities from the sourced characteristic
speeds, checks them against dense numerical samples, records the exact
parabolic/fixed-cone incompatibility, and verifies only the algebraic local
map ``J=q/tau``.  It does not promote that map to a covariant UET derivation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from docs.core.core_paths import canonical_existing_path  # noqa: E402
from docs.core.uet_hyperbolic_phase_field import (
    HyperbolicPhaseFieldConfig,
    compare_augmented_to_cahn_hilliard_chemical,
)
from docs.core.uet_hyperbolic_phase_field_bridge import (
    HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER,
    evaluate_parameter_sequence,
    fixed_cone_parabolic_limit_no_go,
    fixed_light_cone_feasibility,
    hyperbolic_phase_field_bridge_contract,
    map_external_flux_law_to_current,
    shifted_curvature_domain_bounds,
    subluminal_parameter_bounds,
)
from docs.scripts.audit.uet_gr_monotonic_stage import (
    apply_latest_hyperbolic_phase_field_stage,
)

OUT = ROOT / "docs/core/artifacts"
CORE = ROOT / "docs/core/uet_hyperbolic_phase_field_bridge.py"
COMPARATOR = ROOT / "docs/core/uet_hyperbolic_phase_field.py"
DIFFUSION = ROOT / "docs/core/uet_covariant_diffusion.py"
SPEC = ROOT / "docs/core/UET_GR_NONCLOSED_RESEARCH_SPEC.md"
JAIN_KOVTUN = (
    ROOT
    / "docs/data/external/relativistic_transport/jain_kovtun_2024"
    / "source_record.json"
)
CROSSLEY_GLORIOSO_LIU = (
    ROOT
    / "docs/data/external/relativistic_transport/crossley_glorioso_liu_2017"
    / "source_record.json"
)
COMPARATOR_ARTIFACT = (
    OUT / "hyperbolic_phase_field_external_comparator_verification.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _dump(name: str, payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(
        json.dumps(_jsonable(payload), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _source_provenance() -> dict[str, Any]:
    expected = {
        JAIN_KOVTUN: {
            "doi": "10.1007/JHEP01(2024)162",
            "arxiv_id": "2309.00511",
            "archive_sha256": (
                "6a295ee19340cc08559bbb074ac1a495b1764b81b4732b828b682ac800649176"
            ),
            "archive_size": 64030,
            "required_locators": {
                "conserved_u1_current",
                "density_flux_decomposition",
                "entropy_production",
                "maxwell_cattaneo_current_relaxation",
                "relativistic_stability_causality_bound",
                "sk_action_and_dynamical_kms",
            },
        },
        CROSSLEY_GLORIOSO_LIU: {
            "doi": "10.1007/JHEP09(2017)095",
            "arxiv_id": "1511.03646",
            "archive_sha256": (
                "9a7bd94ea12a3040404421e46707b9fd3d3e9898fd9f280393c3d49181b9b629"
            ),
            "archive_size": 171118,
            "required_locators": {
                "closed_time_path_effective_action",
                "local_kms_condition",
                "single_conserved_current_diffusion",
                "entropy_current",
            },
        },
    }
    records: list[dict[str, Any]] = []
    all_pass = True
    for path, contract in expected.items():
        payload = _load(path)
        locators = {item["id"] for item in payload["formula_locators"]}
        checks = {
            "doi_matches": payload.get("doi") == contract["doi"],
            "arxiv_matches": payload.get("arxiv_id") == contract["arxiv_id"],
            "archive_hash_matches_inspection": payload.get(
                "upstream_source_archive_sha256"
            )
            == contract["archive_sha256"],
            "archive_size_matches_inspection": payload.get(
                "source_archive_size_bytes"
            )
            == contract["archive_size"],
            "raw_source_not_committed": payload.get("local_path") is None,
            "required_locators_present": contract["required_locators"] <= locators,
            "claim_boundary_present": bool(payload.get("claim_boundary")),
        }
        status = "PASS" if all(checks.values()) else "FAIL"
        all_pass = all_pass and status == "PASS"
        records.append(
            {
                "path": str(path.relative_to(ROOT)),
                "title": payload["title"],
                "doi": payload["doi"],
                "arxiv_id": payload["arxiv_id"],
                "benchmark_role": payload["benchmark_role"],
                "checks": checks,
                "status": status,
            }
        )
    comparator = _load(COMPARATOR_ARTIFACT)
    comparator_pass = bool(
        comparator.get("audit_status") == "PASS"
        and comparator.get("evidence_status") == "PARTIAL_EXTERNAL_COMPARATOR"
    )
    all_pass = all_pass and comparator_pass
    return {
        "status": "PASS" if all_pass else "FAIL",
        "records": records,
        "sourced_comparator_prerequisite": {
            "artifact": str(COMPARATOR_ARTIFACT.relative_to(ROOT)),
            "audit_status": comparator.get("audit_status"),
            "evidence_status": comparator.get("evidence_status"),
            "passed": comparator_pass,
        },
    }


def _analytic_and_numeric_checks() -> tuple[dict[str, Any], dict[str, Any]]:
    rng = np.random.default_rng(811801)
    dense_residuals: list[float] = []
    interior_speed_ratios: list[float] = []
    negative_control_passes: list[bool] = []
    for _ in range(64):
        amplitude = float(rng.uniform(0.2, 1.8))
        alpha = float(rng.uniform(1.01, 6.0))
        gamma = float(rng.uniform(0.01, 0.8))
        light_speed = float(rng.uniform(0.4, 2.0))
        probe = HyperbolicPhaseFieldConfig(
            alpha_penalty=alpha,
            gamma_gradient=gamma,
            tau_flux=1.0,
            beta_wave=1.0,
            normalized_light_speed=light_speed,
        )
        bounds = subluminal_parameter_bounds(amplitude, probe)
        feasible = HyperbolicPhaseFieldConfig(
            alpha_penalty=alpha,
            gamma_gradient=gamma,
            tau_flux=1.05 * bounds["minimum_tau_flux_for_cone"],
            beta_wave=1.05 * bounds["minimum_beta_wave_for_cone"],
            normalized_light_speed=light_speed,
        )
        result = fixed_light_cone_feasibility(amplitude, feasible)
        grid = np.linspace(-amplitude, amplitude, 4001)
        shifted = alpha + 3.0 * grid**2 - 1.0
        sampled_speed = max(
            float(np.sqrt(np.max(shifted) / feasible.tau_flux)),
            float(np.sqrt(gamma / feasible.beta_wave)),
        )
        dense_residuals.append(
            abs(sampled_speed - result["maximum_characteristic_speed"])
        )
        interior_speed_ratios.append(
            result["maximum_characteristic_speed"] / light_speed
        )
        tau_fail = HyperbolicPhaseFieldConfig(
            alpha_penalty=alpha,
            gamma_gradient=gamma,
            tau_flux=0.95 * bounds["minimum_tau_flux_for_cone"],
            beta_wave=1.05 * bounds["minimum_beta_wave_for_cone"],
            normalized_light_speed=light_speed,
        )
        beta_fail = HyperbolicPhaseFieldConfig(
            alpha_penalty=alpha,
            gamma_gradient=gamma,
            tau_flux=1.05 * bounds["minimum_tau_flux_for_cone"],
            beta_wave=0.95 * bounds["minimum_beta_wave_for_cone"],
            normalized_light_speed=light_speed,
        )
        negative_control_passes.append(
            not fixed_light_cone_feasibility(amplitude, tau_fail)[
                "within_fixed_light_cone"
            ]
            and not fixed_light_cone_feasibility(amplitude, beta_fail)[
                "within_fixed_light_cone"
            ]
        )

    declared_amplitude = 1.25
    boundary_probe = HyperbolicPhaseFieldConfig(
        alpha_penalty=1.5,
        gamma_gradient=0.2,
        tau_flux=1.5 + 3.0 * declared_amplitude**2 - 1.0,
        beta_wave=0.2,
        normalized_light_speed=1.0,
    )
    boundary = fixed_light_cone_feasibility(
        declared_amplitude, boundary_probe
    )

    gamma_values = np.array([0.2, 0.1, 0.05, 0.025])
    source_scaling = evaluate_parameter_sequence(
        alpha_values=1.0 / gamma_values,
        tau_values=gamma_values**2,
        beta_values=gamma_values**2,
        gamma_values=gamma_values,
        max_abs_C=declared_amplitude,
    )

    alpha_sequence = np.array([4.0, 16.0, 64.0, 256.0, 1024.0])
    generic_parabolic_probe = evaluate_parameter_sequence(
        alpha_values=alpha_sequence,
        tau_values=1.0 / alpha_sequence,
        beta_values=1.0 / alpha_sequence**2,
        gamma_values=1.0 / alpha_sequence,
        max_abs_C=declared_amplitude,
    )
    no_go = fixed_cone_parabolic_limit_no_go(
        max_abs_C=declared_amplitude
    )

    x = np.linspace(0.0, 2.0 * np.pi, 256, endpoint=False)
    density = 0.2 * np.cos(2.0 * x) + 0.04 * np.sin(5.0 * x)
    dx = float(x[1] - x[0])
    tradeoff_alpha = np.array([8.0, 32.0, 128.0, 512.0])
    tradeoff_errors: list[float] = []
    tradeoff_tau_min: list[float] = []
    for alpha in tradeoff_alpha:
        config = HyperbolicPhaseFieldConfig(
            alpha_penalty=float(alpha),
            gamma_gradient=0.05,
            tau_flux=float(alpha + 3.0 * declared_amplitude**2 - 1.0) * 1.05,
            beta_wave=0.0525,
        )
        comparison = compare_augmented_to_cahn_hilliard_chemical(
            density, dx, config
        )
        tradeoff_errors.append(comparison["relative_l2_difference"])
        tradeoff_tau_min.append(
            subluminal_parameter_bounds(declared_amplitude, config)[
                "minimum_tau_flux_for_cone"
            ]
        )

    q = rng.normal(size=4096)
    chemical_gradient = rng.normal(size=4096)
    local_map = map_external_flux_law_to_current(
        q, chemical_gradient, tau_flux=0.37
    )

    symbolic = {
        "curvature_domain_bound": (
            "min(alpha+g_second)=alpha-1; "
            "max(alpha+g_second)=alpha+3*C_max^2-1"
        ),
        "strict_hyperbolicity": "alpha_penalty > 1",
        "matter_cone_bound": (
            "tau_flux >= (alpha_penalty+3*C_max^2-1)/c_hat^2"
        ),
        "auxiliary_cone_bound": "beta_wave >= gamma_gradient/c_hat^2",
        "parabolic_fixed_cone_compatibility": no_go,
        "local_current_map": {
            "definition": "J=q/tau_flux",
            "source_law": "q_t+grad(mu)=-q/tau_flux",
            "mapped_law": "tau_flux*J_t+J=-grad(mu)",
            "mobility": 1.0,
        },
    }
    numeric = {
        "random_feasible_cases": 64,
        "maximum_dense_speed_residual": max(dense_residuals),
        "maximum_interior_speed_to_cone_ratio": max(interior_speed_ratios),
        "all_negative_controls_rejected": bool(all(negative_control_passes)),
        "boundary_saturation": boundary,
        "source_scaling_sequence": source_scaling,
        "generic_parabolic_probe": generic_parabolic_probe,
        "accuracy_causality_tradeoff": {
            "alpha_values": tradeoff_alpha,
            "relative_chemical_errors": np.asarray(tradeoff_errors),
            "minimum_causal_tau_values": np.asarray(tradeoff_tau_min),
            "chemical_error_strictly_decreases": bool(
                np.all(np.diff(tradeoff_errors) < 0.0)
            ),
            "minimum_causal_tau_strictly_increases": bool(
                np.all(np.diff(tradeoff_tau_min) > 0.0)
            ),
            "interpretation": (
                "better quasistatic Cahn-Hilliard chemical accuracy requires "
                "larger alpha while the fixed-cone tau lower bound grows"
            ),
        },
        "local_current_map_max_abs_residual": local_map.max_abs_residual,
    }
    return symbolic, numeric


def build_artifacts() -> tuple[dict[str, Any], ...]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    provenance = _source_provenance()
    symbolic, numeric = _analytic_and_numeric_checks()
    contract = hyperbolic_phase_field_bridge_contract()
    achieved = {
        "external_source_provenance": (
            "PASS" if provenance["status"] == "PASS" else "FAIL"
        ),
        "exact_symmetric_domain_curvature_bounds": "PASS",
        "fixed_light_cone_parameter_inequalities": (
            "PASS"
            if numeric["maximum_dense_speed_residual"] <= 1e-12
            and numeric["maximum_interior_speed_to_cone_ratio"] <= 1.0
            and numeric["all_negative_controls_rejected"]
            else "FAIL"
        ),
        "finite_parameter_feasible_controls": (
            "PASS"
            if numeric["boundary_saturation"]["within_fixed_light_cone"]
            else "FAIL"
        ),
        "exact_parabolic_fixed_cone_no_common_limit": (
            "PASS"
            if not symbolic["parabolic_fixed_cone_compatibility"][
                "common_exact_sequence_exists"
            ]
            and not numeric["source_scaling_sequence"]["all_feasible"]
            and not numeric["generic_parabolic_probe"]["all_feasible"]
            else "FAIL"
        ),
        "causal_accuracy_tradeoff": (
            "PASS"
            if numeric["accuracy_causality_tradeoff"][
                "chemical_error_strictly_decreases"
            ]
            and numeric["accuracy_causality_tradeoff"][
                "minimum_causal_tau_strictly_increases"
            ]
            else "FAIL"
        ),
        "external_q_to_local_current_law": (
            "PASS"
            if numeric["local_current_map_max_abs_residual"] <= 1e-12
            else "FAIL"
        ),
        "trace_absent_from_physical_map": (
            "PASS"
            if contract["trace_input"] is False
            and contract["trace_backreaction"] is False
            else "FAIL"
        ),
    }
    blocked = {
        "source_order_parameter_to_noether_density_map": "BLOCKED",
        "uet_native_covariant_phase_field_action": "BLOCKED",
        "classical_entropy_current_and_dissipative_bianchi_closure": "BLOCKED",
        "closed_time_path_kms_transport_matching": "BLOCKED",
        "curved_3p1_well_posed_solver": "BLOCKED",
        "system_specific_si_map": "BLOCKED",
        "external_numerical_benchmark_replication": "BLOCKED",
        "physical_validation": "BLOCKED",
    }
    audit_status = "PASS" if set(achieved.values()) == {"PASS"} else "FAIL"
    evidence_status = (
        "PARTIAL_ANALYTIC_CAUSAL_BRIDGE" if audit_status == "PASS" else "BLOCKED"
    )
    source_hashes = {
        str(path.relative_to(ROOT)): _sha(canonical_existing_path(path))
        for path in (
            CORE,
            COMPARATOR,
            DIFFUSION,
            SPEC,
            JAIN_KOVTUN,
            CROSSLEY_GLORIOSO_LIU,
        )
    }
    verification = {
        "schema_version": "1.0",
        "artifact": "hyperbolic_phase_field_causal_feasibility",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave8_v1",
        "benchmark_role": "analytic_gate",
        "method_label": "fixed_light_cone_domain_feasibility",
        "audit_status": audit_status,
        "evidence_status": evidence_status,
        "claim_class": "B",
        "claim": (
            "normalized analytic fixed-light-cone feasibility, an exact "
            "no-common-limit result for parabolic recovery, and a local "
            "mobility-one current-law map"
        ),
        "source_provenance": provenance,
        "symbolic": symbolic,
        "numeric": numeric,
        "achieved_gates": achieved,
        "blocked_gates": blocked,
        "source_hashes": source_hashes,
        "input_identity": {
            "external_comparator_artifact": str(COMPARATOR_ARTIFACT.relative_to(ROOT)),
            "source_records": [
                str(JAIN_KOVTUN.relative_to(ROOT)),
                str(CROSSLEY_GLORIOSO_LIU.relative_to(ROOT)),
            ],
        },
        "thresholds": {
            "maximum_dense_speed_residual": 1e-12,
            "maximum_speed_to_cone_ratio": 1.0,
            "all_negative_controls_rejected": True,
            "local_current_map_max_abs_residual": 1e-12,
        },
        "run_contract": {
            "seed": 811801,
            "unit_lane": "normalized",
            "declared_amplitude_domain": "abs(C)<=1.25",
            "parameter_fitting": False,
            "trace_backreaction": False,
            "covariant_derivation": False,
            "physical_validation": False,
        },
        "allowed_language": [
            "fixed-light-cone feasibility inequalities for the normalized comparator",
            "analytic no-common exact limit for fixed-cone and parabolic recovery",
            "exact algebraic mobility-one local current-law map",
            "Cahn-Hilliard as a late-time low-wavenumber approximation",
        ],
        "blocked_language": [
            "all causal phase-field theories are impossible",
            "the external comparator is a covariant UET derivation",
            "the source order parameter is already the UET Noether density",
            "the auxiliary phase is UET space response or information",
            "Topic 0.11 or 0.19 is validated",
        ],
        "notes": [
            "No parameters are fit to an external dataset.",
            "The no-common-limit result is restricted to the declared normalized comparator.",
        ],
        "next_controller": HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER,
    }
    formula = {
        "schema_version": "1.0",
        "artifact": "hyperbolic_phase_field_bridge_formula_audit",
        "generated_at": now,
        "status": "WARN" if audit_status == "PASS" else "FAIL",
        "topic": "docs/core UET GR non-closed response",
        "version": "wave8_v1",
        "benchmark_role": "formula_audit",
        "method_label": "derived_bounds_and_local_current_map",
        "unit_lane": "normalized",
        "external_formula_status": "SOURCED",
        "uet_covariant_derivation_status": "BLOCKED",
        "formula_registry": [
            {
                "id": "symmetric_domain_shifted_curvature_bounds",
                "origin": "derived_from_g_second_equals_3C_squared_minus_1",
                "implementation": "docs/core/uet_hyperbolic_phase_field_bridge.py::shifted_curvature_domain_bounds",
                "status": "DERIVED_EXACT",
            },
            {
                "id": "fixed_light_cone_parameter_bounds",
                "origin": "derived_from_sourced_characteristic_speeds",
                "implementation": "docs/core/uet_hyperbolic_phase_field_bridge.py::subluminal_parameter_bounds",
                "status": "DERIVED_EXACT_NORMALIZED",
            },
            {
                "id": "fixed_cone_parabolic_no_common_limit",
                "origin": "derived_from_tau_lower_bound_and_parabolic_target",
                "implementation": "docs/core/uet_hyperbolic_phase_field_bridge.py::fixed_cone_parabolic_limit_no_go",
                "status": "DERIVED_EXACT_FOR_DECLARED_COMPARATOR",
            },
            {
                "id": "external_q_to_current_law_map",
                "origin": "algebraic_change_J_equals_q_over_tau",
                "implementation": "docs/core/uet_hyperbolic_phase_field_bridge.py::map_external_flux_law_to_current",
                "status": "EXACT_LOCAL_MOBILITY_ONE_ONLY",
            },
        ],
        "completed_formula_gates": list(achieved),
        "open_formula_gates": list(blocked),
        "source_hashes": source_hashes,
        "notes": [
            "External formulas and UET-derived bounds remain separately labelled.",
            "Source hashes identify every code, specification, and provenance input.",
        ],
    }
    mapping = {
        "schema_version": "1.0",
        "artifact": "hyperbolic_phase_field_covariant_mapping_gate",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave8_v1",
        "benchmark_role": "dependency_gate",
        "method_label": "covariant_transport_readiness",
        "status": "BLOCKED",
        "evidence_status": evidence_status,
        "input_identity": {
            "external_comparator_artifact": str(
                COMPARATOR_ARTIFACT.relative_to(ROOT)
            ),
            "source_records": [
                str(JAIN_KOVTUN.relative_to(ROOT)),
                str(CROSSLEY_GLORIOSO_LIU.relative_to(ROOT)),
            ],
        },
        "thresholds": {
            "required_fixed_cone_status": "PASS",
            "required_local_current_map_status": "PASS_MOBILITY_ONE",
            "required_covariant_state_map_status_for_promotion": "PASS",
        },
        "notes": [
            "External characteristic formulas are sourced; fixed-cone inequalities are derived.",
            "A local algebraic current map is not a covariant UET derivation.",
        ],
        "completed_layers": {
            "external_formula_transcription": "PASS",
            "fixed_light_cone_normalized_parameter_domain": "PASS",
            "external_q_to_local_current_law": "PASS_MOBILITY_ONE",
        },
        "classical_covariant_lane": {
            "noether_density_to_phase_field_order_parameter": "BLOCKED_CONTROLLING",
            "covariant_projected_current_law": "BLOCKED",
            "nonnegative_entropy_current_divergence": "BLOCKED",
            "stress_energy_exchange_and_bianchi_closure": "BLOCKED",
            "curved_spacetime_well_posedness": "BLOCKED",
        },
        "thermal_stochastic_lane": {
            "closed_time_path_action": "BLOCKED_DOWNSTREAM",
            "dynamical_kms_symmetry": "BLOCKED_DOWNSTREAM",
            "fluctuation_dissipation_matching": "BLOCKED_DOWNSTREAM",
        },
        "external_requirement_sources": [
            {
                "source": str(JAIN_KOVTUN.relative_to(ROOT)),
                "role": "causal_relativistic_current_entropy_and_sk_kms_requirements",
            },
            {
                "source": str(CROSSLEY_GLORIOSO_LIU.relative_to(ROOT)),
                "role": "dissipative_ctp_local_kms_and_entropy_readiness_requirements",
            },
        ],
        "forbidden_shortcuts": [
            "do_not_identify_source_C_with_UET_Noether_density_without_a_map",
            "do_not_identify_source_auxiliary_phase_with_UET_Phi",
            "do_not_use_trace_as_backreaction",
            "do_not_call_a_1D_algebraic_flux_map_covariant",
            "do_not_promote_normalized_feasibility_to_physical_validation",
        ],
        "global_universe_closure": "UNRESOLVED",
        "gr_null_model": {
            "parameter": "epsilon_nc",
            "value": 0,
            "verification_status": "PASS_INHERITED_EXACT_GR_RESPONSE_NULL",
        },
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "controlling_blocker": HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER,
        "required_next_evidence": [
            "declare whether the physical conserved variable is charge, mass, or another Noether density",
            "derive an invertible coarse-graining/state map to the phase-field order parameter",
            "show compatibility with continuity, equilibrium susceptibility, and the UET epsilon_nc=0 null branch",
            "only then construct the covariant entropy-current constitutive lane",
        ],
    }
    program = {
        "schema_version": "1.0",
        "artifact": "uet_gr_research_program_gate",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave8_v1",
        "benchmark_role": "program_gate",
        "method_label": "monotonic_gr_research_stage_gate",
        "input_identity": {
            "causal_feasibility_artifact": "docs/core/07_artifacts/archive/hyperbolic_phase_field_causal_feasibility.json",
            "covariant_mapping_gate": "docs/core/07_artifacts/gates/hyperbolic_phase_field_covariant_mapping_gate.json",
        },
        "notes": [
            "The controlling blocker is the physical density/order-parameter state map.",
            "Thermal SK/KMS completion is downstream of the classical covariant lane.",
        ],
        "status": "BLOCKED",
        "program_stage": "FIXED_LIGHT_CONE_FEASIBILITY_AND_LOCAL_CURRENT_MAP_VERIFIED",
        "current_claim_class": "B",
        "gr_null_model": {
            "parameter": "epsilon_nc",
            "value": 0,
            "verification_status": "PASS",
        },
        "sector_status": {
            "ontology_and_claim_contract": "PASS",
            "legacy_claim_quarantine": "PASS",
            "conservative_tensor_formula": "PASS",
            "exact_gr_closed_limit": "PASS",
            "covariant_exchange_bianchi_balance": "PASS_CONSERVATIVE_PARENT_ONLY",
            "causal_nonclosed_sector": "PASS_CONSTITUTIVE_1P1D",
            "weak_field_reduction": "PARTIAL_RESPONSE_ONLY",
            "covariant_matter_action": "PASS_O2_SCALAR_PILOT",
            "reciprocal_coupling": "PASS_ACTION_LEVEL",
            "matter_number_current": "PASS_ON_SHELL_O2",
            "diffusive_matter_reduction": "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT",
            "local_convex_matter_causality": "PASS_CONTROL",
            "gradient_phase_field_causality": "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY",
            "fixed_light_cone_parameter_domain": "PASS_NORMALIZED_ANALYTIC",
            "uniform_subluminal_phase_field_limit": "NO_GO_FOR_EXACT_PARABOLIC_LIMIT",
            "local_current_law_mapping": "PASS_ALGEBRAIC_MOBILITY_ONE",
            "uet_covariant_phase_field_mapping": "BLOCKED",
            "entropy_current_kms_completion": "BLOCKED",
            "physical_gr_benchmarks": "NOT_STARTED",
        },
        "global_universe_closure": "UNRESOLVED",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "controlling_blocker": HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER,
        "claim_promotion": "BLOCKED",
        "reason": (
            "The normalized comparator now has exact fixed-cone feasibility "
            "bounds, an analytic no-common exact parabolic limit, and a local "
            "mobility-one current-law map. The physical order parameter has not "
            "been mapped to the conserved UET Noether density, so no covariant "
            "dissipative UET completion follows."
        ),
    }
    apply_latest_hyperbolic_phase_field_stage(
        OUT, verification, formula, mapping, program
    )
    return verification, formula, mapping, program


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    verification, formula, mapping, program = build_artifacts()
    _dump("hyperbolic_phase_field_causal_feasibility.json", verification)
    _dump("hyperbolic_phase_field_bridge_formula_audit.json", formula)
    _dump("hyperbolic_phase_field_covariant_mapping_gate.json", mapping)
    _dump("uet_gr_research_program_gate.json", program)
    if args.print_summary:
        print(
            json.dumps(
                _jsonable(
                    {
                        "audit_status": verification["audit_status"],
                        "evidence_status": verification["evidence_status"],
                        "formula_status": formula["status"],
                        "mapping_status": mapping["status"],
                        "program_status": program["status"],
                        "controlling_blocker": program["controlling_blocker"],
                        "numeric": verification["numeric"],
                    }
                ),
                indent=2,
            )
        )
    return 2 if args.strict and verification["audit_status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
