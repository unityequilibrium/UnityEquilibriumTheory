"""Audit an algebraically reduced TT wave system with an energy-stable SAT."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_reduced_wave_sbp_sat_comparator.json"
)
AUDIT_SOURCE = Path(__file__).resolve()
TEST_SOURCE = ROOT / (
    "docs/core/05_tests/regression/root/"
    "test_uet_curved_3p1_gh_reduced_wave_sbp_sat.py"
)
TT_PILOT_SOURCE = ROOT / (
    "docs/scripts/audit/audit_curved_3p1_gh_tt_sbp_sat_boundary.py"
)
FULL_U1_AUDIT_SOURCE = ROOT / (
    "docs/scripts/audit/audit_curved_3p1_gh_full_u1_cpbc_slab.py"
)
FULL_U1_RHS_SOURCE = ROOT / (
    "docs/core/02_equations/covariant/"
    "uet_curved_3p1_gh_full_u1_slab.py"
)
_TT_SPEC = importlib.util.spec_from_file_location(
    "_uet_reduced_tt_sbp_reference", TT_PILOT_SOURCE
)
if _TT_SPEC is None or _TT_SPEC.loader is None:
    raise ImportError("cannot load the source-hashed TT SBP reference")
TT = importlib.util.module_from_spec(_TT_SPEC)
sys.modules[_TT_SPEC.name] = TT
_TT_SPEC.loader.exec_module(TT)
_FULL_U1_SPEC = importlib.util.spec_from_file_location(
    "_uet_reduced_tt_full_u1_reference", FULL_U1_AUDIT_SOURCE
)
if _FULL_U1_SPEC is None or _FULL_U1_SPEC.loader is None:
    raise ImportError("cannot load the source-hashed full-u1 audit reference")
FULL_U1 = importlib.util.module_from_spec(_FULL_U1_SPEC)
sys.modules[_FULL_U1_SPEC.name] = FULL_U1
_FULL_U1_SPEC.loader.exec_module(FULL_U1)


@dataclass(frozen=True)
class ReducedTTState:
    metric: np.ndarray
    momentum: np.ndarray


def reduced_tt_sbp_rhs(
    state: ReducedTTState, operators: Any
) -> ReducedTTState:
    """Evolve h and Pi, reconstructing G=D h algebraically."""

    metric = np.asarray(state.metric, dtype=float)
    momentum = np.asarray(state.momentum, dtype=float)
    expected = (2, operators.nodes.size)
    if metric.shape != expected or momentum.shape != expected:
        raise ValueError(f"metric and momentum must have shape {expected}")
    if not np.all(np.isfinite(metric)) or not np.all(np.isfinite(momentum)):
        raise ValueError("state fields must be finite")

    gradient = metric @ operators.derivative.T
    momentum_rhs = -(gradient @ operators.derivative.T)
    momentum_rhs[:, 0] -= (
        momentum[:, 0] + gradient[:, 0]
    ) / operators.norm_weights[0]
    momentum_rhs[:, -1] -= (
        momentum[:, -1] - gradient[:, -1]
    ) / operators.norm_weights[-1]
    return ReducedTTState(-momentum.copy(), momentum_rhs)


def _combine(
    state: ReducedTTState,
    terms: tuple[tuple[float, ReducedTTState], ...],
) -> ReducedTTState:
    metric = state.metric.copy()
    momentum = state.momentum.copy()
    for coefficient, term in terms:
        metric += coefficient * term.metric
        momentum += coefficient * term.momentum
    return ReducedTTState(metric, momentum)


def _rk4_step(
    state: ReducedTTState, operators: Any, dt: float
) -> ReducedTTState:
    rhs = lambda current: reduced_tt_sbp_rhs(current, operators)  # noqa: E731
    k1 = rhs(state)
    k2 = rhs(_combine(state, ((0.5 * dt, k1),)))
    k3 = rhs(_combine(state, ((0.5 * dt, k2),)))
    k4 = rhs(_combine(state, ((dt, k3),)))
    return _combine(
        state,
        (
            (dt / 6.0, k1),
            (dt / 3.0, k2),
            (dt / 3.0, k3),
            (dt / 6.0, k4),
        ),
    )


def evolve(
    initial: ReducedTTState,
    operators: Any,
    final_time: float,
    target_dt: float,
) -> tuple[ReducedTTState, int, float]:
    if not np.isfinite(final_time) or final_time <= 0.0:
        raise ValueError("final_time must be finite and positive")
    if not np.isfinite(target_dt) or target_dt <= 0.0:
        raise ValueError("target_dt must be finite and positive")
    steps = max(1, int(ceil(final_time / target_dt)))
    dt = final_time / steps
    state = ReducedTTState(initial.metric.copy(), initial.momentum.copy())
    for _ in range(steps):
        state = _rk4_step(state, operators, dt)
        if not np.all(np.isfinite(state.metric)) or not np.all(
            np.isfinite(state.momentum)
        ):
            raise RuntimeError("non-finite state encountered during evolution")
    return state, steps, dt


def _gradient(state: ReducedTTState, operators: Any) -> np.ndarray:
    return state.metric @ operators.derivative.T


def wave_energy(state: ReducedTTState, operators: Any) -> float:
    gradient = _gradient(state, operators)
    density = state.momentum**2 + gradient**2
    return float(0.5 * np.sum(density * operators.norm_weights[None, :]))


def _reduction_residual(state: ReducedTTState, operators: Any) -> float:
    reconstructed = _gradient(state, operators)
    return float(np.max(np.abs(reconstructed - state.metric @ operators.derivative.T)))


def _energy_identity_residual(
    state: ReducedTTState, operators: Any
) -> tuple[float, float, float, float]:
    rhs = reduced_tt_sbp_rhs(state, operators)
    gradient = _gradient(state, operators)
    gradient_rhs = rhs.metric @ operators.derivative.T
    measured = float(
        np.sum(
            operators.norm_weights[None, :]
            * (state.momentum * rhs.momentum + gradient * gradient_rhs)
        )
    )
    expected = -float(
        np.sum(state.momentum[:, 0] ** 2 + state.momentum[:, -1] ** 2)
    )
    count = operators.nodes.size
    boundary = np.zeros((count, count), dtype=float)
    boundary[0, 0] = -1.0
    boundary[-1, -1] = 1.0
    mass = np.diag(operators.norm_weights)
    sbp_defect = (
        mass @ operators.derivative
        + operators.derivative.T @ mass
        - boundary
    )
    defect_contribution = -float(
        np.sum(state.momentum * (gradient @ sbp_defect.T))
    )
    decomposition_residual = abs(measured - expected - defect_contribution)
    return (
        measured,
        abs(measured - expected),
        defect_contribution,
        decomposition_residual,
    )


def _second_order_matrix(operators: Any) -> np.ndarray:
    count = operators.nodes.size
    matrix = np.zeros((2 * count, 2 * count), dtype=float)
    for column in range(2 * count):
        metric = np.zeros((2, count), dtype=float)
        momentum = np.zeros_like(metric)
        if column < count:
            metric[0, column] = 1.0
        else:
            momentum[0, column - count] = 1.0
        rhs = reduced_tt_sbp_rhs(ReducedTTState(metric, momentum), operators)
        matrix[:, column] = np.concatenate(
            (rhs.metric[0], rhs.momentum[0])
        )
    return matrix


def _rk4_amplification(eigenvalues: np.ndarray, dt: float) -> float:
    z = float(dt) * eigenvalues
    polynomial = 1.0 + z + z**2 / 2.0 + z**3 / 6.0 + z**4 / 24.0
    return float(np.max(np.abs(polynomial)))


def _stable_rk4_step(eigenvalues: np.ndarray) -> float:
    if float(np.max(eigenvalues.real)) > 1.0e-10:
        raise RuntimeError("reduced SBP-SAT wave operator has a growing mode")
    scale = max(float(np.max(np.abs(eigenvalues))), 1.0)
    lower = 0.0
    upper = 1.0 / scale
    while _rk4_amplification(eigenvalues, upper) <= 1.0 + 1.0e-10:
        lower = upper
        upper *= 2.0
        if upper > 100.0 / scale:
            raise RuntimeError("failed to bracket RK4 stability limit")
    for _ in range(64):
        middle = 0.5 * (lower + upper)
        if _rk4_amplification(eigenvalues, middle) <= 1.0 + 1.0e-10:
            lower = middle
        else:
            upper = middle
    return 0.75 * lower


def _weighted_difference(
    first: ReducedTTState, second: ReducedTTState, operators: Any
) -> float:
    length = float(operators.nodes[-1] - operators.nodes[0])
    first_gradient = _gradient(first, operators)
    second_gradient = _gradient(second, operators)
    density = (first.metric - second.metric) ** 2
    density += length**2 * (first.momentum - second.momentum) ** 2
    density += length**2 * (first_gradient - second_gradient) ** 2
    return float(np.sqrt(np.sum(operators.norm_weights[None, :] * density)))


def _max_energy_growth_rate(
    derivative: np.ndarray, weights: np.ndarray, *, boundary_method: str
) -> float:
    """Largest dE/dt per unit energy for a one-polarization linear operator."""

    d_matrix = np.asarray(derivative, dtype=float)
    norm = np.asarray(weights, dtype=float)
    count = norm.size
    identity = np.eye(count)
    zero = np.zeros((count, count))
    second = d_matrix @ d_matrix
    if boundary_method == "strong_differentiated_target":
        metric_boundary = np.zeros((count, count))
        momentum_boundary = np.zeros((count, count))
        metric_boundary[0] = second[0]
        metric_boundary[-1] = second[-1]
        momentum_boundary[0] = d_matrix[0]
        momentum_boundary[-1] = -d_matrix[-1]
        acceleration_metric = -second + metric_boundary
        acceleration_momentum = momentum_boundary
    elif boundary_method == "incoming_characteristic_sat":
        metric_penalty = np.zeros((count, count))
        momentum_penalty = np.zeros((count, count))
        metric_penalty[0] = -d_matrix[0] / norm[0]
        metric_penalty[-1] = d_matrix[-1] / norm[-1]
        momentum_penalty[0, 0] = -1.0 / norm[0]
        momentum_penalty[-1, -1] = -1.0 / norm[-1]
        acceleration_metric = -second + metric_penalty
        acceleration_momentum = momentum_penalty
    else:
        raise ValueError("unknown energy-rate boundary method")

    operator = np.block(
        [
            [zero, -identity],
            [acceleration_metric, acceleration_momentum],
        ]
    )
    mass = np.diag(norm)
    energy = np.block(
        [
            [d_matrix.T @ mass @ d_matrix, zero],
            [zero, mass],
        ]
    )
    rate = 0.5 * (operator.T @ energy + energy @ operator)
    eigenvalues, eigenvectors = np.linalg.eigh(energy)
    cutoff = 1.0e-12 * max(float(np.max(eigenvalues)), 1.0)
    positive = eigenvalues > cutoff
    inverse_root = eigenvectors[:, positive] / np.sqrt(eigenvalues[positive])
    normalized_rate = inverse_root.T @ rate @ inverse_root
    return float(np.max(np.linalg.eigvalsh(normalized_rate)))


def _strong_boundary_screens() -> list[dict[str, float | int | str]]:
    screens: list[dict[str, float | int | str]] = []
    for degree in (8, 12, 18, 20):
        lgl = TT.legendre_lobatto_operators(degree)
        lgl_rate = _max_energy_growth_rate(
            lgl.derivative,
            lgl.norm_weights,
            boundary_method="strong_differentiated_target",
        )
        cheb = FULL_U1.chebyshev_lobatto_operators(degree)
        cheb_weights = FULL_U1._clenshaw_curtis_weights(degree)
        cheb_rate = _max_energy_growth_rate(
            cheb.derivative,
            cheb_weights,
            boundary_method="strong_differentiated_target",
        )
        screens.extend(
            (
                {
                    "degree": degree,
                    "grid": "Legendre-Gauss-Lobatto diagonal-norm SBP",
                    "maximum_energy_growth_rate": lgl_rate,
                },
                {
                    "degree": degree,
                    "grid": "Chebyshev-Lobatto with Clenshaw-Curtis energy norm",
                    "maximum_energy_growth_rate": cheb_rate,
                },
            )
        )
    return screens


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact() -> dict[str, Any]:
    order = 72
    final_time = 2.4
    operators = TT.legendre_lobatto_operators(order)
    rng = np.random.default_rng(20260925)
    random_state = ReducedTTState(
        rng.normal(size=(2, order + 1)),
        rng.normal(size=(2, order + 1)),
    )
    (
        energy_rate,
        energy_identity_residual,
        sbp_defect_contribution,
        energy_decomposition_residual,
    ) = _energy_identity_residual(random_state, operators)
    strong_boundary_screens = _strong_boundary_screens()

    first_order_initial = TT.gaussian_right_going_state(operators)
    right_initial = ReducedTTState(
        first_order_initial.displacement.copy(),
        first_order_initial.momentum.copy(),
    )
    left_first_order = TT.gaussian_left_going_state(operators)
    left_initial = ReducedTTState(
        left_first_order.displacement.copy(),
        left_first_order.momentum.copy(),
    )

    first_order_rhs = TT.tt_wave_rhs(first_order_initial, operators)
    reduced_rhs = reduced_tt_sbp_rhs(right_initial, operators)
    first_order_gradient_rhs = first_order_rhs.spatial_gradient
    reduced_gradient_rhs = reduced_rhs.metric @ operators.derivative.T
    rhs_equivalence_residual = max(
        float(np.max(np.abs(first_order_rhs.displacement - reduced_rhs.metric))),
        float(np.max(np.abs(first_order_rhs.momentum - reduced_rhs.momentum))),
        float(np.max(np.abs(first_order_gradient_rhs - reduced_gradient_rhs))),
    )

    matrix = _second_order_matrix(operators)
    eigenvalues = np.linalg.eigvals(matrix)
    stable_dt = _stable_rk4_step(eigenvalues)
    minimum_spacing = float(np.min(np.diff(operators.nodes)))
    timestep_cap = min(0.5 * minimum_spacing, 0.25 * stable_dt)

    convergence_time = 0.25
    convergence_runs = [
        evolve(right_initial, operators, convergence_time, timestep_cap / (4 * 2**r))[0]
        for r in range(3)
    ]
    differences = [
        _weighted_difference(
            convergence_runs[index], convergence_runs[index + 1], operators
        )
        for index in range(2)
    ]
    temporal_ratio = differences[0] / differences[1]

    right_final, right_steps, used_dt = evolve(
        right_initial, operators, final_time, timestep_cap
    )
    left_final, left_steps, left_dt = evolve(
        left_initial, operators, final_time, timestep_cap
    )
    right_energy_ratio = wave_energy(right_final, operators) / wave_energy(
        right_initial, operators
    )
    left_energy_ratio = wave_energy(left_final, operators) / wave_energy(
        left_initial, operators
    )
    maximum_amplification = _rk4_amplification(eigenvalues, used_dt)
    sbp_boundary = np.zeros((order + 1, order + 1))
    sbp_boundary[0, 0] = -1.0
    sbp_boundary[-1, -1] = 1.0
    sbp_residual = float(
        np.max(
            np.abs(
                operators.norm_weights[:, None] * operators.derivative
                + operators.derivative.T * operators.norm_weights[None, :]
                - sbp_boundary
            )
        )
    )
    maximum_sat_energy_growth_rate = _max_energy_growth_rate(
        operators.derivative,
        operators.norm_weights,
        boundary_method="incoming_characteristic_sat",
    )
    checks = {
        "lgl_diagonal_norm_satisfies_sbp_identity": sbp_residual <= 2.0e-12,
        "sat_energy_rate_matches_boundary_flux_plus_sbp_defect": energy_decomposition_residual
        <= 2.0e-11,
        "sat_energy_is_nonincreasing_for_all_states": maximum_sat_energy_growth_rate
        <= 2.0e-9,
        "second_order_rhs_matches_first_order_sat_on_reduction_subspace": rhs_equivalence_residual
        <= 2.0e-11,
        "current_strong_differentiated_target_is_not_energy_contractive_on_both_grids": all(
            row["maximum_energy_growth_rate"] > 1.0e-6
            for row in strong_boundary_screens
        ),
        "rk4_spectrum_has_no_resolved_growing_mode": float(
            np.max(eigenvalues.real)
        )
        <= 1.0e-10,
        "selected_timestep_is_rk4_stable": maximum_amplification
        <= 1.0 + 1.0e-10,
        "right_going_packet_is_absorbed": right_energy_ratio <= 2.0e-6,
        "left_going_packet_is_absorbed": left_energy_ratio <= 2.0e-6,
        "rk4_temporal_refinement_is_fourth_order": 10.0
        <= temporal_ratio
        <= 22.0,
        "algebraic_reduction_has_no_independent_gradient_state": not hasattr(
            right_final, "spatial_gradient"
        )
        and rhs_equivalence_residual <= 2.0e-11,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    local_sources = (
        AUDIT_SOURCE,
        TEST_SOURCE,
        TT_PILOT_SOURCE,
        FULL_U1_AUDIT_SOURCE,
        FULL_U1_RHS_SOURCE,
    )
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in local_sources
        if path.is_file()
    }
    checks["all_declared_local_sources_are_hashed"] = len(source_hashes) == len(
        local_sources
    )
    passed = all(checks.values())

    return {
        "schema_version": "core-curved-3p1-gh-reduced-tt-sbp-sat-v1",
        "artifact": "curved_3p1_gh_reduced_wave_sbp_sat_comparator",
        "diagnostic_id": "uet.core.curved_3p1.gh.reduced_tt_sbp_sat_energy_comparator",
        "generated_at": "2026-09-25",
        "status": "PASS_REDUCED_TT_SBP_SAT_COMPARATOR"
        if passed
        else "FAIL_REDUCED_TT_SBP_SAT_COMPARATOR",
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_REDUCED_TT_SBP_SAT_COMPARATOR",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
            "what_is_closed": [
                "the two standard linearized-GR TT polarizations admit a second-order state (h,Pi) with G=D(h) imposed algebraically",
                "on the LGL diagonal-norm SBP grid, the SAT scheme has the exact energy rate dE/dt=-sum_A(Pi_A,left^2+Pi_A,right^2)<=0",
                "the second-order RHS is algebraically identical to the existing first-order TT SBP-SAT RHS on G=D(h)",
                "right- and left-going Gaussian packets exit with a roundoff-scale energy remainder and RK4 temporal order is verified",
                "the current strong differentiated-target replacement has positive energy-growth directions under both tested LGL-SBP and Chebyshev/Clenshaw-Curtis norms",
            ]
            if passed
            else [],
            "what_remains_open": [
                "this is a physical TT-sector outgoing-wave control, not the full ten-component constraint/physical/gauge GH CPBC system",
                "the constraint and gauge projector sectors, positive-shift u2_A fields, tangential derivatives, corners, variable coefficients, and nonlinear terms remain open",
                "a SAT operator derived for all Rinne constraint/physical/gauge targets is still required before closing full-u1 GH evolution",
            ],
            "equation_or_mapping": {
                "state": "(h_A,Pi_A), A in {+,x}; G_A=D(h_A) is reconstructed algebraically",
                "evolution": "h_dot=-Pi; Pi_dot=-D G-H^-1 e_L*(Pi+G)_L-H^-1 e_R*(Pi-G)_R",
                "incoming_left": "a_L=Pi_L+G_L",
                "incoming_right": "a_R=Pi_R-G_R",
                "energy": "E=1/2 sum_A(Pi_A^T H Pi_A+G_A^T H G_A)",
                "energy_rate": "dE/dt=-sum_A(Pi_A,left^2+Pi_A,right^2)<=0",
                "relation_to_Rinne_physical_target": "for q_A=a_A-gamma2*h_A and homogeneous physical data, q_dot=gamma2*Pi implies a_dot=0; the SAT weakly penalizes a_A, and does not implement the full Rinne CPBC",
            },
            "units": {
                "unit_lane": "geometric c=1 with slab length scale L0=1",
                "h": "dimensionless",
                "Pi_and_G": "L0^-1",
                "UET_symbols_used": [],
            },
            "derivation_class": "standard linearized-GR TT wave equation plus an SBP-SAT semidiscrete energy identity",
            "observable": "discrete energy rate, incoming characteristic, packet remainder, reduction identity, and temporal convergence",
            "data_role": "analytic and synthetic numerical control; no external data, fitting, or holdout",
            "evidence_artifacts": [OUTPUT.relative_to(ROOT).as_posix()],
            "verification_status": "PASS_REDUCED_TT_SBP_SAT_COMPARATOR"
            if passed
            else "FAIL_REDUCED_TT_SBP_SAT_COMPARATOR",
            "open_blockers": [
                "full first-order GH CPBC energy estimate across constraint, physical, and gauge sectors",
                "positive-shift u2_A, tangential derivatives, corners, variable coefficients, and nonlinear boundary evolution",
            ],
            "dependency_unlocked": "none; the Core curved-3+1 parent remains PARTIAL and Gravity remains blocked",
            "claim_boundary": "a second-order reduced TT numerical lane only; not full GH CPBC, continuum well-posedness, Gravity compatibility, or UET closure",
        },
        "checks": checks,
        "metrics": {
            "order": order,
            "node_count": order + 1,
            "sbp_identity_residual": sbp_residual,
            "random_state_energy_rate": energy_rate,
            "random_state_expected_energy_rate": -float(
                np.sum(random_state.momentum[:, 0] ** 2 + random_state.momentum[:, -1] ** 2)
            ),
            "energy_identity_residual": energy_identity_residual,
            "sbp_defect_energy_contribution": sbp_defect_contribution,
            "energy_identity_decomposition_residual": energy_decomposition_residual,
            "maximum_sat_energy_growth_rate_per_unit_energy": maximum_sat_energy_growth_rate,
            "pointwise_strong_target_energy_growth_screens": strong_boundary_screens,
            "second_order_first_order_rhs_equivalence_residual": rhs_equivalence_residual,
            "maximum_semidiscrete_eigenvalue_real_part": float(
                np.max(eigenvalues.real)
            ),
            "stable_rk4_timestep_estimate": stable_dt,
            "selected_timestep_cap": timestep_cap,
            "selected_timestep_rk4_amplification": maximum_amplification,
            "right_packet_final_to_initial_energy_ratio": right_energy_ratio,
            "right_packet_steps": right_steps,
            "right_packet_dt": used_dt,
            "left_packet_final_to_initial_energy_ratio": left_energy_ratio,
            "left_packet_steps": left_steps,
            "left_packet_dt": left_dt,
            "temporal_refinement_difference_ratio": temporal_ratio,
            "temporal_refinement_differences": differences,
            "independent_spatial_gradient_state": False,
        },
        "scope": {
            "physics_lane": "standard linearized-GR transverse-traceless physical sector",
            "domain": "finite one-dimensional flat slab [-1,1]",
            "grid": "Legendre-Gauss-Lobatto diagonal-norm SBP",
            "full_first_order_gh_cpbc": False,
            "constraint_projector_evolved": False,
            "gauge_projector_evolved": False,
            "positive_shift_u2_A": False,
            "tangential_derivatives": False,
            "corners": False,
            "nonlinear_evolution": False,
            "parameter_fitting": False,
            "filtering": False,
            "clipping": False,
        },
        "numerical_policy": {
            "order": order,
            "final_time": final_time,
            "energy_identity_tolerance": 2.0e-11,
            "sbp_identity_tolerance": 2.0e-12,
            "packet_energy_ratio_threshold": 2.0e-6,
            "temporal_refinement_ratio_range": [10.0, 22.0],
            "pointwise_energy_growth_screen_floor": 1.0e-6,
            "random_seed": 20260925,
        },
        "source_hashes": source_hashes,
        "controlling_blocker": "full_first_order_gh_cpbc_not_energy_closed_across_constraint_physical_and_gauge_sectors",
        "next_action": "derive a projector-aware SBP-SAT penalty for all ten incoming u1-minus modes and prove its coupled constraint, Weyl, and gauge energy estimate before testing positive-shift u2_A or corners",
        "claim_boundary": "This closes only a standard-GR second-order reduced TT control. It does not close the full first-order GH boundary evolution, curved 3+1 parent, Gravity, or UET.",
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
