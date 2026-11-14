"""Scheme-dependence witness for finite-temperature condensed stationarity.

The declared Taylor-subtracted Gaussian determinant is compared with one
finite local counterterm that obeys the same value/first/second-derivative
conditions at a reference amplitude.  The two completions are not selected by
external data.  Their different stationary-point behavior therefore closes a
structural identifiability boundary, not a physical phase transition.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_scheme_identifiability import (
    finite_local_counterterm,
)
from docs.core.uet_o2_gaussian_offshell_background import (
    off_shell_curvatures,
    off_shell_mode_omega_sq,
)


@dataclass(frozen=True)
class O2StationaritySchemeDependence:
    """Two finite-temperature stationarity completions under shared anchors."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass_sq: float
    condensate_control: float
    quartic_coupling: float
    x_boundary: float
    reference_x: float
    reference_scale_sq: float
    scheme_a_coefficient: float
    scheme_b_coefficient: float
    scheme_a_boundary_derivative: float
    scheme_a_reference_derivative: float
    scheme_b_boundary_derivative: float
    scheme_b_reference_derivative: float
    scheme_b_stationary_x: float
    scheme_b_stationary_residual: float
    scheme_b_min_low_omega_sq: float
    scheme_b_min_high_omega_sq: float
    scheme_a_grid_min_derivative: float
    scheme_a_grid_max_derivative: float
    scheme_b_grid_min_derivative: float
    scheme_b_grid_max_derivative: float
    quadrature_order: int
    momentum_cutoff: float
    unit_lane: str = "natural"
    vacuum_counterterm_included: bool = True
    condensed_branch_included: bool = False
    physical_kubo_coefficient_included: bool = False
    external_calibration_included: bool = False
    data_role: str = "INTERNAL_SCHEME_IDENTIFIABILITY_NO_GO"


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 32:
        raise ValueError("quadrature_order must be an integer >= 32")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    momenta = 0.5 * cutoff * (nodes + 1.0)
    scaled_weights = 0.5 * cutoff * weights
    return momenta, scaled_weights


def _bose(argument: float, temperature: float) -> float:
    value = _positive(argument / temperature, "Bose argument")
    if value > 50.0:
        return exp(-value)
    return float(1.0 / np.expm1(value))


