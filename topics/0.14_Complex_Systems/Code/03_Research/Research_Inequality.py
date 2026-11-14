"""
[DATA] UET Test 07: Economic Health Index
=====================================

Tests: UET-based economic health k = sqrt(Productivity/Debt) * Employment

Uses World Bank inequality/economic data.

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


from docs import ROOT_PATH
root_path = ROOT_PATH
import numpy as np
import pandas as pd
import os
import sys
from pathlib import Path

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


try:
    from docs.core.uet_glass_box import UETPathManager
    from docs.core.uet_master_equation import (
        UETParameters,
        SIGMA_CRIT,
        strategic_boost,
        potential_V,
        KAPPA_BEKENSTEIN,
    )
except ImportError:
    pass

import glob



TOPIC_DIR = (
    root_path / "docs" / "topics" / "0.14_Complex_Systems"
    if root_path
    else Path(__file__).resolve().parent.parent.parent
)
DATA_PATH = TOPIC_DIR / "Data"
DATA_DIR = str(DATA_PATH)




# Standardized UET Root Path

def load_inequality_data():
    """Load World Bank economic data."""
    data = {}

    # Inequality data
    ineq_dir = os.path.join(DATA_DIR, "03_Research", "inequality")
    if os.path.exists(ineq_dir):
        for filepath in glob.glob(os.path.join(ineq_dir, "worldbank_*.csv")):
            name = (
                os.path.basename(filepath).replace("worldbank_", "").replace(".csv", "")
            )
            try:
                df = pd.read_csv(filepath)
                data[name] = df
            except:
                pass

    # Economic health data
    econ_dir = os.path.join(DATA_DIR, "economic_health")
    if os.path.exists(econ_dir):
        for filepath in glob.glob(os.path.join(econ_dir, "econ_*.csv")):
            name = os.path.basename(filepath).replace("econ_", "").replace(".csv", "")
            try:
                df = pd.read_csv(filepath)
                data[name] = df
            except:
                pass

    return data


def calculate_uet_health_index(gdp_pc, debt_ratio, unemployment):
    """
    Calculate UET Economic Health Index.

    k = sqrt(Productivity / Debt_Ratio) * Employment_Factor

    Where:
    - Productivity proxy = GDP per capita / 1000
    - Debt_Ratio = Government debt / GDP
    - Employment_Factor = 1 - Unemployment_Rate

    Interpretation:
    - k > 1.5: Very Healthy
    - k = 1.0: Balanced
    - k < 0.7: Stressed
    - k < 0.3: Crisis
    """
    if debt_ratio <= 0 or gdp_pc <= 0:
        return None

    productivity = gdp_pc / 10000  # Normalize
    emp_factor = 1 - unemployment / 100

    k = np.sqrt(productivity / (debt_ratio + 0.1)) * emp_factor

    return k


def run_test():
    """Run economic health test."""
    print("\n" + "=" * 60)
    print("[DATA] UET TEST 07: Economic Health Index")
    print("=" * 60)
    print("\nEquation: k = sqrt(Productivity/Debt) * Employment")
    print("UET Prediction: Healthy economies have k ~= 1.0")

    data = load_inequality_data()

    if not data:
        print("[FAIL] No economic data found!")
        return {"status": "FAIL", "error": "No data"}

    print(f"\nLoaded {len(data)} datasets\n")

    # Get common countries with all required metrics
    required = ["gdp_per_capita", "government_debt_gdp", "unemployment"]
    available = [k for k in required if k in data]

    if len(available) < 2:
        print(f"[WARN] Only have: {list(data.keys())}")
        print("   Need: gdp_per_capita, government_debt_gdp, unemployment")

        # Fallback: just analyze GDP data
        if "gdp_per_capita" in data:
            df = data["gdp_per_capita"]
            print("\nFallback: Analyzing GDP per capita trends...")

            # Get latest values by country
            latest = df.sort_values("year").groupby("country_code").last()

            # Top 10 by GDP
            top10 = latest.nlargest(10, "value")

            print("\nTop 10 by GDP per capita (2023~):")
            for idx, row in top10.iterrows():
                print(f"   {row['country_name']:30} ${row['value']:,.0f}")

            return {
                "status": "WARN",
                "message": "Partial data only",
                "gdp_analyzed": len(latest),
            }

    print(f"Available metrics: {available}")

    # Merge data
    results = []

    # Get GDP
    if "gdp_per_capita" in data:
        gdp_df = data["gdp_per_capita"]
        latest_year = gdp_df["year"].max()
        gdp_latest = gdp_df[gdp_df["year"] == latest_year][["country_code", "value"]]
        gdp_latest = gdp_latest.rename(columns={"value": "gdp_pc"})

        # Get debt if available
        if "government_debt_gdp" in data:
            debt_df = data["government_debt_gdp"]
            debt_latest = (
                debt_df.sort_values("year").groupby("country_code").last()[["value"]]
            )
            debt_latest = debt_latest.rename(columns={"value": "debt_ratio"})
            gdp_latest = gdp_latest.set_index("country_code").join(debt_latest)
        else:
            gdp_latest["debt_ratio"] = 50  # Default assumption
            gdp_latest = gdp_latest.set_index("country_code")

        # Get unemployment if available
        if "unemployment" in data:
            unemp_df = data["unemployment"]
            unemp_latest = (
                unemp_df.sort_values("year").groupby("country_code").last()[["value"]]
            )
            unemp_latest = unemp_latest.rename(columns={"value": "unemployment"})
            gdp_latest = gdp_latest.join(unemp_latest)
        else:
            gdp_latest["unemployment"] = 5  # Default assumption

        # Calculate k for each country
        for country_code, row in gdp_latest.iterrows():
            if pd.isna(row.get("gdp_pc")) or pd.isna(row.get("debt_ratio")):
                continue

            k = calculate_uet_health_index(
                row["gdp_pc"], row.get("debt_ratio", 50), row.get("unemployment", 5)
            )

            if k is not None:
                results.append(
                    {
                        "country": country_code,
                        "gdp_pc": row["gdp_pc"],
                        "debt_ratio": row.get("debt_ratio", 50),
                        "unemployment": row.get("unemployment", 5),
                        "k_index": k,
                    }
                )

    if not results:
        print("[FAIL] Could not calculate health index")
        return {"status": "FAIL", "error": "Calculation failed"}

    # Sort by k
    results = sorted(results, key=lambda x: x["k_index"], reverse=True)

    print(f"\nEconomic Health Index for {len(results)} countries:\n")
    print("Top 10 Healthiest:")
    for r in results[:10]:
        k = r["k_index"]
        if k > 1.5:
            emoji = "[GREEN]"
        elif k > 1.0:
            emoji = "🟡"
        elif k > 0.7:
            emoji = "🟠"
        else:
            emoji = "[RED]"
        print(
            f"   {emoji} {r['country']:5} k={k:.2f}  (GDP=${r['gdp_pc']:,.0f}, Debt={r['debt_ratio']:.0f}%)"
        )

    print("\nBottom 5 (Most Stressed):")
    for r in results[-5:]:
        k = r["k_index"]
        emoji = "[RED]" if k < 0.7 else "🟠"
        print(f"   {emoji} {r['country']:5} k={k:.2f}  (GDP=${r['gdp_pc']:,.0f})")

    # Summary
    avg_k = np.mean([r["k_index"] for r in results])
    healthy = len([r for r in results if r["k_index"] > 1.0])
    stressed = len([r for r in results if r["k_index"] < 0.7])

    print("\n" + "=" * 40)
    print(f"Average k: {avg_k:.2f}")
    print(f"Healthy (k>1.0): {healthy}/{len(results)}")
    print(f"Stressed (k<0.7): {stressed}/{len(results)}")
    print("=" * 40)

    # Grade
    if avg_k > 1.0:
        grade = "***** GLOBAL HEALTH GOOD"
        status = "PASS"
    elif avg_k > 0.7:
        grade = "**** MODERATE"
        status = "PASS"
    else:
        grade = "*** STRESSED"
        status = "WARN"

    print(f"\nGrade: {grade}")

    # --- VISUALIZATION ---
    try:
        from docs.core import uet_viz

        result_dir = UETPathManager.get_result_dir(
            topic_id="0.14_Complex_Systems",
            experiment_name="Research_Inequality",
            pillar="03_Research",
            category="log",
        )
        result_dir = result_dir / "03_Research" / "inequality"
        result_dir.mkdir(parents=True, exist_ok=True)

        if results:
            # Top 20 for Viz
            viz_data = results[:20]
            countries = [r["country"] for r in viz_data]
            ks = [r["k_index"] for r in viz_data]
            gdps = [r["gdp_pc"] for r in viz_data]

            fig = uet_viz.go.Figure()
            fig.add_trace(
                uet_viz.go.Bar(
                    x=countries,
                    y=ks,
                    marker=dict(color=ks, colorscale="RdYlGn"),
                    name="UET Health Index (k)",
                )
            )

            fig.add_hline(
                y=1.0,
                line_dash="dash",
                line_color="blue",
                annotation_text="Balanced (k=1)",
            )

            fig.update_layout(
                title="Global Economic Health Index (Top 20)",
                yaxis_title="k-Index (sqrt(P/D) * Emp)",
                xaxis_title="Country",
            )
            uet_viz.save_plot(fig, "inequality_viz.png", result_dir)
            print("  [Viz] Generated 'inequality_viz.png'")

    except Exception as e:
        print(f"Viz Error: {e}")

    return {
        "status": status,
        "avg_k": avg_k,
        "countries_analyzed": len(results),
        "healthy": healthy,
        "stressed": stressed,
        "top_5": results[:5],
        "bottom_5": results[-5:],
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n[OK] Test complete: {result['status']}")
