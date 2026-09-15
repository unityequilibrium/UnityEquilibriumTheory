"""Cross-module formal thermodynamic bridge integration for Topic 13.

This module checks that the named normalized EOS, formal SK/KMS interface,
entropy-current contract, and covariant heat-flux balance compose without
changing ontology or introducing an SI calibration. It is an internal
formal-lane witness, not physical transport or TTG validation.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from docs.core.thermal_collective_response_eos import (
    CollectiveResponseEOSInputs,
    collective_response_eos_contract,
    local_stability,
)
from docs.core.thermal_response_beta_contract import ThermalResponseBetaInputs
from docs.core.thermal_sk_kms_entropy_contract import (
    entropy_production_witness,
    sk_kms_noise_kernel,
    thermal_sk_kms_entropy_contract,
)
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    DEFAULT_FOUR_VELOCITY,
    DEFAULT_METRIC,
    DEFAULT_THERMAL_FORCE_COVARIANT,
    covariant_entropy_heat_flux,
    covariant_entropy_heat_flux_balance_contract,
)


FORMAL_T13_BRIDGE_STATUS = "PASS_FORMAL_T13_THERMODYNAMIC_BRIDGE_INTEGRATION"


def formal_thermodynamic_bridge_witness() -> dict[str, Any]:
    """Return deterministic cross-module witnesses for the formal bridge."""

    eos_inputs = CollectiveResponseEOSInputs(
        thermal=ThermalResponseBetaInputs(300.0, 1.2, 0.18, 0.4, 0.3),
        a_c=1.1,
        b_c=0.5,
    )
    eos_contract = collective_response_eos_contract()
    stability = local_stability(300.0, 0.2, 0.4, eos_inputs)
    sk_contract = thermal_sk_kms_entropy_contract()
    entropy_value = entropy_production_witness(
        np.array((-0.2, 0.4), dtype=float),
        np.array(((1.2, 0.15), (0.15, 0.8)), dtype=float),
    )
    kms_value = sk_kms_noise_kernel(2.0e20, 1.0e-22, 0.7)
    heat = covariant_entropy_heat_flux(
        DEFAULT_METRIC,
        DEFAULT_FOUR_VELOCITY,
        1.0,
        1.0,
        0.75,
        DEFAULT_THERMAL_FORCE_COVARIANT,
    )
    heat_contract = covariant_entropy_heat_flux_balance_contract()

    checks = {
        "eos_local_stability": bool(stability["locally_stable"]),
        "eos_mixed_reciprocity": bool(stability["mixed_derivatives_equal"]),
        "beta_symbols_remain_separate": "not beta_th" in sk_contract["beta_T13_relation"],
        "kms_noise_witness_nonnegative": kms_value >= 0.0,
        "onsager_entropy_witness_nonnegative": entropy_value >= 0.0,
        "heat_flux_entropy_production_nonnegative": heat["entropy_production"] >= 0.0,
        "heat_flux_orthogonal_to_velocity": heat["heat_flux_orthogonality_residual"] <= 1.0e-12,
        "thermal_force_orthogonal_to_velocity": heat["force_orthogonality_residual"] <= 1.0e-12,
        "formal_balance_equation_present": "dissipative_balance" in sk_contract,
        "covariant_balance_equation_present": "conserved_dissipative_balance" in heat_contract["equations"],
        "phi_remains_effective_response": "effective response variable" in heat_contract["unit_contract"]["Phi"],
        "c_remains_collective": "collective system-behaviour coordinate" in heat_contract["unit_contract"]["C"],
        "r_gen_remains_derived": "derived history trace" in heat_contract["unit_contract"]["R_gen"],
        "no_physical_kubo_coefficient": heat_contract["excluded"]["physical_Kubo_coefficient"],
        "no_si_heat_flux": heat_contract["excluded"]["SI_heat_flux"],
        "no_alpha_calibration": heat_contract["excluded"]["alpha_Phi_K"],
        "no_holdout": True,
    }
    return {
        "status": FORMAL_T13_BRIDGE_STATUS,
        "contract_ids": {
            "eos": "T13-THERMAL-EOS-001",
            "sk_kms": sk_contract["contract_id"],
            "covariant_entropy_heat_flux": "T13-O2-COVARIANT-ENTROPY-HEAT-FLUX-001",
        },
        "equations": {
            "normalized_eos": eos_contract["functional"],
            "eos_reciprocity": eos_contract["reciprocity"],
            "sk_action": sk_contract["sk_action"],
            "kms_relation": sk_contract["kms_relation"],
            "entropy_current": sk_contract["entropy_current"],
            "entropy_production": sk_contract["entropy_production"],
            "heat_flux": heat_contract["equations"]["covariant_heat_flux"],
            "dissipative_balance": sk_contract["dissipative_balance"],
        },
        "units": {
            "normalized_eos": "f_hat dimensionless; f=e0*f_hat only after external e0 in J m^-3",
            "beta_T13": "dimensionless stiffness-temperature slope; beta_th remains 1/(k_B T)",
            "sk_kms": "formal local notation with T in K and beta_th in J^-1",
            "heat_flux": "finite-cutoff natural-unit response; not W m^-2",
            "entropy_current": "formal natural-unit current; SI scale remains external",
            "phi": "effective response variable; normalization and alpha_Phi_K remain open",
        },
        "witness": {
            "eos_stability": stability,
            "kms_noise_value": float(kms_value),
            "onsager_entropy_value": float(entropy_value),
            "heat_flux_entropy_production": float(heat["entropy_production"]),
            "heat_flux_orthogonality_residual": float(heat["heat_flux_orthogonality_residual"]),
            "thermal_force_orthogonality_residual": float(heat["force_orthogonality_residual"]),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


__all__ = ["FORMAL_T13_BRIDGE_STATUS", "formal_thermodynamic_bridge_witness"]
