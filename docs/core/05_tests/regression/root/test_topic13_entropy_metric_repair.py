"""Independent Bose entropy Hessian and streaming normalization witnesses."""
from docs.core.core_paths import repo_root
import json
from pathlib import Path
import numpy as np
import pytest


def bose_entropy(f):
    return (1+f)*np.log1p(f)-f*np.log(f)


@pytest.mark.parametrize("temperature", [.22, .5, 2.])
def test_bose_entropy_hessian_matches_susceptibility_coordinates(temperature):
    f = np.array([.2, .7, 2.])
    measure = np.array([.4, .7, 1.2])
    weights = measure*f*(1+f)/temperature
    errors = []
    for amplitude in (.001, .0005, .00025):
        psi = amplitude*np.array([.2, -.1, .3])
        delta_f = f*(1+f)*psi/temperature
        z = np.sqrt(weights)*psi
        deficit = np.dot(measure, bose_entropy(f)+np.log1p(1/f)*delta_f-bose_entropy(f+delta_f))
        predicted = np.dot(z, z)/(2*temperature)
        errors.append(abs(deficit/predicted-1))
    assert errors[2] < errors[1] < errors[0]
    assert errors[2] < .001


@pytest.mark.parametrize("charge", [-1., 1.])
def test_fixed_pressure_bose_streaming_drives_existing_X(charge):
    t, mu, energy, h, grad_t = .5, .2, 1.3, 2., -.01
    grad_mu = -(h-mu)*grad_t/t
    def f(x):
        return 1/np.expm1((energy-charge*(mu+grad_mu*x))/(t+grad_t*x))
    dx = .001
    minus_stream = -(f(dx)-f(-dx))/(2*dx)
    expected = f(0)*(1+f(0))/t*(energy-h*charge)*(-grad_t/t)
    assert minus_stream == pytest.approx(expected, rel=1.e-7)


def test_historical_counterexample_is_preserved():
    root = repo_root()
    old = json.loads((root/"docs/core/07_artifacts/topic13/t13_entropy_force_convention_audit.json").read_text())
    assert old["status"] == "BLOCKED_PHYSICAL_ENTROPY_INTERPRETATION"
    assert old["witnesses"][0]["reported_over_divergence"] == pytest.approx(.22)
