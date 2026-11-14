"""Expanded electroweak benchmark for topic 0.6 with explicit provenance separation."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np


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


from docs import ROOT_PATH
from docs.core.reproducibility import generate_artifact, hash_dataset, hash_file, save_artifact


root_path = ROOT_PATH
topic_path = root_path / "docs" / "topics" / "0.6_Electroweak_Physics"
benchmark_package_json = root_path / "docs" / "data" / "external" / "particle_physics" / "pdg" / "electroweak_benchmark_package.json"
source_lock_json = topic_path / "Data" / "03_Research" / "source_lock_manifest.json"
engine_path = topic_path / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from Engine_Electroweak import M_Z_GEV, UETElectroweakSolver


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def path_hash_record(path_string: str) -> dict:
    path = root_path / path_string
    return {
        "path": path_string,
        "sha256": hash_file(path) if path.exists() and path.is_file() else None,
        "status": "present" if path.exists() else "missing",
    }


def relative_error_percent(predicted: float, observed: float) -> float:
    return abs(predicted - observed) / abs(observed) * 100.0


def running_angle_prediction(q_gev: float) -> float:
    sin2_z = 0.23121
    slope = 0.0075
    if q_gev < 1e-4:
        q_gev = 1e-4
    return sin2_z * (1 + slope * math.log(M_Z_GEV / q_gev))


def to_builtin(value):
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, dict):
        return {k: to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_builtin(v) for v in value]
    return value


def main() -> int:
    benchmark = load_json(benchmark_package_json)
    source_lock = load_json(source_lock_json) if source_lock_json.exists() else {"external_source_records": [], "derived_inputs": []}
    solver = UETElectroweakSolver()
    result = solver.solve()
    core = benchmark["core_observables"]
    neutron = benchmark["neutron_decay_benchmark"]
    running_points = benchmark["running_angle_diagnostic"]["points"]

    core_comparisons = {
        "sin2_theta_W": {
            "predicted": result.sin2_theta_W,
            "observed": core["sin2_theta_W_effective"]["value"],
            "relative_error_percent": relative_error_percent(result.sin2_theta_W, core["sin2_theta_W_effective"]["value"]),
        },
        "m_W_GeV": {
            "predicted": result.m_W_predicted,
            "observed": core["m_W"]["value"],
            "relative_error_percent": relative_error_percent(result.m_W_predicted, core["m_W"]["value"]),
        },
        "m_H_GeV": {
            "predicted": result.m_Higgs_predicted,
            "observed": core["m_H"]["value"],
            "relative_error_percent": relative_error_percent(result.m_Higgs_predicted, core["m_H"]["value"]),
        },
        "G_F_GeV_minus_2": {
            "predicted": result.fermi_constant,
            "observed": core["fermi_constant"]["value"],
            "relative_error_percent": relative_error_percent(result.fermi_constant, core["fermi_constant"]["value"]),
        },
        "neutron_lifetime_s": {
            "predicted": result.neutron_lifetime,
            "observed": neutron["best_lifetime_s"],
            "relative_error_percent": relative_error_percent(result.neutron_lifetime, neutron["best_lifetime_s"]),
        },
    }

    running_diagnostic = []
    for point in running_points:
        pred = running_angle_prediction(point["Q_GeV"])
        running_diagnostic.append(
            {
                "label": point["label"],
                "Q_GeV": point["Q_GeV"],
                "observed": point["sin2_theta_W"],
                "predicted": pred,
                "relative_error_percent": relative_error_percent(pred, point["sin2_theta_W"]),
                "provenance_status": point["provenance_status"],
            }
        )

    running_average_error = sum(item["relative_error_percent"] for item in running_diagnostic) / len(running_diagnostic)

    gates = {
        "sin2_theta_W": core_comparisons["sin2_theta_W"]["relative_error_percent"] < 2.0,
        "m_W_GeV": core_comparisons["m_W_GeV"]["relative_error_percent"] < 2.0,
        "m_H_GeV": core_comparisons["m_H_GeV"]["relative_error_percent"] < 2.0,
        "G_F_GeV_minus_2": core_comparisons["G_F_GeV_minus_2"]["relative_error_percent"] < 0.5,
        "neutron_lifetime_s": core_comparisons["neutron_lifetime_s"]["relative_error_percent"] < 2.0,
    }
    passed = all(gates.values())

    artifact = generate_artifact(
        topic="0.6_Electroweak_Physics",
        dataset_hash=hash_dataset(
            {
                "benchmark_package": str(benchmark_package_json.relative_to(root_path)),
                "sin2_theta_W": core["sin2_theta_W_effective"]["value"],
                "m_W": core["m_W"]["value"],
                "m_H": core["m_H"]["value"],
                "G_F": core["fermi_constant"]["value"],
                "neutron_lifetime_s": neutron["best_lifetime_s"],
            }
        ),
        results=to_builtin(
            {
                "status": "PASS" if passed else "FAIL",
                "core_comparisons": core_comparisons,
                "core_gates": gates,
                "running_angle_diagnostic": running_diagnostic,
                "running_angle_diagnostic_status": benchmark["running_angle_diagnostic"]["status"],
                "running_angle_average_error_percent": running_average_error,
            }
        ),
        config={
            "benchmark_package": str(benchmark_package_json.relative_to(root_path)),
            "source_lock_manifest": str(source_lock_json.relative_to(root_path)),
            "engine_path": str((topic_path / "Code" / "01_Engine" / "Engine_Electroweak.py").relative_to(root_path)),
            "interpretation": "Only the core observables plus neutron lifetime act as benchmark gates; running-angle points remain diagnostic-only because they are compiled local benchmarks.",
        },
        metrics={
            "max_core_relative_error_percent": max(v["relative_error_percent"] for v in core_comparisons.values()),
            "running_angle_average_error_percent": running_average_error,
            "neutron_lifetime_relative_error_percent": core_comparisons["neutron_lifetime_s"]["relative_error_percent"],
        },
        thresholds={
            "sin2_theta_W_max_relative_error_percent": 2.0,
            "m_W_max_relative_error_percent": 2.0,
            "m_H_max_relative_error_percent": 2.0,
            "G_F_max_relative_error_percent": 0.5,
            "neutron_lifetime_max_relative_error_percent": 2.0,
        },
        notes="Expanded electroweak benchmark separates source-linked core gates from checked-local diagnostic layers.",
    )
    artifact["input_hashes"] = {
        "source_lock_manifest": hash_file(source_lock_json) if source_lock_json.exists() else None,
        "benchmark_package": hash_file(benchmark_package_json),
        "source_records": [
            path_hash_record(path) for path in source_lock.get("external_source_records", [])
        ],
    }
    artifact["source_lock"] = {
        "path": str(source_lock_json.relative_to(root_path)),
        "derived_inputs": source_lock.get("derived_inputs", []),
        "claim_boundary": source_lock.get("claim_boundary"),
    }
    artifact_path = topic_path / "Result" / "artifacts" / "electroweak_expanded_benchmark.json"
    save_artifact(artifact, artifact_path)

    print("=" * 70)
    print("UET ELECTROWEAK EXPANDED BENCHMARK")
    print("=" * 70)
    for name, cmp in core_comparisons.items():
        print(f"{name}: pred={cmp['predicted']:.6g} obs={cmp['observed']:.6g} err={cmp['relative_error_percent']:.3f}%")
    print(f"running-angle diagnostic avg error: {running_average_error:.3f}%")
    print(f"Artifact saved to {artifact_path}")
    print(f"RESULT: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
