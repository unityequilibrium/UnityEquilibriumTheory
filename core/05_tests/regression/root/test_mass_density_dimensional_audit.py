import importlib.util
from pathlib import Path

from docs.core.core_paths import repo_root


ROOT = (repo_root() / "docs")


def test_mass_density_dimensional_audit_is_si_1d_only():
    script = ROOT / "scripts/audit/audit_mass_density_dimensional.py"
    spec = importlib.util.spec_from_file_location("mass_density_dimensional_audit", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    artifact = module.build_artifact()
    assert artifact["mapping_status"] == "SI_1D_SYNTHETIC_CONTRACT_ONLY"
    assert artifact["audit_status"] == "PASS_WITH_BLOCKED_3D_PHYSICAL_MAPPING"
    assert all(artifact["gates"].values())
    assert artifact["source_contract"]["observable_unit"] == "kg/m"
