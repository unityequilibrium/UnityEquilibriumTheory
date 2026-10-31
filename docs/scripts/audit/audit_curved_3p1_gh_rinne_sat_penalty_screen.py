"""Reproduce a finite-grid scalar-SAT sensitivity screen for Rinne GH CPBC."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RINNE_AUDIT_SOURCE = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_full_u1_cpbc_slab.py"
RINNE_SPEC = importlib.util.spec_from_file_location(
    "gh_rinne_penalty_reference", RINNE_AUDIT_SOURCE
)
if RINNE_SPEC is None or RINNE_SPEC.loader is None:
    raise ImportError("cannot load the frozen Rinne slab audit")
RINNE_AUDIT = importlib.util.module_from_spec(RINNE_SPEC)
sys.modules[RINNE_SPEC.name] = RINNE_AUDIT
RINNE_SPEC.loader.exec_module(RINNE_AUDIT)

SLAB = RINNE_AUDIT.SLAB
TT_SBP = RINNE_AUDIT.TT_PILOT
GAMMA2 = 0.7
ORDERS = (8, 12, 16)
SIGMA_GRID = (-4.0, -2.0, -1.0, -0.5, -0.25, -0.125, 0.0, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0)
DIRECT_STRENGTH_GRID = (
    -1.0,
    -0.5,
    -0.25,
    -0.125,
    0.0,
    0.125,
    0.25,
    0.5,
    0.75,
    1.0,
    1.25,
    1.5,
    2.0,
    4.0,
)
EIGENVALUE_TOLERANCE = 1.0e-6
PULSE_ENERGY_RATIO_LIMIT = 5.0e-2
PULSE_FINAL_TIME = 2.4
OUTPUT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_sat_penalty_screen.json"
)
AUDIT_SOURCE = Path(__file__).resolve()
SLAB_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_full_u1_slab.py"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
SAT_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_max_dissipative_sat.py"
TT_SOURCE = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_tt_sbp_sat_boundary.py"
BASELINE_ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_full_u1_max_diss_sat_control.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _flatten(state: Any) -> np.ndarray:
    return np.concatenate(
        (state.metric.ravel(), state.normal_derivative.ravel(), state.normal_spatial_derivative.ravel())
    )


def _unflatten(vector: np.ndarray, node_count: int) -> Any:
    block = node_count * 10
    return SLAB.GHSlabState(
        vector[:block].reshape(node_count, 10),
        vector[block : 2 * block].reshape(node_count, 10),
        vector[2 * block :].reshape(node_count, 10),
    )


def _raw_rhs(state: Any, derivative: np.ndarray, gamma2: float) -> Any:
    return SLAB.GHSlabState(
        -state.normal_derivative.copy(),
        -(derivative @ state.normal_spatial_derivative),
        -(derivative @ state.normal_derivative)
        + gamma2 * (derivative @ state.metric)
        - gamma2 * state.normal_spatial_derivative,
    )


def _residual(state: Any, raw_rhs: Any, derivative: np.ndarray, face_index: int, normal: int) -> np.ndarray:
    target = SLAB.full_u1_boundary_target(
        state,
        derivative @ state.metric,
        face_index=face_index,
        normal=normal,
        gamma2=GAMMA2,
        gauge_data_rate=np.zeros(10),
    )
    qdot_raw = (
        raw_rhs.normal_derivative[face_index]
        - normal * raw_rhs.normal_spatial_derivative[face_index]
        - GAMMA2 * raw_rhs.metric[face_index]
    )
    return target - qdot_raw


def _operator_components(operators: Any) -> dict[str, np.ndarray | float]:
    derivative = operators.derivative
    node_count = len(operators.nodes)
    block = node_count * 10
    dimension = 3 * block
    raw = np.zeros((dimension, dimension), dtype=float)
    pi_direct = np.zeros_like(raw)
    pi_weak = np.zeros_like(raw)
    characteristic_weak = np.zeros_like(raw)
    characteristic_strong = np.zeros_like(raw)

    for column in range(dimension):
        basis = np.zeros(dimension, dtype=float)
        basis[column] = 1.0
        state = _unflatten(basis, node_count)
        raw_rhs = _raw_rhs(state, derivative, GAMMA2)
        raw[:, column] = _flatten(raw_rhs)
        for face_index, normal in ((0, -1), (node_count - 1, 1)):
            residual = _residual(state, raw_rhs, derivative, face_index, normal)
            pi_slice = slice(block + face_index * 10, block + (face_index + 1) * 10)
            phi_slice = slice(2 * block + face_index * 10, 2 * block + (face_index + 1) * 10)
            pi_direct[pi_slice, column] = residual
            pi_weak[pi_slice, column] = residual / operators.norm_weights[face_index]
            characteristic_weak[pi_slice, column] = (
                0.5 * residual / operators.norm_weights[face_index]
            )
            characteristic_weak[phi_slice, column] = (
                -0.5 * normal * residual / operators.norm_weights[face_index]
            )
            characteristic_strong[pi_slice, column] = 0.5 * residual
            characteristic_strong[phi_slice, column] = -0.5 * normal * residual

    frozen_rinne = RINNE_AUDIT._linear_operator(operators, GAMMA2, "rinne_pointwise")
    return {
        "raw": raw,
        "pi_direct": pi_direct,
        "pi_weak": pi_weak,
        "characteristic_weak": characteristic_weak,
        "characteristic_strong": characteristic_strong,
        "strong_match_residual": float(
            np.max(np.abs(raw + characteristic_strong - frozen_rinne))
        ),
    }


def _spectral_metrics(matrix: np.ndarray) -> dict[str, float | int | bool]:
    eigenvalues = np.linalg.eigvals(matrix)
    maximum_real = float(np.max(eigenvalues.real))
    positive_modes = int(np.count_nonzero(eigenvalues.real > EIGENVALUE_TOLERANCE))
    return {
        "maximum_eigenvalue_real_part": maximum_real,
        "positive_modes_above_1e-6": positive_modes,
        "spectral_screen_pass": maximum_real <= EIGENVALUE_TOLERANCE,
    }


def _gain_scan(
    base: np.ndarray, penalty: np.ndarray, grid: tuple[float, ...] = SIGMA_GRID
) -> dict[str, Any]:
    points = []
    for sigma in grid:
        metrics = _spectral_metrics(base + sigma * penalty)
        points.append({"sigma_hat": sigma, **metrics})
    passing = [point["sigma_hat"] for point in points if point["spectral_screen_pass"]]
    best = min(points, key=lambda point: point["maximum_eigenvalue_real_part"])
    return {
        "points": points,
        "passing_sigma_hat_values": passing,
        "best_sampled_point": best,
        "classification": "NO_SAMPLED_GAIN_PASSES" if not passing else "SAMPLED_GAIN_PASS_FOUND",
    }


def _evolve_matrix(matrix: np.ndarray, initial: Any, operators: Any) -> tuple[Any, int, float]:
    dt_cap = 0.25 * float(np.min(np.diff(operators.nodes)))
    steps = max(1, int(np.ceil(PULSE_FINAL_TIME / dt_cap)))
    dt = PULSE_FINAL_TIME / steps
    state = _flatten(initial)
    for _ in range(steps):
        k1 = matrix @ state
        k2 = matrix @ (state + 0.5 * dt * k1)
        k3 = matrix @ (state + 0.5 * dt * k2)
        k4 = matrix @ (state + dt * k3)
        state = state + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
    return _unflatten(state, len(operators.nodes)), steps, dt


def build_artifact() -> dict[str, Any]:
    order_results = []
    for order in ORDERS:
        operators = TT_SBP.legendre_lobatto_operators(order)
        components = _operator_components(operators)
        base = components["raw"]
        pi_direct = components["pi_direct"]
        pi_weak = components["pi_weak"]
        characteristic_weak = components["characteristic_weak"]
        characteristic_strong = components["characteristic_strong"]
        assert isinstance(base, np.ndarray)
        assert isinstance(pi_direct, np.ndarray)
        assert isinstance(pi_weak, np.ndarray)
        assert isinstance(characteristic_weak, np.ndarray)
        assert isinstance(characteristic_strong, np.ndarray)

        pi_direct_matrix = base + pi_direct
        pi_direct_spectrum = _spectral_metrics(pi_direct_matrix)
        initial = RINNE_AUDIT._tt_pulse(operators)
        final, steps, dt = _evolve_matrix(pi_direct_matrix, initial, operators)
        pulse_ratio = float(
            RINNE_AUDIT._field_energy(final, operators.norm_weights)
            / RINNE_AUDIT._field_energy(initial, operators.norm_weights)
        )
        reduction_residual = float(
            np.max(np.abs(operators.derivative @ final.metric - final.normal_spatial_derivative))
        )

        order_results.append(
            {
                "lgl_order": order,
                "node_count": order + 1,
                "state_dimension": int(base.shape[0]),
                "strong_rinne_matrix_match_residual": components["strong_match_residual"],
                "pi_only_exact_correction": {
                    **pi_direct_spectrum,
                    "pulse_energy_ratio": pulse_ratio,
                    "pulse_energy_ratio_limit": PULSE_ENERGY_RATIO_LIMIT,
                    "pulse_absorption_pass": pulse_ratio <= PULSE_ENERGY_RATIO_LIMIT,
                    "pulse_final_time": PULSE_FINAL_TIME,
                    "rk4_steps": steps,
                    "dt": dt,
                    "reduction_constraint_linf": reduction_residual,
                },
                "weak_pi_residual_gain_scan": _gain_scan(base, pi_weak),
                "weak_incoming_characteristic_gain_scan": _gain_scan(
                    base, characteristic_weak
                ),
                "direct_strong_rinne_amplitude_scan": _gain_scan(
                    base, characteristic_strong, DIRECT_STRENGTH_GRID
                ),
            }
        )

    checks = {
        "strong_rinne_operator_reproduced_at_every_order": all(
            row["strong_rinne_matrix_match_residual"] <= 5.0e-13 for row in order_results
        ),
        "pi_only_reduction_constraint_preserved_at_every_order": all(
            row["pi_only_exact_correction"]["reduction_constraint_linf"] <= 1.0e-12
            for row in order_results
        ),
        "pi_only_pulse_absorption_fails_at_every_order": all(
            not row["pi_only_exact_correction"]["pulse_absorption_pass"]
            for row in order_results
        ),
        "no_sampled_weak_pi_gain_passes_at_any_order": all(
            not row["weak_pi_residual_gain_scan"]["passing_sigma_hat_values"]
            for row in order_results
        ),
        "no_sampled_weak_characteristic_gain_passes_at_any_order": all(
            not row["weak_incoming_characteristic_gain_scan"]["passing_sigma_hat_values"]
            for row in order_results
        ),
        "direct_strength_scan_has_order8_passes": bool(
            order_results[0]["direct_strong_rinne_amplitude_scan"]["passing_sigma_hat_values"]
        ),
        "direct_strength_scan_has_no_pass_at_orders12_and16": all(
            not row["direct_strong_rinne_amplitude_scan"]["passing_sigma_hat_values"]
            for row in order_results[1:]
        ),
        "direct_strength_scan_has_no_common_gain_across_all_orders": not set.intersection(
            *(
                set(row["direct_strong_rinne_amplitude_scan"]["passing_sigma_hat_values"])
                for row in order_results
            )
        ),
    }
    source_paths = (
        AUDIT_SOURCE,
        RINNE_AUDIT_SOURCE,
        SLAB_SOURCE,
        PROJECTOR_SOURCE,
        SAT_SOURCE,
        TT_SOURCE,
        BASELINE_ARTIFACT,
    )
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path) for path in source_paths
    }
    passed = all(checks.values())
    return {
        "schema_version": "core-curved-3p1-gh-rinne-sat-penalty-screen-v1",
        "artifact": "curved_3p1_gh_rinne_sat_penalty_screen",
        "generated_at": date.today().isoformat(),
        "status": "PASS_BASELINE_REPRODUCTION_AND_SCREEN" if passed else "FAIL_SCREEN_AUDIT",
        "claim_promotion": False,
        "diagnostic_id": "uet.core.curved_3p1.gh.rinne_scalar_sat_gain_grid",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_RINNE_SCALAR_SAT_GAIN_GRID",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the frozen strong-Rinne operator is reproduced exactly by the independent assembly at LGL orders 8, 12, and 16",
                "none of the 13 declared normalized scalar gains passes the semidiscrete spectral screen for either tested weak penalty direction at any declared order",
                "the declared direct strong-correction amplitude grid has sampled passes only at LGL order 8, with no sampled pass at orders 12 or 16 and no common gain across all orders",
                "the direct Pi-only residual correction preserves the reduction constraint to roundoff but fails the declared pulse-absorption and spectrum screens",
            ] if passed else [],
            "equation_or_mapping": {
                "residual": "r = target(q_dot) - q_dot_raw",
                "pi_only_exact": "delta(Pi_dot) = r at each boundary node",
                "weak_pi": "delta(Pi_dot) = sigma_hat * H_hat^-1 * r",
                "weak_incoming_characteristic": "delta(Pi_dot) = sigma_hat*H_hat^-1*r/2; delta(Phi_dot) = -n*sigma_hat*H_hat^-1*r/2",
                "reduction_constraint": "C = D(psi) - Phi; Pi-only RHS correction leaves C_dot unchanged",
            },
            "units": {
                "unit_lane": "normalized geometric coordinate xi=x/L0 on [-1,1], with L0=1 in the computation",
                "psi": "dimensionless perturbation",
                "Pi_Phi_gamma2": "L0^-1",
                "q_dot_residual": "L0^-2",
                "H_hat": "dimensionless SBP norm weights H/L0",
                "sigma_hat": "dimensionless; sigma_hat*H_hat^-1*r has units L0^-2",
                "energy": "normalized linear-wave diagnostic; not SI energy",
            },
            "derivation_class": "standard-GR frozen-background numerical-method screen; no new physical equation",
            "observable": "semidiscrete spectral abscissa, positive eigenvalue count, TT-pulse energy ratio, and reduction-constraint residual",
            "data_role": "analytic and synthetic numerical control; no physical data, fitting, or holdout",
            "evidence_artifacts": [OUTPUT.relative_to(ROOT).as_posix()],
            "verification_status": "PASS_BASELINE_REPRODUCTION_AND_SCREEN" if passed else "FAIL_SCREEN_AUDIT",
            "open_blockers": [
                "the finite gain grid does not prove that every continuous scalar gain fails",
                "a source-matched two-face projector-compatible penalty with a discrete energy estimate remains to be derived",
                "positive-shift u2_A, tangential derivatives, edges/corners, variable coefficients, and nonlinear GH remain open",
                "the general curved 3+1 dimensional observable map remains independently open",
            ],
            "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
            "claim_boundary": "Only the declared finite zero-shift LGL scalar-gain screen (weak-penalty and direct-strength grids) is closed. The order-8 direct-strength pass is not resolution robust. This is not a continuum no-go for scalar penalties, not Rinne CPBC closure, and not a UET physical or Gravity result.",
        },
        "scope": {
            "state_variables": ["psi_ab", "Pi_ab", "Phi_xab"],
            "excluded_variables": ["UET C", "UET Phi", "UET Pi", "R_gen", "R_obs"],
            "domain": "finite one-dimensional slab [-1,1], zero shift, normal incidence",
            "space_discretization": "Legendre-Gauss-Lobatto diagonal-norm SBP at orders 8, 12, and 16",
            "time_discretization": "RK4 with dt <= 0.25 times minimum node spacing for the pulse screen",
            "filtering": False,
            "clipping": False,
            "parameter_fitting": False,
            "holdout_access": False,
            "nonlinear_evolution": False,
        },
        "numerical_policy": {
            "gamma2": GAMMA2,
            "sigma_hat_grid": list(SIGMA_GRID),
            "direct_strong_rinne_amplitude_grid": list(DIRECT_STRENGTH_GRID),
            "eigenvalue_real_part_tolerance": EIGENVALUE_TOLERANCE,
            "pulse_energy_ratio_limit": PULSE_ENERGY_RATIO_LIMIT,
            "pulse_final_time": PULSE_FINAL_TIME,
            "unit_normalization": "xi=x/L0; H_hat=H/L0; L0=1",
            "grid_role": "finite sensitivity screen; no continuum or all-parameter no-go claim; direct-strength pass at order 8 alone is not convergence",
        },
        "checks": checks,
        "order_results": order_results,
        "source_hashes": source_hashes,
        "literature_basis": [
            {
                "source_id": "rinne_2006_first_order_gh_radiation_controlling_cpbc",
                "url": "https://arxiv.org/abs/gr-qc/0606053",
                "locator": "Sec. 3 Fourier-Laplace boundary-stability analysis; conclusion on differential boundary conditions",
                "role": "source formulation for first-order GH constraint/Weyl boundary conditions",
                "limit": "the source's boundary-stability analysis is not automatically inherited by this discrete SAT implementation; the paper notes the open sufficiency question for differential boundary conditions with nontrivial data",
            },
            {
                "source_id": "seiler_etal_2008_second_order_harmonic_cp_sat",
                "url": "https://arxiv.org/abs/0802.3341",
                "locator": "Secs. 2-3 and Appendix",
                "role": "separate first-order-in-time, second-order-in-space harmonic CP-SAT comparator route",
                "limit": "different evolution variables and formulation; cannot replace the first-order GH branch without an explicit correspondence",
            },
        ],
        "controlling_blocker": "rinne_differential_constraint_and_weyl_residuals_not_yet_imposed_in_a_full_u1_sbp_sat_evolution",
        "next_action": "Derive a two-face projector-compatible energy estimate for the differential constraint and Weyl residuals; do not continue scalar coefficient sweeps or promote the comparator formulation as a substitute.",
        "claim_boundary": "Finite-grid standard-GR numerical-method diagnostic only; no continuum no-go, full CPBC, curved-parent closure, Gravity compatibility, UET prediction, or global UET closure is claimed.",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "checks": artifact["checks"],
                "orders": [
                    {
                        "lgl_order": row["lgl_order"],
                        "pi_only_max_real": row["pi_only_exact_correction"]["maximum_eigenvalue_real_part"],
                        "pi_only_pulse_ratio": row["pi_only_exact_correction"]["pulse_energy_ratio"],
                        "pi_gain_best": row["weak_pi_residual_gain_scan"]["best_sampled_point"],
                        "char_gain_best": row["weak_incoming_characteristic_gain_scan"]["best_sampled_point"],
                    }
                    for row in artifact["order_results"]
                ],
            },
            indent=2,
        )
    )
    return 0 if artifact["status"] == "PASS_BASELINE_REPRODUCTION_AND_SCREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
