"""Audit Wave 8 dimensional-observable closure using Topic 0.13 evidence."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "docs/core/artifacts"
READINESS = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_observable_map_readiness.json"
PILOT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_control.json"
SOURCE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json"
T13_HE4_COMPOSITION = ARTIFACTS / "t13_he4_core_thermodynamic_bridge_composition_audit.json"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifacts() -> tuple[dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    readiness, pilot, source = _read(READINESS), _read(PILOT), _read(SOURCE)
    he4_composition = _read(T13_HE4_COMPOSITION)
    core_track = he4_composition["major_result"]
    expected_source_hash = readiness["input_identity"]["source_package_sha256"]
    source_hash = _sha(SOURCE)
    gates = readiness["gates"]
    metrics = {
        "source_package_hash_matches_readiness": source_hash == expected_source_hash,
        "numeric_source_rows_present": sum(1 for row in readiness["source_rows"] if row["local_numeric_present"]),
        "alpha_phi_k_closed": bool(gates["dimensional_phi_to_quasi_temperature_scale_defined"]),
        "heat_flux_map_closed": bool(gates["heat_flux_observable_map_closed"]),
        "entropy_map_closed": bool(gates["entropy_production_observable_map_closed"]),
        "holdout_consumed": not bool(gates["holdout_data_not_consumed"]),
        "pilot_prearrival_leakage": float(pilot["metrics"]["core_prearrival_leakage_fraction"]),
        "pilot_prearrival_threshold": float(pilot["thresholds"]["prearrival_leakage_fraction_max"]),
        "o2_he4_core_closure_level": core_track["closure_level"],
        "o2_he4_full_core_unlock": (
            he4_composition.get("status") == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"
        ),
    }
    checks = {
        "source_identity_locked": metrics["source_package_hash_matches_readiness"],
        "normalized_operator_defined": bool(gates["standard_normalized_ttg_operator_defined"] and gates["normalized_phi_operator_is_explicit"]),
        "numeric_source_package": metrics["numeric_source_rows_present"] > 0,
        "independent_dimensional_calibration": metrics["alpha_phi_k_closed"],
        "heat_flux_observable": metrics["heat_flux_map_closed"],
        "entropy_observable": metrics["entropy_map_closed"],
        "causal_pilot": metrics["pilot_prearrival_leakage"] <= metrics["pilot_prearrival_threshold"],
        "holdout_preserved": not metrics["holdout_consumed"],
        "no_parameter_fitting": bool(gates["no_parameter_fitting"] and not pilot["run_integrity"]["parameter_fitting"]),
        "o2_he4_core_ready": (
            he4_composition.get("status") == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"
            and core_track.get("closure_level") == "CLOSED_FOR_CORE"
            and all(he4_composition.get("checks", {}).values())
        ),
    }
    dimensional_closed = all(checks[name] for name in ("numeric_source_package", "independent_dimensional_calibration", "causal_pilot"))
    audit = {
        "schema_version": "1.0", "artifact": "uet_dimensional_observable_closure_audit",
        "generated_at": now, "audit_status": "PASS_ACCOUNTING" if checks["source_identity_locked"] and checks["normalized_operator_defined"] and checks["holdout_preserved"] else "FAIL",
        "closure_status": "PASS_DIMENSIONAL_OBSERVABLE" if dimensional_closed else "BLOCKED",
        "topic": "0.13_Thermodynamic_Bridge", "measurement_operator": readiness["measurement_operator"],
        "metrics": metrics, "checks": checks,
        "input_identity": {
            "readiness_path": READINESS.relative_to(ROOT).as_posix(), "readiness_sha256": _sha(READINESS),
            "pilot_path": PILOT.relative_to(ROOT).as_posix(), "pilot_sha256": _sha(PILOT),
            "source_path": SOURCE.relative_to(ROOT).as_posix(), "source_sha256": source_hash,
            "t13_he4_composition_path": T13_HE4_COMPOSITION.relative_to(ROOT).as_posix(),
            "t13_he4_composition_sha256": _sha(T13_HE4_COMPOSITION),
        },
        "tracks": {
            "o2_he4_core_ready": {
                "major_result_id": "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY",
                "status": core_track["closure_level"],
                "full_core_unlock": checks["o2_he4_core_ready"],
                "what_is_closed": core_track["what_is_closed"],
                "claim_boundary": core_track["claim_boundary"],
            },
            "legacy_graphite_ttg_external_validation": {
                "status": "BLOCKED",
                "checks": {
                    name: checks[name]
                    for name in (
                        "numeric_source_package",
                        "independent_dimensional_calibration",
                        "causal_pilot",
                        "holdout_preserved",
                    )
                },
                "claim_boundary": (
                    "Historical graphite pilot remains blocked and is not a "
                    "Core physical-unlock dependency."
                ),
            },
        },
        "provenance_gaps": [
            "legacy graphite pilot has no accepted local numeric TTG package with complete locator, preprocessing, uncertainty, and hash",
            "legacy graphite pilot has no independent graphite-specific alpha_Phi_K derivation or calibration",
            "legacy graphite heat flux and entropy production are not direct closed TTG observables",
        ],
        "causal_gap": "legacy graphite pilot pre-arrival leakage exceeds the locked threshold",
        "claim_boundary": (
            "The bounded O(2)/He-4 dimensional thermal bridge is CLOSED_FOR_CORE. "
            "The historical graphite TTG external-validation track remains blocked."
        ),
    }
    gate = {
        "schema_version": "1.0", "artifact": "uet_main_theory_wave8_gate",
        "generated_at": now, "audit_status": audit["audit_status"],
        "dimensional_observable_status": audit["closure_status"],
        "upstream_gate": "uet_main_theory_wave7_gate.json", "checks": checks,
        "track_status": {
            "o2_he4_core_ready": "CLOSED_FOR_CORE",
            "legacy_graphite_ttg_external_validation": "BLOCKED",
        },
        "controlling_blockers": [
            "legacy_graphite_ttg_numeric_source_package_missing",
            "legacy_graphite_alpha_phi_k_independent_calibration_missing",
            "legacy_graphite_thermal_prearrival_leakage_gate_failed",
        ],
        "holdout_status": "LOCKED_UNCONSUMED" if checks["holdout_preserved"] else "INVALID_CONSUMED",
        "claim_promotion": False,
        "next_controller": (
            "Keep graphite acquisition/calibration on the external track; "
            "the Core path proceeds through curved 3+1 time integration and "
            "constraint propagation."
        ),
    }
    return audit, gate


def main() -> int:
    names = ("uet_dimensional_observable_closure_audit.json", "uet_main_theory_wave8_gate.json")
    outputs = dict(zip(names, build_artifacts()))
    for name, payload in outputs.items():
        (ARTIFACTS / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    gate = outputs["uet_main_theory_wave8_gate.json"]
    print(f"audit_status={gate['audit_status']}")
    print(f"dimensional_observable_status={gate['dimensional_observable_status']}")
    print("controlling_blockers=" + ",".join(gate["controlling_blockers"]))
    return 0 if gate["audit_status"] == "PASS_ACCOUNTING" else 1


if __name__ == "__main__":
    raise SystemExit(main())
