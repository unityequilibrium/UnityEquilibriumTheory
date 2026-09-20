"""Audit the external first-order hyperbolic Cahn-Hilliard comparator."""

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
import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
    canonical_existing_path,
)
from docs.core.uet_hyperbolic_phase_field import (  # noqa: E402
    HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV,
    HYPERBOLIC_PHASE_FIELD_SOURCE_DOI,
    HyperbolicPhaseFieldConfig,
    HyperbolicPhaseFieldState,
    analytic_characteristic_speeds,
    compare_augmented_to_cahn_hilliard_chemical,
    double_well_curvature,
    double_well_derivative,
    double_well_potential,
    gradient_constraint_rate_residual,
    hyperbolic_phase_field_contract,
    hyperbolic_phase_field_energy,
    hyperbolic_phase_field_energy_balance,
    hyperbolic_phase_field_rhs,
    hyperbolicity_diagnostics,
    paper_asymptotic_scaling_diagnostics,
    periodic_central_derivative,
    principal_matrix,
)
from docs.core.uet_spatial import integral_1d  # noqa: E402
from docs.scripts.audit.uet_gr_monotonic_stage import (  # noqa: E402
    apply_latest_hyperbolic_phase_field_stage,
)

CORE = canonical_existing_path(ROOT / "docs/core/02_equations/matter_space/uet_hyperbolic_phase_field.py")
SPEC = canonical_existing_path(ROOT / "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md")
SOURCE_RECORD = (
    ROOT
    / "docs/data/external/condensed_matter/phase_transitions"
    / "hyperbolic_cahn_hilliard/dhaouadi_dumbser_gavrilyuk_2025"
    / "source_record.json"
)
DIFFUSION = ROOT / "docs/core/07_artifacts/verification/covariant_diffusive_current_verification.json"
OUT = CANONICAL_ARTIFACT_ROOT


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(name: str, payload: dict[str, Any]) -> None:
    path = canonical_artifact_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


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


