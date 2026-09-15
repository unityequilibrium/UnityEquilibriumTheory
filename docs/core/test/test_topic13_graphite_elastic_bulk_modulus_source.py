from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/artifacts/t13_graphite_elastic_bulk_modulus_source_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "bosak_2007_graphite_elastic_bulk_source_package.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_graphite_elastic_bulk_source_reconstructs_reported_b_without_calling_it_k_t() -> None:
    lane = load(LANE)
    package = load(PACKAGE)
    reconstruction = lane["reconstruction"]
    assert lane["status"] == "PASS_SCOPED_GRAPHITE_ELASTIC_BULK_COMPARATOR"
    assert lane["major_result"]["major_result_id"] == "T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE"
    assert lane["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["major_result"]["data_role"] == "INTERNAL_SOURCE_COMPARATOR_NOT_DING_TTG_GRADE"
    assert reconstruction["reconstructed_B_elastic_GPa"] == pytest.approx(36.44001810774106)
    assert abs(reconstruction["relative_difference"]) <= 0.01
    assert lane["isothermal_boundary"]["dynamic_elastic_value_is_K_T"] is False
    assert lane["isothermal_boundary"]["K_T_emitted"] is False
    assert lane["numeric_alpha_Phi_K_emitted"] is False
    assert all(lane["checks"].values())
    assert package["source"]["sha256"] == lane["source"]["local_hash_observed"]


import pytest
