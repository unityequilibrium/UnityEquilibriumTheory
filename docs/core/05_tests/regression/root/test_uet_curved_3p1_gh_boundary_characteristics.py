from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from docs.core.core_paths import repo_root
from docs.core.uet_curved_3p1_generalized_harmonic import GHParameters
from docs.scripts.audit.audit_curved_3p1_gh_boundary_characteristics import (
    AUDIT_SOURCE,
    GH_SOURCE,
    build_artifact,
    classify_boundary_modes,
)


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_boundary_characteristic_audit.json"


def _parameters(normal, ratio: float) -> GHParameters:
    direction = np.asarray(normal, dtype=float)
    direction /= np.linalg.norm(direction)
    tangent = np.cross(direction, np.array([0.0, 0.0, 1.0]))
    if np.linalg.norm(tangent) < 0.1:
        tangent = np.cross(direction, np.array([1.0, 0.0, 0.0]))
    tangent /= np.linalg.norm(tangent)
    lapse = 0.8
    shift = ratio * lapse * direction + 0.25 * tangent
    return GHParameters(
        lapse=lapse,
        shift=tuple(float(value) for value in shift),
        gamma2=0.6,
        symmetrizer_lambda=1.0,
    )


@pytest.mark.parametrize(
    ("ratio", "incoming", "outgoing", "glancing"),
    [
        (-0.5, ("u1_minus",), ("u1_plus", "u2_tangent_1", "u2_tangent_2"), ("u0",)),
        (0.0, ("u1_minus",), ("u1_plus",), ("u0", "u2_tangent_1", "u2_tangent_2")),
        (0.5, ("u1_minus", "u2_tangent_1", "u2_tangent_2"), ("u1_plus",), ("u0",)),
        (-1.0, (), ("u1_plus", "u2_tangent_1", "u2_tangent_2"), ("u0", "u1_minus")),
        (1.0, ("u1_minus", "u2_tangent_1", "u2_tangent_2"), (), ("u0", "u1_plus")),
    ],
)
def test_incidence_partition_tracks_normal_shift_and_sonic_edges(
    ratio, incoming, outgoing, glancing
) -> None:
    direction = np.array([1.0, 2.0, 2.0]) / 3.0
    result = classify_boundary_modes(direction, _parameters(direction, ratio))
    assert result["incoming_modes"] == incoming
    assert result["outgoing_modes"] == outgoing
    assert result["glancing_modes"] == glancing
    if abs(ratio) >= 1.0:
        assert result["reference_shift_domain"] == "OUTSIDE_SUBLUMINAL_SHIFT_ASSUMPTIONS"
    else:
        assert result["reference_shift_domain"] == "SUBLUMINAL_SHIFT"


@pytest.mark.parametrize("tolerance", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_speed_tolerance_is_rejected(tolerance) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        classify_boundary_modes((1.0, 0.0, 0.0), GHParameters(), speed_tolerance=tolerance)


def test_full_audit_build_is_bounded_and_source_hashed() -> None:
    artifact = build_artifact()
    assert artifact["status"] == "PASS_GH_BOUNDARY_CHARACTERISTIC_CLASSIFICATION"
    assert artifact["case_count"] == 28
    assert artifact["subluminal_flux_case_count"] == 12
    assert artifact["scope"]["boundary_operator_applied"] is False
    assert artifact["scope"]["xie_2026_accessed"] is False
    assert artifact["scope"]["excluded_variables"] == ["UET C", "UET Phi", "R_gen", "R_obs"]
    for source in (GH_SOURCE, AUDIT_SOURCE):
        digest = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
        assert artifact["source_hashes"][source] == digest


def test_generated_artifact_matches_current_audit_inputs_and_stays_lane_only() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["major_result"]["dependency_unlocked"].startswith("boundary design preflight only")
    assert artifact["claim_promotion"] is False
    for source, digest in artifact["source_hashes"].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == digest