def _mode_data(
    wavenumber: float,
    x: float,
    chemical_potential: float,
    condensate_control_value: float,
    quartic_coupling: float,
    kinetic_coefficient: float,
) -> tuple[float, float, float, float, float, float]:
    """Return frequencies and first/second derivatives with respect to ``x=A^2``."""

    k = _finite(wavenumber, "wavenumber")
    x = _finite(x, "x")
    if k <= 0.0 or x <= 0.0:
        raise ValueError("stationarity quadrature requires k>0 and x>0")
    mu = _finite(chemical_potential, "chemical_potential")
    z = _positive(kinetic_coefficient, "matter_kinetic")
    lam = _positive(quartic_coupling, "matter_quartic")
    a_sigma = (-condensate_control_value + 3.0 * lam * x) / z
    a_phase = (-condensate_control_value + lam * x) / z
    discriminant = (
        (a_sigma - a_phase) ** 2
        + 8.0 * mu * mu * (a_sigma + a_phase)
        + 16.0 * mu**4
        + 16.0 * mu * mu * k * k
    )
    if discriminant <= 0.0:
        raise FloatingPointError("stationarity mode discriminant must be positive")
    root = sqrt(discriminant)
    base = k * k + 0.5 * (a_sigma + a_phase + 4.0 * mu * mu)
    low_sq = base - 0.5 * root
    high_sq = base + 0.5 * root
    if low_sq <= 0.0 or high_sq <= 0.0:
        raise FloatingPointError("stationarity mode roots must be positive")

    slope = 2.0 * lam / z
    discriminant_first = 2.0 * slope * slope * x + 16.0 * mu * mu * slope
    discriminant_second = 2.0 * slope * slope
    low_first = slope - discriminant_first / (4.0 * root)
    high_first = slope + discriminant_first / (4.0 * root)
    root_second = (
        discriminant_second / (4.0 * root)
        - discriminant_first**2 / (8.0 * root**3)
    )
    low_second = -root_second
    high_second = root_second
    low = sqrt(low_sq)
    high = sqrt(high_sq)
    values = (
        low,
        high,
        low_first / (2.0 * low),
        high_first / (2.0 * high),
        low_second / (2.0 * low) - low_first**2 / (4.0 * low**3),
        high_second / (2.0 * high) - high_first**2 / (4.0 * high**3),
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("stationarity mode data are not finite")
    return values


def _cutoff(
    temperature: float,
    chemical_potential: float,
    effective_mass_sq_value: float,
    reference_x: float,
    cutoff_factor: float,
) -> float:
    factor = _positive(cutoff_factor, "cutoff_factor")
    return max(
        factor * temperature,
        factor * abs(chemical_potential),
        factor * sqrt(max(effective_mass_sq_value, 0.0)),
        factor * sqrt(reference_x),
        1.0,
    )


def renormalized_gaussian_stationarity_derivative(
    x: float,
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    reference_x: float,
    finite_coefficient: float = 0.0,
    *,
    reference_scale_sq: float | None = None,
    quadrature_order: int = 192,
    cutoff_factor: float = 60.0,
) -> float:
    """Return ``partial_x Omega`` for a declared renormalized Gaussian scheme."""

    x = _finite(x, "x")
    temperature = _positive(temperature, "temperature")
    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    if x <= 0.0 or reference_x <= 0.0:
        raise ValueError("x and reference_x must be positive")
    mass_sq = float(effective_mass_sq(phi, config))
    z = _positive(config.matter.matter_kinetic, "matter_kinetic")
    lam = _positive(config.matter.matter_quartic, "matter_quartic")
    q = z * mu * mu - mass_sq
    if q <= 0.0 or x < q / lam:
        raise ValueError("stationarity derivative requires the stable condensed domain")
    scale_sq = reference_x if reference_scale_sq is None else _positive(
        reference_scale_sq, "reference_scale_sq"
    )
    cutoff = _cutoff(temperature, mu, mass_sq, reference_x, cutoff_factor)
    momenta, weights = _quadrature(quadrature_order, cutoff)
    measure = momenta * momenta / (2.0 * pi**2)
    values = np.asarray(
        [
            _mode_data(float(k), x, mu, q, lam, z)
            for k in momenta
        ],
        dtype=float,
    )
    references = np.asarray(
        [
            _mode_data(float(k), reference_x, mu, q, lam, z)
            for k in momenta
        ],
        dtype=float,
    )
    thermal = float(
        np.sum(
            weights
            * measure
            * np.asarray(
                [
                    _bose(row[0], temperature) * row[2]
                    + _bose(row[1], temperature) * row[3]
                    for row in values
                ],
                dtype=float,
            )
        )
    )
    vacuum = 0.5 * float(
        np.sum(
            weights
            * measure
            * (
                values[:, 2]
                + values[:, 3]
                - references[:, 2]
                - (x - reference_x) * (references[:, 4] + references[:, 5])
                - references[:, 3]
            )
        )
    )
    tree = 0.5 * (-q + lam * x)
    counterterm = 3.0 * float(finite_coefficient) * (x - reference_x) ** 2 / scale_sq
    result = tree + thermal + vacuum + counterterm
    if not isfinite(result):
        raise FloatingPointError("renormalized Gaussian stationarity derivative is not finite")
    return float(result)


def _mode_minima(
    x: float,
    chemical_potential: float,
    condensate_control_value: float,
    quartic_coupling: float,
    kinetic_coefficient: float,
    *,
    quadrature_order: int,
    cutoff: float,
) -> tuple[float, float]:
    momenta, _ = _quadrature(quadrature_order, cutoff)
    records = [
        off_shell_mode_omega_sq(
            float(k),
            sqrt(x),
            chemical_potential,
            0.2,
            O2FiniteDensityEOSConfig(),
        )
        for k in momenta
    ]
    del condensate_control_value, quartic_coupling, kinetic_coefficient
    return (
        min(low for low, _ in records),
        min(high for _, high in records),
    )


def uet_o2_stationarity_scheme_dependence(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 60.0,
    scheme_b_coefficient: float = -0.05,
    max_iterations: int = 96,
) -> O2StationaritySchemeDependence:
    """Build two anchored scheme witnesses and solve the scheme-B stationary root."""

    temperature = _positive(temperature, "temperature")
    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    mass_sq = float(effective_mass_sq(phi, config))
    z = _positive(config.matter.matter_kinetic, "matter_kinetic")
    lam = _positive(config.matter.matter_quartic, "matter_quartic")
    q = z * mu * mu - mass_sq
    if q <= 0.0:
        raise ValueError("scheme-dependence witness requires q > 0")
    x_boundary = q / lam
    reference_x = 2.0 * x_boundary
    scale_sq = reference_x
    cutoff = _cutoff(temperature, mu, mass_sq, reference_x, cutoff_factor)
    scheme_a = 0.0
    scheme_b = _finite(scheme_b_coefficient, "scheme_b_coefficient")
    derivative = lambda x, coefficient: renormalized_gaussian_stationarity_derivative(
        x,
        temperature,
        mu,
        phi,
        config,
        reference_x,
        coefficient,
        reference_scale_sq=scale_sq,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
    )

    grid_factors = (1.0, 1.01, 1.05, 1.1, 1.25, 1.5, 1.75, 2.0)
    scheme_a_values = [derivative(x_boundary * factor, scheme_a) for factor in grid_factors]
    scheme_b_values = [derivative(x_boundary * factor, scheme_b) for factor in grid_factors]
    scheme_a_boundary = scheme_a_values[0]
    scheme_a_reference = scheme_a_values[-1]
    scheme_b_boundary = scheme_b_values[0]
    scheme_b_reference = scheme_b_values[-1]
    if scheme_b_boundary >= 0.0 or scheme_b_reference <= 0.0:
        raise RuntimeError("declared scheme-B witness does not bracket a stationary root")

    lower = x_boundary
    upper = reference_x
    iterations = 0
    for iterations in range(1, max_iterations + 1):
        midpoint = 0.5 * (lower + upper)
        midpoint_value = derivative(midpoint, scheme_b)
        if abs(midpoint_value) <= 1.0e-11:
            break
        if midpoint_value < 0.0:
            lower = midpoint
        else:
            upper = midpoint
    else:
        raise RuntimeError("scheme-B stationarity root did not converge")
    stationary_x = float(midpoint)
    stationary_residual = float(derivative(stationary_x, scheme_b))
    momenta, _ = _quadrature(quadrature_order, cutoff)
    mode_records = [
        _mode_data(float(k), stationary_x, mu, q, lam, z)
        for k in momenta
    ]
    low_min = min(row[0] ** 2 for row in mode_records)
    high_min = min(row[1] ** 2 for row in mode_records)
    anchors_a = finite_local_counterterm(reference_x, reference_x, scale_sq, scheme_a)
    anchors_b = finite_local_counterterm(reference_x, reference_x, scale_sq, scheme_b)
    if any(abs(value) > 1.0e-14 for value in (*anchors_a, *anchors_b)):
        raise FloatingPointError("scheme witnesses do not share reference anchors")
    values = (
        mass_sq,
        q,
        x_boundary,
        reference_x,
        scheme_a_boundary,
        scheme_a_reference,
        scheme_b_boundary,
        scheme_b_reference,
        stationary_x,
        stationary_residual,
        low_min,
        high_min,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("scheme-dependence witness contains a non-finite value")
    if low_min <= 0.0 or high_min <= 0.0:
        raise FloatingPointError("scheme-B stationary witness has unstable modes")
    return O2StationaritySchemeDependence(
        temperature=temperature,
        chemical_potential=mu,
        space_response=phi,
        effective_mass_sq=mass_sq,
        condensate_control=q,
        quartic_coupling=lam,
        x_boundary=x_boundary,
        reference_x=reference_x,
        reference_scale_sq=scale_sq,
        scheme_a_coefficient=scheme_a,
        scheme_b_coefficient=scheme_b,
        scheme_a_boundary_derivative=float(scheme_a_boundary),
        scheme_a_reference_derivative=float(scheme_a_reference),
        scheme_b_boundary_derivative=float(scheme_b_boundary),
        scheme_b_reference_derivative=float(scheme_b_reference),
        scheme_b_stationary_x=stationary_x,
        scheme_b_stationary_residual=stationary_residual,
        scheme_b_min_low_omega_sq=float(low_min),
        scheme_b_min_high_omega_sq=float(high_min),
        scheme_a_grid_min_derivative=float(min(scheme_a_values)),
        scheme_a_grid_max_derivative=float(max(scheme_a_values)),
        scheme_b_grid_min_derivative=float(min(scheme_b_values)),
        scheme_b_grid_max_derivative=float(max(scheme_b_values)),
        quadrature_order=int(quadrature_order),
        momentum_cutoff=float(cutoff),
    )


def uet_o2_stationarity_scheme_dependence_contract() -> dict[str, Any]:
    """Return the shared-anchor scheme-identifiability contract."""

    return {
        "status": "SCOPED_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE",
        "equations": {
            "x_definition": "x=A^2",
            "stable_domain": "x>=q/lambda, q=Z*mu^2-m_eff(Phi)^2>0",
            "taylor_subtracted_vacuum": "V_vac^R(x)=integral[S(x)-S(x_*)-(x-x_*)S'(x_*)-1/2*(x-x_*)^2*S''(x_*)] d^3k/(2*pi)^3",
            "finite_local_counterterm": "Delta V_a(x)=a*(x-x_*)^3/Lambda_*^2",
            "shared_reference_conditions": "Delta V_a(x_*)=partial_x Delta V_a(x_*)=partial_x^2 Delta V_a(x_*)=0",
            "stationarity": "partial_x[Omega_tree+Omega_G+V_vac^R+Delta V_a]=0",
            "witness": "scheme_A(a=0) and scheme_B(a=-0.05) share anchors but have different stationary-point behavior",
        },
        "units": {
            "unit_lane": "natural",
            "x_and_reference_x": "natural amplitude squared",
            "Lambda_star_sq": "natural amplitude squared",
            "Omega": "natural thermodynamic density",
            "Phi": "fixed action response input; no SI map",
            "alpha_Phi_K": "not emitted; SI map remains open",
        },
        "derivation_class": "internal two-scheme finite-counterterm identifiability witness with analytic mode derivatives and numerical convergence",
        "scope": {
            "scheme_A": "declared Taylor-subtracted Gaussian completion with a=0",
            "scheme_B": "same reference anchors plus declared finite local coefficient a=-0.05",
            "vacuum_counterterm": "declared finite subtraction only; not source or microscopic matching",
            "condensed_branch": "stationarity witness only; not a complete interacting branch",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms": "NOT_MATCHED_MICROSCOPICALLY",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature",
            "R_gen": "derived history trace only; not an independent state",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "data_role": "INTERNAL_STRUCTURAL_NO_GO_NO_SOURCE_ROWS_OR_HOLDOUT",
        "claim_boundary": "This closes only the structural non-identifiability of a finite-temperature condensed stationarity outcome under two admissible finite local completions sharing the current reference anchors. It does not select a physical renormalization scheme, establish a physical phase transition, close two-fluid transport, provide SK/KMS/Kubo coefficients, map Phi to SI temperature, calibrate alpha_Phi_K, validate TTG, or close Full Topic 13.",
    }


__all__ = [
    "O2StationaritySchemeDependence",
    "renormalized_gaussian_stationarity_derivative",
    "uet_o2_stationarity_scheme_dependence",
    "uet_o2_stationarity_scheme_dependence_contract",
]
