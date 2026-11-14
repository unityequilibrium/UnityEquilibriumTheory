"""Regression test for the source-locked Ceylon graphite Cp comparator."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/scripts/audit/audit_topic13_desorbo_ceylon_graphite_cp.py"
ARTIFACT_REL = Path('core/07_artifacts/topic13/t13_desorbo_ceylon_graphite_cp_audit.json')


def test_desorbo_ceylon_graphite_cp_is_source_locked_without_promotion(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    env = os.environ.copy()
    env["UET_OUTPUT_ROOT"] = str(output_root)
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
    assert artifact["status"] in {
        "PASS_DESORBO_CEYLON_GRAPHITE_CP_SOURCE_LOCKED_COMPARATOR",
        "PASS_METADATA_ONLY_DESORBO_CEYLON_GRAPHITE_CP_SOURCE_BOUNDARY",
    }
    assert artifact["input_mode"] in {"RAW_SOURCE_VERIFIED", "METADATA_ONLY_PUBLIC_BOUNDARY"}
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["source_row"]["value_J_per_mol_K"] == 7.841
    assert artifact["volumetric_cv_emitted"] is False
    assert artifact["xie_2026_accessed"] is False
    assert artifact["parameter_fitting_performed"] is False
