"""Audit whether the changing-C lane is compatible with a finite response cone.

This is a structural compatibility audit, not a parameter fit.  It combines a
deterministic localized-pulse stencil probe with the continuum high-k
diagnostic for a hypothetical Cattaneo relaxation of the conserved C current.
The latter still has a k^4 principal term when kappa_C > 0, so its group speed
does not admit a finite bound as k grows.
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
from docs.core.uet_matter_space_split import causal_matter_space_split_step  # noqa: E402


OUT = ROOT / "docs/core/07_artifacts/archive/matter_space_causal_cone_compatibility.json"
CORE_SOURCE = ROOT / "docs/core/02_equations/matter_space/uet_matter_space_split.py"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_discrete_probe() -> dict[str, Any]:
    n = 161
    dx = 0.25
    center = n // 2
    config = MatterSpaceConfig(
        a_matter=0.0,
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
        boundary_condition="zero_flux",
        unit_lane="normalized",
        stability_safety=0.2,
    )
    dt = dx / config.space_speed
    C = np.zeros(n, dtype=float)
    C[center] = 0.1
    phi = np.zeros(n, dtype=float)
    pi = np.zeros(n, dtype=float)
    state = MatterSpaceState(C, phi, pi)
    state, _, ledger = causal_matter_space_split_step(
        state, phi, dt, dx, config
    )
    def radius(field: np.ndarray, tolerance: float = 1.0e-14) -> int:
        indices = np.flatnonzero(np.abs(field) > tolerance)
        if indices.size == 0:
            return 0
        return int(max(abs(int(indices.min()) - center), abs(int(indices.max()) - center)))

    C_radius = radius(state.C)
    phi_radius = radius(state.space_response)
    return {
        "n": n,
        "dx": dx,
        "macro_dt": dt,
        "phi_declared_radius_cells": 1,
        "observed_C_radius_cells": C_radius,
        "observed_Phi_radius_cells": phi_radius,
        "matter_substeps": ledger["matter_substeps"],
        "observed_combined_radius_cells": max(C_radius, phi_radius),
        "mass_relative_drift": ledger["mass_relative_drift"],
        "shared_ledger_residual": ledger["shared_ledger_residual"],
        "stencil_probe_status": "FAIL" if phi_radius > 1 or C_radius > 1 else "PASS",
    }


def continuum_diagnostic() -> dict[str, Any]:
    M_C = 0.04
    kappa_C = 0.02
    tau_C = 0.7
    a_C = 0.0
    wave_numbers = [1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
    group_speeds = []
    for k in wave_numbers:
        D = M_C * (a_C * k**2 + kappa_C * k**4)
        omega_sq = max(D / tau_C - 1.0 / (4.0 * tau_C**2), 0.0)
        if omega_sq == 0.0:
            group_speeds.append(0.0)
        else:
            derivative_D = M_C * (2.0 * a_C * k + 4.0 * kappa_C * k**3)
            group_speeds.append(float(derivative_D / (2.0 * tau_C * np.sqrt(omega_sq))))
    return {
        "equation": "tau_C*C_tt + C_t = M_C*Laplacian(mu_C), mu_C=a_C*C-kappa_C*Laplacian(C)",
        "M_C": M_C,
        "kappa_C": kappa_C,
        "tau_C": tau_C,
        "a_C": a_C,
        "wave_numbers": wave_numbers,
        "group_speeds": group_speeds,
        "high_k_group_speed_is_unbounded": True,
        "asymptotic_group_speed": "2*sqrt(M_C*kappa_C/tau_C)*k",
        "interpretation": "A Cattaneo relaxation does not create a finite cone for conserved C when kappa_C>0 because the principal symbol remains k^4.",
    }


def build_report() -> dict[str, Any]:
    discrete = run_discrete_probe()
    continuum = continuum_diagnostic()
    return {
        "schema_version": "matter-space-causal-cone-compatibility-v1",
        "artifact": "matter_space_causal_cone_compatibility",
        "generated_at": date.today().isoformat(),
        "audit_status": "BLOCKED",
        "response_cone_status": "BLOCKED",
        "shared_ledger_status": "PASS",
        "full_candidate_status": "BLOCKED",
        "structural_blocker": "conserved_C_gradient_term_has_unbounded_k4_characteristic_speed",
        "discrete_probe": discrete,
        "continuum_diagnostic": {"cattaneo_extension": continuum},
        "decision_options": [
            "keep C as a parabolic matter lane and restrict the causal cone claim to externally prescribed/frozen C",
            "change the C realization to a non-conserved telegraph/order-parameter lane with a finite principal speed",
            "introduce an explicit UV regularization or nonlocal constitutive law and derive its units/energy contract",
        ],
        "claim_boundary": (
            "The split bridge shared ledger remains internally passing, but this "
            "audit does not establish a finite changing-C cone. It does not promote "
            "the full default operator, continuum causality, SI physics, or downstream topics."
        ),
        "evidence_class": "INTERNAL_STRUCTURAL_COMPATIBILITY_AUDIT",
        "evidence_inputs": {
            "implementation": rel(CORE_SOURCE),
            "implementation_sha256": sha256(CORE_SOURCE),
        },
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
        print(f"response_cone_status={report['response_cone_status']}")
        print(f"structural_blocker={report['structural_blocker']}")
        print(f"observed_C_radius={report['discrete_probe']['observed_C_radius_cells']}")
        print(f"observed_Phi_radius={report['discrete_probe']['observed_Phi_radius_cells']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
