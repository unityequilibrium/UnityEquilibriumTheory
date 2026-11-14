"""
UET Test: Economic Health Validation
=====================================

Tests: UET equilibrium in macroeconomic indicators
- GDP growth vs other economic health metrics
- Trade balance, inflation, debt dynamics

Uses real World Bank / IMF data.

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
DATA_PATH = TOPIC_DIR / "Data" / "03_Research" / "economic_health"

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
    print(f"Error loading Engine 0.14 Econ: {e}")
    sys.exit(1)


def load_economic_data():
    """Load all economic health CSV files."""
    datasets = {}

    if DATA_PATH.exists():
        for filepath in DATA_PATH.glob("econ_*.csv"):
            name = filepath.stem.replace("econ_", "")
            try:
                import pandas as pd

                df = pd.read_csv(filepath)
                datasets[name] = df
            except Exception as e:
                print(f"   [WARN] Error loading {filepath.name}: {e}")

    return datasets


def analyze_economic_equilibrium(datasets):
    """
    Analyze economic indicators for UET equilibrium.

    UET Interpretation:
    - Stable growth = equilibrium state
    - Low volatility = reduced perturbations
    - Correlations = coupled system dynamics
    """
    results = []

    engine = UETComplexityEngine(name="Economic_Stability_Analyzer")

    for name, df in datasets.items():
        if df is None or len(df) < 5:
            continue

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols[:3]:
            values = df[col].dropna().values
            if len(values) < 5:
                continue

            # Delegate to Engine
            metrics = engine.calculate_stability_metrics(values)

            results.append(
                {
                    "indicator": f"{name}_{col}",
                    "mean": metrics["mean"],
                    "std": metrics["std"],
                    "cv": metrics["cv"],
                    "trend": 0.0,  # Simplified
                    "n_points": len(values),
                    "equilibrium_score": metrics["equilibrium_score"],
                }
            )

    return results


def run_test():
    """Run economic health equilibrium test."""
    print("\n" + "=" * 60)
    print("[ECON] UET TEST: Economic Health Equilibrium")
    print("=" * 60)
    print("\nEquation: Omega = V(C) + kappa|grad(C)|^2 + beta*C*I")
    print("UET Prediction: Economies tend toward stable equilibrium")

    # Load data
    print("\n[ECONOMIC INDICATORS]")
    print("-" * 40)

    datasets = load_economic_data()

    if not datasets:
        print("   [FAIL] No economic data found")
        return {"status": "FAIL", "error": "No data"}

    print(f"   Loaded {len(datasets)} datasets:")
    for name in datasets.keys():
        print(f"      - {name}")

    # Analyze
    results = analyze_economic_equilibrium(datasets)

    if not results:
        print("\n   [FAIL] Could not analyze data")
        return {"status": "FAIL", "error": "Analysis failed"}

    print(f"\n   Analyzed {len(results)} indicators")
    print("\n   Top Indicators by Stability:")

    # Sort by equilibrium score
    sorted_results = sorted(results, key=lambda x: x["equilibrium_score"], reverse=True)

    for r in sorted_results[:5]:
        print(f"      {r['indicator'][:30]:30s}")
        print(
            f"         Mean: {r['mean']:.2f}, CV: {r['cv']:.2f}, Score: {r['equilibrium_score']:.3f}"
        )

    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)

    avg_eq = np.mean([r["equilibrium_score"] for r in results])
    avg_cv = np.mean([r["cv"] for r in results])

    print(f"   Indicators analyzed: {len(results)}")
    print(f"   Average CV: {avg_cv:.2f}")
    print(f"   Average Equilibrium Score: {avg_eq:.3f}")

    # Grade
    if avg_eq > 0.5:
        grade = "***** STABLE ECONOMY"
        status = "PASS"
    elif avg_eq > 0.3:
        grade = "**** MODERATE STABILITY"
        status = "PASS"
    else:
        grade = "*** VOLATILE"
        status = "WARN"

    print(f"\n   Grade: {grade}")
    print(f"   Status: {status}")

    return {
        "status": status,
        "n_indicators": len(results),
        "avg_equilibrium": avg_eq,
        "results": results,
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n[OK] Test complete: {result['status']}")
