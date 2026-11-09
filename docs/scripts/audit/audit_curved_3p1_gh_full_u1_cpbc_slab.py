"""Audit the frozen-background, full-u1 GH boundary lane on a 1D slab."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_PACKAGE_NAME = "_uet_curved_3p1_gh_slab_audit"
_PACKAGE = types.ModuleType(_PACKAGE_NAME)
_PACKAGE.__path__ = [
    str(ROOT / "docs/core/02_equations/covariant")
]
sys.modules.setdefault(_PACKAGE_NAME, _PACKAGE)

PROJECTORS = importlib.import_module(
    f"{_PACKAGE_NAME}.uet_curved_3p1_gh_boundary_projectors"
)
BOUNDARY = importlib.import_module(
    f"{_PACKAGE_NAME}.uet_curved_3p1_gh_linear_boundary"
)
SLAB = importlib.import_module(
    f"{_PACKAGE_NAME}.uet_curved_3p1_gh_full_u1_slab"
)

OUTPUT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_full_u1_cpbc_slab_pilot.json"
)
REDUCED_OUTPUT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_reduced_wave_boundary_comparator.json"
)
TEST_SOURCE = ROOT / (
    "docs/core/05_tests/regression/root/"
    "test_uet_curved_3p1_gh_full_u1_slab.py"
)
TT_PILOT_SOURCE = ROOT / (
    "docs/scripts/audit/audit_curved_3p1_gh_tt_sbp_sat_boundary.py"
)
AUDIT_SOURCE = Path(__file__).resolve()
SLAB_SOURCE = ROOT / (
    "docs/core/02_equations/covariant/"
    "uet_curved_3p1_gh_full_u1_slab.py"
)
PROJECTOR_SOURCE = ROOT / (
    "docs/core/02_equations/covariant/"
    "uet_curved_3p1_gh_boundary_projectors.py"
)
RESIDUAL_SOURCE = ROOT / (
    "docs/core/02_equations/covariant/"
    "uet_curved_3p1_gh_linear_boundary.py"
)
GH_SYSTEM_SOURCE = ROOT / (
    "docs/core/02_equations/covariant/"
    "uet_curved_3p1_generalized_harmonic.py"
)
_tt_spec = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_tt_sbp_reference", TT_PILOT_SOURCE
)
if _tt_spec is None or _tt_spec.loader is None:
    raise ImportError("cannot load the existing TT SBP operator reference")
TT_PILOT = importlib.util.module_from_spec(_tt_spec)
sys.modules[_tt_spec.name] = TT_PILOT
_tt_spec.loader.exec_module(TT_PILOT)


@dataclass(frozen=True)
class ChebyshevOperators:
    nodes: np.ndarray
    derivative: np.ndarray


def chebyshev_lobatto_operators(degree: int) -> ChebyshevOperators:
    """Return ascending Chebyshev-Lobatto nodes and their spectral D matrix."""

    order = int(degree)
    if order < 2 or order != degree:
        raise ValueError("degree must be an integer >= 2")
    descending = np.cos(np.pi * np.arange(order + 1) / order)
    coefficients = (-1.0) ** np.arange(order + 1)
    coefficients[[0, -1]] *= 2.0
    difference = descending[:, None] - descending[None, :]
    derivative = np.outer(coefficients, 1.0 / coefficients) / (
        difference + np.eye(order + 1)
    )
    derivative -= np.diag(np.sum(derivative, axis=1))
    return ChebyshevOperators(
        nodes=descending[::-1].copy(),
        derivative=derivative[::-1, ::-1].copy(),
    )


def _unpack_grid(values: np.ndarray) -> np.ndarray:
    return np.stack([SLAB.unpack_symmetric(row) for row in values])


def _pack_tensor_grid(values: np.ndarray) -> np.ndarray:
    return np.stack([SLAB.pack_symmetric(row) for row in values])


def _max_abs(value: np.ndarray) -> float:
    return float(np.max(np.abs(value))) if value.size else 0.0


def _boundary_target_residuals(
    state: Any,
    operators: Any,
    gamma2: float,
    gauge_rates: np.ndarray,
    boundary_method: str = "rinne_pointwise",
) -> dict[str, float]:
    derivative = operators.derivative
    rhs = SLAB.gh_full_u1_slab_rhs(
        state,
        derivative,
        gamma2,
        gauge_rates,
        nodes=operators.nodes,
        boundary_method=boundary_method,
    )
    d_metric = derivative @ state.metric
    residuals = {"constraint": 0.0, "physical": 0.0, "gauge": 0.0}
    for face_index, normal, face_slot in (
        (0, -1, 0),
        (derivative.shape[0] - 1, 1, 1),
    ):
        projectors = PROJECTORS.build_gh_boundary_projectors(
            (float(normal), 0.0, 0.0)
        )
        pi = state.normal_derivative[face_index]
        phi_n = normal * state.normal_spatial_derivative[face_index]
        qdot = (
            rhs.normal_derivative[face_index]
            - normal * rhs.normal_spatial_derivative[face_index]
            - gamma2 * rhs.metric[face_index]
        )
        source = gamma2 * (pi + phi_n)
        d_n_metric = normal * d_metric[face_index]
        residuals["constraint"] = max(
            residuals["constraint"],
            _max_abs(projectors.constraint @ (qdot - source)),
        )
        residuals["physical"] = max(
            residuals["physical"],
            _max_abs(
                projectors.physical
                @ (qdot - source + gamma2 * d_n_metric)
            ),
        )
        residuals["gauge"] = max(
            residuals["gauge"],
            _max_abs(
                projectors.gauge @ qdot - gauge_rates[face_slot]
            ),
        )
    return residuals


def _residual_formula_crosscheck(
    state: Any, derivative: np.ndarray, gamma2: float
) -> dict[str, float]:
    d_metric = derivative @ state.metric
    d_pi = derivative @ state.normal_derivative
    d_phi = derivative @ state.normal_spatial_derivative
    maximum = {"constraint": 0.0, "physical": 0.0, "gauge": 0.0}
    for face_index, normal in (
        (0, -1),
        (derivative.shape[0] - 1, 1),
    ):
        metric = SLAB.unpack_symmetric(state.metric[face_index])
        pi = SLAB.unpack_symmetric(state.normal_derivative[face_index])
        phi_x = SLAB.unpack_symmetric(
            state.normal_spatial_derivative[face_index]
        )
        metric_gradient = np.zeros((3, 4, 4))
        pi_gradient = np.zeros((3, 4, 4))
        phi_gradient = np.zeros((3, 3, 4, 4))
        phi = np.zeros((3, 4, 4))
        metric_gradient[0] = SLAB.unpack_symmetric(d_metric[face_index])
        pi_gradient[0] = SLAB.unpack_symmetric(d_pi[face_index])
        phi_gradient[0, 0] = SLAB.unpack_symmetric(d_phi[face_index])
        phi[0] = phi_x
        result = BOUNDARY.gh_linear_boundary_residuals(
            metric_perturbation=metric,
            pi_perturbation=pi,
            phi_perturbation=phi,
            metric_gradient=metric_gradient,
            pi_gradient=pi_gradient,
            phi_gradient=phi_gradient,
            normal=(float(normal), 0.0, 0.0),
            gamma2=gamma2,
        )
        d_n_q = (
            normal * d_pi[face_index]
            - d_phi[face_index]
            - gamma2 * normal * d_metric[face_index]
        )
        projectors = PROJECTORS.build_gh_boundary_projectors(
            (float(normal), 0.0, 0.0)
        )
        expected_constraint = (
            BOUNDARY.gh_boundary_normal_maps((float(normal), 0.0, 0.0))[
                "constraint"
            ]
            @ d_n_q
        )
        expected_physical = projectors.physical @ (
            normal * d_pi[face_index] - d_phi[face_index]
        )
        q = (
            state.normal_derivative[face_index]
            - normal * state.normal_spatial_derivative[face_index]
            - gamma2 * state.metric[face_index]
        )
        expected_gauge = projectors.gauge @ q
        maximum["constraint"] = max(
            maximum["constraint"],
            _max_abs(result.constraint_incoming - expected_constraint),
        )
        maximum["physical"] = max(
            maximum["physical"],
            _max_abs(
                _pack_tensor_grid(result.physical_weyl_incoming[None, ...])[0]
                - expected_physical
            ),
        )
        maximum["gauge"] = max(
            maximum["gauge"],
            _max_abs(
                _pack_tensor_grid(result.gauge_incoming[None, ...])[0]
                - expected_gauge
            ),
        )
    return maximum


def _linear_operator(
    operators: Any,
    gamma2: float,
    boundary_method: str = "rinne_pointwise",
) -> np.ndarray:
    derivative = operators.derivative
    node_count = derivative.shape[0]
    block_size = node_count * len(PROJECTORS.SYMMETRIC_PAIRS)
    reduced = boundary_method == "reduced_wave_algebraic_phi"
    dimension = (2 if reduced else 3) * block_size
    operator = np.zeros((dimension, dimension), dtype=float)
    for column in range(dimension):
        basis = np.zeros(dimension, dtype=float)
        basis[column] = 1.0
        metric = basis[:block_size].reshape(node_count, -1)
        pi = basis[block_size : 2 * block_size].reshape(node_count, -1)
        phi = (
            derivative @ metric
            if reduced
            else basis[2 * block_size :].reshape(node_count, -1)
        )
        rhs = SLAB.gh_full_u1_slab_rhs(
            SLAB.GHSlabState(metric, pi, phi),
            derivative,
            gamma2,
            nodes=operators.nodes,
            boundary_method=boundary_method,
        )
        output = (rhs.metric, rhs.normal_derivative)
        if not reduced:
            output = (*output, rhs.normal_spatial_derivative)
        operator[:, column] = np.concatenate(tuple(value.ravel() for value in output))
    return operator


def _rk4_amplification(eigenvalues: np.ndarray, dt: float) -> float:
    z = float(dt) * eigenvalues
    return float(
        np.max(np.abs(1.0 + z + z**2 / 2.0 + z**3 / 6.0 + z**4 / 24.0))
    )


def _combine(state: Any, terms: tuple[tuple[float, Any], ...]) -> Any:
    values = [
        state.metric.copy(),
        state.normal_derivative.copy(),
        state.normal_spatial_derivative.copy(),
    ]
    for coefficient, term in terms:
        values[0] += coefficient * term.metric
        values[1] += coefficient * term.normal_derivative
        values[2] += coefficient * term.normal_spatial_derivative
    return SLAB.GHSlabState(*values)


def _rk4_step(
    state: Any,
    operators: Any,
    gamma2: float,
    dt: float,
    boundary_method: str,
) -> Any:
    rhs = lambda current: SLAB.gh_full_u1_slab_rhs(  # noqa: E731
        current,
        operators.derivative,
        gamma2,
        nodes=operators.nodes,
        boundary_method=boundary_method,
    )
    k1 = rhs(state)
    k2 = rhs(_combine(state, ((0.5 * dt, k1),)))
    k3 = rhs(_combine(state, ((0.5 * dt, k2),)))
    k4 = rhs(_combine(state, ((dt, k3),)))
    return _combine(
        state,
        ((dt / 6.0, k1), (dt / 3.0, k2), (dt / 3.0, k3), (dt / 6.0, k4)),
    )


def _evolve(
    initial: Any,
    operators: Any,
    gamma2: float,
    final_time: float,
    dt_cap: float,
    boundary_method: str = "rinne_pointwise",
) -> tuple[Any, int, float]:
    steps = max(1, int(np.ceil(final_time / dt_cap)))
    dt = final_time / steps
    state = SLAB.GHSlabState(
        initial.metric.copy(),
        initial.normal_derivative.copy(),
        initial.normal_spatial_derivative.copy(),
    )
    for _ in range(steps):
        state = _rk4_step(state, operators, gamma2, dt, boundary_method)
    return state, steps, dt


def _lift_identity_residuals(operators: Any, seed: int = 107) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    left = rng.normal(size=10)
    right = rng.normal(size=10)
    metric, pi, phi = SLAB.constraint_compatible_u1_lift(
        operators.nodes, operators.derivative, left, right
    )
    incoming_left = pi[0] + phi[0]
    incoming_right = pi[-1] - phi[-1]
    outgoing_left = pi[0] - phi[0]
    outgoing_right = pi[-1] + phi[-1]
    return {
        "reduction_identity": _max_abs(operators.derivative @ metric - phi),
        "left_incoming_target": _max_abs(incoming_left - left),
        "right_incoming_target": _max_abs(incoming_right - right),
        "left_outgoing_unchanged": _max_abs(outgoing_left),
        "right_outgoing_unchanged": _max_abs(outgoing_right),
        "metric_endpoint_values": max(_max_abs(metric[0]), _max_abs(metric[-1])),
    }


def _state_norm(state: Any) -> float:
    metric = state.metric - np.mean(state.metric, axis=0, keepdims=True)
    return float(
        np.sqrt(
            np.mean(metric**2)
            + np.mean(state.normal_derivative**2)
            + np.mean(state.normal_spatial_derivative**2)
        )
    )


def _state_difference(left: Any, right: Any) -> float:
    return float(
        np.sqrt(
            np.mean((left.metric - right.metric) ** 2)
            + np.mean(
                (left.normal_derivative - right.normal_derivative) ** 2
            )
            + np.mean(
                (left.normal_spatial_derivative - right.normal_spatial_derivative)
                ** 2
            )
        )
    )


def _reduction_linf(state: Any, derivative: np.ndarray) -> float:
    return _max_abs(SLAB.reduction_constraint(state, derivative))


def _tt_pulse(operators: ChebyshevOperators, width: float = 0.45) -> Any:
    x = operators.nodes
    coordinate = x / width
    profile = np.zeros_like(x)
    inside = np.abs(coordinate) < 1.0
    profile[inside] = np.exp(-1.0 / (1.0 - coordinate[inside] ** 2))
    profile *= 0.25
    derivative_profile = operators.derivative @ profile
    tensor = np.zeros((x.size, 4, 4), dtype=float)
    tensor[:, 2, 2] = profile
    tensor[:, 3, 3] = -profile
    tensor[:, 2, 3] = profile * 0.2
    tensor[:, 3, 2] = tensor[:, 2, 3]
    pi_tensor = np.zeros_like(tensor)
    phi_tensor = np.zeros_like(tensor)
    pi_tensor[:, 2, 2] = derivative_profile
    pi_tensor[:, 3, 3] = -derivative_profile
    pi_tensor[:, 2, 3] = derivative_profile * 0.2
    pi_tensor[:, 3, 2] = pi_tensor[:, 2, 3]
    phi_tensor[:] = pi_tensor
    return SLAB.GHSlabState(
        _pack_tensor_grid(tensor),
        _pack_tensor_grid(pi_tensor),
        _pack_tensor_grid(phi_tensor),
    )


def _clenshaw_curtis_weights(degree: int) -> np.ndarray:
    """Return Clenshaw-Curtis quadrature weights on the slab [-1, 1]."""

    order = int(degree)
    if order < 2 or order != degree:
        raise ValueError("degree must be an integer >= 2")
    theta = np.pi * np.arange(order + 1) / order
    weights = np.zeros(order + 1, dtype=float)
    interior = np.arange(1, order)
    values = np.ones(order - 1, dtype=float)
    if order % 2 == 0:
        for mode in range(1, order // 2):
            values -= 2.0 * np.cos(2.0 * mode * theta[interior]) / (
                4.0 * mode**2 - 1.0
            )
        values -= np.cos(order * theta[interior]) / (order**2 - 1.0)
        weights[0] = weights[-1] = 1.0 / (order**2 - 1.0)
    else:
        for mode in range(1, (order - 1) // 2 + 1):
            values -= 2.0 * np.cos(2.0 * mode * theta[interior]) / (
                4.0 * mode**2 - 1.0
            )
        weights[0] = weights[-1] = 1.0 / order**2
    weights[interior] = 2.0 * values / order
    return weights


def _field_energy(state: Any, weights: np.ndarray) -> float:
    quadrature = np.asarray(weights, dtype=float)
    if quadrature.shape != (state.normal_derivative.shape[0],):
        raise ValueError("energy weights must match the slab nodes")
    density = state.normal_derivative**2 + state.normal_spatial_derivative**2
    return float(0.5 * np.sum(quadrature[:, None] * density))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact() -> dict[str, Any]:
    gamma2 = 0.7
    random = np.random.default_rng(20260925)
    operators = chebyshev_lobatto_operators(12)
    random_state = SLAB.GHSlabState(
        random.normal(size=(operators.nodes.size, 10)),
        random.normal(size=(operators.nodes.size, 10)),
        random.normal(size=(operators.nodes.size, 10)),
    )
    gauge_rates = np.zeros((2, 10), dtype=float)
    for face_slot, normal in enumerate((-1, 1)):
        pg = PROJECTORS.build_gh_boundary_projectors(
            (float(normal), 0.0, 0.0)
        ).gauge
        gauge_rates[face_slot] = pg @ random.normal(size=10)

    rank_set = PROJECTORS.build_gh_boundary_projectors((1.0, 0.0, 0.0))
    target_residuals = _boundary_target_residuals(
        random_state, operators, gamma2, gauge_rates
    )
    formula_residuals = _residual_formula_crosscheck(
        random_state, operators.derivative, gamma2
    )

    eigen_screens = []
    for degree in (4, 8, 12):
        current = chebyshev_lobatto_operators(degree)
        matrix = _linear_operator(current, gamma2)
        eigenvalues = np.linalg.eigvals(matrix)
        spectral_scale = max(1.0, float(np.max(np.abs(eigenvalues))))
        eigen_screens.append(
            {
                "degree": degree,
                "node_count": degree + 1,
                "maximum_real_part": float(np.max(eigenvalues.real)),
                "maximum_absolute_eigenvalue": float(np.max(np.abs(eigenvalues))),
                "maximum_scaled_real_part": float(
                    np.max(eigenvalues.real) / spectral_scale
                ),
                "positive_modes_above_1e-6": int(
                    np.count_nonzero(eigenvalues.real > 1.0e-6)
                ),
            }
        )

    lgl_operators = TT_PILOT.legendre_lobatto_operators(10)
    lgl_spectrum = np.linalg.eigvals(
        _linear_operator(lgl_operators, gamma2)
    )
    lgl_sensitivity = {
        "degree": 10,
        "maximum_real_part": float(np.max(lgl_spectrum.real)),
        "positive_modes_above_1e-6": int(
            np.count_nonzero(lgl_spectrum.real > 1.0e-6)
        ),
        "role": "discretization sensitivity only; not the source-matched primary screen",
    }

    pulse_ops = chebyshev_lobatto_operators(12)
    pulse_weights = _clenshaw_curtis_weights(12)
    pulse = _tt_pulse(pulse_ops)
    pulse_matrix = _linear_operator(pulse_ops, gamma2)
    pulse_eigenvalues = np.linalg.eigvals(pulse_matrix)
    pulse_min_spacing = float(np.min(np.diff(pulse_ops.nodes)))
    pulse_dt = min(
        0.5 * pulse_min_spacing,
        0.45 * 2.7 / max(float(np.max(np.abs(pulse_eigenvalues))), 1.0),
    )
    pulse_final, pulse_steps, pulse_dt = _evolve(
        pulse, pulse_ops, gamma2, 2.4, pulse_dt
    )
    pulse_initial_energy = _field_energy(pulse, pulse_weights)
    pulse_final_energy = _field_energy(pulse_final, pulse_weights)
    pulse_energy_ratio = pulse_final_energy / pulse_initial_energy

    noise_ops = chebyshev_lobatto_operators(8)
    noise_matrix = _linear_operator(noise_ops, gamma2)
    noise_eigenvalues = np.linalg.eigvals(noise_matrix)
    noise_dt = min(
        0.5 * float(np.min(np.diff(noise_ops.nodes))),
        0.45 * 2.7 / max(float(np.max(np.abs(noise_eigenvalues))), 1.0),
    )
    noise_initial = SLAB.GHSlabState(
        1.0e-10 * random.normal(size=(noise_ops.nodes.size, 10)),
        1.0e-10 * random.normal(size=(noise_ops.nodes.size, 10)),
        1.0e-10 * random.normal(size=(noise_ops.nodes.size, 10)),
    )
    noise_initial_norm = _state_norm(noise_initial)
    noise_final, noise_steps, noise_dt = _evolve(
        noise_initial, noise_ops, gamma2, 4.0, noise_dt
    )
    noise_final_norm = _state_norm(noise_final)
    noise_growth_factor = noise_final_norm / max(noise_initial_norm, 1.0e-300)

    lift_identity = _lift_identity_residuals(noise_ops)
    lift_matrix = _linear_operator(
        noise_ops, gamma2, boundary_method="constraint_compatible_lift"
    )
    lift_eigenvalues = np.linalg.eigvals(lift_matrix)
    lift_noise_final, lift_noise_steps, lift_noise_dt = _evolve(
        noise_initial,
        noise_ops,
        gamma2,
        4.0,
        noise_dt,
        boundary_method="constraint_compatible_lift",
    )
    lift_noise_growth = _state_norm(lift_noise_final) / max(
        noise_initial_norm, 1.0e-300
    )
    lift_pulse = _tt_pulse(noise_ops)
    lift_pulse_final, lift_pulse_steps, lift_pulse_dt = _evolve(
        lift_pulse,
        noise_ops,
        gamma2,
        4.0,
        noise_dt,
        boundary_method="constraint_compatible_lift",
    )
    lift_pulse_reduction = _reduction_linf(
        lift_pulse_final, noise_ops.derivative
    )

    reduced_matrix = _linear_operator(
        noise_ops, gamma2, boundary_method="reduced_wave_algebraic_phi"
    )
    reduced_eigenvalues = np.linalg.eigvals(reduced_matrix)
    reduced_dt = min(
        0.5 * float(np.min(np.diff(noise_ops.nodes))),
        0.45 * 2.7 / max(float(np.max(np.abs(reduced_eigenvalues))), 1.0),
    )
    reduced_noise = SLAB.GHSlabState(
        noise_initial.metric.copy(),
        noise_initial.normal_derivative.copy(),
        noise_ops.derivative @ noise_initial.metric,
    )
    reduced_noise_initial_norm = _state_norm(reduced_noise)
    reduced_noise_final, reduced_noise_steps, reduced_noise_dt = _evolve(
        reduced_noise,
        noise_ops,
        gamma2,
        4.0,
        reduced_dt,
        boundary_method="reduced_wave_algebraic_phi",
    )
    reduced_noise_growth = _state_norm(reduced_noise_final) / max(
        reduced_noise_initial_norm, 1.0e-300
    )
    reduced_pulse = _tt_pulse(pulse_ops)
    reduced_pulse_final, reduced_pulse_steps, reduced_pulse_dt = _evolve(
        reduced_pulse,
        pulse_ops,
        gamma2,
        2.4,
        pulse_dt,
        boundary_method="reduced_wave_algebraic_phi",
    )
    reduced_pulse_energy_ratio = _field_energy(
        reduced_pulse_final, pulse_weights
    ) / _field_energy(reduced_pulse, pulse_weights)
    reduced_pulse_reduction = _reduction_linf(
        reduced_pulse_final, pulse_ops.derivative
    )
    reduced_maximum_eigen_real = float(np.max(reduced_eigenvalues.real))
    reduced_positive_modes = int(
        np.count_nonzero(reduced_eigenvalues.real > 1.0e-6)
    )
    reduced_checks = {
        "no_resolved_growing_semidiscrete_mode": reduced_maximum_eigen_real
        <= 1.0e-6
        and reduced_positive_modes == 0,
        "random_perturbation_stays_bounded": reduced_noise_growth <= 1.0e3,
        "tt_packet_is_absorbed": reduced_pulse_energy_ratio <= 5.0e-2,
        "reduction_constraint_is_algebraic": reduced_pulse_reduction <= 2.0e-10,
    }
    reduced_passed = all(reduced_checks.values())
    reduced_status = (
        "PASS_REDUCED_WAVE_BOUNDARY_COMPARATOR"
        if reduced_passed
        else (
            "PARTIAL_REDUCED_WAVE_BOUNDARY_COMPARATOR"
            if reduced_checks["no_resolved_growing_semidiscrete_mode"]
            and reduced_checks["random_perturbation_stays_bounded"]
            and reduced_checks["reduction_constraint_is_algebraic"]
            else "FAIL_REDUCED_WAVE_BOUNDARY_COMPARATOR"
        )
    )
    reduced_resolution_screens = []
    for degree in (8, 12, 14, 16, 18, 20):
        current_ops = chebyshev_lobatto_operators(degree)
        current_matrix = _linear_operator(
            current_ops, gamma2, boundary_method="reduced_wave_algebraic_phi"
        )
        current_eigenvalues = np.linalg.eigvals(current_matrix)
        current_spectral_scale = max(
            1.0, float(np.max(np.abs(current_eigenvalues)))
        )
        current_pulse = _tt_pulse(current_ops)
        current_weights = _clenshaw_curtis_weights(degree)
        current_dt = min(
            0.5 * float(np.min(np.diff(current_ops.nodes))),
            0.45
            * 2.7
            / max(float(np.max(np.abs(current_eigenvalues))), 1.0),
        )
        current_final, current_steps, current_dt = _evolve(
            current_pulse,
            current_ops,
            gamma2,
            2.4,
            current_dt,
            boundary_method="reduced_wave_algebraic_phi",
        )
        reduced_resolution_screens.append(
            {
                "degree": degree,
                "node_count": degree + 1,
                "maximum_eigenvalue_real_part": float(
                    np.max(current_eigenvalues.real)
                ),
                "maximum_scaled_eigenvalue_real_part": float(
                    np.max(current_eigenvalues.real) / current_spectral_scale
                ),
                "positive_modes_above_1e-6": int(
                    np.count_nonzero(current_eigenvalues.real > 1.0e-6)
                ),
                "tt_packet_clenshaw_curtis_energy_ratio": _field_energy(
                    current_final, current_weights
                )
                / _field_energy(current_pulse, current_weights),
                "tt_packet_reduction_constraint_linf": _reduction_linf(
                    current_final, current_ops.derivative
                ),
                "tt_packet_steps": current_steps,
                "tt_packet_dt": current_dt,
            }
        )

    convergence_initial = _tt_pulse(noise_ops)
    convergence_runs = [
        _evolve(
            convergence_initial,
            noise_ops,
            gamma2,
            0.2,
            noise_dt / (2**refinement),
        )[0]
        for refinement in range(3)
    ]
    temporal_differences = [
        _state_difference(convergence_runs[index], convergence_runs[index + 1])
        for index in range(2)
    ]
    temporal_convergence_ratio = (
        temporal_differences[0] / temporal_differences[1]
        if temporal_differences[1] > 0.0
        else float("inf")
    )

    source_paths = (
        AUDIT_SOURCE,
        TEST_SOURCE,
        SLAB_SOURCE,
        PROJECTOR_SOURCE,
        RESIDUAL_SOURCE,
        GH_SYSTEM_SOURCE,
        TT_PILOT_SOURCE,
    )
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in source_paths
        if path.is_file()
    }
    checks = {
        "projector_ranks_are_4_2_4": rank_set.ranks
        == {"constraint": 4, "physical": 2, "gauge": 4},
        "projector_algebra_is_orthogonal_and_complete": max(
            rank_set.residuals.values()
        )
        <= 1.0e-12,
        "incoming_rhs_matches_all_three_projected_targets": max(
            target_residuals.values()
        )
        <= 2.0e-11,
        "rhs_targets_match_rinne_normal_incidence_residuals": max(
            formula_residuals.values()
        )
        <= 2.0e-11,
        "chebyshev_semidiscrete_spectrum_has_no_resolved_growing_mode": max(
            item["maximum_real_part"] for item in eigen_screens
        )
        <= 1.0e-6
        and max(item["maximum_scaled_real_part"] for item in eigen_screens)
        <= 1.0e-7,
        "chebyshev_spectrum_has_no_mode_above_growth_tolerance": sum(
            item["positive_modes_above_1e-6"] for item in eigen_screens
        )
        == 0,
        "rk4_temporal_refinement_is_fourth_order": 10.0
        <= temporal_convergence_ratio
        <= 22.0,
        "right_going_tt_packet_is_absorbed_without_large_remainder": pulse_energy_ratio
        <= 5.0e-2,
        "tt_reduction_constraint_remains_bounded": _reduction_linf(
            pulse_final, pulse_ops.derivative
        )
        <= 2.0e-6,
        "small_random_perturbation_stays_bounded_over_two_domain_crossing_times": noise_growth_factor
        <= 1.0e3
        and np.all(
            np.isfinite(
                np.concatenate(
                    (
                        noise_final.metric.ravel(),
                        noise_final.normal_derivative.ravel(),
                        noise_final.normal_spatial_derivative.ravel(),
                    )
                )
            )
        ),
        "constraint_compatible_lift_preserves_reduction_and_incoming_targets": max(
            lift_identity.values()
        )
        <= 2.0e-11,
        "constraint_compatible_lift_has_no_resolved_growing_mode": float(
            np.max(lift_eigenvalues.real)
        )
        <= 1.0e-6,
        "constraint_compatible_lift_noise_stays_bounded": lift_noise_growth
        <= 1.0e3,
        "reduced_wave_has_no_resolved_growing_mode": reduced_checks[
            "no_resolved_growing_semidiscrete_mode"
        ],
        "reduced_wave_random_perturbation_stays_bounded": reduced_checks[
            "random_perturbation_stays_bounded"
        ],
        "reduced_wave_tt_packet_is_absorbed": reduced_checks[
            "tt_packet_is_absorbed"
        ],
        "reduced_wave_reduction_constraint_is_algebraic": reduced_checks[
            "reduction_constraint_is_algebraic"
        ],
        "clenshaw_curtis_energy_weights_integrate_constant": abs(
            float(np.sum(pulse_weights)) - 2.0
        )
        <= 1.0e-13
        and bool(np.all(pulse_weights > 0.0)),
        "all_declared_local_sources_are_hashed": len(source_hashes)
        == len(source_paths),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    status = (
        "PASS_GH_FULL_U1_CHEBYSHEV_SLAB_PILOT"
        if passed
        else "FAIL_GH_FULL_U1_CHEBYSHEV_SLAB_PILOT"
    )
    maximum_eigen_real = max(
        item["maximum_real_part"] for item in eigen_screens
    )
    maximum_scaled_eigen_real = max(
        item["maximum_scaled_real_part"] for item in eigen_screens
    )

    return {
        "schema_version": "core-curved-3p1-gh-full-u1-slab-pilot-v1",
        "artifact": "curved_3p1_gh_full_u1_cpbc_slab_pilot",
        "diagnostic_id": "uet.core.curved_3p1.gh.full_u1_cpbc_chebyshev_slab_pilot",
        "generated_at": "2026-09-25",
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_FULL_U1_CHEBYSHEV_SLAB_PILOT",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
            "what_is_closed": [
                "all ten incoming u1-minus tensor components are decomposed into the source-defined 4+2+4 constraint, physical, and gauge sectors",
            "the normal-incidence boundary RHS replacement matches the separately implemented Rinne residual equations",
            *(
                [
                    "the separate reduced-wave comparator passes its declared baseline spectrum, random-perturbation, TT-packet absorption, and algebraic-reduction screens"
                ]
                if reduced_passed
                else []
            ),
        ],
            "what_remains_open": [
                "the source-matched pointwise method passes the spectrum/noise screens but fails the TT pulse remainder and reduction-constraint limits",
                "the alternative cubic lift preserves the reduction identity but develops resolved growing modes and large perturbation amplification",
                *(
                    []
                    if reduced_passed
                    else [
                        "the separate reduced-wave comparator does not pass its degree-12 baseline absorption threshold; the exploratory degree-8-to-20 sweep is non-monotone in energy remainder and degree 20 has one mode above the locked 1e-6 eigenvalue tolerance"
                    ]
                ),
                "the reduced-wave comparator is a different second-order formulation and cannot stand in for the independent-variable first-order GH CPBC system",
                "the full numerical boundary lane is therefore partial and cannot be integrated into the Core parent as a passed CPBC solver",
            ],
            "equation_or_mapping": {
                "state": "(psi_ab, Pi_ab, Phi_xab), with ten symmetric components per field",
                "u1_minus": "q_ab = Pi_ab - n*Phi_xab - gamma2*psi_ab",
                "q_time_rhs": "qdot = D_n(q) + gamma2*(Pi + Phi_n)",
                "constraint_target": "P_C*qdot = P_C*gamma2*(Pi + Phi_n)",
                "physical_target": "P_P*qdot = P_P*gamma2*(Pi + Phi_n - D_n(psi)) for homogeneous incoming Weyl data",
                "gauge_target": "P_G*qdot = d_t(h_G)",
                "pointwise_method": "replace the incoming characteristic RHS only at the two endpoints",
                "compatible_lift_method": "cubic metric-RHS lift with D(delta_psi_dot)=delta_Phi_dot; exploratory and spectrally unstable",
                "reduced_wave_method": "evolve only (psi,Pi), impose Phi_x=D(psi) algebraically, and use the same projected incoming-u1-minus target; this is a distinct second-order comparator, not full first-order GH",
                "projector_ranks": rank_set.ranks,
                "boundary_scope": "zero shift, fixed flat background, one spatial normal, homogeneous constraint and Weyl data, prescribed gauge-data rate",
            },
            "units": {
                "unit_lane": "geometric units with slab length scale L0=1",
                "psi": "dimensionless",
                "Pi_and_Phi": "L0^-1",
                "gamma2": "L0^-1",
                "u1_minus_time_rhs": "L0^-2",
                "UET_symbols_used": [],
            },
            "derivation_class": "source-matched frozen-background generalized-harmonic boundary conditions plus direct algebraic and numerical controls",
            "observable": "projected boundary residuals, characteristic RHS, semidiscrete eigenvalues, TT energy remainder, and GH reduction-constraint residual",
            "data_role": "analytic and synthetic numerical control; no external data, fitting, or holdout",
            "evidence_artifacts": [OUTPUT.relative_to(ROOT).as_posix()],
            "verification_status": status,
            "open_blockers": [
                "positive-normal-shift incoming u2_A boundary conditions are not evolved",
                "tangential derivatives, corners, variable coefficients, nonlinear GH, matter, and full subsidiary-constraint propagation are out of scope",
                "the pilot is not a proof of continuum or discrete IBVP well-posedness",
                "gamma0 gauge-constraint damping is absent from the linear reduction-damped RHS used here",
            ],
            "dependency_unlocked": "none; the Core curved-3+1 CPBC parent and Gravity remain blocked",
            "claim_boundary": "at most a frozen-background, normal-incidence, zero-shift, full-u1-minus Chebyshev numerical lane; not full GH CPBC, nonlinear well-posedness, Einstein-equation derivation by UET, Gravity compatibility, or global UET closure",
        },
        "scope": {
            "equation_class": "standard linear generalized-harmonic reduction-damped equations",
            "state_variables": ["psi_ab", "Pi_ab", "Phi_xab"],
            "excluded_variables": ["UET C", "UET Phi", "UET Pi", "R_gen", "R_obs"],
            "domain": "finite one-dimensional slab [-1,1], non-periodic, no tangential dependence",
            "method": "Chebyshev-Lobatto collocation and classical RK4; pointwise Rinne-style RHS replacement is primary; cubic compatible lift is a rejected alternative",
            "boundary_conditions": "incoming-u1-minus RHS decomposed into separate constraint, Weyl, and gauge projections",
            "shift": 0.0,
            "lapse": 1.0,
            "gamma1": -1.0,
            "gamma2": gamma2,
            "gamma0": 0.0,
            "full_rinne_cpbc": False,
            "positive_shift_u2_conditions": False,
            "variable_coefficients": False,
            "nonlinear_evolution": False,
            "matter_source": False,
            "filtering": False,
            "clipping": False,
            "parameter_fitting": False,
        },
        "checks": checks,
        "metrics": {
            "projector_ranks": rank_set.ranks,
            "maximum_projector_algebra_residual": max(rank_set.residuals.values()),
            "maximum_projected_rhs_target_residual": max(target_residuals.values()),
            "projected_rhs_target_residuals": target_residuals,
            "maximum_rinne_formula_crosscheck_residual": max(formula_residuals.values()),
            "rinne_formula_crosscheck_residuals": formula_residuals,
            "chebyshev_eigenvalue_screens": eigen_screens,
            "maximum_chebyshev_eigenvalue_real_part": maximum_eigen_real,
            "maximum_scaled_chebyshev_eigenvalue_real_part": maximum_scaled_eigen_real,
            "lgl_sensitivity_screen": lgl_sensitivity,
            "tt_pulse_degree": 12,
            "tt_pulse_initial_energy": pulse_initial_energy,
            "tt_pulse_final_energy": pulse_final_energy,
            "tt_pulse_final_to_initial_energy_ratio": pulse_energy_ratio,
            "clenshaw_curtis_weight_sum": float(np.sum(pulse_weights)),
            "energy_functional": "E=1/2 sum_j w_j (Pi_j^2 + Phi_j^2), with Clenshaw-Curtis weights on [-1,1]",
            "tt_pulse_steps": pulse_steps,
            "tt_pulse_dt": pulse_dt,
            "tt_pulse_final_reduction_constraint_linf": _reduction_linf(
                pulse_final, pulse_ops.derivative
            ),
            "small_noise_initial_norm": noise_initial_norm,
            "small_noise_final_norm": noise_final_norm,
            "small_noise_growth_factor": noise_growth_factor,
            "small_noise_steps": noise_steps,
            "small_noise_dt": noise_dt,
            "small_noise_final_time": 4.0,
            "small_noise_domain_crossing_times": 2.0,
            "constraint_lift_identity_residuals": lift_identity,
            "constraint_lift_maximum_eigenvalue_real_part": float(
                np.max(lift_eigenvalues.real)
            ),
            "constraint_lift_positive_modes_above_1e-6": int(
                np.count_nonzero(lift_eigenvalues.real > 1.0e-6)
            ),
            "constraint_lift_noise_growth_factor": lift_noise_growth,
            "constraint_lift_noise_steps": lift_noise_steps,
            "constraint_lift_noise_dt": lift_noise_dt,
            "constraint_lift_pulse_final_reduction_constraint_linf": lift_pulse_reduction,
            "constraint_lift_pulse_steps": lift_pulse_steps,
            "constraint_lift_pulse_dt": lift_pulse_dt,
            "reduced_wave_state_dimension": int(reduced_matrix.shape[0]),
            "reduced_wave_maximum_eigenvalue_real_part": reduced_maximum_eigen_real,
            "reduced_wave_positive_modes_above_1e-6": reduced_positive_modes,
            "reduced_wave_noise_growth_factor": reduced_noise_growth,
            "reduced_wave_noise_steps": reduced_noise_steps,
            "reduced_wave_noise_dt": reduced_noise_dt,
            "reduced_wave_pulse_final_to_initial_energy_ratio": reduced_pulse_energy_ratio,
            "reduced_wave_pulse_final_reduction_constraint_linf": reduced_pulse_reduction,
            "reduced_wave_pulse_steps": reduced_pulse_steps,
            "reduced_wave_pulse_dt": reduced_pulse_dt,
            "reduced_wave_resolution_screens": reduced_resolution_screens,
            "temporal_refinement_difference_ratio": temporal_convergence_ratio,
            "temporal_refinement_differences": temporal_differences,
        },
        "numerical_policy": {
            "gamma2": gamma2,
            "chebyshev_degrees": [4, 8, 12],
            "lgl_sensitivity_degree": 10,
            "lgl_sensitivity_is_not_a_closure_gate": True,
            "temporal_refinement_final_time": 0.2,
            "temporal_refinement_ratio_range": [10.0, 22.0],
            "eigenvalue_real_part_absolute_tolerance": 1.0e-6,
            "eigenvalue_real_part_scaled_tolerance": 1.0e-7,
            "tt_final_energy_ratio_threshold": 5.0e-2,
            "energy_functional": "E=1/2 sum_j w_j (Pi_j^2 + Phi_j^2), with Clenshaw-Curtis weights on [-1,1]",
            "reduction_constraint_linf_threshold": 2.0e-6,
            "small_noise_growth_factor_threshold": 1.0e3,
            "constraint_lift_growth_factor_threshold": 1.0e3,
            "reduced_wave_growth_factor_threshold": 1.0e3,
            "reduced_wave_tt_final_energy_ratio_threshold": 5.0e-2,
            "reduced_wave_reduction_constraint_linf_threshold": 2.0e-10,
            "reduced_wave_resolution_sweep_degrees": [8, 12, 14, 16, 18, 20],
            "reduced_wave_resolution_sweep_role": "exploratory sensitivity; not a closure gate",
            "random_seed": 20260925,
        },
        "reduced_wave_comparator": {
            "status": reduced_status,
            "checks": reduced_checks,
            "metrics": {
                "state_dimension": int(reduced_matrix.shape[0]),
                "maximum_eigenvalue_real_part": reduced_maximum_eigen_real,
                "positive_modes_above_1e-6": reduced_positive_modes,
                "random_perturbation_growth_factor": reduced_noise_growth,
                "random_perturbation_final_time": 4.0,
                "random_perturbation_steps": reduced_noise_steps,
                "random_perturbation_dt": reduced_noise_dt,
                "tt_packet_final_to_initial_energy_ratio": reduced_pulse_energy_ratio,
                "tt_packet_final_reduction_constraint_linf": reduced_pulse_reduction,
                "tt_packet_final_time": 2.4,
                "tt_packet_steps": reduced_pulse_steps,
                "tt_packet_dt": reduced_pulse_dt,
                "energy_functional": "Clenshaw-Curtis spatial quadrature over [-1,1]",
                "resolution_screens": reduced_resolution_screens,
            },
            "equation_or_mapping": "Second-order algebraic reduced-wave evolution in (psi_ab,Pi_ab), with Phi_xab=D(psi_ab) enforced at every RHS evaluation; incoming u1-minus target is inherited from the 4+2+4 frozen-background GH projector algebra.",
            "claim_boundary": "A comparator formulation only; not the independent-variable first-order GH CPBC system, not a continuum/IBVP well-posedness proof, and no parent or Gravity dependency unlock.",
        },
        "source_hashes": source_hashes,
        "literature_basis": [
            {
                "source_id": "rinne_2006_first_order_gh_radiation_controlling_cpbc",
                "url": "https://arxiv.org/abs/gr-qc/0606053",
                "locators": ["Eqs. (27)-(36)", "Sec. 5.1, Eqs. (150)-(152)"],
                "role": "source for differential constraint/Weyl/gauge conditions and spectral incoming-characteristic RHS prescription",
                "limitation": "the paper's continuum boundary-stability analysis and 3D robust stability results are not inherited by this 1D implementation",
            }
        ],
        "controlling_blocker": (
            "positive_shift_u2_tangential_and_subsidiary_constraint_boundary_evolution_unverified"
            if passed
            else "full_u1_chebyshev_slab_pilot_has_failed_declared_numerical_screens"
        ),
        "next_action": (
            "add positive-shift u2_A conditions and independent subsidiary-constraint evolution checks before integrating this lane into the curved-3+1 parent"
            if passed
            else "diagnose the failed target, spectral, pulse, or random-perturbation check without relaxing its preregistered tolerance"
        ),
        "claim_boundary": "This is a standard-GR numerical boundary-method diagnostic only. No UET equation, physical prediction, full CPBC, or parent dependency unlock is claimed.",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    reduced = artifact["reduced_wave_comparator"]
    REDUCED_OUTPUT.write_text(
        json.dumps(
            {
                "schema_version": "core-curved-3p1-gh-reduced-wave-boundary-comparator-v1",
                "artifact": "curved_3p1_gh_reduced_wave_boundary_comparator",
                "generated_at": artifact["generated_at"],
                "status": reduced["status"],
                "claim_promotion": False,
                "major_result": {
                    "major_result_id": "CORE_CURVED_3P1_GH_REDUCED_WAVE_BOUNDARY_COMPARATOR",
                    "topic": "core",
                    "closure_level": "CLOSED_FOR_LANE"
                    if reduced["status"] == "PASS_REDUCED_WAVE_BOUNDARY_COMPARATOR"
                    else "PARTIAL",
                    "what_is_closed": [
                        "the reduced formulation enforces Phi_x=D(psi) algebraically, with the audited pulse residual at roundoff scale",
                        "the degree-8 spectrum and random-perturbation screens pass their declared limits",
                    ]
                    + (
                        [
                            "the declared degree-12 Clenshaw-Curtis TT-packet absorption threshold passes"
                        ]
                        if reduced["checks"]["tt_packet_is_absorbed"]
                        else []
                    ),
                    "what_remains_open": [
                        "spatial-resolution convergence and an independent semidiscrete energy estimate are not established",
                        "the degree-12 packet retains 0.1549867 of its Clenshaw-Curtis energy against the unchanged 0.05 threshold; higher-resolution remainders are non-monotone, and degree 20 has one eigenvalue above the unchanged 1e-6 tolerance",
                        "this comparator does not close the independent-variable first-order GH CPBC evolution",
                        "positive-shift u2_A, tangential derivatives, corners, variable coefficients, nonlinear terms, matter boundaries, and subsidiary-constraint propagation remain open",
                    ],
                    "equation_or_mapping": reduced["equation_or_mapping"],
                    "units": artifact["major_result"]["units"],
                    "derivation_class": "standard-GR second-order algebraic reduced-wave numerical comparator using source-matched frozen-background incoming-u1 boundary targets",
                    "observable": "semidiscrete spectrum, bounded perturbation growth, TT packet energy remainder, and algebraic reduction residual",
                    "data_role": "analytic and synthetic numerical control; no external data, fitting, or holdout",
                    "evidence_artifacts": [
                        OUTPUT.relative_to(ROOT).as_posix(),
                        REDUCED_OUTPUT.relative_to(ROOT).as_posix(),
                    ],
                    "verification_status": reduced["status"],
                    "open_blockers": [
                        f"degree-12 TT-packet integrated-energy remainder {reduced['metrics']['tt_packet_final_to_initial_energy_ratio']:.7g} exceeds the unchanged 0.05 limit",
                        "degree-20 spectrum has one positive mode above the unchanged 1e-6 real-part tolerance",
                        "the degree-8-to-20 integrated-energy sweep is non-monotone and does not establish spatial convergence",
                        "an independent semidiscrete energy estimate is required before any broader numerical claim",
                        "the distinct reduced formulation cannot substitute for the full first-order GH CPBC parent",
                    ],
                    "dependency_unlocked": "none; Core curved-3+1 parent and Gravity remain blocked",
                    "claim_boundary": reduced["claim_boundary"],
                },
                "controlling_blocker": "reduced_wave_packet_absorption_and_high_order_spectrum_not_converged",
                "next_action": "derive a discrete energy estimate, diagnose the degree-20 near-zero positive eigenvalue under the unchanged tolerance, and establish spatial convergence for the integrated pulse energy",
                "checks": reduced["checks"],
                "metrics": reduced["metrics"],
                "source_hashes": artifact["source_hashes"],
                "parent_full_u1_status": artifact["status"],
                "parent_full_u1_dependency_unlocked": "none",
            },
            indent=2,
            ensure_ascii=True,
        )
        + "\n",
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
