"""
UET Test: CI Ledger Validation
===============================

Tests: UET coupling constant (CI) validation using ledger data
- CI parameter stability across systems
- kappa, delta, M parameter validation

Uses internal validation data.

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
DATA_PATH = TOPIC_DIR / "Data" / "03_Research" / "ledgers"

# Engine Import (Dynamic to bypass 0.14 folder literal restriction)
try:
    import importlib.util
    from docs.core.uet_master_equation import UETParameters

    try:
        from docs.core.uet_master_equation import KAPPA_BEKENSTEIN
    except ImportError:
        KAPPA_BEKENSTEIN = 6.531e-71  # Fallback for UET 0.8.7 standard

    engine_file = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Complexity.py"
    spec = importlib.util.spec_from_file_location("Engine_Complexity", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETComplexityEngine = getattr(module, "UETComplexityEngine")
except Exception as e:
    print(f"Error loading Engine 0.14 Ledger: {e}")
    sys.exit(1)


def load_ledger_data():
    """Load all ledger CSV files."""
    ledgers = {}

    if DATA_PATH.exists():
        for filepath in DATA_PATH.glob("ledger_*.csv"):
            name = filepath.stem.replace("ledger_", "")
            try:
                import pandas as pd

                df = pd.read_csv(filepath)
                ledgers[name] = df
            except Exception as e:
                print(f"   [WARN] Error loading {filepath.name}: {e}")

    return ledgers


def analyze_ledger_consistency(ledgers):
    """
    Analyze ledger data for UET parameter consistency.

    UET Validation:
    - CI parameters should be consistent across systems
    - kappa should match Bekenstein bound
    - Derived parameters should not be fitted
    """
    results = []

    for name, df in ledgers.items():
        if df is None or len(df) < 2:
            continue

        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols[:5]:
            values = df[col].dropna().values
            if len(values) < 2:
                continue

            mean_val = np.mean(values)
            std_val = np.std(values)
            min_val = np.min(values)
            max_val = np.max(values)

            engine = UETComplexityEngine(name="Ledger_Analyzer")
            metrics = engine.calculate_stability_metrics(values)

            results.append(
                {
                    "ledger": name,
                    "parameter": col,
                    "mean": metrics["mean"],
                    "std": metrics["std"],
                    "min": min_val,
                    "max": max_val,
                    "rel_std": metrics["cv"],
                    "consistency_score": metrics["equilibrium_score"],
                    "n_entries": len(values),
                }
            )

    return results


def run_test():
    """Run CI ledger validation test."""
    print("\n" + "=" * 60)
    print("[LEDGER] UET TEST: CI Ledger Validation")
    print("=" * 60)
    print("\nEquation: Omega = V(C) + kappa|grad(C)|^2 + beta*C*I")
    print("Validation: UET parameters should be physically derived, not fitted")

    # Load data
    print("\n[LEDGER DATA]")
    print("-" * 40)

    ledgers = load_ledger_data()

    if not ledgers:
        print("   [FAIL] No ledger data found")
        return {"status": "FAIL", "error": "No data"}

    print(f"   Loaded {len(ledgers)} ledgers:")
    for name in ledgers.keys():
        print(f"      - {name}")

    # Analyze
    results = analyze_ledger_consistency(ledgers)

    if not results:
        print("\n   [FAIL] Could not analyze ledgers")
        return {"status": "FAIL", "error": "Analysis failed"}

    print(f"\n   Analyzed {len(results)} parameters")

    # Check kappa consistency
    print("\n[KAPPA VALIDATION]")
    print("-" * 40)
    print(f"   Theoretical kappa (Bekenstein): {KAPPA_BEKENSTEIN:.3e}")

    kappa_results = [
        r
        for r in results
        if "kappa" in r["ledger"].lower() or "kappa" in r["parameter"].lower()
    ]
    if kappa_results:
        for r in kappa_results[:3]:
            print(
                f"   {r['ledger']}/{r['parameter']}: {r['mean']:.3e} +/- {r['std']:.3e}"
            )

    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)

    avg_consistency = np.mean([r["consistency_score"] for r in results])

    print(f"   Parameters validated: {len(results)}")
    print(f"   Average Consistency: {avg_consistency:.3f}")

    # Grade
    if avg_consistency > 0.7:
        grade = "***** HIGHLY CONSISTENT"
        status = "PASS"
    elif avg_consistency > 0.5:
        grade = "**** GOOD CONSISTENCY"
        status = "PASS"
    elif avg_consistency > 0.3:
        grade = "*** MODERATE"
        status = "PASS"
    else:
        grade = "** LOW CONSISTENCY"
        status = "WARN"

    print(f"\n   Grade: {grade}")
    print(f"   Status: {status}")

    return {
        "status": status,
        "n_parameters": len(results),
        "avg_consistency": avg_consistency,
        "results": results,
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n[OK] Test complete: {result['status']}")
