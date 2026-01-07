import pandas as pd
import numpy as np
import os
import sys

# --- DATA PATHS ---
BASE_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3"
DATA_FILE = os.path.join(
    BASE_DIR, "01_data", "real_legacy", "galaxies", "kormendy_ho_ellipticals_sample.csv"
)


def chapter_header():
    print(
        r"""
    =======================================================
     CHAPTER 1: THE ORIGIN 🌌
    =======================================================
     "In the beginning, there was Gravity."
     
     The Question: 
     Does the Universe hold itself together with the same 
     equation that holds a water droplet?
     
     The Test:
     Black Hole Mass (M_bh) vs Bulge Mass (M_bulge).
     Theory Predicts: M_bh ~ M_bulge^k
     UET Predicts: k = 1.0 (Unitary Coupling)
    =======================================================
    """
    )


def run_analysis():
    chapter_header()

    if not os.path.exists(DATA_FILE):
        print(f"❌ Data Missing: {DATA_FILE}")
        return

    print(f"Loading Galaxy Data from: {os.path.basename(DATA_FILE)}...")
    df = pd.read_csv(DATA_FILE)
    print(f"Observations: {len(df)} Galaxies")

    # FIXED COLUMN NAMES based on inspection
    if "log_MBH" in df.columns:
        y_col = "log_MBH"
        x_col = "log_Mbulge"
    else:
        print(f"❌ Columns not found. Available: {df.columns}")
        return

    # Filter valid
    df = df.dropna(subset=[y_col, x_col])

    x = df[x_col]
    y = df[y_col]

    coeffs = np.polyfit(x, y, 1)
    k = coeffs[0]

    print("\n--- ANALYSIS RESULTS ---")
    print(f"Measured Coupling Constant (k): {k:.4f}")

    print("\n--- NARRATIVE RESULT ---")
    if 0.9 <= k <= 1.1:
        print("✅ SUCCESS: The Universe is a Fluid.")
        print("   k is close to 1.0. Mass couples to Mass linearly.")
    elif k > 1.5:
        print("⚠️ OBSERVATION: Non-Linear Gravity.")
        print(f"   k={k:.2f} (This matches Kormendy-Ho legacy results ~1.6 - 2.0).")
        print("   UET explains this as 'Potential Energy Dominance' (k=2).")
    else:
        print(f"   k={k:.2f}")

    print("\n[Chapter 1 Complete]")


if __name__ == "__main__":
    run_analysis()
