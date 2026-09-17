"""Generate Wave 9 Noether-density/phase-field state-map artifacts."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
    canonical_existing_path,
)
from docs.core.uet_covariant_diffusion import (  # noqa: E402
    ConservedCurrentBridgeConfig,
    normalize_local_charge_and_current,
)
from docs.core.uet_covariant_matter import (  # noqa: E402
    CovariantMatterConfig,
    matter_noether_current,
)
from docs.core.uet_noether_phase_field_map import (  # noqa: E402
    NOETHER_PHASE_FIELD_MAP_CONTROLLER,
    NoetherPhaseFieldMapConfig,
    denormalize_phase_field_coordinates,
    local_cell_average_1d,
    map_continuity_terms,
    map_external_comparator_state,
    map_normalized_constitutive_scales,
    noether_phase_field_map_contract,
    normalize_noether_hydrodynamic_state,
    symmetric_double_well_equilibrium_contract,
    symmetric_double_well_thermodynamic_map,
)
from docs.scripts.audit.uet_gr_monotonic_stage import (  # noqa: E402
    apply_latest_hyperbolic_phase_field_stage,
)

OUT = CANONICAL_ARTIFACT_ROOT
CORE = canonical_existing_path(ROOT / "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py")
MATTER = canonical_existing_path(ROOT / "docs/core/02_equations/covariant/uet_covariant_matter.py")
DIFFUSION = canonical_existing_path(ROOT / "docs/core/02_equations/covariant/uet_covariant_diffusion.py")
CAUSAL_BRIDGE = canonical_existing_path(
    ROOT / "docs/core/02_equations/matter_space/uet_hyperbolic_phase_field_bridge.py"
)
SPEC = canonical_existing_path(ROOT / "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md")
CAHN_HILLIARD = (
    ROOT
    / "docs/data/external/condensed_matter/phase_transitions/cahn_hilliard_1958"
    / "source_record.json"
)
HOHENBERG_HALPERIN = (
    ROOT
    / "docs/data/external/condensed_matter/phase_transitions/hohenberg_halperin_1977"
    / "source_record.json"
)
HYPERBOLIC_SOURCE = (
    ROOT
    / "docs/data/external/condensed_matter/phase_transitions/hyperbolic_cahn_hilliard"
    / "dhaouadi_dumbser_gavrilyuk_2025/source_record.json"
)
JAIN_KOVTUN = (
    ROOT
    / "docs/data/external/relativistic_transport/jain_kovtun_2024"
    / "source_record.json"
)
FEASIBILITY_ARTIFACT = (
    canonical_artifact_path(
        "hyperbolic_phase_field_causal_feasibility.json",
        "verification",
    )
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    """Return repository-relative paths with one platform-independent spelling."""
    return path.relative_to(ROOT).as_posix()


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _dump(name: str, payload: dict[str, Any]) -> None:
    path = canonical_artifact_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_ready(payload), indent=2) + "\n",
        encoding="utf-8",
    )


def _source_provenance() -> dict[str, Any]:
    expected = {
        CAHN_HILLIARD: {
            "doi": "10.1063/1.1744102",
            "role": "EXTERNAL_PHASE_FIELD_VARIABLE_ROLE_SOURCE_NOT_UET_DERIVATION",
        },
        HOHENBERG_HALPERIN: {
            "doi": "10.1103/RevModPhys.49.435",
            "role": "EXTERNAL_MODEL_B_CLASSIFICATION_SOURCE_NOT_MICROSCOPIC_UET_MAP",
        },
        HYPERBOLIC_SOURCE: {
            "doi": "10.1098/rspa.2024.0606",
            "role": "EXTERNAL_MATHEMATICAL_COMPARATOR_NOT_PHYSICAL_VALIDATION",
        },
        JAIN_KOVTUN: {
            "doi": "10.1007/JHEP01(2024)162",
            "role": "EXTERNAL_COVARIANT_TRANSPORT_READINESS_SOURCE_NOT_UET_DERIVATION",
        },
    }
    records: list[dict[str, Any]] = []
    passed = True
    for path, identity in expected.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        checks = {
            "doi_match": payload.get("doi") == identity["doi"],
            "benchmark_role_match": payload.get("benchmark_role")
            == identity["role"],
            "local_path_absent": payload.get("local_path") is None,
            "formula_locator_present": bool(payload.get("formula_locators")),
            "claim_boundary_present": bool(payload.get("claim_boundary")),
        }
        passed = passed and all(checks.values())
        records.append(
            {
                "path": _rel(path),
                "doi": payload["doi"],
                "title": payload["title"],
                "benchmark_role": payload["benchmark_role"],
                "local_copy_status": payload["local_copy_status"],
                "checks": checks,
            }
        )
    return {"status": "PASS" if passed else "FAIL", "records": records}


def _polar_state(
    amplitude: float,
    phase: float,
    phase_gradient_covariant: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    fields = np.array(
        [amplitude * np.cos(phase), amplitude * np.sin(phase)], dtype=float
    )
    gradients = np.vstack(
        [
            -amplitude * np.sin(phase) * phase_gradient_covariant,
            amplitude * np.cos(phase) * phase_gradient_covariant,
        ]
    )
    return fields, gradients


def _numeric_checks() -> dict[str, Any]:
    rng = np.random.default_rng(913201)
    roundtrip_errors: list[float] = []
    continuity_errors: list[float] = []
    legacy_errors: list[float] = []
    external_errors: list[float] = []
    derivative_errors: list[float] = []

    for _ in range(64):
        config = NoetherPhaseFieldMapConfig(
            density_reference=float(rng.uniform(-3.0, 3.0)),
            density_scale=float(rng.uniform(0.2, 4.0)),
            length_scale=float(rng.uniform(0.2, 3.0)),
            time_scale=float(rng.uniform(0.2, 3.0)),
            chemical_potential_scale=float(rng.uniform(0.2, 4.0)),
        )
        density = rng.normal(size=48)
        current = rng.normal(size=48)
        coordinates = normalize_noether_hydrodynamic_state(
            density, current, config
        )
        roundtrip_errors.extend(
            [
                coordinates.density_roundtrip_error,
                coordinates.current_roundtrip_error,
            ]
        )

        density_rate = rng.normal(size=48)
        current_divergence = rng.normal(size=48)
        continuity = map_continuity_terms(
            density_rate, current_divergence, config
        )
        continuity_errors.append(continuity.max_abs_scaling_error)

        old_config = ConservedCurrentBridgeConfig(
            density_scale=config.density_scale,
            length_scale=config.length_scale,
            time_scale=config.time_scale,
        )
        old_C, old_J = normalize_local_charge_and_current(
            density, current, old_config
        )
        zero_reference = NoetherPhaseFieldMapConfig(
            density_scale=config.density_scale,
            length_scale=config.length_scale,
            time_scale=config.time_scale,
            chemical_potential_scale=config.chemical_potential_scale,
        )
        current_map = normalize_noether_hydrodynamic_state(
            density, current, zero_reference
        )
        legacy_errors.append(
            float(
                max(
                    np.max(np.abs(current_map.C - old_C)),
                    np.max(np.abs(current_map.normalized_current - old_J)),
                )
            )
        )

        C = rng.uniform(-1.4, 1.4, size=48)
        q = rng.normal(size=48)
        tau = float(rng.uniform(0.05, 2.0))
        external = map_external_comparator_state(C, q, tau, config)
        external_errors.append(
            max(
                external.density_roundtrip_error,
                external.current_roundtrip_error,
            )
        )

        density_samples = config.density_reference + config.density_scale * C
        step = 1e-6 * config.density_scale
        plus_C = (
            density_samples + step - config.density_reference
        ) / config.density_scale
        minus_C = (
            density_samples - step - config.density_reference
        ) / config.density_scale
        plus = symmetric_double_well_thermodynamic_map(plus_C, config)
        minus = symmetric_double_well_thermodynamic_map(minus_C, config)
        finite_difference = (
            plus.natural_free_energy_density
            - minus.natural_free_energy_density
        ) / (2.0 * step)
        exact = symmetric_double_well_thermodynamic_map(C, config)
        derivative_errors.append(
            float(
                np.max(
                    np.abs(
                        finite_difference - exact.natural_chemical_potential
                    )
                )
            )
        )

    inverse_metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    matter = CovariantMatterConfig(matter_kinetic=1.7)
    phase_gradient = np.array([-0.9, 0.25, -0.1, 0.05])
    fields, gradients = _polar_state(1.4, 0.31, phase_gradient)
    current = matter_noether_current(
        inverse_metric, fields, gradients, matter
    )
    polar_expected = (
        matter.matter_kinetic
        * 1.4**2
        * (inverse_metric @ phase_gradient)
    )
    polar_identity_error = float(np.max(np.abs(current - polar_expected)))

    fields_a, gradients_a = _polar_state(
        1.0, 0.2, np.array([-2.0, 0.4, 0.0, 0.0])
    )
    fields_b, gradients_b = _polar_state(
        np.sqrt(2.0), 1.1, np.array([-1.0, 0.2, 0.0, 0.0])
    )
    current_a = matter_noether_current(
        inverse_metric, fields_a, gradients_a, matter
    )
    current_b = matter_noether_current(
        inverse_metric, fields_b, gradients_b, matter
    )
    microscopic_same_current_error = float(
        np.max(np.abs(current_a - current_b))
    )
    microscopic_state_difference = float(
        np.max(np.abs(fields_a - fields_b))
    )

    micro_a = np.array([0.0, 2.0, 1.0, 3.0, -1.0, 1.0, 2.0, 4.0])
    micro_b = np.array([1.0, 1.0, 0.0, 4.0, 0.0, 0.0, 3.0, 3.0])
    coarse_a = local_cell_average_1d(micro_a, 4)
    coarse_b = local_cell_average_1d(micro_b, 4)
    coarse_same_average_error = float(np.max(np.abs(coarse_a - coarse_b)))
    coarse_microstate_difference = float(np.max(np.abs(micro_a - micro_b)))

    local_C = np.linspace(-2.0, 2.0, 1001)
    local_map = symmetric_double_well_thermodynamic_map(
        local_C, NoetherPhaseFieldMapConfig()
    )
    local_coefficient_error = float(
        np.max(
            np.abs(
                local_map.normalized_chemical_potential
                - (-local_C + np.power(local_C, 3))
            )
        )
    )
    equilibrium = symmetric_double_well_equilibrium_contract(
        NoetherPhaseFieldMapConfig(
            density_reference=2.0,
            density_scale=0.75,
            chemical_potential_scale=1.4,
        )
    )
    scales = map_normalized_constitutive_scales(
        0.4, 0.2, NoetherPhaseFieldMapConfig(
            density_scale=1.3,
            length_scale=0.8,
            time_scale=1.1,
            chemical_potential_scale=1.7,
        )
    )

    negative_controls: dict[str, bool] = {}
    controls = {
        "zero_density_scale": lambda: NoetherPhaseFieldMapConfig(
            density_scale=0.0
        ),
        "mass_shortcut": lambda: NoetherPhaseFieldMapConfig(
            charge_convention="mass_density"
        ),
        "particle_number_shortcut": lambda: NoetherPhaseFieldMapConfig(
            charge_convention="particle_number_density"
        ),
        "nonlocal_kernel_shortcut": lambda: NoetherPhaseFieldMapConfig(
            coarse_graining="unspecified_kernel"
        ),
        "nonpositive_external_tau": lambda: map_external_comparator_state(
            np.ones(4), np.ones(4), 0.0, NoetherPhaseFieldMapConfig()
        ),
        "nondivisible_cell_average": lambda: local_cell_average_1d(
            np.ones(7), 3
        ),
    }
    for name, function in controls.items():
        try:
            function()
        except (ValueError, NotImplementedError):
            negative_controls[name] = True
        else:
            negative_controls[name] = False

    trace_absent = all(
        "trace" not in inspect.signature(function).parameters
        and "space_response" not in inspect.signature(function).parameters
        for function in (
            normalize_noether_hydrodynamic_state,
            denormalize_phase_field_coordinates,
            map_continuity_terms,
            map_external_comparator_state,
            symmetric_double_well_thermodynamic_map,
        )
    )

    return {
        "random_cases": 64,
        "maximum_affine_roundtrip_error": max(roundtrip_errors),
        "maximum_continuity_scaling_error": max(continuity_errors),
        "maximum_existing_bridge_compatibility_error": max(legacy_errors),
        "maximum_external_coordinate_roundtrip_error": max(external_errors),
        "maximum_free_energy_derivative_error": max(derivative_errors),
        "polar_noether_identity_error": polar_identity_error,
        "microscopic_same_current_error": microscopic_same_current_error,
        "microscopic_state_difference": microscopic_state_difference,
        "coarse_same_average_error": coarse_same_average_error,
        "coarse_microstate_difference": coarse_microstate_difference,
        "local_double_well_coefficient_error": local_coefficient_error,
        "equilibrium_contract": equilibrium,
        "constitutive_scale_map": scales.__dict__,
        "negative_controls": negative_controls,
        "all_negative_controls_rejected": all(negative_controls.values()),
        "trace_and_space_response_absent": trace_absent,
    }


def build_artifacts() -> tuple[dict[str, Any], ...]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    provenance = _source_provenance()
    numeric = _numeric_checks()
    contract = noether_phase_field_map_contract()
    thresholds = {
        "maximum_affine_roundtrip_error": 1e-12,
        "maximum_continuity_scaling_error": 1e-12,
        "maximum_existing_bridge_compatibility_error": 1e-12,
        "maximum_external_coordinate_roundtrip_error": 1e-12,
        "maximum_free_energy_derivative_error": 1e-8,
        "polar_noether_identity_error": 1e-12,
        "microscopic_same_current_error": 1e-12,
        "minimum_microscopic_state_difference": 1e-3,
        "coarse_same_average_error": 1e-12,
        "minimum_coarse_microstate_difference": 1e-3,
        "local_double_well_coefficient_error": 1e-12,
        "all_negative_controls_rejected": True,
    }
    achieved = {
        "source_provenance": "PASS"
        if provenance["status"] == "PASS"
        else "FAIL",
        "signed_O2_charge_variable_declared": "PASS",
        "affine_coarse_density_coordinate_bijection": "PASS"
        if numeric["maximum_affine_roundtrip_error"]
        <= thresholds["maximum_affine_roundtrip_error"]
        else "FAIL",
        "continuity_and_current_scale_map": "PASS"
        if numeric["maximum_continuity_scaling_error"]
        <= thresholds["maximum_continuity_scaling_error"]
        and numeric["maximum_existing_bridge_compatibility_error"]
        <= thresholds["maximum_existing_bridge_compatibility_error"]
        else "FAIL",
        "external_C_coordinate_adapter": "PASS"
        if numeric["maximum_external_coordinate_roundtrip_error"]
        <= thresholds["maximum_external_coordinate_roundtrip_error"]
        else "FAIL",
        "double_well_conjugacy_and_local_coefficients": "PASS"
        if numeric["maximum_free_energy_derivative_error"]
        <= thresholds["maximum_free_energy_derivative_error"]
        and numeric["local_double_well_coefficient_error"]
        <= thresholds["local_double_well_coefficient_error"]
        else "FAIL",
        "O2_polar_current_identity": "PASS"
        if numeric["polar_noether_identity_error"]
        <= thresholds["polar_noether_identity_error"]
        else "FAIL",
        "microscopic_noninvertibility_counterexample": "PASS"
        if numeric["microscopic_same_current_error"]
        <= thresholds["microscopic_same_current_error"]
        and numeric["microscopic_state_difference"]
        >= thresholds["minimum_microscopic_state_difference"]
        else "FAIL",
        "coarse_graining_noninvertibility_counterexample": "PASS"
        if numeric["coarse_same_average_error"]
        <= thresholds["coarse_same_average_error"]
        and numeric["coarse_microstate_difference"]
        >= thresholds["minimum_coarse_microstate_difference"]
        else "FAIL",
        "negative_and_ontology_controls": "PASS"
        if numeric["all_negative_controls_rejected"]
        and numeric["trace_and_space_response_absent"]
        else "FAIL",
    }
    audit_status = "PASS" if set(achieved.values()) == {"PASS"} else "FAIL"
    evidence_status = (
        "PARTIAL_HYDRODYNAMIC_STATE_COORDINATE_MAP"
        if audit_status == "PASS"
        else "BLOCKED"
    )
    blocked = {
        "equation_of_state_from_covariant_O2_action": "BLOCKED_CONTROLLING",
        "covariant_coarse_graining_kernel": "BLOCKED",
        "susceptibility_and_transport_coefficient_matching": "BLOCKED",
        "covariant_projected_current_law": "BLOCKED",
        "entropy_current_and_dissipative_Bianchi_closure": "BLOCKED",
        "curved_3p1_well_posed_solver": "BLOCKED",
        "system_specific_SI_map": "BLOCKED",
        "external_physical_validation": "BLOCKED",
    }
    source_hashes = {
        _rel(path): _sha(path)
        for path in (
            CORE,
            MATTER,
            DIFFUSION,
            CAUSAL_BRIDGE,
            SPEC,
            CAHN_HILLIARD,
            HOHENBERG_HALPERIN,
            HYPERBOLIC_SOURCE,
            JAIN_KOVTUN,
            FEASIBILITY_ARTIFACT,
        )
    }
    input_identity = {
        "upstream_feasibility_artifact": _rel(FEASIBILITY_ARTIFACT),
        "source_records": [
            _rel(CAHN_HILLIARD),
            _rel(HOHENBERG_HALPERIN),
            _rel(HYPERBOLIC_SOURCE),
            _rel(JAIN_KOVTUN),
        ],
    }

    verification = {
        "schema_version": "1.0",
        "artifact": "noether_phase_field_state_map_verification",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave9_v1",
        "benchmark_role": "analytic_state_map_gate",
        "method_label": "factorized_noether_to_hydrodynamic_phase_coordinate_map",
        "audit_status": audit_status,
        "evidence_status": evidence_status,
        "claim_class": "B",
        "claim": (
            "exact fixed-scale affine map between coarse O2 Noether charge "
            "density/current and normalized phase coordinates, with explicit "
            "counterexamples to microscopic and coarse-graining invertibility"
        ),
        "source_provenance": provenance,
        "numeric": numeric,
        "achieved_gates": achieved,
        "blocked_gates": blocked,
        "thresholds": thresholds,
        "run_contract": {
            "seed": 913201,
            "random_cases": 64,
            "unit_lane": "natural_to_normalized",
            "charge_convention": "signed_global_O2_noether_charge",
            "coarse_graining": "declared_local_cell_average",
            "parameter_fitting": False,
            "trace_backreaction": False,
            "external_auxiliary_phase_is_UET_Phi": False,
            "microscopic_inverse_claim": False,
            "physical_validation": False,
        },
        "source_hashes": source_hashes,
        "input_identity": input_identity,
        "allowed_language": [
            "hydrodynamic state-coordinate map",
            "signed O2 Noether charge density",
            "exact affine coarse-density coordinate change",
            "external C compatible only after an explicit charge-coordinate declaration",
            "microscopic reconstruction is many-to-one",
        ],
        "blocked_language": [
            "scalar amplitude is the phase-field density",
            "the external material concentration is derived as UET charge",
            "the double-well equation of state is derived from the O2 action",
            "the external auxiliary phase is UET Phi or information",
            "Topic 0.11 or 0.19 is validated",
        ],
        "notes": [
            "Only the final coarse-density/current to C/J coordinate layer is invertible.",
            "The constitutive equation of state and transport remain the controlling physical map blocker.",
        ],
        "next_controller": NOETHER_PHASE_FIELD_MAP_CONTROLLER,
    }
    formula = {
        "schema_version": "1.0",
        "artifact": "noether_phase_field_map_formula_audit",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave9_v1",
        "benchmark_role": "formula_audit",
        "method_label": "affine_state_coordinate_and_conjugate_scale_audit",
        "status": "WARN" if audit_status == "PASS" else "FAIL",
        "unit_lane": "natural_to_normalized",
        "formula_registry": [
            {
                "id": "frame_projected_charge_density",
                "formula": "n=-u_mu*N^mu",
                "status": "KINEMATIC_EXISTING",
            },
            {
                "id": "affine_phase_coordinate",
                "formula": "C=(n_bar-n_ref)/n_scale",
                "status": "DEFINITION_EXACT_FIXED_SCALES",
            },
            {
                "id": "normalized_current_coordinate",
                "formula": "J=j/(n_scale*L/T)",
                "status": "DEFINITION_EXACT_FIXED_SCALES",
            },
            {
                "id": "continuity_residual_scaling",
                "formula": "R_hat=(T/n_scale)*R_natural",
                "status": "DERIVED_EXACT",
            },
            {
                "id": "O2_polar_current",
                "formula": "N^mu=Z*A^2*partial^mu(theta)",
                "status": "DERIVED_EXACT_FROM_IMPLEMENTED_CURRENT",
            },
            {
                "id": "symmetric_double_well_conjugacy",
                "formula": "f=n_scale*mu_scale*(C^2-1)^2/4; df/dn=mu_scale*(C^3-C)",
                "status": "DERIVED_EXACT_CONSTITUTIVE",
            },
            {
                "id": "normalized_constitutive_scales",
                "formula": "tau_nat=T*tau_hat; M_nat=n_scale*L^2/(T*mu_scale)",
                "status": "DIMENSIONAL_COORDINATE_MAP_NOT_MICROSCOPIC_DERIVATION",
            },
        ],
        "completed_formula_gates": list(achieved),
        "open_formula_gates": list(blocked),
        "source_hashes": source_hashes,
        "notes": [
            "The affine coordinate map is exact after coarse graining; the full microscopic map is intentionally not invertible.",
            "The double well is a constitutive free energy, not an action-derived O2 equation of state.",
        ],
    }
    dependency = {
        "schema_version": "1.0",
        "artifact": "noether_phase_field_dependency_gate",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave9_v1",
        "benchmark_role": "dependency_gate",
        "method_label": "hydrodynamic_quotient_readiness",
        "status": "BLOCKED",
        "evidence_status": evidence_status,
        "input_identity": input_identity,
        "thresholds": {
            "required_state_coordinate_map": "PASS",
            "required_equation_of_state_derivation_for_promotion": "PASS",
            "required_covariant_transport_for_promotion": "PASS",
        },
        "completed_layers": {
            "physical_conserved_variable_declaration": "PASS_SIGNED_O2_CHARGE",
            "coarse_density_to_phase_coordinate": "PASS_AFFINE_FIXED_SCALE",
            "continuity_current_scaling": "PASS",
            "external_C_coordinate_adapter": "PASS_DECLARED_ONLY",
            "microscopic_inverse_requirement": "REJECTED_AS_CATEGORY_ERROR",
        },
        "blocked_layers": blocked,
        "forbidden_shortcuts": [
            "do_not_invert_C_to_microscopic_O2_fields",
            "do_not_identify_scalar_amplitude_with_charge_density",
            "do_not_identify_external_varphi_with_UET_Phi",
            "do_not_import_trace_as_state_or_feedback",
            "do_not_call_coordinate_compatibility_an_equation_of_state_derivation",
        ],
        "global_universe_closure": "UNRESOLVED",
        "gr_null_model": {
            "parameter": "epsilon_nc",
            "value": 0,
            "verification_status": "PASS_INHERITED_EXACT_GR_RESPONSE_NULL",
        },
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "controlling_blocker": NOETHER_PHASE_FIELD_MAP_CONTROLLER,
        "required_next_evidence": [
            "derive or calibrate the charge-density equation of state independently of the test set",
            "map equilibrium susceptibility and transport coefficients to the covariant matter theory",
            "specify a covariant coarse-graining or hydrodynamic matching prescription",
            "then construct entropy-current and dissipative-Bianchi closure",
        ],
        "notes": [
            "Hydrodynamic quotient coordinates can be bijective even though the microscopic map is many-to-one.",
            "No topic or global-universe claim is promoted by this coordinate result.",
        ],
    }
    program = {
        "schema_version": "1.0",
        "artifact": "uet_gr_research_program_gate",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave9_v1",
        "benchmark_role": "program_gate",
        "method_label": "monotonic_gr_research_stage_gate",
        "input_identity": {
            "state_map_artifact": "docs/core/07_artifacts/verification/noether_phase_field_state_map_verification.json",
            "state_map_dependency_gate": "docs/core/07_artifacts/gates/noether_phase_field_dependency_gate.json",
        },
        "notes": [
            "The hydrodynamic coordinate map is verified while microscopic reconstruction is disproved by counterexample.",
            "The controlling blocker is now equation-of-state and covariant transport matching.",
        ],
        "status": "BLOCKED",
        "program_stage": "NOETHER_PHASE_FIELD_STATE_COORDINATE_MAP_VERIFIED",
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
            "signed_O2_noether_current": "PASS_ON_SHELL",
            "diffusive_matter_reduction": "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT",
            "local_convex_matter_causality": "PASS_CONTROL",
            "gradient_phase_field_causality": "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY",
            "fixed_light_cone_parameter_domain": "PASS_NORMALIZED_ANALYTIC",
            "uniform_subluminal_phase_field_limit": "NO_GO_FOR_EXACT_PARABOLIC_LIMIT",
            "local_current_law_mapping": "PASS_ALGEBRAIC_MOBILITY_ONE",
            "hydrodynamic_state_coordinate_map": "PASS_AFFINE_FIXED_SCALE",
            "microscopic_state_reconstruction": "NO_GO_MANY_TO_ONE",
            "external_C_noether_coordinate_map": "PASS_DECLARED_SIGNED_CHARGE_ONLY",
            "equation_of_state_from_matter_action": "BLOCKED",
            "covariant_coarse_graining": "BLOCKED",
            "covariant_transport_matching": "BLOCKED",
            "entropy_current_kms_completion": "BLOCKED",
            "physical_gr_benchmarks": "NOT_STARTED",
        },
        "global_universe_closure": "UNRESOLVED",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "controlling_blocker": NOETHER_PHASE_FIELD_MAP_CONTROLLER,
        "claim_promotion": "BLOCKED",
        "reason": (
            "The coarse O2 Noether density/current and normalized C/J now have "
            "an exact fixed-scale coordinate map, while microscopic inversion "
            "is explicitly many-to-one. The charge-density equation of state, "
            "coarse-graining prescription, and covariant dissipative transport "
            "are not derived."
        ),
    }
    apply_latest_hyperbolic_phase_field_stage(OUT, program)
    return verification, formula, dependency, program


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    verification, formula, dependency, program = build_artifacts()
    _dump("noether_phase_field_state_map_verification.json", verification)
    _dump("noether_phase_field_map_formula_audit.json", formula)
    _dump("noether_phase_field_dependency_gate.json", dependency)
    _dump("uet_gr_research_program_gate.json", program)
    if args.print_summary:
        print(
            json.dumps(
                {
                    "audit_status": verification["audit_status"],
                    "evidence_status": verification["evidence_status"],
                    "formula_status": formula["status"],
                    "dependency_status": dependency["status"],
                    "program_status": program["status"],
                    "next_controller": program["controlling_blocker"],
                },
                indent=2,
            )
        )
    if args.strict and verification["audit_status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
