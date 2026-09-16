"""Audit the changing-C split bridge and keep its causal claim blocked.

The split bridge verifies conservation and a shared normalized ledger within a
declared tolerance.  Because the conserved C lane is parabolic and is
subcycled, this artifact does not pass the full response-cone gate.
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
from docs.core.uet_matter_space_split import (  # noqa: E402
    causal_matter_space_split_step,
    causal_split_energy,
)


OUT = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_split_verification.json"
CORE_SOURCE = ROOT / "docs/core/02_equations/matter_space/uet_matter_space_split.py"
THRESHOLD = 1.0e-6


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config() -> MatterSpaceConfig:
    return MatterSpaceConfig(
        a_matter=-0.2,
        b_matter=1.0,
        kappa_matter=0.02,
        mobility_matter=0.04,
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


def run_bridge() -> dict[str, Any]:
    n = 32
    dx = 0.25
    x = np.arange(n, dtype=float) * dx
    cfg = config()
    C = 0.2 + 0.03 * np.cos(2.0 * np.pi * x / (n * dx))
    phi = 0.03 * np.sin(2.0 * np.pi * x / (n * dx))
    pi = 0.01 * np.cos(4.0 * np.pi * x / (n * dx))
    state = MatterSpaceState(C, phi, pi)
    dt = dx / cfg.space_speed
    previous = phi - dt * pi
    max_shared_relative_residual = 0.0
    max_matter_relative_residual = 0.0
    max_mass_drift = 0.0
    max_energy_increase = 0.0
    max_substeps = 0
    for _ in range(5):
        before = causal_split_energy(state, previous, dt, dx, cfg)
        state, old_phi, ledger = causal_matter_space_split_step(
            state, previous, dt, dx, cfg
        )
        after = causal_split_energy(state, old_phi, dt, dx, cfg)
        scale = max(abs(before), 1.0)
        max_shared_relative_residual = max(
            max_shared_relative_residual,
            abs(ledger["shared_ledger_residual"]) / scale,
        )
        max_matter_relative_residual = max(
            max_matter_relative_residual,
            abs(ledger["matter_ledger_residual"]) / scale,
        )
        max_mass_drift = max(max_mass_drift, ledger["mass_relative_drift"])
        max_energy_increase = max(max_energy_increase, after - before)
        max_substeps = max(max_substeps, ledger["matter_substeps"])
        previous = old_phi
    shared_status = (
        "PASS"
        if max_shared_relative_residual <= THRESHOLD
        and max_matter_relative_residual <= THRESHOLD
        and max_mass_drift <= 1.0e-10
        and max_energy_increase <= 1.0e-9 * max(abs(before), 1.0)
        else "FAIL"
    )
    return {
        "status": "PASS_WITHIN_DECLARED_TOLERANCE" if shared_status == "PASS" else "FAIL",
        "metrics": {
            "max_shared_relative_residual": max_shared_relative_residual,
            "max_matter_relative_residual": max_matter_relative_residual,
            "max_mass_relative_drift": max_mass_drift,
            "max_energy_increase": max_energy_increase,
            "max_matter_substeps": max_substeps,
            "threshold": THRESHOLD,
        },
    }


def build_report() -> dict[str, Any]:
    bridge = run_bridge()
    return {
        "schema_version": "matter-space-causal-split-verification-v1",
        "artifact": "matter_space_causal_split_verification",
        "generated_at": date.today().isoformat(),
        "audit_status": "BLOCKED",
        "split_bridge_status": bridge["status"],
        "shared_ledger_status": "PASS" if bridge["status"] == "PASS_WITHIN_DECLARED_TOLERANCE" else "FAIL",
        "changing_C_causal_cone_status": "BLOCKED",
        "full_candidate_status": "BLOCKED",
        "controlling_blocker": "changing_C_response_cone_and_full_operator_integration_missing",
        "bridge": bridge,
        "contract": {
            "matter_lane": "conserved_parabolic_subcycle",
            "phi_lane": "causal_discrete_gradient_cfl_1",
            "coupling_time_level": "time_averaged_Phi_during_C_subcycle",
            "trace_feedback": False,
            "unit_lane": "normalized",
        },
        "evidence_class": "INTERNAL_NUMERICAL_VERIFICATION",
        "evidence_inputs": {
            "implementation": rel(CORE_SOURCE),
            "implementation_sha256": sha256(CORE_SOURCE),
        },
        "claim_boundary": (
            "The changing-C split bridge passes conservation and shared-ledger "
            "checks within its declared tolerance. It does not pass the changing-C "
            "response cone, the full default operator, continuum causality, SI "
            "physics, or downstream topics."
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
        print(f"split_bridge_status={report['split_bridge_status']}")
        print(f"shared_ledger_status={report['shared_ledger_status']}")
        print(f"changing_C_causal_cone_status={report['changing_C_causal_cone_status']}")
        print(f"controlling_blocker={report['controlling_blocker']}")
    return 0 if report["split_bridge_status"] == "PASS_WITHIN_DECLARED_TOLERANCE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
