import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

"""
UET ECONOMICS APPLICATION: VALUE VS PRICE (BUBBLE DETECTION)
------------------------------------------------------------
Goal: Detect the Dot Com Bubble (2000) using UET "True Value" Metric.
Data File: research_v3/01_data/sp500_bubble.csv
"""


def load_data():
    file_path = os.path.join("research_v3", "01_data", "sp500_bubble.csv")
    print(f"Loading economic data from: {file_path}")

    # Load with Pandas, skipping comment lines
    try:
        df = pd.read_csv(file_path, comment="#")
        # Clean up column names (strip whitespace)
        df.columns = df.columns.str.strip()
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def calculate_uet_value(df, alpha=0.5):
    """
    UET Value Logic:
    True Value (V) grows with Earnings (I) but detects 'Hype' (High C/Volume).

    Formula: V = Earnings * (Earnings / Volume)^alpha
    Idea: If Volume (Hype) > Earnings, the 'Quality' of the energy is lower.
    """
    # Normalize for calculation scaling
    E = df["Earnings"]
    C = df["Volume_Billions"]

    # UET Metric
    # If C is excessively high compared to E, Value is suppressed (Hype Discount)
    # If E is high and C is moderate, Value is maximal (Solid Growth)

    efficiency = E / C
    V_uet = E * np.power(efficiency, alpha)

    return V_uet


def run_simulation():
    print("Running Economics Simulation: Dot Com Bubble Test...")

    # 1. Load Real Data
    df = load_data()
    if df is None:
        return None

    # 2. Calculate UET True Value
    df["V_uet"] = calculate_uet_value(df)

    # 3. Scaling for comparison (Price vs Value)
    # We calibrate V_uet to match Price at the start (1995) to see divergence later
    scale_factor = df["SP500_Price"].iloc[0] / df["V_uet"].iloc[0]
    df["V_uet_scaled"] = df["V_uet"] * scale_factor

    # 4. Detect Bubble (Divergence)
    df["Bubble_Size"] = df["SP500_Price"] - df["V_uet_scaled"]

    print("\nSimulation Results (Peak Bubble):")
    # Find row with max bubble size
    peak_idx = df["Bubble_Size"].idxmax()
    peak_bubble = df.loc[peak_idx]

    print(f"Date: {peak_bubble['Date'].strftime('%Y-%m-%d')}")
    print(f"Price: {peak_bubble['SP500_Price']:.2f}")
    print(f"True Value (UET): {peak_bubble['V_uet_scaled']:.2f}")
    print(f"Bubble Gap: {peak_bubble['Bubble_Size']:.2f}")

    return df


def plot_results(df):
    if df is None:
        return

    output_dir = "research_v3/04_analysis/results"
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(12, 6))

    # Plot Price (Hype)
    plt.plot(df["Date"], df["SP500_Price"], "r-o", linewidth=2, label="Market Price (S&P 500)")

    # Plot Value (Reality)
    plt.plot(
        df["Date"], df["V_uet_scaled"], "g--s", linewidth=2, label="UET True Value (Earnings/Hyp)"
    )

    # Highlight Gap
    plt.fill_between(
        df["Date"],
        df["SP500_Price"],
        df["V_uet_scaled"],
        where=(df["SP500_Price"] > df["V_uet_scaled"]),
        facecolor="red",
        alpha=0.3,
        label="Bubble Zone (Risk)",
    )

    plt.title("Economic Bubble Detection: Dot Com Crash (2000)")
    plt.xlabel("Year")
    plt.ylabel("Index Value")
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path = f"{output_dir}/econ_bubble_chart.png"
    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    results = run_simulation()
    plot_results(results)
