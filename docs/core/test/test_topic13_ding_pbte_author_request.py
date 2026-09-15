from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
MANIFEST = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_author_request_manifest.json"
)
AUDIT = ROOT / "docs/core/artifacts/t13_ding_pbte_author_request_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_request_package_is_not_mislabeled_as_received_data() -> None:
    manifest = load(MANIFEST)
    assert manifest["status"] == "REQUEST_PACKAGE_READY_NOT_SENT"
    assert manifest["major_result"]["data_role"] == "REQUEST_SPECIFICATION_NOT_SOURCE_DATA"
    assert manifest["holdout_policy"]["xie_2026_accessed"] is False


def test_request_package_covers_the_missing_ding_payload() -> None:
    manifest = load(MANIFEST)
    scope = manifest["request_scope"]
    joined = " ".join(item for values in scope.values() if isinstance(values, list) for item in values).lower()
    for term in ("force constants", "shengbte", "mode-resolved", "c_src(t)", "uncertainty", "checksum"):
        assert term in joined


def test_audit_is_passing_but_keeps_external_response_open() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_REQUEST_SCHEMA_OPEN_EXTERNAL_RESPONSE"
    assert all(audit["checks"].values())
    assert audit["request_state"] == "REQUEST_PACKAGE_READY_NOT_SENT"
    assert audit["controlling_blocker"] == "author_data_or_independent_reproduction_payload_not_received"
