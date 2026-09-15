from docs.core.core_paths import repo_root
import json
import subprocess
import sys
from pathlib import Path


ROOT = (repo_root() / "docs")


def test_mass_density_amplitude_audit_is_reproducibly_blocked_only_by_dimensional_map():
    script = ROOT / "scripts/audit/audit_mass_density_amplitude.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT.parent,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "AUGMENTED_AMPLITUDE_EXPLICIT_SOURCE_NOT_DERIVED" in completed.stdout
    artifact = json.loads(
        (ROOT / "core/artifacts/mass_density_amplitude_contract_verification.json").read_text(
            encoding="utf-8"
        )
    )
    assert artifact["audit_status"] == "PASS_WITH_BLOCKED_DIMENSIONAL_MAPPING"
    assert all(artifact["gates"].values())
    assert artifact["source_contract"]["fit_status"] == "NOT_FITTED"
