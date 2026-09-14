"""Focused tests for the covariant-to-matter-space response reduction."""

from __future__ import annotations

import inspect

import numpy as np
import pytest

from docs.core.uet_covariant_reduction import (
    WeakFieldReductionConfig,
    compare_response_reduction,
    derive_response_coefficients,
    dimensional_scalar_source_minus_curvature_drive,
    matter_space_config_from_reduction,
    reduction_contract,
    required_dimensionless_scalar_source,
)
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_matter_space import (
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_rhs,
)
from docs.core.uet_spatial import laplacian_1d


def _configs() -> tuple[CovariantResponseConfig, WeakFieldReductionConfig]:
    return (
        CovariantResponseConfig(
            epsilon_nc=.3,
            response_kinetic=1.2,
            response_mass_sq=.8,
            response_quartic=.35,
        ),
        WeakFieldReductionConfig(
            length_scale=2.0,
            time_scale=.8,
            response_field_scale=.45,
            mobility_space=.7,
            tau_space=1.3,
            coupling_g=.22,
        ),
    )


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"length_scale": 0.0}, ValueError),
        ({"time_scale": 0.0}, ValueError),
        ({"response_field_scale": 0.0}, ValueError),
        ({"mobility_space": 0.0}, ValueError),
        ({"tau_space": 0.0}, ValueError),
        ({"coupling_g": -1.0}, ValueError),
        ({"unit_lane": "SI"}, NotImplementedError),
    ],
)
def test_reduction_config_rejects_unsupported_values(
    kwargs: dict[str, object], error: type[Exception]
) -> None:
    with pytest.raises(error):
        WeakFieldReductionConfig(**kwargs)


def test_coefficient_map_preserves_normalized_light_characteristic() -> None:
    covariant, reduction = _configs()
    coefficients = derive_response_coefficients(covariant, reduction)
    speed = np.sqrt(
        coefficients.mobility_space
        * coefficients.kappa_space
        / coefficients.tau_space
    )
    assert speed == pytest.approx(reduction.normalized_light_speed)
    assert coefficients.a_space > 0.0
    assert coefficients.b_space > 0.0


def test_response_acceleration_mapping_is_exact_to_roundoff() -> None:
    covariant, reduction = _configs()
    rng = np.random.default_rng(41)
    arrays = [rng.normal(scale=.1, size=64) for _ in range(5)]
    result = compare_response_reduction(*arrays, covariant, reduction)
    np.testing.assert_allclose(
        result["covariant_acceleration"],
        result["matter_space_acceleration"],
        rtol=0.0,
        atol=1e-14,
    )
    assert result["max_abs_difference"] <= 1e-14


def test_reduction_matches_actual_matter_space_rhs_response_component() -> None:
    covariant, reduction = _configs()
    x = np.linspace(0.0, 2.0 * np.pi, 64, endpoint=False)
    dx = x[1] - x[0]
    matter = .3 + .04 * np.cos(x)
    response = .08 * np.sin(2 * x)
    rate = .03 * np.cos(3 * x)
    drive = .01 * np.sin(x)
    template = MatterSpaceConfig(
        a_matter=-.5,
        b_matter=.8,
        kappa_matter=.2,
        mobility_matter=.3,
        boundary_condition="periodic",
    )
    mapped = matter_space_config_from_reduction(covariant, reduction, template)
    state = MatterSpaceState(matter, response, rate)
    _, _, dPi, _, _ = matter_space_rhs(
        state, dx, mapped, matter_source=np.zeros_like(matter), space_source=drive
    )
    laplacian = laplacian_1d(response, dx, "periodic")
    comparison = compare_response_reduction(
        response, rate, laplacian, matter, drive, covariant, reduction
    )
    np.testing.assert_allclose(dPi, comparison["covariant_acceleration"], atol=1e-14)


def test_matter_coefficients_are_inherited_not_claimed_as_derived() -> None:
    covariant, reduction = _configs()
    template = MatterSpaceConfig(
        a_matter=-.7,
        b_matter=.9,
        kappa_matter=.25,
        mobility_matter=.4,
    )
    mapped = matter_space_config_from_reduction(covariant, reduction, template)
    assert mapped.a_matter == template.a_matter
    assert mapped.b_matter == template.b_matter
    assert mapped.kappa_matter == template.kappa_matter
    assert mapped.mobility_matter == template.mobility_matter


def test_source_scaling_is_finite_and_shape_preserving() -> None:
    covariant, reduction = _configs()
    coefficients = derive_response_coefficients(covariant, reduction)
    rate = np.linspace(-.1, .1, 16)
    matter = np.linspace(.2, .3, 16)
    drive = np.zeros(16)
    source = required_dimensionless_scalar_source(
        rate, matter, drive, coefficients
    )
    dimensional = dimensional_scalar_source_minus_curvature_drive(
        source, covariant, reduction
    )
    assert dimensional.shape == source.shape
    assert np.all(np.isfinite(dimensional))


def test_reduction_adapter_is_not_active_on_exact_gr_branch() -> None:
    _, reduction = _configs()
    with pytest.raises(ValueError, match="epsilon_nc > 0"):
        derive_response_coefficients(
            CovariantResponseConfig(epsilon_nc=0.0), reduction
        )


def test_contract_exposes_partial_scope_and_no_trace_edge() -> None:
    contract = reduction_contract()
    assert contract["response_equation_mapping"] == "EXACT_ALGEBRAIC"
    assert contract["matter_equation_mapping"] == (
        "PARTIAL_IN_SEPARATE_CONSTITUTIVE_CURRENT_BRIDGE"
    )
    assert contract["reciprocal_coupling_derivation"] == (
        "IMPLEMENTED_ACTION_LEVEL_IN_SEPARATE_MATTER_MODULE"
    )
    assert contract["causal_source_realization"] == "BLOCKED"
    assert contract["derived_trace_backreaction"] is False
    assert "trace" not in inspect.signature(compare_response_reduction).parameters
