"""Verify the conserved-current bridge and its restricted causal scope."""

from __future__ import annotations

import argparse
import ast
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

from docs.core.uet_covariant_diffusion import (  # noqa: E402
    ConservedCurrentBridgeConfig,
    ConservedCurrentState,
    causal_current_rhs,
    compare_adiabatic_limit,
    compare_matter_space_conserved_rhs,
    conditioned_matter_chemical_potential,
    conditioned_matter_free_energy,
    current_bridge_contract,
    current_energy_balance,
    decompose_noether_current,
    normalize_local_charge_and_current,
    principal_symbol_diagnostics,
)
from docs.core.uet_spatial import integral_1d  # noqa: E402
from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
    canonical_existing_path,
)

from docs.scripts.audit.uet_gr_monotonic_stage import (  # noqa: E402
    apply_latest_hyperbolic_phase_field_stage,
)

CORE = canonical_existing_path(ROOT / "docs/core/02_equations/covariant/uet_covariant_diffusion.py")
SPEC = canonical_existing_path(ROOT / "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md")
OUT = CANONICAL_ARTIFACT_ROOT
MATTER = canonical_artifact_path(
    "covariant_matter_action_verification.json",
    "verification",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(name: str, payload: dict[str, Any]) -> None:
    path = canonical_artifact_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _epsilon_denominators(source: str) -> list[int]:
    tree = ast.parse(source)
    result: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        if any(
            (isinstance(child, ast.Name) and child.id == "epsilon_nc")
            or (isinstance(child, ast.Attribute) and child.attr == "epsilon_nc")
            for child in ast.walk(node.right)
        ):
            result.append(node.lineno)
    return result


def _symbolic() -> dict[str, Any]:
    tau, mobility = sp.symbols("tau mobility", positive=True)
    current, gradient = sp.symbols("current gradient", real=True)
    epsilon, coupling = sp.symbols(
        "epsilon coupling", real=True, nonnegative=True
    )
    wave_number, curvature, kappa, growth = sp.symbols(
        "k curvature kappa growth", positive=True
    )
    current_rate = (-current - mobility * gradient) / tau
    free_rate = gradient * current
    storage_rate = tau * current * current_rate / mobility
    dissipation = current**2 / mobility
    energy_residual = sp.simplify(free_rate + storage_rate + dissipation)
    dispersion = (
        tau * growth**2
        + growth
        + mobility * (curvature * wave_number**2 + kappa * wave_number**4)
    )
    return {
        "energy_identity_residual": str(energy_residual),
        "energy_identity_exact": energy_residual == 0,
        "adiabatic_flux": str(sp.solve(sp.Eq(0, -current - mobility * gradient), current)[0]),
        "nested_coupling": str(epsilon * coupling),
        "epsilon_zero_coupling_exact": sp.simplify(
            (epsilon * coupling).subs(epsilon, 0)
        )
        == 0,
        "linearized_dispersion_polynomial": str(dispersion),
        "local_characteristic_speed": "sqrt(mobility*curvature/tau)",
        "gradient_high_k_angular_frequency": "sqrt(mobility*kappa/tau)*k^2",
        "gradient_high_k_phase_speed": "sqrt(mobility*kappa/tau)*k",
        "strict_causal_scope": "kappa=0_and_local_curvature_positive",
    }


def _state(boundary: str, rng: np.random.Generator, n: int) -> ConservedCurrentState:
    density = rng.normal(scale=0.12, size=n)
    flux_count = n if boundary == "periodic" else n + 1
    flux = rng.normal(scale=0.035, size=flux_count)
    if boundary == "zero_flux":
        flux[[0, -1]] = 0.0
    return ConservedCurrentState(density, flux)


def _local_cone_control() -> dict[str, float]:
    """Propagate the local convex principal system at exact CFL one."""

    n_cells = 401
    center = n_cells // 2
    steps = 24
    dx = 0.1
    config = ConservedCurrentBridgeConfig(
        a_matter=0.4,
        b_matter=1.0,
        kappa_matter=0.0,
        mobility_matter=0.1,
        tau_current=0.5,
        coupling_base=0.0,
    )
    speed = float(
        np.sqrt(config.mobility_matter * config.a_matter / config.tau_current)
    )
    dt = dx / speed
    density = np.zeros(n_cells)
    density[center] = 1.0
    current = np.zeros(n_cells)
    for _ in range(steps):
        right = current + speed * density
        left = current - speed * density
        right = np.roll(right, 1)
        left = np.roll(left, -1)
        density = (right - left) / (2.0 * speed)
        current = 0.5 * (right + left)
        current *= np.exp(-dt / config.tau_current)
    offsets = np.minimum(
        (np.arange(n_cells) - center) % n_cells,
        (center - np.arange(n_cells)) % n_cells,
    )
    outside = offsets > steps
    peak = max(float(np.max(np.abs(density))), np.finfo(float).tiny)
    leakage = float(np.max(np.abs(density[outside]))) / peak
    active = offsets[np.abs(density) > peak * 1e-13]
    reached_cells = int(np.max(active))
    observed_speed = reached_cells * dx / (steps * dt)
    return {
        "characteristic_speed": speed,
        "observed_front_speed": observed_speed,
        "arrival_speed_relative_error": abs(observed_speed - speed) / speed,
        "outside_cone_leakage_ratio": leakage,
        "normalized_light_speed": config.normalized_light_speed,
    }


def _numeric() -> dict[str, Any]:
    rng = np.random.default_rng(190061)
    n_cells = 96
    dx = 0.125
    response = rng.normal(scale=0.08, size=n_cells)
    mass_residuals: dict[str, float] = {}
    energy_residuals: dict[str, float] = {}
    adiabatic_residuals: dict[str, float] = {}
    for boundary in ("periodic", "zero_flux"):
        state = _state(boundary, rng, n_cells)
        config = ConservedCurrentBridgeConfig(
            a_matter=-0.35,
            b_matter=0.8,
            kappa_matter=0.25,
            mobility_matter=0.6,
            tau_current=0.3,
            coupling_base=0.2,
            epsilon_nc=0.4,
            boundary_condition=boundary,
        )
        density_rate, _, _, _ = causal_current_rhs(
            state, response, dx, config
        )
        mass_residuals[boundary] = abs(integral_1d(density_rate, dx))
        energy_residuals[boundary] = abs(
            current_energy_balance(state, response, dx, config)[
                "closure_residual"
            ]
        )
        adiabatic_residuals[boundary] = compare_adiabatic_limit(
            state.C, response, dx, config
        )["max_abs_difference"]

    density = rng.normal(scale=0.1, size=n_cells)
    direction = rng.normal(size=n_cells)
    direction /= np.linalg.norm(direction)
    phase_config = ConservedCurrentBridgeConfig(
        a_matter=-0.4,
        b_matter=0.9,
        kappa_matter=0.2,
        mobility_matter=0.7,
        tau_current=0.25,
        coupling_base=0.3,
        epsilon_nc=0.35,
    )
    step = 1e-6
    finite_difference = (
        conditioned_matter_free_energy(
            density + step * direction, response, dx, phase_config
        )
        - conditioned_matter_free_energy(
            density - step * direction, response, dx, phase_config
        )
    ) / (2.0 * step)
    chemical = conditioned_matter_chemical_potential(
        density, response, dx, phase_config
    )
    directional_residual = abs(
        finite_difference - integral_1d(chemical * direction, dx)
    )
    matter_space_residual = compare_matter_space_conserved_rhs(
        density, response, dx, phase_config
    )["max_abs_difference"]

    gr_config = ConservedCurrentBridgeConfig(
        a_matter=-0.4,
        b_matter=0.9,
        kappa_matter=0.2,
        mobility_matter=0.7,
        tau_current=0.25,
        coupling_base=1e6,
        epsilon_nc=0.0,
    )
    gr_first = compare_adiabatic_limit(
        density, response, dx, gr_config
    )["model_b_rhs"]
    gr_second = compare_adiabatic_limit(
        density, response + 1e9, dx, gr_config
    )["model_b_rhs"]

    metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    velocity = 0.37
    gamma = 1.0 / np.sqrt(1.0 - velocity**2)
    decomposition = decompose_noether_current(
        metric,
        np.array([gamma, gamma * velocity, 0.0, 0.0]),
        np.array([1.5, -0.2, 0.13, -0.07]),
    )
    normalized_density, normalized_current = normalize_local_charge_and_current(
        np.array([4.0]),
        np.array([32.0]),
        ConservedCurrentBridgeConfig(
            density_scale=2.0, length_scale=4.0, time_scale=0.5
        ),
    )

    local_config = ConservedCurrentBridgeConfig(
        a_matter=0.4,
        b_matter=0.2,
        kappa_matter=0.0,
        mobility_matter=0.1,
        tau_current=0.5,
    )
    local_diagnostics = principal_symbol_diagnostics(
        np.linspace(-0.1, 0.1, n_cells), np.zeros(n_cells), local_config
    )
    gradient_diagnostics = principal_symbol_diagnostics(
        np.zeros(n_cells),
        np.zeros(n_cells),
        ConservedCurrentBridgeConfig(
            a_matter=1.0,
            kappa_matter=0.2,
            mobility_matter=0.1,
            tau_current=0.5,
        ),
    )
    spinodal_diagnostics = principal_symbol_diagnostics(
        np.zeros(n_cells),
        np.zeros(n_cells),
        ConservedCurrentBridgeConfig(a_matter=-1.0, kappa_matter=0.0),
    )
    return {
        "mass_conservation_abs_residual": mass_residuals,
        "energy_identity_abs_residual": energy_residuals,
        "adiabatic_model_b_max_abs_residual": adiabatic_residuals,
        "functional_directional_derivative_abs_residual": directional_residual,
        "matter_space_rhs_max_abs_residual": matter_space_residual,
        "epsilon_zero_space_response_invariance_max_abs": float(
            np.max(np.abs(gr_first - gr_second))
        ),
        "current_reconstruction_max_abs_error": decomposition.reconstruction_error,
        "current_orthogonality_abs_error": decomposition.orthogonality_error,
        "normalized_density_control": float(normalized_density[0]),
        "normalized_current_control": float(normalized_current[0]),
        "local_principal_symbol": local_diagnostics,
        "gradient_phase_field_principal_symbol": gradient_diagnostics,
        "spinodal_principal_symbol": spinodal_diagnostics,
        "local_cone_control": _local_cone_control(),
    }


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    symbolic = _symbolic()
    numeric = _numeric()
    contract = current_bridge_contract()
    source = CORE.read_text(encoding="utf-8")
    denominators = _epsilon_denominators(source)
    matter = json.loads(MATTER.read_text(encoding="utf-8"))
    signature = inspect.signature(causal_current_rhs)
    local = numeric["local_principal_symbol"]
    gradient = numeric["gradient_phase_field_principal_symbol"]
    spinodal = numeric["spinodal_principal_symbol"]
    cone = numeric["local_cone_control"]
    achieved_gates = {
        "covariant_current_frame_decomposition": "PASS"
        if max(
            numeric["current_reconstruction_max_abs_error"],
            numeric["current_orthogonality_abs_error"],
        )
        <= 1e-12
        else "FAIL",
        "declared_charge_current_normalization": "PASS"
        if numeric["normalized_density_control"] == 2.0
        and numeric["normalized_current_control"] == 2.0
        else "FAIL",
        "discrete_charge_conservation": "PASS"
        if max(numeric["mass_conservation_abs_residual"].values()) <= 1e-12
        else "FAIL",
        "semi_discrete_energy_identity": "PASS"
        if symbolic["energy_identity_exact"]
        and max(numeric["energy_identity_abs_residual"].values()) <= 1e-11
        else "FAIL",
        "functional_derivative_closure": "PASS"
        if numeric["functional_directional_derivative_abs_residual"] <= 1e-8
        else "FAIL",
        "adiabatic_model_b_limit": "PASS"
        if max(numeric["adiabatic_model_b_max_abs_residual"].values()) <= 1e-12
        else "FAIL",
        "existing_matter_space_matter_rhs_map": "PASS"
        if numeric["matter_space_rhs_max_abs_residual"] <= 1e-12
        else "FAIL",
        "regular_epsilon_null_coupling": "PASS"
        if symbolic["epsilon_zero_coupling_exact"]
        and numeric["epsilon_zero_space_response_invariance_max_abs"] == 0.0
        and not denominators
        else "FAIL",
        "local_convex_causal_control": "PASS"
        if local["status"] == "PASS_LOCAL_CONVEX_MAXWELL_CATTANEO"
        and cone["outside_cone_leakage_ratio"] <= 1e-12
        and cone["arrival_speed_relative_error"] <= 0.05
        and cone["characteristic_speed"] <= cone["normalized_light_speed"]
        else "FAIL",
        "phase_field_causal_claim_restrained": "PASS"
        if gradient["status"] == "BLOCKED_FOURTH_ORDER_UV_CAUSALITY"
        and spinodal["status"] == "BLOCKED_NONCONVEX_OR_SPINODAL"
        else "FAIL",
        "derived_trace_disconnected": "PASS"
        if "trace" not in signature.parameters
        and "uet_trace" not in source
        and not contract["derived_trace_backreaction"]
        else "FAIL",
        "covariant_matter_dependency": "PASS"
        if matter.get("audit_status") == "PASS"
        and matter.get("evidence_status") == "PARTIAL"
        else "FAIL",
    }
    blocked_gates = {
        "microscopic_amplitude_to_charge_density_matching": "BLOCKED",
        "first_order_hyperbolic_gradient_phase_field": "BLOCKED",
        "spinodal_hyperbolicity_and_stability": "BLOCKED",
        "closed_time_path_kms_transport_derivation": "BLOCKED",
        "dissipative_current_coupled_bianchi_identity": "BLOCKED",
        "curved_3p1_transport_solver": "BLOCKED",
        "system_specific_SI_map": "BLOCKED",
        "physical_validation": "BLOCKED",
    }
    audit_status = "PASS" if set(achieved_gates.values()) == {"PASS"} else "FAIL"
    evidence_status = "PARTIAL" if audit_status == "PASS" else "BLOCKED"
    hashes = {
        str(CORE.relative_to(ROOT)): _sha(CORE),
        str(SPEC.relative_to(ROOT)): _sha(SPEC),
        str(MATTER.relative_to(ROOT)): _sha(MATTER),
    }
    verification = {
        "schema_version": "1.0",
        "artifact": "covariant_diffusive_current_verification",
        "generated_at": now,
        "audit_status": audit_status,
        "evidence_status": evidence_status,
        "claim_class": "B",
        "claim": "partial constitutive bridge from an on-shell O(2) charge current to a normalized conserved finite-relaxation current with an exact Model-B limit",
        "symbolic": symbolic,
        "numeric": numeric,
        "epsilon_denominator_lines": denominators,
        "achieved_gates": achieved_gates,
        "blocked_gates": blocked_gates,
        "source_hashes": hashes,
        "run_contract": {
            "seed": 190061,
            "external_data": False,
            "parameter_fitting": False,
            "spatial_dimension": 1,
            "local_convex_causal_control": True,
            "full_gradient_phase_field_causality": False,
            "trace_backreaction": False,
        },
        "allowed_language": [
            "declared coarse-grained Noether-charge density",
            "finite-relaxation conserved-current constitutive bridge",
            "exact discrete Model-B adiabatic limit",
            "causal local convex Maxwell-Cattaneo control",
        ],
        "blocked_language": [
            "scalar amplitude derived as matter density",
            "full Cahn-Hilliard phase field proved relativistically causal",
            "transport coefficients derived microscopically",
            "Topic 0.11 or 0.19 validated",
        ],
        "comparison_sources": [
            {
                "role": "conserved_order_parameter_classification",
                "title": "Theory of dynamic critical phenomena",
                "doi": "10.1103/RevModPhys.49.435",
                "url": "https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.49.435",
            },
            {
                "role": "causal_diffusion_effective_action_constraint",
                "title": "Schwinger-Keldysh effective field theory for stable and causal relativistic hydrodynamics",
                "url": "https://arxiv.org/abs/2309.00511",
            },
            {
                "role": "future_first_order_hyperbolic_phase_field_comparator",
                "title": "A first-order hyperbolic reformulation of the Cahn-Hilliard equation",
                "doi": "10.1098/rspa.2024.0606",
                "url": "https://arxiv.org/abs/2408.03862",
            },
        ],
        "next_controller": "first_order_hyperbolic_phase_field_uv_closure_missing",
    }
    formula = {
        "schema_version": "1.0",
        "artifact": "covariant_diffusion_formula_audit",
        "generated_at": now,
        "status": "WARN" if audit_status == "PASS" else "FAIL",
        "implementation_status": "PRESENT" if audit_status == "PASS" else "INCOMPLETE",
        "derivation_status": "constitutive current reduction with exact discrete identities; microscopic and full hyperbolic phase-field derivations remain open",
        "unit_lane": "natural_to_normalized",
        "formula_registry": [
            {
                "id": "current_frame_decomposition",
                "implementation": "docs/core/02_equations/covariant/uet_covariant_diffusion.py::decompose_noether_current",
                "status": "IMPLEMENTED_KINEMATIC",
            },
            {
                "id": "finite_relaxation_current",
                "implementation": "docs/core/02_equations/covariant/uet_covariant_diffusion.py::causal_current_rhs",
                "status": "IMPLEMENTED_CONSTITUTIVE",
            },
            {
                "id": "semi_discrete_energy_identity",
                "implementation": "docs/core/02_equations/covariant/uet_covariant_diffusion.py::current_energy_balance",
                "status": "IMPLEMENTED_EXACT",
            },
            {
                "id": "model_b_adiabatic_limit",
                "implementation": "docs/core/02_equations/covariant/uet_covariant_diffusion.py::compare_adiabatic_limit",
                "status": "IMPLEMENTED_EXACT_DISCRETE",
            },
        ],
        "completed_formula_gates": [
            "regular_epsilon_nested_matter_coupling",
            "conserved_current_energy_identity",
            "model_b_matter_equation_map",
            "local_convex_characteristic_control",
        ],
        "open_formula_gates": list(blocked_gates),
        "epsilon_denominator_lines": denominators,
        "source_hashes": hashes,
    }
    contract_artifact = {
        "schema_version": "1.0",
        "artifact": "covariant_diffusion_contract",
        "generated_at": now,
        **contract,
    }
    program = {
        "schema_version": "1.0",
        "artifact": "uet_gr_research_program_gate",
        "generated_at": now,
        "status": "BLOCKED",
        "program_stage": "CONSERVED_CURRENT_DIFFUSIVE_BRIDGE_PARTIAL"
        if audit_status == "PASS"
        else "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED",
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
            "gradient_phase_field_causality": "BLOCKED_UV",
            "physical_gr_benchmarks": "NOT_STARTED",
        },
        "global_universe_closure": "UNRESOLVED",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "controlling_blocker": "first_order_hyperbolic_phase_field_uv_closure_missing",
        "claim_promotion": "BLOCKED",
        "reason": "The coarse-grained conserved-current bridge, energy identity, regular epsilon nesting, and Model-B limit close, but microscopic density matching and a first-order hyperbolic closure for the gradient/spinodal phase field are absent.",
    }
    apply_latest_hyperbolic_phase_field_stage(OUT, verification, formula, contract_artifact, program)
    return verification, formula, contract_artifact, program


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    verification, formula, contract, program = build_artifacts()
    _dump("covariant_diffusive_current_verification.json", verification)
    _dump("covariant_diffusion_formula_audit.json", formula)
    _dump("covariant_diffusion_contract.json", contract)
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
