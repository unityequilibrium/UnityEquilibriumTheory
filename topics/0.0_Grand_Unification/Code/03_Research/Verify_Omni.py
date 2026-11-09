"""
Verify_Omni.py
==============
UET Omni-Engine integration verification.

This script checks whether selected component engines can be orchestrated and whether
their current internal metrics are recorded. It is an integration/run-contract verifier,
not a proof of grand unification.
"""

import json
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path


def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None


ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)

TOPIC_DIR = ROOT / "docs" / "topics" / "0.0_Grand_Unification"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_0_grand_unification_verification.json"
DEPENDENCY_MANIFEST_PATH = TOPIC_DIR / "Data" / "03_Research" / "integration_dependency_manifest.json"

engine_dir = TOPIC_DIR / "Code" / "01_Engine"
if str(engine_dir) not in sys.path:
    sys.path.insert(0, str(engine_dir))

try:
    from Engine_Omni import UETOmniEngine
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import Omni-Engine: {e}")
    sys.exit(1)


def _state_to_record(label, state):
    return {
        "label": label,
        "beta_phase": float(state.beta_phase),
        "status": state.status,
        "metrics": {
            "galaxy_halo_ratio": float(state.galaxy_chi2),
            "weinberg_angle": float(state.weinberg_angle),
            "reynolds_critical": float(state.reynolds_critical),
            "tau_mass_MeV": float(state.tau_mass),
            "entanglement_entropy": float(state.entanglement_entropy),
            "ai_initial_loss": float(state.ai_learning_rate),
            "economic_omega": float(state.economic_omega),
            "atomic_h_alpha_error_percent": float(state.atomic_error),
        },
        "audit_flags": dict(state.audit_flags),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _dependency_inputs():
    inputs = []
    dependencies = []
    if DEPENDENCY_MANIFEST_PATH.exists():
        inputs.append(
            {
                "path": str(DEPENDENCY_MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/"),
                "bytes": DEPENDENCY_MANIFEST_PATH.stat().st_size,
                "sha256": _sha256(DEPENDENCY_MANIFEST_PATH),
                "provenance_role": "integration_dependency_manifest",
            }
        )
        manifest = _read_json(DEPENDENCY_MANIFEST_PATH)
        dependencies = manifest.get("dependencies", [])
    else:
        inputs.append(
            {
                "path": str(DEPENDENCY_MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/"),
                "missing": True,
                "provenance_role": "integration_dependency_manifest",
            }
        )

    records = []
    for dependency in dependencies:
        artifact_path = ROOT / dependency["artifact"]
        record = {
            "topic": dependency.get("topic"),
            "role": dependency.get("role"),
            "metric_bridge": dependency.get("metric_bridge"),
            "artifact": dependency.get("artifact"),
        }
        if artifact_path.exists():
            artifact = _read_json(artifact_path)
            record.update(
                {
                    "status": artifact.get("status", "UNKNOWN"),
                    "claim_class": artifact.get("claim_class"),
                    "schema_version": artifact.get("schema_version"),
                    "timestamp_utc": artifact.get("timestamp_utc"),
                    "sha256": _sha256(artifact_path),
                    "bytes": artifact_path.stat().st_size,
                }
            )
            inputs.append(
                {
                    "path": dependency.get("artifact"),
                    "bytes": artifact_path.stat().st_size,
                    "sha256": record["sha256"],
                    "provenance_role": "subordinate_artifact",
                    "status": record["status"],
                }
            )
        else:
            record.update({"status": "MISSING", "missing": True})
            inputs.append(
                {
                    "path": dependency.get("artifact"),
                    "missing": True,
                    "provenance_role": "subordinate_artifact",
                }
            )
        records.append(record)
    return inputs, records


def write_verification_artifact(result):
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "schema_version": "1.1",
        "topic": "0.0_Grand_Unification",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.0_Grand_Unification/Code/03_Research/Verify_Omni.py",
        "status": result["status"],
        "passed_run_contract": result["status"] in {"PASS", "WARN"},
        "input_hashes": result["input_hashes"],
        "dependency_artifacts": result["dependency_artifacts"],
        "metrics": result["summary_metrics"],
        "thresholds": {
            "run_without_error": True,
            "artifact_written": True,
            "weinberg_angle_abs_error_max": 0.001,
            "tau_mass_abs_error_MeV_max": 1.0,
            "entanglement_entropy_abs_error_max": 0.001,
        },
        "interpretation": (
            "Internal integration/run-contract artifact. This records selected "
            "component-engine outputs and does not prove grand unification or "
            "override subordinate topic limitations. Dependency PASS/WARN/FAIL status is read "
            "from the integration dependency manifest and subordinate artifacts."
        ),
        "results": result,
    }
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"Artifact saved: {ARTIFACT_PATH}")


def run_verification():
    print("UET OMNI-ENGINE: INTEGRATION VERIFICATION")
    print("==========================================")

    omni = UETOmniEngine()

    print("\n[Test 1] Standard integration run (Beta=1.0)...")
    state_std = omni.run_universe(beta=1.0)
    omni.report(state_std)

    has_error = False
    if abs(state_std.weinberg_angle - 0.2312) > 0.001:
        print("Electroweak mismatch")
        has_error = True
    if abs(state_std.tau_mass - 1776.9) > 1.0:
        print("Mass-generation branch mismatch")
        has_error = True
    if abs(state_std.entanglement_entropy - 1.0) > 0.001:
        print("Quantum entropy mismatch")
        has_error = True

    if not has_error:
        print("Integration check: selected beta=1.0 component gates passed.")

    print("\n[Test 2] Low-coupling sensitivity run (Beta=0.1)...")
    state_chaos = omni.run_universe(beta=0.1)
    omni.report(state_chaos)
    print(
        f"  Shift in Re_c: {state_std.reynolds_critical:.1f} -> {state_chaos.reynolds_critical:.1f}"
    )

    input_hashes, dependency_artifacts = _dependency_inputs()
    dependency_statuses = [item.get("status") for item in dependency_artifacts]
    missing_dependencies = [item for item in dependency_artifacts if item.get("missing")]
    dependency_failures = [item for item in dependency_artifacts if item.get("status") == "FAIL"]
    dependency_warnings = [
        item
        for item in dependency_artifacts
        if item.get("status") in {"WARN", "MISSING", "UNKNOWN", None}
    ]

    if dependency_failures or missing_dependencies:
        integration_status = "FAIL"
    elif has_error or dependency_warnings:
        integration_status = "WARN"
    else:
        integration_status = "PASS"

    result = {
        "status": integration_status,
        "input_hashes": input_hashes,
        "dependency_artifacts": dependency_artifacts,
        "component_scope": [
            "0.1_Galaxy_Rotation_Problem",
            "0.6_Electroweak_Physics",
            "0.10_Fluid_Dynamics_Chaos",
            "0.17_Mass_Generation",
            "0.18_Mathnicry",
            "0.20_Atomic_Physics",
            "0.24_Artificial_Intelligence",
            "0.25_Strategy_Power_Economics",
        ],
        "states": [
            _state_to_record("beta_1_0", state_std),
            _state_to_record("beta_0_1", state_chaos),
        ],
        "summary_metrics": {
            "beta_1_0_weinberg_angle": float(state_std.weinberg_angle),
            "beta_1_0_tau_mass_MeV": float(state_std.tau_mass),
            "beta_1_0_entanglement_entropy": float(state_std.entanglement_entropy),
            "reynolds_shift_beta_1_0_to_0_1": float(
                state_chaos.reynolds_critical - state_std.reynolds_critical
            ),
        },
        "dependency_summary": {
            "statuses": dependency_statuses,
            "pass_count": sum(1 for status in dependency_statuses if status == "PASS"),
            "warn_count": sum(1 for status in dependency_statuses if status == "WARN"),
            "fail_count": sum(1 for status in dependency_statuses if status == "FAIL"),
            "missing_count": len(missing_dependencies),
        },
        "inherited_limitations": [
            "Subordinate topic failures or WARN artifacts remain blockers for theory-level claims.",
            "This integration check owns an artifact-dependency manifest, not raw scientific data.",
            "Component outputs may use benchmark-fed or heuristic branches documented in their own topics.",
        ],
    }
    write_verification_artifact(result)
    print("\nFINAL STATUS: OMNI-ENGINE INTEGRATION CHECK COMPLETE")
    return result


if __name__ == "__main__":
    verification_result = run_verification()
    sys.exit(0 if verification_result["status"] in {"PASS", "WARN"} else 1)
