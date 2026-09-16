"""Verify the quadratic discrete energy identity of the causal reference lane.

The check is intentionally narrower than the full matter-space operator.  It
audits the centered damped recurrence in the frozen-C, source-free, quadratic
space-response limit.  The full nonlinear coupled candidate remains gated by
its own causal and ledger requirements.
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

from docs.core.uet_matter_space import (  # noqa: E402
    MatterSpaceConfig,
    MatterSpaceState,
    causal_linear_space_step,
)


OUT = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_reference_energy_verification.json"
DEFAULT_REPAIR = ROOT / "docs/core/07_artifacts/archive/causal_discretization_repair_artifact.json"
CORE_SOURCE = ROOT / "docs/core/02_equations/matter_space/uet_matter_space.py"
THRESHOLD = 1.0e-10


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def cross_time_quadratic_energy(
    current: np.ndarray,
    previous: np.ndarray,
    dt: float,
    dx: float,
    config: MatterSpaceConfig,
) -> float:
    """Return the cross-time energy paired with the centered recurrence.

    For the declared reference lane, ``a_space=0``, ``coupling_g=0`` and the
    source is zero.  The discrete potential is therefore the cross-time
    gradient term.  The kinetic term uses the backward difference required by
    the exact two-level identity.
    """

    velocity = (current - previous) / dt
    current_gradient = np.diff(current) / dx
    previous_gradient = np.diff(previous) / dx
    kinetic = config.tau_space / (2.0 * config.mobility_space)
    gradient = config.kappa_space / 2.0
    return float(
        kinetic * np.sum(velocity * velocity) * dx
        + gradient * np.sum(current_gradient * previous_gradient) * dx
    )


def run_reference_energy() -> dict[str, Any]:
    n = 161
    dx = 0.0125
    center = n // 2
    config = MatterSpaceConfig(
        a_matter=0.0,
        b_matter=1.0,
        kappa_matter=1.0e-8,
        mobility_matter=1.0e-8,
        a_space=0.0,
        # MatterSpaceConfig keeps b_space positive.  The reference is the
        # linearized quadratic limit; this tiny regularizer is recorded and
        # its residual is included in the gate rather than hidden.
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
    previous = phi - dt * pi
    state = MatterSpaceState(C, phi, pi)

    energy_before = cross_time_quadratic_energy(phi, previous, dt, dx, config)
    max_abs_residual = 0.0
    max_relative_residual = 0.0
    max_energy_increase = 0.0
    energy_increase_steps = 0
    steps = 50
    for _ in range(steps):
        state, old_phi = causal_linear_space_step(
            state, previous, dt, dx, config
        )
        current = state.space_response
        energy_after = cross_time_quadratic_energy(
            current, old_phi, dt, dx, config
        )
        damping_work = (
            np.sum((current - previous) ** 2)
            * dx
            / (4.0 * config.mobility_space * dt)
        )
        residual = energy_after - energy_before + damping_work
        scale = max(abs(energy_before), abs(damping_work), 1.0)
        max_abs_residual = max(max_abs_residual, abs(float(residual)))
        max_relative_residual = max(
            max_relative_residual, abs(float(residual)) / scale
        )
        increase = energy_after - energy_before
        max_energy_increase = max(max_energy_increase, float(increase))
        if increase > 1.0e-12:
            energy_increase_steps += 1
        energy_before = energy_after
        previous = old_phi

    status = (
        "PASS"
        if max_relative_residual <= THRESHOLD and energy_increase_steps == 0
        else "FAIL"
    )
    return {
        "status": status,
        "grid": {"n": n, "dx": dx, "steps": steps, "boundary_condition": "zero_flux"},
        "config": {
            "space_speed": config.space_speed,
            "tau_space": config.tau_space,
            "kappa_space": config.kappa_space,
            "mobility_space": config.mobility_space,
            "a_space": config.a_space,
            "b_space": config.b_space,
            "coupling_g": config.coupling_g,
            "unit_lane": config.unit_lane,
        },
        "identity": {
            "energy": "tau/(2M)||delta_t Phi||^2 + kappa/2 <grad Phi^n, grad Phi^(n-1)>",
            "damping_work": "-1/(4 M dt)||Phi^(n+1)-Phi^(n-1)||^2",
            "residual_relation": "E^(n+1)-E^n-damping_work=0",
            "scope": "quadratic_reference_lane",
        },
        "metrics": {
            "max_absolute_identity_residual": max_abs_residual,
            "max_relative_identity_residual": max_relative_residual,
            "threshold": THRESHOLD,
            "max_energy_increase": max_energy_increase,
            "energy_increase_steps": energy_increase_steps,
        },
        "interpretation": (
            "The centered damped recurrence has a closed cross-time quadratic "
            "energy identity in the frozen-C source-free reference lane. "
            "The tiny positive b_space regularizer is retained by the shared "
            "config contract and its residual is measured, not hidden."
        ),
    }


def build_report(repair_path: Path = DEFAULT_REPAIR) -> dict[str, Any]:
    reference = run_reference_energy()
    repair = load(repair_path)
    return {
        "schema_version": "causal-reference-energy-verification-v1",
        "artifact": "matter_space_causal_reference_energy_verification",
        "generated_at": date.today().isoformat(),
        "audit_status": reference["status"],
        "reference_status": reference["status"],
        "full_coupled_candidate_status": "BLOCKED",
        "controlling_blocker": repair["controlling_blocker"],
        "reference": reference,
        "evidence_class": "INTERNAL_NUMERICAL_VERIFICATION",
        "evidence_inputs": {
            "core_source": rel(CORE_SOURCE),
            "core_source_sha256": sha256(CORE_SOURCE),
            "repair_artifact": rel(repair_path),
        },
        "claim_boundary": (
            "This closes the discrete ledger identity only for the declared "
            "quadratic frozen-C reference lane. It does not close the full "
            "nonlinear coupled operator, continuum causality, SI physics, or "
            "any downstream topic."
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
        metrics = report["reference"]["metrics"]
        print(f"audit_status={report['audit_status']}")
        print(f"max_relative_identity_residual={metrics['max_relative_identity_residual']:.6g}")
        print(f"max_energy_increase={metrics['max_energy_increase']:.6g}")
        print(f"full_coupled_candidate_status={report['full_coupled_candidate_status']}")
    return 0 if report["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
