from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
FULL = ROOT / 'docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json'
REGISTER = ROOT / 'docs/core/07_artifacts/gates/uet_major_result_closure_register.json'
DEPENDENCY = ROOT / 'docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json'


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8-sig'))


def test_figure3_binary_identity_is_integrated_without_unlock() -> None:
    result_id = 'T13_BERUT_FIGURE3_REMOTE_BINARY_IDENTITY'
    full = load(FULL)
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    lane = full['verification_status']['source_package']['berut_figure3_remote_binary_identity']
    assert lane['major_result_id'] == result_id
    assert lane['closure_level'] == 'CLOSED_FOR_LANE'
    assert any(item.get('major_result_id') == result_id for item in register['entries'])
    partial = dependency['topic13_partial_evidence']
    assert partial['berut_figure3_remote_binary_identity']['summary']['major_result_id'] == result_id
    assert partial['berut_figure3_remote_binary_identity_full_core_unlock'] is False
    assert dependency['status'] == 'BLOCKED_DOWNSTREAM_MAJOR_RESULTS'
    assert full['claim_promotion'] is False

