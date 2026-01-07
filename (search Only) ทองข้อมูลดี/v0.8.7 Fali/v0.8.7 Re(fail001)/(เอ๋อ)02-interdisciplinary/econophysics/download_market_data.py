#!/usr/bin/env python3
"""
🏦 ECONOPHYSICS: Market Data Downloader
========================================

Downloads real stock market data for econophysics analysis.
Uses Yahoo Finance via yfinance package.

Data:
- S&P 500 (^GSPC)
- NASDAQ (^IXIC)
- Dow Jones (^DJI)
- Individual stocks (AAPL, GOOGL, MSFT, etc.)

Author: UET Research Team
Date: 2025-12-28
"""

import os
from datetime import datetime
from pathlib import Path

try:
    import yfinance as yf

    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not installed. Run: pip install yfinance")

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

# Major indices
INDICES = {
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
    "VIX": "^VIX",  # Volatility index
}

# Individual stocks (diverse sectors) - ticker as value
STOCKS = {
    "AAPL": "AAPL",
    "GOOGL": "GOOGL",
    "MSFT": "MSFT",
    "AMZN": "AMZN",
    "TSLA": "TSLA",
    "JPM": "JPM",
    "XOM": "XOM",
    "JNJ": "JNJ",
}

# Time period
START_DATE = "2010-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

# Output directory
OUTPUT_DIR = Path(__file__).parent / "market_data"


# ============================================================
# DATA DOWNLOAD
# ============================================================


def download_market_data(symbols: dict, start: str, end: str, output_dir: Path):
    """Download market data for given symbols."""

    if not YFINANCE_AVAILABLE:
        print("❌ yfinance not available. Cannot download data.")
        return {}

    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    for name, ticker in symbols.items():
        print(f"📥 Downloading {name} ({ticker})...")

        try:
            # Download data
            data = yf.download(ticker, start=start, end=end, progress=False)

            if data.empty:
                print(f"   ⚠️ No data for {ticker}")
                continue

            # Save to CSV
            output_file = output_dir / f"{name}.csv"
            data.to_csv(output_file)

            print(f"   ✅ Saved {len(data)} rows → {output_file.name}")

            results[name] = {
                "ticker": ticker,
                "rows": len(data),
                "start": data.index[0].strftime("%Y-%m-%d"),
                "end": data.index[-1].strftime("%Y-%m-%d"),
                "file": str(output_file),
            }

        except Exception as e:
            print(f"   ❌ Error: {e}")

    return results


def create_summary(results: dict, output_dir: Path):
    """Create summary file of downloaded data."""

    summary_file = output_dir / "SUMMARY.md"

    lines = [
        "# Market Data Summary",
        f"\nDownloaded: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"\nPeriod: {START_DATE} to {END_DATE}",
        "\n## Files\n",
        "| Symbol | Ticker | Rows | Start | End |",
        "|--------|--------|------|-------|-----|",
    ]

    for name, info in results.items():
        lines.append(
            f"| {name} | {info['ticker']} | {info['rows']} | {info['start']} | {info['end']} |"
        )

    lines.append("\n---\n")
    lines.append("*Data from Yahoo Finance via yfinance*")

    with open(summary_file, "w") as f:
        f.write("\n".join(lines))

    print(f"\n📄 Summary saved: {summary_file}")


# ============================================================
# MAIN
# ============================================================


def main():
    print("\n" + "🏦" * 30)
    print("   ECONOPHYSICS DATA DOWNLOADER")
    print("🏦" * 30)

    print(f"\n📅 Period: {START_DATE} to {END_DATE}")
    print(f"📁 Output: {OUTPUT_DIR}")

    # Download indices
    print("\n" + "=" * 50)
    print("MARKET INDICES")
    print("=" * 50)
    index_results = download_market_data(INDICES, START_DATE, END_DATE, OUTPUT_DIR)

    # Download stocks
    print("\n" + "=" * 50)
    print("INDIVIDUAL STOCKS")
    print("=" * 50)
    stock_results = download_market_data(STOCKS, START_DATE, END_DATE, OUTPUT_DIR)

    # Combine results
    all_results = {**index_results, **stock_results}

    # Create summary
    create_summary(all_results, OUTPUT_DIR)

    # Summary stats
    total_rows = sum(r["rows"] for r in all_results.values())
    print("\n" + "=" * 50)
    print(f"✅ Downloaded {len(all_results)} symbols")
    print(f"📊 Total: {total_rows:,} data points")
    print("=" * 50)


if __name__ == "__main__":
    main()
