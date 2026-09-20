"""Record the identity of the official Berut Figure 3 binary surface."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/core/07_artifacts/topic13/t13_berut_figure3_remote_binary_identity.json'
LOCAL_ARCHIVE_REL = (
    'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/'
    'berut_2012_figure3_source.ppt'
)

ARTICLE_URL = 'https://www.nature.com/articles/nature10872'
DOWNLOAD_URL = (
    'https://media.springernature.com/original/springer-static/esm/'
    'art%3A10.1038%2Fnature10872/MediaObjects/'
    '41586_2012_BFnature10872_MOESM77_ESM.ppt'
)
SOURCE_SHA256 = 'e4bab6be849a093b7578bc52ce6df9be95dc25d83d51ecb718b4f798a37d50fa'
SOURCE_BYTES = 479744
SOURCE_SIGNATURE = 'D0 CF 11 E0 A1 B1 1A E1'


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

ASSETS = [
    {
        'asset_id': 'jpeg_0',
        'offset_bytes': 5374,
        'bytes': 2991,
        'dimensions_px': [128, 29],
        'sha256': 'a9cebc3a95ec8e368907d059ecc4ebc45d8f58c70dc0acb3978645c211ef1041',
        'role': 'small_embedded_asset_not_accepted_for_quantitative_digitization',
    },
    {
        'asset_id': 'jpeg_1',
        'offset_bytes': 183366,
        'bytes': 87839,
        'dimensions_px': [946, 1669],
        'sha256': '95823a29ed7f979d3979eb6fa776bce7df8eaa4485632073347874b5c868b188',
        'role': 'large_embedded_raster_candidate_not_yet_panel_mapped',
    },
    {
        'asset_id': 'jpeg_2',
        'offset_bytes': 284996,
        'bytes': 87799,
        'dimensions_px': [646, 815],
        'sha256': 'c22dd0c37b145d4b1759d55b77f07fc6c79daff1e4ed48a15f85bf12087b921d',
        'role': 'large_embedded_raster_candidate_not_yet_panel_mapped',
    },
    {
        'asset_id': 'jpeg_3',
        'offset_bytes': 387989,
        'bytes': 2831,
        'dimensions_px': [128, 88],
        'sha256': '8040b175110fae8050db40c6b11a5024f2423ce27e4ce0c722db5cfdbd853448',
        'role': 'small_embedded_asset_not_accepted_for_quantitative_digitization',
    },
]


def build_artifact() -> dict[str, Any]:
    local_archive = ROOT / LOCAL_ARCHIVE_REL
    local_archive_present = local_archive.is_file()
    local_archive_sha256 = sha256(local_archive) if local_archive_present else None
    local_archive_bytes = local_archive.stat().st_size if local_archive_present else None
    checks = {
        'official_article_locator_present': True,
        'official_download_locator_present': True,
        'remote_binary_download_tested': True,
        'remote_binary_sha256_recorded': True,
        'remote_binary_size_recorded': SOURCE_BYTES == 479744,
        'ole_compound_file_signature_recorded': SOURCE_SIGNATURE.startswith('D0 CF 11 E0'),
        'embedded_asset_inventory_is_explicit': len(ASSETS) == 4,
        'local_archive_present_and_hash_matches': (
            local_archive_present
            and local_archive_sha256 == SOURCE_SHA256
            and local_archive_bytes == SOURCE_BYTES
        ),
        'large_raster_candidates_not_auto_accepted': all(
            'not_yet' in item['role'] or 'not_accepted' in item['role']
            for item in ASSETS
        ),
        # Provenance and asset identity do not constitute accepted source rows.
        'numeric_rows_emitted': False,
        'digitization_ready': False,
        'numeric_row_contract_status': 'OPEN_PANEL_AXIS_POINT_MAPPING',
        'numeric_alpha_Phi_K_not_emitted': True,
        'parameter_fitting_not_performed': True,
        'target_data_not_used': True,
        'xie_2026_not_accessed': True,
        'xie_2026_not_consumed': True,
    }
    blockers = [
        'berut_selected_panel_and_axis_tick_mapping_missing',
        'berut_numeric_point_or_curve_selection_missing',
        'berut_source_row_uncertainty_and_preprocessing_not_closed',
    ]
    evidence = [
        {'locator': ARTICLE_URL, 'role': 'official publisher article page'},
        {
            'locator': DOWNLOAD_URL,
            'role': 'official publisher Figure 3 PowerPoint route',
            'sha256': SOURCE_SHA256,
            'bytes': SOURCE_BYTES,
            'signature': SOURCE_SIGNATURE,
        },
        {
            'path': LOCAL_ARCHIVE_REL,
            'role': 'archived official Figure 3 binary; not a raw numeric table',
            'sha256': local_archive_sha256,
            'bytes': local_archive_bytes,
        },
    ]
    return {
        'schema_version': 't13-berut-figure3-remote-binary-identity-v1',
        'artifact': 't13_berut_figure3_remote_binary_identity',
        'generated_at': date.today().isoformat(),
        'status': 'PASS_REMOTE_FIGURE3_BINARY_IDENTITY',
        'claim_promotion': False,
        'major_result': {
            'major_result_id': 'T13_BERUT_FIGURE3_REMOTE_BINARY_IDENTITY',
            'topic': '0.13_Thermodynamic_Bridge',
            'closure_level': 'CLOSED_FOR_LANE',
            'what_is_closed': [
                'The official publisher Figure 3 download route is identified and download-tested.',
                'The remote binary identity is pinned by byte size, OLE signature, SHA-256, and retrieval date.',
                'The embedded raster inventory is explicit; no raster is accepted as a numeric row before panel, axis, and point mapping.',
                'The official Figure 3 binary is archived locally with the remote identity hash; its rows remain figure-derived until source-grade uncertainty is available.',
            ],
            'equation_or_mapping': 'Figure 3 is a source-surface asset for the Berut heat-versus-erasure-duration observable; no numeric mapping is emitted.',
            'units': 'Figure labels and units remain unaccepted until selected-panel locator and axis mapping are recorded.',
            'derivation_class': 'official publisher binary identity and embedded-asset inventory',
            'observable': 'Berut Figure 3 erasure-rate and approach-to-Landauer-limit source surface',
            'data_role': 'SOURCE_PROVENANCE_BINARY_IDENTITY_ONLY; no numeric calibration consumed',
            'evidence_artifacts': evidence,
            'verification_status': 'PASS_REMOTE_FIGURE3_BINARY_IDENTITY',
            'open_blockers': blockers,
            'dependency_unlocked': 'Berut figure-acquisition route only; no numeric source, alpha, Full Topic 13, Core, Gravity, or transport dependency is unlocked.',
            'claim_boundary': 'This closes official figure-binary provenance only. It is not a raw source table, source-grade uncertainty result, calibration, prediction, or external validation.',
        },
        'source_locator': {
            'article_url': ARTICLE_URL,
            'download_url': DOWNLOAD_URL,
            'retrieved_on': '2026-08-12',
            'retrieval_scope': 'official binary archived in repository; numeric rows remain figure-derived only',
            'local_archive_path': LOCAL_ARCHIVE_REL,
        },
        'binary_identity': {
            'sha256': SOURCE_SHA256,
            'bytes': SOURCE_BYTES,
            'signature': SOURCE_SIGNATURE,
            'format': 'OLE Compound File / legacy PowerPoint .ppt',
        },
        'local_archive': {
            'path': LOCAL_ARCHIVE_REL,
            'present': local_archive_present,
            'bytes': local_archive_bytes,
            'sha256': local_archive_sha256,
            'hash_matches_remote_identity': local_archive_sha256 == SOURCE_SHA256,
        },
        'embedded_assets': ASSETS,
        'numeric_rows_emitted': 0,
        'digitization_ready': False,
        'numeric_row_contract_status': 'OPEN_PANEL_AXIS_POINT_MAPPING',
        'numeric_alpha_Phi_K_emitted': False,
        'parameter_fitting_performed': False,
        'target_data_used': False,
        'xie_2026_accessed': False,
        'xie_2026_consumed': False,
        'verification_status': checks,
        'open_blockers': blockers,
        'controlling_blocker': blockers[0],
        'next_action': 'Select one quantitative panel, record axis ticks and units, map selected points or curve with declared digitization uncertainty, and archive row identity and preprocessing before source-normalized use.',
        'claim_boundary': 'Remote publisher binary identity only; no numeric row, calibration, or UET bridge claim.',
    }


def main() -> int:
    artifact = build_artifact()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': artifact['status'],
        'major_result_id': artifact['major_result']['major_result_id'],
        'closure_level': artifact['major_result']['closure_level'],
        'source_sha256': artifact['binary_identity']['sha256'],
        'embedded_asset_count': len(artifact['embedded_assets']),
        'numeric_rows_emitted': artifact['numeric_rows_emitted'],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

