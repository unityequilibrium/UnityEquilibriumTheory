from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_curved_3p1_generalized_harmonic import GHNonlinearParameters
from docs.core.uet_curved_3p1_gh_evolution import (
    GHEvolutionState,
    GHTimeIntegrationParameters,
    evolve_periodic_vacuum_gh,
    generalized_harmonic_time_evolution_contract,
    gh_constraint_norms,
    harmonic_gauge_wave_state,
)


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "docs/core/artifacts/curved_3p1_gh_time_evolution_verification.json"
FORMULA = ROOT / "docs/core/artifacts/curved_3p1_gh_time_evolution_formula_audit.json"
GATE = ROOT / "docs/core/artifacts/curved_3p1_gh_time_evolution_gate.json"


def test_cfl_domain_is_fail_closed() -> None:
    assert GHTimeIntegrationParameters(cfl=0.2).maximum_cfl == 0.2
    with pytest.raises(ValueError):
        GHTimeIntegrationParameters(cfl=0.21)
    with pytest.raises(ValueError):
        GHTimeIntegrationParameters(cfl=0.0)


def test_exact_gauge_wave_evolves_without_projection_or_filtering() -> None:
    state, source, source_derivative, spacing = harmonic_gauge_wave_state(
        (12, 5, 5), (1.0, 1.0, 1.0), amplitude=0.05
    )
    result = evolve_periodic_vacuum_gh(
        state, source, source_derivative, spacing, 0.02
    )
    exact = harmonic_gauge_wave_state(
        (12, 5, 5), (1.0, 1.0, 1.0), time=0.02, amplitude=0.05
    )[0]
    assert np.sqrt(np.mean((result.state.spacetime_metric - exact.spacetime_metric) ** 2)) < 5.0e-6
    assert result.maximum_observed_courant <= 0.08 + 1.0e-14
    assert result.run_contract["constraint_projection"] is False
    assert result.run_contract["numerical_filtering"] is False
    assert result.diagnostics[-1].gauge_linf < 1.0e-12


def test_constant_offdiagonal_reduction_violation_damps_at_gamma2_rate() -> None:
    shape = (5, 5, 5)
    metric = np.broadcast_to(np.diag([-1.0, 1.0, 1.0, 1.0]), shape + (4, 4)).copy()
    phi = np.zeros(shape + (3, 4, 4))
    phi[..., 0, 2, 3] = phi[..., 0, 3, 2] = 1.0e-6
    state = GHEvolutionState(metric, np.zeros_like(metric), phi)
    source = np.zeros(shape + (4,))
    source_derivative = np.zeros(shape + (4, 4))
    initial = gh_constraint_norms(state, source, (0.2, 0.2, 0.2))
    result = evolve_periodic_vacuum_gh(
        state,
        source,
        source_derivative,
        (0.2, 0.2, 0.2),
        0.2,
        GHNonlinearParameters(gamma2=1.0),
    )
    ratio = result.diagnostics[-1].reduction_l2 / initial.reduction_l2
    assert math.isclose(ratio, math.exp(-0.2), rel_tol=1.0e-8)


def test_contract_keeps_boundaries_matter_and_observables_open() -> None:
    contract = generalized_harmonic_time_evolution_contract()
    assert contract["integrator"] == "classical explicit RK4"
    assert "constraint-preserving non-periodic boundaries" in contract["not_implemented"]
    assert "matter stress-energy wiring" in contract["not_implemented"]
    assert "R_gen" in contract["excluded_state"]


def test_generated_time_evolution_artifacts_are_hash_linked() -> None:
    verification = json.loads(VERIFY.read_text(encoding="utf-8"))
    formula = json.loads(FORMULA.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    assert verification["status"] == "PASS_GH_PERIODIC_VACUUM_TIME_EVOLUTION"
    assert verification["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert formula["status"] == "PASS_GH_TIME_EVOLUTION_NUMERICAL_CONTRACT"
    assert gate["status"] == "PARTIAL_GH_PERIODIC_VACUUM_EVOLUTION_READY"
    assert gate["requirements"]["constraint_propagation_convergence"] == "PASS"
    assert gate["requirements"]["constraint_preserving_boundaries"] == "OPEN"
    for relative_path, expected_hash in verification["source_hashes"].items():
        assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == expected_hash
    for evidence in gate["evidence_artifacts"]:
        assert hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest() == evidence["sha256"]
