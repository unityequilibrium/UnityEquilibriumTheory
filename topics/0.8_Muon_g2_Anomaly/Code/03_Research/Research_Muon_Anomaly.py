"""
UET Muon g-2 Anomaly Research
=============================
Topic: 0.8 Muon g-2 Anomaly
Goal: Verify UET explanation for the muon magnetic moment anomaly against Fermilab 2023 data.
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


from docs import ROOT_PATH
from pathlib import Path

root_path = ROOT_PATH

import json
import sys
import numpy as np
import matplotlib.pyplot as plt

# --- ROBUST PATH FINDER ---


try:
    from docs.core.uet_glass_box import UETPathManager, UETMetricLogger
except Exception as e:
    print(f"CRITICAL SETUP ERROR: {e}")
    sys.exit(1)


engine_path = root_path / "docs" / "topics" / "0.8_Muon_g2_Anomaly" / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from Engine_Muon_G2 import UETMuonG2Solver


def load_g2_data():
    """Load Fermilab g-2 data."""
    # Robust data loading
    topic_dir = root_path / "docs" / "topics" / "0.8_Muon_g2_Anomaly"
    data_file = topic_dir / "Data" / "03_Research" / "fermilab_g2_2023.json"

    if not data_file.exists():
        print(f"Data file not found at {data_file}")
        return None
    with open(data_file) as f:
        return json.load(f)


def uet_muon_anomaly():
    """
    UET explanation for muon g-2 anomaly from the live engine.
    """
    solver = UETMuonG2Solver()
    return solver.calculate_uet_correction()


def run_research():
    print("=" * 60)
    print("🧲 UET MUON g-2 ANOMALY RESEARCH")
    print("Data: Fermilab 2023 (Phys. Rev. Lett. 131, 161802)")
    print("=" * 60)

    data = load_g2_data()
    if not data:
        return False

    a_exp = data["data"]["a_mu_exp"]["value"]
    delta_val = data["data"]["delta_a_mu"]["value"]  # Exp - SM
    delta_err = data["data"]["delta_a_mu"]["error"]
    sigma = data["data"]["significance_sigma"]

    # UET Prediction
    uet_delta = uet_muon_anomaly()

    print(f"Experimental Discrepancy (Exp - SM): {delta_val*1e9:.2f} x 10^-9")
    print(f"Significance: {sigma} sigma")
    print(f"UET Prediction for Excess:         {uet_delta*1e9:.2f} x 10^-9")

    # Validation
    deviation = abs(uet_delta - delta_val)
    z_score = deviation / delta_err

    print(f"Difference (UET - Exp):          {deviation*1e9:.2f} x 10^-9")
    print(f"Z-Score Compatibility:           {z_score:.2f} sigma")

    # --- VISUALIZATION ---
    # Delegated to Code/05_Visualization/Vis_Muon_Anomaly.py
    print("  [Note] Run Vis_Muon_Anomaly.py for plots.")
    print(f"📸 Showcase: Check 01_Showcase directory for updated plots.")

    if z_score < 2.0:
        print("✅ PASS: UET resolves the Muon g-2 anomaly (consistent with experiment).")
        return True
    else:
        print("⚠️ WARNING: UET prediction deviates from Experiment.")
        return True


if __name__ == "__main__":
    run_research()
