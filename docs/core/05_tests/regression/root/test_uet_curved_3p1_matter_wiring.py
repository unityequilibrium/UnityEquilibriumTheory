from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_curved_3p1_matter_wiring import (
    RelativisticFluidState,
    compute_nonlinear_prescribed_matter_gh_rhs,
    curved_3p1_matter_wiring_contract,
    project_stress_energy_3p1,
    relativistic_fluid_stress_energy,
    trace_reversed_stress_energy,
)


def minkowski(shape: tuple[int, ...] = ()) -> np.ndarray:
    return np.broadcast_to(np.diag([-1.0, 1.0, 1.0, 1.0]), shape + (4, 4)).copy()


def velocity(shape: tuple[int, ...], speed: float = 0.0) -> np.ndarray:
    gamma = 1.0 / np.sqrt(1.0 - speed**2)
    value = np.zeros(shape + (4,), dtype=float)
    value[..., 0] = gamma
    value[..., 1] = gamma * speed
    return value


def test_rest_perfect_fluid_projects_to_declared_eos() -> None:
    metric = minkowski()
    stress = relativistic_fluid_stress_energy(
        metric,
        RelativisticFluidState(2.5, 0.4, velocity(())),
    )
    projection = project_stress_energy_3p1(metric, stress, unit_lane="natural")

    assert stress[0, 0] == pytest.approx(2.5)
    assert np.allclose(stress[1:, 1:], 0.4 * np.eye(3))
    assert projection.energy_density == pytest.approx(2.5)
    assert np.allclose(projection.momentum_density, 0.0)
    assert np.allclose(projection.spatial_stress, 0.4 * np.eye(3))
    assert projection.trace_spatial_stress == pytest.approx(1.2)
    assert projection.reconstruction_residual <= 1.0e-14
    assert projection.for_constraints().energy_density == pytest.approx(2.5)
    assert np.allclose(projection.for_evolution().spatial_stress, 0.4 * np.eye(3))


def test_boosted_perfect_fluid_projection_has_expected_momentum() -> None:
    metric = minkowski()
    energy, pressure, speed = 2.0, 0.3, 0.2
    gamma = 1.0 / np.sqrt(1.0 - speed**2)
    stress = relativistic_fluid_stress_energy(
        metric,
        RelativisticFluidState(energy, pressure, velocity((), speed)),
    )
    projection = project_stress_energy_3p1(metric, stress, unit_lane="natural")

    assert projection.energy_density == pytest.approx(
        (energy + pressure) * gamma**2 - pressure
    )
    assert projection.momentum_density[0] == pytest.approx(
        (energy + pressure) * gamma**2 * speed
    )
    assert projection.spatial_stress[0, 0] == pytest.approx(
        (energy + pressure) * gamma**2 * speed**2 + pressure
    )
    assert projection.reconstruction_residual <= 1.0e-14


def test_eulerian_fluid_projection_handles_nonzero_shift() -> None:
    metric = minkowski()
    metric[0, 0] = -0.96
    metric[0, 1] = metric[1, 0] = 0.2
    normal = np.array([1.0, -0.2, 0.0, 0.0])
    energy, pressure = 1.7, 0.25
    stress = relativistic_fluid_stress_energy(
        metric,
        RelativisticFluidState(energy, pressure, normal),
    )
    projection = project_stress_energy_3p1(metric, stress, unit_lane="natural")

    assert projection.energy_density == pytest.approx(energy)
    assert np.allclose(projection.momentum_density, 0.0, atol=1.0e-14)
    assert np.allclose(projection.spatial_stress, pressure * np.eye(3))
    assert projection.reconstruction_residual <= 1.0e-14


def test_heat_flux_and_anisotropic_constraints_are_enforced() -> None:
    metric = minkowski()
    with pytest.raises(ValueError, match="heat_flux must be orthogonal"):
        relativistic_fluid_stress_energy(
            metric,
            RelativisticFluidState(1.0, 0.1, velocity(()), heat_flux=np.ones(4)),
        )
    bad_pi = np.diag([0.0, 1.0, 0.0, 0.0])
    with pytest.raises(ValueError, match="trace free"):
        relativistic_fluid_stress_energy(
            metric,
            RelativisticFluidState(1.0, 0.1, velocity(()), anisotropic_stress=bad_pi),
        )


def test_gh_source_is_exact_trace_reverse_and_vacuum_null() -> None:
    shape = (5, 5, 5)
    metric = minkowski(shape)
    zero_pi = np.zeros(shape + (4, 4))
    zero_phi = np.zeros(shape + (3, 4, 4))
    source = np.zeros(shape + (4,))
    source_derivative = np.zeros(shape + (4, 4))
    stress = relativistic_fluid_stress_energy(
        metric,
        RelativisticFluidState(0.02, 0.003, velocity(shape)),
    )
    coupling = 0.25
    result = compute_nonlinear_prescribed_matter_gh_rhs(
        metric,
        zero_pi,
        zero_phi,
        source,
        source_derivative,
        (0.2, 0.2, 0.2),
        stress,
        einstein_coupling=coupling,
        matter_unit_lane="natural_witness",
    )
    expected = -2.0 * coupling * trace_reversed_stress_energy(metric, stress)

    assert np.allclose(result.matter_source_term, expected)
    assert np.allclose(result.normal_derivative_rhs, expected)
    assert np.allclose(result.metric_rhs, 0.0)
    assert np.allclose(result.spatial_derivative_rhs, 0.0)
    assert result.diagnostics["matter_state_evolution"] is False

    vacuum = compute_nonlinear_prescribed_matter_gh_rhs(
        metric,
        zero_pi,
        zero_phi,
        source,
        source_derivative,
        (0.2, 0.2, 0.2),
        np.zeros_like(stress),
        einstein_coupling=coupling,
        matter_unit_lane="natural_witness",
    )
    assert np.allclose(vacuum.normal_derivative_rhs, vacuum.vacuum_rhs.normal_derivative_rhs)


def test_multiplicative_energy_scale_preserves_projection() -> None:
    metric = minkowski()
    natural = relativistic_fluid_stress_energy(
        metric,
        RelativisticFluidState(0.02, 0.003, velocity(())),
    )
    e0 = 512994.17164886114
    si = relativistic_fluid_stress_energy(
        metric,
        RelativisticFluidState(e0 * 0.02, e0 * 0.003, velocity(()), unit_lane="SI"),
    )
    natural_projection = project_stress_energy_3p1(metric, natural, unit_lane="natural")
    si_projection = project_stress_energy_3p1(metric, si, unit_lane="SI_J_m^-3")

    assert np.allclose(si, e0 * natural)
    assert si_projection.energy_density == pytest.approx(e0 * natural_projection.energy_density)
    assert np.allclose(si_projection.spatial_stress, e0 * natural_projection.spatial_stress)


def test_contract_preserves_ontology_and_open_boundaries() -> None:
    contract = curved_3p1_matter_wiring_contract()
    assert contract["ontology"]["Phi"].startswith("excluded")
    assert contract["ontology"]["R_gen"].startswith("excluded")
    assert "matter-state time evolution" in contract["not_implemented"]
    assert "constraint-preserving non-periodic boundaries" in contract["not_implemented"]
