"""Verify the bounded He-II operator-domain decision and evidence identity."""

import hashlib
import importlib.util
import json
from pathlib import Path


SOURCE = Path(__file__).with_name("Research_T13_Funding_HeII_Operator_Domain.py")
SPEC = importlib.util.spec_from_file_location("t13_funding_heii_operator_domain", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
AUDIT = MODULE.audit()


def test_frozen_bundle_has_no_admitted_heii_second_sound_domain():
    assert all(AUDIT["checks"].values())
    assert AUDIT["frozen_branch"]["q_recomputed"] < 0
    assert AUDIT["frozen_branch"]["heii_anchor_superfluid_fraction"] > 0
    assert AUDIT["g1_physical_protocol_status"].startswith("BLOCKED")
    assert AUDIT["g2_scientific_disposition"].startswith("UNRESOLVED")
    assert AUDIT["dependency_unlocked"] == []
    assert AUDIT["full_core_unlock"] is False
    assert AUDIT["xie_2026_accessed"] is False


def test_scoped_decision_is_reproducible_from_hashed_inputs():
    assert AUDIT == json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
    assert AUDIT["closure_level"] == "CLOSED_FOR_LANE"
    assert AUDIT["verification_status"] == "PASS_SCOPED_OPERATOR_DOMAIN_BOUNDARY"
    for item in AUDIT["evidence_artifacts"]:
        source = MODULE.ROOT / item["path"]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item["sha256"]
