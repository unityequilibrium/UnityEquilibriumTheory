"""Hydrodynamic state-coordinate map from Noether charge to phase field.

The conservative O(2) matter pilot provides a Noether current ``N^mu``.  Once
a unit timelike frame ``u^mu`` and a coarse-graining prescription are declared,
the hydrodynamic charge density is ``n = -u_mu N^mu``.  This module maps that
already-coarse-grained density and its spatial current to dimensionless phase-
field coordinates,

``C = (n - n_ref) / n_scale`` and ``J = j / (n_scale L / T)``.

At fixed positive scales this final affine coordinate change is exactly
invertible and preserves continuity.  The preceding map from microscopic O(2)
fields to a current, and any non-trivial spatial coarse graining, are many-to-
one.  The module therefore does not claim to reconstruct the microscopic
matter fields from ``C``.

The symmetric Cahn-Hilliard double well is also mapped as a constitutive free-
energy coordinate.  Its equation of state and transport coefficients are not
derived from the O(2) action.  The external comparator's auxiliary phase is not
UET ``Phi``.  No history trace is accepted and no trace can feed back here.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import numpy as np

NOETHER_PHASE_FIELD_MAP_STATUS: Final[str] = (
    "PARTIAL_HYDRODYNAMIC_STATE_COORDINATE_MAP"
)
NOETHER_PHASE_FIELD_MAP_CONTROLLER: Final[str] = (
    "noether_charge_equation_of_state_and_covariant_transport_matching_missing"
)


def _finite_scalar(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive_scalar(value: float, name: str) -> float:
    result = _finite_scalar(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _field(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.size == 0:
        raise ValueError(f"{name} must be non-empty")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


def _matching_fields(**values: Any) -> dict[str, np.ndarray]:
    arrays = {name: _field(value, name) for name, value in values.items()}
    shapes = {array.shape for array in arrays.values()}
    if len(shapes) != 1:
        raise ValueError("mapped fields must share one shape")
    return arrays


@dataclass(frozen=True)
class NoetherPhaseFieldMapConfig:
    """Fixed scales for the local-frame hydrodynamic coordinate map."""

    density_reference: float = 0.0
    density_scale: float = 1.0
    length_scale: float = 1.0
    time_scale: float = 1.0
    chemical_potential_scale: float = 1.0
    charge_convention: str = "signed_global_O2_noether_charge"
    coarse_graining: str = "declared_local_cell_average"
    unit_lane: str = "natural_to_normalized"

    def __post_init__(self) -> None:
        _finite_scalar(self.density_reference, "density_reference")
        for name in (
            "density_scale",
            "length_scale",
            "time_scale",
            "chemical_potential_scale",
        ):
            _positive_scalar(getattr(self, name), name)
        if self.charge_convention != "signed_global_O2_noether_charge":
            raise NotImplementedError(
                "v1 maps only the signed global-O2 Noether charge; mass and "
                "particle-number interpretations require separate evidence"
            )
        if self.coarse_graining != "declared_local_cell_average":
            raise NotImplementedError(
                "v1 supports only an explicitly declared local cell average"
            )
        if self.unit_lane != "natural_to_normalized":
            raise NotImplementedError(
                "v1 supports only unit_lane='natural_to_normalized'"
            )

    @property
    def current_scale(self) -> float:
        """Return ``n_scale L/T`` for the spatial current component."""

        return float(self.density_scale * self.length_scale / self.time_scale)

    @property
    def free_energy_density_scale(self) -> float:
        """Return the conjugate scale ``n_scale * mu_scale``."""

        return float(self.density_scale * self.chemical_potential_scale)

    @property
    def mobility_scale(self) -> float:
        """Return ``n_scale L^2/(T mu_scale)`` for a unit normalized mobility."""

        return float(
            self.density_scale
            * self.length_scale**2
            / (self.time_scale * self.chemical_potential_scale)
        )


@dataclass(frozen=True)
class NoetherPhaseFieldCoordinates:
    """Round-trip result for the affine hydrodynamic state map."""

    C: np.ndarray
    normalized_current: np.ndarray
    reconstructed_density: np.ndarray
    reconstructed_current: np.ndarray
    density_roundtrip_error: float
    current_roundtrip_error: float


@dataclass(frozen=True)
class ContinuityMap:
    """Natural and normalized continuity residuals under fixed scales."""

    natural_density_rate: np.ndarray
    natural_current_divergence: np.ndarray
    normalized_density_rate: np.ndarray
    normalized_current_divergence: np.ndarray
    natural_residual: np.ndarray
    normalized_residual: np.ndarray
    expected_normalized_residual: np.ndarray
    max_abs_scaling_error: float


@dataclass(frozen=True)
class ExternalComparatorStateMap:
    """Coordinate map for external ``C`` and physical flux ``J=q/tau``."""

    C: np.ndarray
    flux_impulse: np.ndarray
    normalized_current: np.ndarray
    coarse_charge_density: np.ndarray
    spatial_noether_current: np.ndarray
    density_roundtrip_error: float
    current_roundtrip_error: float


@dataclass(frozen=True)
class DoubleWellThermodynamicMap:
    """Constitutive symmetric-double-well quantities in both coordinates."""

    C: np.ndarray
    coarse_charge_density: np.ndarray
    normalized_free_energy_density: np.ndarray
    normalized_chemical_potential: np.ndarray
    normalized_curvature: np.ndarray
    natural_free_energy_density: np.ndarray
    natural_chemical_potential: np.ndarray
    natural_inverse_susceptibility: np.ndarray


@dataclass(frozen=True)
class ConstitutiveScaleMap:
    """Natural scales implied by a normalized relaxation/gradient model."""

    normalized_relaxation: float
    normalized_gradient_coefficient: float
    natural_relaxation_time: float
    natural_current_scale: float
    natural_mobility: float
    natural_density_gradient_coefficient: float


def normalize_noether_hydrodynamic_state(
    coarse_charge_density: Any,
    spatial_noether_current: Any,
    config: NoetherPhaseFieldMapConfig,
) -> NoetherPhaseFieldCoordinates:
    """Map coarse hydrodynamic ``(n,j)`` to normalized ``(C,J)`` and back."""

    arrays = _matching_fields(
        coarse_charge_density=coarse_charge_density,
        spatial_noether_current=spatial_noether_current,
    )
    density = arrays["coarse_charge_density"]
    current = arrays["spatial_noether_current"]
    C = (density - config.density_reference) / config.density_scale
    normalized_current = current / config.current_scale
    reconstructed_density = (
        config.density_reference + config.density_scale * C
    )
    reconstructed_current = config.current_scale * normalized_current
    return NoetherPhaseFieldCoordinates(
        C=np.asarray(C, dtype=float),
        normalized_current=np.asarray(normalized_current, dtype=float),
        reconstructed_density=np.asarray(reconstructed_density, dtype=float),
        reconstructed_current=np.asarray(reconstructed_current, dtype=float),
        density_roundtrip_error=float(
            np.max(np.abs(reconstructed_density - density))
        ),
        current_roundtrip_error=float(
            np.max(np.abs(reconstructed_current - current))
        ),
    )


def denormalize_phase_field_coordinates(
    C: Any,
    normalized_current: Any,
    config: NoetherPhaseFieldMapConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Invert the final affine coordinate layer to coarse ``(n,j)``."""

    arrays = _matching_fields(C=C, normalized_current=normalized_current)
    density = (
        config.density_reference + config.density_scale * arrays["C"]
    )
    current = config.current_scale * arrays["normalized_current"]
    return np.asarray(density, dtype=float), np.asarray(current, dtype=float)


