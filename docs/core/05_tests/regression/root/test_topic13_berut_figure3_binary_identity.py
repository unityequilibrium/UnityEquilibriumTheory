from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / 'docs/core/artifacts/t13_berut_figure3_remote_binary_identity.json'


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding='utf-8-sig'))


def test_remote_binary_identity_is_closed_for_lane_only() -> None:
    artifact = load()
    assert artifact['status'] == 'PASS_REMOTE_FIGURE3_BINARY_IDENTITY'
    assert artifact['major_result']['closure_level'] == 'CLOSED_FOR_LANE'
    checks = artifact['verification_status']
    positive = [
        value
        for key, value in checks.items()
        if key not in {
            'xie_2026_not_accessed',
            'xie_2026_not_consumed',
            'numeric_rows_emitted',
            'digitization_ready',
        }
    ]
    assert all(positive)
    assert checks['xie_2026_not_accessed'] is True
    assert checks['xie_2026_not_consumed'] is True
    assert checks['numeric_rows_emitted'] is False
    assert checks['digitization_ready'] is False


def test_remote_binary_identity_emits_no_numeric_claim() -> None:
    artifact = load()
    assert artifact['binary_identity']['sha256'] == 'e4bab6be849a093b7578bc52ce6df9be95dc25d83d51ecb718b4f798a37d50fa'
    assert artifact['binary_identity']['bytes'] == 479744
    assert len(artifact['embedded_assets']) == 4
    assert artifact['numeric_rows_emitted'] == 0
    assert artifact['digitization_ready'] is False
    assert artifact['numeric_row_contract_status'] == 'OPEN_PANEL_AXIS_POINT_MAPPING'
    assert artifact['numeric_alpha_Phi_K_emitted'] is False
    assert artifact['parameter_fitting_performed'] is False
    assert artifact['target_data_used'] is False

