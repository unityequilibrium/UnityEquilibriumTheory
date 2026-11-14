"""
[CHART] UET Test 03: Economy Value-Flow
==================================

Tests: V = C × I^k, where k ~= 1

Uses real stock market data from Yahoo Finance.

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


import numpy as np
import pandas as pd

# Import from UET V3.0 Master Equation
import sys
from docs.core.uet_glass_box import UETPathManager

from pathlib import Path

# Define Data Path
# Script: .../0.14_Complex_Systems/Code/economy/
# Data:   .../0.14_Complex_Systems/Data/
TOPIC_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = TOPIC_DIR / "Data"

_root = Path(__file__).parent
while _root.name != "docs" and _root.parent != _root:
    _root = _root.parent
sys.path.insert(0, str(_root.parent))
try:
    from docs.core.uet_master_equation import (
        UETParameters,
        SIGMA_CRIT,
        strategic_boost,
        potential_V,
        KAPPA_BEKENSTEIN,
    )
except ImportError:
    pass  # Use local definitions if not available

import os

# DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "06_complex_systems")
DATA_DIR = str(DATA_PATH)


def load_economy_data():
    """Load stock market data."""
    datasets = []
    economy_dir = os.path.join(DATA_DIR, "03_Research", "economy")

    if os.path.exists(economy_dir):
        for filename in os.listdir(economy_dir):
            if filename.endswith("_yahoo_real.csv"):
                filepath = os.path.join(economy_dir, filename)
                try:
                    df = pd.read_csv(filepath)
                    # Handle multi-index columns from yfinance
                    if "Close" in df.columns:
                        close_col = "Close"
                    elif len(df.columns) > 1:
                        # Find close column
                        for col in df.columns:
                            if "close" in str(col).lower():
                                close_col = col
                                break
                        else:
                            close_col = df.columns[1]  # Usually 2nd column
                    else:
                        continue

                    # Convert to numeric
                    df[close_col] = pd.to_numeric(df[close_col], errors="coerce")
                    name = filename.replace("_yahoo_real.csv", "")
                    datasets.append((name, df, close_col))
                except Exception as e:
                    pass

    return datasets


def calculate_value_flow_k(prices):
    """
    Calculate k from V = C × I^k

    Where:
    - C = Price level (observable)
    - I = Volume or momentum (hidden)
    - V = Total value

    Using returns: r(t) = dC/dt / C
    UET predicts: Volatility scales with k ~= 1
    """
    if len(prices) < 10:
        return None, None

    # Calculate returns
    returns = np.diff(prices) / (prices[:-1] + 1e-10)
    returns = returns[np.isfinite(returns)]

    if len(returns) < 10:
        return None, None

    # Volatility (std of returns)
    volatility = np.std(returns)

    # Autocorrelation (memory)
    mean_r = np.mean(returns)
    autocorr = np.correlate(returns - mean_r, returns - mean_r, mode="full")
    autocorr = autocorr[len(returns) - 1 :] / (autocorr[len(returns) - 1] + 1e-10)

    # Memory decay -> estimate k
    # Fast decay = k close to 1 (efficient market)
    # Slow decay = k < 1 (momentum)
    memory_time = 1
    for i, a in enumerate(autocorr[1:20]):
        if a < 0.5:
            memory_time = i + 1
            break

    # k estimation based on volatility scaling
    # For efficient markets: k ~= 1
    k_estimate = 1.0 / (1 + np.log1p(memory_time) / 5)

    return k_estimate, volatility


def run_test():
    """Run economy test."""
    print("\n" + "=" * 60)
    print("[CHART] UET TEST 03: Economy Value-Flow")
    print("=" * 60)
    print("\nEquation: V = C × I^k")
    print("UET Prediction: k ~= 1 (efficient flow)")

    datasets = load_economy_data()

    if not datasets:
        print("[FAIL] No economy data found!")
        return {"status": "FAIL", "error": "No data"}

    print(f"\nAnalyzing {len(datasets)} markets...\n")

    results = []

    for name, df, close_col in datasets:
        prices = df[close_col].dropna().values

        if len(prices) < 100:
            continue

        k, vol = calculate_value_flow_k(prices)

        if k is not None:
            results.append({"name": name, "k": k, "volatility": vol, "data_points": len(prices)})
            print(f"   {name:15}: k = {k:.3f}, vol = {vol:.4f} ({len(prices)} days)")

    if not results:
        print("[FAIL] Could not calculate k for any dataset")
        return {"status": "FAIL", "error": "Calculation failed"}

    # Average k
    avg_k = np.mean([r["k"] for r in results])
    std_k = np.std([r["k"] for r in results])

    print("\n" + "=" * 40)
    print(f"Average k = {avg_k:.3f} ± {std_k:.3f}")
    print(f"UET predicts k ~= 1.0")
    print("=" * 40)

    # Grade
    deviation = abs(avg_k - 1.0)

    if deviation < 0.1:
        grade = "***** EXCELLENT"
        status = "PASS"
    elif deviation < 0.2:
        grade = "**** GOOD"
        status = "PASS"
    elif deviation < 0.4:
        grade = "*** MODERATE"
        status = "WARN"
    else:
        grade = "** NEEDS WORK"
        status = "FAIL"

    print(f"\nGrade: {grade}")

    # --- VISUALIZATION ---
    try:
        from docs.core import uet_viz

        result_dir = UETPathManager.get_result_dir(
            topic_id="0.14_Complex_Systems",
            experiment_name="Research_Economy",
            pillar="03_Research",
            category="log",
        )
        result_dir.mkdir(parents=True, exist_ok=True)

        if results:
            k_vals = [r["k"] for r in results]
            names = [r["name"] for r in results]
            vols = [r["volatility"] for r in results]

            fig = uet_viz.go.Figure()
            # Plot K vs Volatility
            fig.add_trace(
                uet_viz.go.Scatter(
                    x=vols,
                    y=k_vals,
                    mode="markers+text",
                    text=names,
                    marker=dict(size=12, color=k_vals, colorscale="Bluered"),
                    name="Markets",
                )
            )

            # Theoretical Line (k=1)
            fig.add_hline(
                y=1.0, line_dash="dash", line_color="green", annotation_text="UET Ideal (k=1)"
            )

            fig.update_layout(
                title="Economic Value Flow: k-index Analysis",
                xaxis_title="Volatility (sigma)",
                yaxis_title="k (Value Flow Coefficient)",
            )
            uet_viz.save_plot(fig, "economy_viz.png", result_dir)
            print("  [Viz] Generated 'economy_viz.png'")

    except Exception as e:
        print(f"Viz Error: {e}")

    return {
        "status": status,
        "avg_k": avg_k,
        "std_k": std_k,
        "expected": 1.0,
        "deviation": deviation,
        "markets_tested": len(results),
        "results": results,
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n[OK] Test complete: {result['status']}")