def map_continuity_terms(
    natural_density_rate: Any,
    natural_current_divergence: Any,
    config: NoetherPhaseFieldMapConfig,
) -> ContinuityMap:
    """Map ``d_t n + div j`` into normalized coordinates exactly.

    The reference and all scales are constant in v1.  With ``t=T t_hat`` and
    ``x=L x_hat``, both normalized terms equal ``T/n_scale`` times their
    natural counterparts.
    """

    arrays = _matching_fields(
        natural_density_rate=natural_density_rate,
        natural_current_divergence=natural_current_divergence,
    )
    scale = config.time_scale / config.density_scale
    density_rate = arrays["natural_density_rate"]
    current_divergence = arrays["natural_current_divergence"]
    natural_residual = density_rate + current_divergence
    normalized_density_rate = scale * density_rate
    normalized_current_divergence = scale * current_divergence
    normalized_residual = normalized_density_rate + normalized_current_divergence
    expected = scale * natural_residual
    return ContinuityMap(
        natural_density_rate=np.asarray(density_rate, dtype=float),
        natural_current_divergence=np.asarray(current_divergence, dtype=float),
        normalized_density_rate=np.asarray(normalized_density_rate, dtype=float),
        normalized_current_divergence=np.asarray(
            normalized_current_divergence, dtype=float
        ),
        natural_residual=np.asarray(natural_residual, dtype=float),
        normalized_residual=np.asarray(normalized_residual, dtype=float),
        expected_normalized_residual=np.asarray(expected, dtype=float),
        max_abs_scaling_error=float(np.max(np.abs(normalized_residual - expected))),
    )


