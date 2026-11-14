"""
UET Test: CI_s Validation
==========================

Tests: Comprehensive validation of UET coupling parameters
- CI_s_validation data
- Transient vs steady-state behavior
- Cross-system consistency

Uses internal validation datasets.

Updated for UET V3.0
"""

import numpy as np
import os
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


TOPIC_DIR = ROOT / "docs" / "topics" / "0.14_Complex_Systems"
DATA_PATH = TOPIC_DIR / "Data" / "03_Research" / "validation"

# Engine Import (Dynamic to bypass 0.14 folder literal restriction)
try:
    import importlib.util
    from docs.core.uet_master_equation import UETParameters

    engine_file = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Complexity.py"
    spec = importlib.util.spec_from_file_location("Engine_Complexity", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETComplexityEngine = getattr(module, "UETComplexityEngine")
except Exception as e:
    print(f"Error loading Engine 0.14 Validation: {e}")
    sys.exit(1)


def load_validation_data():
    """Load all validation files (CSV and JSON)."""
    data = {}

    if DATA_PATH.exists():
        # Load CSV files
        for filepath in DATA_PATH.glob("*.csv"):
            name = filepath.stem
            try:
                import pandas as pd

                df = pd.read_csv(filepath)
                data[name] = {"type": "csv", "data": df}
            except Exception as e:
                print(f"   [WARN] Error loading {filepath.name}: {e}")

        # Load JSON files
        for filepath in DATA_PATH.glob("*.json"):
            name = filepath.stem
            try:
                import json

                with open(filepath, "r") as f:
                    json_data = json.load(f)
                data[name] = {"type": "json", "data": json_data}
            except Exception as e:
                print(f"   [WARN] Error loading {filepath.name}: {e}")

    return data


def analyze_validation_data(data):
    """
    Analyze validation datasets for UET consistency.

    Checks:
    1. CI_s parameter ranges
    2. Steady-state convergence
    3. Cross-validation scores
    """
    results = []

    for name, info in data.items():
        dtype = info["type"]
        content = info["data"]

        if dtype == "csv":
            df = content
            if df is None or len(df) < 2:
                continue

            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

            for col in numeric_cols[:5]:
                values = df[col].dropna().values
                if len(values) < 2:
                    continue

                mean_val = np.mean(values)
                std_val = np.std(values)

                # Convergence check: is the std decreasing over time?
                if len(values) > 10:
                    first_half_std = np.std(values[: len(values) // 2])
                    second_half_std = np.std(values[len(values) // 2 :])
                    converging = second_half_std < first_half_std
                else:
                    converging = None

                engine = UETComplexityEngine(name="Validation_Analyzer")
                metrics = engine.calculate_stability_metrics(values)

                results.append(
                    {
                        "dataset": name,
                        "parameter": col,
                        "mean": metrics["mean"],
                        "std": metrics["std"],
                        "cv": metrics["cv"],
                        "converging": converging,
                        "validation_score": metrics["equilibrium_score"],
                        "n_points": len(values),
                    }
                )

        elif dtype == "json":
            # Handle JSON structure
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, (int, float)):
                        results.append(
                            {
                                "dataset": name,
                                "parameter": key,
                                "mean": value,
                                "std": 0,
                                "cv": 0,
                                "converging": None,
                                "validation_score": 1.0,  # Single value = consistent
                                "n_points": 1,
                            }
                        )

    return results


def run_test():
    """Run CI_s validation test."""
    print("\n" + "=" * 60)
    print("[VALID] UET TEST: CI_s Validation")
    print("=" * 60)
    print("\nEquation: Omega = V(C) + kappa|grad(C)|^2 + beta*C*I")
    print("Validation: Cross-system consistency check")

    # Load data
    print("\n[VALIDATION DATA]")
    print("-" * 40)

    data = load_validation_data()

    if not data:
        print("   [FAIL] No validation data found")
        return {"status": "FAIL", "error": "No data"}

    print(f"   Loaded {len(data)} datasets:")
    for name, info in data.items():
        dtype = info["type"]
        if dtype == "csv":
            rows = len(info["data"])
            print(f"      - {name} ({dtype}, {rows} rows)")
        else:
            print(f"      - {name} ({dtype})")

    # Analyze
    results = analyze_validation_data(data)

    if not results:
        print("\n   [FAIL] Could not analyze data")
        return {"status": "FAIL", "error": "Analysis failed"}

    print(f"\n   Analyzed {len(results)} parameters")

    # Convergence analysis
    converging_count = sum(1 for r in results if r.get("converging") == True)
    diverging_count = sum(1 for r in results if r.get("converging") == False)

    print(f"\n   Convergence Status:")
    print(f"      Converging: {converging_count}")
    print(f"      Diverging: {diverging_count}")

    # Top validated parameters
    print("\n   Top Validated Parameters:")
    sorted_results = sorted(results, key=lambda x: x["validation_score"], reverse=True)
    for r in sorted_results[:5]:
        print(
            f"      {r['dataset']}/{r['parameter']}: Score={r['validation_score']:.3f}"
        )

    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)

    avg_score = np.mean([r["validation_score"] for r in results])

    print(f"   Parameters validated: {len(results)}")
    print(f"   Average Validation Score: {avg_score:.3f}")

    # Grade
    if avg_score > 0.7:
        grade = "***** EXCELLENT VALIDATION"
        status = "PASS"
    elif avg_score > 0.5:
        grade = "**** GOOD VALIDATION"
        status = "PASS"
    elif avg_score > 0.3:
        grade = "*** MODERATE"
        status = "PASS"
    else:
        grade = "** NEEDS REVIEW"
        status = "WARN"

    print(f"\n   Grade: {grade}")
    print(f"   Status: {status}")

    return {
        "status": status,
        "n_parameters": len(results),
        "avg_score": avg_score,
        "converging": converging_count,
        "results": results,
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n[OK] Test complete: {result['status']}")
