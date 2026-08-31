"""Canonical field covariance and charge labels of the kinetic comparator."""
import numpy as np
import pytest

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import FiniteTemperatureO2QuasiparticleConfig
from docs.core.uet_o2_kinetic_collision_kubo import _normal_state_inputs, kinetic_collision_state


def config(z=1., coupling=.5):
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(matter=CovariantMatterConfig(
            matter_kinetic=z, matter_mass_sq=z,
            matter_quartic=coupling*z*z, response_coupling=0.,
        )),
    )


def state(cfg, mu=.2, quantum=False):
    return kinetic_collision_state(
        .25, mu, 0., cfg, quadrature_order=32, angular_order=24,
        cutoff_factor=20., include_final_state_bose_enhancement=quantum,
    )


@pytest.mark.parametrize("z", [.25, 1., 4.])
@pytest.mark.parametrize("mu", [-.2, .2])
def test_inputs_are_canonical_and_chemical_potential_is_signed(z, mu):
    t, physical_mu, mass, occupation_mu, coupling = _normal_state_inputs(.25, mu, 0., config(z))
    assert (t, physical_mu, mass, occupation_mu, coupling) == pytest.approx(
        (.25, mu, 1., mu, .5)
    )


@pytest.mark.parametrize("z", [.25, 4.])
@pytest.mark.parametrize("quantum", [False, True])
def test_kinetic_outputs_are_invariant_under_field_rescaling(z, quantum):
    original, canonical = state(config(z), quantum=quantum), state(config(), quantum=quantum)
    for name in (
        "effective_mass", "quartic_coupling", "momentum_cutoff", "reference_momentum",
        "drude_weight_by_species", "collision_width_by_species",
        "kinetic_coefficient_by_species",
    ):
        np.testing.assert_allclose(getattr(original, name), getattr(canonical, name), rtol=1e-12, atol=0.)


@pytest.mark.parametrize("quantum", [False, True])
def test_charge_conjugation_swaps_labeled_species(quantum):
    positive, negative = state(config(), quantum=quantum), state(config(), mu=-.2, quantum=quantum)
    for name in ("drude_weight_by_species", "collision_width_by_species", "kinetic_coefficient_by_species"):
        np.testing.assert_allclose(getattr(positive, name), getattr(negative, name)[::-1], rtol=1e-12, atol=0.)
    assert positive.drude_weight == pytest.approx(negative.drude_weight, rel=1e-12)


def test_declared_comparator_coupling_scaling():
    base, doubled = state(config()), state(config(coupling=1.))
    np.testing.assert_allclose(doubled.collision_width_by_species, 4*np.array(base.collision_width_by_species), rtol=1e-12)
    assert doubled.kinetic_coefficient == pytest.approx(base.kinetic_coefficient/4, rel=1e-12)


@pytest.mark.parametrize("mu", [-1., 1., -1.1, 1.1])
def test_condensed_or_critical_inputs_remain_rejected(mu):
    with pytest.raises(ValueError):
        _normal_state_inputs(.25, mu, 0., config(4.))


def test_potential_derivatives_are_independent_of_legacy_tensor():
    from docs.scripts.audit.audit_topic13_kinetic_canonical_action_match import potential_vertex_witnesses
    witness = potential_vertex_witnesses()
    assert witness["derivative_verification_pass"]
    for row in witness["rows"]:
        assert row["potential_d1111"] == pytest.approx(6*row["lambda_c"])
        assert row["potential_d1122"] == pytest.approx(2*row["lambda_c"])
        assert row["charged_all_incoming_contact_magnitude"] == pytest.approx(4*row["lambda_c"])
        expected = np.isclose(row["legacy_tensor_1111"], row["potential_d1111"])
        assert row["legacy_tensor_matches_potential"] == bool(expected)


def test_vertex_audit_rejects_changed_production_potential(monkeypatch):
    from docs.scripts.audit import audit_topic13_kinetic_canonical_action_match as audit
    original = audit.matter_potential
    monkeypatch.setattr(audit, "matter_potential", lambda fields, cfg: 2*original(fields, cfg))
    assert not audit.potential_vertex_witnesses()["derivative_verification_pass"]


def test_comparator_contract_does_not_claim_full_action_tensor():
    from docs.core.uet_o2_kinetic_collision_kubo import kinetic_collision_contract
    contract = kinetic_collision_contract()
    assert contract["normalization_revision"] == "CANONICAL_NORMAL_KINETIC_V2"
    assert contract["species_order"] == [-1, 1]
    assert contract["excluded"]["full_action_tensor_and_channel_symmetry_matching"]


@pytest.mark.parametrize("z", [.25, 4.])
def test_transition_consumer_has_canonical_covariance(z):
    from docs.core.uet_o2_action_derived_transition_kernel import action_derived_transition_kernel_state
    original = action_derived_transition_kernel_state(.22, .35, 0., config(z, coupling=1.))
    canonical = action_derived_transition_kernel_state(.22, .35, 0., config(coupling=1.))
    np.testing.assert_allclose(original.channel_rates, canonical.channel_rates, rtol=1e-12, atol=0.)
    np.testing.assert_allclose(original.state_energies, canonical.state_energies, rtol=1e-12, atol=0.)
    assert max(original.channel_detailed_balance_residuals) < 1e-10
