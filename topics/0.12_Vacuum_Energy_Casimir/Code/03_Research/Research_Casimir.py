"""
UET Casimir Effect Test
========================
Topic: 0.12 - Vacuum Energy
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import platform

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
current_path = Path(__file__).resolve()
root_path = ROOT_PATH
import sys
from pathlib import Path

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


# Engine Import (Dynamic)
try:
    import importlib.util

    engine_file = (
        root_path
        / "docs"
        / "topics"
        / "0.12_Vacuum_Energy_Casimir"
        / "Code"
        / "01_Engine"
        / "Engine_Vacuum.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Vacuum", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETVacuumEngine = getattr(module, "UETVacuumEngine")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)

import json
import math
import numpy as np






# Standardized UET Root Path
TOPIC_DIR = root_path / "docs" / "topics" / "0.12_Vacuum_Energy_Casimir"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_12_vacuum_energy_casimir_verification.json"

def load_casimir_data():
    """Load Mohideen & Roy 1998 Data."""
    # Try multiple standard locations
    candidates = [
        root_path
        / "docs"
        / "topics"
        / "0.12_Vacuum_Energy_Casimir"
        / "Code"
        / "03_Research"
        / "mohideen_1998_casimir.json",
        root_path
        / "docs"
        / "topics"
        / "0.12_Vacuum_Energy_Casimir"
        / "Data"
        / "03_Research"
        / "mohideen_1998_casimir.json",
        current_path.parent / "mohideen_1998_casimir.json",
    ]

    for path in candidates:
        if path.exists():
            with open(path, "r") as f:
                return json.load(f), path

    raise FileNotFoundError("Data not found (checked standard locations)")


def file_sha256(path):
    digest = sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_artifact(artifact):
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")


def run_test():
    engine = UETVacuumEngine()
    print("=" * 70)
    print("UET CASIMIR EFFECT TEST")
    print("Data: Mohideen & Roy 1998")
    print("=" * 70)

    try:
        data, data_path = load_casimir_data()
    except FileNotFoundError as e:
        artifact = {
            "schema_version": "1.1",
            "topic": "0.12_Vacuum_Energy_Casimir",
            "status": "FAIL",
            "claim_class": "E - blocked, missing primary dataset",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "command": "python docs/topics/0.12_Vacuum_Energy_Casimir/Code/03_Research/Research_Casimir.py",
            "failure_reason": str(e),
        }
        write_artifact(artifact)
        print(f"FAIL: {e}")
        return False

    measurements = data["measurements"]
    separations = [m["d_nm"] for m in measurements]
    # Convert pN -> nN (1 pN = 0.001 nN)
    forces_exp = [abs(m["F_measured_pN"]) * 1e-3 for m in measurements]

    print("\n[1] CASIMIR FORCE MEASUREMENTS")
    print("-" * 50)
    print("| Separation (nm) | F_exp (nN) | F_UET (nN) | Error |")
    print("|:----------------|:-----------|:-----------|:------|")

    results = []
    rows = []
    for d, F_exp in zip(separations, forces_exp):
        F_uet = engine.calculate_physical_casimir_force(d, radius_um=200.0)
        error = abs(abs(F_uet) - F_exp) / F_exp * 100 if F_exp > 0 else 0
        print(f"| {d:15} | {F_exp:10.4f} | {F_uet:10.4f} | {error:5.1f}% |")
        results.append(error)
        rows.append(
            {
                "separation_nm": d,
                "experimental_force_nN": F_exp,
                "model_force_nN": F_uet,
                "absolute_model_force_nN": abs(F_uet),
                "relative_error_percent": error,
            }
        )

    avg_error = sum(results) / len(results)
    max_error = max(results)
    threshold = {
        "average_relative_error_percent_max": 10.0,
        "max_relative_error_percent_max": 15.0,
    }

    print(f"\nAverage Error: {avg_error:.1f}%")
    print(f"Max Error: {max_error:.1f}%")
    passed = (
        avg_error <= threshold["average_relative_error_percent_max"]
        and max_error <= threshold["max_relative_error_percent_max"]
    )
    status = "PASS" if passed else "FAIL"
    print(f"\n{status} - UET Casimir Validation")

    # --- PLOTTING FOR SHOWCASE ---
    try:
        import matplotlib.pyplot as plt

        # Get Standard Showcase Path
        from docs.core.uet_glass_box import UETPathManager

        output_dir = UETPathManager.get_result_dir(
            topic_id="0.12", experiment_name="Casimir_Validation", category="showcase"
        )

        plt.figure(figsize=(10, 6))
        plt.loglog(separations, forces_exp, "ro", label="Exp: Mohideen (1998)")
        plt.loglog(
            separations,
            [
                abs(f)
                for f in [engine.calculate_physical_casimir_force(d, 200.0) for d in separations]
            ],
            "b-",
            label="UET Prediction",
        )

        plt.xlabel("Separation d (nm)")
        plt.ylabel("Casimir Force F (nN)")
        plt.title(f"Vacuum Energy Validation: UET vs Experiment (Err: {avg_error:.1f}%)")
        plt.grid(True, which="both", ls="-", alpha=0.5)
        plt.legend()

        output_path = output_dir / "Casimir_Validation_Plot.png"
        plt.savefig(output_path, dpi=300)
        print(f"📸 Showcase Image Saved: {output_path}")

    except Exception as e:
        print(f"⚠️ Could not generate plot: {e}")

    artifact = {
        "schema_version": "1.1",
        "topic": "0.12_Vacuum_Energy_Casimir",
        "status": status,
        "claim_class": "C - source-backed internal benchmark for Casimir force only",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.12_Vacuum_Energy_Casimir/Code/03_Research/Research_Casimir.py",
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "inputs": [
            {
                "path": str(data_path.relative_to(root_path)).replace("\\", "/"),
                "sha256": file_sha256(data_path),
                "source": data.get("paper", "Mohideen & Roy, PRL 81, 4549 (1998)"),
                "geometry": data.get("geometry", "sphere-plate"),
                "material": data.get("material", "gold"),
                "sphere_radius_um_dataset": data.get("sphere_radius_um"),
                "sphere_radius_um_model": 200.0,
            }
        ],
        "formula_ids": [
            "VAC-SPHERE-PFA",
            "VAC-FINITE-CONDUCTIVITY",
        ],
        "threshold": threshold,
        "metrics": {
            "average_relative_error_percent": avg_error,
            "max_relative_error_percent": max_error,
            "point_count": len(rows),
        },
        "results": rows,
        "limitations": [
            "This artifact validates the topic-local sphere-plate Casimir benchmark only.",
            "It does not validate the dark-energy anchor or solve the cosmological-constant problem.",
            "The engine uses a clipped finite-conductivity correction and a 200 um model radius against a 196 um dataset radius.",
        ],
    }
    write_artifact(artifact)
    print(f"Artifact written: {ARTIFACT_PATH}")

    return passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
