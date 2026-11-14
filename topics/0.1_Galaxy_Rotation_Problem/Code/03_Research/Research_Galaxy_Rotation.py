"""
Research: Galaxy Rotation Validation (V3.0)
===========================================
Internal repository comparison against working-copy galaxy rotation data.
"""

import importlib
import json
import sys
from dataclasses import make_dataclass
from pathlib import Path

import numpy as np

from docs import ROOT_PATH
from docs.core.reproducibility import generate_artifact, hash_dataset, save_artifact


root_path = ROOT_PATH
topic_path = root_path / "docs" / "topics" / "0.1_Galaxy_Rotation_Problem"
engine_path = topic_path / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

try:
    Engine_Galaxy_V3 = importlib.import_module("Engine_Galaxy_V3")
    UETGalaxyEngine = Engine_Galaxy_V3.UETGalaxyEngine
except ImportError as exc:
    print(f"ENGINE IMPORT ERROR: {exc}")
    sys.exit(1)


def load_data():
    """Load SPARC working-copy data from JSON."""
    data_path = topic_path / "Data" / "03_Research" / "sparc_data.json"
    if not data_path.exists():
        print(f"SPARC data not found at {data_path}")
        return []

    with data_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_validation():
    """Execute the full validation sweep."""
    print("Starting UET galaxy rotation validation...")
    data = load_data()
    if not data:
        return

    results = []
    errors = []
    mock_series = make_dataclass(
        "MockSeries",
        [
            ("name", str),
            ("mass_disk", float),
            ("radius_disk", float),
            ("mass_bulge", float),
            ("redshift", float),
        ],
    )

    for entry in data:
        name = entry.get("name", "Unknown")
        try:
            gal_params = mock_series(
                name=name,
                mass_disk=entry.get("mass_disk", 0.0),
                radius_disk=entry.get("radius_disk", 1.0),
                mass_bulge=entry.get("mass_bulge", 0.0),
                redshift=entry.get("redshift", 0.0),
            )
            engine = UETGalaxyEngine(gal_params)

            r_obs = np.asarray(entry.get("r_obs", []), dtype=float)
            v_obs = np.asarray(entry.get("v_obs", []), dtype=float)
            if r_obs.size == 0 or v_obs.size == 0:
                continue

            v_pred = np.asarray(engine.compute_curve(r_obs), dtype=float)
            mask = v_obs > 0
            if np.any(mask):
                mape = np.mean(np.abs((v_pred[mask] - v_obs[mask]) / v_obs[mask])) * 100
                if not np.isnan(mape) and not np.isinf(mape):
                    errors.append(float(mape))
                    results.append(
                        {
                            "name": name,
                            "mape": float(mape),
                            "v_max_obs": float(np.max(v_obs)),
                            "v_max_pred": float(np.max(v_pred)),
                        }
                    )
        except Exception as exc:
            print(f"Error processing {name}: {exc}")

    if not errors:
        print("No valid comparisons were produced.")
        return

    avg_error = float(np.mean(errors))
    pass_rate = float(np.sum(np.array(errors) < 15.0) / len(errors) * 100)

    print("\n" + "=" * 40)
    print("VALIDATION COMPLETE")
    print(f"Mean Error Rate: {avg_error:.2f}%")
    print(f"Pass Rate (<15% Error): {pass_rate:.1f}%")
    print("=" * 40)

    artifact = generate_artifact(
        topic="0.1_Galaxy_Rotation_Problem",
        dataset_hash=hash_dataset(data),
        results={
            "processed_entries": len(results),
            "average_error_percent": avg_error,
            "pass_rate_percent": pass_rate,
        },
        config={"error_threshold_percent": 15.0},
        metrics={
            "average_error_percent": avg_error,
            "pass_rate_percent": pass_rate,
        },
        thresholds={"max_average_error_percent": 15.0},
        notes="Internal benchmark artifact generated from repository working-copy data.",
    )
    artifact_path = topic_path / "Result" / "artifacts" / "galaxy_rotation_validation.json"
    save_artifact(artifact, artifact_path)
    print(f"Artifact saved to {artifact_path}")


if __name__ == "__main__":
    run_validation()
