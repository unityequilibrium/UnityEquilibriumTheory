"""Independent fixed-Phi action regressions, not full thermal-bridge acceptance."""
from math import exp, log1p, pi, sqrt
import numpy as np
import pytest
from scipy.integrate import quad

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig, o2_equilibrium_state
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    condensed_quasiparticle_energies,
    finite_temperature_o2_quasiparticle_contract,
    quasiparticle_pressure,
)


def config(z=1., mass_sq=None, quartic=1.):
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(matter=CovariantMatterConfig(
            matter_kinetic=z, matter_mass_sq=z if mass_sq is None else mass_sq,
            matter_quartic=quartic, response_coupling=0.,
        )),
        quadrature_order=192,
    )


@pytest.mark.parametrize("z", [.25, 1., 4.])
@pytest.mark.parametrize("k", [0., 1e-8, 1e-4, .1, 1., 5.])
def test_spectrum_matches_independent_linear_generator(z, k):
    cfg = config(z)
    mu = sqrt(3.)
    q = z*mu**2-z
    generator = np.array([
        [0., 0., 1., 0.], [0., 0., 0., 1.],
        [-k*k-2*q/z, 0., 0., -2*mu],
        [0., -k*k, 2*mu, 0.],
    ])
    eigenvalues = np.linalg.eigvals(generator)
    assert np.max(abs(eigenvalues.real)) < 1e-10
    expected_squared = np.sort(eigenvalues.imag**2)
    upper, lower = condensed_quasiparticle_energies(k, mu, 0., cfg)
    np.testing.assert_allclose(
        [lower**2, lower**2, upper**2, upper**2],
        expected_squared, rtol=1e-10, atol=1e-11,
    )


@pytest.mark.parametrize("z", [.25, 1., 4.])
@pytest.mark.parametrize("sign", [-1., 1.])
def test_small_momentum_sound_matches_tree_eos_without_clipping(z, sign):
    cfg = config(z)
    mu = sign*sqrt(3.)
    state = o2_equilibrium_state(mu, 0., cfg.eos)
    for k in [1e-5, 1e-8, 1e-10]:
        _, lower = condensed_quasiparticle_energies(k, mu, 0., cfg)
        assert lower > 0.
        assert (lower/k)**2 == pytest.approx(state.sound_speed_sq, rel=1e-8)


@pytest.mark.parametrize("T,mu", [(.25, .2), (.15, sqrt(3.))])
def test_canonical_field_rescaling_preserves_pressure(T, mu):
    original = config(4., 4., 1.)
    canonical = config(1., 1., 1./16)
    assert quasiparticle_pressure(T, mu, 0., original) == pytest.approx(
        quasiparticle_pressure(T, mu, 0., canonical), rel=1e-11
    )


@pytest.mark.parametrize("z", [.25, 1., 4.])
def test_normal_pressure_matches_independent_canonical_bose_integral(z):
    T, mu = .25, .2
    def integrand(k):
        energy = sqrt(k*k+1.)
        return T*k*k/(2*pi*pi)*sum(
            -log1p(-exp(-(energy+s*mu)/T)) for s in [-1, 1]
        )
    expected, error = quad(integrand, 0., np.inf, epsabs=1e-13)
    assert error < 1e-11
    assert quasiparticle_pressure(T, mu, 0., config(z)) == pytest.approx(
        expected, rel=1e-9, abs=1e-13
    )


@pytest.mark.parametrize("z", [.25, 1., 4.])
def test_condensed_spectrum_has_correct_one_sided_boundary(z):
    mu, k = sqrt(1.+1e-8), .2
    actual = condensed_quasiparticle_energies(k, mu, 0., config(z))
    expected = (sqrt(k*k+1.)+1., sqrt(k*k+1.)-1.)
    np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=1e-8)
    with pytest.raises(ValueError):
        quasiparticle_pressure(.2, 1., 0., config(z))


def test_contract_declares_fixed_response_and_canonical_normalization():
    contract = finite_temperature_o2_quasiparticle_contract()
    assert contract["response_policy"] == "FIXED_PHI_BACKGROUND"
    assert contract["spectrum_revision"] == "FIXED_PHI_CANONICAL_V2"
    assert "canonical_field_map" in contract["equations"]
    assert "normal_quasiparticles" in contract["equations"]
    assert "not" in contract["claim_boundary"]


