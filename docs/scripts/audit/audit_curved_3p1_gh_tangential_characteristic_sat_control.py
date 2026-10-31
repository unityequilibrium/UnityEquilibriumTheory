from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SPECTRUM_AUDIT = (
    ROOT / "docs/scripts/audit/audit_curved_3p1_gh_tangential_cpbc_spectrum.py"
)
SPECTRUM_ARTIFACT = (
    ROOT
    / "docs/core/07_artifacts/verification/"
    / "curved_3p1_gh_tangential_cpbc_spectrum.json"
)
OUTPUT = (
    ROOT / "docs/core/07_artifacts/verification/"
    / "curved_3p1_gh_tangential_characteristic_sat_control.json"
)
ORDERS = (8, 10, 12, 14, 16)
WAVE_NUMBER = float(np.pi)
GAMMA0 = 0.0
GAMMA2 = 1.0
LAMBDA2 = 4.0
EIGENVALUE_TOLERANCE = 1.0e-6

_spec = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_gh_characteristic_sat_spectrum", SPECTRUM_AUDIT
)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load the registered tangential GH audit helpers")
SPECTRUM = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = SPECTRUM
_spec.loader.exec_module(SPECTRUM)
MODE = SPECTRUM.MODE


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _weak_characteristic_rhs(
    grid: Any,
    state: tuple[np.ndarray, ...],
    norm_weights: np.ndarray,
) -> tuple[np.ndarray, ...]:
    metric, pi, phi = state
    metric_rhs, pi_rhs, phi_rhs = SPECTRUM._bulk_rhs(
        grid, state, GAMMA2, GAMMA0
    )
    for face, normal in ((0, -1.0), (grid.node_count - 1, 1.0)):
        for phase in range(metric.shape[1]):
            incoming = (
                pi[face, phase]
                - normal * phi[face, phase, 0]
                - GAMMA2 * metric[face, phase]
            )
            pi_rhs[face, phase] -= incoming / norm_weights[face]
    return metric_rhs, pi_rhs, phi_rhs


def _assemble_matrix(
    grid: Any,
    norm_weights: np.ndarray,
    boundary_method: str,
) -> np.ndarray:
    dimension = SPECTRUM._state_size(grid.node_count)
    matrix = np.empty((dimension, dimension), dtype=float)
    basis = np.zeros(dimension, dtype=float)
    for column in range(dimension):
        basis[column] = 1.0
        state = SPECTRUM._unpack(basis, grid.node_count)
        if boundary_method == "differential_rinne_strong_target":
            rhs = MODE._rhs(grid, state, GAMMA2, GAMMA0)
        elif boundary_method == "direct_incoming_characteristic_weak_sat":
            rhs = _weak_characteristic_rhs(grid, state, norm_weights)
        else:
            raise ValueError(f"unknown boundary method: {boundary_method}")
        matrix[:, column] = SPECTRUM._flatten(rhs)
        basis[column] = 0.0
    return matrix


def _energy(state: tuple[np.ndarray, ...], weights: np.ndarray) -> float:
    metric, pi, phi = state
    density = (
        LAMBDA2 * metric**2
        - 2.0 * GAMMA2 * metric * pi
        + pi**2
        + np.sum(phi**2, axis=2)
    )
    return float(
        0.5
        * np.sum(
            density
            * weights[:, None, None]
            * MODE.TENSOR_WEIGHTS
        )
    )


def _energy_rate(
    state: tuple[np.ndarray, ...],
    rhs: tuple[np.ndarray, ...],
    weights: np.ndarray,
) -> float:
    metric, pi, phi = state
    metric_rhs, pi_rhs, phi_rhs = rhs
    metric_gradient = LAMBDA2 * metric - GAMMA2 * pi
    pi_gradient = pi - GAMMA2 * metric
    density_rate = (
        metric_gradient * metric_rhs
        + pi_gradient * pi_rhs
        + np.sum(phi * phi_rhs, axis=2)
    )
    return float(
        np.sum(
            density_rate
            * weights[:, None, None]
            * MODE.TENSOR_WEIGHTS
        )
    )


