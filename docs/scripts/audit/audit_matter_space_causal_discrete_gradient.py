"""Audit the causal Phi/Pi discrete-gradient closure packet.

The artifact deliberately reports a partial closure: the causal Phi/Pi
substep is verified with nonlinear local potential, coupling and source, while
the changing-C shared operator remains blocked.
"""

from __future__ import annotations

import argparse
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

from docs.core.uet_matter_space import MatterSpaceConfig, MatterSpaceState  # noqa: E402
from docs.core.uet_matter_space_causal import (  # noqa: E402
    causal_space_discrete_energy,
    causal_space_discrete_gradient_step,
)


OUT = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_discrete_gradient_verification.json"
CORE_SOURCE = ROOT / "docs/core/uet_matter_space_causal.py"
THRESHOLD = 1.0e-10


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference_config() -> MatterSpaceConfig:
    return MatterSpaceConfig(
        a_matter=0.0,
        b_matter=1.0,
        kappa_matter=1.0e-8,
        mobility_matter=1.0e-8,
        a_space=0.0,
        b_space=1.0e-12,
        kappa_space=5.0,
        mobility_space=1.0,
        tau_space=5.0,
        coupling_g=0.0,
        matter_dynamics="conserved",
        boundary_condition="zero_flux",
        unit_lane="normalized",
        stability_safety=0.2,
    )


def run_reference() -> dict[str, Any]:
    n = 161
    dx = 0.0125
    center = n // 2
    config = reference_config()
    dt = dx / config.space_speed
    C = np.zeros(n)
    phi = np.zeros(n)
    pi = np.zeros(n)
    pi[center] = 1.0 / dx
    previous = phi - dt * pi
    state = MatterSpaceState(C, phi, pi)
    energy_before = causal_space_discrete_energy(phi, previous, C, dt, dx, config)
    max_relative_residual = 0.0
    max_energy_increase = 0.0
    energy_increase_steps = 0
    max_leakage = 0.0
    max_root_residual = 0.0
    for step in range(1, 41):
        state, old_phi, ledger = causal_space_discrete_gradient_step(
            state, previous, dt, dx, config
        )
        current = state.space_response
        energy_after = causal_space_discrete_energy(
            current, old_phi, C, dt, dx, config
        )
        damping = (
            np.sum((current - previous) ** 2)
            * dx
            / (4.0 * config.mobility_space * dt)
        )
        residual = energy_after - energy_before + damping - ledger["source_work"]
        scale = max(abs(energy_before), abs(damping), 1.0)
        max_relative_residual = max(max_relative_residual, abs(float(residual)) / scale)
        increase = energy_after - energy_before
        max_energy_increase = max(max_energy_increase, float(increase))
        if increase > 1.0e-12:
            energy_increase_steps += 1
        radius = step - 1
        outside = np.ones(n, dtype=bool)
        outside[max(0, center - radius) : min(n, center + radius + 1)] = False
        max_leakage = max(max_leakage, float(np.max(np.abs(current[outside]))))
        max_root_residual = max(max_root_residual, ledger["max_root_residual"])
        energy_before = energy_after
        previous = old_phi
    status = (
        "PASS"
        if max_relative_residual <= THRESHOLD
        and max_energy_increase <= 1.0e-10
        and energy_increase_steps == 0
        and max_leakage == 0.0
        and max_root_residual <= 1.0e-10
        else "FAIL"
    )
    return {
        "status": status,
        "grid": {"n": n, "dx": dx, "steps": 40, "boundary_condition": "zero_flux"},
        "config": {
            "space_speed": config.space_speed,
            "tau_space": config.tau_space,
            "kappa_space": config.kappa_space,
            "mobility_space": config.mobility_space,
            "coupling_g": config.coupling_g,
            "unit_lane": config.unit_lane,
        },
        "metrics": {
            "max_relative_energy_ledger_residual": max_relative_residual,
            "threshold": THRESHOLD,
            "max_energy_increase": max_energy_increase,
            "energy_increase_steps": energy_increase_steps,
            "max_prearrival_leakage": max_leakage,
            "max_root_residual": max_root_residual,
        },
    }


