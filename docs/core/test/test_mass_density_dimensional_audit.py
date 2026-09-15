from docs.core.core_paths import repo_root
import json
import subprocess
import sys
from pathlib import Path


ROOT = (repo_root() / "docs")


def test_mass_density_dimensional_audit_is_si_1d_only():
    script = ROOT / "scripts/audit/audit_mass_density_dimensional.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT.parent,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "SI_1D_SYNTHETIC_CONTRACT_ONLY" in completed.stdout
    artifact = json.loads(
        (ROOT / "core/artifacts/mass_density_dimensional_contract_verification.json").read_text(
            encoding="utf-8"
        )
    )
    assert artifact["audit_status"] == "PASS_WITH_BLOCKED_3D_PHYSICAL_MAPPING"
    assert all(artifact["gates"].values())
    assert artifact["source_contract"]["observable_unit"] == "kg/m"
