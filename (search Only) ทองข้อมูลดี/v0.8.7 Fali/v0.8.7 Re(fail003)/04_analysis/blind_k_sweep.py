import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os


def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gal_dir = os.path.join(base, "01_data", "real_legacy", "galaxies")

    # Load Low-Z
    kh_path = os.path.join(gal_dir, "kormendy_ho_ellipticals_sample.csv")

    # Debug Load
    print(f"DEBUG: Reading {kh_path}")
    try:
        df_low = pd.read_csv(kh_path)  # Try without comment='#' first to see raw
        print("Columns found:", df_low.columns.tolist())
        print("First row:", df_low.iloc[0].tolist())
    except:
        print("Failed basic read")
        return pd.DataFrame(), pd.DataFrame()

    # Re-read properly
    df_low = pd.read_csv(kh_path, comment="#")

    # Strip whitespace from columns
    df_low.columns = df_low.columns.str.strip()

    # Fix 'distance_Mpc'
    # It might be 'distance_Mpc ' or have hidden chars
    col_name = [c for c in df_low.columns if "distance" in c or "dist" in c][0]
    print(f"Using distance column: '{col_name}'")

    df_low[col_name] = pd.to_numeric(df_low[col_name], errors="coerce")
    df_low = df_low.dropna(subset=[col_name])

    df_low["log_ratio"] = pd.to_numeric(df_low["log_ratio"], errors="coerce")
    df_low["z"] = df_low[col_name] * 70 / 300000

    # Load High-Z
    fz_path = os.path.join(gal_dir, "farrah_highz_sample.csv")
    df_high = pd.read_csv(fz_path)
    df_high["log_ratio"] = df_high["logMBH"] - df_high["logMstar"]

    return df_low, df_high


def ccbh_model(z, k, offset):
    return offset - k * np.log10(1 + z)


def run_blind_sweep():
    print("💎 BLIND K-SWEEP: DEBUG MODE")
    print("===========================")

    try:
        df_low, df_high = load_data()
        print(f"✅ Data Loaded: Low-Z (N={len(df_low)}), High-Z (N={len(df_high)})")

        if len(df_low) == 0:
            print("❌ Low-Z data still empty. Aborting fit.")
            return

        # Combined Dataset
        z_all = np.concatenate([df_low["z"], df_high["z"]])
        ratio_all = np.concatenate([df_low["log_ratio"], df_high["log_ratio"]])

        # Blind Fit
        popt, pcov = curve_fit(ccbh_model, z_all, ratio_all)
        k_fit = popt[0]
        error = np.sqrt(np.diag(pcov))[0]

        print(f"\n📈 FIT RESULTS:")
        print(f"   Calculated k = {k_fit:.2f} ± {error:.2f}")

        targets = {0.0: "GR", 2.8: "UET", 3.0: "Farrah"}
        best_match = min(targets.keys(), key=lambda x: abs(x - k_fit))
        print(f"   Verdict: {targets[best_match]}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    run_blind_sweep()
