"""
Plasma Physics Data
===================
Real measurements from Tokamak fusion (JET, ITER) and Space Plasma (Parker Solar Probe).

Sources:
- JET Joint European Torus (2024 results)
- Parker Solar Probe (NASA 2024/2025)
"""

import json
import os


def _load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "references", "plasma_records.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


_data = _load_data()

# ============================================
# TOKAMAK FUSION (Magnetic Confinement)
# ============================================

JET_RECORD_2024 = _data["fusion"]["jet_2024"]
ITER_DESIGN = _data["fusion"]["iter_design"]

# ============================================
# SPACE PLASMA (Solar Wind)
# ============================================

PARKER_SOLAR_PROBE = _data["space"]["parker_solar_probe"]


# ============================================
# PLASMA PARAMETERS FUSION
# ============================================


def lawson_criterion(n_density_m3, T_keV, tau_s):
    """
    Lawson Triple Product: n * T * tau
    Ignition condition: n*T*tau > 3e21 keV s m^-3
    """
    return n_density_m3 * T_keV * tau_s


if __name__ == "__main__":
    print("=" * 60)
    print("PLASMA PHYSICS DATA")
    print("=" * 60)

    print("\nJET 2024 Record:")
    print(f"  Energy: {JET_RECORD_2024['energy_output_MJ']} MJ")
    print(f"  Duration: {JET_RECORD_2024['duration_sec']} s")
    print(f"  Temp: {JET_RECORD_2024['plasma_temp_C']/1e6:.1f} M C")

    print("\nITER Goals:")
    print(f"  Target Q: {ITER_DESIGN['target_Q']}")
    print(f"  First Plasma: {ITER_DESIGN['first_plasma']}")

    print("\nParker Solar Probe:")
    print(f"  Origin: {PARKER_SOLAR_PROBE['origin']}")
    print(f"  Discovery: {PARKER_SOLAR_PROBE['phenomena']}")
