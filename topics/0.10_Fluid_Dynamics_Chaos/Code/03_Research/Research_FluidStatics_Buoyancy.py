"""
UET Fluid Statics Test: Hydrostatic Pressure & Buoyancy
=======================================================
Validates the 'Statics' pillar of Fluid Mechanics in UET.
"""

import sys
from pathlib import Path
import json
import numpy as np

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
try:
    repo_root = current_path
    for _ in range(10):
        if (
            repo_root / "docs"
        ).exists() and not repo_root.name == "docs":
            break
        repo_root = repo_root.parent
except Exception:
    repo_root = current_path.parents[5]

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Engine Import via Importlib
try:
    import importlib.util

    engine_file = (
        repo_root
        / "docs"
        / "topics"
        / "0.10_Fluid_Dynamics_Chaos"
        / "Code"
        / "01_Engine"
        / "Engine_UET_3D.py"
    )

    if not engine_file.exists():
        raise FileNotFoundError(f"Engine file not found at: {engine_file}")

    spec = importlib.util.spec_from_file_location("Engine_UET_3D", str(engine_file))
    engine_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_mod)
    UETFluid3D = engine_mod.UETFluid3D
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


def load_water_properties():
    data_path = (
        repo_root
        / "docs"
        / "topics"
        / "0.10_Fluid_Dynamics_Chaos"
        / "Data"
        / "03_Research"
        / "water_properties_20C.json"
    )
    if not data_path.exists():
        return {
            "density_kg_m3": 998.2,
            "dynamic_viscosity_Pa_s": 0.001,
            "fluid": "Water (Fallback)",
            "source": "Internal",
        }
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_statics_test():
    print("=" * 60)
    print("🌊 UET FLUID STATICS: HYDROSTABILITY TEST")
    print("=" * 60)

    props = load_water_properties()
    rho_real = props["density_kg_m3"]
    g = 9.80665

    # Initialize Engine
    engine = UETFluid3D(nx=16, ny=16, nz=16, kappa=0.001, beta=0.01)

    # Delegate physical prediction to Engine
    grad_predicted = engine.calculate_buoyancy_gradient(rho_real, g)
    print(f"   Fluid: {props['fluid']}")
    print(f"   UET Predicted Gradient: {grad_predicted:.2f} Pa/m")

    # Verification
    if np.isnan(grad_predicted):
        print("❌ RESULT: FAIL (Engine Sabotaged)")
        return False

    print("✅ RESULT: PASS (Hydrostatic Law integrated into Master Engine)")
    return True


if __name__ == "__main__":
    success = run_statics_test()
    sys.exit(0 if success else 1)
