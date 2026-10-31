from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
REFERENCE_AUDIT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_full_u1_cpbc_slab.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_tangential_cpbc_mode.json"
GH_EQUATIONS = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"

_spec = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_gh_tangential_reference_audit", REFERENCE_AUDIT
)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load the source-matched GH slab reference audit")
REFERENCE = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = REFERENCE
_spec.loader.exec_module(REFERENCE)


def _load_canonical_gh():
    package_name = "_uet_canonical_gh_formula_audit"
    package = types.ModuleType(package_name)
    package.__path__ = [str(GH_EQUATIONS.parent)]
    sys.modules[package_name] = package

    geometry = types.ModuleType(f"{package_name}.uet_curved_3p1_geometry")
    geometry.periodic_central_derivative = lambda *args, **kwargs: None
    sys.modules[geometry.__name__] = geometry

    module_name = f"{package_name}.uet_curved_3p1_generalized_harmonic"
    spec = importlib.util.spec_from_file_location(module_name, GH_EQUATIONS)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load canonical generalized-harmonic equations")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


CANONICAL_GH = _load_canonical_gh()

SLAB = REFERENCE.SLAB
BOUNDARY = REFERENCE.BOUNDARY
PROJECTORS = REFERENCE.PROJECTORS
PAIRS = PROJECTORS.SYMMETRIC_PAIRS
ETA = np.diag([-1.0, 1.0, 1.0, 1.0])
N_COV = np.array([-1.0, 0.0, 0.0, 0.0])
TENSOR_WEIGHTS = np.asarray([1.0 if i == j else 2.0 for i, j in PAIRS])


class TangentialGrid:
    def __init__(self, degree: int, wave_number: float) -> None:
        operators = REFERENCE.chebyshev_lobatto_operators(degree)
        self.nodes = operators.nodes
        self.derivative = operators.derivative
        self.node_count = len(self.nodes)
        self.phase_derivative = np.array(
            [[0.0, wave_number], [-wave_number, 0.0]], dtype=float
        )


def _unpack_grid(values: np.ndarray) -> np.ndarray:
    return np.stack([SLAB.unpack_symmetric(row) for row in values])


def _pack_grid(values: np.ndarray) -> np.ndarray:
    return np.stack([SLAB.pack_symmetric(row) for row in values])


def _harmonic_constraint(
    metric: np.ndarray, pi: np.ndarray, phi: np.ndarray
) -> np.ndarray:
    derivative_fields = [-pi, phi[0], phi[1], phi[2]]
    result = np.zeros(4, dtype=float)
    for a in range(4):
        divergence = sum(ETA[b, b] * derivative_fields[b][a, b] for b in range(4))
        trace_derivative = sum(
            ETA[b, c] * derivative_fields[a][b, c]
            for b in range(4)
            for c in range(4)
        )
        result[a] = divergence - 0.5 * trace_derivative
    return result


def _gamma0_source(
    metric: np.ndarray, pi: np.ndarray, phi: np.ndarray, gamma0: float
) -> np.ndarray:
    if gamma0 == 0.0:
        return np.zeros((4, 4), dtype=float)
    constraint = _harmonic_constraint(metric, pi, phi)
    return gamma0 * (
        np.outer(constraint, N_COV)
        + np.outer(N_COV, constraint)
        - ETA * constraint[0]
    )


def _physical_coordinates(residual: np.ndarray, normal: float) -> np.ndarray:
    tangent_1, tangent_2 = BOUNDARY._tangent_basis(
        np.array([normal, 0.0, 0.0], dtype=float)
    )
    tangent_1 = np.concatenate(([0.0], tangent_1))
    tangent_2 = np.concatenate(([0.0], tangent_2))
    return np.asarray(
        [
            0.5
            * (
                tangent_1 @ residual @ tangent_1
                - tangent_2 @ residual @ tangent_2
            ),
            tangent_1 @ residual @ tangent_2,
        ],
        dtype=float,
    )


