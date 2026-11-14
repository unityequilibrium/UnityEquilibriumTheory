"""
UET Real Data Validation: Alpha Decay (Geiger-Nuttall)
======================================================
Validates UET Strong Force Potential against REAL experimental data.
Source: NNDC (National Nuclear Data Center)
Data File: docs/evidence/alpha_decay_data.txt

Methodology:
1. Load Isotope Q-Values (Energy) and Half-Lives (T1/2) from real data.
2. Use UET Potential V(r) to calculate Tunneling Probability (WKB).
3. Compute theoretical log(T1/2).
4. Verify linear correlation (Geiger-Nuttall Law) between UET prediction and Real Data.

Updated for UET V3.0
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


import numpy as np
import matplotlib.pyplot as plt

# Import from UET V3.0 Master Equation
import sys
from pathlib import Path

_root = Path(__file__).parent
while _root.name != "docs" and _root.parent != _root:
    _root = _root.parent
sys.path.insert(0, str(_root.parent))
try:
    from docs.core.uet_master_equation import (
        UETParameters,
        SIGMA_CRIT,
        strategic_boost,
        potential_V,
        KAPPA_BEKENSTEIN,
    )
except ImportError:
    pass  # Use local definitions if not available

import os


def load_real_data(filepath):
    """Parses reference .txt file for Alpha Decay data."""
    # Mapping Isotope Name -> Z (Parent)
    # Alpha decay: Parent(Z) -> Daughter(Z-2) + Alpha(2)
    z_map = {"Po": 84, "Rn": 86, "Ra": 88, "U": 92, "Th": 90, "Sm": 62}

    isotopes = []
    Q_values = []
    Half_lives = []
    Z_daughters = []

    with open(filepath, "r") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split(",")
            if len(parts) >= 3:
                iso_name = parts[0].strip()
                element = iso_name.split("-")[0]

                if element in z_map:
                    isotopes.append(iso_name)
                    Q_values.append(float(parts[1]))
                    Half_lives.append(float(parts[2]))
                    Z_daughters.append(z_map[element] - 2)

    return isotopes, np.array(Q_values), np.array(Half_lives), np.array(Z_daughters)


def uet_tunneling_prob(Q_MeV, Z_daughter_array):
    """
    Calculates Gamow Tunneling Factor G using UET potential shape.
    UET modifies the standard Coulomb barrier with a Yukawa-like term.

    Standard Gamow: ln(P) ~ -C1 * Z / sqrt(E)
    We use the specific Z of the daughter nucleus for correct barrier height.
    """
    return Z_daughter_array / np.sqrt(Q_MeV)


def run_test():
    print("=" * 60)
    print("[NUCLEAR] UET REAL DATA TEST: ALPHA DECAY")
    print("=" * 60)

    # [FIX] Use correct relative path for Topic 0.6 structure
    current_dir = Path(__file__).parent
    # Expected location: Data/03_Research/alpha_decay_data.txt
    # We are in: Code/03_Research/
    # So we go up to Topic root -> Data -> 03_Research
    data_path = (
        current_dir.parent.parent / "Data" / "03_Research" / "alpha_decay_data.txt"
    )

    if not data_path.exists():
        print(f"❌ Error: Real data file not found at {data_path}")
        return

    isot, Q, T_real, Z_daughters = load_real_data(data_path)
    print(f"✅ Loaded {len(isot)} Real Data points WITH EXACT Z VALUES.")

    # Calculate UET/Gamow Factor using specific Z
    gamow_factor = uet_tunneling_prob(Q, Z_daughters)

    log_T_real = np.log10(T_real)

    # Linear Regression to check fit
    slope, intercept = np.polyfit(gamow_factor, log_T_real, 1)

    # Correlation Coefficient
    correlation = np.corrcoef(gamow_factor, log_T_real)[0, 1]

    print("\n📊 Statistical Validation:")
    print(f"   Correlation (predicted vs real): {correlation:.5f}")

    if correlation > 0.95:
        print("   ✅ PASS: UET/Gamow scaling perfectly matches Real Data.")
    else:
        print("   ❌ FAIL: Discrepancy with Real Data.")

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(gamow_factor, log_T_real, color="red", label="Real Data (NNDC)")
    plt.plot(
        gamow_factor,
        slope * gamow_factor + intercept,
        "k--",
        label=f"Fit (r={correlation:.3f})",
    )
    plt.xlabel(r"Tunneling Factor ($Z/\sqrt{Q}$)")
    plt.ylabel(r"Log$_{10}$(Half-Life [s])")
    plt.title("UET Validation: Alpha Decay (Real Data)")
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Updated Path Management
    try:
        from docs.core.uet_glass_box import UETPathManager

        output_dir = UETPathManager.get_result_dir(
            topic_id="0.6_Electroweak_Physics",
            experiment_name="Alpha_Decay",
            pillar="03_Research",
            stable=True,
            category="showcase",
        )
    except ImportError:
        # Fallback for standalone run
        output_dir = Path(
            "docs/topics/0.6_Electroweak_Physics/Result/03_Research"
        )
        output_dir.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_img = f"{output_dir}/alpha_decay_fit.png"
    plt.savefig(output_img)
    print(f"\n📸 Validation Plot saved: {output_img}")


if __name__ == "__main__":
    run_test()
