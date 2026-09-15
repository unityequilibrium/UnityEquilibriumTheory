"""Verify the strict-CFL causal reference lane for the matter-space operator.

This verifier exercises only the linearized Phi sector with C frozen.  It is
an implementation reference for compact discrete support, not a verification
of the full nonlinear matter-space candidate or of a continuum causal law.
The existing default Heun/RK2 operator remains separately gated.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_matter_space import (  # noqa: E402
    MatterSpaceConfig,
    MatterSpaceState,
    causal_linear_space_step,
)


OUT = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_reference_verification.json"
DEFAULT_VERIFICATION = (
    ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json"
)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def run_reference() -> dict[str, Any]:
    n = 161
    dx = 0.0125
    center = n // 2
    target_distance_cells = 40
    target = center + target_distance_cells
    config = MatterSpaceConfig(
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
    dt = dx / config.space_speed
    C = np.zeros(n, dtype=float)
    phi = np.zeros(n, dtype=float)
    pi = np.zeros(n, dtype=float)
    pi[center] = 1.0 / dx
    state = MatterSpaceState(C, phi, pi)
    previous = phi - dt * pi

    prearrival_max = 0.0
    support_violations = 0
    peak = 0.0
    for step in range(1, target_distance_cells + 1):
        state, old_phi = causal_linear_space_step(
            state, previous, dt, dx, config
        )
        previous = old_phi
        peak = max(peak, float(np.max(np.abs(state.space_response))))
        radius = step - 1
        outside = np.ones(n, dtype=bool)
        left = max(0, center - radius)
        right = min(n, center + radius + 1)
        outside[left:right] = False
        leakage = float(np.max(np.abs(state.space_response[outside])))
        prearrival_max = max(prearrival_max, leakage)
        if leakage > 0.0:
            support_violations += 1

    prearrival_target = float(abs(state.space_response[target]))
    state, old_phi = causal_linear_space_step(state, previous, dt, dx, config)
    arrival_target = float(abs(state.space_response[target]))
    peak = max(peak, float(np.max(np.abs(state.space_response))))
    normalized_leakage = prearrival_max / max(peak, np.finfo(float).tiny)
    support_status = (
        "PASS"
        if support_violations == 0 and prearrival_target == 0.0 and arrival_target > 0.0
        else "FAIL"
    )
    return {
        "grid": {
            "n": n,
            "dx": dx,
            "center_index": center,
            "target_index": target,
            "target_distance_cells": target_distance_cells,
        },
        "config": {
            "space_speed": config.space_speed,
            "tau_space": config.tau_space,
            "kappa_space": config.kappa_space,
            "mobility_space": config.mobility_space,
            "coupling_g": config.coupling_g,
            "boundary_condition": config.boundary_condition,
            "unit_lane": config.unit_lane,
        },
        "time_step": {
            "dt": dt,
            "cfl": config.space_speed * dt / dx,
            "steps_before_target": target_distance_cells,
            "arrival_step_checked": target_distance_cells + 1,
        },
        "metrics": {
            "prearrival_target_abs": prearrival_target,
            "arrival_target_abs": arrival_target,
            "prearrival_max_outside_discrete_cone": prearrival_max,
            "prearrival_leakage_fraction": normalized_leakage,
            "support_violations": support_violations,
        },
        "status": support_status,
        "scope": "linearized_space_response_with_frozen_C",
        "interpretation": (
            "The strict-CFL reference recurrence has compact discrete support in "
            "the tested frozen-C lane. This does not verify the full nonlinear "
            "coupled operator, its energy ledger, or the continuum equation."
        ),
    }


def build_report(verification_path: Path = DEFAULT_VERIFICATION) -> dict[str, Any]:
    reference = run_reference()
    default_verification = load(verification_path)
    default_leakage = float(
        default_verification["metrics"]["prearrival_leakage"]["value"]
    )
    default_status = default_verification["metrics"]["prearrival_leakage"]["gate"]
    return {
        "schema_version": "1.0",
        "artifact": "matter_space_causal_reference_verification",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS" if reference["status"] == "PASS" else "FAIL",
        "reference_status": reference["status"],
        "default_candidate_status": "BLOCKED",
        "default_candidate_causal_gate": default_status,
        "default_candidate_prearrival_leakage_fraction": default_leakage,
        "reference": reference,
        "implementation_contract": {
            "scheme": "centered_second_order_damped_recurrence",
            "required_cfl": 1.0,
            "support_property": "nearest-neighbor compact discrete cone",
            "physical_state_feedback": "C is frozen and trace is absent",
            "scope_boundary": "reference/control lane only; not a replacement for matter_space_step",
        },
        "evidence_inputs": {
            "core_source": "docs/core/uet_matter_space.py",
            "default_candidate_verification": rel(verification_path),
        },
        "claim_boundary": (
            "The causal reference lane is an internally verified numerical "
            "control for compact support in its declared scope. The default "
            "full coupled candidate remains blocked by its original causal "
            "leakage gate and is not promoted by this artifact."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        report = build_report()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={report['audit_status']}")
        print(f"reference_status={report['reference_status']}")
        print(f"default_candidate_status={report['default_candidate_status']}")
        print(
            "prearrival_leakage_fraction="
            f"{report['reference']['metrics']['prearrival_leakage_fraction']:.6g}"
        )
    return 0 if report["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
