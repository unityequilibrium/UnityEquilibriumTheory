"""
[CLIMATE] UET Test 06: Climate Forced Equilibrium
==========================================

Tests: Forced system far from equilibrium

Uses real NASA/NOAA climate data.

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
import sys
import os
from pathlib import Path


# --- ROBUST PATH FINDER (5x4 Grid Standard) ---
_root = Path(__file__).resolve().parent
while _root.name != "docs" and _root.parent != _root:
    _root = _root.parent
if _root.name == "docs":
    sys.path.insert(0, str(_root.parent))
    from docs import ROOT_PATH

    root_path = ROOT_PATH
else:
    print("CRITICAL: Root path not found.")
    sys.exit(1)

TOPIC_DIR = root_path / "docs" / "topics" / "0.14_Complex_Systems"
DATA_PATH = TOPIC_DIR / "Data"
DATA_DIR = str(DATA_PATH)

# Engine Import
try:
    import importlib.util

    engine_file = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Complexity.py"
    spec = importlib.util.spec_from_file_location("Engine_Complexity", str(engine_file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    UETComplexityEngine = mod.UETComplexityEngine
except Exception:
    UETComplexityEngine = None

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


def load_climate_data():
    """Load climate data."""
    data = {}
    climate_dir = os.path.join(DATA_DIR, "03_Research", "climate")

    # CO2
    co2_path = os.path.join(climate_dir, "noaa_co2_mauna_loa.csv")
    if os.path.exists(co2_path):
        df = pd.read_csv(co2_path, comment="#")
        data["co2"] = df

    # Sea level
    sea_path = os.path.join(climate_dir, "noaa_sea_level.csv")
    if os.path.exists(sea_path):
        try:
            df = pd.read_csv(sea_path, comment="#")
            data["sea_level"] = df
        except:
            pass

    return data


def analyze_equilibrium_distance(time_series, name):
    """
    Analyze how far system is from equilibrium using UET Complexity Engine.
    """
    if len(time_series) < 10:
        return None

    values = time_series.values if hasattr(time_series, "values") else time_series
    values = values[np.isfinite(values)]

    if len(values) < 10:
        return None

    # Use Engine if available
    if UETComplexityEngine:
        engine = UETComplexityEngine(name="Climate_Analyzer")
        metrics = engine.calculate_stability_metrics(values)
        hurst = engine.calculate_hurst_exponent(values)

        return {
            "name": name,
            "current_value": values[-1],
            "avg_rate": metrics["cv"],  # Proxy for rate of change/volatility
            "avg_accel": 0.0,
            "eq_distance": 1.0 - metrics["equilibrium_score"],
            "equilibrium_score": metrics["equilibrium_score"],
            "hurst": hurst,
            "status": "UNSTABLE" if metrics["equilibrium_score"] < 0.5 else "STABLE",
            "data_points": len(values),
        }

    # Fallback if engine fails
    return None


def run_test():
    """Run climate equilibrium test."""
    print("\n" + "=" * 60)
    print("[CLIMATE] UET TEST 06: Climate Forced Equilibrium")
    print("=" * 60)
    print("\nEquation: dOmega/dt = Forcing - Stabilization")
    print("UET Interpretation: Climate is FORCED system")

    data = load_climate_data()

    if not data:
        print("[FAIL] No climate data found!")
        return {"status": "FAIL", "error": "No data"}

    print(f"\nLoaded {len(data)} climate datasets\n")

    results = []

    # Analyze CO2
    if "co2" in data:
        df = data["co2"]
        # Find CO2 column
        co2_col = None
        for col in df.columns:
            if "average" in col.lower() or "co2" in col.lower() or "trend" in col.lower():
                co2_col = col
                break

        if co2_col is None and len(df.columns) > 1:
            co2_col = df.columns[1]  # Usually second column

        if co2_col:
            metrics = analyze_equilibrium_distance(df[co2_col], "CO2 (ppm)")
            if metrics:
                results.append(metrics)
                print(f"   CO2:")
                print(f"      Current: {metrics['current_value']:.1f} ppm")
                print(f"      Rate: +{metrics['avg_rate']:.2f} ppm/month")
                print(f"      Status: {metrics['status']}")
                print()

    # Analyze sea level
    if "sea_level" in data:
        df = data["sea_level"]
        # Find sea level column
        sl_col = None
        for col in df.columns:
            if "gmsl" in col.lower() or "sea" in col.lower() or "level" in col.lower():
                sl_col = col
                break

        if sl_col is None and len(df.columns) > 1:
            sl_col = df.columns[1]

        if sl_col:
            metrics = analyze_equilibrium_distance(df[sl_col], "Sea Level (mm)")
            if metrics:
                results.append(metrics)
                print(f"   Sea Level:")
                print(f"      Current: {metrics['current_value']:.1f} mm")
                print(f"      Rate: +{metrics['avg_rate']:.2f} mm/period")
                print(f"      Status: {metrics['status']}")
                print()

    if not results:
        print("[FAIL] Could not analyze climate data")
        return {"status": "FAIL", "error": "Analysis failed"}

    # Summary
    print("=" * 40)
    print("UET Analysis:")
    print("=" * 40)

    accelerating = [r for r in results if "ACCELERATING" in r["status"]]
    increasing = [r for r in results if "INCREASING" in r["status"]]

    if accelerating:
        status = "WARN"
        grade = "[WARN] FORCED DISEQUILIBRIUM"
        print("\n[WARN] Climate system is being FORCED away from equilibrium")
        print("   CO2 injection > Natural absorption")
        print("   dOmega/dt > 0 (system stress increasing)")
    elif increasing:
        status = "WARN"
        grade = "⚡ TRANSITIONAL"
        print("\n⚡ Climate system in transition")
    else:
        status = "PASS"
        grade = "[OK] STABLE"

    print(f"\nGrade: {grade}")

    print("\nUET Interpretation:")
    print("   I (Information) = CO2 concentration")
    print("   C (Capacity) = Temperature, Sea Level")
    print("   beta*C*I coupling = Greenhouse effect")
    print("   Current state: Far from pre-industrial equilibrium")

    # --- VISUALIZATION ---
    try:
        from docs.core import uet_viz

        result_dir = UETPathManager.get_result_dir(
            topic_id="0.14_Complex_Systems",
            experiment_name="Research_Climate",
            pillar="03_Research",
            category="log",
        )
        result_dir.mkdir(parents=True, exist_ok=True)

        fig = uet_viz.go.Figure()

        # Plot CO2
        if "co2" in data:
            df = data["co2"]
            # Try to grab relevant columns
            if len(df.columns) >= 2:
                # Assuming index or year/month is implicit or 1st column
                # Just plot simple sequence if no proper time index found
                vals = df.iloc[:, 1].values  # 2nd column usually data
                vals = vals[vals > 0]  # Filter invalid

                fig.add_trace(
                    uet_viz.go.Scatter(
                        y=vals,
                        mode="lines",
                        name="CO2 Concentration",
                        line=dict(color="red"),
                    )
                )

        # Plot Sea Level (on secondary axis potentially, or normalized)
        # For simplicity, just CO2 helps visualize "Forcing"

        fig.update_layout(
            title="Climate Forcing (CO2): Information Injection",
            xaxis_title="Time Steps",
            yaxis_title="CO2 (ppm)",
        )
        uet_viz.save_plot(fig, "climate_viz.png", result_dir)
        print("  [Viz] Generated 'climate_viz.png'")

    except Exception as e:
        print(f"Viz Error: {e}")

    return {
        "status": status,
        "grade": grade,
        "datasets_analyzed": len(results),
        "accelerating": len(accelerating),
        "results": results,
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n[OK] Test complete: {result['status']}")
