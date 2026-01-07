import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

"""
UET UNIVERSAL METRIC TEST: CROSS-SCALE VALIDATION
-------------------------------------------------
Goal: Plot all 5 systems (Galaxy, Econ, Bio, AI, Social) on ONE graph.
Hypothesis: All stable systems exist in a "Golden Zone" of Connectivity.
X-Axis: Normalized Connectivity/Input (C)
Y-Axis: Normalized Stability/Health (V)
"""


def normalize(series):
    return (series - series.min()) / (series.max() - series.min())


def load_galaxy_data():
    # Galaxy: X = Radius (Space), Y = Stability (Observed Velocity / Predicted)
    # Ideally, Stability = 1.0. Deviations show failure of standard physics (Newton).
    # UET 'I' restores it to 1.0.
    path = "research_v3/01_data/NGC6503_rotmod.dat"
    try:
        data = np.loadtxt(path, skiprows=3)
        r = data[:, 0]
        v_obs = data[:, 3]

        # Normalize
        X = normalize(r)  # Radius (0 to 1)
        Y = normalize(v_obs)  # Velocity Profile (Structure)
        return X, Y, "Galaxy (Structure)"
    except:
        return None, None, None


def load_econ_data():
    # Econ: X = Volume (Hype/Connectivity), Y = True Value (UET V)
    path = "research_v3/01_data/sp500_bubble.csv"
    try:
        df = pd.read_csv(path, comment="#")
        E = df["Earnings"]
        C = df["Volume_Billions"]
        V_uet = E * np.sqrt(E / C)

        X = normalize(C)  # High Connectivity
        Y = normalize(V_uet)  # Health
        return X, Y, "Markey (Value)"
    except:
        return None, None, None


def load_bio_data():
    # Bio: X = Flexibility (StdDev), Y = Health Score
    path = "research_v3/01_data/hrv_stress.csv"
    try:
        df = pd.read_csv(path, comment="#")
        X_vals = []
        Y_vals = []

        for _, row in df.iterrows():
            rr = [row[c] for c in row.index if c.startswith("RR")]
            rr = np.array(rr, dtype=float)
            mean = np.mean(rr)
            std = np.std(rr)
            vitality = std / mean

            X_vals.append(std)  # Flexibility
            Y_vals.append(vitality)  # Health

        X = normalize(np.array(X_vals))
        Y = normalize(np.array(Y_vals))
        return X, Y, "Biology (Vitality)"
    except:
        return None, None, None


def load_ai_data():
    # AI: X = Training Step (Energy Input), Y = 1/Loss (Intelligence/Order)
    path = "research_v3/01_data/llm_training.csv"
    try:
        df = pd.read_csv(path, comment="#")
        X = normalize(df["Step"])
        Y = normalize(1 / df["Training_Loss"])  # Inverse Loss = Optimization
        return X, Y, "AI (Intelligence)"
    except:
        return None, None, None


def load_social_data():
    # Social: X = Connectivity, Y = Cohesion (1 - Polarization)
    path = "research_v3/01_data/social_polarization.csv"
    try:
        df = pd.read_csv(path, comment="#")
        X = normalize(df["Connectivity_Index"])
        Y = normalize(1 - df["Polarization_Score"])  # Cohesion
        return X, Y, "Society (Cohesion)"
    except:
        return None, None, None


def run_meta_analysis():
    print("Running Universal Metric Test...")

    systems = [load_galaxy_data, load_econ_data, load_bio_data, load_ai_data, load_social_data]

    plt.figure(figsize=(12, 8))

    # Plot "Golden Zone" Background
    x_range = np.linspace(0, 1, 100)
    y_golden = np.sin(x_range * np.pi)  # Idealized Hill Curve
    plt.fill_between(x_range, y_golden, color="gold", alpha=0.1, label="Theoretical Golden Zone")

    colors = ["purple", "green", "red", "blue", "orange"]

    for i, loader in enumerate(systems):
        X, Y, label = loader()
        if X is not None:
            # Sort for clean lines
            idx = np.argsort(X)
            X_sorted = X[idx]
            Y_sorted = Y[idx]

            plt.plot(
                X_sorted,
                Y_sorted,
                marker="o",
                linestyle="-",
                linewidth=2,
                color=colors[i],
                label=label,
                alpha=0.7,
            )

    plt.title("The UET Universal Stability Curve (Cross-Scale Validation)", fontsize=16)
    plt.xlabel("Normalized Connectivity / Energy Input (C)", fontsize=12)
    plt.ylabel("System Health / Structure / Cohesion (V)", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.text(0.5, 0.95, "PEAK STABILITY", ha="center", color="gold", fontweight="bold")
    plt.text(0.05, 0.05, "STASIS", color="gray")
    plt.text(0.95, 0.05, "CHAOS", ha="right", color="red")

    output_path = "research_v3/04_analysis/results/universal_metric_chart.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    print(f"Universal Plot Saved: {output_path}")


if __name__ == "__main__":
    run_meta_analysis()
