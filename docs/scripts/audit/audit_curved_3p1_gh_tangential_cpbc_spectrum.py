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
MODE_AUDIT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_tangential_cpbc_mode.py"
LGL_AUDIT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_tt_sbp_sat_boundary.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_tangential_cpbc_spectrum.json"

_spec = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_tangential_mode_audit", MODE_AUDIT
)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load the matched-profile tangential-mode audit")
MODE = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = MODE
_spec.loader.exec_module(MODE)

_lgl_spec = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_gh_lgl_sbp_operators", LGL_AUDIT
)
if _lgl_spec is None or _lgl_spec.loader is None:
    raise ImportError("cannot load the registered LGL-SBP operator audit")
LGL = importlib.util.module_from_spec(_lgl_spec)
sys.modules[_lgl_spec.name] = LGL
_lgl_spec.loader.exec_module(LGL)


def _state_size(node_count: int) -> int:
    return node_count * 2 * (2 + 3) * 10


def _unpack(vector: np.ndarray, node_count: int) -> tuple[np.ndarray, ...]:
    block = node_count * 2 * 10
    return (
        vector[:block].reshape(node_count, 2, 10),
        vector[block : 2 * block].reshape(node_count, 2, 10),
        vector[2 * block :].reshape(node_count, 2, 3, 10),
    )


def _flatten(state: tuple[np.ndarray, ...]) -> np.ndarray:
    return np.concatenate([value.ravel() for value in state])


