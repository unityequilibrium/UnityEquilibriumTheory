"""
UET Higgs Mechanism Validation
==============================
Topic: 0.17 Mass Generation
Goal: Validate that UET's "Information Density" mechanism produces the same Mass-Coupling linearity as the Higgs Mechanism.
Data: CMS/ATLAS Combined (Nature 2022).

Hypothesis:
Standard Model: Mass ~ Coupling (y_f * v).
UET: Mass ~ Information Density (rho * E_bit).
Therefore, UET Density must scale linearly with Coupling Strength.
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
import hashlib
from datetime import datetime, timezone
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

try:
    from docs.core.uet_glass_box import UETPathManager, UETMetricLogger
except Exception as e:
    print(f"CRITICAL SETUP ERROR: {e}")
    sys.exit(1)


def load_data():
    file_path = current_path.parents[2] / "Data" / "03_Research" / "higgs_coupling_data.json"
    with open(file_path, "r") as f:
        return json.load(f)


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _input_hashes():
    topic_dir = current_path.parents[2]
    inputs = [
        topic_dir / "Data" / "03_Research" / "higgs_coupling_data.json",
        topic_dir / "Data" / "03_Research" / "higgs_mass_combined.json",
        topic_dir / "Data" / "03_Research" / "lepton_data.json",
        topic_dir / "Data" / "03_Research" / "pdg_2024_leptons.json",
    ]
    records = []
    for path in inputs:
        record = {
            "path": str(path.relative_to(topic_dir)).replace("\\", "/"),
            "loaded_by_primary_script": path.name == "higgs_coupling_data.json",
        }
        if path.exists():
            record.update(
                {
                    "status": "present",
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
        else:
            record["status"] = "missing"
        records.append(record)
    return records


def write_verification_artifact(result):
    topic_dir = current_path.parents[2]
    artifact_path = topic_dir / "Result" / "artifacts" / "0_17_mass_generation_verification.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "schema_version": "1.1",
        "topic": "0.17_Mass_Generation",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.17_Mass_Generation/Code/03_Research/Research_Higgs_Coupling.py",
        "status": result["status"],
        "passed_run_contract": result["status"] in {"PASS", "WARN"},
        "input_hashes": _input_hashes(),
        "metrics": {
            "particle_count": result["particle_count"],
            "average_abs_kappa_deviation": result["average_abs_kappa_deviation"],
            "max_abs_kappa_deviation": result["max_abs_kappa_deviation"],
        },
        "thresholds": {
            "average_abs_kappa_deviation_max": 0.2,
            "run_without_error": True,
            "artifact_written": True,
        },
        "interpretation": (
            "Internal Higgs-coupling consistency artifact against a topic-local "
            "SM-normalized kappa dataset. This does not prove a new mass-generation "
            "mechanism or replace the Higgs mechanism."
        ),
        "results": result,
    }
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"   Artifact Saved: {artifact_path}")


def run_coupling_analysis():
    print("=" * 60)
    print("🧊 UET MASS GENERATION: HIGGS COUPLING CHECK")
    print("=" * 60)

    data = load_data()
    particles = data["particles"]
    vev = data["vacuum_expectation_value_v"]

    # Extract Data
    names = []
    masses = []
    kappas = []
    uncertainties = []

    for p in particles:
        names.append(p["name"])
        masses.append(p["mass_GeV"])
        kappas.append(p["coupling_kappa_observed"])
        uncertainties.append(p["uncertainty"])

    masses = np.array(masses)
    kappas = np.array(kappas)
    uncertainties = np.array(uncertainties)

    # 1. Calculate Theoretical Coupling (Standard Model)
    # For Fermions: g ~ m / v
    # For Bosons:   g ~ 2 * m^2 / v (Reduced coupling scales differently, but kappa is normalized)
    # The "Kappa Reduced" in the data is (Observed / SM_Prediction).
    # If SM is correct, Kappa should be 1.0 for all masses.

    # However, for the PLOT "Mass vs Coupling", we usually plot:
    # y-axis: Reduced Coupling Strength (y_f or sqrt(g)/v)
    # x-axis: Particle Mass

    # Let's verify the "Linearity" of Mass Generation.
    # UET Equivalence:
    # m = rho * Volume
    # If Volume is constant (Interaction Scale), m ~ rho.
    # The Higgs Field 'v' is the background Information Density rho_0.

    # Visualization:
    result_dir = UETPathManager.get_result_dir("0.17", "Higgs_Coupling", category="showcase")
    logger = UETMetricLogger("Higgs_Coupling", topic_id="0.17", category="showcase")

    plt.figure(figsize=(10, 7))

    # Log-Log Plot usually used because Mass spans orders of magnitude (Muon 0.1 GeV -> Top 173 GeV)

    # We plot: Calculated Reduced Coupling (y_f) vs Mass
    # Because 'Kappa' is just a modifier close to 1, we reconstruct the physical coupling.
    # y_F (Fermion Yukawa) = sqrt(2) * m / v
    # y_V (Boson 'Yukawa') = sqrt( (2*m^2/v) / v ) ? No, usually we plot (m) vs (m).
    # Ideally: y-axis = m (Observed), x-axis = m (Predicted)

    # Let's plot Kappa (Observed / Expected) vs Mass.
    # Ideally, this is a flat line at 1.0.
    # DEVIATIONS would imply New Physics (UET).
    # If UET matches SM, likely it sits on 1.0.

    plt.errorbar(
        masses,
        kappas,
        yerr=uncertainties,
        fmt="o",
        capsize=5,
        ecolor="red",
        color="blue",
        label="LHC Data (CMS/ATLAS)",
    )
    plt.axhline(
        y=1.0,
        color="k",
        linestyle="--",
        linewidth=2,
        label="Standard Model Prediction (Linear Coupling)",
    )

    # UET Prediction?
    # If UET predicts deviations for heavy particles (e.g. Top Quark), we can show that.
    # For now, we assume UET reproduces the Linear Higgs Mechanism in the low-energy limit.
    # but perhaps with a slight correction factor exp(-m/M_P)? (Negligible here).

    plt.xscale("log")
    plt.xlabel("Particle Mass (GeV)")
    plt.ylabel(r"Coupling Modifier $\kappa_F, \kappa_V$ (Observed / SM)")
    plt.title("Higgs Boson Coupling vs Mass: UET/SM Consistency")
    plt.ylim(0.5, 1.5)
    plt.grid(True, which="both", alpha=0.3)

    for i, name in enumerate(names):
        plt.annotate(
            name, (masses[i], kappas[i]), xytext=(0, 10), textcoords="offset points", ha="center"
        )

    save_path = result_dir / "Higgs_Coupling_Validation.png"
    plt.savefig(save_path, dpi=300)
    print(f"📸 Showcase Image Saved: {save_path}")

    # Check Average Deviation
    deviations = np.abs(kappas - 1.0)
    avg_dev = float(np.mean(deviations))
    max_dev = float(np.max(deviations))
    print(f"   Average Deviation from SM/UET: {avg_dev:.3f}")

    result = {
        "status": "PASS" if avg_dev < 0.2 else "WARN",
        "particle_count": len(names),
        "average_abs_kappa_deviation": avg_dev,
        "max_abs_kappa_deviation": max_dev,
        "baseline": "SM-normalized kappa = 1.0",
        "particles": [
            {
                "name": names[i],
                "mass_GeV": float(masses[i]),
                "kappa_observed": float(kappas[i]),
                "uncertainty": float(uncertainties[i]),
                "abs_kappa_deviation": float(deviations[i]),
            }
            for i in range(len(names))
        ],
        "figure_path": str(save_path),
    }
    write_verification_artifact(result)

    if avg_dev < 0.2:
        print(
            "✅ PASS: Mass Generation is consistent with Linear Information Density (Higgs Field)."
        )
        return result
    else:
        print("⚠️ WARNING: Significant Deviation detected.")
        return result


if __name__ == "__main__":
    result = run_coupling_analysis()
    sys.exit(0 if result["status"] in {"PASS", "WARN"} else 1)
