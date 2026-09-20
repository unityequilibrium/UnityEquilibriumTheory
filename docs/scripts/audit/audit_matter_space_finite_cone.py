"""Generate the finite-cone C candidate verification artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from docs.core.uet_matter_space_finite_cone import (
    FINITE_CONE_C_OPERATOR_MODE,
    FiniteConeCConfig,
    FiniteConeCState,
    finite_cone_c_contract,
    finite_cone_c_chemical_potentials,
    finite_cone_c_free_energy,
    finite_cone_c_step,
)


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/archive/matter_space_causal_lane_comparison.json"


def _state(n: int = 32) -> FiniteConeCState:
    x = np.arange(n, dtype=float)
    return FiniteConeCState(
        C=0.15 + 0.04 * np.sin(2.0 * np.pi * x / n),
        C_rate=0.02 * np.cos(2.0 * np.pi * x / n),
        space_response=0.02 * np.sin(2.0 * np.pi * x / n),
        space_rate=0.01 * np.cos(2.0 * np.pi * x / n),
    )


def _config() -> FiniteConeCConfig:
    return FiniteConeCConfig(
        a_C=1.0,
        b_C=1.0,
        kappa_C=0.2,
        mobility_C=1.0,
        tau_C=1.0,
        a_space=1.0,
        b_space=1.0,
        kappa_space=0.2,
        mobility_space=1.0,
        tau_space=1.0,
        coupling_g=0.1,
        c_limit=1.0,
    )


def _directional_derivative_residual(state, dx, config):
    direction = FiniteConeCState(
        C=np.sin(np.arange(state.C.size, dtype=float)),
        C_rate=np.zeros_like(state.C),
        space_response=np.cos(np.arange(state.C.size, dtype=float)),
        space_rate=np.zeros_like(state.C),
    )
    eps = 1.0e-6
    plus = FiniteConeCState(
        state.C + eps * direction.C,
        state.C_rate,
        state.space_response + eps * direction.space_response,
        state.space_rate,
    )
    minus = FiniteConeCState(
        state.C - eps * direction.C,
        state.C_rate,
        state.space_response - eps * direction.space_response,
        state.space_rate,
    )
    numerical = (
        finite_cone_c_free_energy(plus, dx, config)
        - finite_cone_c_free_energy(minus, dx, config)
    ) / (2.0 * eps)
    mu_C, mu_Phi = finite_cone_c_chemical_potentials(state, dx, config)
    analytic = float(
        dx * np.sum(mu_C * direction.C + mu_Phi * direction.space_response)
    )
    return abs(numerical - analytic) / max(abs(numerical), abs(analytic), 1.0e-12)


def build_artifact() -> dict:
    config = _config()
    state = _state()
    dx = 1.0
    dt = 1.0e-4
    result = finite_cone_c_step(state, dt, dx, config)
    derivative_residual = _directional_derivative_residual(state, dx, config)
    return {
        "schema_version": "matter-space-causal-lane-comparison-v1",
        "artifact": "matter_space_causal_lane_comparison",
        "status": "BLOCKED",
        "candidate_status": "CANDIDATE",
        "generated_by": "docs/scripts/audit/audit_matter_space_finite_cone.py",
        "operator_mode": FINITE_CONE_C_OPERATOR_MODE,
        "contract": finite_cone_c_contract(),
        "lanes": {
            "conserved_C_baseline": {
                "status": "BLOCKED_FOR_CHANGING_C_FINITE_CONE",
                "controller": "conserved_C_gradient_term_has_unbounded_k4_characteristic_speed",
                "role": "normalized_conserved_phase_comparator",
            },
            "finite_cone_C_candidate": {
                "status": "CANDIDATE",
                "role": "nonconserved_collective_order_parameter",
                "principal_speed_C": config.matter_speed,
                "principal_speed_Phi": config.space_speed,
                "declared_speed_limit": config.c_limit,
                "within_declared_limit": bool(
                    config.matter_speed <= config.c_limit
                    and config.space_speed <= config.c_limit
                ),
            },
            "conserved_Cattaneo_comparator": {
                "status": "BLOCKED",
                "controller": "high_k_group_speed_unbounded_when_kappa_C_positive",
                "role": "negative_control_until_UV_or_nonlocal_regularization",
            },
        },
        "checks": {
            "functional_directional_derivative_relative_residual": derivative_residual,
            "functional_derivative_gate": derivative_residual <= 1.0e-6,
            "ledger_gate": result.energy_ledger["ledger_gate"],
            "energy_descent_gate": result.energy_ledger["energy_descent_gate"],
            "trace_feedback": result.diagnostics["trace_backreaction"],
            "no_clipping": result.diagnostics["field_clipping_applied"] is False,
            "no_parameter_fitting": result.diagnostics["parameter_fitting_applied"] is False,
            "finite_principal_speed": True,
            "numerical_compact_support_gate": "BLOCKED_NOT_YET_CLOSED",
        },
        "evidence_class": "INTERNAL_CHECKED_CANDIDATE",
        "claim_boundary": (
            "candidate normalized finite-cone collective-response lane; "
            "not mass, density, covariant transport, or empirical validation"
        ),
        "next_controller": (
            "construct a characteristic/staggered or otherwise causal discrete "
            "integrator and rerun pre-arrival leakage without cone padding or clipping"
        ),
    }


def main() -> None:
    artifact = build_artifact()
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()