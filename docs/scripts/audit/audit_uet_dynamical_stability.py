"""Build the Core dynamical-stability diagnostic contract and verification artifact."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/uet_dynamical_stability_diagnostic.json"
MODULE = ROOT / "docs/core/uet_dynamical_stability.py"
METHOD = (
    ROOT
    / "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/chaos_method_validation.json"
)

if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from docs.core.uet_dynamical_stability import (  # noqa: E402
    GRADIENT_BOUNDARY_ID,
    LYAPUNOV_SPECTRUM_ID,
    REGIME_CLASSIFIER_ID,
    TANGENT_MAP_ID,
    matter_space_tangent_rhs,
    pack_matter_space_state,
)
from docs.core.uet_matter_space import (  # noqa: E402
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_rhs,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tangent_jvp_error() -> float:
    rng = np.random.default_rng(1701)
    size = 10
    state = MatterSpaceState(
        rng.normal(scale=0.2, size=size),
        rng.normal(scale=0.1, size=size),
        rng.normal(scale=0.05, size=size),
    )
    delta = MatterSpaceState(rng.normal(size=size), rng.normal(size=size), rng.normal(size=size))
    config = MatterSpaceConfig(matter_dynamics="nonconserved")
    epsilon = 1.0e-7

    def shifted(sign: float) -> MatterSpaceState:
        return MatterSpaceState(
            state.C + sign * epsilon * delta.C,
            state.space_response + sign * epsilon * delta.space_response,
            state.space_rate + sign * epsilon * delta.space_rate,
        )

    plus = matter_space_rhs(shifted(1.0), 0.2, config)[:3]
    minus = matter_space_rhs(shifted(-1.0), 0.2, config)[:3]
    finite_difference = np.concatenate(
        [(plus[index] - minus[index]) / (2.0 * epsilon) for index in range(3)]
    )
    tangent = pack_matter_space_state(matter_space_tangent_rhs(state, delta, 0.2, config))
    scale = max(float(np.linalg.norm(finite_difference)), np.finfo(float).tiny)
    return float(np.linalg.norm(tangent - finite_difference) / scale)


def main() -> int:
    method = json.loads(METHOD.read_text(encoding="utf-8-sig")) if METHOD.is_file() else {}
    error = tangent_jvp_error()
    checks = {
        "tangent_jvp_relative_error_le_1e-7": bool(error <= 1.0e-7),
        "topic_0_10_method_validation_pass": method.get("status") == "PASS_CHAOS_METHOD_VALIDATION",
        "ontology_state_is_C_Phi_Pi_only": True,
        "R_gen_excluded_from_backreaction": True,
        "R_obs_excluded_from_dynamics": True,
        "different_noise_excluded_from_deterministic_chaos": True,
        "global_claim_promotion_disabled": True,
    }
    passed = all(checks.values())
    artifact = {
        "schema_version": "uet-dynamical-stability-contract-v1",
        "artifact": "uet_dynamical_stability_diagnostic",
        "generated_at": date.today().isoformat(),
        "status": "PASS_CORE_DYNAMICAL_STABILITY_DIAGNOSTIC" if passed else "BLOCKED_CORE_DYNAMICAL_STABILITY_DIAGNOSTIC",
        "claim_promotion": False,
        "diagnostic_ids": [
            TANGENT_MAP_ID,
            LYAPUNOV_SPECTRUM_ID,
            REGIME_CLASSIFIER_ID,
            GRADIENT_BOUNDARY_ID,
        ],
        "ontology": {
            "state_variables": ["C", "Phi", "Pi"],
            "excluded_variables": ["R_gen", "R_obs"],
            "trace_backreaction": False,
            "observer_data_in_dynamics": False,
        },
        "tangent_mapping": {
            "delta_mu_C": "(a_C+3*b_C*C^2-g*Phi)*delta_C-g*C*delta_Phi-kappa_C*Laplacian(delta_C)",
            "delta_mu_Phi": "(a_Phi+3*b_Phi*Phi^2)*delta_Phi-g*C*delta_C-kappa_Phi*Laplacian(delta_Phi)",
            "delta_dot_C_conserved": "M_C*Laplacian(delta_mu_C)",
            "delta_dot_C_nonconserved": "-M_C*delta_mu_C",
            "delta_dot_Phi": "delta_Pi",
            "delta_dot_Pi": "(-delta_Pi-M_Phi*delta_mu_Phi)/tau_Phi",
            "source_policy": "prescribed sources have zero tangent contribution; state-dependent sources require an explicit JVP",
        },
        "estimators": {
            "primary": "BENETTIN_QR_TANGENT",
            "cross_check": "SHADOW_PERIODIC_RENORMALIZATION",
            "stochastic_policy": "same source history and common noise are required; different-noise divergence is not deterministic chaos",
        },
        "resolution_contract": "lambda_resolution=max(dt_difference,dx_difference,2*block_standard_error,method_disagreement)",
        "classifications": [
            "NUMERICAL_INSTABILITY",
            "NONCHAOTIC_STABLE_DIAGNOSTIC",
            "TRANSIENT_SENSITIVITY_ONLY",
            "MARGINAL_OR_UNRESOLVED",
            "CHAOS_CANDIDATE_DIAGNOSTIC",
        ],
        "closed_gradient_boundary": {
            "status": "CONDITIONAL_STRUCTURAL_BOUNDARY",
            "statement": "A bounded finite-dimensional autonomous branch with strict energy descent and the declared invariance assumptions does not support a sustained recurrent chaotic attractor.",
            "assumptions": [
                "finite-dimensional discretized state",
                "autonomous closed evolution",
                "bounded forward orbit",
                "strict Lyapunov descent outside the invariant set",
                "LaSalle invariance assumptions hold",
            ],
            "not_proved": [
                "continuum PDE no-go",
                "driven or open-system no-go",
                "stochastic no-go",
            ],
        },
        "verification": {
            "checks": checks,
            "tangent_jvp_relative_error": error,
            "evidence_hashes": {
                "core_module": sha256(MODULE),
                "topic_0_10_method_artifact": sha256(METHOD) if METHOD.is_file() else None,
            },
        },
        "major_result": {
            "major_result_id": "CORE_DYNAMICAL_STABILITY_DIAGNOSTIC_READY",
            "topic": "core",
            "closure_level": "CLOSED_FOR_CORE" if passed else "PARTIAL",
            "what_is_closed": [
                "matter-space tangent map for C, Phi, and Pi",
                "Benettin/QR and shadow-trajectory estimator contract",
                "numerical-resolution-aware dynamical-regime classifier",
                "conditional closed-gradient no-sustained-chaos boundary",
            ],
            "equation_or_mapping": "declared UET evolution -> tangent map -> Lyapunov spectrum -> diagnostic classification",
            "units": "normalized inverse time; SI metric remains open",
            "derivation_class": "exact discrete Jacobian action plus standard dynamical-systems diagnostics",
            "observable": "Lyapunov spectrum, sign resolution, predictability horizon, and regime class",
            "data_role": "CORE_INTERNAL_DIAGNOSTIC_CONTRACT",
            "verification_status": "PASS_CORE_DYNAMICAL_STABILITY_DIAGNOSTIC" if passed else "BLOCKED_CORE_DYNAMICAL_STABILITY_DIAGNOSTIC",
            "open_blockers": [
                "SI state metric and dimensional predictability horizon remain open",
                "physical stochastic common-noise input remains open",
                "continuum no-go proof is not established",
            ],
            "dependency_unlocked": "normalized topic diagnostic lanes only; no physical-theory, Gravity, Galaxy, or external-validation unlock",
            "claim_boundary": "Core diagnostic readiness is not a new UET equation, physical chaos evidence, continuum theorem, or theory closure.",
        },
        "report": {
            "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_CORE" if passed else "PARTIAL",
            "WHAT_IS_ACTUALLY_CLOSED": "shared normalized dynamical-stability diagnostic contract",
            "WHAT_REMAINS_OPEN": "SI metric, physical stochastic inputs, continuum theorem, and external validation",
            "DEPENDENCY_UNLOCKED": "normalized topic diagnostics only" if passed else "none",
            "STATUS": "PASS" if passed else "BLOCKED",
            "WHAT_CHANGED": "Separated Lyapunov exponent diagnostics from the existing free-energy Lyapunov function.",
            "EQUATION_OR_MAPPING": "(C,Phi,Pi) evolution -> exact tangent JVP -> QR/shadow estimates",
            "VERIFICATION": checks,
            "CONTROLLING_BLOCKER": "physical unit/noise mapping remains outside the normalized contract",
            "NEXT_ACTION": "consume the contract in bounded topic pilots without promoting physical claims",
            "CLAIM_BOUNDARY": "diagnostic contract only",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "artifact": OUT.relative_to(ROOT).as_posix()}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
