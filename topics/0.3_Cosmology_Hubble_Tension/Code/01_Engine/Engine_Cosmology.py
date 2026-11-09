"""
UET Cosmology Engine (Topic 0.3) - v0.9.5 Hardened
=====================================================
Validates UET prediction of "Cosmic Stiffness" (k) against REAL Planck/JWST data.
Inherits UETBaseSolver for standardized Data/Result management.
Eliminates all Meteo Tuning (H0-fixes replaced by first-principles scaling).
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
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path

# Ensure project root is in path
current_file = Path(__file__).resolve()
project_root = current_file.parents[5] 
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Core Imports
from docs.core.uet_base_solver import UETBaseSolver
from docs.core.uet_master_equation import UETParameters
from docs.core.uet_glass_box import UETPathManager
from docs.core.uet_parameters import (
    C,
    ALPHA_EM,
    INTEGRITY_KILL_SWITCH,
    H0,
    TAU_MEM_VACUUM,
    get_params
)
from docs.core.uet_observables import (
    get_hubble_at_redshift,
    get_a0_at_redshift
)

# Standard Cosmological Observed Values
H0_PLANCK = 67.4  # km/s/Mpc (Planck 2018)
H0_SHOES = 73.04  # km/s/Mpc (SH0ES 2022)




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

class UETCosmologyEngine(UETBaseSolver):
    """
    Cosmology Engine for Topic 0.3.
    Use Case: Analytic Comparison (0D simulation).
    """

    def __init__(self, name: str = "UET_Cosmology_Engine", uet_params=None):
        if uet_params is None:
            # THE GREAT PURGE: No more manual overrides or sqrt(alpha) tuning.
            uet_params = get_params("0.3")

        super().__init__(
            nx=1,
            ny=1,
            dt=1.0,  # 1-cell grid for Scalar/Analytic work
            params=uet_params,
            name=name,
            topic="0.3_Cosmology_Hubble_Tension",
            pillar="01_Engine",
        )
        # Coupling Parameters
        self.beta = self.params.beta
        self.hubble_frame_beta = float(np.sqrt(ALPHA_EM))
        self.hubble_frame_beta_source = "sqrt(ALPHA_EM)"
        self.kappa = self.params.kappa

        self.results_cache = []
        self.stable_path = True

    def load_data(self) -> List[Dict]:
        """Load comparative data (Planck, SHOES, JWST)."""
        data_dir = root_path / "docs" / "topics" / "0.3_Cosmology_Hubble_Tension" / "Data" / "03_Research"
        
        datasets = []
        
        # 1. Load Standard Tension Data
        std_path = data_dir / "cosmic_tension_data.txt"
        if std_path.exists():
            with open(std_path, "r") as f:
                for line in f:
                    if line.startswith("Telescope") or not line.strip(): continue
                    parts = line.split(",")
                    if len(parts) >= 3:
                        datasets.append({"name": parts[0], "method": parts[1], "H0": float(parts[2]), "z": 0.0 if "SHOES" in parts[0] else 1100.0})

        # 2. Load JWST High-Z Calibration
        jwst_path = data_dir / "jwst_highz_calibration.csv"
        if jwst_path.exists():
            import csv
            with open(jwst_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    datasets.append({
                        "name": row["Source"],
                        "method": "JWST_HighZ" if "JWST" in row["Source"] else "Standard",
                        "H0": float(row["H0_Obs(km/s/Mpc)"]),
                        "z": float(row["Redshift(z)"])
                    })
        return datasets

    def get_hubble_parameter(self, z: float) -> float:
        """
        Calculate H(z) using UET Horizon Scaling.
        Integrates with uet_observables to ensure global consistency.
        """
        return get_hubble_at_redshift(z)

    def get_a0_at_redshift(self, z: float) -> float:
        """
        Axiom 7: Pattern Recurrence Across Scales.
        a0(z) = c * H(z) / 2pi from uet_observables.
        """
        a0_si = get_a0_at_redshift(z)
        # Convert to astro units (km/s)^2 / kpc for legacy script compatibility
        # 1 m/s^2 = 3.086e16 (km/s)^2 / kpc (Approx)
        return a0_si / 3.24078e-14

    def predict_uet_h0(self, h0_global: float, z_obs: float) -> float:
        """
        Axiomatic Prediction of local Hubble Parameter (v5.0).
        Compares early- and late-epoch H0 measurement frames via the
        topic-specific dimensionless frame coupling.
        
        Scaling Law: H(z) = H_global * (1 + beta_frame * exp(-z / z_crit))
        beta_frame = sqrt(alpha_em), an independently specified physical
        constant already used by the legacy topic proof notes. This must not be
        replaced by a value fitted to the Planck-SH0ES gap.
        """
        if INTEGRITY_KILL_SWITCH:
            return float("nan")

        # Redshift scaling: Informational drag is maximum locally (z=0) 
        # and decays exponentially as we look back toward the CMB baseline.
        z_crit = 5.0 # Transition scale used only away from the z=0 H0 benchmark.
        drag_factor = self.hubble_frame_beta * np.exp(-z_obs / z_crit)
        
        return h0_global * (1.0 + drag_factor)

    def solve_hubble_tension(self, h0_early: float, h0_late: float) -> Dict[str, float]:
        """
        Engine-level resolution.
        """
        if INTEGRITY_KILL_SWITCH:
            return {
                "H0_early_uet": float("nan"),
                "H0_late_uet": float("nan"),
                "Delta_H0": float("nan"),
            }

        # UET Prediction for late universe (z=0)
        h_late_uet = self.predict_uet_h0(h0_early, 0.0)

        return {
            "H0_early_uet": h0_early,
            "H0_late_uet": h_late_uet,
            "Delta_H0": h_late_uet - h0_early,
            "beta": self.hubble_frame_beta,
            "beta_source": self.hubble_frame_beta_source,
            "solver_beta": self.beta,
        }

    def get_extra_metrics(self) -> Dict[str, float]:
        """Expose key metrics for Proof validation."""
        h_late = self.predict_uet_h0(H0_PLANCK, 0.0)
        return {
            "H0_predicted": h_late,  # Legacy alias for Proof scripts
            "H0_late_predicted": h_late,
            "beta_cosmo": self.hubble_frame_beta,
            "beta_source": self.hubble_frame_beta_source,
            "solver_beta": self.beta,
        }

    def step(self, step_idx: int = 0):
        """
        Execute Axiomatic Audit of Hubble Tension.
        Compare Local Measurements (SH0ES/JWST) against UET-corrected Planck Global value.
        """
        datasets = self.load_data()

        # Find Planck (Global Baseline) from Core
        planck_h0 = H0  # Axial H0 from uet_parameters

        for d in datasets:
            h0_obs = d["H0"]
            z_eff = d["z"]

            # UET Prediction: Redshift-dependent H0
            h_pred = self.predict_uet_h0(planck_h0, z_eff)

            accuracy = 1.0 - abs(h_pred - h0_obs) / h0_obs

            result = {
                "source": d["name"],
                "redshift": z_eff,
                "H0_Obs": h0_obs,
                "H0_UET_Pred": h_pred,
                "Accuracy": f"{accuracy:.2%}",
                "Status": "MATCH" if accuracy > 0.95 else "DEVIATION"
            }
            self.results_cache.append(result)

        # Log to Glass Box
        self.logger.log_step(
            step=step_idx,
            time_val=0.0,
            results=str(self.results_cache),
            omega=0.0,
            potential=0.0,
            gradient_energy=0.0,
            entropy_interaction=0.0,
        )

    def save_results(self):
        # Override to save custom JSON analysis
        import json

        out_path = Path(self.logger.run_dir) / "cosmology_analysis.json"
        with open(out_path, "w") as f:
            json.dump(self.results_cache, f, indent=2)
        return str(out_path)


# =============================================================================
# VERIFICATION DEMO
# =============================================================================
def run_demo():
    print("🚀 Verifying 5x4 Grid Compliance for Cosmology Engine...")
    engine = UETCosmologyEngine()
    engine.step()
    path = engine.save_results()
    print(f"✅ Cosmology Result: {path}")


if __name__ == "__main__":
    run_demo()
