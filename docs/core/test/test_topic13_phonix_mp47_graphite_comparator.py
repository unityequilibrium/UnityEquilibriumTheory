from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_phonix_mp47_graphite_comparator_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "phonix_mp47_graphite_source_package.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_phonix_mp47_comparator_is_source_locked_without_cv_promotion() -> None:
    artifact = load(AUDIT)
    assert artifact["status"] == "PASS_SCOPED_PHONIX_GRAPHITE_HARMONIC_COMPARATOR"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert artifact["source"]["row_locator"]["mp_id"] == "mp-47"
    assert artifact["source"]["space_group_number"] == 194
    assert artifact["numeric_c_v_emitted"] is False
    assert artifact["numeric_C_src_emitted"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False


def test_phonix_package_keeps_arbitrary_dos_and_ding_boundary() -> None:
    package = load(PACKAGE)
    assert package["data_role"] == "TRAINING/COMPARISON"
    assert package["uncertainty"]["standard_uncertainty_available"] is False
    assert package["material"]["Ding_TTG_material_equivalence"] == "NOT_ESTABLISHED"
    assert package["holdout_policy"]["xie_2026_accessed"] is False
    assert "arbitrary-unit DOS" in package["fields"]["phdos[a.u.]" ]
