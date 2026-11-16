import importlib.util
from pathlib import Path

from docs.core.core_paths import repo_root


ROOT = (repo_root() / "docs")


def test_mass_density_amplitude_audit_is_reproducibly_blocked_only_by_dimensional_map():
    script = ROOT / "scripts/audit/audit_mass_density_amplitude.py"
    spec = importlib.util.spec_from_file_location("mass_density_amplitude_audit", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    artifact = module.build_artifact()
    assert artifact["mapping_status"] == "AUGMENTED_AMPLITUDE_EXPLICIT_SOURCE_NOT_DERIVED"
    assert artifact["audit_status"] == "PASS_WITH_BLOCKED_DIMENSIONAL_MAPPING"
    assert all(artifact["gates"].values())
    assert artifact["source_contract"]["fit_status"] == "NOT_FITTED"