def _boundary_target(
    metric: np.ndarray,
    pi: np.ndarray,
    phi: np.ndarray,
    dx_metric: np.ndarray,
    dx_pi: np.ndarray,
    dx_phi: np.ndarray,
    dy_metric: np.ndarray,
    dy_pi: np.ndarray,
    dy_phi: np.ndarray,
    normal: float,
    gamma2: float,
    gamma0: float,
) -> tuple[np.ndarray, dict[str, float]]:
    unit = np.array([normal, 0.0, 0.0], dtype=float)
    metric_gradient = np.zeros((3, 4, 4), dtype=float)
    pi_gradient = np.zeros_like(metric_gradient)
    phi_gradient = np.zeros((3, 3, 4, 4), dtype=float)
    metric_gradient[0] = dx_metric
    metric_gradient[1] = dy_metric
    pi_gradient[0] = dx_pi
    pi_gradient[1] = dy_pi
    for phi_index in range(3):
        phi_gradient[0, phi_index] = dx_phi[phi_index]
        phi_gradient[1, phi_index] = dy_phi[phi_index]

    residual = BOUNDARY.gh_linear_boundary_residuals(
        metric_perturbation=metric,
        pi_perturbation=pi,
        phi_perturbation=phi,
        metric_gradient=metric_gradient,
        pi_gradient=pi_gradient,
        phi_gradient=phi_gradient,
        normal=unit,
        gamma2=gamma2,
    )
    maps = BOUNDARY.gh_boundary_normal_maps(unit)
    projectors = PROJECTORS.build_gh_boundary_projectors(unit)

    normal_metric_derivative = normal * dx_metric
    normal_pi_derivative = normal * dx_pi
    normal_phi_derivative = dx_phi[0]
    q_normal_derivative = SLAB.pack_symmetric(
        normal_pi_derivative
        - normal_phi_derivative
        - gamma2 * normal_metric_derivative
    )
    p_normal_derivative = SLAB.pack_symmetric(
        normal_pi_derivative - normal_phi_derivative
    )

    constraint_tangent = (
        residual.constraint_incoming
        - maps["constraint"] @ q_normal_derivative
    )
    physical_tangent = (
        _physical_coordinates(residual.physical_weyl_incoming, normal)
        - maps["physical"] @ p_normal_derivative
    )

    tangential_divergence = dy_phi[1]
    source_matrix = (
        gamma2 * (pi + normal * phi[0])
        - tangential_divergence
        + _gamma0_source(metric, pi, phi, gamma0)
    )
    source = SLAB.pack_symmetric(source_matrix)
    pc = projectors.constraint
    pp = projectors.physical
    pg = projectors.gauge
    constraint_target = pc @ np.linalg.pinv(maps["constraint"] @ pc) @ (
        maps["constraint"] @ source - constraint_tangent
    )
    physical_target = pp @ np.linalg.pinv(maps["physical"] @ pp) @ (
        maps["physical"]
        @ (source - gamma2 * SLAB.pack_symmetric(normal_metric_derivative))
        - physical_tangent
    )
    target = constraint_target + physical_target

    errors = {
        "constraint_reconstruction": float(
            np.max(
                np.abs(
                    maps["constraint"] @ (target - source)
                    + constraint_tangent
                )
            )
        ),
        "physical_reconstruction": float(
            np.max(
                np.abs(
                    maps["physical"]
                    @ (
                        target
                        - source
                        + gamma2
                        * SLAB.pack_symmetric(normal_metric_derivative)
                    )
                    + physical_tangent
                )
            )
        ),
        "gauge_rate": float(np.max(np.abs(pg @ target))),
    }
    return target, errors


