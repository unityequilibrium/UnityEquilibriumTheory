import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

"""
UET AI APPLICATION: INTELLIGENCE AS OPTIMIZATION
------------------------------------------------
Goal: Analyze LLM Training Curve as Thermodynamic Energy Minimization.
Data File: research_v3/01_data/llm_training.csv
"""


def load_data():
    file_path = os.path.join("research_v3", "01_data", "llm_training.csv")
    print(f"Loading AI training data from: {file_path}")

    try:
        df = pd.read_csv(file_path, comment="#")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def analyze_thermodynamics(df):
    """
    UET Logic:
    Loss = Omega (Potential Energy).
    Learning is the process of minimizing Omega.
    """
    # 1. Delta Omega (Energy Change)
    # diff() calculates typical change, we want negative because drop is good
    df["d_Omega"] = -df["Training_Loss"].diff()

    # 2. Dissipation Efficiency (Energy drop per Step)
    # Normalize by step size to get rate
    df["Step_Diff"] = df["Step"].diff()
    df["Dissipation_Rate"] = df["d_Omega"] / df["Step_Diff"]

    # Fill NaN
    df = df.fillna(0)

    return df


def run_simulation():
    print("Running AI Simulation: Energy Landscape Analysis...")

    # 1. Load Data
    df = load_data()
    if df is None:
        return None

    # 2. Analyze
    df = analyze_thermodynamics(df)

    # 3. Detect Phase Transition (Grokking)
    # Find the point of maximum sudden drop (High Dissipation)
    grokking_idx = df["Dissipation_Rate"].idxmax()
    grokking_step = df.loc[grokking_idx, "Step"]
    grokking_rate = df.loc[grokking_idx, "Dissipation_Rate"]

    print("\nSimulation Results (Learning Dynamics):")
    print(f"Initial Energy (Loss): {df['Training_Loss'].iloc[0]}")
    print(f"Final Energy (Loss): {df['Training_Loss'].iloc[-1]}")
    print(f"Phase Transition (Grokking) detected at Step: {grokking_step}")
    print(f"Max Dissipation Rate: {grokking_rate:.5f} (Energy/Step)")

    return df, grokking_step


def plot_results(df, grokking_step):
    if df is None:
        return

    output_dir = "research_v3/04_analysis/results"
    os.makedirs(output_dir, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot Omega (Loss)
    color = "tab:blue"
    ax1.set_xlabel("Training Steps")
    ax1.set_ylabel("Potential Energy (Loss)", color=color)
    ax1.plot(
        df["Step"], df["Training_Loss"], color=color, linewidth=2, label="Omega (System Stress)"
    )
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.grid(True, alpha=0.3)

    # Plot Dissipation Rate (Learning Speed)
    ax2 = ax1.twinx()
    color = "tab:orange"
    ax2.set_ylabel("Dissipation Rate (-dE/dt)", color=color)
    ax2.plot(
        df["Step"],
        df["Dissipation_Rate"],
        color=color,
        linestyle="--",
        label="Dissipation (Learning Efficiency)",
    )
    ax2.tick_params(axis="y", labelcolor=color)

    # Mark Grokking
    plt.axvline(
        x=grokking_step,
        color="red",
        linestyle=":",
        linewidth=2,
        label=f"Grokking Event (Step {int(grokking_step)})",
    )
    plt.text(
        grokking_step,
        df["Dissipation_Rate"].max(),
        " PHASE TRANSITION",
        color="red",
        fontweight="bold",
    )

    plt.title("AI Optimization: Intelligence as Energy Minimization")
    fig.tight_layout()

    output_path = f"{output_dir}/ai_training_chart.png"
    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    result = run_simulation()
    if result:
        plot_results(*result)
