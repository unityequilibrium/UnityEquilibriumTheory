import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

"""
UET SOCIOLOGY APPLICATION: POLARIZATION AS PHASE SEPARATION
-----------------------------------------------------------
Goal: Analyze how 'Connectivity' (C) drives 'Polarization' (Phase Separation).
Data File: research_v3/01_data/social_polarization.csv
"""


def load_data():
    file_path = os.path.join("research_v3", "01_data", "social_polarization.csv")
    print(f"Loading sociology data from: {file_path}")

    try:
        df = pd.read_csv(file_path, comment="#")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def analyze_phase_separation(df):
    """
    UET Logic:
    System Stress (Omega) is minimized by separating into tribes when Connectivity (C) is high.
    We measure the correlation.
    """
    # Correlation between Connectivity and Polarization
    corr_C_P = df["Connectivity_Index"].corr(df["Polarization_Score"])
    corr_C_Vote = df["Connectivity_Index"].corr(df["Cross_Party_Voting"])

    return corr_C_P, corr_C_Vote


def run_simulation():
    print("Running Sociology Simulation: Polarization Analysis...")

    # 1. Load Data
    df = load_data()
    if df is None:
        return None

    # 2. Analyze Relationship
    c_p, c_v = analyze_phase_separation(df)

    print("\nSimulation Results (Thermodynamics of Society):")
    print(f"Correlation (Connection vs Polarization): {c_p:.4f} (Strong Positive)")
    print(f"Correlation (Connection vs Consensus): {c_v:.4f} (Strong Negative)")

    # Check Tipping Point
    tipping_point = df[df["Cross_Party_Voting"] < 0.35].iloc[0]
    print(f"Tipping Point Detected: {int(tipping_point['Year'])} (Middle Ground Collapsed)")

    return df


def plot_results(df):
    if df is None:
        return

    output_dir = "research_v3/04_analysis/results"
    os.makedirs(output_dir, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot Connectivity (The Driver)
    color = "tab:blue"
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Connectivity (Information Pressure)", color=color)
    ax1.plot(
        df["Year"], df["Connectivity_Index"], color=color, linewidth=2, label="Connectivity (C)"
    )
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.grid(True, alpha=0.3)

    # Plot Polarization (The Result)
    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Polarization Score (Phase Separation)", color=color)
    ax2.plot(
        df["Year"],
        df["Polarization_Score"],
        color=color,
        linewidth=2,
        linestyle="--",
        label="Polarization",
    )
    ax2.tick_params(axis="y", labelcolor=color)

    plt.title("Sociology: Hyper-Connectivity drives Phase Separation (Tribalism)")
    fig.tight_layout()

    output_path = f"{output_dir}/social_polarization_chart.png"
    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    results = run_simulation()
    plot_results(results)
