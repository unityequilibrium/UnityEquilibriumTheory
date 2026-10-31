"""Audit a bounded linear-GR TT wave sector with an SBP-SAT boundary."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Any

import numpy as np
from numpy.polynomial.legendre import Legendre

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_tt_sbp_sat_boundary_pilot.json"
)
AUDIT_SOURCE = Path(__file__).resolve()
TEST_SOURCE = ROOT / (
    "docs/core/05_tests/regression/root/"
    "test_uet_curved_3p1_gh_tt_sbp_sat_boundary.py"
)
PERIODIC_GH_SOURCE = ROOT / (
    "docs/core/02_equations/covariant/uet_curved_3p1_gh_evolution.py"
)
GH_BOUNDARY_SOURCE = ROOT / (
    "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
)
GH_SYSTEM_SOURCE = ROOT / (
    "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"
)


@dataclass(frozen=True)
class TTWaveState:
    displacement: np.ndarray
    momentum: np.ndarray
    spatial_gradient: np.ndarray


@dataclass(frozen=True)
class SBPOperators:
    nodes: np.ndarray
    norm_weights: np.ndarray
    derivative: np.ndarray


def legendre_lobatto_operators(
    order: int, bounds: tuple[float, float] = (-1.0, 1.0)
) -> SBPOperators:
    """Return diagonal-norm Legendre-Gauss-Lobatto SBP operators."""

    degree = int(order)
    left, right = (float(value) for value in bounds)
    if degree < 2 or degree != order:
        raise ValueError("order must be an integer >= 2")
    if not np.isfinite(left + right) or right <= left:
        raise ValueError("bounds must be finite and strictly increasing")

    polynomial = Legendre.basis(degree)
    reference_nodes = np.concatenate(
        (np.array([-1.0]), polynomial.deriv().roots(), np.array([1.0]))
    )
    reference_nodes.sort()
    p_values = polynomial(reference_nodes)
    reference_weights = 2.0 / (degree * (degree + 1) * p_values**2)

    derivative = np.zeros((degree + 1, degree + 1), dtype=float)
    for row in range(degree + 1):
        for column in range(degree + 1):
            if row != column:
                derivative[row, column] = p_values[row] / (
                    p_values[column]
                    * (reference_nodes[row] - reference_nodes[column])
                )
        derivative[row, row] = -np.sum(derivative[row])

    half_length = 0.5 * (right - left)
    nodes = left + half_length * (reference_nodes + 1.0)
    return SBPOperators(
        nodes=nodes,
        norm_weights=half_length * reference_weights,
        derivative=derivative / half_length,
    )


def _validate_state(state: TTWaveState, node_count: int) -> None:
    expected = (2, node_count)
    for name, value in (
        ("displacement", state.displacement),
        ("momentum", state.momentum),
        ("spatial_gradient", state.spatial_gradient),
    ):
        if value.shape != expected or not np.all(np.isfinite(value)):
            raise ValueError(f"{name} must be finite with shape {expected}")


def tt_wave_rhs(state: TTWaveState, operators: SBPOperators) -> TTWaveState:
    """Evolve both TT polarizations with constraint-compatible SAT penalties."""

    _validate_state(state, operators.nodes.size)
    pi = state.momentum
    grad = state.spatial_gradient
    pi_rhs = -(grad @ operators.derivative.T)
    grad_rhs = -(pi @ operators.derivative.T)

    # The left/right penalties cancel incoming characteristic energy flux while
    # leaving grad_dot = D(displacement_dot), so the reduction constraint persists.
    left_incoming = pi[:, 0] + grad[:, 0]
    right_incoming = pi[:, -1] - grad[:, -1]
    pi_rhs[:, 0] -= left_incoming / operators.norm_weights[0]
    pi_rhs[:, -1] -= right_incoming / operators.norm_weights[-1]

    return TTWaveState(
        displacement=-pi.copy(),
        momentum=pi_rhs,
        spatial_gradient=grad_rhs,
    )


def wave_energy(state: TTWaveState, operators: SBPOperators) -> float:
    density = state.momentum**2 + state.spatial_gradient**2
    return float(0.5 * np.sum(density * operators.norm_weights[None, :]))


def reduction_constraint_linf(
    state: TTWaveState, operators: SBPOperators
) -> float:
    residual = state.displacement @ operators.derivative.T - state.spatial_gradient
    return float(np.max(np.abs(residual)))


def _combine(
    state: TTWaveState,
    terms: tuple[tuple[float, TTWaveState], ...],
) -> TTWaveState:
    values = [
        state.displacement.copy(),
        state.momentum.copy(),
        state.spatial_gradient.copy(),
    ]
    for coefficient, term in terms:
        values[0] += coefficient * term.displacement
        values[1] += coefficient * term.momentum
        values[2] += coefficient * term.spatial_gradient
    return TTWaveState(*values)


def rk4_step(
    state: TTWaveState, operators: SBPOperators, dt: float
) -> TTWaveState:
    step = float(dt)
    if not np.isfinite(step) or step <= 0.0:
        raise ValueError("dt must be finite and positive")
    k1 = tt_wave_rhs(state, operators)
    k2 = tt_wave_rhs(_combine(state, ((0.5 * step, k1),)), operators)
    k3 = tt_wave_rhs(_combine(state, ((0.5 * step, k2),)), operators)
    k4 = tt_wave_rhs(_combine(state, ((step, k3),)), operators)
    return _combine(
        state,
        (
            (step / 6.0, k1),
            (step / 3.0, k2),
            (step / 3.0, k3),
            (step / 6.0, k4),
        ),
    )


def _semi_discrete_matrix(operators: SBPOperators) -> np.ndarray:
    count = operators.nodes.size
    matrix = np.zeros((2 * count, 2 * count), dtype=float)
    for column in range(2 * count):
        pi = np.zeros((2, count), dtype=float)
        grad = np.zeros_like(pi)
        if column < count:
            pi[0, column] = 1.0
        else:
            grad[0, column - count] = 1.0
        zero = np.zeros_like(pi)
        rhs = tt_wave_rhs(TTWaveState(zero, pi, grad), operators)
        matrix[:, column] = np.concatenate(
            (rhs.momentum[0], rhs.spatial_gradient[0])
        )
    return matrix


def _rk4_stability_polynomial(value: np.ndarray) -> np.ndarray:
    return 1.0 + value + value**2 / 2.0 + value**3 / 6.0 + value**4 / 24.0


def rk4_stable_timestep(operators: SBPOperators) -> tuple[float, float]:
    """Compute a conservative RK4 step from the declared linear operator."""

    eigenvalues = np.linalg.eigvals(_semi_discrete_matrix(operators))
    if float(np.max(eigenvalues.real)) > 1.0e-10:
        raise RuntimeError("semi-discrete operator has a growing eigenmode")

    def stable(step: float) -> bool:
        amplification = _rk4_stability_polynomial(step * eigenvalues)
        return bool(np.max(np.abs(amplification)) <= 1.0 + 1.0e-10)

    scale = max(float(np.max(np.abs(eigenvalues))), 1.0)
    lower = 0.0
    upper = 1.0 / scale
    for _ in range(50):
        if not stable(upper):
            break
        lower = upper
        upper *= 2.0
    else:
        raise RuntimeError("failed to bracket the RK4 stability boundary")

    for _ in range(70):
        middle = 0.5 * (lower + upper)
        if stable(middle):
            lower = middle
        else:
            upper = middle
    return 0.75 * lower, float(np.max(eigenvalues.real))


def maximum_rk4_amplification(operators: SBPOperators, dt: float) -> float:
    eigenvalues = np.linalg.eigvals(_semi_discrete_matrix(operators))
    return float(
        np.max(np.abs(_rk4_stability_polynomial(float(dt) * eigenvalues)))
    )


def evolve(
    initial: TTWaveState,
    operators: SBPOperators,
    final_time: float,
    target_dt: float,
) -> tuple[TTWaveState, int, float]:
    target = float(final_time)
    step_cap = float(target_dt)
    if not np.isfinite(target) or target <= 0.0:
        raise ValueError("final_time must be finite and positive")
    if not np.isfinite(step_cap) or step_cap <= 0.0:
        raise ValueError("target_dt must be finite and positive")
    count = max(1, int(ceil(target / step_cap)))
    dt = target / count
    state = TTWaveState(
        initial.displacement.copy(),
        initial.momentum.copy(),
        initial.spatial_gradient.copy(),
    )
    _validate_state(state, operators.nodes.size)
    for _ in range(count):
        state = rk4_step(state, operators, dt)
        if not all(
            np.all(np.isfinite(value))
            for value in (
                state.displacement,
                state.momentum,
                state.spatial_gradient,
            )
        ):
            raise RuntimeError("non-finite state encountered during evolution")
    return state, count, dt


def gaussian_right_going_state(
    operators: SBPOperators,
    *, center: float = 0.0, width: float = 0.12,
) -> TTWaveState:
    x = operators.nodes
    profile = np.exp(-0.5 * ((x - center) / width) ** 2)
    displacement = np.stack((profile, 0.35 * profile))
    gradient = displacement @ operators.derivative.T
    return TTWaveState(displacement, gradient.copy(), gradient.copy())


def gaussian_left_going_state(
    operators: SBPOperators,
    *, center: float = 0.0, width: float = 0.12,
) -> TTWaveState:
    right_going = gaussian_right_going_state(
        operators, center=center, width=width
    )
    return TTWaveState(
        right_going.displacement,
        -right_going.spatial_gradient.copy(),
        right_going.spatial_gradient.copy(),
    )


def _weighted_state_difference(
    left: TTWaveState, right: TTWaveState, operators: SBPOperators
) -> float:
    domain_length = float(operators.nodes[-1] - operators.nodes[0])
    total = np.zeros(operators.nodes.size, dtype=float)
    for first, second, scale in (
        (left.displacement, right.displacement, 1.0),
        (left.momentum, right.momentum, domain_length),
        (left.spatial_gradient, right.spatial_gradient, domain_length),
    ):
        total += np.sum(((first - second) * scale) ** 2, axis=0)
    return float(np.sqrt(np.sum(operators.norm_weights * total)))


def _semi_discrete_energy_identity_residual(
    state: TTWaveState, operators: SBPOperators
) -> tuple[float, float]:
    rhs = tt_wave_rhs(state, operators)
    measured = float(
        np.sum(
            operators.norm_weights[None, :]
            * (
                state.momentum * rhs.momentum
                + state.spatial_gradient * rhs.spatial_gradient
            )
        )
    )
    expected = -float(
        np.sum(state.momentum[:, 0] ** 2 + state.momentum[:, -1] ** 2)
    )
    return measured, abs(measured - expected)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact() -> dict[str, Any]:
    order = 72
    final_time = 2.4
    operators = legendre_lobatto_operators(order)
    degree_checks = [4, 8, 12, order]
    sbp_residuals = []
    derivative_residuals = []
    for degree in degree_checks:
        current = legendre_lobatto_operators(degree)
        boundary = np.zeros((degree + 1, degree + 1), dtype=float)
        boundary[0, 0] = -1.0
        boundary[-1, -1] = 1.0
        weighted_derivative = current.norm_weights[:, None] * current.derivative
        sbp_residuals.append(
            float(
                np.max(
                    np.abs(
                        weighted_derivative
                        + weighted_derivative.T
                        - boundary
                    )
                )
            )
        )
        for power in range(degree + 1):
            exact = (
                np.zeros_like(current.nodes)
                if power == 0
                else power * current.nodes ** (power - 1)
            )
            observed = current.derivative @ current.nodes**power
            derivative_residuals.append(
                float(np.max(np.abs(observed - exact)))
            )

    rng = np.random.default_rng(20260925)
    random_state = TTWaveState(
        displacement=rng.normal(size=(2, order + 1)),
        momentum=rng.normal(size=(2, order + 1)),
        spatial_gradient=rng.normal(size=(2, order + 1)),
    )
    measured_energy_rate, energy_identity_residual = (
        _semi_discrete_energy_identity_residual(random_state, operators)
    )

    analytic_initial = gaussian_right_going_state(operators)
    initial_reduction_residual = reduction_constraint_linf(
        analytic_initial, operators
    )
    stable_dt, maximum_eigenvalue_real_part = rk4_stable_timestep(operators)
    minimum_spacing = float(np.min(np.diff(operators.nodes)))
    timestep_cap = min(0.5 * minimum_spacing, 0.25 * stable_dt)

    convergence_time = 0.25
    convergence_base_dt = timestep_cap / 4.0
    convergence_runs = []
    for refinement in range(3):
        result, steps, used_dt = evolve(
            analytic_initial,
            operators,
            convergence_time,
            convergence_base_dt / (2**refinement),
        )
        convergence_runs.append((result, steps, used_dt))
    convergence_differences = [
        _weighted_state_difference(
            convergence_runs[index][0],
            convergence_runs[index + 1][0],
            operators,
        )
        for index in range(2)
    ]
    temporal_convergence_ratio = (
        convergence_differences[0] / convergence_differences[1]
        if convergence_differences[1] > 0.0
        else float("inf")
    )

    absorbed, pulse_steps, pulse_dt = evolve(
        analytic_initial, operators, final_time, timestep_cap
    )
    left_initial = gaussian_left_going_state(operators)
    left_absorbed, left_pulse_steps, left_pulse_dt = evolve(
        left_initial, operators, final_time, timestep_cap
    )
    initial_energy = wave_energy(analytic_initial, operators)
    final_energy = wave_energy(absorbed, operators)
    final_energy_ratio = final_energy / initial_energy
    left_initial_energy = wave_energy(left_initial, operators)
    left_final_energy = wave_energy(left_absorbed, operators)
    left_final_energy_ratio = left_final_energy / left_initial_energy
    final_reduction_residual = reduction_constraint_linf(absorbed, operators)
    left_final_reduction_residual = reduction_constraint_linf(
        left_absorbed, operators
    )
    maximum_amplification = maximum_rk4_amplification(operators, pulse_dt)
    incoming_left_initial = float(
        np.max(np.abs(analytic_initial.momentum[:, 0] + analytic_initial.spatial_gradient[:, 0]))
    )
    incoming_right_initial = float(
        np.max(np.abs(analytic_initial.momentum[:, -1] - analytic_initial.spatial_gradient[:, -1]))
    )

    local_sources = (
        AUDIT_SOURCE,
        TEST_SOURCE,
        PERIODIC_GH_SOURCE,
        GH_BOUNDARY_SOURCE,
        GH_SYSTEM_SOURCE,
    )
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in local_sources
        if path.is_file()
    }
    checks = {
        "lgl_diagonal_norm_satisfies_sbp_identity": max(sbp_residuals) <= 2.0e-12,
        "lgl_derivative_is_polynomial_exact_to_degree": max(derivative_residuals) <= 2.0e-10,
        "semi_discrete_energy_rate_matches_boundary_flux": energy_identity_residual <= 2.0e-11,
        "initial_tt_reduction_constraint_is_closed": initial_reduction_residual <= 2.0e-10,
        "tt_reduction_constraint_is_preserved_by_time_evolution": final_reduction_residual <= 2.0e-9,
        "initial_packet_has_no_material_incoming_boundary_tail": max(
            incoming_left_initial, incoming_right_initial
        ) <= 2.0e-10,
        "rk4_temporal_refinement_is_fourth_order": 10.0
        <= temporal_convergence_ratio
        <= 22.0,
        "right_going_packet_leaves_through_right_face": final_energy_ratio <= 2.0e-6,
        "left_going_packet_leaves_through_left_face": left_final_energy_ratio <= 2.0e-6,
        "linear_semidiscrete_operator_has_no_positive_real_eigenvalue": maximum_eigenvalue_real_part
        <= 1.0e-10,
        "selected_timestep_is_inside_rk4_eigenvalue_stability_region": maximum_amplification
        <= 1.0 + 1.0e-10,
        "all_declared_local_sources_are_present": len(source_hashes) == len(local_sources),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    status = (
        "PASS_GH_LINEAR_TT_SBP_SAT_BOUNDARY_PILOT"
        if all(checks.values())
        else "FAIL_GH_LINEAR_TT_SBP_SAT_BOUNDARY_PILOT"
    )

    return {
        "schema_version": "core-curved-3p1-gh-tt-sbp-sat-pilot-v1",
        "artifact": "curved_3p1_gh_tt_sbp_sat_boundary_pilot",
        "diagnostic_id": "uet.core.curved_3p1.gh.tt_sbp_sat_boundary_pilot",
        "generated_at": "2026-09-25",
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_LINEAR_TT_SBP_SAT_BOUNDARY_PILOT",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
            "what_is_closed": [
                "two linearized-GR transverse-traceless polarizations evolve on a finite non-periodic interval",
                "Legendre-Gauss-Lobatto diagonal-norm SBP identity and polynomial derivative exactness pass",
                "a constraint-compatible SAT penalty gives the exact semidiscrete energy rate minus the squared endpoint momenta",
                "the TT reduction constraint is preserved and a right-going packet exits without a large reflected-energy remainder",
                "a left-going analytic packet is independently absorbed at the opposite face",
            ],
            "equation_or_mapping": {
                "tt_wave": "partial_t^2 h_A - partial_x^2 h_A = 0, A in {+,x}",
                "first_order_state": "Pi_A=-partial_t h_A; G_A=partial_x h_A",
                "incoming_left": "w_in,L=Pi+G",
                "incoming_right": "w_in,R=Pi-G",
                "sat": "Pi_dot=-D G-H^-1 e_L*(Pi+G)_L-H^-1 e_R*(Pi-G)_R; G_dot=-D Pi; h_dot=-Pi",
                "semi_discrete_energy": "E=1/2 sum_A (Pi_A^T H Pi_A + G_A^T H G_A)",
                "energy_rate": "dE/dt=-sum_A(Pi_A,left^2+Pi_A,right^2)<=0",
                "reduction_constraint": "D h_A-G_A=0 is invariant under the semidiscrete evolution",
            },
            "units": {
                "unit_lane": "geometric c=1, dimensionless metric perturbation",
                "h_A": "dimensionless",
                "Pi_A_and_G_A": "L^-1",
                "energy": "L^-1 per unit transverse area",
                "UET_symbols_used": [],
            },
            "derivation_class": "standard linearized-GR TT wave equation plus directly verified SBP-SAT semidiscrete energy identity",
            "observable": "boundary flux, semidiscrete energy, reduction-constraint residual, and pulse remainders at both faces",
            "data_role": "manufactured analytic/synthetic numerical control; no source data, fitting, or holdout",
            "evidence_artifacts": [],
            "verification_status": status,
            "open_blockers": [
                "the 4+2+4 constraint/physical/gauge decomposition is not imposed on the full ten-component GH system",
                "positive-normal-shift incoming u2_A constraint conditions are not evolved",
                "variable-coefficient nonlinear GH, corners, matter boundary conditions, and full subsidiary-constraint propagation remain untested",
                "this pilot does not implement the full differential Rinne CPBC and does not modify the periodic GH solver",
            ],
            "dependency_unlocked": "none; this validates one standard-GR physical TT boundary sector only",
            "claim_boundary": "bounded linearized-GR TT-sector numerical control only; not full GH CPBC, nonlinear IBVP well-posedness, Einstein-equation derivation by UET, Gravity compatibility, or global UET closure",
        },
        "scope": {
            "equation_class": "standard linearized-GR physical TT sector; not a new UET equation",
            "state_variables": ["h_plus", "h_cross", "Pi_plus", "Pi_cross", "G_plus", "G_cross"],
            "excluded_variables": ["UET C", "UET Phi", "UET Pi", "R_gen", "R_obs"],
            "domain": "finite one-dimensional slab [-1,1] with no periodic wraparound",
            "method": "Legendre-Gauss-Lobatto collocation with diagonal-norm SBP and weak SAT boundary penalties",
            "boundary_data": "homogeneous no-incoming TT characteristic data at both faces",
            "filtering": False,
            "clipping": False,
            "parameter_fitting": False,
            "full_rinne_cpbc_implemented": False,
            "periodic_gh_solver_modified": False,
        },
        "checks": checks,
        "metrics": {
            "sbp_order_grid": degree_checks,
            "maximum_sbp_identity_residual": max(sbp_residuals),
            "maximum_polynomial_derivative_residual": max(derivative_residuals),
            "semi_discrete_energy_rate": measured_energy_rate,
            "maximum_energy_identity_residual": energy_identity_residual,
            "initial_reduction_constraint_linf": initial_reduction_residual,
            "final_reduction_constraint_linf": final_reduction_residual,
            "left_final_reduction_constraint_linf": left_final_reduction_residual,
            "initial_incoming_left_characteristic_linf": incoming_left_initial,
            "initial_incoming_right_characteristic_linf": incoming_right_initial,
            "temporal_refinement_difference_ratio": temporal_convergence_ratio,
            "pulse_grid_order": order,
            "minimum_grid_spacing": minimum_spacing,
            "timestep_cap": timestep_cap,
            "pulse_final_time": final_time,
            "pulse_steps": pulse_steps,
            "pulse_dt": pulse_dt,
            "pulse_initial_energy": initial_energy,
            "pulse_final_energy": final_energy,
            "pulse_final_to_initial_energy_ratio": final_energy_ratio,
            "left_pulse_steps": left_pulse_steps,
            "left_pulse_dt": left_pulse_dt,
            "left_pulse_initial_energy": left_initial_energy,
            "left_pulse_final_energy": left_final_energy,
            "left_pulse_final_to_initial_energy_ratio": left_final_energy_ratio,
            "maximum_semidiscrete_eigenvalue_real_part": maximum_eigenvalue_real_part,
            "maximum_rk4_amplification_at_selected_dt": maximum_amplification,
        },
        "numerical_policy": {
            "integrator": "classical RK4",
            "timestep": "min(0.5 times minimum LGL spacing, 0.25 times the computed RK4 linear stability limit)",
            "energy_identity_tolerance": 2.0e-11,
            "constraint_tolerance": 2.0e-9,
            "absorption_ratio_threshold": 2.0e-6,
            "temporal_refinement_ratio_range": [10.0, 22.0],
            "random_seed_for_energy_identity_control": 20260925,
        },
        "literature_route_screen": [
            {
                "source_id": "rinne_2006_first_order_gh_radiation_controlling_cpbc",
                "url": "https://arxiv.org/html/gr-qc/0606053v2",
                "locators": ["Eqs. (9)-(11)", "Secs. 2.2-2.4", "Sec. 5.1"],
                "finding": "same first-order GH characteristic variables; differential constraint and Weyl boundary conditions; spectral implementation prescribes time derivatives of incoming characteristic fields",
                "route_role": "primary reference for the next full frozen-background GH CPBC implementation; this TT-only pilot does not reproduce that full system",
            },
            {
                "source_id": "dailey_schnetter_afshordi_2025_covariant_sbp_sat_gh",
                "url": "https://arxiv.org/html/2409.17970v2",
                "locators": ["Secs. II-III", "Sec. V.4"],
                "finding": "their SBP-SAT GH implementation requires critical changes to the evolved equations and chooses boundary data that can reflect constraint violations",
                "route_role": "useful discrete-method comparison, but not a drop-in realization of transparent Rinne differential CPBC for the current branch",
            },
        ],
        "source_hashes": source_hashes,
        "controlling_blocker": "full_first_order_gh_differential_cpbc_not_yet_applied_to_nonperiodic_evolution",
        "next_action": "extend the frozen-background slab pilot from the two physical TT modes to the full ten-component incoming u1-minus sector with separate constraint, Weyl, and gauge RHS conditions; then add positive-shift u2_A conditions and discrete subsidiary-constraint checks",
        "claim_boundary": "No full CPBC, nonlinear GH evolution, physical data validation, Gravity unlock, or UET theory promotion is claimed.",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "checks": artifact["checks"],
                "metrics": artifact["metrics"],
            },
            indent=2,
        )
    )
    return 0 if artifact["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
