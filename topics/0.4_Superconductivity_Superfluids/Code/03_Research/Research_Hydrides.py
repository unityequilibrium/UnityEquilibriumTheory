"""
UET High-Pressure Superconductivity Research
============================================
Topic: 0.4 Superconductivity
Goal: Validate UET prediction that pressure increases Information Density (Omega), raising Tc.
Data: Drozdov et al. (H3S, LaH10).

Hypothesis:
Tc ~ Omega_phonons ~ Pressure^(alpha)
UET predicts alpha approx 0.5 (geometric compression).
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


import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
project_root = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists():
        project_root = parent
        break

if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
elif not project_root:
    # Fallback: Go up 5 levels from Code/03_Research to Project Root
    # Path: topics/0.4/Code/03_Research/script.py
    # Parents: 0=03_Res, 1=Code, 2=0.4, 3=topics, 4=docs (pkg), 5=ROOT
    fallback = current_path.parents[5]
    if (fallback / "docs").exists():
        sys.path.insert(0, str(fallback))
    else:
        # Try 4 levels just in case
        sys.path.insert(0, str(current_path.parents[4]))

from docs.core.uet_glass_box import UETPathManager, UETMetricLogger


def load_hydride_data():
    """Load Hydride data."""
    # Hardcoded relative path
    data_file = current_path.parents[2] / "Data" / "03_Research" / "hydride_superconductivity.json"
    if not data_file.exists():
        return None
    with open(data_file, encoding="utf-8") as f:
        return json.load(f)


def run_hydride_analysis():
    print("=" * 60)
    print("❄️ UET SUPERCONDUCTIVITY: HYDRIDE PRESSURE TEST")
    print("Data: Drozdov et al. (2015, 2019)")
    print("=" * 60)

    data = load_hydride_data()
    if not data:
        return False

    # H3S Data
    h3s_p = [d["Pressure_GPa"] for d in data["H3S"]["data_points"]]
    h3s_tc = [d["Tc_K"] for d in data["H3S"]["data_points"]]

    # LaH10 Data
    lah10_p = [d["Pressure_GPa"] for d in data["LaH10"]["data_points"]]
    lah10_tc = [d["Tc_K"] for d in data["LaH10"]["data_points"]]

    print("\n[1] H3S (Sulfur Hydride)")
    print(f"  Max Tc: {max(h3s_tc)} K at {h3s_p[h3s_tc.index(max(h3s_tc))]} GPa")

    print("\n[2] LaH10 (Lanthanum Decahydride)")
    print(f"  Max Tc: {max(lah10_tc)} K at {lah10_p[lah10_tc.index(max(lah10_tc))]} GPa")

    # --- VISUALIZATION ---
    result_dir = UETPathManager.get_result_dir(
        "0.4_Superconductivity_Superfluids", "Hydride_Validation", category="showcase"
    )
    logger = UETMetricLogger("HydrideSC", topic_id="0.4", category="showcase")

    plt.figure(figsize=(10, 6))

    # Plot Data
    plt.plot(h3s_p, h3s_tc, "bo-", label="H3S Data (Drozdov 2015)")
    plt.plot(lah10_p, lah10_tc, "ro-", label="LaH10 Data (Drozdov 2019)")

    plt.xlabel("Pressure (GPa)")
    plt.ylabel("Critical Temperature Tc (K)")
    plt.title("High-Tc Superconductivity in Hydrides under Pressure")
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Add room temp line
    plt.axhline(y=295, color="green", linestyle="--", alpha=0.5, label="Room Temperature (Goal)")
    plt.text(120, 300, "Room Temp Goal", color="green")

    save_path = result_dir / "Hydride_Validation.png"
    plt.savefig(save_path, dpi=300)
    print(f"📸 Showcase Image Saved: {save_path}")

    print("✅ PASS: Hydride data visualized.")
    return True


if __name__ == "__main__":
    run_hydride_analysis()
