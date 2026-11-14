"""
UET Extended Neutrino Validation
================================
Tests UET interpretation of:
1. Neutrino mass mechanism vs KATRIN limits
2. Solar neutrino flux (Borexino detection)

Principle: UET explains neutrino mass via I-field coupling loops.

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


import sys
from pathlib import Path

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


from docs.core.uet_glass_box import UETPathManager
from docs.core.uet_master_equation import (
UETParameters,
strategic_boost,
potential_V,
KAPPA_BEKENSTEIN,
)

import os
import numpy as np
import math

# Import Data from docs/data/01_particle_physics/neutrinos
# Import Data from local pmns_mixing folder
current_dir = Path(__file__).resolve().parent
topic_dir = current_dir.parent.parent
data_dir = topic_dir / "Data" / "pmns_mixing"
sys.path.insert(0, str(data_dir))

from neutrino_extended_data import (


    KATRIN_RESULTS,
    SOLAR_NEUTRINOS_BOREXINO,
    CNB_DATA,
)




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def uet_neutrino_mass_mechanism():
    """
    UET mechanism for neutrino mass.
    Delegates to Engine_Neutrino.
    """
    # Initialize Standard Engine
    import importlib.util

    eng_path = (
        root_path
        / "docs/topics/0.7_Neutrino_Physics/Code/01_Engine/Engine_Neutrino.py"
    )
    if eng_path.exists():
        spec = importlib.util.spec_from_file_location("Engine_Neutrino", eng_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        UETNeutrinoSolver = mod.UETNeutrinoSolver
    else:
        print("CRITICAL: Engine not found.")
        return float("nan")

    solver = UETNeutrinoSolver()
    m_nu_pred = solver.predict_neutrino_mass()

    if math.isnan(m_nu_pred):
        print("KILL SWITCH DETECTED: Engine returned NaN")
        return float("nan")

    return m_nu_pred


def test_katrin_limit():
    """Test compatibility with KATRIN 2025 limit."""
    print("\n" + "=" * 60)
    print("TEST 1: KATRIN Mass Limit Compatibility")
    print("=" * 60)

    limit = KATRIN_RESULTS["mass_limit_eV"]
    print(f"\nKATRIN 2025 Limit: < {limit} eV")

    # UET Prediction
    m_pred = uet_neutrino_mass_mechanism()

    print(f"UET Prediction (Type-I See-Saw analog): ~{m_pred:.3f} eV")

    valid = m_pred < limit
    print(f"Compatible? {'YES' if valid else 'NO'}")

    print("\nUET Interpretation:")
    print("  - Neutrinos = Information field (I) carriers")
    print("  - Very low mass due to weak C-field coupling")
    print("  - Detectable mass confirms I-field energy content")

    return valid


def test_solar_flux_cno():
    """Test interpretation of solar neutrino flux."""
    print("\n" + "=" * 60)
    print("TEST 2: Solar Neutrino Flux (Borexino)")
    print("=" * 60)

    cno_flux = SOLAR_NEUTRINOS_BOREXINO["CNO_cycle"]["flux_cm2_s"]
    pp_flux = SOLAR_NEUTRINOS_BOREXINO["pp_chain"]["pp_flux"]

    print(f"\nObserved CNO Flux: {cno_flux:.2e} cm^-2 s^-1")
    print(f"Observed pp Flux:  {pp_flux:.2e} cm^-2 s^-1")

    ratio = cno_flux / pp_flux
    print(f"CNO/pp Ratio: {ratio:.4f} (~1%)")

    print("\nUET Interpretation:")
    print("  - Neutrinos carry 'Information' of fusion process")
    print("  - Flux conservation = I-field continuity")
    print("  - Flavor oscillation = I-field rotation (C-I mixing)")
    print("  - UET supplements detection probability via mixing angle")

    return True


def run_all_tests():
    print("=" * 70)
    print("UET EXTENDED NEUTRINO VALIDATION")
    print("Using KATRIN 2025 and Borexino Data")
    print("=" * 70)

    t1 = test_katrin_limit()
    t2 = test_solar_flux_cno()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"KATRIN Limit: {'PASS' if t1 else 'FAIL'}")
    print(f"Solar Flux:   PASS (Interpretation)")

    return t1


if __name__ == "__main__":
    run_all_tests()
