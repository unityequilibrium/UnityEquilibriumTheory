"""
UET Gravitational Wave Test - Entropy Unification
=================================================
Verifies that Gravitational Waves (GW) are Information Entropy waves.

Hypothesis:
Energy radiated (E_gw) corresponds to the Information (S) lost
during the merger event, mediated by the Universal Memory Field.

Event: GW150914
Data: LIGO Open Science Center
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


# --- PATH SETUP (Must be FIRST) ---
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
while _root.name != "docs" and _root.parent != _root:
    _root = _root.parent
if _root.name == "docs":
    sys.path.insert(0, str(_root.parent))
    from docs import ROOT_PATH

    root_path = ROOT_PATH
    ROOT = ROOT_PATH
else:
    print("CRITICAL: Root path not found.")
    sys.exit(1)

# Core Imports
import json
import math
from docs.core.uet_glass_box import UETPathManager
from docs.core.uet_parameters import G, C, M_SUN, K_B, HBAR

c = C
M_sun = M_SUN
k_B = K_B
h_bar = HBAR

# Helper: Dynamic Import of Engine
import importlib.util

try:
    eng_path = (
        ROOT
        / "docs"
        / "topics"
        / "0.2_Black_Hole_Physics"
        / "Code"
        / "01_Engine"
        / "Engine_BlackHole.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_BlackHole", str(eng_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    UETBlackHoleEngine = mod.UETBlackHoleEngine
except Exception as e:
    print(f"CRITICAL: Engine not found: {e}")
    sys.exit(1)


def bekenstein_entropy(M):
    """
    S = 4 * PI * G * M^2 * k_B / (h_bar * c)
    """
    return 4 * math.pi * G * M**2 * k_B / (h_bar * c)


def run_test():
    print("=" * 60)
    print("UET GRAVITATIONAL WAVE ENTROPY TEST")
    print("Event: GW150914")
    print("=" * 60)

    # Path to Data
    TOPIC_DIR = ROOT / "docs" / "topics" / "0.2_Black_Hole_Physics"
    data_path = TOPIC_DIR / "Data" / "03_Research" / "black_hole_data.json"

    try:
        with open(data_path, "r") as f:
            bh_data = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

    gw_event = next(item for item in bh_data["gravitational_wave"] if item["event"] == "GW150914")

    # Initialize Engine
    engine = UETBlackHoleEngine()

    M1 = gw_event["m1"]
    M2 = gw_event["m2"]
    M_final = gw_event["final_mass"]

    # Radiated Energy (Observed)
    E_rad_obs = ((M1 + M2) - M_final) * M_sun * c**2

    # Calculate Entropies using Engine
    S1 = engine.compute_entropy(M1)
    S2 = engine.compute_entropy(M2)
    S_final = engine.compute_entropy(M_final)

    S_init = S1 + S2
    Delta_S = S_final - S_init

    print(f"Initial Entropy: {S_init:.2e} J/K")
    print(f"Final Entropy:   {S_final:.2e} J/K")
    print(f"Entropy Change:  {Delta_S:.2e} J/K (Increased)")

    # Temperature Scale (Hawking Temp of Final BH)
    T_H_final = engine.compute_temperature(M_final)
    Thermodynamic_Available_Work = Delta_S * T_H_final

    print(f"T_Hawking (Final): {T_H_final:.2e} K")
    print(f"T * Delta_S:       {Thermodynamic_Available_Work:.2e} J")
    print(f"Observed E_rad:    {E_rad_obs:.2e} J")

    # Guard against zero division if kill switch active (T=nan)
    if math.isnan(T_H_final):
        print("KILL SWITCH DETECTED: Engine returned NaN.")
        return False

    Ratio = E_rad_obs / Thermodynamic_Available_Work
    print(f"Amplification Ratio: {Ratio:.4f}")

    UET_CONSTANT = math.log(2) / math.pi
    print(f"Theoretical UET Constant (ln(2)/pi): {UET_CONSTANT:.4f}")

    error_margin = abs(Ratio - UET_CONSTANT) / UET_CONSTANT
    print(f"Deviation: {error_margin*100:.2f}%")

    if error_margin < 0.05:
        print("\nSUCCESS! Universal Gravitational Entropy Relation Confirmed.")
        print(f"Formula: E_rad = (ln 2 / pi) * T_H * Delta_S")
        return True
    else:
        print("\nFAIL: Ratio does not match ln(2)/pi.")
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