def _bulk_rhs(
    grid: Any, state: tuple[np.ndarray, ...], gamma2: float, gamma0: float
) -> tuple[np.ndarray, ...]:
    metric, pi, phi = state
    dx_metric, dx_pi, dx_phi, dy_metric, dy_pi, dy_phi = MODE._derivatives(
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
            metric_tensor = MODE.SLAB.unpack_symmetric(metric[node, phase])
            pi_tensor = MODE.SLAB.unpack_symmetric(pi[node, phase])
            phi_tensors = MODE._unpack_grid(phi[node, phase])
            damping = MODE._gamma0_source(
                metric_tensor, pi_tensor, phi_tensors, gamma0
            )
            pi_rhs[node, phase] += MODE.SLAB.pack_symmetric(damping)
    return metric_rhs, pi_rhs, phi_rhs


def _energy_matrix(
    node_count: int, spatial_weights: np.ndarray, gamma2: float = 1.0
) -> np.ndarray:
    component_weights = MODE.TENSOR_WEIGHTS
    block = node_count * 2 * 10
    matrix = np.zeros((_state_size(node_count), _state_size(node_count)))

    for node in range(node_count):
        for phase in range(2):
            for component in range(10):
                weight = spatial_weights[node] * component_weights[component]
                metric_index = (node * 2 + phase) * 10 + component
                pi_index = block + metric_index
                matrix[metric_index, metric_index] = 4.0 * weight
                matrix[pi_index, pi_index] = weight
                matrix[metric_index, pi_index] = -gamma2 * weight
                matrix[pi_index, metric_index] = -gamma2 * weight
                for direction in range(3):
                    phi_index = 2 * block + (
                        (node * 2 + phase) * 3 + direction
                    ) * 10 + component
                    matrix[phi_index, phi_index] = weight
    return matrix


def _assemble_rhs_matrix(grid: Any, gamma2: float, gamma0: float) -> np.ndarray:
    dimension = _state_size(grid.node_count)
    operator = np.empty((dimension, dimension), dtype=float)
    basis = np.zeros(dimension, dtype=float)
    for column in range(dimension):
        basis[column] = 1.0
        rhs = MODE._rhs(grid, _unpack(basis, grid.node_count), gamma2, gamma0)
        operator[:, column] = _flatten(rhs)
        basis[column] = 0.0
    return operator


def _boundary_sector_fractions(
    state: tuple[np.ndarray, ...], gamma2: float
) -> dict[str, Any]:
    metric, pi, phi = state
    result: dict[str, Any] = {}
    for face, normal, label in (
        (0, -1.0, "left"),
        (metric.shape[0] - 1, 1.0, "right"),
    ):
        projectors = MODE.PROJECTORS.build_gh_boundary_projectors(
            np.array([normal, 0.0, 0.0])
        )
        projector_map = {
            "constraint": projectors.constraint,
            "physical": projectors.physical,
            "gauge": projectors.gauge,
        }
        norms = {name: 0.0 for name in projector_map}
        for phase in range(2):
            psi_tensor = MODE.SLAB.unpack_symmetric(metric[face, phase])
            pi_tensor = MODE.SLAB.unpack_symmetric(pi[face, phase])
            phi_tensor = MODE._unpack_grid(phi[face, phase])
            incoming = MODE.SLAB.pack_symmetric(
                pi_tensor - normal * phi_tensor[0] - gamma2 * psi_tensor
            )
            for name, projector in projector_map.items():
                projected = projector @ incoming
                norms[name] += float(
                    np.dot(projected * MODE.TENSOR_WEIGHTS, projected)
                )
        total = sum(norms.values())
        result[label] = {
            "projected_incoming_norm_squared": total,
            "sector_fractions": {
                name: value / total for name, value in norms.items()
            },
        }
    return result


def _case(
    degree: int, wave_number: float, operator_family: str
) -> dict[str, Any]:
    gamma0 = 1.0
    gamma2 = 1.0
    grid = MODE.TangentialGrid(degree, wave_number)
    if operator_family == "chebyshev_clenshaw_curtis":
        spatial_weights = MODE.REFERENCE._clenshaw_curtis_weights(degree)
    elif operator_family == "legendre_gauss_lobatto_sbp":
        sbp_operators = LGL.legendre_lobatto_operators(degree)
        grid.nodes = sbp_operators.nodes
        grid.derivative = sbp_operators.derivative
        grid.node_count = len(grid.nodes)
        spatial_weights = sbp_operators.norm_weights
    else:
        raise ValueError(f"unknown normal operator family: {operator_family}")

    norm_matrix = np.diag(spatial_weights)
    boundary_form = np.zeros_like(norm_matrix)
    boundary_form[0, 0] = -1.0
    boundary_form[-1, -1] = 1.0
    sbp_residual = (
        norm_matrix @ grid.derivative
        + grid.derivative.T @ norm_matrix
        - boundary_form
    )
    sbp_scale = max(
        float(np.linalg.norm(norm_matrix @ grid.derivative, ord="fro")),
        float(np.linalg.norm(boundary_form, ord="fro")),
        1.0,
    )
    sbp_relative_residual = float(
        np.linalg.norm(sbp_residual, ord="fro") / sbp_scale
    )
    roundoff_tolerance = 1000.0 * np.finfo(float).eps
    operator = _assemble_rhs_matrix(grid, gamma2, gamma0)
    energy = _energy_matrix(grid.node_count, spatial_weights, gamma2)
    factor = np.linalg.cholesky(energy)

    symmetric_rate = 0.5 * (energy @ operator + operator.T @ energy)
    left_whitened = np.linalg.solve(factor, symmetric_rate)
    energy_rate_operator = np.linalg.solve(factor, left_whitened.T).T
    energy_rate_operator = 0.5 * (energy_rate_operator + energy_rate_operator.T)
    energy_rates, energy_modes = np.linalg.eigh(energy_rate_operator)
    energy_norm_growth_rate = float(energy_rates[-1])
    optimal_state = np.linalg.solve(factor.T, energy_modes[:, -1])
    optimal_rhs = _flatten(
        MODE._rhs(grid, _unpack(optimal_state, grid.node_count), gamma2, gamma0)
    )
    optimal_bulk_rhs = _flatten(
        _bulk_rhs(grid, _unpack(optimal_state, grid.node_count), gamma2, gamma0)
    )
    optimal_boundary_rhs = optimal_rhs - optimal_bulk_rhs
    optimal_energy = float(0.5 * optimal_state @ (energy @ optimal_state))
    direct_energy_relative_rate = float(
        optimal_state @ (energy @ optimal_rhs) / optimal_energy
    )
    bulk_energy_relative_rate = float(
        optimal_state @ (energy @ optimal_bulk_rhs) / optimal_energy
    )
    boundary_energy_relative_rate = float(
        optimal_state @ (energy @ optimal_boundary_rhs) / optimal_energy
    )
    state_parts = _unpack(optimal_state, grid.node_count)
    metric_state, pi_state, phi_state = state_parts
    quadrature = spatial_weights[:, None, None]
    local_density = (
        4.0 * metric_state**2
        - 2.0 * gamma2 * metric_state * pi_state
        + pi_state**2
        + np.sum(phi_state**2, axis=2)
    ) * quadrature * MODE.TENSOR_WEIGHTS
    local_energy = 0.5 * np.sum(local_density, axis=(1, 2))
    endpoint_energy_fraction = float(
        (local_energy[0] + local_energy[-1]) / np.sum(local_energy)
    )
    boundary_sectors = _boundary_sector_fractions(state_parts, gamma2)

    eigenvalues = np.linalg.eigvals(operator)
    order = np.argsort(eigenvalues.real)[::-1]
    leading = eigenvalues[order[:8]]

    rng = np.random.default_rng(2400 + degree + int(round(wave_number * 100.0)))
    probe = rng.standard_normal(operator.shape[0])
    direct_rhs = _flatten(
        MODE._rhs(grid, _unpack(probe, grid.node_count), gamma2, gamma0)
    )
    assembled_rhs = operator @ probe
    linearity_residual = float(
        np.linalg.norm(direct_rhs - assembled_rhs)
        / max(np.linalg.norm(direct_rhs), np.linalg.norm(assembled_rhs), 1.0e-300)
    )

    return {
        "normal_operator_family": operator_family,
        "normal_norm_family": (
            "clenshaw_curtis_diagonal_quadrature"
            if operator_family == "chebyshev_clenshaw_curtis"
            else "legendre_gauss_lobatto_diagonal_sbp_norm"
        ),
        "degree": degree,
        "node_count": grid.node_count,
        "state_dimension": int(operator.shape[0]),
        "tangential_wavenumber_over_L0": wave_number,
        "gamma0_L0": gamma0,
        "gamma2_L0": gamma2,
        "spectral_abscissa_over_L0_inverse": float(np.max(eigenvalues.real)),
        "eigenvalue_count_real_part_above_existing_1e-6_tolerance": int(
            np.count_nonzero(eigenvalues.real > 1.0e-6)
        ),
        "leading_eigenvalues_over_L0_inverse": [
            {"real": float(value.real), "imag": float(value.imag)}
            for value in leading
        ],
        "maximum_energy_norm_log_growth_rate_over_L0_inverse": (
            energy_norm_growth_rate
        ),
        "maximum_energy_relative_growth_rate_over_L0_inverse": (
            2.0 * energy_norm_growth_rate
        ),
        "optimal_direction_direct_relative_energy_growth_rate_over_L0_inverse": (
            direct_energy_relative_rate
        ),
        "optimal_direction_bulk_relative_energy_rate_over_L0_inverse": (
            bulk_energy_relative_rate
        ),
        "optimal_direction_boundary_correction_relative_energy_rate_over_L0_inverse": (
            boundary_energy_relative_rate
        ),
        "optimal_direction_bulk_boundary_rate_balance_abs_residual": abs(
            direct_energy_relative_rate
            - bulk_energy_relative_rate
            - boundary_energy_relative_rate
        ),
        "optimal_direction_energy_rate_check_abs_residual": abs(
            direct_energy_relative_rate - 2.0 * energy_norm_growth_rate
        ),
        "optimal_direction_endpoint_energy_fraction": endpoint_energy_fraction,
        "optimal_direction_boundary_projector_fractions": boundary_sectors,
        "minimum_energy_matrix_eigenvalue": float(
            np.linalg.eigvalsh(energy)[0]
        ),
        "operator_assembly_probe_relative_residual": linearity_residual,
        "sbp_identity_relative_frobenius_residual": sbp_relative_residual,
        "sbp_identity_max_abs_residual": float(np.max(np.abs(sbp_residual))),
        "sbp_identity_spectral_norm_residual": float(
            np.linalg.norm(sbp_residual, ord=2)
        ),
        "normal_operator_norm_sbp_compatible_at_roundoff": (
            bool(sbp_relative_residual <= roundoff_tolerance)
        ),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact() -> dict[str, Any]:
    cases = [
        (4, float(np.pi)),
        (8, float(np.pi)),
        (12, float(np.pi)),
        (8, float(0.5 * np.pi)),
        (8, float(2.0 * np.pi)),
    ]
    operator_families = (
        "chebyshev_clenshaw_curtis",
        "legendre_gauss_lobatto_sbp",
    )
    results = [
        _case(degree, wave_number, operator_family)
        for operator_family in operator_families
        for degree, wave_number in cases
    ]
    sources = {
        "spectrum_audit": Path(__file__).resolve(),
        "matched_profile_audit": MODE_AUDIT,
        "lgl_sbp_operator_audit": LGL_AUDIT,
        "reference_audit": MODE.REFERENCE_AUDIT,
        "slab_equations": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_full_u1_slab.py",
        "boundary_residuals": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py",
        "boundary_projectors": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py",
        "canonical_gh_equations": MODE.GH_EQUATIONS,
    }
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in sources.values()
    }
    return {
        "schema_version": "core-curved-3p1-gh-tangential-cpbc-spectrum-v2",
        "artifact": "curved_3p1_gh_tangential_cpbc_spectrum",
        "diagnostic_id": "uet.core.curved_3p1.gh.rinne_tangential_semidiscrete_spectrum",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "major_result_id": "CORE_CURVED_3P1_GH_TANGENTIAL_CPBC_SPECTRAL_ENERGY_SCREEN",
        "closure_level": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": [
            "The exact finite-dimensional matrix of the registered linear one-mode RHS is assembled for the declared degree/wavenumber cases under both normal operator/norm pairings.",
            "The SBP identity residual is measured for each derivative/norm pairing, distinguishing SBP-compatible energy estimates from a quadrature-only diagnostic.",
            "The GH symmetrizer energy matrix is positive definite and its finite-grid logarithmic norm is computed for every assembled case.",
            "A random-vector matrix-application check independently matches each assembled matrix to the direct RHS evaluator.",
            "The maximizing energy-growth direction's instantaneous rate is checked again using the direct RHS rather than only the assembled matrix.",
            "The same directional energy rate is decomposed into the bulk GH RHS and its registered boundary correction, with a closure residual recorded.",
        ],
        "WHAT_REMAINS_OPEN": [
            "The Chebyshev/Clenshaw-Curtis pairing is not SBP-compatible under the diagonal quadrature norm used here; its energy logarithmic norm is only a numerical comparator and cannot support an SBP energy-stability conclusion.",
            "The LGL-SBP results are finite-grid statements for this frozen-background one-mode operator, not continuum or nonlinear initial-boundary well-posedness proofs.",
            "These finite matrices do not prove continuum or nonlinear initial-boundary well-posedness.",
            "The cases omit positive normal shift, incoming u2_A, multiple simultaneous tangential modes, edges/corners, variable coefficients, and matter boundaries.",
            "A positive logarithmic norm is an instantaneous growth direction, not by itself an unstable eigenmode; its degree dependence and any boundary localization require an energy estimate and further resolution studies.",
        ],
        "DEPENDENCY_UNLOCKED": "none; Core curved-3+1 parent remains PARTIAL and Gravity remains blocked",
        "STATUS": "OPEN_MATCHED_OPERATOR_NORM_COMPARISON",
        "WHAT_CHANGED": "Extended the finite-matrix audit to compare Chebyshev/Clenshaw-Curtis against the registered LGL-SBP derivative/norm pair, recording SBP identity defects with spectrum and energy growth.",
        "EQUATION_OR_MAPPING": {
            "semidiscrete_system": "U_dot = A_h(k_y) U, with the registered linear bulk GH equations and projected differential boundary targets",
            "energy": "E = 0.5 U^T M_h U, using the positive GH symmetrizer, the declared normal quadrature/norm, and tensor Frobenius weights",
            "energy_logarithmic_norm": "mu_E = lambda_max(M_h^(-1/2) sym(M_h A_h) M_h^(-1/2)); dE/dt <= 2*mu_E*E",
            "sbp_identity": "H D + D^T H = diag(-1, 0, ..., 0, +1); residual recorded for every normal operator/norm pairing",
            "operator_probe": "Compare A_h*v with direct RHS(v) for a deterministic random vector",
        },
        "PREREGISTRATION": {
            "cases_degree_wavenumber_over_L0": [
                {"degree": degree, "k_y_L0": wave_number}
                for degree, wave_number in cases
            ],
            "normal_operator_families": list(operator_families),
            "gamma0_L0": 1.0,
            "gamma2_L0": 1.0,
            "existing_positive_eigenvalue_reference_tolerance": 1.0e-6,
            "decision_thresholds": "Report only; do not promote status or unlock dependencies",
        },
        "VERIFICATION": {
            "cases": results,
            "operator_family_summaries": {
                family: {
                    "case_count": sum(
                        result["normal_operator_family"] == family
                        for result in results
                    ),
                    "maximum_sbp_identity_relative_frobenius_residual": max(
                        result["sbp_identity_relative_frobenius_residual"]
                        for result in results
                        if result["normal_operator_family"] == family
                    ),
                    "all_cases_sbp_compatible_at_roundoff": all(
                        result["normal_operator_norm_sbp_compatible_at_roundoff"]
                        for result in results
                        if result["normal_operator_family"] == family
                    ),
                    "maximum_spectral_abscissa_over_L0_inverse": max(
                        result["spectral_abscissa_over_L0_inverse"]
                        for result in results
                        if result["normal_operator_family"] == family
                    ),
                    "maximum_energy_norm_log_growth_rate_over_L0_inverse": max(
                        result["maximum_energy_norm_log_growth_rate_over_L0_inverse"]
                        for result in results
                        if result["normal_operator_family"] == family
                    ),
                }
                for family in operator_families
            },
            "lgl_sbp_identity_verified_at_floating_point_roundoff": all(
                result["normal_operator_norm_sbp_compatible_at_roundoff"]
                for result in results
                if result["normal_operator_family"]
                == "legendre_gauss_lobatto_sbp"
            ),
            "maximum_operator_assembly_probe_relative_residual": max(
                result["operator_assembly_probe_relative_residual"]
                for result in results
            ),
            "maximum_optimal_direction_energy_rate_check_abs_residual": max(
                result["optimal_direction_energy_rate_check_abs_residual"]
                for result in results
            ),
            "maximum_bulk_boundary_rate_balance_abs_residual": max(
                result["optimal_direction_bulk_boundary_rate_balance_abs_residual"]
                for result in results
            ),
            "all_energy_matrices_positive_definite": all(
                result["minimum_energy_matrix_eigenvalue"] > 0.0
                for result in results
            ),
            "source_hashes_sha256": source_hashes,
            "fitting": False,
            "clipping": False,
            "external_data": False,
            "holdout_access": False,
        },
        "CONTROLLING_BLOCKER": "full_first_order_gh_differential_cpbc_energy_stability_and_resolution_convergence_missing",
        "NEXT_ACTION": "Interpret the matched LGL-SBP finite-grid spectrum and energy rates first; then derive a projector-aware boundary energy estimate and broaden the resolution/mode screen before positive-shift u2_A or corners.",
        "CLAIM_BOUNDARY": "Finite-dimensional, frozen-background standard-GR linear boundary diagnostic only; not continuum well-posedness, full Rinne CPBC reproduction, curved 3+1 parent closure, UET validation, or Gravity unlock.",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["STATUS"],
                "artifact": OUTPUT.as_posix(),
                "operator_family_summaries": artifact["VERIFICATION"][
                    "operator_family_summaries"
                ],
                "max_probe_residual": artifact["VERIFICATION"][
                    "maximum_operator_assembly_probe_relative_residual"
                ],
                "max_energy_rate_residual": artifact["VERIFICATION"][
                    "maximum_optimal_direction_energy_rate_check_abs_residual"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
