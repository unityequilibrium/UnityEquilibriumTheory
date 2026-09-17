"""Formal Topic 13 SK/KMS and entropy-current interface.

The functions in this module verify a named interface and positivity witness.
They do not provide microscopic transport coefficients or a finite-temperature
normal component.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def sk_kms_noise_kernel(
    beta_th_J_inv: float,
    omega_energy_J: float,
    im_retarded: float,
) -> float:
    """Return the symmetrized noise witness from a KMS retarded response."""

    beta = float(beta_th_J_inv)
    omega = float(omega_energy_J)
    imaginary = float(im_retarded)
    if beta <= 0.0 or omega <= 0.0 or imaginary < 0.0:
        raise ValueError("KMS witness requires beta>0, omega>0, and Im G_R>=0")
    return float(2.0 / np.tanh(0.5 * beta * omega) * imaginary)


def entropy_production_witness(
    forces: Any,
    onsager_matrix: Any,
) -> float:
    """Return X^T L X after checking a symmetric PSD Onsager matrix."""

    x = np.asarray(forces, dtype=float)
    matrix = np.asarray(onsager_matrix, dtype=float)
    if x.shape != (2,) or matrix.shape != (2, 2):
        raise ValueError("the named interface uses two forces and a 2x2 matrix")
    if not np.allclose(matrix, matrix.T, atol=1.0e-12):
        raise ValueError("Onsager matrix must be symmetric")
    if float(np.min(np.linalg.eigvalsh(matrix))) < -1.0e-12:
        raise ValueError("Onsager matrix must be positive semidefinite")
    return float(x @ matrix @ x)


def thermal_sk_kms_entropy_contract() -> dict[str, Any]:
    """Return the declared equations and boundaries for the named lane."""

    return {
        "contract_id": "T13-SK-KMS-ENTROPY-001",
        "sk_action": "S_SK = integral [Phi_a D_R Phi_r + i Phi_a N Phi_a / 2]",
        "kms_relation": "N(omega) = coth(beta_th omega / 2) * 2 Im D_R(omega)",
        "entropy_current": "J_S^mu = s u^mu + q^mu / T",
        "entropy_production": "nabla_mu J_S^mu = q_perp^2/(kappa T^2) + X_A L^(AB) X_B >= 0",
        "dissipative_balance": "nabla_mu T_matter^(mu nu) = Q^nu; nabla_mu T_UET^(mu nu) = -Q^nu",
        "thermodynamic_inverse_temperature": "beta_th = 1/(k_B T)",
        "beta_T13_relation": "beta_T13 remains a candidate stiffness-temperature coefficient and is not beta_th",
        "sk_field_meaning": "Phi_r and Phi_a are response/contour copies of effective Phi; Phi_a is not a new physical field",
        "C_meaning": "C remains a collective system-behaviour coordinate",
        "R_gen_meaning": "R_gen remains a derived history trace with no backreaction in this contract",
        "unit_contract": {
            "T": "K",
            "beta_th": "J^-1",
            "q": "W m^-2",
            "kappa": "W m^-1 K^-1",
            "J_S": "W m^-2 K^-1",
            "nabla_J_S": "W m^-3 K^-1",
            "q_perp_sq": "(W m^-2)^2",
            "Phi_r_Phi_a": "dimensionless normalized response copies; SI action scale remains external",
        },
        "coefficient_policy": "physical Kubo coefficients require source or microscopic matching; synthetic values are verifier-only",
        "temperature_scope": "formal interface only; finite-temperature normal component remains open",
        "curved_scope": "flat/local tensor notation only; curved 3+1 solver remains open",
        "physical_status": "named formal SK/KMS/entropy interface; not physical transport closure",
    }
