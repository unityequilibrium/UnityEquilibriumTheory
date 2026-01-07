import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

"""
UET BIOLOGY APPLICATION: HEALTH VS STRESS (HRV ANALYSIS)
--------------------------------------------------------
Goal: Distinguish Healthy vs Stressed hearts using UET Vitality Metric.
Data File: research_v3/01_data/hrv_stress.csv
"""


def load_data():
    file_path = os.path.join("research_v3", "01_data", "hrv_stress.csv")
    print(f"Loading biology data from: {file_path}")

    # Load data skipping comments
    try:
        df = pd.read_csv(file_path, comment="#")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def calculate_vitality(row):
    """
    UET Vitality Logic:
    Health requires 'Flexibility' (Variance/C).
    Stress creates 'Rigidity' (Low Variance/I).

    Formula: Vitality = StdDev(RR) / Mean(RR) * 100
    (Coefficient of Variation, widely used in complexity biology)
    """
    # Extract RR intervals (columns starting with RR)
    rr_values = [row[col] for col in row.index if col.startswith("RR")]
    rr_array = np.array(rr_values, dtype=float)

    mean_rr = np.mean(rr_array)  # Representative of 'I' (State)
    std_rr = np.std(rr_array)  # Representative of 'C' (Flexibility)

    if mean_rr == 0:
        return 0

    # UET Vitality Score
    vitality = (std_rr / mean_rr) * 100
    return vitality


def run_simulation():
    print("Running Biology Simulation: Heart Rate Variability Analysis...")

    # 1. Load Data
    df = load_data()
    if df is None:
        return None

    # 2. Calculate UET Vitality Score
    df["UET_Vitality"] = df.apply(calculate_vitality, axis=1)

    print("\nSimulation Results (Health Scores):")
    for index, row in df.iterrows():
        status = "✅ HEALTHY" if row["UET_Vitality"] > 5.0 else "⚠️ STRESSED/AGED"
        print(
            f"Subject: {row['Subject_ID']} ({row['Condition']}) | Vitality: {row['UET_Vitality']:.2f} | {status}"
        )

    return df


def plot_results(df):
    if df is None:
        return

    output_dir = "research_v3/04_analysis/results"
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10, 6))

    # Color mapping
    colors = ["green" if cond in ["Healthy", "Athlete"] else "red" for cond in df["Condition"]]

    # Bar Chart
    bars = plt.bar(df["Subject_ID"], df["UET_Vitality"], color=colors, alpha=0.7)

    plt.title("UET Health Metric: Heart Rate Flexibility", fontsize=14)
    plt.xlabel("Subject", fontsize=12)
    plt.ylabel("Vitality Score (C/I Ratio)", fontsize=12)
    plt.grid(axis="y", alpha=0.3)

    # Add labels
    for bar, label in zip(bars, df["Condition"]):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{label}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    output_path = f"{output_dir}/bio_health_chart.png"
    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    results = run_simulation()
    plot_results(results)
