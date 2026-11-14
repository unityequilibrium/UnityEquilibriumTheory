"""
UET Electroweak vs PDG 2025 Real-Data Comparison
================================================
Reads source-locked PDG SQLite data and compares UET electroweak engine outputs
against PDG 2025 summary-table values.

This script is strict about what it proves:
- It validates selected electroweak observables against a real upstream source.
- It does not claim a full Standard Model replacement.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

# --- ROBUST UET BOOTSTRAP ---
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
engine_path = topic_path / "Code" / "01_Engine"
reference_package_json = root_path / "docs" / "data" / "external" / "particle_physics" / "pdg" / "electroweak_reference_package.json"
source_lock_json = topic_path / "Data" / "03_Research" / "source_lock_manifest.json"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

try:
    from Engine_Electroweak import UETElectroweakSolver
except ImportError as exc:
    print(f"CRITICAL SETUP ERROR: {exc}")
    sys.exit(1)

def load_reference_package() -> dict:
    if not reference_package_json.exists():
        raise FileNotFoundError(f"Electroweak reference package not found: {reference_package_json}")
    return json.loads(reference_package_json.read_text(encoding="utf-8"))


def load_source_lock() -> dict:
    if not source_lock_json.exists():
        return {"external_source_records": [], "derived_inputs": [], "status": "MISSING"}
    return json.loads(source_lock_json.read_text(encoding="utf-8"))


def path_hash_record(path_string: str) -> dict:
    path = root_path / path_string
    return {
        "path": path_string,
        "sha256": hash_file(path) if path.exists() and path.is_file() else None,
        "status": "present" if path.exists() else "missing",
    }


def relative_error_percent(predicted: float, observed: float) -> float:
    return abs(predicted - observed) / abs(observed) * 100.0


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


def run_test() -> bool:
    print("=" * 70)
    print("UET ELECTROWEAK REAL-DATA TEST")
    print("Data: PDG 2025 SQLite + electroweak effective-angle snapshot")
    print("=" * 70)

    reference_package = load_reference_package()
    pdg = reference_package["references"]
    source_lock = load_source_lock()
    solver = UETElectroweakSolver()
    result = solver.solve()

    comparisons = {
        "sin2_theta_W": {
            "predicted": result.sin2_theta_W,
            "observed": pdg["sin2_theta_W_effective"]["value"],
            "unit": "dimensionless",
        },
        "m_W_GeV": {
            "predicted": result.m_W_predicted,
            "observed": pdg["m_W"]["value"],
            "unit": "GeV",
        },
        "m_H_GeV": {
            "predicted": result.m_Higgs_predicted,
            "observed": pdg["m_H"]["value"],
            "unit": "GeV",
        },
        "G_F_GeV_minus_2": {
            "predicted": result.fermi_constant,
            "observed": pdg["fermi_constant"]["value"],
            "unit": "GeV^-2",
        },
    }

    print("\n[1] ELECTROWEAK OBSERVABLES")
    print("-" * 70)
    print("| Observable | UET | PDG/reference | Rel. error |")
    print("| :-- | --: | --: | --: |")

    max_rel_error = 0.0
    for key, cmp in comparisons.items():
        err = relative_error_percent(cmp["predicted"], cmp["observed"])
        cmp["relative_error_percent"] = err
        max_rel_error = max(max_rel_error, err)
        print(
            f"| {key} | {cmp['predicted']:.6g} | {cmp['observed']:.6g} | {err:.3f}% |"
        )

    print("\n[2] INTERPRETATION")
    print("-" * 70)
    print(
        "This test checks whether the UET electroweak engine lands near real upstream\n"
        "electroweak scales and couplings. It does not prove the full gauge theory; it\n"
        "tests whether the numerical consequences of the engine are close to real PDG values."
    )

    # Strict but not theorem-level thresholds.
    passes = {
        "sin2_theta_W": comparisons["sin2_theta_W"]["relative_error_percent"] < 2.0,
        "m_W_GeV": comparisons["m_W_GeV"]["relative_error_percent"] < 2.0,
        "m_H_GeV": comparisons["m_H_GeV"]["relative_error_percent"] < 2.0,
        "G_F_GeV_minus_2": comparisons["G_F_GeV_minus_2"]["relative_error_percent"] < 0.5,
    }
    passed = all(passes.values())

    print("\n[3] PASS/FAIL GATES")
    print("-" * 70)
    for name, ok in passes.items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")

    artifact = generate_artifact(
        topic="0.6_Electroweak_Physics",
        dataset_hash=hash_dataset(
            {
                "reference_package": str(reference_package_json.relative_to(root_path)),
                "reference_package_exists": reference_package_json.exists(),
                "m_W": pdg["m_W"]["value"],
                "m_Z": pdg["m_Z"]["value"],
                "m_H": pdg["m_H"]["value"],
                "sin2_theta_W_effective": pdg["sin2_theta_W_effective"]["value"],
                "G_F": pdg["fermi_constant"]["value"],
            }
        ),
        results=to_builtin({
            "status": "PASS" if passed else "FAIL",
            "audit": result.audit,
            "mW_mZ_ratio": result.mW_mZ_ratio,
            "theta_W_deg": result.theta_W_deg,
            "lambda_higgs": result.lambda_higgs,
            "comparisons": comparisons,
            "passes": passes,
        }),
        config={
            "source_locked_reference": str(reference_package_json.relative_to(root_path)),
            "pdg_sqlite_source": reference_package["pdg_sqlite_source"],
            "checked_local_reference_source": reference_package["checked_local_reference_source"],
            "source_lock_manifest": str(source_lock_json.relative_to(root_path)),
            "sin2_theta_reference_note": pdg["sin2_theta_W_effective"]["source_note"],
            "rule": "real-data comparison against PDG 2025 summary-table observables where available",
        },
        metrics={
            "max_relative_error_percent": max_rel_error,
            "m_W_relative_error_percent": comparisons["m_W_GeV"]["relative_error_percent"],
            "m_H_relative_error_percent": comparisons["m_H_GeV"]["relative_error_percent"],
            "G_F_relative_error_percent": comparisons["G_F_GeV_minus_2"]["relative_error_percent"],
            "sin2_theta_W_relative_error_percent": comparisons["sin2_theta_W"]["relative_error_percent"],
        },
        thresholds={
            "sin2_theta_W_max_relative_error_percent": 2.0,
            "m_W_max_relative_error_percent": 2.0,
            "m_H_max_relative_error_percent": 2.0,
            "G_F_max_relative_error_percent": 0.5,
        },
        notes="Real-data electroweak comparison using a structured source-locked PDG reference package plus explicit checked-local note for observables not yet directly mapped from the SQLite workflow.",
    )
    artifact["input_hashes"] = {
        "source_lock_manifest": hash_file(source_lock_json) if source_lock_json.exists() else None,
        "reference_package": hash_file(reference_package_json),
        "source_records": [
            path_hash_record(path) for path in source_lock.get("external_source_records", [])
        ],
    }
    artifact["source_lock"] = {
        "path": str(source_lock_json.relative_to(root_path)),
        "derived_inputs": source_lock.get("derived_inputs", []),
        "claim_boundary": source_lock.get("claim_boundary"),
    }
    artifact_path = topic_path / "Result" / "artifacts" / "electroweak_pdg_validation.json"
    save_artifact(artifact, artifact_path)
    print(f"\nArtifact saved to {artifact_path}")
    print(f"\nRESULT: {'PASS' if passed else 'FAIL'}")
    return passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
