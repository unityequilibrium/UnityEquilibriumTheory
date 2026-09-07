"""Tests for the coupled response-mode heat-carrier no-go."""
import numpy as np

from docs.scripts.audit.audit_topic13_coupled_response_heat_carrier_no_go import (
    source_rank_witness,
)


def _witness(mu=0.2):
    return source_rank_witness(
        chemical_potential=mu,
        radial_order=6,
        angular_order=4,
        azimuth_order=4,
        cutoff=6.0,
        metric_order=96,
    )


def test_physical_grand_heat_source_remains_charge_rank_one():
    witness = _witness()
    assert witness["projected_momentum_source_norm"] <= 1.0e-10
    assert witness["heat_charge_identity_relative_residual"] <= 1.0e-10
    assert witness["charge_heat_source_rank"] == 1


def test_zero_mu_projected_heat_source_vanishes():
    witness = _witness(0.0)
    assert np.linalg.norm(witness["projected_grand_heat_source"]) <= 1.0e-10


def test_neutral_trial_is_independent_but_not_conserved():
    witness = _witness()
    assert witness["charge_neutral_trial_rank"] == 2
    assert witness["neutral_count_relaxation_relative"] > 1.0e-12
    assert witness["total_count_null_relative"] <= 1.0e-10
    assert witness["neutral_trial_admissibility"].startswith("REJECTED")


def test_energy_weighted_trial_cannot_be_relabelled_as_heat_current():
    witness = _witness()
    assert witness["charge_energy_moment_trial_rank"] == 2
    assert "E*p/T^2" in witness["vector_basis"]
    assert witness["energy_moment_trial_admissibility"].startswith("REJECTED")


def test_active_collision_solve_is_well_defined():
    witness = _witness()
    assert witness["minimum_active_collision_rate"] > 0.0
    assert witness["collision_solve_relative_residual"] <= 1.0e-8
