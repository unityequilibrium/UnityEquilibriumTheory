from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_dynamical_stability import (
    benettin_qr,
    classify_dynamical_regime,
    lyapunov_resolution,
    matter_space_tangent_rhs,
    pack_matter_space_state,
    shadow_trajectory_exponent,
    validate_diagnostic_contract,
)
from docs.core.uet_matter_space import MatterSpaceConfig, MatterSpaceState, matter_space_rhs


def test_matter_space_tangent_matches_central_difference_jvp() -> None:
    rng = np.random.default_rng(17)
    size = 12
    state = MatterSpaceState(
        rng.normal(scale=0.2, size=size),
        rng.normal(scale=0.1, size=size),
        rng.normal(scale=0.05, size=size),
    )
    perturbation = MatterSpaceState(
        rng.normal(size=size), rng.normal(size=size), rng.normal(size=size)
    )
    config = MatterSpaceConfig(matter_dynamics="nonconserved")
    epsilon = 1.0e-7

    def shifted(sign: float) -> MatterSpaceState:
        return MatterSpaceState(
            state.C + sign * epsilon * perturbation.C,
            state.space_response + sign * epsilon * perturbation.space_response,
            state.space_rate + sign * epsilon * perturbation.space_rate,
        )

    plus = matter_space_rhs(shifted(1.0), 0.2, config)[:3]
    minus = matter_space_rhs(shifted(-1.0), 0.2, config)[:3]
    finite_difference = np.concatenate(
        [
            (plus[index] - minus[index]) / (2.0 * epsilon)
            for index in range(3)
        ]
    )
    tangent = pack_matter_space_state(
        matter_space_tangent_rhs(state, perturbation, 0.2, config)
    )
    np.testing.assert_allclose(tangent, finite_difference, rtol=2.0e-7, atol=2.0e-7)


def test_benettin_and_shadow_recover_stable_linear_exponent() -> None:
    decay = 0.4
    dt = 0.05
    multiplier = np.exp(-decay * dt)

    def step(state: np.ndarray, _: int) -> np.ndarray:
        return multiplier * state

    def tangent_step(_: np.ndarray, tangent: np.ndarray, __: int) -> np.ndarray:
        return multiplier * tangent

    tangent = benettin_qr(step, tangent_step, np.array([1.0]), dt, 400)
    shadow = shadow_trajectory_exponent(
        step, np.array([1.0]), dt, 400, perturbation_amplitude=1.0e-7
    )
    assert tangent["lambda_max"] == pytest.approx(-decay, abs=1.0e-12)
    assert shadow["lambda_max"] == pytest.approx(-decay, abs=2.0e-7)


def test_logistic_map_recovers_ln_two() -> None:
    def step(state: np.ndarray, _: int) -> np.ndarray:
        return np.array([4.0 * state[0] * (1.0 - state[0])])

    def tangent_step(state: np.ndarray, tangent: np.ndarray, _: int) -> np.ndarray:
        return (4.0 - 8.0 * state[0]) * tangent

    estimate = benettin_qr(
        step,
        tangent_step,
        np.array([0.123456789]),
        dt=1.0,
        steps=30000,
        transient_steps=1000,
    )
    assert estimate["lambda_max"] == pytest.approx(np.log(2.0), abs=8.0e-3)


def test_classifier_requires_numerical_and_physical_gates() -> None:
    resolution = lyapunov_resolution(0.01, 0.02, 0.005, 0.015)
    assert resolution == pytest.approx(0.02)
    assert classify_dynamical_regime(
        lambda_max=0.1,
        lambda_resolution_value=resolution,
        early_ftle_positive=True,
        boundedness=True,
        stationarity=True,
        ledger_pass=True,
        conservation_pass=True,
        causal_pass=True,
        method_agreement=True,
    ) == "CHAOS_CANDIDATE_DIAGNOSTIC"
    assert classify_dynamical_regime(
        lambda_max=0.1,
        lambda_resolution_value=resolution,
        early_ftle_positive=True,
        boundedness=True,
        stationarity=True,
        ledger_pass=False,
        conservation_pass=True,
        causal_pass=True,
        method_agreement=True,
    ) == "NUMERICAL_INSTABILITY"


def test_contract_excludes_trace_and_observer_records_from_state() -> None:
    record = {
        "diagnostic_id": "test",
        "owner_topic": "core",
        "equation_registry_ids": ["uet.dynamics.tangent_map"],
        "state_variables": ["C", "Phi", "Pi"],
        "excluded_variables": ["R_gen", "R_obs"],
        "unit_lane": "normalized",
        "forcing_class": "closed_autonomous",
        "noise_coupling": "none",
        "state_metric": "normalized_block_l2",
        "estimator": "BENETTIN_QR_TANGENT",
        "transient_window": 10,
        "renormalization_interval": 1,
        "perturbation_amplitudes": [1.0e-8, 1.0e-7, 1.0e-6],
        "resolution_grid": {"dt": [0.1, 0.05]},
        "lambda_max": -0.4,
        "lambda_spectrum": [-0.4],
        "confidence_or_block_error": 0.0,
        "lambda_resolution": 0.01,
        "boundedness": True,
        "stationarity": True,
        "ledger_status": "PASS",
        "conservation_status": "PASS",
        "causal_status": "PASS",
        "method_agreement": True,
        "classification": "NONCHAOTIC_STABLE_DIAGNOSTIC",
        "controlling_blocker": "none_for_method_control",
        "evidence_hashes": {},
        "claim_boundary": "method control only",
    }
    validate_diagnostic_contract(record)
    record["state_variables"].append("R_gen")
    with pytest.raises(ValueError, match="not dynamical"):
        validate_diagnostic_contract(record)
