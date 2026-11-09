from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

AUDIT_PATH = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_reduced_wave_sbp_sat.py"
SPEC = importlib.util.spec_from_file_location("reduced_wave_sbp_sat_audit", AUDIT_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load audit module: {AUDIT_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)

ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_reduced_wave_sbp_sat_comparator.json"
)


def test_random_state_energy_rate_matches_sbp_defect_decomposition() -> None:
    operators = AUDIT.TT.legendre_lobatto_operators(12)
    random = np.random.default_rng(1417)
    state = AUDIT.ReducedTTState(
        random.normal(size=(2, 13)),
        random.normal(size=(2, 13)),
    )
    measured, _, _, decomposition_residual = AUDIT._energy_identity_residual(
        state, operators
    )
    assert measured < 0.0
    assert decomposition_residual < 2.0e-11


def test_sat_energy_growth_is_nonpositive_to_roundoff() -> None:
    operators = AUDIT.TT.legendre_lobatto_operators(20)
    growth_rate = AUDIT._max_energy_growth_rate(
        operators.derivative,
        operators.norm_weights,
        boundary_method="incoming_characteristic_sat",
    )
    assert growth_rate <= 2.0e-9


def test_strong_differentiated_target_has_positive_energy_growth_directions() -> None:
    lgl = AUDIT.TT.legendre_lobatto_operators(12)
    cheb = AUDIT.FULL_U1.chebyshev_lobatto_operators(12)
    lgl_rate = AUDIT._max_energy_growth_rate(
        lgl.derivative,
        lgl.norm_weights,
        boundary_method="strong_differentiated_target",
    )
    cheb_rate = AUDIT._max_energy_growth_rate(
        cheb.derivative,
        AUDIT.FULL_U1._clenshaw_curtis_weights(12),
        boundary_method="strong_differentiated_target",
    )
    assert lgl_rate > 1.0e-6
    assert cheb_rate > 1.0e-6


def test_second_order_rhs_matches_first_order_sat_on_reduction_subspace() -> None:
    operators = AUDIT.TT.legendre_lobatto_operators(12)
    random = np.random.default_rng(20260925)
    metric = random.normal(size=(2, 13))
    momentum = random.normal(size=(2, 13))
    first_order = AUDIT.TT.TTWaveState(
        metric,
        momentum,
        metric @ operators.derivative.T,
    )
    first_rhs = AUDIT.TT.tt_wave_rhs(first_order, operators)
    reduced_rhs = AUDIT.reduced_tt_sbp_rhs(
        AUDIT.ReducedTTState(metric, momentum), operators
    )
    assert np.max(np.abs(first_rhs.displacement - reduced_rhs.metric)) < 2.0e-13
    assert np.max(np.abs(first_rhs.momentum - reduced_rhs.momentum)) < 2.0e-12
    assert np.max(
        np.abs(first_rhs.spatial_gradient - reduced_rhs.metric @ operators.derivative.T)
    ) < 2.0e-12


def test_artifact_passes_without_claim_or_dependency_promotion() -> None:
    artifact = AUDIT.build_artifact()
    assert artifact["status"] == "PASS_REDUCED_TT_SBP_SAT_COMPARATOR"
    assert all(artifact["checks"].values())
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["claim_promotion"] is False
    assert artifact["major_result"]["dependency_unlocked"].startswith("none;")
    assert artifact["scope"]["full_first_order_gh_cpbc"] is False


def test_artifact_source_hashes_match() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for relative_path, expected_hash in artifact["source_hashes"].items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash


def run_tests() -> None:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
