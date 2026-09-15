"""Repair idempotent routing and test paths for the Berut source wave."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FULL_GATE = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
WAVE_RUNNER = ROOT / "docs/scripts/audit/run_topic13_berut_source_package_wave.py"
SOURCE_TEST = ROOT / "docs/core/test/test_topic13_berut_source_package_availability.py"
INTEGRATION_TEST = ROOT / "docs/core/test/test_topic13_berut_source_package_availability_integration.py"


def repair_full_gate() -> bool:
    text = FULL_GATE.read_text(encoding="utf-8-sig")
    marker = "Keep source-acquisition evidence in the source-package lane."
    if marker in text:
        return False
    anchor = '    artifact["verification_status"]["eos_transport_kms_entropy"].update(discovered_lane_integrations)\n'
    addition = '''    # Keep source-acquisition evidence in the source-package lane.
    # The discovery sweep is broad, but a source row must not be classified as
    # an EOS/transport result merely because it carries a major-result record.
    berut_source_lane = discovered_lane_integrations.get(
        "berut_source_package_availability_boundary"
    )
    if berut_source_lane:
        artifact["verification_status"]["source_package"][
            "berut_source_package_availability_boundary"
        ] = berut_source_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "berut_source_package_availability_boundary", None
        )
'''
    if anchor not in text:
        raise SystemExit("full gate routing anchor not found")
    FULL_GATE.write_text(text.replace(anchor, anchor + addition, 1), encoding="utf-8")
    return True


def repair_test_paths() -> bool:
    changed = False
    source_text = SOURCE_TEST.read_text(encoding="utf-8-sig")
    source_old = 'ROOT = Path(__file__).resolve().parents[2]\nAUDIT = ROOT / "artifacts/t13_berut_source_package_availability_boundary.json"'
    source_new = 'ROOT = Path(__file__).resolve().parents[3]\nAUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_berut_source_package_availability_boundary.json"'
    if source_old in source_text:
        SOURCE_TEST.write_text(source_text.replace(source_old, source_new, 1), encoding="utf-8")
        changed = True

    integration_text = INTEGRATION_TEST.read_text(encoding="utf-8-sig")
    integration_old = '''ROOT = Path(__file__).resolve().parents[2]
FULL = ROOT / "../topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "artifacts/uet_major_result_dependency_unlock_gate.json"'''
    integration_new = '''ROOT = Path(__file__).resolve().parents[3]
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"'''
    if integration_old in integration_text:
        INTEGRATION_TEST.write_text(integration_text.replace(integration_old, integration_new, 1), encoding="utf-8")
        changed = True
    return changed


def repair_runner_order() -> bool:
    text = WAVE_RUNNER.read_text(encoding="utf-8-sig")
    if "repair_topic13_berut_source_boundary_integration.py" in text:
        return False
    anchor = '        "repair_topic13_berut_source_lane_key.py",\n'
    addition = anchor + '        "repair_topic13_berut_source_boundary_integration.py",\n'
    if anchor not in text:
        raise SystemExit("Berut runner anchor not found")
    WAVE_RUNNER.write_text(text.replace(anchor, addition, 1), encoding="utf-8")
    return True


def main() -> int:
    changed = {
        "full_gate": repair_full_gate(),
        "test_paths": repair_test_paths(),
        "runner_order": repair_runner_order(),
    }
    print({"status": "PASS_BERUT_SOURCE_BOUNDARY_REPAIR", "changed": changed})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