def _mapping_checks() -> dict[str, float]:
    rng = np.random.default_rng(20260925)
    maximum = {
        "constraint_reconstruction": 0.0,
        "physical_reconstruction": 0.0,
        "gauge_rate": 0.0,
        "normal_only_target_reduction": 0.0,
    }

    for normal in (-1.0, 1.0):
        for tangential in (False, True):
            def symmetric() -> np.ndarray:
                value = rng.normal(size=(4, 4))
                return 0.5 * (value + value.T)

            metric, pi = symmetric(), symmetric()
            phi = np.stack([symmetric() for _ in range(3)])
            dx_metric, dx_pi = symmetric(), symmetric()
            dx_phi = np.stack([symmetric() for _ in range(3)])
            dy_metric, dy_pi = symmetric(), symmetric()
            dy_phi = np.stack([symmetric() for _ in range(3)])
            if not tangential:
                dy_metric.fill(0.0)
                dy_pi.fill(0.0)
                dy_phi.fill(0.0)

            target, errors = _boundary_target(
                metric,
                pi,
                phi,
                dx_metric,
                dx_pi,
                dx_phi,
                dy_metric,
                dy_pi,
                dy_phi,
                normal,
                gamma2=1.0,
                gamma0=1.0,
            )
            for name, value in errors.items():
                maximum[name] = max(maximum[name], value)

            if not tangential:
                projectors = PROJECTORS.build_gh_boundary_projectors(
                    np.array([normal, 0.0, 0.0])
                )
                normal_source = (
                    pi
                    + normal * phi[0]
                    + _gamma0_source(metric, pi, phi, gamma0=1.0)
                )
                normal_metric_derivative = normal * dx_metric
                expected = (
                    projectors.constraint @ SLAB.pack_symmetric(normal_source)
                    + projectors.physical
                    @ SLAB.pack_symmetric(
                        normal_source - normal_metric_derivative
                    )
                )
                maximum["normal_only_target_reduction"] = max(
                    maximum["normal_only_target_reduction"],
                    float(np.max(np.abs(target - expected))),
                )

    return maximum


def _canonical_formula_checks() -> dict[str, float]:
    rng = np.random.default_rng(20260926)
    maximum = {
        "harmonic_constraint": 0.0,
        "gamma0_damping": 0.0,
        "slab_helper_harmonic_constraint": 0.0,
    }
    normal = np.array([1.0, 0.0, 0.0, 0.0])
    metric = ETA.copy()
    kinematics = CANONICAL_GH.derive_gh_kinematics(metric)

    for _ in range(64):
        raw_pi = rng.normal(size=(4, 4))
        pi = 0.5 * (raw_pi + raw_pi.T)
        raw_phi = rng.normal(size=(3, 4, 4))
        phi = 0.5 * (raw_phi + np.swapaxes(raw_phi, -1, -2))
        canonical_constraint = CANONICAL_GH.gh_gauge_constraint(
            metric, pi, phi, np.zeros(4), normal
        )
        linearized_constraint = _harmonic_constraint(metric, pi, phi)
        maximum["harmonic_constraint"] = max(
            maximum["harmonic_constraint"],
            float(np.max(np.abs(canonical_constraint - linearized_constraint))),
        )
        canonical_damping = CANONICAL_GH.gh_gamma0_damping_term(
            metric, canonical_constraint, kinematics, gamma0=1.0
        )
        local_damping = _gamma0_source(metric, pi, phi, gamma0=1.0)
        maximum["gamma0_damping"] = max(
            maximum["gamma0_damping"],
            float(np.max(np.abs(canonical_damping - local_damping))),
        )
        normal_phi = np.stack((phi[0], np.zeros_like(phi[0]), np.zeros_like(phi[0])))
        slab_state = SLAB.GHSlabState(
            metric=np.zeros((1, 4, 4)),
            normal_derivative=pi[None, :, :],
            normal_spatial_derivative=normal_phi[0][None, :, :],
        )
        slab_constraint = SLAB.linearized_harmonic_constraint(slab_state)[0]
        normal_canonical = CANONICAL_GH.gh_gauge_constraint(
            metric, pi, normal_phi, np.zeros(4), normal
        )
        maximum["slab_helper_harmonic_constraint"] = max(
            maximum["slab_helper_harmonic_constraint"],
            float(np.max(np.abs(slab_constraint - normal_canonical))),
        )
    return maximum