def local_cell_average_1d(values: Any, cells: int) -> np.ndarray:
    """Return a deterministic 1D block average used as a coarse-graining audit.

    This operation is intentionally not invertible.  It is a numerical witness
    of the information discarded before the affine ``n_bar <-> C`` layer.
    """

    field = _field(values, "values")
    if field.ndim != 1:
        raise ValueError("values must be one-dimensional")
    if isinstance(cells, bool) or int(cells) != cells or int(cells) <= 0:
        raise ValueError("cells must be a positive integer")
    cell_count = int(cells)
    if field.size % cell_count != 0:
        raise ValueError("field length must be divisible by cells")
    return np.asarray(
        field.reshape(cell_count, field.size // cell_count).mean(axis=1),
        dtype=float,
    )


def map_external_comparator_state(
    C: Any,
    flux_impulse: Any,
    tau_flux: float,
    config: NoetherPhaseFieldMapConfig,
) -> ExternalComparatorStateMap:
    """Map external ``C,q`` after declaring ``J=q/tau`` as the charge flux."""

    arrays = _matching_fields(C=C, flux_impulse=flux_impulse)
    tau = _positive_scalar(tau_flux, "tau_flux")
    normalized_current = arrays["flux_impulse"] / tau
    density, current = denormalize_phase_field_coordinates(
        arrays["C"], normalized_current, config
    )
    roundtrip = normalize_noether_hydrodynamic_state(density, current, config)
    return ExternalComparatorStateMap(
        C=np.asarray(arrays["C"], dtype=float),
        flux_impulse=np.asarray(arrays["flux_impulse"], dtype=float),
        normalized_current=np.asarray(normalized_current, dtype=float),
        coarse_charge_density=density,
        spatial_noether_current=current,
        density_roundtrip_error=float(
            np.max(np.abs(roundtrip.C - arrays["C"]))
        ),
        current_roundtrip_error=float(
            np.max(np.abs(roundtrip.normalized_current - normalized_current))
        ),
    )


def symmetric_double_well_thermodynamic_map(
    C: Any,
    config: NoetherPhaseFieldMapConfig,
) -> DoubleWellThermodynamicMap:
    """Map ``g=(C^2-1)^2/4`` as a constitutive density free energy.

    The natural free-energy density is chosen as
    ``f = n_scale*mu_scale*g(C)``.  Therefore the conjugate chemical potential
    is exactly ``d f/d n = mu_scale*(C^3-C)``.
    """

    phase = _field(C, "C")
    density = config.density_reference + config.density_scale * phase
    free_energy = 0.25 * np.square(np.square(phase) - 1.0)
    chemical = np.power(phase, 3) - phase
    curvature = 3.0 * np.square(phase) - 1.0
    return DoubleWellThermodynamicMap(
        C=np.asarray(phase, dtype=float),
        coarse_charge_density=np.asarray(density, dtype=float),
        normalized_free_energy_density=np.asarray(free_energy, dtype=float),
        normalized_chemical_potential=np.asarray(chemical, dtype=float),
        normalized_curvature=np.asarray(curvature, dtype=float),
        natural_free_energy_density=np.asarray(
            config.free_energy_density_scale * free_energy, dtype=float
        ),
        natural_chemical_potential=np.asarray(
            config.chemical_potential_scale * chemical, dtype=float
        ),
        natural_inverse_susceptibility=np.asarray(
            config.chemical_potential_scale
            / config.density_scale
            * curvature,
            dtype=float,
        ),
    )


def symmetric_double_well_equilibrium_contract(
    config: NoetherPhaseFieldMapConfig,
) -> dict[str, float]:
    """Return the two coexistence coordinates and local susceptibility."""

    inverse_susceptibility = (
        2.0 * config.chemical_potential_scale / config.density_scale
    )
    return {
        "C_minus": -1.0,
        "C_plus": 1.0,
        "density_minus": config.density_reference - config.density_scale,
        "density_plus": config.density_reference + config.density_scale,
        "natural_chemical_potential_at_both_minima": 0.0,
        "natural_inverse_susceptibility_at_both_minima": (
            inverse_susceptibility
        ),
        "natural_susceptibility_at_both_minima": (
            1.0 / inverse_susceptibility
        ),
    }


def map_normalized_constitutive_scales(
    normalized_relaxation: float,
    normalized_gradient_coefficient: float,
    config: NoetherPhaseFieldMapConfig,
) -> ConstitutiveScaleMap:
    """Map declared normalized scales without claiming microscopic derivation."""

    relaxation = _positive_scalar(
        normalized_relaxation, "normalized_relaxation"
    )
    gradient = _finite_scalar(
        normalized_gradient_coefficient,
        "normalized_gradient_coefficient",
    )
    if gradient < 0.0:
        raise ValueError("normalized_gradient_coefficient must be non-negative")
    return ConstitutiveScaleMap(
        normalized_relaxation=relaxation,
        normalized_gradient_coefficient=gradient,
        natural_relaxation_time=config.time_scale * relaxation,
        natural_current_scale=config.current_scale,
        natural_mobility=config.mobility_scale,
        natural_density_gradient_coefficient=(
            config.chemical_potential_scale
            * gradient
            * config.length_scale**2
            / config.density_scale
        ),
    )


def noether_phase_field_map_contract() -> dict[str, Any]:
    """Return the achieved coordinate map and its non-invertible boundaries."""

    return {
        "status": NOETHER_PHASE_FIELD_MAP_STATUS,
        "conserved_variable": (
            "signed_global_O2_Noether_charge_density_n_equals_minus_u_dot_N"
        ),
        "map_factorization": [
            "microscopic_O2_state_to_Noether_current_many_to_one",
            "frame_projection_to_charge_density_many_to_one",
            "declared_cell_average_many_to_one",
            "coarse_density_current_to_C_J_affine_bijection",
        ],
        "invertible_layer": (
            "coarse_density_current_bijective_with_C_J_at_fixed_reference_and_scales"
        ),
        "microscopic_inverse": "IMPOSSIBLE_WITHOUT_ADDITIONAL_STATE",
        "external_C_role": (
            "compatible_only_as_declared_normalized_signed_charge_coordinate"
        ),
        "double_well_local_map": "a_matter_minus_one_b_matter_plus_one",
        "equation_of_state_origin": "CONSTITUTIVE_NOT_DERIVED_FROM_O2_ACTION",
        "external_auxiliary_phase_to_UET_Phi": "FORBIDDEN",
        "trace_input": False,
        "trace_backreaction": False,
        "global_universe_closure": "UNRESOLVED",
        "gr_null_branch": "epsilon_nc_equals_zero_remains_exact_GR_response_null",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "next_controller": NOETHER_PHASE_FIELD_MAP_CONTROLLER,
    }
