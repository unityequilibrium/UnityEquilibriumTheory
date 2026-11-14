"""
UET Superfluids Test - Helium-4
================================
Tests UET prediction for superfluid properties.
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
import math
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH

# Import Engines and Data
try:
    import importlib.util

    # Topic 0.4 Engine
    engine_path = (
        root_path
        / "docs"
        / "topics"
        / "0.4_Superconductivity_Superfluids"
        / "Code"
        / "01_Engine"
        / "Engine_Superconductivity.py"
    )
    spec_eng = importlib.util.spec_from_file_location("Engine_Supercon", str(engine_path))
    mod_eng = importlib.util.module_from_spec(spec_eng)
    spec_eng.loader.exec_module(mod_eng)
    AllenDynesEngine = mod_eng.AllenDynesEngine

    # Topic 0.4 Data
    data_path = (
        root_path
        / "docs"
        / "topics"
        / "0.4_Superconductivity_Superfluids"
        / "Data"
        / "03_Research"
        / "superfluid_data.py"
    )
    spec_data = importlib.util.spec_from_file_location("SuperfluidData", str(data_path))
    mod_data = importlib.util.module_from_spec(spec_data)
    spec_data.loader.exec_module(mod_data)
    HE4_DATA = mod_data.HELIUM_4_SUPERFLUID

    from docs.core.uet_glass_box import UETPathManager
except Exception as e:
    print(f"CRITICAL SETUP ERROR: {e}")
    sys.exit(1)

# Initialize Engine
engine = AllenDynesEngine()


def uet_lambda_point():
    """Delegated to Engine."""
    return engine.compute_lambda_point(rho=HE4_DATA["density_kg_m3"])


def uet_quantum_circulation():
    """Delegated to Engine."""
    # From Donnelly 1998: kappa = h/m_He4 = 9.97e-4 cm^2/s
    return engine.compute_quantum_vortex()


def run_test():
    """Run superfluid test."""
    print("=" * 70)
    print("UET SUPERFLUID TEST - HELIUM-4")
    print("Data: Donnelly 1998")
    print("=" * 70)

    results = []

    # Test 1: Lambda point
    print("\n[1] LAMBDA TRANSITION TEMPERATURE")
    print("-" * 50)

    T_obs = HE4_DATA["lambda_point_K"]
    T_uet = uet_lambda_point()

    print(f"  Observed: T_lambda = {T_obs:.4f} K")
    print(f"  UET:      T_lambda = {T_uet:.4f} K")

    error = abs(T_uet - T_obs) / T_obs * 100
    print(f"  Error: {error:.1f}%")

    passed = error < 10
    results.append(passed)
    print(f"  {'PASS' if passed else 'FAIL'}")

    # Test 2: Quantum of circulation
    print("\n[2] QUANTUM OF CIRCULATION")
    print("-" * 50)

    # h / m_He4 ~ 9.97e-4 cm^2/s
    kappa_obs = 9.97e-4
    kappa_uet = uet_quantum_circulation()

    print(f"  Observed: kappa = {kappa_obs:.3e} cm^2/s")
    print(f"  UET:      kappa = {kappa_uet:.3e} cm^2/s")

    error_k = abs(kappa_uet - kappa_obs) / kappa_obs * 100
    print(f"  Error: {error_k:.1f}%")

    passed = error_k < 5
    results.append(passed)
    print(f"  {'PASS' if passed else 'FAIL'}")

    passed_count = sum(results)
    total = len(results)

    print("=" * 70)
    print(f"RESULT: {passed_count}/{total} PASSED")
    print("=" * 70)

    # Save Report
    try:
        result_dir_base = UETPathManager.get_result_dir(
            topic_id="0.4",
            experiment_name="Research_Superfluids",
            pillar="03_Research",
            category="log",
        )
        report_path = result_dir_base / "superfluids_report.txt"
        with open(report_path, "w") as f:
            f.write(f"UET Superfluids Test Results\nPassed: {passed_count}/{total}\n")
        print(f"Report saved to {report_path}")
    except Exception as e:
        # Fallback to local Result dir
        local_res = Path("Result")
        local_res.mkdir(exist_ok=True)
        with open(local_res / "superfluids_report.txt", "w") as f:
            f.write(f"UET Superfluids Test Results\nPassed: {passed_count}/{total}\n")

    return passed_count >= 1


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
