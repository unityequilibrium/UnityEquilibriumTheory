"""Regression tests for the Oxford TGS provenance-only lane."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
import subprocess
import sys
from pathlib import Path


ROOT = repo_root()
SCRIPT = ROOT / "docs/scripts/audit/audit_topic13_oxford_tgs_comparator_provenance.py"
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_oxford_tgs_comparator_provenance_audit.json"


def test_oxford_tgs_provenance_audit_passes_without_numeric_rows() -> None:
    completed = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["status"] == "PASS_OXFORD_TGS_PROVENANCE_ARCHIVE_LOCKED_EXTRACTION_PENDING"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["numeric_rows_emitted"] == 0
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["xie_2026_accessed"] is False

