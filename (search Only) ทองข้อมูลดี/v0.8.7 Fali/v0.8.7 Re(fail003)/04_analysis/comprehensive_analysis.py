import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

# --- PATHS ---
DATA_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\01_data"
RESULTS_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\04_analysis\results_comprehensive"
os.makedirs(RESULTS_DIR, exist_ok=True)


# --- UET CORE MODELS ---
def uet_coupling_model(x, k, offset):
    """General UET Coupling: y = offset + k * log(x)"""
    return offset + k * np.log10(x)


def uet_value_metric(baseline, momentum):
    """The Fundamental Value Metric: V = sqrt(B / M)"""
    return np.sqrt(baseline / (momentum + 1e-9))


# --- ANALYSIS FUNCTIONS ---


def analyze_dataset(name, filename, x_col, y_col, type_label):
    path = os.path.join(DATA_DIR, filename)
    print(f"--- Analyzing {name} ({type_label}) ---")

    try:
        if filename.endswith(".dat"):
            # Special handling for Rotmod (whitespace separated)
            df = pd.read_csv(
                path, sep=r"\s+", comment="#", names=["r", "v_obs", "v_gas", "v_disk", "v_halo"]
            )
            df = df.rename(columns={"r": x_col, "v_obs": y_col})
        else:
            # Universal fix: Handle commented headers
            df = pd.read_csv(path, comment="#")

        # --- PRE-PROCESSING FOR SPECIAL DATASETS ---
        if name == "HRV_Bio":
            rr_cols = [c for c in df.columns if "RR" in c]
            df["Mean_RR"] = df[rr_cols].mean(axis=1)
            df[y_col] = df["Mean_RR"]
            df[x_col] = df.index + 1  # Proxy for Time Step

        # 1. basic clean
        # Check if columns exist
        if x_col not in df.columns or y_col not in df.columns:
            raise ValueError(f"Missing columns: {x_col} or {y_col}. Found: {df.columns.tolist()}")

        df = df.dropna(subset=[x_col, y_col])
        df = df[df[x_col] > 0]  # log safety
        df = df[df[y_col] > 0]

        # 2. Fit Coupling Constant (k)
        # We assume y ~ x^k  => log(y) ~ k * log(x)
        x_data = df[x_col].values
        y_data = np.log10(df[y_col].values)

        # Initial guess for k is crucial. Start with 1.0 (linear)
        popt, pcov = curve_fit(uet_coupling_model, x_data, y_data, p0=[1.0, 0.0])
        k_val = popt[0]
        k_err = np.sqrt(np.diag(pcov))[0]

        print(f"   k (Coupling) = {k_val:.4f} +/- {k_err:.4f}")

        # 3. Calculate Value Metric (V)
        # Baseline (B) = Mean(y), Momentum (M) = StdDev(y) over rolling window
        df["rolling_mean"] = df[y_col].rolling(window=10).mean()
        df["rolling_std"] = df[y_col].rolling(window=10).std()

        # Drop NaN mainly from rolling window
        df_metric = df.dropna(subset=["rolling_mean", "rolling_std"])

        df_metric["UET_Value"] = uet_value_metric(
            df_metric["rolling_mean"], df_metric["rolling_std"]
        )

        avg_value = df_metric["UET_Value"].mean()
        print(f"   Avg UET Value = {avg_value:.4f}")

        # 4. Plot
        plt.figure(figsize=(10, 5))

        plt.subplot(1, 2, 1)
        plt.scatter(x_data, y_data, alpha=0.5, label="Data", s=10)
        plt.plot(x_data, uet_coupling_model(x_data, *popt), "r-", label=f"Fit k={k_val:.2f}")
        plt.title(f"{name}: Scaling Law")
        plt.xlabel(f"log({x_col})")
        plt.ylabel(f"log({y_col})")
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.subplot(1, 2, 2)
        plt.plot(df.index, df["rolling_mean"], "b-", alpha=0.3, label="Baseline (B)")
        if not df_metric.empty:
            plt.plot(df_metric.index, df_metric["UET_Value"], "g-", label="UET Value (V)")
        plt.title(f"{name}: Stability Metric")
        plt.xlabel("Index")
        plt.ylabel("V = sqrt(B/M)")
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, f"{name}_analysis.png"))
        plt.close()

        return {"name": name, "k": k_val, "k_err": k_err, "avg_V": avg_value, "status": "PASS"}

    except Exception as e:
        print(f"   FAILED: {e}")
        return {"name": name, "k": 0, "k_err": 0, "avg_V": 0, "status": "FAIL"}


# --- MAIN EXECUTION ---

datasets = [
    # Finance: Volatility ~ Volume^k
    # Header: Date,SP500_Price,Earnings,Volume_Billions
    {
        "name": "SP500_Crash",
        "file": "sp500_bubble.csv",
        "x": "Volume_Billions",
        "y": "SP500_Price",
        "type": "Finance",
    },
    # Biology: HRV ~ Time
    # Header: Subject_ID,Condition,RR_Interval_1...
    {"name": "HRV_Bio", "file": "hrv_stress.csv", "x": "Time", "y": "Mean_RR", "type": "Biology"},
    # Physics: Velocity ~ Radius (Galaxy Rotation)
    {
        "name": "Galaxy_Rot",
        "file": "NGC6503_rotmod.dat",
        "x": "r",
        "y": "v_obs",
        "type": "Astrophysics",
    },
    # AI: Loss ~ Training Steps
    # Header: Step,Training_Loss,Validation_Loss,Learning_Rate
    {
        "name": "LLM_Loss",
        "file": "llm_training.csv",
        "x": "Step",
        "y": "Training_Loss",
        "type": "AI",
    },
    # Social: Polarization ~ Network Connectivity (Interaction leads to tribalism?)
    # Header: Year,Connectivity_Index,Polarization_Score,Cross_Party_Voting
    {
        "name": "Social_Pol",
        "file": "social_polarization.csv",
        "x": "Connectivity_Index",
        "y": "Polarization_Score",
        "type": "Sociology",
    },
]

results = []
print("--- STARTING COMPREHENSIVE UET ANALYSIS (Robust Mode v2) ---")

for d in datasets:
    res = analyze_dataset(d["name"], d["file"], d["x"], d["y"], d["type"])
    results.append(res)

print("\n--- FINAL SUMMARY ---")
summary_df = pd.DataFrame(results)
print(summary_df)
summary_df.to_csv(os.path.join(RESULTS_DIR, "comprehensive_summary.csv"), index=False)
