"""
UET Black Hole Physics Test
============================
Tests UET predictions against EHT data for:
- M87* black hole shadow
- Sgr A* black hole shadow
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

# --- PATH SETUP (Must be FIRST) ---
from docs import ROOT_PATH

ROOT = ROOT_PATH

TOPIC_DIR = ROOT / "docs" / "topics" / "0.2_Black_Hole_Physics"
DATA_PATH = TOPIC_DIR / "Data"

# Core Imports
from docs.core.uet_glass_box import UETPathManager, UETMetricLogger
from docs.core.uet_parameters import G, C, M_SUN

pc_to_m = 3.085677581e16
c = C
M_sun = M_SUN

import json
import math
import numpy as np
import platform
from datetime import datetime, timezone
from hashlib import sha256


def load_eht_data():
    """Load EHT black hole data from master source."""
    with open(DATA_PATH / "03_Research" / "black_hole_data.json") as f:
        raw_data = json.load(f)

    # Transform list to dict for easy access
    data = {item["name"]: item for item in raw_data["supermassive"]}
    return data


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


# --- DELEGATE MATH TO ENGINE ---
# Local math removed: schwarzschild_radius, shadow_radius, angular_size_uas


def run_test():
    """Run black hole physics tests."""
    print("=" * 60)
    print("UET BLACK HOLE PHYSICS TEST")
    print("Data: Event Horizon Telescope (M87*, Sgr A*)")
    print("Data: Event Horizon Telescope (M87*, Sgr A*)")
    print("=" * 60)

    # Initialize Standard Logger
    # This automatically creates: /Result/{timestamp}_EHT_Validation/
    # Initialize Standard Logger (V2.1 Showcase)
    result_dir_base = UETPathManager.get_result_dir(
        topic_id="0.2", experiment_name="EHT_Validation", category="showcase"
    )
    logger = UETMetricLogger("EHT_Validation", topic_id="0.2", category="showcase")

    # Save Metadata
    logger.set_metadata(
        {
            "data_source": "Event Horizon Telescope (EHT)",
            "targets": ["M87*", "Sgr A*"],
            "method": "UET_Schwarzschild_Shadow",
            "parameters": {"G": G, "c": c},
        }
    )

    print(f"\\n📂 Logging detailed results to: {logger.run_dir}")

    data = load_eht_data()
    results = []
    artifact_rows = []

    # Initialize Engine
    if "UETBlackHoleSolver" not in globals():
        import importlib.util

        topic_dir_path = Path(__file__).resolve().parent.parent.parent
        engine_path = topic_dir_path / "Code" / "01_Engine" / "Engine_BlackHole.py"
        if engine_path.exists():
            spec = importlib.util.spec_from_file_location("Engine_BlackHole", str(engine_path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            UETBlackHoleSolver = mod.UETBlackHoleSolver
        else:
            print("CRITICAL: Engine not found")
            return False

    # Initialize with default params (Room Temp Landauer or Unitary)
    solver = UETBlackHoleSolver()

    # Test 1: M87* Shadow
    print("\n[1] M87* Black Hole Shadow")
    print("-" * 40)

    m87 = data["M87*"]
    M_m87 = m87["mass_solar"]
    d_m87 = m87["distance_Mpc"] * 1e6 * pc_to_m  # Mpc to m
    theta_obs = m87["shadow_uas"]
    theta_err = m87["shadow_error_uas"]

    r_s = solver.compute_schwarzschild_radius(M_m87)
    # Note: Engine returns Diameter for shadow
    d_shadow = solver.compute_shadow_diameter(r_s)
    theta_uet = solver.compute_angular_size_uas(d_shadow, d_m87)

    error = abs(theta_uet - theta_obs) / theta_obs * 100

    print(f"  Mass:     {M_m87:.1e} M☉")
    print(f"  Distance: {m87['distance_Mpc']} Mpc")
    print(f"  Observed: {theta_obs} ± {theta_err} μas")
    print(f"  UET:      {theta_uet:.1f} μas")
    print(f"  Error:    {error:.1f}%")

    passed = abs(theta_uet - theta_obs) <= 2 * theta_err  # 2σ
    results.append(("M87* Shadow", error, passed))
    artifact_rows.append(
        {
            "target": "M87*",
            "mass_solar": M_m87,
            "distance_m": d_m87,
            "observed_shadow_uas": theta_obs,
            "observed_error_uas": theta_err,
            "predicted_shadow_uas": theta_uet,
            "relative_error_percent": error,
            "within_2sigma": bool(passed),
        }
    )
    print(f"  {'✅ PASS' if passed else '❌ FAIL'}")

    # Test 2: Sgr A* Shadow
    print("\n[2] Sgr A* Black Hole Shadow")
    print("-" * 40)

    sgra = data["Sgr A*"]
    M_sgra = sgra["mass_solar"]
    d_sgra = sgra["distance_kpc"] * 1e3 * pc_to_m  # kpc to m
    theta_obs_sgra = sgra["shadow_uas"]
    theta_err_sgra = sgra["shadow_error_uas"]

    r_s_sgra = solver.compute_schwarzschild_radius(M_sgra)
    d_shadow_sgra = solver.compute_shadow_diameter(r_s_sgra)
    theta_uet_sgra = solver.compute_angular_size_uas(d_shadow_sgra, d_sgra)

    error_sgra = abs(theta_uet_sgra - theta_obs_sgra) / theta_obs_sgra * 100

    print(f"  Mass:     {M_sgra:.1e} M☉")
    print(f"  Distance: {sgra['distance_kpc']} kpc")
    print(f"  Observed: {theta_obs_sgra} ± {theta_err_sgra} μas")
    print(f"  UET:      {theta_uet_sgra:.1f} μas")
    print(f"  Error:    {error_sgra:.1f}%")

    passed_sgra = abs(theta_uet_sgra - theta_obs_sgra) <= 2 * theta_err_sgra
    results.append(("Sgr A* Shadow", error_sgra, passed_sgra))
    artifact_rows.append(
        {
            "target": "Sgr A*",
            "mass_solar": M_sgra,
            "distance_m": d_sgra,
            "observed_shadow_uas": theta_obs_sgra,
            "observed_error_uas": theta_err_sgra,
            "predicted_shadow_uas": theta_uet_sgra,
            "relative_error_percent": error_sgra,
            "within_2sigma": bool(passed_sgra),
        }
    )
    print(f"  {'✅ PASS' if passed_sgra else '❌ FAIL'}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for _, _, p in results if p)
    total = len(results)

    for name, error, passed in results:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}: {error:.1f}% error")

    print(f"\nResult: {passed_count}/{total} PASSED")
    print("=" * 60)

    artifact = {
        "schema_version": "1.1",
        "topic": "0.2_Black_Hole_Physics",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.2_Black_Hole_Physics/Code/03_Research/Research_EHT_Validation.py",
        "status": "PASS" if passed_count == total else "FAIL",
        "claim_class": "C internal benchmark",
        "inputs": [
            {
                "path": str((DATA_PATH / "03_Research" / "black_hole_data.json").relative_to(TOPIC_DIR)),
                "sha256": hash_file(DATA_PATH / "03_Research" / "black_hole_data.json"),
                "role": "EHT shadow benchmark working copy",
            }
        ],
        "thresholds": {
            "per_target": "abs(predicted_shadow_uas - observed_shadow_uas) <= 2 * observed_error_uas"
        },
        "metrics": {
            "passed_targets": passed_count,
            "total_targets": total,
            "all_targets_within_2sigma": passed_count == total,
        },
        "results": artifact_rows,
        "limitations": [
            "Uses compact GR shadow diameter approximation D_shadow = 5.2 Rs.",
            "Topic-local EHT data package is a working copy, not a fully normalized upstream archive.",
            "This artifact does not prove singularity resolution or a GR replacement.",
        ],
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy_version": np.__version__,
        },
    }
    artifact_path = TOPIC_DIR / "Result" / "artifacts" / "0_2_black_hole_physics_verification.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Artifact saved to {artifact_path}")

    # --- VISUALIZATION ---
    # Delegated to Code/05_Visualization/Vis_BlackHole_Signature.py
    print("  [Note] Run Vis_BlackHole_Signature.py for EHT shadow plots.")

    return passed_count == total

    # Save Final Report
    logger.log_step(
        step=1,
        time_val=1.0,
        omega=1.0,
        entropy=0.0,
        extra_metrics={"Passed": passed_count, "Total": total},
    )
    logger.save_report()

    return passed_count == total


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
