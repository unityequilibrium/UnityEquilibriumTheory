"""Verify the named conserved finite-cone flux branch."""

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

from docs.core.uet_matter_space_flux_telegraph import (  # noqa: E402
    FLUX_TELEGRAPH_OPERATOR_MODE,
    FluxTelegraphConfig,
    flux_telegraph_step,
)


OUT = ROOT / "docs/core/artifacts/matter_space_conserved_flux_telegraph_verification.json"
CORE_SOURCE = ROOT / "docs/core/uet_matter_space_flux_telegraph.py"


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


def _evolve(
    dx: float,
    cfl: float,
    physical_time: float,
    n: int,
    config: FluxTelegraphConfig,
    compact_pulse: bool,
) -> tuple[np.ndarray, dict[str, float]]:
    dt = cfl * dx / config.characteristic_speed
    steps = max(1, int(round(physical_time / dt)))
    C = _initial_profile(dx, n, compact_pulse)
    flux = np.zeros(n + 1 if config.boundary_condition == "zero_flux" else n, dtype=float)
    max_mass_drift = 0.0
    max_energy_relative_residual = 0.0
    for _ in range(steps):
        C, flux, ledger = flux_telegraph_step(C, flux, dt, dx, config)
        max_mass_drift = max(max_mass_drift, abs(float(ledger["mass_drift"])))
        scale = max(abs(float(ledger["energy_before"])), 1.0)
        max_energy_relative_residual = max(
            max_energy_relative_residual,
            abs(float(ledger["energy_residual"])) / scale,
        )
    return C, {
        "dt": float(dt),
        "steps": float(steps),
        "physical_time": float(steps * dt),
        "max_mass_drift": float(max_mass_drift),
        "max_energy_relative_residual": float(max_energy_relative_residual),
    }


def run_domain_probe(config: FluxTelegraphConfig) -> dict[str, Any]:
    n = 161
    dx = 1.0e-3
    cfl = 0.4
    dt = cfl * dx / config.characteristic_speed
    center = n // 2
    target_distance = 40
    C = _initial_profile(dx, n, compact_pulse=False)
    flux = np.zeros(n + 1, dtype=float)
    prearrival_max = 0.0
    support_excess = 0
    max_mass_drift = 0.0
    max_energy_relative_residual = 0.0
    no_clipping = True
    no_padding = True
    no_fit = True
    for step in range(1, target_distance + 1):
        C, flux, ledger = flux_telegraph_step(C, flux, dt, dx, config)
        radius = _support_radius(C, center)
        support_excess = max(support_excess, radius - step)
        outside = np.ones(n, dtype=bool)
        left = max(0, center - step)
        right = min(n, center + step + 1)
        outside[left:right] = False
        prearrival_max = max(prearrival_max, float(np.max(np.abs(C[outside]))))
        max_mass_drift = max(max_mass_drift, abs(float(ledger["mass_drift"])))
        scale = max(abs(float(ledger["energy_before"])), 1.0)
        max_energy_relative_residual = max(
            max_energy_relative_residual,
            abs(float(ledger["energy_residual"])) / scale,
        )
        no_clipping = no_clipping and ledger["field_clipping_applied"] is False
        no_padding = no_padding and ledger["cone_padding_applied"] is False
        no_fit = no_fit and ledger["parameter_fitting_applied"] is False

    arrival_target = float(abs(C[center + target_distance]))
    peak = max(float(np.max(np.abs(C))), np.finfo(float).tiny)
    return {
        "initial_condition": "single-cell compact pulse",
        "grid": {
            "n": n,
            "dx": dx,
            "center_index": center,
            "target_distance_cells": target_distance,
        },
        "time_step": {
            "dt": float(dt),
            "cfl": float(config.characteristic_speed * dt / dx),
            "steps_before_target": target_distance - 1,
            "arrival_step_checked": target_distance,
        },
        "metrics": {
            "prearrival_max_outside_discrete_cone": float(prearrival_max),
            "prearrival_leakage_fraction": float(prearrival_max / peak),
            "arrival_target_abs": arrival_target,
            "support_excess_cells": int(support_excess),
            "max_mass_drift": float(max_mass_drift),
            "max_energy_relative_residual": float(max_energy_relative_residual),
        },
        "checks": {
            "finite_cone_support": support_excess <= 0,
            "prearrival_threshold": prearrival_max / peak <= 1.0e-6,
            "arrival_target_nonzero": arrival_target > 0.0,
            "mass_conservation": max_mass_drift <= 1.0e-12,
            "energy_ledger": max_energy_relative_residual <= 1.0e-6,
            "no_clipping": no_clipping,
            "no_cone_padding": no_padding,
            "no_parameter_fitting": no_fit,
        },
    }


def run_convergence_probe(config: FluxTelegraphConfig) -> dict[str, Any]:
    physical_time = 0.01
    coarse, coarse_meta = _evolve(1.0e-3, 0.4, physical_time, 161, config, True)
    temporal, temporal_meta = _evolve(1.0e-3, 0.2, physical_time, 161, config, True)
    spatial, spatial_meta = _evolve(5.0e-4, 0.2, physical_time, 321, config, True)
    temporal_error = float(
        np.linalg.norm(coarse - temporal) / max(np.linalg.norm(temporal), 1.0e-15)
    )
    spatial_error = float(
        np.linalg.norm(coarse - spatial[::2])
        / max(np.linalg.norm(spatial[::2]), 1.0e-15)
    )
    return {
        "initial_condition": "compact triangular pulse with fixed physical width 0.004",
        "physical_time_target": physical_time,
        "temporal": {
            "coarse": coarse_meta,
            "refined": temporal_meta,
            "relative_l2_difference": temporal_error,
        },
        "spatial": {
            "coarse": coarse_meta,
            "refined": spatial_meta,
            "relative_l2_difference": spatial_error,
        },
        "checks": {
            "temporal_finite": bool(np.isfinite(temporal_error)),
            "spatial_finite": bool(np.isfinite(spatial_error)),
            "temporal_reasonable": temporal_error <= 0.25,
            "spatial_reasonable": spatial_error <= 0.25,
        },
    }


