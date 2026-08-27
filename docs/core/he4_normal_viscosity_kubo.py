"""Physical He-4 normal-component viscosity record for Topic 13."""

from __future__ import annotations

import hashlib
from pathlib import Path

from docs.core.he4_o2_response_calibration import calibration_record


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "he4_svp_normal_viscosity_kubo_source_package.json"
)


def source_hash() -> str:
    return hashlib.sha256(PACKAGE.read_bytes()).hexdigest()


def physical_transport_record() -> dict:
    """Return the source-locked SI shear coefficient and response contracts."""

    calibration = calibration_record()
    return {
        "coefficient_name": "normal_component_shear_viscosity_eta",
        "value": 1.29e-6,
        "uncertainty": 5.0e-8,
        "units": "Pa s",
        "unit_lane": "SI",
        "hydrodynamic_frame": "Landau two-fluid local rest frame; normal-component shear channel",
        "state": {
            "temperature_K": 1.7,
            "chemical_potential": 0.0,
            "chemical_potential_definition": "delta_mu relative to the declared SVP equilibrium state; gauge reference, not absolute atomic chemical potential",
            "space_response": float(calibration["superfluid_fraction_reference"]),
            "space_response_definition": "rho_s/rho on the calibrated local He-4 response lane",
            "phase": "He II",
            "pressure_path": "saturated vapour pressure",
        },
        "correlator_formula_id": "standard.green_kubo.shear_viscosity",
        "correlator_locator": "eta=V/(k_B T) integral_0^infinity dt <delta_Pi_xy(t) delta_Pi_xy(0)>; equivalently eta=-lim_(omega->0+) Im G_R^(xy,xy)/omega",
        "source_locator": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/he4_svp_normal_viscosity_kubo_source_package.json; Donnelly-Barenghi Table 12.3 at 1.70 K",
        "source_hash": source_hash(),
        "evidence_status": "SOURCE_LOCKED",
        "kms_fdt": {
            "status": "PASS",
            "relation": "G_K=coth(hbar omega/(2 k_B T)) (G_R-G_A)",
            "classical_low_frequency_noise": "<Xi_xy Xi_xy>=2 k_B T eta delta",
        },
        "entropy_mapping": {
            "status": "PASS",
            "relation": "nabla_mu J_S^mu contains 2 eta sigma_mu_nu sigma^mu_nu/T",
            "positivity_basis": "eta minus uncertainty remains positive",
        },
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "fit_or_tuning_used": False,
        },
        "data_role": "EXTERNAL_INPUT_NOT_UET_PREDICTION",
    }