def _symbolic() -> dict[str, Any]:
    lam = sp.symbols("lambda", real=True)
    alpha, tau, gamma, beta = sp.symbols(
        "alpha tau gamma beta", positive=True
    )
    curvature = sp.symbols("g_second", real=True)
    matrix = sp.Matrix(
        [
            [0, 1 / tau, 0, 0, 0],
            [curvature + alpha, 0, 0, 0, -alpha],
            [0, 0, 0, -gamma, 0],
            [0, 0, -1 / beta, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    characteristic = sp.factor((lam * sp.eye(5) - matrix).det())
    expected = sp.factor(
        lam
        * (lam**2 - (alpha + curvature) / tau)
        * (lam**2 - gamma / beta)
    )
    q, delta, w = sp.symbols("q delta w", real=True)
    source_energy = sp.simplify(
        (q / tau) * (-q / tau)
        + (w / beta) * (alpha * delta)
        + (-alpha * delta) * (w / beta)
    )
    dissipation = (q / tau) ** 2
    return {
        "characteristic_polynomial": str(characteristic),
        "expected_characteristic_polynomial": str(expected),
        "characteristic_factorization_exact": sp.simplify(
            characteristic - expected
        )
        == 0,
        "source_energy_terms": str(source_energy),
        "energy_plus_dissipation_exact": sp.simplify(
            source_energy + dissipation
        )
        == 0,
        "periodic_derivative_requirement": "D_transpose_equals_minus_D",
        "strict_double_well_hyperbolicity": "alpha > 1",
        "fixed_parameter_speeds": [
            "sqrt((alpha+g_second)/tau)",
            "sqrt(gamma/beta)",
        ],
        "paper_asymptotic_scaling": "alpha=gamma^-1,tau=gamma^2,beta=gamma^2",
        "asymptotic_speed_behavior": ["O(gamma^-3/2)", "O(gamma^-1/2)"],
    }


def _state(seed: int = 719061, n: int = 128) -> HyperbolicPhaseFieldState:
    rng = np.random.default_rng(seed)
    return HyperbolicPhaseFieldState(
        C=rng.normal(scale=0.12, size=n),
        flux_impulse=rng.normal(scale=0.025, size=n),
        auxiliary_rate=rng.normal(scale=0.02, size=n),
        gradient_proxy=rng.normal(scale=0.06, size=n),
        auxiliary_phase=rng.normal(scale=0.1, size=n),
    )


def _principal_cone_control() -> dict[str, float]:
    """Propagate the constant principal system along exact grid characteristics."""

    n_cells = 401
    center = n_cells // 2
    steps = 24
    dx = 0.1
    config = HyperbolicPhaseFieldConfig(
        alpha_penalty=1.25,
        tau_flux=0.25,
        gamma_gradient=0.25,
        beta_wave=0.25,
    )
    matrix = principal_matrix(0.0, config)
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    inverse = np.linalg.inv(eigenvectors)
    state = np.zeros((5, n_cells), dtype=complex)
    state[0, center] = 1.0
    characteristic = inverse @ state
    dt = dx
    for _ in range(steps):
        for index, speed in enumerate(eigenvalues.real):
            shift = int(np.rint(speed * dt / dx))
            if abs(speed * dt / dx - shift) > 1e-12:
                raise RuntimeError("cone control requires integer cell characteristics")
            characteristic[index] = np.roll(characteristic[index], shift)
    evolved = np.asarray((eigenvectors @ characteristic).real, dtype=float)
    amplitude = np.max(np.abs(evolved), axis=0)
    peak = max(float(np.max(amplitude)), np.finfo(float).tiny)
    offsets = np.minimum(
        (np.arange(n_cells) - center) % n_cells,
        (center - np.arange(n_cells)) % n_cells,
    )
    outside = offsets > steps
    leakage = float(np.max(amplitude[outside])) / peak
    active = offsets[amplitude > peak * 1e-12]
    reached = int(np.max(active))
    observed_speed = reached * dx / (steps * dt)
    expected_speed = float(np.max(np.abs(eigenvalues.real)))
    return {
        "expected_max_characteristic_speed": expected_speed,
        "observed_front_speed": observed_speed,
        "arrival_speed_relative_error": abs(observed_speed - expected_speed)
        / expected_speed,
        "outside_cone_leakage_ratio": leakage,
        "eigenvector_condition_number": float(np.linalg.cond(eigenvectors)),
    }


def _source_provenance() -> dict[str, Any]:
    record = json.loads(SOURCE_RECORD.read_text(encoding="utf-8"))
    required = {
        "title",
        "authors",
        "doi",
        "doi_url",
        "arxiv_id",
        "arxiv_url",
        "license_or_terms",
        "original_file_name",
        "local_copy_status",
        "preprocessing_note",
        "formula_locators",
        "unit_system",
        "benchmark_role",
        "topics_used",
        "upstream_source_archive_sha256",
    }
    missing = sorted(required - set(record))
    locator_ids = {
        item.get("id") for item in record.get("formula_locators", [])
    }
    required_locators = {
        "first_order_hyperbolic_system",
        "augmented_lyapunov_functional",
        "characteristic_speeds",
        "formal_cahn_hilliard_scaling",
    }
    archive_hash = str(record.get("upstream_source_archive_sha256", ""))
    return {
        "status": "PASS"
        if not missing
        and record.get("doi") == HYPERBOLIC_PHASE_FIELD_SOURCE_DOI
        and record.get("arxiv_id") == HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV
        and record.get("local_path") is None
        and record.get("local_copy_status")
        == "TEMPORARY_INSPECTION_ONLY_NOT_REDISTRIBUTED"
        and len(archive_hash) == 64
        and required_locators <= locator_ids
        else "FAIL",
        "missing_required_fields": missing,
        "required_formula_locators_present": sorted(
            required_locators & locator_ids
        ),
        "upstream_source_archive_sha256": archive_hash,
        "raw_source_committed": False,
        "publisher_pdf_parsed": False,
        "formula_source_version": "arXiv_2408.03862v1",
        "peer_reviewed_identity": "doi_10.1098/rspa.2024.0606",
        "benchmark_role": record.get("benchmark_role"),
    }


def _numeric() -> dict[str, Any]:
    state = _state()
    dx = 0.1
    config = HyperbolicPhaseFieldConfig(
        alpha_penalty=1.4,
        beta_wave=0.7,
        tau_flux=1.2,
        gamma_gradient=0.2,
    )
    rates = hyperbolic_phase_field_rhs(state, dx, config)
    mass_residual = abs(integral_1d(rates.C, dx))
    energy = hyperbolic_phase_field_energy_balance(state, dx, config)
    constraint_rate = float(
        np.max(np.abs(gradient_constraint_rate_residual(state, dx, config)))
    )

    rng = np.random.default_rng(719062)
    direction = rng.normal(size=state.C.size)
    step = 1e-6
    potential_derivative = (
        integral_1d(double_well_potential(state.C + step * direction), dx)
        - integral_1d(double_well_potential(state.C - step * direction), dx)
    ) / (2.0 * step)
    potential_expected = integral_1d(
        double_well_derivative(state.C) * direction, dx
    )

    energy_step = 1e-7

    def displaced(sign: float) -> HyperbolicPhaseFieldState:
        return HyperbolicPhaseFieldState(
            state.C + sign * energy_step * rates.C,
            state.flux_impulse + sign * energy_step * rates.flux_impulse,
            state.auxiliary_rate + sign * energy_step * rates.auxiliary_rate,
            state.gradient_proxy + sign * energy_step * rates.gradient_proxy,
            state.auxiliary_phase + sign * energy_step * rates.auxiliary_phase,
        )

    energy_fd = (
        hyperbolic_phase_field_energy(displaced(1.0), dx, config)
        - hyperbolic_phase_field_energy(displaced(-1.0), dx, config)
    ) / (2.0 * energy_step)

    backgrounds = (-0.8, -0.2, 0.0, 0.35, 0.9)
    eigen_errors = []
    for background in backgrounds:
        numeric = np.sort(np.linalg.eigvals(principal_matrix(background, config)).real)
        analytic = np.sort(analytic_characteristic_speeds(background, config))
        eigen_errors.append(float(np.max(np.abs(numeric - analytic))))

    causal_config = HyperbolicPhaseFieldConfig(
        alpha_penalty=1.2,
        tau_flux=8.0,
        gamma_gradient=0.1,
        beta_wave=1.0,
    )
    fixed_parameter = hyperbolicity_diagnostics(
        np.linspace(-1.0, 1.0, 257), causal_config
    )
    critical = hyperbolicity_diagnostics(
        np.zeros(64), HyperbolicPhaseFieldConfig(alpha_penalty=1.0)
    )
    superluminal = hyperbolicity_diagnostics(
        np.zeros(64),
        HyperbolicPhaseFieldConfig(alpha_penalty=2.0, tau_flux=1e-3),
    )

    x = np.linspace(0.0, 2.0 * np.pi, 256, endpoint=False)
    density = 0.2 * np.cos(2.0 * x) + 0.04 * np.sin(5.0 * x)
    spacing = float(x[1] - x[0])
    alphas = np.array([8.0, 32.0, 128.0, 512.0])
    convergence_errors = []
    quasistatic_residuals = []
    for alpha in alphas:
        comparison = compare_augmented_to_cahn_hilliard_chemical(
            density,
            spacing,
            HyperbolicPhaseFieldConfig(
                alpha_penalty=float(alpha),
                gamma_gradient=0.05,
                tau_flux=float(alpha + 1.0),
            ),
        )
        convergence_errors.append(comparison["relative_l2_difference"])
        quasistatic_residuals.append(
            comparison["quasistatic_constraint_max_abs"]
        )
    observed_order = float(
        -np.polyfit(np.log(alphas), np.log(convergence_errors), 1)[0]
    )
    singular = paper_asymptotic_scaling_diagnostics(
        np.array([0.2, 0.1, 0.05, 0.025])
    )
    return _json_ready(
        {
            "mass_conservation_abs_residual": mass_residual,
            "energy_identity_abs_residual": abs(energy["closure_residual"]),
            "energy_directional_derivative_abs_residual": abs(
                energy_fd - energy["energy_rate"]
            ),
            "gradient_constraint_rate_max_abs_residual": constraint_rate,
            "potential_derivative_abs_residual": abs(
                potential_derivative - potential_expected
            ),
            "principal_eigenvalue_max_abs_residual": max(eigen_errors),
            "fixed_parameter_hyperbolicity": fixed_parameter,
            "critical_alpha_control": critical,
            "superluminal_parameter_control": superluminal,
            "principal_cone_control": _principal_cone_control(),
            "chemical_limit_alpha_values": alphas,
            "chemical_limit_relative_l2_errors": convergence_errors,
            "chemical_limit_observed_order": observed_order,
            "quasistatic_constraint_max_abs_residual": max(
                quasistatic_residuals
            ),
            "paper_asymptotic_scaling": singular,
        }
    )


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    symbolic = _symbolic()
    numeric = _numeric()
    provenance = _source_provenance()
    contract = hyperbolic_phase_field_contract()
    diffusion = json.loads(DIFFUSION.read_text(encoding="utf-8"))
    signature = inspect.signature(hyperbolic_phase_field_rhs)
    fixed = numeric["fixed_parameter_hyperbolicity"]
    critical = numeric["critical_alpha_control"]
    superluminal = numeric["superluminal_parameter_control"]
    cone = numeric["principal_cone_control"]
    singular = numeric["paper_asymptotic_scaling"]
    achieved_gates = {
        "primary_source_provenance": provenance["status"],
        "formula_transcription_symbolic_closure": "PASS"
        if symbolic["characteristic_factorization_exact"]
        and symbolic["energy_plus_dissipation_exact"]
        else "FAIL",
        "double_well_functional_derivative": "PASS"
        if numeric["potential_derivative_abs_residual"] <= 1e-8
        else "FAIL",
        "periodic_mass_conservation": "PASS"
        if numeric["mass_conservation_abs_residual"] <= 1e-12
        else "FAIL",
        "periodic_lyapunov_identity": "PASS"
        if numeric["energy_identity_abs_residual"] <= 1e-11
        and numeric["energy_directional_derivative_abs_residual"] <= 1e-7
        else "FAIL",
        "gradient_constraint_involution": "PASS"
        if numeric["gradient_constraint_rate_max_abs_residual"] <= 1e-12
        else "FAIL",
        "analytic_characteristic_speeds": "PASS"
        if numeric["principal_eigenvalue_max_abs_residual"] <= 1e-12
        else "FAIL",
        "fixed_parameter_hyperbolic_subluminal_control": "PASS"
        if fixed["status"]
        == "PASS_FIXED_PARAMETER_HYPERBOLIC_SUBLUMINAL_CONTROL"
        and cone["outside_cone_leakage_ratio"] <= 1e-12
        and cone["arrival_speed_relative_error"] <= 0.05
        else "FAIL",
        "negative_parameter_controls": "PASS"
        if critical["status"] == "BLOCKED_NOT_STRICTLY_HYPERBOLIC"
        and superluminal["status"]
        == "HYPERBOLIC_BUT_FAILS_NORMALIZED_LIGHT_CONE"
        else "FAIL",
        "quasistatic_cahn_hilliard_chemical_limit": "PASS"
        if numeric["chemical_limit_observed_order"] >= 0.8
        and numeric["chemical_limit_relative_l2_errors"][-1]
        < numeric["chemical_limit_relative_l2_errors"][0]
        and numeric["quasistatic_constraint_max_abs_residual"] <= 1e-11
        else "FAIL",
        "singular_limit_claim_restrained": "PASS"
        if singular["speed_increases_as_gamma_decreases"]
        and not singular["all_subluminal"]
        and not singular["uniform_subluminal_parabolic_limit"]
        else "FAIL",
        "ontology_separation": "PASS"
        if "trace" not in signature.parameters
        and "space_response" not in signature.parameters
        and "auxiliary_phase_is_not_UET_space_response"
        in contract["forbidden_identifications"]
        else "FAIL",
        "diffusive_bridge_dependency": "PASS"
        if diffusion.get("audit_status") == "PASS"
        and diffusion.get("evidence_status") == "PARTIAL"
        else "FAIL",
    }
    blocked_gates = {
        "uet_native_derivation_of_auxiliary_system": "BLOCKED",
        "covariant_action_and_current_mapping": "BLOCKED",
        "uniform_subluminal_cahn_hilliard_limit": "BLOCKED",
        "closed_time_path_kms_transport_matching": "BLOCKED",
        "dissipative_bianchi_identity": "BLOCKED",
        "curved_3p1_hyperbolic_solver": "BLOCKED",
        "system_specific_si_map": "BLOCKED",
        "external_numerical_benchmark_replication": "BLOCKED",
        "physical_validation": "BLOCKED",
    }
    audit_status = "PASS" if set(achieved_gates.values()) == {"PASS"} else "FAIL"
    evidence_status = (
        "PARTIAL_EXTERNAL_COMPARATOR" if audit_status == "PASS" else "BLOCKED"
    )
    hashes = {
        str(CORE.relative_to(ROOT)): _sha(canonical_existing_path(CORE)),
        str(SPEC.relative_to(ROOT)): _sha(canonical_existing_path(SPEC)),
        str(SOURCE_RECORD.relative_to(ROOT)): _sha(canonical_existing_path(SOURCE_RECORD)),
        str(DIFFUSION.relative_to(ROOT)): _sha(canonical_existing_path(DIFFUSION)),
    }
    verification = {
        "schema_version": "1.0",
        "artifact": "hyperbolic_phase_field_external_comparator_verification",
        "generated_at": now,
        "audit_status": audit_status,
        "evidence_status": evidence_status,
        "claim_class": "B",
        "claim": (
            "formula-level external comparator with fixed-parameter first-order "
            "hyperbolicity, periodic mass and Lyapunov closure, and an explicitly "
            "non-uniform parabolic causal limit"
        ),
        "source_provenance": provenance,
        "symbolic": symbolic,
        "numeric": numeric,
        "achieved_gates": achieved_gates,
        "blocked_gates": blocked_gates,
        "source_hashes": hashes,
        "run_contract": {
            "seed": 719061,
            "external_formula_source": True,
            "raw_source_committed": False,
            "parameter_fitting": False,
            "spatial_dimension": 1,
            "boundary_condition": "periodic",
            "time_integrator_validated": False,
            "physical_validation": False,
            "trace_backreaction": False,
        },
        "allowed_language": [
            "external first-order hyperbolic Cahn-Hilliard comparator",
            "fixed-parameter finite characteristic-speed control",
            "periodic semi-discrete mass and Lyapunov identity",
            "singular non-uniform Cahn-Hilliard causal limit",
        ],
        "blocked_language": [
            "UET derives the external hyperbolic phase-field system",
            "the paper auxiliary phase is UET space response",
            "the Cahn-Hilliard limit remains uniformly subluminal",
            "Topic 0.11 or 0.19 is externally validated",
        ],
        "next_controller": contract["next_controller"],
    }
    formula = {
        "schema_version": "1.0",
        "artifact": "hyperbolic_phase_field_formula_audit",
        "generated_at": now,
        "status": "WARN" if audit_status == "PASS" else "FAIL",
        "transcription_status": "PASS" if audit_status == "PASS" else "FAIL",
        "uet_derivation_status": "BLOCKED",
        "unit_lane": "normalized",
        "formula_registry": [
            {
                "id": "external_first_order_hyperbolic_system",
                "source_locator": "source_record::first_order_hyperbolic_system",
                "implementation": "docs/core/02_equations/matter_space/uet_hyperbolic_phase_field.py::hyperbolic_phase_field_rhs",
                "status": "IMPLEMENTED_EXTERNAL_COMPARATOR",
            },
            {
                "id": "external_augmented_lyapunov_functional",
                "source_locator": "source_record::augmented_lyapunov_functional",
                "implementation": "docs/core/02_equations/matter_space/uet_hyperbolic_phase_field.py::hyperbolic_phase_field_energy_balance",
                "status": "IMPLEMENTED_EXACT_PERIODIC_SEMI_DISCRETE",
            },
            {
                "id": "external_characteristic_speeds",
                "source_locator": "source_record::characteristic_speeds",
                "implementation": "docs/core/02_equations/matter_space/uet_hyperbolic_phase_field.py::hyperbolicity_diagnostics",
                "status": "IMPLEMENTED_WITH_SEPARATE_LIGHT_CONE_GATE",
            },
            {
                "id": "external_formal_ch_scaling",
                "source_locator": "source_record::formal_cahn_hilliard_scaling",
                "implementation": "docs/core/02_equations/matter_space/uet_hyperbolic_phase_field.py::paper_asymptotic_scaling_diagnostics",
                "status": "IMPLEMENTED_NEGATIVE_UNIFORM_CAUSAL_CONTROL",
            },
        ],
        "completed_formula_gates": list(achieved_gates),
        "open_formula_gates": list(blocked_gates),
        "source_hashes": hashes,
    }
    contract_artifact = {
        "schema_version": "1.0",
        "artifact": "hyperbolic_phase_field_source_contract",
        "generated_at": now,
        "provenance_status": provenance["status"],
        **contract,
    }
    program = {
        "schema_version": "1.0",
        "artifact": "uet_gr_research_program_gate",
        "generated_at": now,
        "status": "BLOCKED",
        "program_stage": (
            "EXTERNAL_HYPERBOLIC_PHASE_FIELD_COMPARATOR_FORMULA_VERIFIED"
            if audit_status == "PASS"
            else "CONSERVED_CURRENT_DIFFUSIVE_BRIDGE_PARTIAL"
        ),
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
            "covariant_exchange_bianchi_balance": "PASS",
            "causal_nonclosed_sector": "PASS_CONSTITUTIVE_1P1D",
            "weak_field_reduction": "PARTIAL_RESPONSE_ONLY",
            "covariant_matter_action": "PASS_O2_SCALAR_PILOT",
            "reciprocal_coupling": "PASS_ACTION_LEVEL",
            "matter_number_current": "PASS_ON_SHELL_O2",
            "diffusive_matter_reduction": "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT",
            "local_convex_matter_causality": "PASS_CONTROL",
            "gradient_phase_field_causality": "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY",
            "uniform_subluminal_phase_field_limit": "BLOCKED",
            "uet_covariant_phase_field_mapping": "BLOCKED",
            "physical_gr_benchmarks": "NOT_STARTED",
        },
        "global_universe_closure": "UNRESOLVED",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "controlling_blocker": contract["next_controller"],
        "claim_promotion": "BLOCKED",
        "reason": (
            "A sourced external first-order hyperbolic phase-field comparator now "
            "closes at formula level for fixed parameters, but it is not UET-derived "
            "and its parabolic Cahn-Hilliard scaling is not uniformly subluminal."
        ),
    }
    apply_latest_hyperbolic_phase_field_stage(OUT, verification, formula, contract_artifact, program)
    return verification, formula, contract_artifact, program


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    verification, formula, contract, program = build_artifacts()
    _dump(
        "hyperbolic_phase_field_external_comparator_verification.json",
        verification,
    )
    _dump("hyperbolic_phase_field_formula_audit.json", formula)
    _dump("hyperbolic_phase_field_source_contract.json", contract)
    _dump("uet_gr_research_program_gate.json", program)
    if args.print_summary:
        print(
            json.dumps(
                {
                    "audit_status": verification["audit_status"],
                    "evidence_status": verification["evidence_status"],
                    "formula_status": formula["status"],
                    "program_status": program["status"],
                    "controlling_blocker": program["controlling_blocker"],
                    "numeric": verification["numeric"],
                },
                indent=2,
            )
        )
    return 2 if args.strict and verification["audit_status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
