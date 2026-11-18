"""Layer 2 from the layer 1 action: chi as a thermal bath for phi (stage 3, wave L2-1).

Checks through the general one-loop integral (wightman_greater), not through the closed forms:
1. The canonical couplings read from the action code equal sigma = h sqrt(eps)/(Z sqrt(k)), M_phi^2 = mu^2/k,
   M_chi^2 = m^2/Z, and sigma scales as sqrt(eps) (eps is partly redundant, as THEORY_CARD states).
2. KMS emerges: Pi>(w) = exp(w/T) Pi<(w) at random kinematic points, and the temperature read back from the
   ratio is the bath temperature. Friction (rho) and noise (Pi_sym) therefore obey fluctuation-dissipation.
3. Known limits: q -> 0 gives the pair-decay closed form with Bose enhancement; T -> 0 gives the textbook
   width of phi -> chi chi; the Landau-damping closed form matches in 0 < w < q.
4. Ohmic limit: rho/(2w) -> gamma(q, T) with an error of order w^2, so the Caldeira-Leggett friction is derived.
5. Threshold and low T: no dissipation for a timelike mode below the pair threshold; gamma(q, T) -> 0 as T -> 0.
"""

from __future__ import annotations

import importlib
import math
import random

import pytest

pytestmark = pytest.mark.physics

l2 = importlib.import_module("core.03_lanes.open_system.uet_layer2_from_action")
cov = importlib.import_module("core.02_equations.covariant.uet_covariant_matter")
resp = importlib.import_module("core.02_equations.covariant.uet_covariant_response")


def _configs(seed: int):
    rng = random.Random(seed)
    eps, k, mu2 = rng.uniform(0.05, 2.0), rng.uniform(0.3, 3.0), rng.uniform(0.2, 4.0)
    Z, m2, h = rng.uniform(0.3, 3.0), rng.uniform(0.1, 3.0), rng.uniform(0.05, 2.0)
    rc = resp.CovariantResponseConfig(epsilon_nc=eps, response_kinetic=k, response_mass_sq=mu2, response_quartic=0.3)
    mc = cov.CovariantMatterConfig(matter_kinetic=Z, matter_mass_sq=m2, matter_quartic=0.4, response_coupling=h)
    return rc, mc, (eps, k, mu2, Z, m2, h)


@pytest.mark.parametrize("seed", range(6))
def test_canonical_couplings_are_read_from_the_action(seed: int) -> None:
    rc, mc, (eps, k, mu2, Z, m2, h) = _configs(seed)
    c = l2.canonical_couplings(rc, mc)
    assert c.sigma == pytest.approx(h * math.sqrt(eps) / (Z * math.sqrt(k)), rel=1e-6)
    assert c.M_phi == pytest.approx(math.sqrt(mu2 / k), rel=1e-6)
    assert c.M_chi == pytest.approx(math.sqrt(m2 / Z), rel=1e-6)


def test_portal_strength_scales_as_sqrt_eps() -> None:
    rc, mc, _ = _configs(11)
    rc4 = resp.CovariantResponseConfig(epsilon_nc=4 * rc.epsilon_nc, response_kinetic=rc.response_kinetic,
                                       response_mass_sq=rc.response_mass_sq, response_quartic=rc.response_quartic)
    assert l2.canonical_couplings(rc4, mc).sigma / l2.canonical_couplings(rc, mc).sigma == pytest.approx(2.0, rel=1e-6)


def _kinematic_point(rng: random.Random, M: float) -> tuple[float, float]:
    """A point that is either above the pair threshold (timelike) or spacelike."""
    while True:
        w, q = rng.uniform(-4.0, 4.0), rng.uniform(0.05, 3.0)
        s = w * w - q * q
        if s > 4 * M * M * 1.02 or s < -0.01:
            return w, q


@pytest.mark.parametrize("seed", range(8))
def test_kms_emerges_from_the_thermal_bath(seed: int) -> None:
    rng = random.Random(100 + seed)
    M, sigma, T = rng.uniform(0.2, 1.0), rng.uniform(0.1, 1.0), rng.uniform(0.2, 2.0)
    w, q = _kinematic_point(rng, M)
    greater = l2.wightman_greater(w, q, T, M, sigma)
    lesser = l2.wightman_greater(-w, q, T, M, sigma)
    assert greater / lesser == pytest.approx(math.exp(w / T), rel=1e-9)
    assert w / math.log(greater / lesser) == pytest.approx(T, rel=1e-9)  # the bath temperature is read back


@pytest.mark.parametrize("w", [1.2, 2.0, 3.5])
def test_q_to_zero_reproduces_pair_decay_with_bose_enhancement(w: float) -> None:
    M, sigma, T = 0.5, 0.7, 0.8
    assert l2.spectral(w, 1e-4, T, M, sigma) == pytest.approx(l2.rho_q0(w, T, M, sigma), rel=1e-6)


@pytest.mark.parametrize("seed", range(5))
def test_zero_temperature_width_is_the_textbook_decay_rate(seed: int) -> None:
    rng = random.Random(200 + seed)
    M_chi, sigma = rng.uniform(0.1, 1.0), rng.uniform(0.1, 1.0)
    M_phi = 2 * M_chi * rng.uniform(1.05, 4.0)
    width = l2.damping_rate(M_phi, 1e-4, 1e-9, M_chi, sigma)  # general integral at q -> 0, T -> 0
    assert width == pytest.approx(l2.zero_temperature_decay_rate(M_phi, M_chi, sigma), rel=1e-6)


@pytest.mark.parametrize("seed", range(6))
def test_landau_damping_closed_form(seed: int) -> None:
    rng = random.Random(300 + seed)
    M, sigma, T = rng.uniform(0.2, 1.0), rng.uniform(0.1, 1.0), rng.uniform(0.2, 2.0)
    q = rng.uniform(0.3, 3.0)
    w = q * rng.uniform(0.05, 0.95)
    assert l2.spectral(w, q, T, M, sigma) == pytest.approx(l2.rho_landau(w, q, T, M, sigma), rel=1e-9)


def test_ohmic_friction_is_derived_with_order_w2_error() -> None:
    M, sigma, T, q = 0.5, 0.7, 0.8, 1.0
    gamma = l2.caldeira_leggett_gamma(q, T, M, sigma)
    errs = [abs(l2.spectral(w, q, T, M, sigma) / (2 * w) - gamma) for w in (2e-2, 1e-2, 5e-3)]
    assert errs[0] / errs[1] == pytest.approx(4.0, rel=0.05)
    assert errs[1] / errs[2] == pytest.approx(4.0, rel=0.05)


def test_no_dissipation_below_the_pair_threshold() -> None:
    M, sigma, T = 0.5, 0.7, 0.8
    assert l2.rho_q0(0.99, T, M, sigma) == 0.0
    assert l2.spectral(0.9, 0.3, T, M, sigma) == 0.0  # timelike, s < 4 M^2


def test_friction_vanishes_as_temperature_goes_to_zero() -> None:
    M, sigma, q = 0.5, 0.7, 1.0
    E0 = math.sqrt(q * q / 4 + M * M)
    for T in (0.1, 0.05, 0.02):
        g = l2.caldeira_leggett_gamma(q, T, M, sigma)
        assert g == pytest.approx(2 * sigma**2 * math.exp(-E0 / T) / (16 * math.pi * q), rel=1e-6 + math.exp(-E0 / T))
