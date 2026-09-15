from __future__ import annotations
from docs.core.core_paths import repo_root

import json
import math
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_gatech_standard_transport_comparator_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_conditional_standard_comparator_passes_and_has_units() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_STANDARD_GRAPHITE_TRANSPORT_COMPARATOR_CONDITIONAL"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    derived = audit["derived_comparator"]
    assert math.isclose(derived["cv_conditional_J_per_m3_K"], 2242474.161628692, rel_tol=1.0e-12)
    assert math.isclose(derived["k_reconstructed_W_per_m_K"], 74.0939625200673, rel_tol=1.0e-12)


def test_density_and_uet_mapping_remain_explicitly_open() -> None:
    audit = load(AUDIT)
    assert audit["uncertainty_contract"]["status"] == "SOURCE_REPORTED_AND_FIRST_ORDER_PROPAGATED_ENVELOPES_SEPARATE"
    assert audit["synthetic_controls"]["phi_response"]["alpha_Phi_K_emitted"] is False
    assert audit["controlling_blocker"] == "standard_comparator_is_not_a_UET_Phi_transport_coefficient_or_Ding_C_src"