def run_coupling_source_probe() -> dict[str, Any]:
    n = 32
    dx = 0.25
    x = np.arange(n, dtype=float) * dx
    config = MatterSpaceConfig(
        a_matter=-0.2,
        b_matter=1.0,
        kappa_matter=0.1,
        mobility_matter=0.4,
        a_space=0.8,
        b_space=0.6,
        kappa_space=0.2,
        mobility_space=0.5,
        tau_space=0.7,
        coupling_g=0.15,
        matter_dynamics="conserved",
        boundary_condition="periodic",
        unit_lane="normalized",
        stability_safety=0.2,
    )
    C = 0.2 + 0.03 * np.cos(2.0 * np.pi * x / (n * dx))
    phi = 0.03 * np.sin(2.0 * np.pi * x / (n * dx))
    pi = 0.01 * np.cos(4.0 * np.pi * x / (n * dx))
    state = MatterSpaceState(C, phi, pi)
    dt = dx / config.space_speed
    previous = phi - dt * pi
    source = 0.01 * np.cos(2.0 * np.pi * x / (n * dx))
    before = causal_space_discrete_energy(phi, previous, C, dt, dx, config)
    updated, old_phi, ledger = causal_space_discrete_gradient_step(
        state, previous, dt, dx, config, source
    )
    after = causal_space_discrete_energy(
        updated.space_response, old_phi, C, dt, dx, config
    )
    damping = (
        np.sum((updated.space_response - previous) ** 2)
        * dx
        / (4.0 * config.mobility_space * dt)
    )
    residual = after - before + damping - ledger["source_work"]
    return {
        "status": "PASS" if abs(residual) / max(abs(before), 1.0) <= THRESHOLD else "FAIL",
        "relative_residual": abs(float(residual)) / max(abs(before), 1.0),
        "source_work": ledger["source_work"],
        "max_root_residual": ledger["max_root_residual"],
    }


def build_report() -> dict[str, Any]:
    reference = run_reference()
    coupling_probe = run_coupling_source_probe()
    partial_status = "PASS" if reference["status"] == "PASS" and coupling_probe["status"] == "PASS" else "FAIL"
    return {
        "schema_version": "matter-space-causal-discrete-gradient-verification-v1",
        "artifact": "matter_space_causal_discrete_gradient_verification",
        "generated_at": date.today().isoformat(),
        "audit_status": "BLOCKED",
        "partial_closure_status": partial_status,
        "full_coupled_candidate_status": "BLOCKED",
        "controlling_blocker": "matter_C_shared_ledger_integration_missing",
        "operator_mode": "causal_space_discrete_gradient_v1",
        "reference_lane": reference,
        "coupling_source_probe": coupling_probe,
        "formula_contract": {
            "discrete_local_gradient": "a_Phi*(Phi_next+Phi_previous)/2 + b_Phi*(Phi_next+Phi_previous)*(Phi_next^2+Phi_previous^2)/4 - g*C^2/2",
            "centered_recurrence": "tau*delta2_Phi/dt^2 + delta_center_Phi/dt + M_Phi*(mu_bar_local - kappa_Phi*Laplacian(Phi_current)) = J_Phi",
            "two_level_energy": "tau/(2*M_Phi)||delta_backward Phi||^2 + kappa_Phi/2 <grad Phi_current, grad Phi_previous> + (V_current+V_previous)/2",
            "ledger_identity": "E_next - E_current + ||Phi_next-Phi_previous||^2/(4*M_Phi*dt) = <J_Phi, Phi_next-Phi_previous>/(2*M_Phi)",
            "derivation_class": "discrete_gradient_local_potential_plus_centered_finite_volume_spatial_term"
        },        "contract": {
            "C_during_step": "frozen",
            "Phi_potential": "nonlinear_discrete_gradient",
            "spatial_operator": "explicit_finite_volume_laplacian_at_current_time",
            "required_cfl": 1.0,
            "trace_feedback": False,
            "unit_lane": "normalized",
        },
        "evidence_class": "INTERNAL_NUMERICAL_VERIFICATION",
        "evidence_inputs": {
            "implementation": rel(CORE_SOURCE),
            "implementation_sha256": sha256(CORE_SOURCE),
        },
        "claim_boundary": (
            "The causal Phi/Pi substep is internally verified with a fixed C, "
            "nonlinear local potential, C-to-Phi coupling and explicit source. "
            "The changing-C full operator, continuum causality, SI physics and "
            "downstream topics remain blocked."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if not args.no_write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={report['audit_status']}")
        print(f"partial_closure_status={report['partial_closure_status']}")
        print(f"controlling_blocker={report['controlling_blocker']}")
    return 0 if report["partial_closure_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
