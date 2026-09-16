"""Verify the named conserved C/Phi coupled finite-cone branch."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_matter_space_flux_phi import (  # noqa: E402
    FLUX_PHI_COUPLED_OPERATOR_MODE,
    FluxPhiCoupledConfig,
    flux_phi_coupled_step,
)


OUT = ROOT / "docs/core/07_artifacts/verification/matter_space_flux_phi_coupled_verification.json"
CORE_SOURCE = ROOT / "docs/core/02_equations/matter_space/uet_matter_space_flux_phi.py"
BASELINE_SOURCE = ROOT / "docs/core/02_equations/matter_space/uet_matter_space_flux_telegraph.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _support_radius(field: np.ndarray, center: int) -> int:
    indices = np.flatnonzero(np.abs(field) > 0.0)
    if indices.size == 0:
        return 0
    return int(max(abs(int(indices.min()) - center), abs(int(indices.max()) - center)))


def _initial_profile(dx: float, n: int, compact_pulse: bool) -> np.ndarray:
    if not compact_pulse:
        profile = np.zeros(n, dtype=float)
        profile[n // 2] = 0.1
        return profile
    coordinate = (np.arange(n) - n // 2) * dx
    profile = 0.1 * (1.0 - np.abs(coordinate) / 0.004)
    return np.where(profile > 0.0, profile, 0.0)


def _step_state(
    C: np.ndarray,
    flux: np.ndarray,
    Phi: np.ndarray,
    previous_Phi: np.ndarray,
    dt: float,
    dx: float,
    config: FluxPhiCoupledConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    return flux_phi_coupled_step(C, flux, Phi, previous_Phi, dt, dx, config)


def _evolve(
    dx: float,
    cfl_C: float,
    physical_time: float,
    n: int,
    config: FluxPhiCoupledConfig,
    compact_pulse: bool,
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    dt = cfl_C * dx / config.C.characteristic_speed
    steps = max(1, int(round(physical_time / dt)))
    C = _initial_profile(dx, n, compact_pulse)
    flux = np.zeros(n + 1, dtype=float)
    Phi = np.zeros(n, dtype=float)
    previous_Phi = np.zeros(n, dtype=float)
    max_mass_drift = 0.0
    max_energy_relative_residual = 0.0
    for _ in range(steps):
        C, flux, Phi, previous_Phi, ledger = _step_state(
            C, flux, Phi, previous_Phi, dt, dx, config
        )
        max_mass_drift = max(max_mass_drift, abs(float(ledger["C_mass_drift"])))
        max_energy_relative_residual = max(
            max_energy_relative_residual,
            abs(float(ledger["combined_energy_relative_residual"])),
        )
    return C, Phi, {
        "dt": float(dt),
        "steps": float(steps),
        "physical_time": float(steps * dt),
        "max_mass_drift": float(max_mass_drift),
        "max_energy_relative_residual": float(max_energy_relative_residual),
    }


def run_domain_probe(config: FluxPhiCoupledConfig) -> dict[str, Any]:
    n = 161
    dx = 1.0e-3
    cfl_C = 0.4
    dt = cfl_C * dx / config.C.characteristic_speed
    center = n // 2
    target_distance = 40
    C = _initial_profile(dx, n, compact_pulse=False)
    flux = np.zeros(n + 1, dtype=float)
    Phi = np.zeros(n, dtype=float)
    previous_Phi = np.zeros(n, dtype=float)
    prearrival_max = 0.0
    support_excess = 0
    max_mass_drift = 0.0
    max_energy_relative_residual = 0.0
    no_clipping = True
    no_padding = True
    no_fit = True
    phi_arrival_target = 0.0
    C_arrival_target = 0.0

    for step in range(1, target_distance + 2):
        C, flux, Phi, previous_Phi, ledger = _step_state(
            C, flux, Phi, previous_Phi, dt, dx, config
        )
        if step <= target_distance:
            radius = max(_support_radius(C, center), _support_radius(Phi, center))
            support_excess = max(support_excess, radius - step)
            outside = np.ones(n, dtype=bool)
            left = max(0, center - step)
            right = min(n, center + step + 1)
            outside[left:right] = False
            prearrival_max = max(
                prearrival_max,
                float(np.max(np.abs(C[outside]))) if np.any(outside) else 0.0,
                float(np.max(np.abs(Phi[outside]))) if np.any(outside) else 0.0,
            )
        if step == target_distance:
            C_arrival_target = float(abs(C[center + target_distance]))
        if step == target_distance + 1:
            phi_arrival_target = float(abs(Phi[center + target_distance]))
        max_mass_drift = max(max_mass_drift, abs(float(ledger["C_mass_drift"])))
        max_energy_relative_residual = max(
            max_energy_relative_residual,
            abs(float(ledger["combined_energy_relative_residual"])),
        )
        no_clipping = no_clipping and ledger["field_clipping_applied"] is False
        no_padding = no_padding and ledger["cone_padding_applied"] is False
        no_fit = no_fit and ledger["parameter_fitting_applied"] is False

    peak = max(float(np.max(np.abs(C))), float(np.max(np.abs(Phi))), np.finfo(float).tiny)
    return {
        "initial_condition": "single-cell compact C pulse; zero Phi response",
        "grid": {
            "n": n,
            "dx": dx,
            "center_index": center,
            "target_distance_cells": target_distance,
        },
        "time_step": {
            "dt": float(dt),
            "C_cfl": float(config.C.characteristic_speed * dt / dx),
            "Phi_cfl": float(config.Phi.space_speed * dt / dx),
            "steps_before_target": target_distance - 1,
            "C_arrival_step_checked": target_distance,
            "Phi_arrival_step_checked": target_distance + 1,
        },
        "metrics": {
            "prearrival_max_outside_discrete_cone": float(prearrival_max),
            "prearrival_leakage_fraction": float(prearrival_max / peak),
            "C_arrival_target_abs": C_arrival_target,
            "Phi_arrival_target_abs": phi_arrival_target,
            "support_excess_cells": int(support_excess),
            "max_mass_drift": float(max_mass_drift),
            "max_combined_energy_relative_residual": float(
                max_energy_relative_residual
            ),
        },
        "checks": {
            "finite_cone_support": support_excess <= 0,
            "prearrival_threshold": prearrival_max / peak <= 1.0e-6,
            "arrival_target_nonzero": C_arrival_target > 0.0,
            "response_arrival_target_nonzero": phi_arrival_target > 0.0,
            "mass_conservation": max_mass_drift <= 1.0e-12,
            "energy_ledger": max_energy_relative_residual <= 1.0e-6,
            "no_clipping": no_clipping,
            "no_cone_padding": no_padding,
            "no_parameter_fitting": no_fit,
        },
    }


def run_convergence_probe(config: FluxPhiCoupledConfig) -> dict[str, Any]:
    physical_time = 0.01
    coarse, coarse_phi, coarse_meta = _evolve(
        1.0e-3, 0.4, physical_time, 161, config, True
    )
    temporal, temporal_phi, temporal_meta = _evolve(
        1.0e-3, 0.2, physical_time, 161, config, True
    )
    spatial, spatial_phi, spatial_meta = _evolve(
        5.0e-4, 0.2, physical_time, 321, config, True
    )
    temporal_error = float(
        np.linalg.norm(coarse - temporal)
        / max(np.linalg.norm(temporal), 1.0e-15)
    )
    spatial_error = float(
        np.linalg.norm(coarse - spatial[::2])
        / max(np.linalg.norm(spatial[::2]), 1.0e-15)
    )
    temporal_phi_error = float(
        np.linalg.norm(coarse_phi - temporal_phi)
        / max(np.linalg.norm(temporal_phi), 1.0e-15)
    )
    spatial_phi_error = float(
        np.linalg.norm(coarse_phi - spatial_phi[::2])
        / max(np.linalg.norm(spatial_phi[::2]), 1.0e-15)
    )
    return {
        "initial_condition": "compact triangular C pulse with fixed physical width 0.004",
        "physical_time_target": physical_time,
        "temporal": {
            "coarse": coarse_meta,
            "refined": temporal_meta,
            "C_relative_l2_difference": temporal_error,
            "Phi_relative_l2_difference": temporal_phi_error,
        },
        "spatial": {
            "coarse": coarse_meta,
            "refined": spatial_meta,
            "C_relative_l2_difference": spatial_error,
            "Phi_relative_l2_difference": spatial_phi_error,
        },
        "checks": {
            "temporal_finite": bool(
                np.isfinite(temporal_error) and np.isfinite(temporal_phi_error)
            ),
            "spatial_finite": bool(
                np.isfinite(spatial_error) and np.isfinite(spatial_phi_error)
            ),
            "temporal_reasonable": temporal_error <= 0.25 and temporal_phi_error <= 0.25,
            "spatial_reasonable": spatial_error <= 0.25 and spatial_phi_error <= 0.25,
        },
    }


def build_report() -> dict[str, Any]:
    config = FluxPhiCoupledConfig()
    domain = run_domain_probe(config)
    convergence = run_convergence_probe(config)
    checks = {**domain["checks"], **convergence["checks"]}
    status = "PASS" if all(checks.values()) else "BLOCKED"
    return {
        "schema_version": "matter-space-flux-phi-coupled-verification-v1",
        "artifact": "matter_space_flux_phi_coupled_verification",
        "generated_at": date.today().isoformat(),
        "status": status,
        "operator_mode": FLUX_PHI_COUPLED_OPERATOR_MODE,
        "branch_id": "T13-CAUSAL-FLUX-PHI-COUPLED-001",
        "equations": {
            "conservation": "C_t + partial_x J_C = 0",
            "flux_relaxation": "tau_C * J_C_t + J_C = -M_C * partial_x(mu_C)",
            "chemical_potential_C": "mu_C = a_C*C + b_C*C^3 - coupling_g*C*Phi",
            "response_equation": "tau_Phi * Phi_tt + Phi_t + M_Phi*mu_Phi = 0",
            "chemical_potential_Phi": "mu_Phi = a_Phi*Phi + b_Phi*Phi^3 - kappa_Phi*Laplacian(Phi) - 0.5*coupling_g*C^2",
            "coupling_energy": "V_CPhi = -0.5*coupling_g*C^2*Phi",
            "energy_exchange": "Delta E = -W_C_diss - W_Phi_damp + W_CPhi_exchange + residual",
        },
        "units": {
            "lane": config.C.unit_lane,
            "C": "normalized collective-coordinate density lane",
            "J_C": "normalized conserved flux lane",
            "Phi": "normalized effective response variable",
            "R_gen": "derived history trace; absent from dynamics",
        },
        "derivation_class": (
            "named local conserved C flux branch plus causal Phi discrete-gradient "
            "lane; staggered internal numerical integration"
        ),
        "observable": "normalized coupled C/Phi response and shared energy ledger",
        "data_role": "internal numerical branch verification; not external thermal data",
        "config": {
            "a_C": config.C.a_C,
            "b_C": config.C.b_C,
            "mobility_C": config.C.mobility_C,
            "tau_C": config.C.tau_C,
            "a_Phi": config.Phi.a_space,
            "b_Phi": config.Phi.b_space,
            "kappa_Phi": config.Phi.kappa_space,
            "mobility_Phi": config.Phi.mobility_space,
            "tau_Phi": config.Phi.tau_space,
            "coupling_g": config.C.coupling_g,
            "C_kappa": config.C.kappa_C,
            "boundary_condition": config.C.boundary_condition,
        },
        "domain_of_dependence": domain,
        "convergence": convergence,
        "verification": {
            "checks": checks,
            "full_original_conserved_gradient_candidate_replaced": False,
            "full_original_conserved_gradient_candidate_pass": False,
            "trace_backreaction": False,
            "xie_2026_accessed": False,
            "thresholds": {
                "prearrival_leakage_fraction": 1.0e-6,
                "energy_relative_residual": 1.0e-6,
            },
        },
        "evidence_inputs": {
            "implementation": "docs/core/02_equations/matter_space/uet_matter_space_flux_phi.py",
            "implementation_sha256": sha256(CORE_SOURCE),
            "C_branch_implementation": "docs/core/02_equations/matter_space/uet_matter_space_flux_telegraph.py",
            "C_branch_implementation_sha256": sha256(BASELINE_SOURCE),
            "baseline_no_go": "docs/core/07_artifacts/archive/conserved_c_finite_cone_no_go_assessment.json",
        },
        "major_result": {
            "major_result_id": "T13_CAUSAL_FLUX_PHI_COUPLED_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status == "PASS" else "PARTIAL",
            "what_is_closed": [
                "named conserved C flux branch integrated with the causal Phi lane",
                "finite-volume compact discrete domain of dependence for the named lane",
                "C mass conservation and shared normalized energy ledger",
            ] if status == "PASS" else [],
            "equation_or_mapping": {
                "C_to_Phi": "mu_C and mu_Phi share V_CPhi = -0.5*coupling_g*C^2*Phi",
                "measurement": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
            },
            "units": {
                "lane": config.C.unit_lane,
                "alpha_Phi_K": "not derived by this internal branch",
            },
            "derivation_class": "named normalized internal coupled-lane verification",
            "observable": "normalized C/Phi response and ledger diagnostics",
            "data_role": "internal numerical verification; no TTG source consumed",
            "evidence_artifacts": [
                {"path": "docs/core/07_artifacts/verification/matter_space_flux_phi_coupled_verification.json"}
            ],
            "verification_status": status,
            "open_blockers": [
                "original kappa_C>0 conserved-gradient baseline remains blocked",
                "TTG numeric source package remains provisional",
                "alpha_Phi_K independent calibration remains open",
                "non-circular bridge, beta, EOS, transport, KMS, and entropy remain open",
            ],
            "dependency_unlocked": "none; Topic 13 full bridge remains open",
            "claim_boundary": (
                "CLOSED_FOR_LANE only: this named normalized C/Phi branch does not "
                "close the original conserved-gradient baseline, establish SI thermal "
                "mapping, external validation, or global UET closure."
            ),
        },
        "claim_boundary": (
            "This artifact verifies a named normalized coupled C/Phi branch only. "
            "It does not pass the original kappa_C>0 conserved-gradient equation, "
            "derive alpha_Phi_K, or establish external thermal validity."
        ),
        "next_controller": (
            "if this named lane remains PASS, close the permitted TTG source package "
            "and independent alpha_Phi_K calibration without reading Xie 2026"
        ),
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "branch_id": report["branch_id"],
        "checks": report["verification"]["checks"],
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
