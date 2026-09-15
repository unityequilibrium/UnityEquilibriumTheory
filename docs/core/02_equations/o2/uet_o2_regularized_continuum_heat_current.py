"""Named regularized continuum heat-current lane for Topic 13.

The existing heat-current Kubo lane uses a finite momentum cutoff and fails
the repository continuum controller.  This module tests one explicitly named
alternative: compactify the positive radial momentum axis to ``u in (0, 1)``
and apply the same normal-branch action-derived collision width to the
resulting quadrature.  The source is projected against charge, energy, and
three-momentum moments before the response is evaluated.

This is a lane-level natural-unit result.  It is not a physical SI Kubo
coefficient, a loop-renormalized transport theory, an alpha calibration, or
an external TTG validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cosh, exp, expm1, isfinite, pi, sinh, sqrt

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    finite_temperature_o2_state,
)
from docs.core.uet_o2_kinetic_collision_kubo import (
    _bose,
    _collision_width,
    _normal_state_inputs,
)


REGULARIZED_CONTINUUM_HEAT_CURRENT_STATUS = (
    "PASS_ACTION_DERIVED_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE"
)
CONTINUUM_ACCEPTANCE_THRESHOLD = 1.0e-2
DEFAULT_RADIAL_ORDERS = (24, 32, 40)
DEFAULT_ANGULAR_ORDER = 24
DEFAULT_ANGULAR_REFINED_ORDER = 32
DEFAULT_RADIAL_SCALE_FACTOR = 1.0
DEFAULT_REFINED_SCALE_FACTOR = 0.5
_DIRECTIONS = (
    (1.0, 0.0, 0.0),
    (-1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, -1.0),
)


@dataclass(frozen=True)
class RegularizedContinuumHeatCurrentState:
    """Convergence and conservation record for the named continuum branch."""

    temperature: float
    chemical_potential: float
    space_response: float
    branch: str
    effective_mass: float
    quartic_coupling: float
    radial_orders: tuple[int, ...]
    angular_order: int
    angular_refined_order: int
    radial_scale: float
    refined_radial_scale: float
    state_count: int
    radial_k_max_by_order: tuple[float, ...]
    radial_kappa_natural: tuple[float, ...]
    radial_relative_changes: tuple[float, ...]
    radial_max_relative_change: float
    angular_refined_kappa_natural: float
    angular_refined_relative_change: float
    scale_refined_kappa_natural: float
    scale_refined_relative_change: float
    kappa_natural: float
    collision_operator_min_eigenvalue: float
    collision_operator_symmetry_residual: float
    conservation_residual: float
    source_constraint_residual: float
    entropy_production: float
    retarded_frequency_over_rate: tuple[float, ...]
    retarded_response_real: tuple[float, ...]
    retarded_response_imag: tuple[float, ...]
    kms_frequency_over_temperature: tuple[float, ...]
    kms_ratio_residual: float
    fdt_residual: float
    continuum_convergence_passes: bool
    compactified_radial_domain_used: bool
    finite_cutoff_used: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_REGULARIZED_CONTINUUM_HEAT_CURRENT_NOT_PHYSICAL_KUBO"
    )


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


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _compactified_radial_quadrature(
    order: int,
    scale: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Map Gauss-Legendre nodes from ``u in (0, 1)`` to ``k in (0, infinity)``."""

    order = _integer(order, "radial_order", 16)
    scale = _positive(scale, "radial_scale")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    u = 0.5 * (nodes + 1.0)
    du = 0.5 * weights
    momentum = scale * u / (1.0 - u)
    jacobian = scale / (1.0 - u) ** 2
    return momentum, du * jacobian


def _angle_quadrature(order: int) -> tuple[np.ndarray, np.ndarray]:
    order = _integer(order, "angular_order", 16)
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return nodes, weights


