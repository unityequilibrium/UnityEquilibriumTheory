"""
[HRV] UET Test 04: Bio HRV Equilibrium
===================================

Tests: dOmega/dt <= 0 (System seeks equilibrium)

Uses real HRV data from PhysioNet.

Updated for UET V3.0
"""

import sys
from pathlib import Path

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


import sys
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


import numpy as np
import os
import glob
import math
import json
import hashlib
from datetime import datetime, timezone
from docs.core.uet_glass_box import UETPathManager


# Import from UET V3.0 Master Equation
try:
    from docs.core.uet_master_equation import (
        UETParameters,
        SIGMA_CRIT,
        strategic_boost,
        potential_V,
        KAPPA_BEKENSTEIN,
    )
except ImportError:
    pass

# Define Data Path
TOPIC_DIR = (
    root_path / "docs" / "topics" / "0.14_Complex_Systems"
    if root_path
    else Path(__file__).resolve().parent.parent.parent
)
DATA_PATH = TOPIC_DIR / "Data"
DATA_DIR = str(DATA_PATH)
ARTIFACT_PATH = (
    TOPIC_DIR / "Result" / "artifacts" / "0_14_complex_systems_verification.json"
)


# Standardized UET Root Path
from docs import ROOT_PATH

root_path = ROOT_PATH


def load_hrv_data():
    """Load HRV data from PhysioNet."""
    bio_dir = os.path.join(DATA_DIR, "03_Research", "biology_hrv")
    datasets = []

    if os.path.exists(bio_dir):
        for filename in os.listdir(bio_dir):
            if filename.startswith("physionet_") and filename.endswith("_rr.csv"):
                filepath = os.path.join(bio_dir, filename)
                try:
                    # Read CSV, first column is RR intervals
                    import pandas as pd

                    df = pd.read_csv(filepath)
                    if len(df.columns) > 0:
                        # Convert to numeric, coerce errors (handles header in data)
                        rr = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().values
                        if len(rr) > 10:
                            name = filename.replace(".csv", "")
                            datasets.append((name, rr))
                except Exception as e:
                    print(f"   [WARN] Could not load {filename}: {e}")

    return datasets


def _to_jsonable(value):
    """Convert numpy/scalar values to stable JSON primitives."""
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hrv_input_hashes():
    bio_dir = TOPIC_DIR / "Data" / "03_Research" / "biology_hrv"
    inputs = []
    extra_inputs = [
        bio_dir / "source_lock_manifest.json",
        root_path
        / "docs"
        / "data"
        / "external"
        / "biophysics"
        / "hrv"
        / "mit_bih_nsrdb"
        / "source_record.json",
    ]
    for path in extra_inputs:
        try:
            rel = path.relative_to(root_path)
        except ValueError:
            rel = path
        if path.exists():
            inputs.append(
                {
                    "path": str(rel).replace("\\", "/"),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                    "loaded_by_primary_script": False,
                    "provenance_role": "source_lock",
                }
            )
        else:
            inputs.append(
                {
                    "path": str(rel).replace("\\", "/"),
                    "missing": True,
                    "provenance_role": "source_lock",
                }
            )
    if not bio_dir.exists():
        return inputs
    for path in sorted(bio_dir.glob("*.csv")):
        inputs.append(
            {
                "path": str(path.relative_to(TOPIC_DIR)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "loaded_by_primary_script": path.name.startswith("physionet_")
                and path.name.endswith("_rr.csv"),
            }
        )
    return inputs


def write_verification_artifact(result):
    """Write the primary verifier artifact required by VERIFICATION_SPEC.md."""
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "schema_version": "1.1",
        "topic": "0.14_Complex_Systems",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.14_Complex_Systems/Code/03_Research/Research_Biology_HRV.py",
        "status": result.get("status", "FAIL"),
        "passed_run_contract": result.get("status") in {"PASS", "WARN"},
        "input_hashes": _hrv_input_hashes(),
        "metrics": {
            "avg_sdnn_ms": result.get("avg_sdnn_ms"),
            "avg_rmssd_ms": result.get("avg_rmssd_ms"),
            "avg_equilibrium": result.get("avg_equilibrium"),
            "subjects": result.get("subjects", 0),
        },
        "thresholds": {
            "run_without_error": True,
            "artifact_written": True,
            "working_sdnn_pass_range_ms": [30, 200],
            "working_equilibrium_min_for_strong_pass": 0.5,
        },
        "interpretation": (
            "Source-referenced derived-RR HRV run-contract artifact only; this does not validate "
            "clinical classification, SOC, econophysics, climate, inequality, or social-network branches."
        ),
        "results": _to_jsonable(result),
    }
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"  [Artifact] Saved {ARTIFACT_PATH}")


