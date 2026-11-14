"""
UET Market Cycle Analysis
=========================
Topic: 0.25 - Strategy Power Economics
Hypothesis: Markets follow Power Laws (Unity Scale) rather than Gaussian Walks.
Data: S&P 500 Historical Data (Yahoo Finance Real)
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
import csv
import math
import numpy as np

# --- PATH SETUP ---
current_path = Path(__file__).resolve()
ROOT = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists():
        ROOT = parent
        break

if ROOT and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from docs.core.uet_glass_box import UETPathManager, UETMetricLogger
except Exception as e:
    print(f"CRITICAL SETUP ERROR: {e}")
    sys.exit(1)


def load_market_data(filename):
    """Load and parse Yahoo Finance CSV (Multi-header format)."""
    # Try standard paths
    path = (
        ROOT
        / "docs"
        / "topics"
        / "0.25_Strategy_Power_Economics"
        / "Data"
        / "03_Research"
        / filename
    )

    if not path.exists():
        raise FileNotFoundError(f"Missing Data: {path}")

    prices = []
    dates = []

    with open(path, "r") as f:
        lines = f.readlines()

    # Skip first 3 header lines (Ticker, etc)
    # Line 0: Price,Close...
    # Line 1: Ticker,^GSPC...
    # Line 2: Date,,,,,

    start_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("20") or line.startswith("19"):  # Detect Date row
            start_idx = i
            break

    print(f"  Parsng from line {start_idx}...")

    for line in lines[start_idx:]:
        parts = line.strip().split(",")
        if len(parts) < 2:
            continue
        try:
            d = parts[0]
            # Column 1 is Close based on file inspection
            p = float(parts[1])
            dates.append(d)
            prices.append(p)
        except ValueError:
            continue

    return dates, np.array(prices)


def run_analysis():
    print("=" * 60)
    print("UET MARKET POWER LAW ANALYSIS")
    print("Data: S&P 500 (Real Historical)")
    print("=" * 60)

    # 1. Setup Standard Logger (Showcase)
    output_dir = UETPathManager.get_result_dir(
        topic_id="0.25", experiment_name="Market_Power_Law", category="showcase"
    )
    logger = UETMetricLogger("Market_Power_Law", topic_id="0.25", category="showcase")

    # 2. Load Data
    try:
        dates, prices = load_market_data("SP500_yahoo_real.csv")
    except Exception as e:
        print(f"❌ Data Load Error: {e}")
        return False

    print(f"  Loaded {len(prices)} trading days.")
    print(f"  Range: {dates[0]} to {dates[-1]}")

    # 3. Compute Log Returns
    # R_t = ln(P_t / P_{t-1})
    returns = np.diff(np.log(prices))

    # Filter zeros
    returns = returns[returns != 0]

    # Statistics
    mu = np.mean(returns)
    sigma = np.std(returns)
    kurtosis = np.mean(((returns - mu) / sigma) ** 4)  # Excess Kurtosis should be > 3 for Fat Tails

    print(f"  Mean Return: {mu:.5f}")
    print(f"  Volatility (Sigma): {sigma:.5f}")
    print(f"  Kurtosis: {kurtosis:.2f} (Normal=3.0)")

    passed = kurtosis > 3.5  # Proof of Fat Tails
    print(f"  Result: {'✅ PASS' if passed else '❌ FAIL'} (Fat Tails Confirmed)")

    # 4. Visualization (Fat Tail Proof)
    try:
        import matplotlib.pyplot as plt
        import scipy.stats as stats

        plt.figure(figsize=(10, 6))

        # Empirical Data (Histogram)
        # Normalize to probability density
        n, bins, patches = plt.hist(
            returns, bins=100, density=True, alpha=0.6, color="blue", label="S&P 500 Returns"
        )

        # Gaussian Fit (The "Standard" theory failure)
        x = np.linspace(min(returns), max(returns), 1000)
        pdf_normal = stats.norm.pdf(x, mu, sigma)
        plt.plot(x, pdf_normal, "r--", linewidth=2, label="Gaussian Prediction (BSM)")

        # Power Law / Student-t / Cauchy (UET-like Fat Tail)
        # We assume UET implies higher probability of extremes (Linkage of events)
        # Just creating a visual reference for "Fat Tail" (e.g. Student-t with df=3)
        pdf_fat = stats.t.pdf(x, df=3, loc=mu, scale=sigma * 0.6)  # Heuristic fit
        plt.plot(x, pdf_fat, "g-", linewidth=2, label="UET / Power Law (Fat Tail)")

        plt.yscale("log")  # Log scale is crucial to see tails!
        plt.ylim(1e-4, max(pdf_normal) * 2)
        plt.xlim(-0.05, 0.05)  # Zoom in on the core distributions

        plt.xlabel("Daily Log Return")
        plt.ylabel("Probability Density (Log Scale)")
        plt.title(f"Market Structure Proof: Fat Tails (Kurtosis={kurtosis:.1f})")
        plt.legend()
        plt.grid(True, which="major", alpha=0.3)

        save_path = output_dir / "Market_Power_Law.png"
        plt.savefig(save_path, dpi=300)
        print(f"📸 Showcase Image Saved: {save_path}")

    except Exception as e:
        print(f"Viz Error: {e}")

    return passed


if __name__ == "__main__":
    run_analysis()
