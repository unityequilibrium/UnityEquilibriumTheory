"""Regression tests for the source-locked Oxford TGS numeric-row lane."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = repo_root()
EXTRACT = ROOT / "docs/scripts/audit/extract_topic13_oxford_tgs_numeric_rows.py"
AUDIT = ROOT / "docs/scripts/audit/audit_topic13_oxford_tgs_numeric_rows.py"
ARTIFACT_REL = Path('core/07_artifacts/topic13/t13_oxford_tgs_numeric_rows_audit.json')


def test_oxford_tgs_numeric_rows_are_source_locked_without_promotion(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    env = os.environ.copy()
    env["UET_OUTPUT_ROOT"] = str(output_root)
    extracted = subprocess.run(
        [sys.executable, str(EXTRACT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert extracted.returncode == 0, extracted.stdout + extracted.stderr
    audited = subprocess.run(
        [sys.executable, str(AUDIT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert audited.returncode == 0, audited.stdout + audited.stderr
    artifact = json.loads((output_root / ARTIFACT_REL).read_text(encoding="utf-8"))
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    if artifact["input_mode"] == "METADATA_ONLY_PUBLIC_BOUNDARY":
        assert artifact["status"] == "PASS_OXFORD_TGS_NUMERIC_ROWS_METADATA_BOUNDARY"
        assert artifact["numeric_rows_emitted"] == 0
        assert artifact["raw_payload_available"] is False
        assert artifact["csv_present"] is False
        assert artifact["source"]["raw_mat_hash_is_expected_when_unavailable"] is True
    else:
        assert artifact["status"] == "PASS_OXFORD_TGS_NUMERIC_ROWS_SOURCE_LOCKED_COMPARATOR"
        assert artifact["numeric_rows_emitted"] == 10 * 2002
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["xie_2026_accessed"] is False
    assert artifact["parameter_fitting_performed"] is False
