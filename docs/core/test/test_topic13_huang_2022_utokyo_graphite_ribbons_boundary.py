from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PDF = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/huang_2022_utokyo_graphite_ribbons_thesis.pdf"
PACKAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/huang_2022_utokyo_graphite_ribbons_source_package.json"
AUDIT = ROOT / "docs/core/artifacts/t13_huang_2022_utokyo_graphite_ribbons_boundary_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_utokyo_source_identity_is_locked() -> None:
    package = load(PACKAGE)
    assert PDF.is_file()
    assert PDF.stat().st_size == 25_529_971
    assert hashlib.sha256(PDF.read_bytes()).hexdigest() == (
        "812ca326070b8036179a0f5fd40addacb88c9bfdf73c2f4c16f0873175a04e6a"
    )
    assert package["source"]["reviewed_page_count"] == 110
    assert package["source"]["doi"] == "https://doi.org/10.15083/0002011088"


def test_utokyo_route_is_comparator_boundary_not_csrc_or_alpha() -> None:
    package = load(PACKAGE)
    audit = load(AUDIT)
    assert package["status"] == "PASS_HUANG_2022_UTOKYO_GRAPHITE_RIBBONS_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    capabilities = audit["review_boundary"]["payload_capabilities"]
    assert capabilities["has_mode_resolved_csrc_rows"] is False
    assert capabilities["has_base_phi_amplitude"] is False
    assert capabilities["has_alpha_phi_k_record"] is False
    assert audit["review_boundary"]["material_state"]["Ding_TTG_material_equivalence"] is False
    assert audit["checks"]["no_holdout_access"] is True
    assert audit["claim_promotion"] is False
