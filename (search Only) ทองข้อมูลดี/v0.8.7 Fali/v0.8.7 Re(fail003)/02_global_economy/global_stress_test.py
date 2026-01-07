import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
import os
import glob

# --- CONFIG ---
DATA_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\02_global_economy\data"
RESULTS_DIR = (
    r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\02_global_economy\results"
)
os.makedirs(RESULTS_DIR, exist_ok=True)


# --- UET METRICS ---
def calculate_uet_metrics(df, price_col="Close", window=20):
    """
    Calculate UET Value Metric (V) and Momentum (M).
    V = sqrt(Baseline / Momentum)
    Baseline (B) = SMA(Price)
    Momentum (M) = StdDev(Price) * Volume_Factor (if available) or just Volatility
    """
    # Force Numeric
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    df = df.dropna(subset=[price_col])

    # 1. Baseline (B)
    df["B"] = df[price_col].rolling(window=window).mean()

    # 2. Momentum (M) = Flux
    # We use realized volatility as the primary proxy for Momentum in financial fluids
    df["M"] = df[price_col].rolling(window=window).std()

    # 3. Value (V)
    # Avoid div by zero
    df["V"] = np.sqrt(df["B"] / (df["M"] + 1e-9))

    return df.dropna()


def coupling_model(x, k, offset):
    return offset + k * np.log10(x)


# --- ANALYSIS ENGINE ---
def analyze_global_economy():
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    csv_files = [f for f in csv_files if "_acquisition_summary" not in f]

    summary = []
    combined_v = pd.DataFrame()

    print(f"--- GLOBAL STRESS TEST: ANALYZING {len(csv_files)} ASSETS ---")

    for file_path in csv_files:
        name = os.path.basename(file_path).replace(".csv", "")
        print(f"Processing {name}...")

        try:
            # FIX: Skip the second row (Ticker symbol row) which makes cols object type
            # yfinance format: Row 0 = Headers, Row 1 = Tickers
            df = pd.read_csv(file_path, header=0, skiprows=[1])

            # Robust Column Detection
            # Find 'Close' or 'Adj Close'
            close_col = [c for c in df.columns if "Close" in c]
            if not close_col:
                print(f"   SKIP: No 'Close' column found. Cols: {df.columns.tolist()}")
                continue
            target_col = close_col[0]  # Prefer first found (usually Adj Close or Close)

            # Calculate Metrics
            df = calculate_uet_metrics(df, price_col=target_col)

            # Fit Coupling Constant (k)
            df_fit = df[df["B"] > 0]
            x_data = df_fit["B"].values
            y_data = np.log10(df_fit["M"].values + 1e-9)  # Safety log

            # Initial guess k=1
            popt, pcov = curve_fit(coupling_model, x_data, y_data, p0=[1.0, 0.0])
            k_val = popt[0]
            k_err = np.sqrt(np.diag(pcov))[0]

            print(f"   k (Scaling) = {k_val:.4f} +/- {k_err:.4f}")
            print(f"   Avg V Score = {df['V'].mean():.4f}")

            summary.append(
                {
                    "Asset": name,
                    "k": k_val,
                    "k_err": k_err,
                    "Avg_V": df["V"].mean(),
                    "Max_V": df["V"].max(),
                    "Min_V": df["V"].min(),
                }
            )

            # Store V series for correlation
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df.set_index("Date", inplace=True)
                # Resample to daily to align (handle gaps)
                v_series = df["V"].resample("D").mean().fillna(method="ffill")
                combined_v[name] = v_series

            # Plot Individual Asset
            plt.figure(figsize=(10, 4))
            plt.plot(df.index, df["V"], label="UET Value (V)", color="green", linewidth=1)
            # Normalize price for comparison
            normalized_price = (df[target_col] - df[target_col].min()) / (
                df[target_col].max() - df[target_col].min()
            )
            normalized_v = (df["V"] - df["V"].min()) / (df["V"].max() - df["V"].min())

            plt.plot(
                df.index,
                normalized_price * df["V"].max(),
                label="Normalized Price",
                color="gray",
                alpha=0.3,
            )
            plt.title(f"{name}: UET Value Metric (V)")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(RESULTS_DIR, f"{name}_V_metric.png"))
            plt.close()

        except Exception as e:
            print(f"   FAIL: {e}")

    # --- GLOBAL SUMMARY ---
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(os.path.join(RESULTS_DIR, "global_summary.csv"), index=False)
    print("\n--- GLOBAL RESULTS ---")
    print(summary_df)

    # --- CORRELATION MATRIX (The "Fluid" Check) ---
    print("\nCalculating Global Synchronization...")
    if not combined_v.empty:
        corr_matrix = combined_v.corr()

        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, cmap="mako", vmin=-1, vmax=1)
        plt.title("Reference Frame Synchronization: Global V-Score Correlation")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "global_correlation_heatmap.png"))
        plt.close()
        print("Market Fluid Heatmap Saved.")
    else:
        print("No combined data for heatmap.")


if __name__ == "__main__":
    analyze_global_economy()
