import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

"""
UET BLACK HOLE SCALING (V3 IMPLEMENTATION)
------------------------------------------
Objective: Demonstrate Cosmological Coupling in 'Dead' Ellipticals using MIGRATED data.
Source: 'research_v3/01_data/real_legacy/galaxies/kormendy_ho_ellipticals_sample.csv'

Physics:
- M_BH(a) = M_BH(0) * (a/a_0)^k
- k = 2.8 (UET Prediction from Dark Sector)
- k = 0.0 (Standard GR)
"""


def ccbh_coupling_law(mass_initial, z_target, k_val):
    """
    Rewinds black hole mass from z=0 to z_target.
    M(z) = M(0) * (1+z)^(-k)
    """
    return mass_initial * (1 + z_target) ** (-k_val)


def run_ccbh_v3():
    print("💎 UET V3: BLACK HOLE SCALING ANALYSIS")
    print("======================================")

    # 1. Load Data from V3 INTERNAL Path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # research_v3
    file_path = os.path.join(
        base_dir, "01_data", "real_legacy", "galaxies", "kormendy_ho_ellipticals_sample.csv"
    )

    if not os.path.exists(file_path):
        print(f"❌ Error: Data missing at {file_path}")
        print("   (Did migration succeed?)")
        return

    df = pd.read_csv(file_path, comment="#")
    print(f"✅ Loaded {len(df)} Galaxy records from V3 Storage.")

    # 2. Analyze
    # Calculate Mean Ratio
    mean_ratio = np.mean(10 ** df["log_ratio"])
    print(f"   > Mean Local Ratio (M_BH/M_Bulge): {mean_ratio*100:.3f}%")

    # 3. Simulate "Red Nugget" Progenitor at z=2
    z_progenitor = 2.0

    # A typical modern elliptical BH: 10^9 Solar Masses
    m_bh_modern = 1e9

    # Rewind
    m_bh_gr = ccbh_coupling_law(m_bh_modern, z_progenitor, k_val=0.0)
    m_bh_uet = ccbh_coupling_law(m_bh_modern, z_progenitor, k_val=2.8)

    print("\n--- PROGENITOR PREDICTION (z=2) ---")
    print(f"   Modern Mass: {np.log10(m_bh_modern):.2f} logM")
    print(
        f"   GR Prediction (No Coupling):  {np.log10(m_bh_gr):.2f} logM (Ratio: {mean_ratio*100:.3f}%)"
    )
    print(
        f"   UET Prediction (k=2.8):       {np.log10(m_bh_uet):.2f} logM (Ratio: {(mean_ratio / (1+z_progenitor)**2.8)*100:.3f}%)"
    )

    print("\n✅ CONCLUSION:")
    print("   UET predicts z=2 progenitors had much smaller BHs relative to stars.")
    print("   This matches 'Overmassive' claims if you assume k=0 (GR),")
    print("   but matches 'Coupled Growth' if you assume k=2.8 (UET).")


if __name__ == "__main__":
    run_ccbh_v3()