def _derivatives(
    grid: TangentialGrid, state: tuple[np.ndarray, np.ndarray, np.ndarray]
) -> tuple[np.ndarray, ...]:
    metric, pi, phi = state
    dx_metric = np.einsum("ij,jab->iab", grid.derivative, metric)
    dx_pi = np.einsum("ij,jab->iab", grid.derivative, pi)
    dx_phi = np.einsum("ij,jabc->iabc", grid.derivative, phi)
    dy_metric = np.einsum("ab,ibc->iac", grid.phase_derivative, metric)
    dy_pi = np.einsum("ab,ibc->iac", grid.phase_derivative, pi)
    dy_phi = np.einsum("ab,ibcd->iacd", grid.phase_derivative, phi)
    return dx_metric, dx_pi, dx_phi, dy_metric, dy_pi, dy_phi


def _rhs(
    grid: TangentialGrid,
    state: tuple[np.ndarray, np.ndarray, np.ndarray],
    gamma2: float,
    gamma0: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    metric, pi, phi = state
    dx_metric, dx_pi, dx_phi, dy_metric, dy_pi, dy_phi = _derivatives(
        grid, state
    )
    metric_rhs = -pi
    pi_rhs = -dx_phi[:, :, 0] - dy_phi[:, :, 1]
    phi_rhs = np.empty_like(phi)
    phi_rhs[:, :, 0] = (
        -dx_pi + gamma2 * dx_metric - gamma2 * phi[:, :, 0]
    )
    phi_rhs[:, :, 1] = (
        -dy_pi + gamma2 * dy_metric - gamma2 * phi[:, :, 1]
    )
    phi_rhs[:, :, 2] = -gamma2 * phi[:, :, 2]

    for node in range(grid.node_count):
        for phase in range(2):
            metric_matrix = SLAB.unpack_symmetric(metric[node, phase])
            pi_matrix = SLAB.unpack_symmetric(pi[node, phase])
            phi_matrices = _unpack_grid(phi[node, phase])
            damping = _gamma0_source(
                metric_matrix, pi_matrix, phi_matrices, gamma0
            )
            pi_rhs[node, phase] += SLAB.pack_symmetric(damping)

    for face, normal in ((0, -1.0), (grid.node_count - 1, 1.0)):
        for phase in range(2):
            target, _ = _boundary_target(
                SLAB.unpack_symmetric(metric[face, phase]),
                SLAB.unpack_symmetric(pi[face, phase]),
                _unpack_grid(phi[face, phase]),
                SLAB.unpack_symmetric(dx_metric[face, phase]),
                SLAB.unpack_symmetric(dx_pi[face, phase]),
                _unpack_grid(dx_phi[face, phase]),
                SLAB.unpack_symmetric(dy_metric[face, phase]),
                SLAB.unpack_symmetric(dy_pi[face, phase]),
                _unpack_grid(dy_phi[face, phase]),
                normal,
                gamma2,
                gamma0,
            )
            qdot = (
                pi_rhs[face, phase]
                - normal * phi_rhs[face, phase, 0]
                - gamma2 * metric_rhs[face, phase]
            )
            correction = target - qdot
            pi_rhs[face, phase] += 0.5 * correction
            phi_rhs[face, phase, 0] -= 0.5 * normal * correction

    return metric_rhs, pi_rhs, phi_rhs


def _combine(
    state: tuple[np.ndarray, np.ndarray, np.ndarray],
    rhs: tuple[np.ndarray, np.ndarray, np.ndarray],
    scale: float,
    dt: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return tuple(
        value + scale * dt * derivative
        for value, derivative in zip(state, rhs)
    )


def _rk4_step(
    grid: TangentialGrid,
    state: tuple[np.ndarray, np.ndarray, np.ndarray],
    dt: float,
    gamma2: float,
    gamma0: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    k1 = _rhs(grid, state, gamma2, gamma0)
    k2 = _rhs(grid, _combine(state, k1, 0.5, dt), gamma2, gamma0)
    k3 = _rhs(grid, _combine(state, k2, 0.5, dt), gamma2, gamma0)
    k4 = _rhs(grid, _combine(state, k3, 1.0, dt), gamma2, gamma0)
    return tuple(
        value + dt * (a + 2.0 * b + 2.0 * c + d) / 6.0
        for value, a, b, c, d in zip(state, k1, k2, k3, k4)
    )


def _state_metrics(
    grid: TangentialGrid,
    state: tuple[np.ndarray, np.ndarray, np.ndarray],
    gamma2: float,
) -> dict[str, float]:
    metric, pi, phi = state
    weights = REFERENCE._clenshaw_curtis_weights(grid.node_count - 1)[:, None, None]
    centered_metric = metric - metric.mean(axis=(0, 1), keepdims=True)
    state_density = (
        centered_metric**2 + pi**2 + np.sum(phi**2, axis=2)
    ) * TENSOR_WEIGHTS
    energy_density = (
        4.0 * metric**2
        - 2.0 * gamma2 * metric * pi
        + pi**2
        + np.sum(phi**2, axis=2)
    ) * TENSOR_WEIGHTS
    state_norm = float(np.sqrt(np.sum(weights * state_density)))
    gh_energy = float(0.5 * np.sum(weights * energy_density))

    dx_metric = np.einsum("ij,jab->iab", grid.derivative, metric)
    dy_metric = np.einsum("ab,ibc->iac", grid.phase_derivative, metric)
    reduction = max(
        float(np.max(np.abs(dx_metric - phi[:, :, 0]))),
        float(np.max(np.abs(dy_metric - phi[:, :, 1]))),
        float(np.max(np.abs(phi[:, :, 2]))),
    )
    harmonic = 0.0
    for node in range(grid.node_count):
        for phase in range(2):
            value = _harmonic_constraint(
                SLAB.unpack_symmetric(metric[node, phase]),
                SLAB.unpack_symmetric(pi[node, phase]),
                _unpack_grid(phi[node, phase]),
            )
            harmonic = max(harmonic, float(np.max(np.abs(value))))
    return {
        "state_norm": state_norm,
        "gh_energy": gh_energy,
        "reduction_linf": reduction,
        "harmonic_constraint_linf": harmonic,
    }


def _run_mode(degree: int, wave_number: float, final_time: float) -> dict[str, Any]:
    gamma2 = 1.0
    gamma0 = 1.0
    grid = TangentialGrid(degree, wave_number)
    rng = np.random.default_rng(900)
    profile_degree = 4
    basis = np.polynomial.chebyshev.chebvander(grid.nodes, profile_degree)
    metric_coefficients = 1.0e-10 * rng.standard_normal(
        (profile_degree + 1, 2, 10)
    )
    pi_coefficients = 1.0e-10 * rng.standard_normal(
        (profile_degree + 1, 2, 10)
    )
    phi_coefficients = 1.0e-10 * rng.standard_normal(
        (profile_degree + 1, 2, 3, 10)
    )
    state = (
        np.einsum("im,mqa->iqa", basis, metric_coefficients),
        np.einsum("im,mqa->iqa", basis, pi_coefficients),
        np.einsum("im,mqka->iqka", basis, phi_coefficients),
    )
    initial = _state_metrics(grid, state, gamma2)
    spacing = float(np.min(np.diff(grid.nodes)))
    dt_cap = min(0.3 * spacing, 0.3 / (wave_number + 1.0))
    steps_per_unit = int(np.ceil(1.0 / dt_cap))
    dt = 1.0 / steps_per_unit
    step_count = int(round(final_time * steps_per_unit))
    peak_norm = initial["state_norm"]
    peak_energy = initial["gh_energy"]

    for _ in range(step_count):
        state = _rk4_step(grid, state, dt, gamma2, gamma0)
        metric, pi, phi = state
        weights = REFERENCE._clenshaw_curtis_weights(grid.node_count - 1)[:, None, None]
        centered_metric = metric - metric.mean(axis=(0, 1), keepdims=True)
        state_density = (
            centered_metric**2 + pi**2 + np.sum(phi**2, axis=2)
        ) * TENSOR_WEIGHTS
        energy_density = (
            4.0 * metric**2
            - 2.0 * gamma2 * metric * pi
            + pi**2
            + np.sum(phi**2, axis=2)
        ) * TENSOR_WEIGHTS
        peak_norm = max(peak_norm, float(np.sqrt(np.sum(weights * state_density))))
        peak_energy = max(peak_energy, float(0.5 * np.sum(weights * energy_density)))

    final = _state_metrics(grid, state, gamma2)
    return {
        "degree": degree,
        "node_count": grid.node_count,
        "phase_components": ["cos", "sin"],
        "tangential_wave_number_over_L0": wave_number,
        "gamma0_L0": gamma0,
        "gamma2_L0": gamma2,
        "final_time_over_L0": final_time,
        "time_steps": step_count,
        "dt_over_L0": dt,
        "initial_chebyshev_degree": profile_degree,
        "initial_seed": 900,
        "initial_coefficient_scale": 1.0e-10,
        "initial_profile_shared_across_degrees": True,
        "state_norm_peak_growth": peak_norm / initial["state_norm"],
        "state_norm_final_growth": final["state_norm"] / initial["state_norm"],
        "gh_energy_peak_ratio": peak_energy / initial["gh_energy"],
        "gh_energy_final_ratio": final["gh_energy"] / initial["gh_energy"],
        "final_reduction_linf": final["reduction_linf"],
        "final_harmonic_constraint_linf": final["harmonic_constraint_linf"],
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact() -> dict[str, Any]:
    mapping_errors = _mapping_checks()
    canonical_formula_errors = _canonical_formula_checks()
    screen_degrees = (4, 8, 12)
    screen_wavenumbers = (0.5 * np.pi, np.pi, 2.0 * np.pi)
    screen_final_time = 8.0
    mode_results = [
        _run_mode(degree, float(wave_number), final_time=screen_final_time)
        for wave_number in screen_wavenumbers
        for degree in screen_degrees
    ]
    source_paths = {
        "audit_script": Path(__file__).resolve(),
        "reference_audit": REFERENCE_AUDIT,
        "slab_equations": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_full_u1_slab.py",
        "boundary_residuals": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py",
        "boundary_projectors": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py",
        "canonical_gh_equations": GH_EQUATIONS,
    }
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in source_paths.values()
    }
    return {
        "schema_version": "core-curved-3p1-gh-tangential-cpbc-mode-v1",
        "artifact": "curved_3p1_gh_tangential_cpbc_mode",
        "diagnostic_id": "uet.core.curved_3p1.gh.rinne_tangential_mode_screen",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_TANGENTIAL_MODE_SCREEN",
        "closure_level": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": [
            "The 3D normal-map reconstruction of constraint, Psi0, and gauge-rate targets closes algebraically against the local Core residual evaluator at both x faces.",
            "With tangential derivatives set to zero, the reconstructed target reduces to the normal-incidence 4+2+4 formula, including the declared linear gamma0 source contribution.",
            "The flat-space harmonic constraint, gamma0 damping, and slab helper agree with the canonical Core GH functions to the recorded floating-point residuals.",
            "Both spatial degrees sample the same seed-locked Chebyshev initial profile, so their finite-time responses use matched initial data.",
        ],
        "WHAT_REMAINS_OPEN": [
            "The one-Fourier-mode screen is only run to t/L0=4 on two spatial degrees; it is not a long-time, multi-wavenumber, spatial-convergence, or energy-stability result.",
            "The two matched-grid responses remain exploratory; the differential-CPBC lane and its stability classification are unresolved.",
            "Positive normal shift, incoming u2_A, multiple tangential modes, edges/corners, variable coefficients, nonlinear GH, and continuum well-posedness remain open.",
        ],
        "DEPENDENCY_UNLOCKED": "none; Core curved-3+1 parent remains PARTIAL and Gravity remains blocked",
        "STATUS": "OPEN_EXPLORATORY_SCREEN",
        "WHAT_CHANGED": "Corrected the slab helper's trace contraction to match the canonical GH equation, added its regression, and added a source-hashed 2D slab screen with one exact tangential Fourier mode and direct canonical constraint/gamma0 checks.",
        "EQUATION_OR_MAPPING": {
            "constraint_target": "A_C P_C qdot = A_C(S) - T_C, where T_C is the tangential remainder of the incoming subsidiary-constraint residual",
            "physical_target": "A_P P_P qdot = A_P(S - gamma2 D_n psi) - T_P, where T_P is the tangential remainder of the incoming Psi0 residual",
            "bulk_qdot_source": "S = gamma2(Pi + Phi_n) - div_tangent(Phi_tangent) + gamma0 damping source",
            "gauge_target": "P_G qdot = 0 for homogeneous gauge-rate data",
            "reduction_constraint": "D_x psi - Phi_x = 0; K_y psi - Phi_y = 0; Phi_z = 0 for this one-mode slab",
            "initial_profile": "Same seed-900 random Chebyshev coefficients through degree 4, sampled on both LGL grids",
            "tensor_metric": "Frobenius weights 1 for diagonal and 2 for off-diagonal packed symmetric components",
        },
        "PREREGISTRATION": {
            "spatial_degrees": list(screen_degrees),
            "tangential_wavenumbers_over_L0": [
                float(value) for value in screen_wavenumbers
            ],
            "final_time_over_L0": screen_final_time,
            "gamma0_over_L0_inverse": 1.0,
            "gamma2_over_L0_inverse": 1.0,
            "initial_profile": "shared seed-900 Chebyshev coefficients through degree 4, sampled on every grid",
            "decision_thresholds": "No new pass threshold; report diagnostics only and do not unlock dependencies",
            "reported_metrics": [
                "state norm peak and final ratios",
                "GH energy peak and final ratios",
                "harmonic constraint and reduction-constraint residuals",
            ],
        },
        "VERIFICATION": {
            "mapping_max_abs_residuals": mapping_errors,
            "canonical_gh_formula_max_abs_residuals": canonical_formula_errors,
            "tangential_mode_runs": mode_results,
            "mapping_algebra_max_abs": max(mapping_errors.values()),
            "source_hashes_sha256": source_hashes,
            "filtering": False,
            "clipping": False,
            "parameter_fitting": False,
            "external_data": False,
            "holdout_access": False,
        },
        "CONTROLLING_BLOCKER": "full_first_order_gh_differential_cpbc_stability_and_resolution_convergence_missing",
        "NEXT_ACTION": "Derive semidiscrete spectra and a projector-aware energy estimate over the preregistered matched-profile sweep; only after that, evaluate positive-shift u2_A and multidimensional corner compatibility. Preserve the frozen full-u1 baseline and do not relax thresholds.",
        "CLAIM_BOUNDARY": "Finite-grid, frozen-background standard-GR boundary-method diagnostic only; not a full Rinne CPBC reproduction, continuum well-posedness proof, curved 3+1 parent closure, UET validation, or Gravity unlock.",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": artifact["STATUS"], "artifact": OUTPUT.as_posix(), "checks": artifact["VERIFICATION"]["mapping_max_abs_residuals"], "runs": artifact["VERIFICATION"]["tangential_mode_runs"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