def build_report() -> dict[str, Any]:
    config = FluxTelegraphConfig()
    domain = run_domain_probe(config)
    convergence = run_convergence_probe(config)
    checks = {**domain["checks"], **convergence["checks"]}
    status = "PASS" if all(checks.values()) else "BLOCKED"
    return {
        "schema_version": "matter-space-conserved-flux-telegraph-verification-v1",
        "artifact": "matter_space_conserved_flux_telegraph_verification",
        "generated_at": date.today().isoformat(),
        "status": status,
        "operator_mode": FLUX_TELEGRAPH_OPERATOR_MODE,
        "branch_id": "T13-CAUSAL-FLUX-TELEGRAPH-001",
        "equations": {
            "conservation": "C_t + partial_x J_C = 0",
            "flux_relaxation": "tau_C * J_C_t + J_C = -M_C * partial_x(mu_C)",
            "chemical_potential": "mu_C = a_C*C + b_C*C^3 - coupling_g*C*Phi",
            "energy": "E_C = integral[U(C,Phi) + tau_C*J_C^2/(2*M_C)] dx",
            "dissipation": "dE_C/dt = -integral[J_C^2/M_C] dx for closed boundaries",
        },
        "units": {
            "lane": config.unit_lane,
            "C": "normalized collective-coordinate density lane",
            "J_C": "normalized conserved flux lane",
            "Phi": "normalized effective response variable",
            "kappa_C": "0 in this named branch; the original kappa_C>0 class remains blocked",
        },
        "derivation_class": "named local conserved flux-telegraph branch; normalized internal verification",
        "config": {
            "a_C": config.a_C,
            "b_C": config.b_C,
            "mobility_C": config.mobility_C,
            "tau_C": config.tau_C,
            "coupling_g": config.coupling_g,
            "kappa_C": config.kappa_C,
            "characteristic_speed": config.characteristic_speed,
            "boundary_condition": config.boundary_condition,
        },
        "domain_of_dependence": domain,
        "convergence": convergence,
        "verification": {
            "checks": checks,
            "full_default_operator_replaced": False,
            "trace_backreaction": False,
            "xie_2026_accessed": False,
        },
        "evidence_inputs": {
            "implementation": "docs/core/uet_matter_space_flux_telegraph.py",
            "implementation_sha256": sha256(CORE_SOURCE),
            "baseline_no_go": "docs/core/artifacts/conserved_c_finite_cone_no_go_assessment.json",
        },
        "claim_boundary": (
            "This artifact verifies a named normalized conserved flux branch only. "
            "It does not pass the original kappa_C>0 conserved-gradient equation, "
            "does not close the coupled Phi branch, and does not establish SI or "
            "external thermal validity."
        ),
        "next_controller": (
            "integrate the named C flux branch with the causal Phi lane and rerun "
            "the full-candidate leakage/energy gate"
        ),
        "major_result": {
            "major_result_id": "T13_CAUSAL_FLUX_TELEGRAPH_BRANCH",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status == "PASS" else "PARTIAL",
            "what_is_closed": [
                "conserved C flux-telegraph equations with local chemical potential",
                "finite-volume compact discrete domain of dependence",
                "mass conservation and normalized energy/dissipation diagnostic"
            ] if status == "PASS" else [],
            "equation_or_mapping": {
                "conservation": "C_t + partial_x J_C = 0",
                "flux_relaxation": "tau_C * J_C_t + J_C = -M_C * partial_x(mu_C)",
                "chemical_potential": "mu_C = a_C*C + b_C*C^3 - coupling_g*C*Phi",
                "energy": "E_C = integral[U(C,Phi) + tau_C*J_C^2/(2*M_C)] dx",
                "dissipation": "dE_C/dt = -integral[J_C^2/M_C] dx for closed boundaries"
            },
            "units": {
                "lane": config.unit_lane,
                "C": "normalized collective-coordinate density lane",
                "J_C": "normalized conserved flux lane",
                "Phi": "normalized effective response variable",
                "kappa_C": "0 in this named branch; the original kappa_C>0 class remains blocked"
            },
            "derivation_class": "named local conserved flux-telegraph branch; normalized internal verification",
            "observable": "normalized C response and conserved flux diagnostic",
            "data_role": "internal numerical branch verification; not external thermal data",
            "evidence_artifacts": [
                {"path": "docs/core/artifacts/matter_space_conserved_flux_telegraph_verification.json"}
            ],
            "verification_status": status,
            "open_blockers": [
                "full coupled Phi integration",
                "full-candidate leakage rerun"
            ],
            "dependency_unlocked": "none; Topic 13 full bridge remains open",
            "claim_boundary": "CLOSED_FOR_LANE only: this named normalized C flux branch does not replace the original kappa_C>0 baseline, close Phi transport, or establish SI or external thermal validity."
        }
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "branch_id": report["branch_id"],
        "checks": report["verification"]["checks"],
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
