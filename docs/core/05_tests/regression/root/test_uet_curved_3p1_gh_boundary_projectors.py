from __future__ import annotations

import hashlib
import importlib
import json
from itertools import product

import numpy as np
import pytest

from docs.core.core_paths import repo_root


ROOT = repo_root()
PROJECTORS = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gh_boundary_projectors"
)
AUDIT = importlib.import_module(
    "docs.scripts.audit.audit_uet_curved_3p1_gh_boundary_projectors"
)
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_boundary_projector_audit.json"
)


def _directions():
    for value in product((-1.0, 0.0, 1.0), repeat=3):
        if value != (0.0, 0.0, 0.0):
            vector = np.asarray(value, dtype=float)
            yield vector / np.linalg.norm(vector)


def test_published_projector_decomposition_has_4_2_4_ranks_for_all_face_normals() -> None:
    for normal in _directions():
        projectors = PROJECTORS.build_gh_boundary_projectors(normal)
        assert projectors.ranks == {"constraint": 4, "physical": 2, "gauge": 4}
        assert max(projectors.residuals.values()) < 1.0e-12


def test_projected_random_symmetric_tensor_reconstructs_and_physical_piece_is_transverse() -> None:
    projectors = PROJECTORS.build_gh_boundary_projectors((1.0, 2.0, -1.0))
    raw = np.arange(16, dtype=float).reshape(4, 4)
    tensor = 0.5 * (raw + raw.T)
    constraint = PROJECTORS.apply_gh_boundary_projector(tensor, projectors.constraint)
    physical = PROJECTORS.apply_gh_boundary_projector(tensor, projectors.physical)
    gauge = PROJECTORS.apply_gh_boundary_projector(tensor, projectors.gauge)
    assert np.allclose(tensor, constraint + physical + gauge, atol=1.0e-12, rtol=0.0)
    n_up = np.concatenate(([0.0], np.asarray(projectors.normal)))
    assert np.max(np.abs(projectors.timelike_normal @ physical)) < 1.0e-12
    assert np.max(np.abs(n_up @ physical)) < 1.0e-12
    assert abs(np.einsum("ab,ab->", projectors.spatial_projector_contravariant, physical)) < 1.0e-12


def test_tensor_and_projector_validation_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="nonzero"):
        PROJECTORS.build_gh_boundary_projectors((0.0, 0.0, 0.0))
    with pytest.raises(ValueError, match="symmetric"):
        PROJECTORS.apply_gh_boundary_projector(np.triu(np.ones((4, 4))), np.eye(10))
    with pytest.raises(ValueError, match="shape"):
        PROJECTORS.apply_gh_boundary_projector(np.eye(4), np.eye(9))


def test_generated_projector_audit_hashes_current_sources_and_stays_preflight_only() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    rebuilt = AUDIT.build_artifact()
    assert artifact["status"] == "PASS_GH_BOUNDARY_PROJECTOR_DECOMPOSITION"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["scope"]["boundary_operator_applied"] is False
    assert artifact["scope"]["periodic_solver_modified"] is False
    assert artifact["claim_promotion"] is False
    for source, digest in artifact["source_hashes"].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == digest
        assert rebuilt["source_hashes"][source] == digest
