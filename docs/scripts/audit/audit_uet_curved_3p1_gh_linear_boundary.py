"""Verify local frozen-background GH differential boundary residuals."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_artifact_path

_projector_module = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gh_boundary_projectors"
)
_boundary_module = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gh_linear_boundary"
)
_gh_module = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_generalized_harmonic"
)
apply_gh_boundary_projector = _projector_module.apply_gh_boundary_projector
build_gh_boundary_projectors = _projector_module.build_gh_boundary_projectors
SYMMETRIC_PAIRS = _projector_module.SYMMETRIC_PAIRS
gh_boundary_normal_maps = _boundary_module.gh_boundary_normal_maps
gh_linear_boundary_residuals = _boundary_module.gh_linear_boundary_residuals
GHParameters = _gh_module.GHParameters
gh_principal_symbol = _gh_module.gh_principal_symbol


OUT = canonical_artifact_path(
    "curved_3p1_gh_linear_boundary_residual_audit.json", "verification"
)
PROJECTOR_SOURCE = "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
BOUNDARY_SOURCE = "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
GH_SOURCE = "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"
AUDIT_SOURCE = "docs/scripts/audit/audit_uet_curved_3p1_gh_linear_boundary.py"
TEST_SOURCE = "docs/core/05_tests/regression/root/test_uet_curved_3p1_gh_linear_boundary.py"
TOLERANCE = 1.0e-10


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _symmetric(rng: np.random.Generator, prefix: tuple[int, ...] = ()) -> np.ndarray:
    raw = rng.normal(size=prefix + (4, 4))
    return 0.5 * (raw + np.swapaxes(raw, -1, -2))


def _directions() -> tuple[np.ndarray, ...]:
    return tuple(
        np.asarray(value, dtype=float) / np.linalg.norm(value)
        for value in product((-1.0, 0.0, 1.0), repeat=3)
        if value != (0.0, 0.0, 0.0)
    )


def _empty_jet() -> dict[str, np.ndarray]:
    return {
        "metric_perturbation": np.zeros((4, 4)),
        "pi_perturbation": np.zeros((4, 4)),
        "phi_perturbation": np.zeros((3, 4, 4)),
        "metric_gradient": np.zeros((3, 4, 4)),
        "pi_gradient": np.zeros((3, 4, 4)),
        "phi_gradient": np.zeros((3, 3, 4, 4)),
    }


def _data_sector_control(normal: np.ndarray) -> tuple[float, float]:
    projectors = build_gh_boundary_projectors(normal)
    raw = np.arange(16, dtype=float).reshape(4, 4)
    symmetric = 0.5 * (raw + raw.T)
    physical_data = apply_gh_boundary_projector(symmetric, projectors.physical)
    gauge_data = apply_gh_boundary_projector(symmetric, projectors.gauge)
    jet = _empty_jet()
    jet["pi_perturbation"] = gauge_data
    jet["pi_gradient"] = normal[:, None, None] * physical_data[None, :, :]
    result = gh_linear_boundary_residuals(
        **jet,
        normal=normal,
        physical_data=physical_data,
        gauge_data=gauge_data,
    )
    return (
        float(np.max(np.abs(result.physical_weyl_incoming))),
        float(np.max(np.abs(result.gauge_incoming))),
    )


def _u2_hessian_control(normal: np.ndarray) -> float:
    rng = np.random.default_rng(20260925)
    hessian = rng.normal(size=(3, 3))
    hessian = 0.5 * (hessian + hessian.T)
    tensor = _symmetric(rng)
    jet = _empty_jet()
    jet["phi_gradient"] = np.einsum("ij,ab->ijab", hessian, tensor)
    result = gh_linear_boundary_residuals(
        **jet, normal=normal, normal_shift=0.2
    )
    return float(np.max(np.abs(result.u2_curl_incoming)))


def _u2_normal_map_control() -> tuple[int, float]:
    normal = np.array([1.0, 0.0, 0.0])
    normal_map = np.zeros((20, 20), dtype=float)
    for column in range(20):
        tangent_index, tensor_index = divmod(column, len(SYMMETRIC_PAIRS))
        i, j = SYMMETRIC_PAIRS[tensor_index]
        jet = _empty_jet()
        jet["phi_gradient"][0, tangent_index + 1, i, j] = 1.0
        jet["phi_gradient"][0, tangent_index + 1, j, i] = 1.0
        result = gh_linear_boundary_residuals(
            **jet, normal=normal, normal_shift=0.2
        )
        row = 0
        for tangent_output in range(2):
            for a, b in SYMMETRIC_PAIRS:
                normal_map[row, column] = result.u2_curl_incoming[
                    tangent_output, a, b
                ]
                row += 1
    return int(np.linalg.matrix_rank(normal_map, tol=1.0e-10)), float(
        np.max(np.abs(normal_map - np.eye(20)))
    )


def _incoming_condition_count_control(normal: np.ndarray) -> tuple[bool, int, int, int]:
    maps = gh_boundary_normal_maps(normal)
    gauge_projector = np.eye(10) - maps["constraint_projector"] - maps["physical_projector"]
    base_condition_count = (
        int(np.linalg.matrix_rank(maps["constraint"], tol=1.0e-10))
        + int(np.linalg.matrix_rank(maps["physical"], tol=1.0e-10))
        + int(np.linalg.matrix_rank(gauge_projector, tol=1.0e-10))
    )
    maximum_count_mismatch = 0
    observed_counts: list[int] = []
    for normal_shift in (-0.2, 0.0, 0.2):
        parameters = GHParameters(
            lapse=1.0,
            shift=tuple(float(value) for value in normal_shift * normal),
            gamma2=0.6,
            symmetrizer_lambda=1.0,
        )
        speeds = gh_principal_symbol(normal, parameters).characteristic_speeds
        incoming_mode_count = int(np.count_nonzero(speeds < -1.0e-10)) * 10
        condition_count = base_condition_count + (20 if normal_shift > 0.0 else 0)
        observed_counts.append(incoming_mode_count)
        maximum_count_mismatch = max(
            maximum_count_mismatch, abs(incoming_mode_count - condition_count)
        )
    expected = observed_counts == [10, 10, 30]
    return expected and maximum_count_mismatch == 0, maximum_count_mismatch, *observed_counts


def build_artifact() -> dict[str, Any]:
    max_constraint_kernel = 0.0
    max_physical_kernel = 0.0
    max_physical_data_residual = 0.0
    max_gauge_data_residual = 0.0
    max_u2_hessian_residual = 0.0
    max_zero_jet_residual = 0.0
    u2_normal_rank, max_u2_normal_map_residual = _u2_normal_map_control()
    incoming_count_cases_pass = True
    maximum_incoming_count_mismatch = 0
    incoming_counts_by_shift = {"negative": set(), "zero": set(), "positive": set()}
    normal_map_ranks_pass = True
    regime_cases_pass = True

    for index, normal in enumerate(_directions()):
        maps = gh_boundary_normal_maps(normal)
        normal_map_ranks_pass &= (
            int(np.linalg.matrix_rank(maps["constraint"], tol=1.0e-10)) == 4
            and int(np.linalg.matrix_rank(maps["physical"], tol=1.0e-10)) == 2
        )
        max_constraint_kernel = max(
            max_constraint_kernel,
            float(
                np.max(
                    np.abs(
                        maps["constraint"]
                        @ (np.eye(10) - maps["constraint_projector"])
                    )
                )
            ),
        )
        max_physical_kernel = max(
            max_physical_kernel,
            float(
                np.max(
                    np.abs(
                        maps["physical"]
                        @ (np.eye(10) - maps["physical_projector"])
                    )
                )
            ),
        )
        physical_error, gauge_error = _data_sector_control(normal)
        max_physical_data_residual = max(max_physical_data_residual, physical_error)
        max_gauge_data_residual = max(max_gauge_data_residual, gauge_error)
        max_u2_hessian_residual = max(
            max_u2_hessian_residual, _u2_hessian_control(normal)
        )
        counts_pass, count_mismatch, negative_count, zero_count, positive_count = (
            _incoming_condition_count_control(normal)
        )
        incoming_count_cases_pass &= counts_pass
        maximum_incoming_count_mismatch = max(
            maximum_incoming_count_mismatch, count_mismatch
        )
        incoming_counts_by_shift["negative"].add(negative_count)
        incoming_counts_by_shift["zero"].add(zero_count)
        incoming_counts_by_shift["positive"].add(positive_count)

        empty = gh_linear_boundary_residuals(
            **_empty_jet(), normal=normal, normal_shift=(-0.2 if index % 2 == 0 else 0.2)
        )
        max_zero_jet_residual = max(
            max_zero_jet_residual,
            *(
                float(np.max(np.abs(value)))
                for value in (
                    empty.constraint_incoming,
                    empty.physical_weyl_incoming,
                    empty.gauge_incoming,
                    empty.u2_curl_incoming,
                )
            ),
        )
        expected_regime = (
            "U1_ONLY_INCOMING_SUBLUMINAL"
            if index % 2 == 0
            else "U1_AND_U2_INCOMING_SUBLUMINAL"
        )
        regime_cases_pass &= empty.boundary_regime == expected_regime

    checks = {
        "constraint_normal_map_rank_four_and_projector_kernel": (
            normal_map_ranks_pass and max_constraint_kernel <= TOLERANCE
        ),
        "physical_normal_map_rank_two_and_projector_kernel": (
            normal_map_ranks_pass and max_physical_kernel <= TOLERANCE
        ),
        "prescribed_physical_and_gauge_data_are_satisfied_in_their_sectors": (
            max_physical_data_residual <= TOLERANCE
            and max_gauge_data_residual <= TOLERANCE
        ),
        "mixed_derivative_compatibility_sets_incoming_u2_curl_to_zero": (
            max_u2_hessian_residual <= TOLERANCE
        ),
        "positive_shift_u2_normal_map_has_rank_twenty": (
            u2_normal_rank == 20 and max_u2_normal_map_residual <= TOLERANCE
        ),
        "boundary_condition_counts_match_gh_incoming_characteristics": (
            incoming_count_cases_pass and maximum_incoming_count_mismatch == 0
        ),
        "homogeneous_zero_jet_and_shift_regime_classification": (
            max_zero_jet_residual <= TOLERANCE and regime_cases_pass
        ),
    }
    source_hashes = {
        source: _sha256(ROOT / source)
        for source in (
            PROJECTOR_SOURCE,
            BOUNDARY_SOURCE,
            GH_SOURCE,
            AUDIT_SOURCE,
            TEST_SOURCE,
        )
    }
    passed = all(checks.values())
    return {
        "schema_version": "core-curved-3p1-gh-linear-boundary-v1",
        "diagnostic_id": "uet.curved_3p1.gh.linear_boundary_residuals",
        "artifact": "curved_3p1_gh_linear_boundary_residual_audit",
        "generated_at": "2026-09-25",
        "status": "PASS_GH_LINEAR_BOUNDARY_RESIDUAL_OPERATOR_AUDIT" if passed else "FAIL_GH_LINEAR_BOUNDARY_RESIDUAL_OPERATOR_AUDIT",
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_LINEAR_DIFFERENTIAL_BOUNDARY_RESIDUALS",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "frozen-background linear GH residual evaluation for the incoming subsidiary constraint, Weyl/Psi_0 radiation, and gauge data",
                "rank-4 and rank-2 normal-derivative maps match the complementary kernels of the source-defined constraint and physical projectors",
                "incoming u2_A definition-curl residual evaluation for positive subluminal normal shift"
            ] if passed else [],
            "equation_or_mapping": {
                "constraint": "c0_minus_a=0 using Rinne 2006 Eq. (27)",
                "physical": "w_minus_ab=partial_t hP_ab using Rinne 2006 Eqs. (30)-(33)",
                "gauge": "P_G u1_minus_ab=hG_ab using Rinne 2006 Eqs. (35)-(36)",
                "positive_shift": "partial_n u2_Aab-partial_A Phi_nab=0 using Rinne 2006 Eq. (29)",
                "incoming_u1": "u1_minus=delta_Pi-delta_Phi_n-gamma2*delta_psi",
                "normal_maps": "rank(A_C)=4, rank(A_P)=2; A_C(I-P_C)=0 and A_P(I-P_P)=0",
                "boundary_condition_count": {
                    "nonpositive_normal_shift": "10 incoming u1_minus fields = 4 constraint derivative + 2 physical derivative + 4 gauge data",
                    "zero_normal_shift": "10 incoming u1_minus fields; u2_A modes are glancing",
                    "positive_sub_luminal_normal_shift": "30 incoming fields = previous 10 + 20 u2_A definition-curl conditions",
                    "verification": "incoming characteristic counts compared with projector ranks and the measured rank-20 u2_A normal map over all 26 face normals"
                }
            },
            "units": {
                "unit_lane": "geometric c=1, local orthonormal frame",
                "delta_psi": "dimensionless",
                "delta_Pi_and_delta_Phi": "L^-1",
                "gamma2": "L^-1",
                "constraint_and_weyl_residuals": "L^-2",
                "physical_boundary_data_partial_t_hP": "L^-2",
                "gauge_residual": "L^-1",
                "gauge_boundary_data_hG": "L^-1",
                "u2_definition_curl_residual": "L^-2"
            },
            "derivation_class": "source-locked linearized/frozen-coefficient GH boundary formulas with local deterministic verification",
            "observable": "boundary residual components and projector-kernel residuals; no gravitational observable",
            "data_role": "manufactured analytic tensors only; no physical data, fitting, or holdout",
            "evidence_artifacts": [],
            "verification_status": "PASS_GH_LINEAR_BOUNDARY_RESIDUAL_OPERATOR_AUDIT" if passed else "FAIL_GH_LINEAR_BOUNDARY_RESIDUAL_OPERATOR_AUDIT",
            "open_blockers": [
                "no nonlinear variable-coefficient boundary operator",
                "no SBP/SAT or other non-periodic initial-boundary evolution implementation",
                "no boundary energy estimate or numerical stability/convergence result",
                "no edge/corner compatibility analysis",
                "no self-consistent matter boundary subsystem or dimensional gravitational-observable map"
            ],
            "dependency_unlocked": "local boundary-residual implementation and verification only; parent remains PARTIAL and Gravity remains blocked",
            "claim_boundary": "This verifies source-matched frozen-background linear residual maps only; it does not implement CPBC on the nonlinear solver or prove a well-posed repository IBVP."
        },
        "scope": {
            "normal_count": 26,
            "normal_shift_regimes": ["-lapse < beta_n <= 0: u1_minus incoming", "0 < beta_n < lapse: u1_minus and u2_A incoming"],
            "coefficient_background": "Minkowski local orthonormal frame",
            "equation_approximation": "linearized principal/frozen-coefficient boundary residuals",
            "boundary_operator_applied_to_evolution": False,
            "periodic_solver_modified": False,
            "UET_ontology_modified": False,
            "excluded_variables": ["UET C", "UET Phi", "R_gen", "R_obs"]
        },
        "tolerance": TOLERANCE,
        "checks": checks,
        "metrics": {
            "maximum_constraint_projector_kernel_residual": max_constraint_kernel,
            "maximum_physical_projector_kernel_residual": max_physical_kernel,
            "maximum_physical_prescribed_data_residual": max_physical_data_residual,
            "maximum_gauge_prescribed_data_residual": max_gauge_data_residual,
            "maximum_u2_symmetric_hessian_curl_residual": max_u2_hessian_residual,
            "u2_normal_map_rank": u2_normal_rank,
            "maximum_u2_normal_map_identity_residual": max_u2_normal_map_residual,
            "incoming_count_cases": 26 * 3,
            "incoming_counts_by_shift": {
                key: sorted(value) for key, value in incoming_counts_by_shift.items()
            },
            "maximum_incoming_condition_count_mismatch": maximum_incoming_count_mismatch,
            "maximum_homogeneous_zero_jet_residual": max_zero_jet_residual
        },
        "source_hashes": source_hashes,
        "literature_basis": [
            {
                "citation": "O. Rinne, Stable radiation-controlling boundary conditions for the generalized harmonic Einstein equations (2006)",
                "url": "https://arxiv.org/abs/gr-qc/0606053",
                "locators": "Eqs. (27)-(33), (35)-(36); subluminal normal-shift analysis",
                "role": "source for the differential subsidiary-constraint and Weyl boundary conditions, algebraic gauge data, and incoming u2_A definition-constraint condition"
            },
            {
                "citation": "G. Calabrese and O. Sarbach, Detecting ill posed boundary conditions in General Relativity (2003)",
                "url": "https://arxiv.org/abs/gr-qc/0303040",
                "role": "well-posedness caution; motivates keeping the IBVP and stability gates open"
            }
        ],
        "claim_boundary": "No CPBC solver pass, nonlinear well-posedness claim, Einstein-equation derivation, external gravity test, or global UET closure."
    }


def main() -> int:
    artifact = build_artifact()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "major_result_id": artifact["major_result"]["major_result_id"],
                "closure_level": artifact["major_result"]["closure_level"],
                "checks": artifact["checks"],
                "metrics": artifact["metrics"],
            },
            indent=2,
        )
    )
    return 0 if artifact["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