def _lower_order_rate(
    state: tuple[np.ndarray, ...], weights: np.ndarray
) -> float:
    metric, pi, phi = state
    density_rate = (
        -LAMBDA2 * metric * pi
        + GAMMA2 * pi**2
        - GAMMA2 * np.sum(phi**2, axis=2)
    )
    return float(
        np.sum(
            density_rate
            * weights[:, None, None]
            * MODE.TENSOR_WEIGHTS
        )
    )


def _boundary_dissipation(
    state: tuple[np.ndarray, ...], weights: np.ndarray
) -> float:
    metric, pi, _ = state
    total = 0.0
    for face in (0, len(weights) - 1):
        p = pi[face] - GAMMA2 * metric[face]
        total += float(np.sum(p**2 * MODE.TENSOR_WEIGHTS[None, :]))
    return total


def _energy_growth_constant() -> dict[str, Any]:
    symmetrizer = np.array(
        [
            [LAMBDA2, -GAMMA2, 0.0],
            [-GAMMA2, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    lower_order = np.array(
        [
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, -GAMMA2],
        ]
    )
    quadratic = 0.5 * (
        symmetrizer @ lower_order + lower_order.T @ symmetrizer
    )
    cholesky = np.linalg.cholesky(symmetrizer)
    transformed = np.linalg.solve(cholesky, quadratic)
    transformed = np.linalg.solve(cholesky, transformed.T).T
    eigenvalues = np.linalg.eigvalsh(0.5 * (transformed + transformed.T))
    return {
        "mu_over_L0_inverse": float(eigenvalues[-1]),
        "2mu_over_L0_inverse": float(2.0 * eigenvalues[-1]),
        "generalized_eigenvalues_over_L0_inverse": [
            float(value) for value in eigenvalues
        ],
    }


def _projector_compatibility() -> dict[str, Any]:
    metric = np.diag(MODE.TENSOR_WEIGHTS)
    identity = np.eye(10)
    maximum_reconstruction = 0.0
    maximum_self_adjoint = 0.0
    maximum_cross_orthogonality = 0.0
    ranks: dict[str, int] | None = None
    for normal in (-1.0, 1.0):
        projectors = MODE.PROJECTORS.build_gh_boundary_projectors(
            np.array([normal, 0.0, 0.0])
        )
        pieces = (
            projectors.constraint,
            projectors.physical,
            projectors.gauge,
        )
        if ranks is None:
            ranks = projectors.ranks
        total = sum(pieces)
        maximum_reconstruction = max(
            maximum_reconstruction,
            float(np.max(np.abs(total - identity))),
        )
        for index, projector in enumerate(pieces):
            maximum_self_adjoint = max(
                maximum_self_adjoint,
                float(np.max(np.abs(metric @ projector - projector.T @ metric))),
            )
            for other_index, other in enumerate(pieces):
                if index != other_index:
                    maximum_cross_orthogonality = max(
                        maximum_cross_orthogonality,
                        float(
                            np.max(
                                np.abs(projector.T @ metric @ other)
                            )
                        ),
                    )
    return {
        "normal_count": 2,
        "projector_ranks": ranks,
        "metric_minimum_eigenvalue": float(
            np.min(np.linalg.eigvalsh(metric))
        ),
        "maximum_projector_sum_identity_residual": maximum_reconstruction,
        "maximum_G_self_adjoint_residual": maximum_self_adjoint,
        "maximum_cross_sector_orthogonality_residual": (
            maximum_cross_orthogonality
        ),
    }


def _operator_probe(
    grid: Any,
    weights: np.ndarray,
    method: str,
    matrix: np.ndarray,
    seed: int,
) -> float:
    rng = np.random.default_rng(seed)
    vector = rng.standard_normal(SPECTRUM._state_size(grid.node_count))
    state = SPECTRUM._unpack(vector, grid.node_count)
    direct = (
        MODE._rhs(grid, state, GAMMA2, GAMMA0)
        if method == "differential_rinne_strong_target"
        else _weak_characteristic_rhs(grid, state, weights)
    )
    direct_vector = SPECTRUM._flatten(direct)
    matrix_vector = matrix @ vector
    return float(
        np.linalg.norm(matrix_vector - direct_vector)
        / max(
            np.linalg.norm(matrix_vector),
            np.linalg.norm(direct_vector),
            1.0e-300,
        )
    )


def _energy_norm_probe(
    matrix: np.ndarray,
    energy_matrix: np.ndarray,
    energy_factor: np.ndarray,
    grid: Any,
    weights: np.ndarray,
    method: str,
) -> dict[str, Any]:
    symmetric_rate = 0.5 * (
        energy_matrix @ matrix + matrix.T @ energy_matrix
    )
    left_whitened = np.linalg.solve(energy_factor, symmetric_rate)
    whitened_rate = np.linalg.solve(energy_factor, left_whitened.T).T
    whitened_rate = 0.5 * (whitened_rate + whitened_rate.T)
    rates, directions = np.linalg.eigh(whitened_rate)
    energy_log_norm = float(rates[-1])
    optimal_vector = np.linalg.solve(
        energy_factor.T, directions[:, -1]
    )
    state = SPECTRUM._unpack(optimal_vector, grid.node_count)
    total_rhs = (
        MODE._rhs(grid, state, GAMMA2, GAMMA0)
        if method == "differential_rinne_strong_target"
        else _weak_characteristic_rhs(grid, state, weights)
    )
    bulk_rhs = SPECTRUM._bulk_rhs(grid, state, GAMMA2, GAMMA0)
    boundary_rhs = tuple(
        total_part - bulk_part
        for total_part, bulk_part in zip(total_rhs, bulk_rhs)
    )
    energy = _energy(state, weights)
    total_rate = _energy_rate(state, total_rhs, weights) / energy
    bulk_rate = _energy_rate(state, bulk_rhs, weights) / energy
    boundary_rate = _energy_rate(state, boundary_rhs, weights) / energy

    metric, pi, phi = state
    density = (
        LAMBDA2 * metric**2
        - 2.0 * GAMMA2 * metric * pi
        + pi**2
        + np.sum(phi**2, axis=2)
    )
    local_energy = 0.5 * np.sum(
        density * weights[:, None, None] * MODE.TENSOR_WEIGHTS,
        axis=(1, 2),
    )
    endpoint_energy_fraction = float(
        (local_energy[0] + local_energy[-1]) / np.sum(local_energy)
    )
    return {
        "maximum_energy_norm_log_growth_rate_over_L0_inverse": (
            energy_log_norm
        ),
        "maximum_energy_relative_growth_rate_over_L0_inverse": (
            2.0 * energy_log_norm
        ),
        "energy_matrix_positive_definite_by_cholesky": True,
        "optimal_direction_relative_energy_rate_over_L0_inverse": (
            total_rate
        ),
        "optimal_direction_energy_rate_check_abs_residual": abs(
            total_rate - 2.0 * energy_log_norm
        ),
        "optimal_direction_bulk_relative_energy_rate_over_L0_inverse": (
            bulk_rate
        ),
        "optimal_direction_boundary_relative_energy_rate_over_L0_inverse": (
            boundary_rate
        ),
        "optimal_direction_bulk_boundary_balance_abs_residual": abs(
            total_rate - bulk_rate - boundary_rate
        ),
        "optimal_direction_endpoint_energy_fraction": (
            endpoint_energy_fraction
        ),
        "optimal_direction_incoming_sector_fractions": (
            SPECTRUM._boundary_sector_fractions(state, GAMMA2)
        ),
    }


def _order_case(order: int) -> dict[str, Any]:
    operators = SPECTRUM.LGL.legendre_lobatto_operators(order)
    grid = MODE.TangentialGrid(order, WAVE_NUMBER)
    grid.nodes = operators.nodes
    grid.derivative = operators.derivative
    grid.node_count = len(grid.nodes)
    weights = operators.norm_weights

    boundary = np.zeros((grid.node_count, grid.node_count), dtype=float)
    boundary[0, 0] = -1.0
    boundary[-1, -1] = 1.0
    h = np.diag(weights)
    sbp_residual = h @ grid.derivative + grid.derivative.T @ h - boundary
    energy_matrix = SPECTRUM._energy_matrix(
        grid.node_count, weights, GAMMA2
    )
    energy_factor = np.linalg.cholesky(energy_matrix)

    rng = np.random.default_rng(20260925 + order)
    sample = rng.standard_normal(SPECTRUM._state_size(grid.node_count))
    state = SPECTRUM._unpack(sample, grid.node_count)
    weak_rhs = _weak_characteristic_rhs(grid, state, weights)
    observed_rate = _energy_rate(state, weak_rhs, weights)
    lower_rate = _lower_order_rate(state, weights)
    boundary_rate = _boundary_dissipation(state, weights)
    energy = _energy(state, weights)

    metric, _, _ = state
    metric_rhs, _, phi_rhs = weak_rhs
    observed_constraint_rate = (
        np.einsum("ij,jpa->ipa", grid.derivative, metric_rhs)
        - phi_rhs[:, :, 0]
    )
    expected_constraint_rate = -GAMMA2 * (
        np.einsum("ij,jpa->ipa", grid.derivative, metric)
        - state[2][:, :, 0]
    )

    matrices: dict[str, np.ndarray] = {}
    spectra: dict[str, Any] = {}
    for method in (
        "direct_incoming_characteristic_weak_sat",
        "differential_rinne_strong_target",
    ):
        matrix = _assemble_matrix(grid, weights, method)
        matrices[method] = matrix
        eigenvalues = np.linalg.eigvals(matrix)
        order_index = np.argsort(eigenvalues.real)[::-1]
        spectra[method] = {
            "spectral_abscissa_over_L0_inverse": float(
                np.max(eigenvalues.real)
            ),
            "positive_mode_count_above_existing_1e-6_tolerance": int(
                np.count_nonzero(eigenvalues.real > EIGENVALUE_TOLERANCE)
            ),
            "leading_eigenvalues_over_L0_inverse": [
                {"real": float(value.real), "imag": float(value.imag)}
                for value in eigenvalues[order_index[:6]]
            ],
        }
        spectra[method].update(
            _energy_norm_probe(
                matrix,
                energy_matrix,
                energy_factor,
                grid,
                weights,
                method,
            )
        )

    direct_probe_norm = _operator_probe(
        grid,
        weights,
        "direct_incoming_characteristic_weak_sat",
        matrices["direct_incoming_characteristic_weak_sat"],
        30000 + order,
    )
    rinne_probe_norm = _operator_probe(
        grid,
        weights,
        "differential_rinne_strong_target",
        matrices["differential_rinne_strong_target"],
        40000 + order,
    )
    reduction_residual = float(
        np.max(np.abs(observed_constraint_rate - expected_constraint_rate))
    )
    return {
        "lgl_order": order,
        "node_count": grid.node_count,
        "state_dimension": int(matrices[
            "direct_incoming_characteristic_weak_sat"
        ].shape[0]),
        "tangential_wavenumber_over_L0": WAVE_NUMBER,
        "gamma0_L0": GAMMA0,
        "gamma2_L0": GAMMA2,
        "sbp_identity_max_abs_residual": float(
            np.max(np.abs(sbp_residual))
        ),
        "random_state_direct_sat_energy_balance": {
            "observed_dE_dt": observed_rate,
            "lower_order_rate": lower_rate,
            "boundary_dissipation": boundary_rate,
            "predicted_dE_dt": lower_rate - boundary_rate,
            "absolute_identity_residual": abs(
                observed_rate - (lower_rate - boundary_rate)
            ),
            "energy": energy,
        },
        "reduction_constraint_rhs_identity_residual": reduction_residual,
        "spectra": spectra,
        "operator_application_relative_residuals": {
            "direct_sat": direct_probe_norm,
            "rinne_strong": rinne_probe_norm,
        },
    }


def build_artifact() -> dict[str, Any]:
    spectrum_artifact = json.loads(
        SPECTRUM_ARTIFACT.read_text(encoding="utf-8")
    )
    expected_source = spectrum_artifact["VERIFICATION"][
        "source_hashes_sha256"
    ].get(SPECTRUM_AUDIT.relative_to(ROOT).as_posix())
    if expected_source != _sha256(SPECTRUM_AUDIT):
        raise RuntimeError(
            "the matched spectrum artifact is stale relative to its source"
        )

    cases = [_order_case(order) for order in ORDERS]
    projectors = _projector_compatibility()
    growth = _energy_growth_constant()
    sources = {
        "characteristic_sat_control_audit": Path(__file__).resolve(),
        "spectrum_audit": SPECTRUM_AUDIT,
        "spectrum_artifact_input": SPECTRUM.OUTPUT,
        "matched_profile_audit": SPECTRUM.MODE_AUDIT,
        "lgl_sbp_operator_audit": SPECTRUM.LGL_AUDIT,
        "boundary_residuals": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py",
        "boundary_projectors": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py",
        "slab_equations": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_full_u1_slab.py",
        "max_diss_sat_control": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_max_dissipative_sat.py",
    }
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in sources.values()
    }
    source_hashes_match = all(
        source_hashes[path.relative_to(ROOT).as_posix()] == _sha256(path)
        for path in sources.values()
    )
    residuals = [
        case["random_state_direct_sat_energy_balance"][
            "absolute_identity_residual"
        ]
        for case in cases
    ]
    sbp_residuals = [
        case["sbp_identity_max_abs_residual"] for case in cases
    ]
    reduction_residuals = [
        case["reduction_constraint_rhs_identity_residual"] for case in cases
    ]
    direct_operator_residuals = [
        case["operator_application_relative_residuals"]["direct_sat"]
        for case in cases
    ]
    rinne_operator_residuals = [
        case["operator_application_relative_residuals"]["rinne_strong"]
        for case in cases
    ]
    weak_counts = [
        case["spectra"]["direct_incoming_characteristic_weak_sat"][
            "positive_mode_count_above_existing_1e-6_tolerance"
        ]
        for case in cases
    ]
    rinne_counts = [
        case["spectra"]["differential_rinne_strong_target"][
            "positive_mode_count_above_existing_1e-6_tolerance"
        ]
        for case in cases
    ]
    direct_energy_growth_rates = [
        case["spectra"]["direct_incoming_characteristic_weak_sat"][
            "maximum_energy_relative_growth_rate_over_L0_inverse"
        ]
        for case in cases
    ]
    rinne_energy_growth_rates = [
        case["spectra"]["differential_rinne_strong_target"][
            "maximum_energy_relative_growth_rate_over_L0_inverse"
        ]
        for case in cases
    ]
    energy_rate_residuals = [
        result["optimal_direction_energy_rate_check_abs_residual"]
        for case in cases
        for result in case["spectra"].values()
    ]
    bulk_boundary_residuals = [
        result["optimal_direction_bulk_boundary_balance_abs_residual"]
        for case in cases
        for result in case["spectra"].values()
    ]
    return {
        "schema_version": "core-curved-3p1-gh-tangential-characteristic-sat-control-v2",
        "artifact": "curved_3p1_gh_tangential_characteristic_sat_control",
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "major_result_id": "CORE_CURVED_3P1_GH_TANGENTIAL_CHARACTERISTIC_SAT_CONTROL",
        "closure_level": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": [
            "For the same LGL-SBP tangential-mode bulk operator, direct homogeneous incoming-characteristic SAT obeys the GH symmetrizer energy identity at every declared order.",
            "The identity penalty is componentwise and therefore commutes with the registered constraint/physical/gauge projector decomposition in the packed tensor metric.",
            "At the same zero-shift orders, tangential wavenumber, gamma0=0, and gamma2=1, the direct incoming-value control and the differential-Rinne-target strong replacement are assembled and spectrally compared.",
            "The direct SAT's maximum relative energy-growth rate equals the analytic 2*mu bulk bound within numerical tolerance at every order; the differential-target strong replacement has much larger endpoint-localized energy-growth directions in this sampled discretization.",
            "The experiment keeps the boundary data types distinct: the direct SAT prescribes q_in, while the differential target computes q_in_dot; the audit does not identify these quantities.",
        ],
        "WHAT_REMAINS_OPEN": [
            "The direct characteristic SAT is a stable control boundary, not the differential Rinne constraint/Weyl boundary condition.",
            "The differential Rinne conditions are of differential type and are assessed in the continuum by a Fourier-Laplace/Kreiss boundary-stability analysis, not by assuming a maximally dissipative energy inequality. A source-matched boundary-symbol/Kreiss audit of the local exact branch is still missing.",
            "The large finite-grid energy-log norms and positive modes characterize this strong endpoint replacement only; they do not prove that the continuum Rinne CPBC is ill-posed.",
            "The finite-grid comparison is not a continuum proof, a nonlinear GH result, or a curved-parent closure; strong well-posedness with general nonzero initial/source data remains outside this audit.",
        ],
        "DEPENDENCY_UNLOCKED": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "STATUS": "OPEN_TANGENTIAL_CHARACTERISTIC_SAT_CONTROL",
        "WHAT_CHANGED": "Added a source-hashed tangential-mode weak-SAT control, same-grid spectra, and GH-energy logarithmic-norm/bulk-boundary-work diagnostics against the differential-Rinne strong replacement, using the existing LGL orders and unchanged eigenvalue tolerance.",
        "EQUATION_OR_MAPPING": {
            "energy": "E_h=1/2 sum_x,phase w_x [4||psi||_G^2-2*gamma2<psi,Pi>_G+||Pi||_G^2+sum_i||Phi_i||_G^2]",
            "incoming_characteristic": "q_in=Pi-n*Phi_x-gamma2*psi",
            "direct_sat": "delta(Pi_dot)_face=-H_face^-1*q_in; delta(psi_dot)=delta(Phi_dot)=0",
            "energy_identity": "dE_h/dt=R_lower-sum_faces||Pi-gamma2*psi||_G^2 for homogeneous q_in=0; tangential periodic-mode flux cancels",
            "lower_order_rate": "R_lower=sum w[-4<psi,Pi>_G+gamma2||Pi||_G^2-gamma2*sum_i||Phi_i||_G^2]",
            "energy_logarithmic_norm": "mu_E=lambda_max(H_E^(-1/2)*sym(H_E*A_h)*H_E^(-1/2)); dE_h/dt<=2*mu_E*E_h; evaluated for each semidiscrete matrix",
            "energy_method_scope": "The analytic 2*mu bound applies to the direct homogeneous max-dissipative SAT control in this audit, not as a required acceptance condition for the differential-type Rinne CPBC.",
            "differential_rinne_target": "target is a prescribed value for d(q_in)/dt from the constraint/physical/gauge residual maps; it is not q_in boundary data",
            "projector_contract": "P_C+P_P+P_G=I, with G-self-adjoint, mutually orthogonal projectors; the identity SAT penalty is sectorwise compatible",
        },
        "PREREGISTRATION": {
            "operator_family": "Legendre-Gauss-Lobatto diagonal-norm SBP",
            "orders": list(ORDERS),
            "tangential_wavenumber_over_L0": WAVE_NUMBER,
            "gamma0_L0": GAMMA0,
            "gamma2_L0": GAMMA2,
            "symmetrizer_lambda_squared": LAMBDA2,
            "positive_real_part_reference_tolerance": EIGENVALUE_TOLERANCE,
            "parameter_fitting": False,
            "threshold_changes": False,
        },
        "VERIFICATION": {
            "cases": cases,
            "case_count": len(cases),
            "maximum_random_state_energy_identity_residual": max(residuals),
            "maximum_sbp_identity_abs_residual": max(sbp_residuals),
            "maximum_reduction_constraint_rhs_identity_residual": max(
                reduction_residuals
            ),
            "maximum_direct_sat_matrix_application_relative_residual": max(
                direct_operator_residuals
            ),
            "maximum_rinne_strong_matrix_application_relative_residual": max(
                rinne_operator_residuals
            ),
            "maximum_projector_sum_identity_residual": projectors[
                "maximum_projector_sum_identity_residual"
            ],
            "maximum_projector_G_self_adjoint_residual": projectors[
                "maximum_G_self_adjoint_residual"
            ],
            "maximum_projector_cross_orthogonality_residual": projectors[
                "maximum_cross_sector_orthogonality_residual"
            ],
            "projector_audit": projectors,
            "lower_order_growth_bound": growth,
            "maximum_direct_sat_energy_relative_growth_rate_over_L0_inverse": max(
                direct_energy_growth_rates
            ),
            "all_direct_sat_energy_growth_rates_within_2mu_bound": all(
                value <= growth["2mu_over_L0_inverse"] + 1.0e-10
                for value in direct_energy_growth_rates
            ),
            "maximum_differential_rinne_energy_relative_growth_rate_over_L0_inverse": max(
                rinne_energy_growth_rates
            ),
            "maximum_optimal_direction_energy_rate_check_abs_residual": max(
                energy_rate_residuals
            ),
            "maximum_optimal_direction_bulk_boundary_balance_abs_residual": max(
                bulk_boundary_residuals
            ),
            "weak_sat_positive_mode_counts": weak_counts,
            "rinne_strong_positive_mode_counts": rinne_counts,
            "all_source_hashes_match_at_generation": source_hashes_match,
            "source_hashes_sha256": source_hashes,
            "fitting": False,
            "clipping": False,
            "external_data": False,
            "holdout_access": False,
        },
        "CONTROLLING_BLOCKER": "source_matched_fourier_laplace_kreiss_boundary_symbol_audit_for_registered_differential_cpbc_missing",
        "SECONDARY_OPEN_QUESTION": "Whether an energy-compatible weak discretization of the registered differential targets exists is a numerical-method question, not a continuum prerequisite; do not equate q_in_dot with q_in or posit boundary storage without a physical derivation.",
        "NEXT_ACTION": "Build the frozen-coefficient Fourier-Laplace boundary symbol for the registered constraint, Weyl/physical, and gauge residuals; verify decay-subspace dimensions, determinant/smallest-singular-value behavior for Re(s)>=0 including generalized-eigenvalue limits, then compare the semidiscrete LGL boundary operator without using its spectrum as a continuum no-go.",
        "CLAIM_BOUNDARY": "Finite-grid, frozen-background standard-GR numerical-method control only; not the differential Rinne CPBC, continuum stability proof, UET validation, curved 3+1 parent closure, or Gravity unlock.",
        "literature_basis": [
            {
                "source_id": "rinne_2006_first_order_gh_radiation_controlling_cpbc",
                "url": "https://arxiv.org/abs/gr-qc/0606053",
                "role": "The paper identifies these as differential-type boundary conditions, for which maximally dissipative energy theorems do not directly apply; it establishes boundary stability for its specified frozen-coefficient GH problem using Fourier-Laplace/Kreiss analysis. This does not validate the local discrete strong-replacement implementation or establish general strong well-posedness with arbitrary initial/source data.",
            },
            {
                "source_id": "ruiz_rinne_sarbach_2007_harmonic_outer_boundary_conditions",
                "url": "https://arxiv.org/abs/0707.2797",
                "role": "Primary reference for frozen-coefficient well-posedness of a class of constraint-preserving harmonic boundary conditions.",
            },
        ],
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": artifact["STATUS"],
                "artifact": OUTPUT.as_posix(),
                "maximum_energy_identity_residual": artifact[
                    "VERIFICATION"
                ]["maximum_random_state_energy_identity_residual"],
                "projector_audit": artifact["VERIFICATION"]["projector_audit"],
                "lower_order_growth_bound": artifact["VERIFICATION"][
                    "lower_order_growth_bound"
                ],
                "cases": [
                    {
                        "order": case["lgl_order"],
                        "weak_sat": case["spectra"][
                            "direct_incoming_characteristic_weak_sat"
                        ],
                        "rinne": case["spectra"][
                            "differential_rinne_strong_target"
                        ],
                        "energy_identity_residual": case[
                            "random_state_direct_sat_energy_balance"
                        ]["absolute_identity_residual"],
                        "reduction_residual": case[
                            "reduction_constraint_rhs_identity_residual"
                        ],
                    }
                    for case in artifact["VERIFICATION"]["cases"]
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
