"""
Data Loader: World Economic Indicators
======================================
Topic: 0.25 Strategy, Power, and Economics
Source: World Bank / IMF (2024 Estimates)
Target: Real-world baselines for Economic Equilibrium Analysis.

Generates: 'Global_Economy_2024.json'
Metrics:
- Population (N)
- GDP PPP (Total Wealth)
- Gini Coefficient (Inequality)
"""

import json
from pathlib import Path


def fetch_economic_data():
    print("📥 Loading World Economic Data (World Bank/IMF 2024)...")

    # Representative Economies for UET Equilibrium Testing
    # Mix of High/Low Gini and High/Low GDP
    economies = {
        "World_Total": {
            "Population": 8.1e9,
            "GDP_PPP_USD": 185e12,
            "Gini": 62.0,  # Global Wealth Inequality approx
            "Note": "Earth System Limit",
        },
        "USA": {
            "Population": 341e6,
            "GDP_PPP_USD": 28.7e12,
            "Gini": 41.5,
            "Type": "Developed / High Inequality",
        },
        "China": {
            "Population": 1.41e9,
            "GDP_PPP_USD": 35.2e12,
            "Gini": 37.1,
            "Type": "Developed / State Controlled",
        },
        "Thailand": {
            "Population": 71.8e6,
            "GDP_PPP_USD": 1.58e12,
            "Gini": 35.0,
            "Type": "Developing / UET Pilot Target",
        },
        "Norway": {
            "Population": 5.5e6,
            "GDP_PPP_USD": 0.45e12,
            "Gini": 27.7,
            "Type": "Developed / Low Inequality (Ideal?)",
        },
        "South_Africa": {
            "Population": 60.4e6,
            "GDP_PPP_USD": 0.99e12,
            "Gini": 63.0,
            "Type": "Developing / Extreme Inequality",
        },
    }

    output_data = {
        "Source": "UET Economic Audit 2026 (World Bank/IMF Ref)",
        "Metric_Definitions": {
            "Population": "Total Human Nodes (N)",
            "GDP_PPP": "Total Resource Throughput (Energy)",
            "Gini": "Entropy of Distribution (0=Perfect Order, 100=Max Entropy)",
        },
        "Economies": economies,
    }

    output_dir = Path(__file__).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "Global_Economy_2024.json"

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"✅ Production Economic Data Saved: {output_path}")
    print(f"   Economies Tracked: {len(economies)}")


if __name__ == "__main__":
    fetch_economic_data()
