from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[5]
AUDIT_PATH = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_full_u1_cpbc_slab.py"
ARTIFACT_PATH = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_full_u1_cpbc_slab_pilot.json"
)
REDUCED_ARTIFACT_PATH = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_reduced_wave_boundary_comparator.json"
)
_SPEC = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_full_u1_audit_test", AUDIT_PATH
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("cannot load the full-u1 slab audit")
AUDIT = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = AUDIT
_SPEC.loader.exec_module(AUDIT)
_BUILT_ARTIFACT: dict | None = None


def _artifact() -> dict:
    global _BUILT_ARTIFACT
    if _BUILT_ARTIFACT is None:
        _BUILT_ARTIFACT = AUDIT.build_artifact()
    return _BUILT_ARTIFACT


def test_chebyshev_lobatto_derivative_is_polynomial_exact() -> None:
    operators = AUDIT.chebyshev_lobatto_operators(8)
    residuals = []
    for degree in range(9):
        exact = (
            np.zeros_like(operators.nodes)
            if degree == 0
            else degree * operators.nodes ** (degree - 1)
        )
        residuals.append(
            float(
                np.max(
                    np.abs(operators.derivative @ operators.nodes**degree - exact)
                )
            )
        )
    assert max(residuals) < 2.0e-12


def test_clenshaw_curtis_weights_integrate_polynomials_on_the_slab() -> None:
    degree = 8
    operators = AUDIT.chebyshev_lobatto_operators(degree)
    weights = AUDIT._clenshaw_curtis_weights(degree)
    residuals = []
    for power in range(degree + 1):
        exact = 0.0 if power % 2 else 2.0 / (power + 1)
        residuals.append(
            abs(float(np.sum(weights * operators.nodes**power)) - exact)
        )
    assert np.all(weights > 0.0)
    assert max(residuals) < 2.0e-13


def test_linearized_harmonic_constraint_uses_one_inverse_metric_trace() -> None:
    slab = AUDIT.SLAB
    pi = np.zeros((1, 4, 4))
    pi[0, 0, 0] = 1.0
    state = slab.GHSlabState(
        metric=np.zeros((1, 4, 4)),
        normal_derivative=pi,
        normal_spatial_derivative=np.zeros((1, 4, 4)),
    )
    expected = np.array([[0.5, 0.0, 0.0, 0.0]])
    assert np.allclose(
        slab.linearized_harmonic_constraint(state), expected, atol=1.0e-14, rtol=0.0
    )


def test_projector_target_and_rinne_residual_identities_pass() -> None:
    artifact = _artifact()
    checks = artifact["checks"]
    assert checks["projector_ranks_are_4_2_4"]
    assert checks["projector_algebra_is_orthogonal_and_complete"]
    assert checks["incoming_rhs_matches_all_three_projected_targets"]
    assert checks["rhs_targets_match_rinne_normal_incidence_residuals"]


def test_unclosed_slab_evolution_is_not_promoted() -> None:
    artifact = _artifact()
    assert artifact["status"] == "FAIL_GH_FULL_U1_CHEBYSHEV_SLAB_PILOT"
    assert artifact["major_result"]["closure_level"] == "PARTIAL"
    assert artifact["major_result"]["dependency_unlocked"] == (
        "none; the Core curved-3+1 CPBC parent and Gravity remain blocked"
    )
    assert artifact["checks"]["chebyshev_spectrum_has_no_mode_above_growth_tolerance"]
    assert artifact["checks"]["small_random_perturbation_stays_bounded_over_two_domain_crossing_times"]
    assert not artifact["checks"]["right_going_tt_packet_is_absorbed_without_large_remainder"]
    assert not artifact["checks"]["tt_reduction_constraint_remains_bounded"]
    assert artifact["checks"]["constraint_compatible_lift_preserves_reduction_and_incoming_targets"]
    assert not artifact["checks"]["constraint_compatible_lift_has_no_resolved_growing_mode"]
    assert not artifact["checks"]["constraint_compatible_lift_noise_stays_bounded"]
    assert artifact["reduced_wave_comparator"]["status"] == (
        "PARTIAL_REDUCED_WAVE_BOUNDARY_COMPARATOR"
    )
    assert artifact["checks"]["reduced_wave_has_no_resolved_growing_mode"]
    assert artifact["checks"]["reduced_wave_random_perturbation_stays_bounded"]
    assert artifact["checks"]["reduced_wave_reduction_constraint_is_algebraic"]
    assert artifact["checks"]["clenshaw_curtis_energy_weights_integrate_constant"]
    assert not artifact["checks"]["reduced_wave_tt_packet_is_absorbed"]
    resolution_screens = artifact["metrics"]["reduced_wave_resolution_screens"]
    assert [item["degree"] for item in resolution_screens] == [8, 12, 14, 16, 18, 20]
    assert resolution_screens[1]["tt_packet_clenshaw_curtis_energy_ratio"] > 5.0e-2
    assert resolution_screens[-2]["tt_packet_clenshaw_curtis_energy_ratio"] < 5.0e-2
    assert resolution_screens[-1]["positive_modes_above_1e-6"] == 1


def test_artifact_hashes_match_the_recorded_sources() -> None:
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    for relative_path, expected_hash in artifact["source_hashes"].items():
        import hashlib

        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash
    reduced_artifact = json.loads(REDUCED_ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert reduced_artifact["major_result"]["closure_level"] == "PARTIAL"
    assert reduced_artifact["claim_promotion"] is False
    assert reduced_artifact["controlling_blocker"] == (
        "reduced_wave_packet_absorption_and_high_order_spectrum_not_converged"
    )
    assert len(reduced_artifact["major_result"]["open_blockers"]) >= 4
    for relative_path, expected_hash in reduced_artifact["source_hashes"].items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash


def run_tests() -> None:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
