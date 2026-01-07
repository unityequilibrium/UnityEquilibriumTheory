#!/usr/bin/env python3
"""
🏦 ECONOPHYSICS: F = -∇E Analysis
==================================

Core Analysis: Apply UET's "Force = -∇E" framework to financial markets.

Physics-Economics Analogy:
- Energy E(t) → Market "stress" / Deviation from equilibrium
- Force F → Price change (returns)
- ∇E → Gradient of market stress

Key Hypothesis:
- Returns (price changes) should correlate with gradient of market "energy"
- Similar to physical systems moving toward lower energy states

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from scipy.optimize import curve_fit
from dataclasses import dataclass
from typing import Optional, Tuple

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).parent / "market_data"
FIGURES_DIR = Path(__file__).parent / "figures"


# ============================================================
# DATA CLASSES
# ============================================================


@dataclass
class MarketAnalysis:
    """Container for market analysis results."""

    symbol: str
    returns: np.ndarray
    energy: np.ndarray
    gradient: np.ndarray
    correlation: float
    p_value: float
    power_law_alpha: Optional[float] = None


# ============================================================
# MARKET ENERGY DEFINITIONS
# ============================================================


def compute_market_energy_v1(prices: pd.Series, window: int = 20) -> pd.Series:
    """
    Market Energy Definition 1: Deviation from moving average

    E(t) = [P(t) - MA(t)]² / σ²

    Interpretation: "Stress" from being away from trend
    """
    ma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()

    # Normalized deviation squared (like potential energy)
    energy = ((prices - ma) / std) ** 2

    return energy


def compute_market_energy_v2(prices: pd.Series, window: int = 20) -> pd.Series:
    """
    Market Energy Definition 2: Cumulative volatility

    E(t) = Σ (log returns)² over window

    Interpretation: Accumulated "kinetic energy" of market
    """
    log_returns = np.log(prices / prices.shift(1))
    energy = log_returns.rolling(window=window).apply(lambda x: np.sum(x**2))

    return energy


def compute_market_energy_v3(prices: pd.Series, window: int = 5) -> pd.Series:
    """
    Market Energy Definition 3: Price momentum

    E(t) = -log(P(t)/P(t-n))

    Interpretation: Like gravitational potential (higher = more potential to fall)
    """
    energy = -np.log(prices / prices.shift(window))

    return energy


# ============================================================
# F = -∇E ANALYSIS
# ============================================================


def compute_gradient(energy: pd.Series, dt: int = 1) -> pd.Series:
    """
    Compute gradient of energy: ∇E = dE/dt
    """
    return energy.diff(dt) / dt


def compute_returns(prices: pd.Series, dt: int = 1) -> pd.Series:
    """
    Compute returns (our "Force" analog)

    F = log(P(t+dt)/P(t)) = log returns
    """
    return np.log(prices / prices.shift(dt))


def test_force_gradient_relationship(
    returns: np.ndarray, gradient: np.ndarray
) -> Tuple[float, float, float, float]:
    """
    Test: F = -β × ∇E

    If UET-like physics applies:
    - Returns should be negatively correlated with energy gradient
    - β should be positive (move toward lower energy)

    Returns: (correlation, p_value, slope, intercept)
    """
    # Remove NaN
    mask = ~(np.isnan(returns) | np.isnan(gradient))
    r = returns[mask]
    g = gradient[mask]

    if len(r) < 10:
        return 0, 1, 0, 0

    # Correlation
    corr, p_value = stats.pearsonr(r, g)

    # Linear fit: F = β × ∇E + c
    slope, intercept, _, _, _ = stats.linregress(g, r)

    return corr, p_value, slope, intercept


# ============================================================
# POWER LAW ANALYSIS
# ============================================================


def fit_power_law(returns: np.ndarray, bins: int = 50) -> Tuple[float, float]:
    """
    Fit power law to return distribution: P(|r| > x) ~ x^(-α)

    Econophysics finding: α ≈ 3 (inverse cubic law)
    """
    # Use absolute returns
    abs_returns = np.abs(returns[~np.isnan(returns)])
    abs_returns = abs_returns[abs_returns > 0]

    # Sort for CCDF
    sorted_returns = np.sort(abs_returns)[::-1]
    ccdf = np.arange(1, len(sorted_returns) + 1) / len(sorted_returns)

    # Fit power law in log-log
    # Only use tail (top 10%)
    n_tail = len(sorted_returns) // 10
    x = np.log10(sorted_returns[:n_tail])
    y = np.log10(ccdf[:n_tail])

    slope, intercept, _, _, _ = stats.linregress(x, y)

    # α = -slope (since P ~ x^(-α) means log P ~ -α log x)
    alpha = -slope

    return alpha, intercept


# ============================================================
# MAIN ANALYSIS
# ============================================================


def analyze_symbol(symbol: str, data_dir: Path) -> Optional[MarketAnalysis]:
    """Full econophysics analysis for one symbol."""

    file_path = data_dir / f"{symbol}.csv"

    if not file_path.exists():
        print(f"⚠️  No data for {symbol}")
        return None

    # Load data - yfinance creates multi-level headers, skip first 2 rows
    try:
        df = pd.read_csv(file_path, skiprows=2, header=0)

        # First column is Date
        df.columns = ["Date"] + list(df.columns[1:])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")

        # Convert all columns to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    except Exception as e:
        print(f"⚠️  Error loading {symbol}: {e}")
        return None

    # Find Close column (first numeric column after Date)
    if df.empty or len(df.columns) == 0:
        print(f"⚠️  No data columns for {symbol}")
        return None

    # Use first column as Close price
    prices = df.iloc[:, 0].dropna()

    if len(prices) < 100:
        print(f"⚠️  Not enough data for {symbol}")
        return None

    print(f"\n📈 Analyzing {symbol} ({len(prices)} data points)...")

    # Compute returns (Force analog)
    returns = compute_returns(prices)

    # Try all 3 energy definitions and pick the best one
    energy_funcs = [
        ("v1-Deviation", compute_market_energy_v1),
        ("v2-Volatility", compute_market_energy_v2),
        ("v3-Momentum", compute_market_energy_v3),
    ]

    best_corr = 0
    best_result = None
    best_name = ""

    for name, energy_func in energy_funcs:
        try:
            energy = energy_func(prices)
            gradient = compute_gradient(energy)

            corr, p_value, slope, _ = test_force_gradient_relationship(
                returns.values, gradient.values
            )

            # We want the most NEGATIVE correlation
            if corr < best_corr or best_result is None:
                best_corr = corr
                best_result = (energy, gradient, corr, p_value, slope)
                best_name = name
        except:
            continue

    if best_result is None:
        print(f"   ⚠️ Analysis failed")
        return None

    energy, gradient, corr, p_value, slope = best_result

    print(f"   Best energy: {best_name}")
    print(f"   Correlation (F vs ∇E): {corr:.4f} (p = {p_value:.2e})")
    print(f"   Slope: {slope:.6f}")

    # UET prediction: slope should be NEGATIVE (F = -∇E)
    if slope < 0 and p_value < 0.05:
        print(f"   ✅ CONSISTENT with F = -∇E (slope < 0, significant)")
    elif p_value >= 0.05:
        print(f"   ⚠️  Not significant (p > 0.05)")
    else:
        print(f"   ❌ OPPOSITE sign (slope > 0)")

    # Power law fit
    alpha, _ = fit_power_law(returns.values)
    print(f"   Power law exponent α: {alpha:.2f} (expected: ~3)")

    return MarketAnalysis(
        symbol=symbol,
        returns=returns.values,
        energy=energy.values,
        gradient=gradient.values,
        correlation=corr,
        p_value=p_value,
        power_law_alpha=alpha,
    )


def run_full_analysis():
    """Run analysis on all available data."""

    print("\n" + "🏦" * 30)
    print("   ECONOPHYSICS: F = -∇E ANALYSIS")
    print("🏦" * 30)

    # Check data directory
    if not DATA_DIR.exists():
        print(f"\n❌ Data directory not found: {DATA_DIR}")
        print("   Run download_market_data.py first!")
        return

    # Find all CSV files
    csv_files = list(DATA_DIR.glob("*.csv"))

    if not csv_files:
        print(f"\n❌ No CSV files found in {DATA_DIR}")
        return

    print(f"\n📁 Found {len(csv_files)} data files")

    # Analyze each
    results = []
    for csv_file in csv_files:
        symbol = csv_file.stem
        result = analyze_symbol(symbol, DATA_DIR)
        if result:
            results.append(result)

    if not results:
        print("\n❌ No valid analysis results")
        return

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY: F = -∇E Test Results")
    print("=" * 70)

    print(f"\n{'Symbol':<10} {'Corr(F,∇E)':<12} {'p-value':<12} {'α (power)':<10} {'F=-∇E?':<10}")
    print("-" * 60)

    n_consistent = 0
    for r in results:
        consistent = "✅ Yes" if (r.correlation < 0 and r.p_value < 0.05) else "❌ No"
        if r.correlation < 0 and r.p_value < 0.05:
            n_consistent += 1

        print(
            f"{r.symbol:<10} {r.correlation:>+.4f}    {r.p_value:<.2e}    {r.power_law_alpha:>5.2f}     {consistent}"
        )

    print("-" * 60)
    print(f"\n✅ {n_consistent}/{len(results)} symbols consistent with F = -∇E")

    # Average power law exponent
    alphas = [r.power_law_alpha for r in results if r.power_law_alpha]
    if alphas:
        print(f"📈 Average power law α = {np.mean(alphas):.2f} ± {np.std(alphas):.2f}")
        print(f"   (Econophysics predicts α ≈ 3, 'inverse cubic law')")

    # Create figures
    create_summary_figures(results)

    return results


# ============================================================
# VISUALIZATION
# ============================================================


def create_summary_figures(results: list):
    """Create summary plots."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: Correlation distribution
    ax = axes[0, 0]
    corrs = [r.correlation for r in results]
    colors = ["green" if c < 0 else "red" for c in corrs]
    ax.bar(range(len(results)), corrs, color=colors, alpha=0.7)
    ax.set_xticks(range(len(results)))
    ax.set_xticklabels([r.symbol for r in results], rotation=45, ha="right")
    ax.axhline(0, color="black", linestyle="--")
    ax.set_ylabel("Correlation (F vs ∇E)")
    ax.set_title("F = -∇E Test: Correlation by Symbol")
    ax.set_ylim(-0.5, 0.5)

    # Plot 2: Power law exponents
    ax = axes[0, 1]
    alphas = [r.power_law_alpha for r in results]
    ax.bar(range(len(results)), alphas, color="steelblue", alpha=0.7)
    ax.set_xticks(range(len(results)))
    ax.set_xticklabels([r.symbol for r in results], rotation=45, ha="right")
    ax.axhline(3, color="red", linestyle="--", label="Predicted α=3")
    ax.set_ylabel("Power law exponent α")
    ax.set_title("Return Distribution: Power Law Fit")
    ax.legend()

    # Plot 3: p-values
    ax = axes[1, 0]
    pvals = [r.p_value for r in results]
    ax.bar(range(len(results)), np.log10(pvals), color="purple", alpha=0.7)
    ax.set_xticks(range(len(results)))
    ax.set_xticklabels([r.symbol for r in results], rotation=45, ha="right")
    ax.axhline(np.log10(0.05), color="red", linestyle="--", label="p=0.05")
    ax.set_ylabel("log₁₀(p-value)")
    ax.set_title("Statistical Significance")
    ax.legend()

    # Plot 4: Scatter of one example
    ax = axes[1, 1]
    if results:
        r = results[0]  # Use first result
        mask = ~(np.isnan(r.returns) | np.isnan(r.gradient))
        ax.scatter(r.gradient[mask][::10], r.returns[mask][::10], alpha=0.3, s=5, color="blue")
        ax.axhline(0, color="gray", linestyle="-", alpha=0.3)
        ax.axvline(0, color="gray", linestyle="-", alpha=0.3)
        ax.set_xlabel("∇E (Energy Gradient)")
        ax.set_ylabel("F (Returns)")
        ax.set_title(f"{r.symbol}: Force vs Energy Gradient")
        ax.set_xlim(-5, 5)
        ax.set_ylim(-0.1, 0.1)

    plt.suptitle("Econophysics: F = -∇E Analysis", fontsize=14, fontweight="bold")
    plt.tight_layout()

    output = FIGURES_DIR / "econophysics_summary.png"
    plt.savefig(output, dpi=150, bbox_inches="tight")
    print(f"\n📊 Figure saved: {output}")
    plt.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_full_analysis()