@pytest.mark.parametrize("T,mu", [(.25, .2), (.15, sqrt(3.))])
def test_static_response_is_invariant_under_canonical_field_rescaling(T, mu):
    from docs.core.uet_o2_formal_transverse_response import (
        formal_transverse_quasiparticle_response,
    )
    original = formal_transverse_quasiparticle_response(T, mu, 0., config(4., 4., 1.))
    canonical = formal_transverse_quasiparticle_response(T, mu, 0., config(1., 1., 1./16))
    assert original.normal_momentum_susceptibility == pytest.approx(
        canonical.normal_momentum_susceptibility, rel=1e-10
    )
    assert original.condensate_phase_stiffness == pytest.approx(
        canonical.condensate_phase_stiffness, rel=1e-12
    )


@pytest.mark.parametrize("z", [.25, 1., 4.])
def test_normal_static_response_matches_enthalpy(z):
    from docs.core.uet_o2_finite_temperature_quasiparticle_eos import finite_temperature_o2_state
    from docs.core.uet_o2_formal_transverse_response import formal_transverse_quasiparticle_response
    cfg = config(z)
    state = finite_temperature_o2_state(.25, .2, 0., cfg)
    response = formal_transverse_quasiparticle_response(.25, .2, 0., cfg)
    # Integration by parts for this ideal relativistic normal gas only.
    assert response.normal_momentum_susceptibility == pytest.approx(
        state.energy_density + state.pressure, rel=2e-6
    )


def test_primary_audit_serializes_inapplicable_goldstone_without_masking_errors():
    import json
    from dataclasses import replace
    from docs.core.uet_o2_finite_temperature_quasiparticle_eos import finite_temperature_o2_state
    from docs.scripts.audit.audit_topic13_finite_temperature_quasiparticle_eos import state_record
    normal = finite_temperature_o2_state(.25, .2, 0., config())
    record = state_record(normal)
    assert record["goldstone_energy_at_zero_momentum"] is None
    json.dumps(record, allow_nan=False)
    condensed = finite_temperature_o2_state(.15, sqrt(3.), 0., config())
    corrupt = replace(condensed, goldstone_energy_at_zero_momentum=float("nan"))
    with pytest.raises(ValueError):
        json.dumps(state_record(corrupt), allow_nan=False)


def test_independent_audit_detects_broken_spectrum(monkeypatch):
    from docs.scripts.audit import audit_topic13_fixed_phi_spectrum_repair as audit
    original = audit.condensed_quasiparticle_energies

    def broken(*args, **kwargs):
        upper, lower = original(*args, **kwargs)
        return upper*sqrt(1.25), lower

    monkeypatch.setattr(audit, "condensed_quasiparticle_energies", broken)
    checks = audit.fixed_phi_witnesses()["checks"]
    assert not checks["independent_action_spectrum"]
    assert not checks["corrected_gap_squared"]


def test_import_inventory_tracks_transitive_paths_without_reading_payloads(tmp_path):
    from docs.scripts.audit.audit_topic13_fixed_phi_spectrum_repair import consumer_inventory
    core = tmp_path / "docs/core"
    audit = tmp_path / "docs/scripts/audit"
    core.mkdir(parents=True)
    audit.mkdir(parents=True)
    (core / "uet_o2_finite_temperature_quasiparticle_eos.py").write_text("", encoding="utf-8")
    (core / "direct.py").write_text(
        "from docs.core.uet_o2_finite_temperature_quasiparticle_eos import config",
        encoding="utf-8",
    )
    (audit / "indirect.py").write_text("from docs.core import direct", encoding="utf-8")
    (audit / "unrelated.py").write_text("import math", encoding="utf-8")
    # Invalid UTF-8 would raise if the scanner opened this data payload.
    (core / "not_an_input.json").write_bytes(bytes([255]))
    result = consumer_inventory(tmp_path)
    rows = {row["path"]: row["relationship"] for row in result["review_required"]}
    assert rows == {
        "docs/core/direct.py": "DIRECT",
        "docs/scripts/audit/indirect.py": "TRANSITIVE",
    }
    assert not result["parse_errors"]
    assert not result["experimental_payloads_read"]