def _relative_changes(values: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(
        abs(current - previous) / max(abs(previous), 1.0e-300)
        for previous, current in zip(values, values[1:])
    )


def _retarded_response(
    source: np.ndarray,
    frequency: float,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
) -> complex:
    projected = eigenvectors.T @ source
    response = 0.0j
    for coefficient, eigenvalue in zip(projected, eigenvalues):
        if eigenvalue <= 1.0e-12 and frequency == 0.0:
            continue
        response += float(coefficient * coefficient) / (
            float(eigenvalue) - 1.0j * float(frequency)
        )
    return complex(response)


def _response_at_resolution(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    *,
    radial_order: int,
    angular_order: int,
    radial_scale: float,
    retarded_frequency_over_rate: tuple[float, ...],
    kms_frequency_over_temperature: tuple[float, ...],
) -> dict[str, object]:
    """Build one compactified conservative heat-current response."""

    t, mu, mass, mu_eff, quartic = _normal_state_inputs(
        temperature, chemical_potential, space_response, config
    )
    radial_nodes, radial_weights = _compactified_radial_quadrature(
        radial_order, radial_scale
    )
    angle_nodes, angle_weights = _angle_quadrature(angular_order)
    state_signs: list[float] = []
    momenta: list[tuple[float, float, float]] = []
    energies: list[float] = []
    weights: list[float] = []
    widths: list[float] = []
    direction_weight = 1.0 / float(len(_DIRECTIONS))
    radial_measure = 1.0 / (2.0 * pi**2)
    for sign in (-1.0, 1.0):
        for momentum, momentum_weight in zip(radial_nodes, radial_weights):
            p = float(momentum)
            energy = sqrt(p * p + mass * mass)
            occupation = _bose(energy - sign * mu_eff, t)
            state_weight = (
                float(momentum_weight)
                * p
                * p
                * radial_measure
                * occupation
                * (1.0 + occupation)
                / t
                * direction_weight
            )
            # Omitted only when the compactified Bose tail underflows to zero in float64; no floor or clipping is applied.
            if state_weight <= 0.0:
                continue
            width = _collision_width(
                p,
                sign,
                t,
                mass,
                mu_eff,
                quartic,
                radial_nodes,
                radial_weights,
                angle_nodes,
                angle_weights,
                include_final_state_bose_enhancement=False,
            )
            for direction in _DIRECTIONS:
                state_signs.append(sign)
                momenta.append(tuple(p * float(value) for value in direction))
                energies.append(energy)
                weights.append(float(state_weight))
                widths.append(_positive(width, "continuum collision width"))

    weight_array = np.asarray(weights, dtype=float)
    momentum_array = np.asarray(momenta, dtype=float)
    energy_array = np.asarray(energies, dtype=float)
    sign_array = np.asarray(state_signs, dtype=float)
    sqrt_weight = np.sqrt(weight_array)
    invariant_columns = np.column_stack(
        (
            sign_array * sqrt_weight,
            energy_array * sqrt_weight,
            momentum_array[:, 0] * sqrt_weight,
            momentum_array[:, 1] * sqrt_weight,
            momentum_array[:, 2] * sqrt_weight,
        )
    )
    if int(np.linalg.matrix_rank(invariant_columns, tol=1.0e-12)) != 5:
        raise ValueError("continuum heat-current invariants must have rank five")
    orthonormal, _ = np.linalg.qr(invariant_columns, mode="reduced")
    projector = np.eye(len(weights), dtype=float) - orthonormal @ orthonormal.T
    operator = projector @ np.diag(np.asarray(widths, dtype=float)) @ projector
    eos = finite_temperature_o2_state(t, mu, space_response, config)
    if abs(eos.charge_density) <= 1.0e-14:
        raise ValueError("normal heat-current branch requires nonzero charge density")
    enthalpy_per_charge = (eos.energy_density + eos.pressure) / eos.charge_density
    source = (energy_array - enthalpy_per_charge * sign_array) * (
        momentum_array[:, 0] / energy_array
    ) * sqrt_weight
    projected_source = projector @ source
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    positive_eigenvalues = eigenvalues[eigenvalues > 1.0e-12]
    positive_rate = _positive(float(np.mean(positive_eigenvalues)), "positive mode rate")
    frequencies = tuple(positive_rate * value for value in retarded_frequency_over_rate)
    responses = tuple(
        _retarded_response(projected_source, frequency, eigenvalues, eigenvectors)
        for frequency in frequencies
    )
    kms_frequencies = tuple(t * value for value in kms_frequency_over_temperature)
    kms_responses = tuple(
        _retarded_response(projected_source, frequency, eigenvalues, eigenvectors)
        for frequency in kms_frequencies
    )
    spectral = tuple(2.0 * response.imag for response in kms_responses)
    occupations = tuple(1.0 / expm1(value) for value in kms_frequency_over_temperature)
    greater = tuple(rho * (1.0 + occupation) for rho, occupation in zip(spectral, occupations))
    lesser = tuple(rho * occupation for rho, occupation in zip(spectral, occupations))
    kms_ratio = tuple(g / l for g, l in zip(greater, lesser))
    kms_target = tuple(exp(value) for value in kms_frequency_over_temperature)
    kms_residual = max(
        abs(actual - target) / max(abs(target), 1.0)
        for actual, target in zip(kms_ratio, kms_target)
    )
    fdt_residual = max(
        abs((g + l) - rho * (1.0 + 2.0 / expm1(ratio)))
        / max(abs(rho), 1.0)
        for g, l, rho, ratio in zip(
            greater, lesser, spectral, kms_frequency_over_temperature
        )
    )
    symmetric_operator = 0.5 * (operator + operator.T)
    kappa = _positive(float(responses[0].real), "regularized kappa")
    entropy = _positive(
        float(projected_source @ symmetric_operator @ projected_source / t),
        "regularized entropy production",
    )
    values = (
        *eigenvalues,
        *[response.real for response in responses],
        *[response.imag for response in responses],
        *spectral,
        kms_residual,
        fdt_residual,
        kappa,
        entropy,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("regularized continuum heat response is not finite")
    return {
        "kappa_natural": kappa,
        "state_count": len(weights),
        "k_max": float(np.max(radial_nodes)),
        "operator_min_eigenvalue": float(np.min(eigenvalues)),
        "operator_symmetry_residual": float(np.linalg.norm(operator - operator.T)),
        "conservation_residual": float(np.linalg.norm(operator @ invariant_columns)),
        "source_constraint_residual": float(
            np.linalg.norm(orthonormal.T @ projected_source)
        ),
        "entropy_production": entropy,
        "retarded_response_real": tuple(float(response.real) for response in responses),
        "retarded_response_imag": tuple(float(response.imag) for response in responses),
        "kms_ratio_residual": float(kms_residual),
        "fdt_residual": float(fdt_residual),
    }


def regularized_continuum_heat_current_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_orders: tuple[int, ...] = DEFAULT_RADIAL_ORDERS,
    angular_order: int = DEFAULT_ANGULAR_ORDER,
    angular_refined_order: int = DEFAULT_ANGULAR_REFINED_ORDER,
    radial_scale_factor: float = DEFAULT_RADIAL_SCALE_FACTOR,
    refined_scale_factor: float = DEFAULT_REFINED_SCALE_FACTOR,
    retarded_frequency_over_rate: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
    kms_frequency_over_temperature: tuple[float, ...] = (0.25, 0.5, 1.0),
) -> RegularizedContinuumHeatCurrentState:
    """Evaluate the regularized normal-branch heat-current response."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if len(radial_orders) < 2 or tuple(sorted(radial_orders)) != tuple(radial_orders):
        raise ValueError("radial_orders must be sorted and contain at least two orders")
    radial_orders = tuple(_integer(value, "radial_order", 16) for value in radial_orders)
    angular_order = _integer(angular_order, "angular_order", 16)
    angular_refined_order = _integer(
        angular_refined_order, "angular_refined_order", angular_order
    )
    radial_scale_factor = _positive(radial_scale_factor, "radial_scale_factor")
    refined_scale_factor = _positive(refined_scale_factor, "refined_scale_factor")
    frequencies = tuple(_finite(value, "retarded frequency ratio") for value in retarded_frequency_over_rate)
    if not frequencies or frequencies[0] != 0.0 or tuple(sorted(frequencies)) != frequencies:
        raise ValueError("retarded frequency ratios must start at zero and be sorted")
    kms_ratios = tuple(
        _positive(value, "kms frequency ratio") for value in kms_frequency_over_temperature
    )
    if tuple(sorted(kms_ratios)) != kms_ratios:
        raise ValueError("KMS frequency ratios must be sorted")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    eos = finite_temperature_o2_state(
        temperature, chemical_potential, space_response, config
    )
    if eos.branch != "normal":
        raise ValueError("regularized continuum heat-current lane requires normal branch")
    base_scale = max(temperature, eos.effective_mass, 1.0e-6) * radial_scale_factor
    records = tuple(
        _response_at_resolution(
            temperature,
            chemical_potential,
            space_response,
            config,
            radial_order=order,
            angular_order=angular_order,
            radial_scale=base_scale,
            retarded_frequency_over_rate=frequencies,
            kms_frequency_over_temperature=kms_ratios,
        )
        for order in radial_orders
    )
    radial_values = tuple(float(record["kappa_natural"]) for record in records)
    radial_changes = _relative_changes(radial_values)
    baseline = records[-1]
    angular_record = _response_at_resolution(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=radial_orders[-1],
        angular_order=angular_refined_order,
        radial_scale=base_scale,
        retarded_frequency_over_rate=frequencies,
        kms_frequency_over_temperature=kms_ratios,
    )
    scale_record = _response_at_resolution(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=radial_orders[-1],
        angular_order=angular_order,
        radial_scale=base_scale * refined_scale_factor,
        retarded_frequency_over_rate=frequencies,
        kms_frequency_over_temperature=kms_ratios,
    )
    angular_change = abs(float(angular_record["kappa_natural"]) - float(baseline["kappa_natural"])) / max(
        abs(float(baseline["kappa_natural"])), 1.0e-300
    )
    scale_change = abs(float(scale_record["kappa_natural"]) - float(baseline["kappa_natural"])) / max(
        abs(float(baseline["kappa_natural"])), 1.0e-300
    )
    radial_max_change = max(radial_changes, default=0.0)
    convergence_passes = (
        radial_max_change <= CONTINUUM_ACCEPTANCE_THRESHOLD
        and angular_change <= CONTINUUM_ACCEPTANCE_THRESHOLD
        and scale_change <= CONTINUUM_ACCEPTANCE_THRESHOLD
    )
    return RegularizedContinuumHeatCurrentState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        branch=eos.branch,
        effective_mass=eos.effective_mass,
        quartic_coupling=config.eos.matter.matter_quartic,
        radial_orders=radial_orders,
        angular_order=angular_order,
        angular_refined_order=angular_refined_order,
        radial_scale=base_scale,
        refined_radial_scale=base_scale * refined_scale_factor,
        state_count=int(baseline["state_count"]),
        radial_k_max_by_order=tuple(float(record["k_max"]) for record in records),
        radial_kappa_natural=radial_values,
        radial_relative_changes=radial_changes,
        radial_max_relative_change=float(radial_max_change),
        angular_refined_kappa_natural=float(angular_record["kappa_natural"]),
        angular_refined_relative_change=float(angular_change),
        scale_refined_kappa_natural=float(scale_record["kappa_natural"]),
        scale_refined_relative_change=float(scale_change),
        kappa_natural=float(baseline["kappa_natural"]),
        collision_operator_min_eigenvalue=float(baseline["operator_min_eigenvalue"]),
        collision_operator_symmetry_residual=float(baseline["operator_symmetry_residual"]),
        conservation_residual=float(baseline["conservation_residual"]),
        source_constraint_residual=float(baseline["source_constraint_residual"]),
        entropy_production=float(baseline["entropy_production"]),
        retarded_frequency_over_rate=frequencies,
        retarded_response_real=tuple(baseline["retarded_response_real"]),
        retarded_response_imag=tuple(baseline["retarded_response_imag"]),
        kms_frequency_over_temperature=kms_ratios,
        kms_ratio_residual=float(baseline["kms_ratio_residual"]),
        fdt_residual=float(baseline["fdt_residual"]),
        continuum_convergence_passes=convergence_passes,
        compactified_radial_domain_used=True,
    )


def regularized_continuum_heat_current_contract() -> dict[str, object]:
    """Return the equations, units, and explicit lane boundary."""

    return {
        "status": REGULARIZED_CONTINUUM_HEAT_CURRENT_STATUS,
        "equations": {
            "radial_map": "k=Lambda*u/(1-u), u in (0,1), dk=Lambda/(1-u)^2 du",
            "normal_dispersion": "E_s(k)=sqrt(k^2+m_eff^2)-s*sqrt(Z)*abs(mu)",
            "collision_width": "Gamma_s(k)=sum_r integral[d^3p/(2*pi)^3] f_r(E_p) v_rel sigma_22(s)",
            "heat_source": "b_q=(E-h*q)*(p_x/E)*sqrt(w), h=(epsilon+p)/n",
            "conserved_invariants": "I_A=(q,E,p_x,p_y,p_z)*sqrt(w); P=I-Q*Q^T",
            "collision_operator": "L_reg=P*diag(Gamma_s(k))*P; L_reg*I_A=0; L_reg>=0",
            "retarded_response": "G_R=(L_reg-i*omega*I)^(-1); kappa=Re[b_q^T G_R(0) b_q]",
            "kms_ratio": "G^>/G^<=exp(beta_th*omega)",
            "entropy": "sigma=b_q^T L_reg b_q/T>=0",
            "continuum_controller": "max(radial, angular, scale relative changes)<=1e-2",
        },
        "unit_contract": {
            "unit_lane": "natural continuum thermal integral",
            "temperature_chemical_potential_mass_rate": "energy",
            "kappa_natural": "formal natural-unit response; not SI conductivity",
            "heat_flux": "formal natural-unit moment current; not W m^-2",
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived normal-branch constant-amplitude 2-to-2 collision width "
            "with compactified infinite radial quadrature and invariant projection"
        ),
        "observable": "regularized natural-unit normal-branch heat-current response stability",
        "data_role": "ACTION_DERIVED_REGULARIZED_CONTINUUM_HEAT_CURRENT_NOT_PHYSICAL_KUBO",
        "closed_scope": [
            "the radial domain is represented by an explicit k in [0,infinity) compactification",
            "radial order, angular order, and compactification-scale refinements are checked",
            "charge, energy, and three-momentum conservation are projected explicitly",
            "the collision operator is symmetric positive semidefinite and entropy production is nonnegative",
            "the normal-branch heat-current response is a named converged natural-unit lane when the unchanged 1e-2 gate passes",
        ],
        "excluded_scope": [
            "loop-renormalized off-shell self-energy and microscopic SK/KMS action matching",
            "finite-temperature condensed two-fluid completion",
            "physical Kubo coefficient or SI Phi-to-thermal mapping",
            "alpha_Phi_K calibration and TTG validation",
        ],
        "claim_boundary": (
            "This closes only a named normal-branch regularized continuum lane if its "
            "convergence and conservation checks pass. It does not replace the failed "
            "finite-cutoff baseline, emit a physical Kubo coefficient, or close Full Topic 13."
        ),
    }


__all__ = [
    "CONTINUUM_ACCEPTANCE_THRESHOLD",
    "DEFAULT_ANGULAR_ORDER",
    "DEFAULT_ANGULAR_REFINED_ORDER",
    "DEFAULT_RADIAL_ORDERS",
    "REGULARIZED_CONTINUUM_HEAT_CURRENT_STATUS",
    "RegularizedContinuumHeatCurrentState",
    "regularized_continuum_heat_current_contract",
    "regularized_continuum_heat_current_state",
]