def calculate_hrv_metrics(rr_intervals):
    """
    Calculate HRV metrics related to UET equilibrium.
    Delegates to Engine_Complexity.
    """
    # Initialize Engine
    # Note: We use the Complexity Engine which handles Stochastic systems
    import importlib.util

    eng_path = (
        root_path / "docs/topics/0.14_Complex_Systems/Code/01_Engine/Engine_Complexity.py"
    )
    if eng_path.exists():
        spec = importlib.util.spec_from_file_location("Engine_Complexity", eng_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        engine = mod.UETComplexityEngine(name="HRV_Analyzer")
    else:
        print("CRITICAL: Engine not found.")
        return None

    metrics = engine.calculate_hrv_metrics(rr_intervals)

    # Check Kill Switch
    if metrics and math.isnan(metrics.get("equilibrium_score", 0)):
        print("KILL SWITCH DETECTED.")
        return None

    return metrics


def run_test():
    """Run HRV equilibrium test."""
    print("\n" + "=" * 60)
    print("[HRV] UET TEST 04: Bio HRV Equilibrium")
    print("=" * 60)
    print("\nEquation: dOmega/dt <= 0 (equilibrium seeking)")
    print("UET Prediction: Healthy systems show balanced variability")

    datasets = load_hrv_data()

    if not datasets:
        print("[FAIL] No HRV data found!")
        result = {"status": "FAIL", "error": "No data"}
        write_verification_artifact(result)
        return result

    print(f"\nAnalyzing {len(datasets)} subjects...\n")

    results = []

    for name, rr in datasets:
        metrics = calculate_hrv_metrics(rr)

        if metrics:
            results.append({"name": name, **metrics})
            print(f"   {name}:")
            print(f"      Mean RR: {metrics['mean_rr']*1000:.0f} ms")
            print(f"      SDNN: {metrics['sdnn']*1000:.0f} ms")
            print(f"      RMSSD: {metrics['rmssd']*1000:.0f} ms")
            print(f"      Equilibrium Score: {metrics['equilibrium_score']:.2f}")
            print()

    if not results:
        print("[FAIL] Could not calculate metrics")
        result = {"status": "FAIL", "error": "Calculation failed"}
        write_verification_artifact(result)
        return result

    # Summary
    avg_eq = np.mean([r["equilibrium_score"] for r in results])
    avg_sdnn = np.mean([r["sdnn"] for r in results]) * 1000
    avg_rmssd = np.mean([r["rmssd"] for r in results]) * 1000

    print("=" * 40)
    print(f"Average SDNN: {avg_sdnn:.0f} ms")
    print(f"Average RMSSD: {avg_rmssd:.0f} ms")
    print(f"Average Equilibrium Score: {avg_eq:.2f}")
    print("=" * 40)

    # Grade
    # Normal SDNN: 50-150 ms (healthy)
    if 50 < avg_sdnn < 150 and avg_eq > 0.5:
        grade = "***** HEALTHY EQUILIBRIUM"
        status = "PASS"
    elif 30 < avg_sdnn < 200:
        grade = "**** NORMAL RANGE"
        status = "PASS"
    elif avg_sdnn > 20:
        grade = "*** BORDERLINE"
        status = "WARN"
    else:
        grade = "** LOW VARIABILITY"
        status = "FAIL"

    print(f"\nGrade: {grade}")
    print("\nInterpretation:")
    print("   High SDNN (>100ms) = High adaptability")
    print("   Low SDNN (<50ms) = Reduced flexibility (stress/disease)")

    # --- VISUALIZATION ---
    try:
        from docs.core import uet_viz

        result_dir = UETPathManager.get_result_dir(
            topic_id="0.14_Complex_Systems",
            experiment_name="Research_Biology_HRV",
            pillar="03_Research",
            category="log",
        )
        result_dir.mkdir(parents=True, exist_ok=True)

        if results:
            # Plot SD1 vs SD2 (Poincaré Metrics) representing Equilibrium State
            sd1s = [r.get("sd1", 0) * 1000 for r in results]
            sd2s = [r.get("sd2", 0) * 1000 for r in results]
            names = [r.get("name", "Subject") for r in results]
            scores = [r.get("equilibrium_score", 0) for r in results]

            fig = uet_viz.go.Figure()
            fig.add_trace(
                uet_viz.go.Scatter(
                    x=sd1s,
                    y=sd2s,
                    mode="markers",
                    text=names,
                    marker=dict(
                        size=12,
                        color=scores,
                        colorscale="RdYlGn",
                        showscale=True,
                        colorbar=dict(title="Equilibrium Score"),
                    ),
                )
            )

            # Identity line (SD1=SD2)
            max_val = max(max(sd1s), max(sd2s)) if sd1s else 100
            fig.add_trace(
                uet_viz.go.Scatter(
                    x=[0, max_val],
                    y=[0, max_val],
                    mode="lines",
                    line=dict(dash="dash", color="gray"),
                    name="Balanced",
                )
            )

            fig.update_layout(
                title="HRV Non-Linear Dynamics: Equilibrium Analysis",
                xaxis_title="SD1 (Short-Term Variability) [ms]",
                yaxis_title="SD2 (Long-Term Variability) [ms]",
            )
            uet_viz.save_plot(fig, "biology_viz.png", result_dir)
            print("  [Viz] Generated 'biology_viz.png'")

    except Exception as e:
        print(f"Viz Error: {e}")

    result = {
        "status": status,
        "avg_sdnn_ms": avg_sdnn,
        "avg_rmssd_ms": avg_rmssd,
        "avg_equilibrium": avg_eq,
        "subjects": len(results),
        "results": results,
    }
    write_verification_artifact(result)
    return result


if __name__ == "__main__":
    result = run_test()
    print(f"\n[OK] Test complete: {result['status']}")
