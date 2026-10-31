"""Audit a full-u1 GH maximally dissipative SAT control on an LGL slab."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import sys
import types
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
EQUATION_DIR = ROOT / "docs/core/02_equations/covariant"
PACKAGE_NAME = "_uet_curved_3p1_gh_max_diss_sat_audit"
PACKAGE = types.ModuleType(PACKAGE_NAME)
PACKAGE.__path__ = [str(EQUATION_DIR)]
sys.modules.setdefault(PACKAGE_NAME, PACKAGE)
PROJECTORS = importlib.import_module(
    f"{PACKAGE_NAME}.uet_curved_3p1_gh_boundary_projectors"
)
GH_SLAB = importlib.import_module(
    f"{PACKAGE_NAME}.uet_curved_3p1_gh_full_u1_slab"
)
SAT = importlib.import_module(
    f"{PACKAGE_NAME}.uet_curved_3p1_gh_max_dissipative_sat"
)
gh_max_dissipative_u1_sat_rhs = SAT.gh_max_dissipative_u1_sat_rhs


TT_SOURCE = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_tt_sbp_sat_boundary.py"
RINNE_AUDIT_SOURCE = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_full_u1_cpbc_slab.py"
RINNE_BASELINE_ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_full_u1_cpbc_slab_pilot.json"
)
TT_SPEC = importlib.util.spec_from_file_location("gh_tt_sbp_source", TT_SOURCE)
if TT_SPEC is None or TT_SPEC.loader is None:
    raise ImportError("cannot load the canonical LGL SBP operator")
TT_SBP = importlib.util.module_from_spec(TT_SPEC)
sys.modules[TT_SPEC.name] = TT_SBP
TT_SPEC.loader.exec_module(TT_SBP)
RINNE_SPEC = importlib.util.spec_from_file_location(
    "gh_rinne_slab_audit_source", RINNE_AUDIT_SOURCE
)
if RINNE_SPEC is None or RINNE_SPEC.loader is None:
    raise ImportError("cannot load the frozen Rinne slab audit helpers")
RINNE_AUDIT = importlib.util.module_from_spec(RINNE_SPEC)
sys.modules[RINNE_SPEC.name] = RINNE_AUDIT
RINNE_SPEC.loader.exec_module(RINNE_AUDIT)

OUTPUT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_full_u1_max_diss_sat_control.json"
)
AUDIT_SOURCE = Path(__file__).resolve()
SAT_SOURCE = EQUATION_DIR / "uet_curved_3p1_gh_max_dissipative_sat.py"
SLAB_SOURCE = EQUATION_DIR / "uet_curved_3p1_gh_full_u1_slab.py"
PROJECTOR_SOURCE = EQUATION_DIR / "uet_curved_3p1_gh_boundary_projectors.py"
TT_TEST_SOURCE = ROOT / (
    "docs/core/05_tests/regression/root/"
    "test_uet_curved_3p1_gh_tt_sbp_sat_boundary.py"
)
TEST_SOURCE = ROOT / (
    "docs/core/05_tests/regression/root/"
    "test_uet_curved_3p1_gh_max_dissipative_sat_control.py"
)

GAMMA2 = 0.7
SYMMETRIZER_LAMBDA = 2.0
ORDERS = (4, 8, 12)
EIGENVALUE_TOLERANCE = 1.0e-6
RINNE_PULSE_ENERGY_THRESHOLD = 5.0e-2
RINNE_REDUCTION_TOLERANCE = 2.0e-6
RANDOM_SEED = 20260925


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tensor_metric() -> np.ndarray:
    return np.diag(
        [
            1.0 if i == j else 2.0
            for i, j in PROJECTORS.SYMMETRIC_PAIRS
        ]
    )


def _inner_rows(left: np.ndarray, metric: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.sum((left @ metric) * right, axis=1)


def _energy(
    state: Any, weights: np.ndarray, metric: np.ndarray
) -> float:
    lam2 = SYMMETRIZER_LAMBDA**2
    density = (
        lam2 * _inner_rows(state.metric, metric, state.metric)
        - 2.0 * GAMMA2 * _inner_rows(state.metric, metric, state.normal_derivative)
        + _inner_rows(state.normal_derivative, metric, state.normal_derivative)
        + _inner_rows(
            state.normal_spatial_derivative,
            metric,
            state.normal_spatial_derivative,
        )
    )
    return float(0.5 * (weights @ density))


def _energy_rate(
    state: Any, rhs: Any, weights: np.ndarray, metric: np.ndarray
) -> float:
    lam2 = SYMMETRIZER_LAMBDA**2
    pi_gradient = -GAMMA2 * state.metric + state.normal_derivative
    psi_gradient = lam2 * state.metric - GAMMA2 * state.normal_derivative
    density_rate = (
        _inner_rows(psi_gradient, metric, rhs.metric)
        + _inner_rows(pi_gradient, metric, rhs.normal_derivative)
        + _inner_rows(
            state.normal_spatial_derivative,
            metric,
            rhs.normal_spatial_derivative,
        )
    )
    return float(weights @ density_rate)


def _lower_order_energy_rate(
    state: Any, weights: np.ndarray, metric: np.ndarray
) -> float:
    psi_pi = _inner_rows(state.metric, metric, state.normal_derivative)
    pi_pi = _inner_rows(
        state.normal_derivative, metric, state.normal_derivative
    )
    phi_phi = _inner_rows(
        state.normal_spatial_derivative,
        metric,
        state.normal_spatial_derivative,
    )
    return float(
        weights
        @ (
            -SYMMETRIZER_LAMBDA**2 * psi_pi
            + GAMMA2 * pi_pi
            - GAMMA2 * phi_phi
        )
    )


def _lower_order_growth_constant() -> tuple[float, np.ndarray]:
    lam2 = SYMMETRIZER_LAMBDA**2
    symmetrizer = np.array(
        [
            [lam2, -GAMMA2, 0.0],
            [-GAMMA2, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    lower_order = np.array(
        [
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, -GAMMA2],
        ]
    )
    quadratic = 0.5 * (
        symmetrizer @ lower_order + lower_order.T @ symmetrizer
    )
    chol = np.linalg.cholesky(symmetrizer)
    transformed = np.linalg.solve(chol, quadratic)
    transformed = np.linalg.solve(chol, transformed.T).T
    values = np.linalg.eigvalsh(0.5 * (transformed + transformed.T))
    return float(values[-1]), values


def _energy_balance(
    state: Any,
    rhs: Any,
    weights: np.ndarray,
    metric: np.ndarray,
) -> dict[str, float]:
    boundary_dissipation = 0.0
    for face_index in (0, len(weights) - 1):
        p = (
            state.normal_derivative[face_index]
            - GAMMA2 * state.metric[face_index]
        )
        boundary_dissipation += float(p @ metric @ p)
    observed = _energy_rate(state, rhs, weights, metric)
    lower_order = _lower_order_energy_rate(state, weights, metric)
    expected = lower_order - boundary_dissipation
    mu, _ = _lower_order_growth_constant()
    energy = _energy(state, weights, metric)
    return {
        "observed_energy_rate": observed,
        "lower_order_rate": lower_order,
        "boundary_dissipation": boundary_dissipation,
        "identity_residual": abs(observed - expected),
        "energy": energy,
        "gronwall_slack": 2.0 * mu * energy - boundary_dissipation - observed,
    }


def _reduction_rhs_residual(
    state: Any, rhs: Any, derivative: np.ndarray
) -> float:
    observed = derivative @ rhs.metric - rhs.normal_spatial_derivative
    expected = -GAMMA2 * (
        derivative @ state.metric - state.normal_spatial_derivative
    )
    return float(np.max(np.abs(observed - expected)))


def _operator_matrix(operators: Any) -> np.ndarray:
    derivative = operators.derivative
    weights = operators.norm_weights
    node_count = derivative.shape[0]
    block_size = node_count * 10
    dimension = 3 * block_size
    matrix = np.zeros((dimension, dimension), dtype=float)
    for column in range(dimension):
        basis = np.zeros(dimension, dtype=float)
        basis[column] = 1.0
        state = GH_SLAB.GHSlabState(
            basis[:block_size].reshape(node_count, 10),
            basis[block_size : 2 * block_size].reshape(node_count, 10),
            basis[2 * block_size :].reshape(node_count, 10),
        )
        rhs = gh_max_dissipative_u1_sat_rhs(
            state, derivative, weights, GAMMA2
        )
        matrix[:, column] = np.concatenate(
            (
                rhs.metric.ravel(),
                rhs.normal_derivative.ravel(),
                rhs.normal_spatial_derivative.ravel(),
            )
        )
    return matrix


def _face_normals() -> list[np.ndarray]:
    normals = []
    for a in (-1.0, 0.0, 1.0):
        for b in (-1.0, 0.0, 1.0):
            for c in (-1.0, 0.0, 1.0):
                value = np.array([a, b, c])
                norm = float(np.linalg.norm(value))
                if norm:
                    normals.append(value / norm)
    return normals


def _projector_metric_audit(metric: np.ndarray) -> dict[str, Any]:
    max_self_adjoint = 0.0
    max_orthogonality = 0.0
    max_norm_decomposition = 0.0
    ranks: dict[str, int] | None = None
    rng = np.random.default_rng(RANDOM_SEED)
    for normal in _face_normals():
        projectors = PROJECTORS.build_gh_boundary_projectors(normal)
        current = (
            projectors.constraint,
            projectors.physical,
            projectors.gauge,
        )
        if ranks is None:
            ranks = projectors.ranks
        max_self_adjoint = max(
            max_self_adjoint,
            *(float(np.max(np.abs(metric @ p - p.T @ metric))) for p in current),
        )
        for i in range(3):
            for j in range(3):
                if i != j:
                    max_orthogonality = max(
                        max_orthogonality,
                        float(np.max(np.abs(current[i].T @ metric @ current[j]))),
                    )
        vector = rng.normal(size=10)
        parts = [p @ vector for p in current]
        max_norm_decomposition = max(
            max_norm_decomposition,
            abs(
                float(vector @ metric @ vector)
                - sum(float(part @ metric @ part) for part in parts)
            ),
        )
    return {
        "normal_count": len(_face_normals()),
        "projector_ranks": ranks,
        "tensor_metric_min_eigenvalue": float(np.min(np.linalg.eigvalsh(metric))),
        "max_self_adjoint_residual": max_self_adjoint,
        "max_sector_orthogonality_residual": max_orthogonality,
        "max_norm_decomposition_residual": max_norm_decomposition,
    }


def _order_audit(order: int, tensor_metric: np.ndarray) -> dict[str, Any]:
    operators = TT_SBP.legendre_lobatto_operators(order)
    nodes = operators.nodes
    weights = operators.norm_weights
    derivative = operators.derivative
    node_count = len(nodes)
    boundary = np.zeros((node_count, node_count), dtype=float)
    boundary[0, 0] = -1.0
    boundary[-1, -1] = 1.0
    sbp_defect = np.diag(weights) @ derivative
    sbp_defect += derivative.T @ np.diag(weights) - boundary

    polynomial_defect = 0.0
    for power in range(order + 1):
        exact = (
            np.zeros_like(nodes)
            if power == 0
            else power * nodes ** (power - 1)
        )
        polynomial_defect = max(
            polynomial_defect,
            float(np.max(np.abs(derivative @ nodes**power - exact))),
        )

    rng = np.random.default_rng(RANDOM_SEED + order)
    state = GH_SLAB.GHSlabState(
        rng.normal(size=(node_count, 10)),
        rng.normal(size=(node_count, 10)),
        rng.normal(size=(node_count, 10)),
    )
    rhs = gh_max_dissipative_u1_sat_rhs(
        state, derivative, weights, GAMMA2
    )
    balance = _energy_balance(state, rhs, weights, tensor_metric)
    reduction_residual = _reduction_rhs_residual(state, rhs, derivative)
    matrix = _operator_matrix(operators)
    eigenvalues = np.linalg.eigvals(matrix)
    maximum_real = float(np.max(eigenvalues.real))
    return {
        "order": order,
        "node_count": node_count,
        "state_dimension": int(matrix.shape[0]),
        "sbp_identity_residual": float(np.max(np.abs(sbp_defect))),
        "polynomial_derivative_residual": polynomial_defect,
        "energy_balance": balance,
        "reduction_rhs_identity_residual": reduction_residual,
        "maximum_eigenvalue_real_part": maximum_real,
        "positive_modes_above_1e-6": int(
            np.count_nonzero(eigenvalues.real > EIGENVALUE_TOLERANCE)
        ),
    }


def _strong_rinne_lgl_sensitivity(tensor_metric: np.ndarray) -> dict[str, Any]:
    screens = []
    for order in (8, 12, 16):
        operators = TT_SBP.legendre_lobatto_operators(order)
        matrix = RINNE_AUDIT._linear_operator(
            operators, GAMMA2, "rinne_pointwise"
        )
        eigenvalues = np.linalg.eigvals(matrix)
        initial = RINNE_AUDIT._tt_pulse(operators)
        initial_energy = 0.5 * np.sum(
            operators.norm_weights[:, None]
            * (
                initial.normal_derivative @ tensor_metric
                * initial.normal_derivative
                + initial.normal_spatial_derivative @ tensor_metric
                * initial.normal_spatial_derivative
            )
        )
        dt_cap = 0.25 * float(np.min(np.diff(operators.nodes)))
        final, steps, dt = RINNE_AUDIT._evolve(
            initial,
            operators,
            GAMMA2,
            2.4,
            dt_cap,
            "rinne_pointwise",
        )
        final_energy = 0.5 * np.sum(
            operators.norm_weights[:, None]
            * (
                final.normal_derivative @ tensor_metric
                * final.normal_derivative
                + final.normal_spatial_derivative @ tensor_metric
                * final.normal_spatial_derivative
            )
        )
        pulse_ratio = float(final_energy / initial_energy)
        reduction = float(
            np.max(
                np.abs(
                    operators.derivative @ final.metric
                    - final.normal_spatial_derivative
                )
            )
        )
        positive_modes = int(
            np.count_nonzero(eigenvalues.real > EIGENVALUE_TOLERANCE)
        )
        screens.append(
            {
                "lgl_order": order,
                "node_count": len(operators.nodes),
                "pulse_energy_ratio": pulse_ratio,
                "pulse_absorption_pass": pulse_ratio
                <= RINNE_PULSE_ENERGY_THRESHOLD,
                "final_reduction_constraint_linf": reduction,
                "reduction_constraint_pass": reduction
                <= RINNE_REDUCTION_TOLERANCE,
                "maximum_eigenvalue_real_part": float(
                    np.max(eigenvalues.real)
                ),
                "positive_modes_above_1e-6": positive_modes,
                "spectral_screen_pass": positive_modes == 0,
                "steps": steps,
                "dt": dt,
            }
        )
    passed = all(
        item["pulse_absorption_pass"]
        and item["reduction_constraint_pass"]
        and item["spectral_screen_pass"]
        for item in screens
    )
    return {
        "diagnostic_id": "uet.core.curved_3p1.gh.strong_rinne_lgl_sensitivity",
        "status": "PASS_STRONG_RINNE_LGL_SENSITIVITY"
        if passed
        else "FAIL_STRONG_RINNE_LGL_SENSITIVITY",
        "claim_promotion": False,
        "purpose": "Determine whether changing the strong pointwise Rinne RHS replacement from Chebyshev to LGL alone rescues its declared full-u1 screens.",
        "thresholds": {
            "pulse_energy_ratio_max": RINNE_PULSE_ENERGY_THRESHOLD,
            "reduction_constraint_linf_max": RINNE_REDUCTION_TOLERANCE,
            "positive_eigenvalue_real_part_max": EIGENVALUE_TOLERANCE,
            "pulse_final_time": 2.4,
            "dt_cap": "0.25*minimum_LGL_node_spacing",
        },
        "screens": screens,
        "interpretation": "The tested LGL strong-RHS replacement fails at every tested order; a grid change alone does not resolve the full-u1 pulse/reduction boundary defect. This finite zero-shift slab screen does not establish a continuum no-go.",
        "claim_boundary": "Sensitivity comparison only; not an alternative CPBC implementation or proof that all LGL/SAT discretizations fail.",
    }


def build_artifact() -> dict[str, Any]:
    tensor_metric = _tensor_metric()
    projector_audit = _projector_metric_audit(tensor_metric)
    mu, lower_order_eigenvalues = _lower_order_growth_constant()
    orders = [_order_audit(order, tensor_metric) for order in ORDERS]
    rinne_lgl = _strong_rinne_lgl_sensitivity(tensor_metric)
    checks = {
        "common_positive_tensor_metric": projector_audit[
            "tensor_metric_min_eigenvalue"
        ] > 0.0,
        "projector_ranks_are_4_2_4": projector_audit["projector_ranks"]
        == {"constraint": 4, "physical": 2, "gauge": 4},
        "projectors_are_self_adjoint_and_orthogonal": (
            projector_audit["max_self_adjoint_residual"] <= 1.0e-12
            and projector_audit["max_sector_orthogonality_residual"] <= 1.0e-12
            and projector_audit["max_norm_decomposition_residual"] <= 1.0e-11
        ),
        "lower_order_energy_bound_is_finite": np.isfinite(mu) and mu > 0.0,
        "sbp_identity_passes_all_orders": all(
            item["sbp_identity_residual"] <= 2.0e-12 for item in orders
        ),
        "polynomial_derivatives_pass_all_orders": all(
            item["polynomial_derivative_residual"] <= 2.0e-10
            for item in orders
        ),
        "energy_balance_identity_passes_all_orders": all(
            item["energy_balance"]["identity_residual"] <= 2.0e-10
            for item in orders
        ),
        "gronwall_bound_holds_all_orders": all(
            item["energy_balance"]["gronwall_slack"] >= -2.0e-10
            for item in orders
        ),
        "reduction_constraint_damping_identity_passes": all(
            item["reduction_rhs_identity_residual"] <= 2.0e-10
            for item in orders
        ),
        "spectrum_has_no_resolved_growing_modes": all(
            item["positive_modes_above_1e-6"] == 0 for item in orders
        ),
    }
    source_paths = (
        AUDIT_SOURCE,
        SAT_SOURCE,
        SLAB_SOURCE,
        PROJECTOR_SOURCE,
        TT_SOURCE,
        TT_TEST_SOURCE,
        TEST_SOURCE,
    )
    return {
        "schema_version": "core-curved-3p1-gh-max-diss-sat-control-v1",
        "artifact": "curved_3p1_gh_full_u1_max_diss_sat_control",
        "generated_at": date.today().isoformat(),
        "status": "PASS_FULL_U1_MAX_DISS_SAT_CONTROL"
        if all(checks.values())
        else "FAIL_FULL_U1_MAX_DISS_SAT_CONTROL",
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_MAX_DISSIPATIVE_SAT_CONTROL",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE"
            if all(checks.values())
            else "PARTIAL",
            "what_is_closed": [
                "a full ten-component frozen-background GH slab has a weak incoming-u1 maximally dissipative SAT control",
                "the packed symmetric-tensor Frobenius metric makes the 4+2+4 boundary projectors self-adjoint and mutually orthogonal on the declared normal set",
                "the LGL-SBP semidiscrete energy balance includes an explicit lower-order Gronwall term and nonnegative boundary dissipation",
                "the definition/reduction constraint obeys Cdot=-gamma2*C under the Pi-only SAT",
            ],
            "equation_or_mapping": {
                "incoming_u1_minus": "q_n=Pi-n*Phi_n-gamma2*psi",
                "sat": "Pi_dot=-D(Phi)-H^-1 e_L*(q_L-g_L)-H^-1 e_R*(q_R-g_R); psi_dot=-Pi; Phi_dot=-D(Pi)+gamma2*D(psi)-gamma2*Phi",
                "tensor_metric": "G_ab,cd induces sum_ab T_ab^2; in packed symmetric coordinates diag(G) is 1 on diagonal entries and 2 on off-diagonal entries",
                "energy": "E=1/2 sum_j w_j[lambda^2||psi||_G^2-2*gamma2<psi,Pi>_G+||Pi||_G^2+||Phi||_G^2]",
                "energy_rate": "dE/dt=R_lower-sum_faces||Pi-gamma2*psi||_G^2 for homogeneous incoming data",
                "lower_order_bound": "R_lower<=2*mu*E; mu=lambda_max(S^-1/2*K0*S^-1/2), K0=(S*L0+L0^T*S)/2",
                "reduction_constraint": "C=D(psi)-Phi; Cdot=-gamma2*C",
            },
            "units": {
                "unit_lane": "geometric units with slab length L0=1",
                "psi": "dimensionless",
                "Pi_Phi_gamma2": "L0^-1",
                "time_rhs": "L0^-2",
                "energy": "positive mathematical GH symmetrizer; not SI energy",
            },
            "derivation_class": "standard linear generalized-harmonic system with an SBP-SAT energy identity and synthetic numerical controls",
            "observable": "semidiscrete energy balance, reduction-constraint RHS, projector metric residuals, and eigenvalue screens",
            "data_role": "ANALYTIC_AND_SYNTHETIC_NUMERICAL_CONTROL; no external source rows, fitting, or holdout",
            "evidence_artifacts": [
                "docs/core/07_artifacts/verification/curved_3p1_gh_full_u1_max_diss_sat_control.json"
            ],
            "verification_status": "PASS_FULL_U1_MAX_DISS_SAT_CONTROL"
            if all(checks.values())
            else "FAIL_FULL_U1_MAX_DISS_SAT_CONTROL",
            "open_blockers": [
                "this direct characteristic control does not impose Rinne differential constraint or Weyl/Psi_0 residuals",
                "the strong pointwise Rinne RHS replacement also fails the declared LGL pulse/reduction screens at orders 8, 12, and 16; this finite comparison does not establish a continuum no-go",
                "positive-normal-shift incoming u2_A conditions, tangential derivatives, edges/corners, variable coefficients, and nonlinear GH remain open",
                "the curved 3+1 dimensional observable parent remains independently open",
            ],
            "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
            "claim_boundary": "A full-u1 standard-GR numerical control for direct incoming characteristic data only; not the differential Rinne CPBC, a continuum nonlinear IBVP proof, Gravity compatibility, Einstein-equation derivation by UET, or global UET closure.",
        },
        "scope": {
            "state_variables": ["psi_ab", "Pi_ab", "Phi_xab"],
            "excluded_variables": ["UET C", "UET Phi", "UET Pi", "R_gen", "R_obs"],
            "domain": "finite one-dimensional slab [-1,1], zero shift, normal incidence",
            "boundary_condition": "weak homogeneous maximally dissipative incoming u1-minus data; not Rinne differential CPBC",
            "space_discretization": "Legendre-Gauss-Lobatto diagonal-norm SBP",
            "filtering": False,
            "clipping": False,
            "parameter_fitting": False,
            "nonlinear_evolution": False,
            "positive_shift_u2_A": False,
            "tangential_derivatives": False,
        },
        "checks": checks,
        "parameters": {
            "gamma2": GAMMA2,
            "symmetrizer_lambda": SYMMETRIZER_LAMBDA,
            "lgl_orders": list(ORDERS),
            "eigenvalue_real_part_tolerance": EIGENVALUE_TOLERANCE,
            "random_seed": RANDOM_SEED,
            "lower_order_growth_mu": mu,
            "energy_growth_constant_2mu": 2.0 * mu,
            "lower_order_generalized_eigenvalues": [
                float(value) for value in lower_order_eigenvalues
            ],
        },
        "metrics": {
            "projector_metric_audit": projector_audit,
            "lgl_order_screens": orders,
        },
        "method_comparison": rinne_lgl,
        "source_hashes": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (*source_paths, RINNE_AUDIT_SOURCE, RINNE_BASELINE_ARTIFACT)
        },
        "literature_basis": [
            {
                "source_id": "rinne_2006_first_order_gh_radiation_controlling_cpbc",
                "url": "https://arxiv.org/abs/gr-qc/0606053",
                "locators": ["Eqs. (9)-(11)", "Secs. 2.2-2.4"],
                "role": "source for GH characteristic fields and the differential constraint, Weyl, and gauge boundary conditions",
                "limitation": "this control imposes direct incoming characteristic data and does not implement the differential Rinne conditions",
            }
        ],
        "controlling_blocker": "rinne_differential_constraint_and_weyl_residuals_not_yet_imposed_in_a_full_u1_sbp_sat_evolution",
        "next_action": "Use this uniform-in-grid energy estimate as the control baseline; derive a projector-compatible penalty for the differential constraint and Weyl residuals, then repeat the energy and subsidiary-constraint analysis without relaxing the source conditions.",
        "claim_boundary": "No Rinne differential CPBC, nonlinear GH boundary evolution, curved-parent closure, Gravity unlock, physical observable validation, or UET claim promotion is claimed.",
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
                "metrics": artifact["metrics"],
            },
            indent=2,
        )
    )
    return 0 if artifact["status"] == "PASS_FULL_U1_MAX_DISS_SAT_CONTROL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
