"""First-order generalized-harmonic principal-system research contract.

This module implements the source-locked principal part of the Lindblom et al.
first-order GH system and its reduction-constraint damping term. It is not a
complete nonlinear Einstein evolution system or a time integrator.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import numpy as np

from .uet_curved_3p1_geometry import periodic_central_derivative


GH_PRINCIPAL_SYSTEM_STATUS: Final[str] = (
    "GH_PRINCIPAL_CHARACTERISTIC_SYSTEM_READY_EVOLUTION_OPEN"
)


def _finite_array(value: Any, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _spacing_tuple(spacing: Any) -> tuple[float, float, float]:
    values = tuple(float(value) for value in spacing)
    if len(values) != 3:
        raise ValueError("spacing must contain three values")
    if any(not isfinite(value) or value <= 0.0 for value in values):
        raise ValueError("spacing values must be finite and positive")
    return values


def _unit_direction(direction: Any) -> np.ndarray:
    vector = _finite_array(direction, "direction")
    if vector.shape != (3,):
        raise ValueError("direction must have shape (3,)")
    norm = float(np.linalg.norm(vector))
    if norm <= 0.0:
        raise ValueError("direction must be nonzero")
    return vector / norm


def _tangent_basis(normal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    seed = np.array([1.0, 0.0, 0.0])
    if abs(float(normal @ seed)) > 0.8:
        seed = np.array([0.0, 1.0, 0.0])
    first = seed - float(seed @ normal) * normal
    first /= np.linalg.norm(first)
    second = np.cross(normal, first)
    second /= np.linalg.norm(second)
    return first, second


@dataclass(frozen=True)
class GHParameters:
    lapse: float = 1.0
    shift: tuple[float, float, float] = (0.0, 0.0, 0.0)
    gamma0: float = 1.0
    gamma1: float = -1.0
    gamma2: float = 1.0
    symmetrizer_lambda: float = 2.0

    def __post_init__(self) -> None:
        values = (self.lapse, self.gamma0, self.gamma1, self.gamma2, self.symmetrizer_lambda)
        if any(not isfinite(float(value)) for value in values):
            raise ValueError("GH parameters must be finite")
        if self.lapse <= 0.0:
            raise ValueError("lapse must be positive")
        if len(self.shift) != 3 or any(not isfinite(float(value)) for value in self.shift):
            raise ValueError("shift must contain three finite values")
        if self.gamma0 <= 0.0 or self.gamma2 <= 0.0:
            raise ValueError("gamma0 and gamma2 must be positive")
        if self.gamma1 != -1.0:
            raise ValueError("the preregistered linearly-degenerate branch requires gamma1=-1")
        if self.symmetrizer_lambda**2 <= self.gamma2**2:
            raise ValueError("symmetrizer_lambda^2 must exceed gamma2^2")

    @property
    def gamma3(self) -> float:
        return self.gamma1 * self.gamma2


@dataclass(frozen=True)
class GHNonlinearParameters:
    gamma0: float = 1.0
    gamma1: float = -1.0
    gamma2: float = 1.0

    def __post_init__(self) -> None:
        if any(not isfinite(float(value)) for value in (self.gamma0, self.gamma1, self.gamma2)):
            raise ValueError("nonlinear GH parameters must be finite")
        if self.gamma0 <= 0.0 or self.gamma2 <= 0.0:
            raise ValueError("gamma0 and gamma2 must be positive")
        if self.gamma1 != -1.0:
            raise ValueError("the preregistered linearly-degenerate branch requires gamma1=-1")

    @property
    def gamma3(self) -> float:
        return self.gamma1 * self.gamma2


@dataclass(frozen=True)
class GHPrincipalSymbolResult:
    matrix: np.ndarray
    characteristic_transform: np.ndarray
    characteristic_speeds: np.ndarray
    symmetrizer: np.ndarray
    eigenvector_rank: int
    transform_condition_number: float
    characteristic_residual: float
    symmetrizer_residual: float
    minimum_symmetrizer_eigenvalue: float
    normal: np.ndarray


@dataclass(frozen=True)
class GHLinearRHS:
    metric_rhs: np.ndarray
    normal_derivative_rhs: np.ndarray
    spatial_derivative_rhs: np.ndarray
    diagnostics: dict[str, Any]


@dataclass(frozen=True)
class GHKinematics:
    inverse_metric: np.ndarray
    lapse: np.ndarray
    shift: np.ndarray
    unit_normal: np.ndarray
    unit_normal_covector: np.ndarray
    spatial_inverse_metric: np.ndarray


@dataclass(frozen=True)
class GHNonlinearVacuumRHS:
    metric_rhs: np.ndarray
    normal_derivative_rhs: np.ndarray
    spatial_derivative_rhs: np.ndarray
    gauge_constraint: np.ndarray
    lowered_christoffel: np.ndarray
    kinematics: GHKinematics
    diagnostics: dict[str, Any]


def gh_principal_symbol(
    direction: Any,
    parameters: GHParameters = GHParameters(),
) -> GHPrincipalSymbolResult:
    """Return the one-metric-component local-orthonormal GH symbol."""

    normal = _unit_direction(direction)
    tangent_1, tangent_2 = _tangent_basis(normal)
    alpha = float(parameters.lapse)
    beta = np.asarray(parameters.shift, dtype=float)
    beta_normal = float(beta @ normal)
    gamma1 = float(parameters.gamma1)
    gamma2 = float(parameters.gamma2)
    gamma3 = float(parameters.gamma3)

    matrix = np.zeros((5, 5), dtype=float)
    matrix[0, 0] = -(1.0 + gamma1) * beta_normal
    matrix[1, 0] = -gamma3 * beta_normal
    matrix[1, 1] = -beta_normal
    matrix[1, 2:] = alpha * normal
    matrix[2:, 0] = -gamma2 * alpha * normal
    matrix[2:, 1] = alpha * normal
    matrix[2:, 2:] = -beta_normal * np.eye(3)

    transform = np.zeros((5, 5), dtype=float)
    transform[0, 0] = 1.0
    transform[1, :2] = (-gamma2, 1.0)
    transform[1, 2:] = normal
    transform[2, :2] = (-gamma2, 1.0)
    transform[2, 2:] = -normal
    transform[3, 2:] = tangent_1
    transform[4, 2:] = tangent_2
    speeds = np.array(
        [
            -(1.0 + gamma1) * beta_normal,
            -beta_normal + alpha,
            -beta_normal - alpha,
            -beta_normal,
            -beta_normal,
        ],
        dtype=float,
    )

    symmetrizer = np.eye(5, dtype=float)
    symmetrizer[0, 0] = parameters.symmetrizer_lambda**2
    symmetrizer[0, 1] = symmetrizer[1, 0] = -gamma2
    characteristic_residual = float(
        np.max(np.abs(transform @ matrix - speeds[:, None] * transform))
    )
    symmetrizer_residual = float(
        np.max(np.abs(symmetrizer @ matrix - matrix.T @ symmetrizer))
    )
    return GHPrincipalSymbolResult(
        matrix=matrix,
        characteristic_transform=transform,
        characteristic_speeds=speeds,
        symmetrizer=symmetrizer,
        eigenvector_rank=int(np.linalg.matrix_rank(transform, tol=1e-12)),
        transform_condition_number=float(np.linalg.cond(transform)),
        characteristic_residual=characteristic_residual,
        symmetrizer_residual=symmetrizer_residual,
        minimum_symmetrizer_eigenvalue=float(np.min(np.linalg.eigvalsh(symmetrizer))),
        normal=normal,
    )


def gh_characteristic_fields(
    metric: float,
    normal_derivative: float,
    spatial_derivative: Any,
    direction: Any,
    parameters: GHParameters = GHParameters(),
) -> np.ndarray:
    spatial = _finite_array(spatial_derivative, "spatial_derivative")
    if spatial.shape != (3,):
        raise ValueError("spatial_derivative must have shape (3,)")
    state = np.concatenate(([float(metric), float(normal_derivative)], spatial))
    return gh_principal_symbol(direction, parameters).characteristic_transform @ state


def reconstruct_gh_state(
    characteristic_fields: Any,
    direction: Any,
    parameters: GHParameters = GHParameters(),
) -> np.ndarray:
    fields = _finite_array(characteristic_fields, "characteristic_fields")
    if fields.shape != (5,):
        raise ValueError("characteristic_fields must have shape (5,)")
    transform = gh_principal_symbol(direction, parameters).characteristic_transform
    return np.linalg.solve(transform, fields)


def gh_reduction_constraint(metric: Any, spatial_derivative: Any, spacing: Any) -> np.ndarray:
    psi = _finite_array(metric, "metric")
    phi = _finite_array(spatial_derivative, "spatial_derivative")
    if psi.ndim != 5 or psi.shape[-2:] != (4, 4):
        raise ValueError("metric must have shape (nx, ny, nz, 4, 4)")
    if phi.shape != psi.shape[:3] + (3, 4, 4):
        raise ValueError("spatial_derivative must have shape (nx, ny, nz, 3, 4, 4)")
    steps = _spacing_tuple(spacing)
    gradient = np.stack(
        [periodic_central_derivative(psi, axis=i, spacing=steps[i]) for i in range(3)],
        axis=3,
    )
    return gradient - phi


def gh_curl_constraint(spatial_derivative: Any, spacing: Any) -> np.ndarray:
    phi = _finite_array(spatial_derivative, "spatial_derivative")
    if phi.ndim != 6 or phi.shape[3:] != (3, 4, 4):
        raise ValueError("spatial_derivative must have shape (nx, ny, nz, 3, 4, 4)")
    steps = _spacing_tuple(spacing)
    curl = np.zeros(phi.shape[:3] + (3, 3, 4, 4), dtype=float)
    for i in range(3):
        for j in range(3):
            curl[..., i, j, :, :] = (
                periodic_central_derivative(phi[..., j, :, :], axis=i, spacing=steps[i])
                - periodic_central_derivative(phi[..., i, :, :], axis=j, spacing=steps[j])
            )
    return curl


def gh_gauge_constraint(
    spacetime_metric: Any,
    normal_derivative: Any,
    spatial_derivative: Any,
    gauge_source: Any,
    unit_normal: Any,
) -> np.ndarray:
    """Evaluate Eq. (40) of Lindblom et al. at one spacetime point."""

    psi = _finite_array(spacetime_metric, "spacetime_metric")
    pi = _finite_array(normal_derivative, "normal_derivative")
    phi = _finite_array(spatial_derivative, "spatial_derivative")
    source = _finite_array(gauge_source, "gauge_source")
    normal = _finite_array(unit_normal, "unit_normal")
    if psi.shape != (4, 4) or pi.shape != (4, 4) or phi.shape != (3, 4, 4):
        raise ValueError("expected psi/pi/phi shapes (4,4), (4,4), and (3,4,4)")
    if source.shape != (4,) or normal.shape != (4,):
        raise ValueError("gauge_source and unit_normal must have shape (4,)")
    if not np.allclose(psi, psi.T, atol=1e-12, rtol=0.0):
        raise ValueError("spacetime_metric must be symmetric")
    inverse = np.linalg.inv(psi)
    eigenvalues = np.linalg.eigvalsh(psi)
    if np.count_nonzero(eigenvalues < 0.0) != 1:
        raise ValueError("spacetime_metric must have Lorentzian (-,+,+,+) signature")
    normal_cov = psi @ normal
    if not np.isclose(float(normal_cov @ normal), -1.0, atol=1e-10, rtol=0.0):
        raise ValueError("unit_normal must be future/past timelike unit normalized")

    spatial_inverse = inverse[1:, 1:] + np.outer(normal[1:], normal[1:])
    projector_a_i = np.eye(4)[:, 1:] + np.outer(normal_cov, normal[1:])
    constraint = source.copy()
    for a in range(4):
        constraint[a] += np.einsum("ij,ij->", spatial_inverse, phi[:, 1:, a])
        constraint[a] += np.einsum("b,b->", normal, pi[:, a])
        constraint[a] -= 0.5 * np.einsum("i,bc,ibc->", projector_a_i[a], inverse, phi)
        constraint[a] -= 0.5 * normal_cov[a] * np.einsum("bc,bc->", inverse, pi)
    return constraint


def derive_gh_kinematics(spacetime_metric: Any) -> GHKinematics:
    """Derive lapse, shift, normal, and spatial inverse metric from psi_ab."""

    psi = _finite_array(spacetime_metric, "spacetime_metric")
    if psi.ndim < 2 or psi.shape[-2:] != (4, 4):
        raise ValueError("spacetime_metric must end with shape (4,4)")
    if not np.allclose(psi, np.swapaxes(psi, -1, -2), atol=1e-12, rtol=0.0):
        raise ValueError("spacetime_metric must be symmetric")
    eigenvalues = np.linalg.eigvalsh(psi)
    if not np.all(np.sum(eigenvalues < 0.0, axis=-1) == 1):
        raise ValueError("spacetime_metric must have Lorentzian (-,+,+,+) signature")
    inverse = np.linalg.inv(psi)
    if np.any(inverse[..., 0, 0] >= 0.0):
        raise ValueError("t=constant slices require inverse_metric[0,0] < 0")
    lapse = 1.0 / np.sqrt(-inverse[..., 0, 0])
    shift = lapse[..., None] ** 2 * inverse[..., 0, 1:]
    normal = np.concatenate(
        ((1.0 / lapse)[..., None], -shift / lapse[..., None]), axis=-1
    )
    normal_covector = np.einsum("...ab,...b->...a", psi, normal)
    spatial_inverse = inverse[..., 1:, 1:] + np.einsum(
        "...i,...j->...ij", normal[..., 1:], normal[..., 1:]
    )
    if np.any(np.linalg.eigvalsh(spatial_inverse) <= 0.0):
        raise ValueError("derived spatial inverse metric must be positive definite")
    return GHKinematics(
        inverse_metric=inverse,
        lapse=lapse,
        shift=shift,
        unit_normal=normal,
        unit_normal_covector=normal_covector,
        spatial_inverse_metric=spatial_inverse,
    )


def reconstruct_metric_derivatives(
    normal_derivative: Any,
    spatial_derivative: Any,
    kinematics: GHKinematics,
) -> np.ndarray:
    """Reconstruct partial_c psi_ab from Eqs. (38)-(39)."""

    pi = _finite_array(normal_derivative, "normal_derivative")
    phi = _finite_array(spatial_derivative, "spatial_derivative")
    if pi.shape[-2:] != (4, 4) or phi.shape != pi.shape[:-2] + (3, 4, 4):
        raise ValueError("normal/spatial derivative shapes are inconsistent")
    time_derivative = (
        -kinematics.lapse[..., None, None] * pi
        + np.einsum("...i,...iab->...ab", kinematics.shift, phi)
    )
    return np.concatenate((time_derivative[..., None, :, :], phi), axis=-3)


def lowered_christoffel_from_gh_state(
    normal_derivative: Any,
    spatial_derivative: Any,
    kinematics: GHKinematics,
) -> np.ndarray:
    """Compute Gamma_abc from first-order GH metric derivatives."""

    derivative = reconstruct_metric_derivatives(
        normal_derivative, spatial_derivative, kinematics
    )
    connection = np.empty(derivative.shape[:-3] + (4, 4, 4), dtype=float)
    for a in range(4):
        for b in range(4):
            for c in range(4):
                connection[..., a, b, c] = 0.5 * (
                    derivative[..., b, a, c]
                    + derivative[..., c, a, b]
                    - derivative[..., a, b, c]
                )
    return connection


def gh_gauge_constraint_grid(
    spacetime_metric: Any,
    normal_derivative: Any,
    spatial_derivative: Any,
    gauge_source: Any,
    kinematics: GHKinematics | None = None,
) -> np.ndarray:
    """Vectorized first-order GH gauge constraint from Eq. (40)."""

    psi = _finite_array(spacetime_metric, "spacetime_metric")
    pi = _finite_array(normal_derivative, "normal_derivative")
    phi = _finite_array(spatial_derivative, "spatial_derivative")
    source = _finite_array(gauge_source, "gauge_source")
    if pi.shape != psi.shape or phi.shape != psi.shape[:-2] + (3, 4, 4):
        raise ValueError("GH state shapes are inconsistent")
    if source.shape != psi.shape[:-2] + (4,):
        raise ValueError("gauge_source must have shape grid+(4,)")
    kin = derive_gh_kinematics(psi) if kinematics is None else kinematics
    projector_a_i = (
        np.eye(4)[:, 1:]
        + kin.unit_normal_covector[..., :, None] * kin.unit_normal[..., None, 1:]
    )
    constraint = source.copy()
    constraint += np.einsum(
        "...ij,...ija->...a", kin.spatial_inverse_metric, phi[..., :, 1:, :]
    )
    constraint += np.einsum("...b,...ba->...a", kin.unit_normal, pi)
    constraint -= 0.5 * np.einsum(
        "...ai,...bc,...ibc->...a",
        projector_a_i,
        kin.inverse_metric,
        phi,
    )
    pi_trace = np.einsum("...bc,...bc->...", kin.inverse_metric, pi)
    constraint -= 0.5 * kin.unit_normal_covector * pi_trace[..., None]
    return constraint


def gh_gamma0_damping_term(
    spacetime_metric: Any,
    gauge_constraint: Any,
    kinematics: GHKinematics,
    gamma0: float,
) -> np.ndarray:
    """Return the algebraic gamma0 term in Eq. (36)."""

    psi = _finite_array(spacetime_metric, "spacetime_metric")
    constraint = _finite_array(gauge_constraint, "gauge_constraint")
    rate = float(gamma0)
    if not isfinite(rate) or rate <= 0.0:
        raise ValueError("gamma0 must be finite and positive")
    if constraint.shape != psi.shape[:-2] + (4,):
        raise ValueError("gauge_constraint must have shape grid+(4,)")
    normal_contraction = np.einsum(
        "...c,...c->...", kinematics.unit_normal, constraint
    )
    bracket = (
        np.einsum(
            "...a,...b->...ab", constraint, kinematics.unit_normal_covector
        )
        + np.einsum(
            "...a,...b->...ab", kinematics.unit_normal_covector, constraint
        )
        - psi * normal_contraction[..., None, None]
    )
    return kinematics.lapse[..., None, None] * rate * bracket


def compute_nonlinear_vacuum_gh_rhs(
    spacetime_metric: Any,
    normal_derivative: Any,
    spatial_derivative: Any,
    gauge_source: Any,
    gauge_source_covariant_derivative: Any,
    spacing: Any,
    parameters: GHNonlinearParameters = GHNonlinearParameters(),
) -> GHNonlinearVacuumRHS:
    """Evaluate source-locked vacuum Eqs. (35)-(37) on a periodic grid."""

    psi = _finite_array(spacetime_metric, "spacetime_metric")
    pi = _finite_array(normal_derivative, "normal_derivative")
    phi = _finite_array(spatial_derivative, "spatial_derivative")
    source = _finite_array(gauge_source, "gauge_source")
    source_covariant_derivative = _finite_array(
        gauge_source_covariant_derivative, "gauge_source_covariant_derivative"
    )
    if psi.ndim != 5 or psi.shape[-2:] != (4, 4) or pi.shape != psi.shape:
        raise ValueError("spacetime_metric and normal_derivative must have shape (nx,ny,nz,4,4)")
    if phi.shape != psi.shape[:3] + (3, 4, 4):
        raise ValueError("spatial_derivative must have shape (nx,ny,nz,3,4,4)")
    if source.shape != psi.shape[:3] + (4,):
        raise ValueError("gauge_source must have shape (nx,ny,nz,4)")
    if source_covariant_derivative.shape != psi.shape[:3] + (4, 4):
        raise ValueError("gauge_source_covariant_derivative must have shape (nx,ny,nz,4,4)")
    if any(size < 5 for size in psi.shape[:3]):
        raise ValueError("each periodic grid axis must contain at least five points")
    steps = _spacing_tuple(spacing)
    kin = derive_gh_kinematics(psi)
    connection = lowered_christoffel_from_gh_state(pi, phi, kin)
    constraint = gh_gauge_constraint_grid(psi, pi, phi, source, kin)

    d_psi = [periodic_central_derivative(psi, axis=k, spacing=steps[k]) for k in range(3)]
    d_pi = [periodic_central_derivative(pi, axis=k, spacing=steps[k]) for k in range(3)]
    d_phi = [periodic_central_derivative(phi, axis=k, spacing=steps[k]) for k in range(3)]
    adv_psi = sum(kin.shift[..., k, None, None] * d_psi[k] for k in range(3))
    adv_pi = sum(kin.shift[..., k, None, None] * d_pi[k] for k in range(3))
    adv_phi = sum(kin.shift[..., k, None, None, None] * d_phi[k] for k in range(3))
    shift_phi = np.einsum("...i,...iab->...ab", kin.shift, phi)
    divergence_phi = np.zeros_like(pi)
    for k in range(3):
        for i in range(3):
            divergence_phi += (
                kin.spatial_inverse_metric[..., k, i, None, None]
                * d_phi[k][..., i, :, :]
            )
    gradient_pi = np.stack(d_pi, axis=3)
    gradient_psi = np.stack(d_psi, axis=3)

    metric_rhs = (
        (1.0 + parameters.gamma1) * adv_psi
        - kin.lapse[..., None, None] * pi
        - parameters.gamma1 * shift_phi
    )
    pi_rhs = (
        adv_pi
        - kin.lapse[..., None, None] * divergence_phi
        + parameters.gamma3 * adv_psi
    )

    quadratic_phi = np.einsum(
        "...cd,...ij,...ica,...jdb->...ab",
        kin.inverse_metric,
        kin.spatial_inverse_metric,
        phi,
        phi,
    )
    quadratic_pi = np.einsum(
        "...cd,...ca,...db->...ab", kin.inverse_metric, pi, pi
    )
    quadratic_connection = np.einsum(
        "...cd,...ef,...ace,...bdf->...ab",
        kin.inverse_metric,
        kin.inverse_metric,
        connection,
        connection,
    )
    pi_rhs += 2.0 * kin.lapse[..., None, None] * (
        quadratic_phi - quadratic_pi - quadratic_connection
    )
    pi_rhs -= kin.lapse[..., None, None] * (
        source_covariant_derivative
        + np.swapaxes(source_covariant_derivative, -1, -2)
    )
    normal_pi_scalar = np.einsum(
        "...c,...d,...cd->...", kin.unit_normal, kin.unit_normal, pi
    )
    pi_rhs -= (
        0.5
        * kin.lapse[..., None, None]
        * normal_pi_scalar[..., None, None]
        * pi
    )
    mixed_phi = np.einsum(
        "...c,...ci,...ij,...jab->...ab",
        kin.unit_normal,
        pi[..., :, 1:],
        kin.spatial_inverse_metric,
        phi,
    )
    pi_rhs -= kin.lapse[..., None, None] * mixed_phi
    pi_rhs += gh_gamma0_damping_term(psi, constraint, kin, parameters.gamma0)
    pi_rhs -= parameters.gamma1 * parameters.gamma2 * shift_phi

    phi_rhs = (
        adv_phi
        - kin.lapse[..., None, None, None] * gradient_pi
        + parameters.gamma2 * kin.lapse[..., None, None, None] * gradient_psi
    )
    normal_phi_scalar = np.einsum(
        "...c,...d,...icd->...i", kin.unit_normal, kin.unit_normal, phi
    )
    phi_rhs += (
        0.5
        * kin.lapse[..., None, None, None]
        * normal_phi_scalar[..., :, None, None]
        * pi[..., None, :, :]
    )
    phi_rhs += kin.lapse[..., None, None, None] * np.einsum(
        "...jk,...c,...ijc,...kab->...iab",
        kin.spatial_inverse_metric,
        kin.unit_normal,
        phi[..., :, 1:, :],
        phi,
    )
    phi_rhs -= parameters.gamma2 * kin.lapse[..., None, None, None] * phi

    return GHNonlinearVacuumRHS(
        metric_rhs=metric_rhs,
        normal_derivative_rhs=pi_rhs,
        spatial_derivative_rhs=phi_rhs,
        gauge_constraint=constraint,
        lowered_christoffel=connection,
        kinematics=kin,
        diagnostics={
            "equations": "Lindblom et al. Eqs. 35-40",
            "matter_source": "VACUUM_ONLY",
            "gauge_source_role": "DECLARED_ALGEBRAIC_INPUT",
            "gauge_source_covariant_derivative_role": "DECLARED_INPUT_NOT_NUMERICALLY_INFERRED",
            "time_integrator": None,
            "constraint_preserving_boundaries": "NOT_IMPLEMENTED",
            "field_clipping": False,
            "parameter_fitting": False,
        },
    )


def compute_linear_gh_reduction_damped_rhs(
    metric: Any,
    normal_derivative: Any,
    spatial_derivative: Any,
    spacing: Any,
    parameters: GHParameters = GHParameters(),
) -> GHLinearRHS:
    """Evaluate the constant-coefficient principal/reduction-damping operator."""

    psi = _finite_array(metric, "metric")
    pi = _finite_array(normal_derivative, "normal_derivative")
    phi = _finite_array(spatial_derivative, "spatial_derivative")
    if psi.ndim != 5 or psi.shape[-2:] != (4, 4) or pi.shape != psi.shape:
        raise ValueError("metric and normal_derivative must have shape (nx,ny,nz,4,4)")
    if phi.shape != psi.shape[:3] + (3, 4, 4):
        raise ValueError("spatial_derivative must have shape (nx,ny,nz,3,4,4)")
    if any(size < 5 for size in psi.shape[:3]):
        raise ValueError("each periodic grid axis must contain at least five points")
    steps = _spacing_tuple(spacing)
    beta = np.asarray(parameters.shift, dtype=float)
    alpha = float(parameters.lapse)
    d_psi = [periodic_central_derivative(psi, axis=k, spacing=steps[k]) for k in range(3)]
    d_pi = [periodic_central_derivative(pi, axis=k, spacing=steps[k]) for k in range(3)]
    d_phi = [periodic_central_derivative(phi, axis=k, spacing=steps[k]) for k in range(3)]
    adv_psi = sum(beta[k] * d_psi[k] for k in range(3))
    adv_pi = sum(beta[k] * d_pi[k] for k in range(3))
    adv_phi = sum(beta[k] * d_phi[k] for k in range(3))
    beta_phi = np.einsum("i,...iab->...ab", beta, phi)
    divergence_phi = sum(d_phi[i][..., i, :, :] for i in range(3))
    gradient_pi = np.stack(d_pi, axis=3)
    gradient_psi = np.stack(d_psi, axis=3)

    metric_rhs = (
        (1.0 + parameters.gamma1) * adv_psi
        - alpha * pi
        - parameters.gamma1 * beta_phi
    )
    pi_rhs = adv_pi - alpha * divergence_phi + parameters.gamma3 * adv_psi
    phi_rhs = (
        adv_phi
        - alpha * gradient_pi
        + parameters.gamma2 * alpha * gradient_psi
        - parameters.gamma2 * alpha * phi
    )
    return GHLinearRHS(
        metric_rhs=metric_rhs,
        normal_derivative_rhs=pi_rhs,
        spatial_derivative_rhs=phi_rhs,
        diagnostics={
            "operator_scope": "constant-coefficient principal part plus C_iab damping",
            "gamma3_equals_gamma1_gamma2": parameters.gamma3 == parameters.gamma1 * parameters.gamma2,
            "time_integrator": None,
            "nonlinear_algebraic_einstein_terms": "NOT_IMPLEMENTED",
            "gauge_constraint_gamma0_damping_rhs": "NOT_IMPLEMENTED",
            "field_clipping": False,
            "parameter_fitting": False,
        },
    )


def generalized_harmonic_contract() -> dict[str, Any]:
    return {
        "status": GH_PRINCIPAL_SYSTEM_STATUS,
        "source": "Lindblom et al. 2006, arXiv:gr-qc/0512093v3, Eqs. 6, 12, 26-40",
        "state": ["psi_ab", "Pi_ab", "Phi_iab"],
        "excluded_state": ["UET Phi", "UET Pi", "C", "R_gen", "R_obs"],
        "relations": {
            "gauge_constraint": "C_a = H_a + Gamma_a",
            "reduction_constraint": "C_iab = partial_i psi_ab - Phi_iab",
            "gamma3": "gamma3 = gamma1 gamma2",
            "characteristic_0": "u0_ab = psi_ab",
            "characteristic_pm": "u1pm_ab = Pi_ab +/- n^i Phi_iab - gamma2 psi_ab",
            "characteristic_2": "u2_iab = P_i^k Phi_kab",
            "speeds": "{-(1+gamma1) beta_n, -beta_n +/- alpha, -beta_n}",
            "symmetrizer_condition": "Lambda^2 > gamma2^2",
        },
        "implemented": [
            "source-locked first-order principal matrix",
            "complete characteristic transform",
            "analytic positive symmetrizer",
            "gauge/reduction/curl constraint evaluators",
            "constant-coefficient reduction-damped periodic operator",
            "complete nonlinear vacuum GH algebraic right-hand sides for declared H_a and nabla_a H_b",
            "gamma0 gauge-constraint damping term in the nonlinear vacuum RHS",
        ],
        "not_implemented": [
            "time integration and CFL policy",
            "constraint propagation convergence",
            "constraint-preserving boundaries",
            "matter stress-energy wiring and detector observable map",
        ],
        "claim_boundary": (
            "source-locked vacuum GH RHS and principal/constraint operators only; "
            "not a time-integrated numerical-relativity solver, matter-coupled system, or UET validation"
        ),
    }


__all__ = [
    "GH_PRINCIPAL_SYSTEM_STATUS",
    "GHParameters",
    "GHNonlinearParameters",
    "GHPrincipalSymbolResult",
    "GHLinearRHS",
    "GHKinematics",
    "GHNonlinearVacuumRHS",
    "gh_principal_symbol",
    "gh_characteristic_fields",
    "reconstruct_gh_state",
    "gh_reduction_constraint",
    "gh_curl_constraint",
    "gh_gauge_constraint",
    "derive_gh_kinematics",
    "reconstruct_metric_derivatives",
    "lowered_christoffel_from_gh_state",
    "gh_gauge_constraint_grid",
    "gh_gamma0_damping_term",
    "compute_linear_gh_reduction_damped_rhs",
    "compute_nonlinear_vacuum_gh_rhs",
    "generalized_harmonic_contract",
]
