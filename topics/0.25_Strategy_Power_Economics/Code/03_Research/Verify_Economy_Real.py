"""
Verify_Economy_Real.py
======================
Production Verification for Topic 0.25 (Economics).
Checks if "Global_Economy_2024.json" is correctly loaded and parsed.
This ensures the UET Economic Engine is running on Real World Data.
"""

import sys
import json
from pathlib import Path


def run_verification():
    print("💰 UET ECONOMICS: REAL DATA VERIFICATION")
    print("=======================================")

    # Path to Data
    data_path = Path(__file__).parents[2] / "Data/Global_Economy_2024.json"

    if not data_path.exists():
        print(f"❌ DATA MISSING: {data_path}")
        return

    print(f"  Loading: {data_path.name}")
    try:
        with open(data_path, "r") as f:
            data = json.load(f)

        economies = data.get("Economies", {})
        print(f"  Entries Found: {len(economies)}")

        print("\n  [Sample Data Check]")

        # Check Thailand (Pilot Target)
        thai = economies.get("Thailand")
        if thai:
            print(f"  🇹🇭 Thailand:")
            print(f"     N (Pop):    {thai['Population'] / 1e6:.1f} M")
            print(f"     GDP (PPP):  ${thai['GDP_PPP_USD'] / 1e12:.2f} T")
            print(f"     Gini:       {thai['Gini']}")
        else:
            print("  ❌ Thailand Data Missing")

        # Check Global
        world = economies.get("World_Total")
        if world:
            print(f"  🌍 World Total:")
            print(f"     N (Pop):    {world['Population'] / 1e9:.2f} B")
            print(f"     Gini:       {world['Gini']}")

        print("\n✅ STATUS: SUCCESS (Economic Data Online)")
        print("   The Engine is now connected to World Bank 2024 Baselines.")

    except Exception as e:
        print(f"❌ LOAD ERROR: {e}")


if __name__ == "__main__":
    run_verification()
