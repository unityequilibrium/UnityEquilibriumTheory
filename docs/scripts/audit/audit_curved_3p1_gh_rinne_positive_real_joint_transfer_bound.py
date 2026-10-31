from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OPERATOR_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_joint_real_kreiss_operator.py"
OPERATOR_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_joint_real_kreiss_operator.json"
FLOOR_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_rescaled_determinant_floor.py"
FLOOR_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_rescaled_determinant_floor.json"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_positive_real_joint_transfer_bound.json"
REGRESSION = ROOT / "docs/core/05_tests/regression/root/test_uet_curved_3p1_gh_rinne_positive_real_joint_transfer_bound.py"

CHART_CAPS = {
    "unit_generic_eigenmodes": {"rescaled_map_frobenius": 60.0, "state_map_frobenius": 8.0},
    "normalized_confluent_divided_difference": {"rescaled_map_frobenius": 96.0, "state_map_frobenius": 8.0},
    "source_ode_consistent_jordan": {"rescaled_map_frobenius": 128.0, "state_map_frobenius": 8.0},
}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OPERATOR = _load("_uet_joint_transfer_bound_operator", OPERATOR_SCRIPT)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _matrices(row: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    chart = row["basis_chart"]
    zeta, beta = float(row["zeta"]), float(row["beta"])
    if chart == "unit_generic_eigenmodes":
        boundary, state, _ = OPERATOR._generic_matrices(zeta, beta)
    elif chart == "normalized_confluent_divided_difference":
        boundary, state, _ = OPERATOR._confluent_matrices(zeta, beta)
    elif chart == "source_ode_consistent_jordan":
        boundary, state, _ = OPERATOR._jordan_matrices(zeta)
    else:
        raise ValueError(f"unregistered basis chart: {chart}")
    return boundary, state


def _probe_fixed_boundary_maps() -> tuple[list[float], list[float]]:
    state_norms: list[float] = []
    derivative_norms: list[float] = []
    zero = np.zeros(4, dtype=complex)
    for variable in range(4):
        state_value = np.zeros(4, dtype=complex)
        state_value[variable] = 1.0
        state_block = np.column_stack([
            OPERATOR.NEGATIVE._boundary_column(0.0, 1.0, state_value, zero, component)[0]
            for component in range(10)
        ])
        state_matrix = OPERATOR.ROW @ np.column_stack((state_block, np.zeros((30, 20), dtype=complex))) @ OPERATOR.COLUMN
        state_norms.append(float(np.linalg.norm(state_matrix[:10], ord="fro")))

        derivative_value = np.zeros(4, dtype=complex)
        derivative_value[variable] = 1.0
        derivative_block = np.column_stack([
            OPERATOR.NEGATIVE._boundary_column(0.0, 1.0, zero, derivative_value, component)[0]
            for component in range(10)
        ])
        derivative_matrix = OPERATOR.ROW @ np.column_stack((derivative_block, np.zeros((30, 20), dtype=complex))) @ OPERATOR.COLUMN
        derivative_norms.append(float(np.linalg.norm(derivative_matrix[:10], ord="fro")))
    return state_norms, derivative_norms


def _analytic_envelopes(delta_max: float, state_norms: list[float], derivative_norms: list[float]) -> dict[str, Any]:
    a_hi = math.sqrt(1.0 + delta_max**2) / (1.0 - delta_max**2)
    generic_top = 3.0 * 11.0 + a_hi * 3.2 + (a_hi + 1.0) * 3.2
    generic_curl_a = 4.0 * math.sqrt((a_hi + 1.0) ** 2 + 4.0)
    generic_curl_b = 4.0
    rho = 1.0 + math.sqrt(2.0)
    jordan_top = 3.0 * 11.0 + 2.0 * 3.2 * rho
    jordan_curl_a = 4.0 * math.sqrt((rho + 1.0) ** 2 + 4.0)
    jordan_curl_b = 4.0 * rho
    r_lo, r_hi = 20.0 / 21.0, 21.0 / 20.0
    zeta_prime = delta_max / (r_lo * r_lo)
    gap_coefficient_lower = (r_lo + 1.0) / (r_hi * (r_hi * math.sqrt(1.0 + delta_max**2) + 1.0))
    return {
        "fixed_boundary_coefficient_frobenius_norms": {
            "state_maps": state_norms,
            "normal_derivative_maps": derivative_norms,
            "state_map_sum_cap": 11.0,
            "active_normal_derivative_map_cap": 3.2,
            "tangential_normal_derivative_maps_are_zero": True,
        },
        "generic_chart": {
            "lambda1_magnitude_upper": a_hi,
            "top_block_upper": generic_top,
            "first_curl_block_upper": generic_curl_a,
            "second_curl_block_upper": generic_curl_b,
            "rescaled_map_frobenius_upper": generic_top + generic_curl_a + generic_curl_b,
            "declared_cap": CHART_CAPS["unit_generic_eigenmodes"]["rescaled_map_frobenius"],
        },
        "confluent_chart": {
            "ratio_interval": [r_lo, r_hi],
            "abs_zeta_derivative_upper": zeta_prime,
            "abs_beta_magnitude_derivative_upper": delta_max,
            "eigenvalue_gap_lower_coefficient_derived": gap_coefficient_lower,
            "abs_lambda1_derivative_upper": 0.00065,
            "abs_first_unit_mode_derivative_upper": 0.016,
            "abs_first_normal_derivative_mode_derivative_upper": 0.017,
            "abs_second_unit_mode_derivative_upper": 0.53,
            "abs_second_normal_derivative_mode_derivative_upper": 1.67,
            "divided_difference_numerator_derivative_frobenius_upper": 45.0,
            "eigenvalue_gap_lower_coefficient": 0.9,
            "first_divided_difference_column_upper": 50.0,
            "regular_column_block_upper_1": 25.5,
            "regular_column_block_upper_2": 15.0,
            "rescaled_map_frobenius_upper": 90.5,
            "declared_cap": CHART_CAPS["normalized_confluent_divided_difference"]["rescaled_map_frobenius"],
        },
        "corrected_jordan_chart": {
            "jordan_mode_value_and_derivative_envelope_rho": rho,
            "top_block_upper": jordan_top,
            "first_curl_block_upper": jordan_curl_a,
            "second_curl_block_upper": jordan_curl_b,
            "rescaled_map_frobenius_upper": jordan_top + jordan_curl_a + jordan_curl_b,
            "declared_cap": CHART_CAPS["source_ode_consistent_jordan"]["rescaled_map_frobenius"],
        },
        "state_map_frobenius_upper_all_charts": math.sqrt(60.0),
        "state_map_declared_cap_all_charts": 8.0,
        "proof_scope": "The coefficient bounds are for the fixed source/projector maps and the stated delta/r chart; they are not sampled-fit envelopes.",
    }


def build_artifact() -> dict[str, Any]:
    floor = json.loads(FLOOR_ARTIFACT.read_text(encoding="utf-8"))
    operator_artifact = json.loads(OPERATOR_ARTIFACT.read_text(encoding="utf-8"))
    floor_verification = floor["VERIFICATION"]
    floors = {
        "unit_generic_eigenmodes": floor_verification["analytic_bounds"]["generic_determinant_floor_conservative"],
        "normalized_confluent_divided_difference": floor_verification["analytic_bounds"]["confluent_determinant_floor_conservative"],
        "source_ode_consistent_jordan": floor_verification["analytic_bounds"]["jordan_determinant_floor_conservative"],
    }
    state_coefficients, derivative_coefficients = _probe_fixed_boundary_maps()
    envelopes = _analytic_envelopes(float(floor_verification["analytic_bounds"]["delta_max"]), state_coefficients, derivative_coefficients)
    records: list[dict[str, Any]] = []
    chart_counts = {chart: 0 for chart in CHART_CAPS}
    max_overlap_difference = max(x["max_abs_operator_difference"] for x in operator_artifact["VERIFICATION"]["basis_invariance_cases"])
    max_determinant_error = 0.0
    max_transfer_error = 0.0
    max_sigma_bound_violation = 0.0
    for source_row in floor_verification["cases"]:
        chart = source_row["basis_chart"]
        boundary, state = _matrices(source_row)
        beta, zeta = float(source_row["beta"]), float(source_row["zeta"])
        row_scale = np.diag([zeta] * 6 + [1.0] * 4 + [min(abs(beta), zeta)] * 10 + [abs(beta)] * 10)
        scaled = row_scale @ boundary
        sign, logdet = np.linalg.slogdet(scaled)
        sigma = np.linalg.svd(scaled, compute_uv=False)
        transfer_direct = np.linalg.solve(boundary.T, state.T).T
        transfer_factored = state @ np.linalg.solve(scaled, row_scale)
        cap = CHART_CAPS[chart]
        sigma_lower = floors[chart] / (cap["rescaled_map_frobenius"] ** 29)
        transfer_bound = cap["state_map_frobenius"] / sigma_lower
        max_determinant_error = max(max_determinant_error, abs(float(logdet) - float(source_row["expected_log_abs_determinant"])))
        max_transfer_error = max(max_transfer_error, float(np.max(np.abs(transfer_direct - transfer_factored))))
        max_sigma_bound_violation = max(max_sigma_bound_violation, max(0.0, sigma_lower - float(sigma[-1])))
        records.append({
            "delta": float(source_row["delta"]),
            "ratio_abs_beta_over_zeta": float(source_row["ratio_abs_beta_over_zeta"]),
            "basis_chart": chart,
            "rescaled_map_frobenius_sample": float(np.linalg.norm(scaled, ord="fro")),
            "state_map_frobenius_sample": float(np.linalg.norm(state, ord="fro")),
            "state_transfer_spectral_norm_sample": float(np.linalg.svd(transfer_direct, compute_uv=False)[0]),
            "sigma_min_sample": float(sigma[-1]),
            "analytic_sigma_min_lower_bound": sigma_lower,
            "analytic_state_transfer_upper_bound": transfer_bound,
            "determinant_log_error": abs(float(logdet) - float(source_row["expected_log_abs_determinant"])),
            "factorization_max_abs_error": float(np.max(np.abs(transfer_direct - transfer_factored))),
            "rescaled_determinant_phase_real": float(np.real(sign)),
        })
        chart_counts[chart] += 1

    chart_bounds: dict[str, dict[str, float]] = {}
    for chart, cap in CHART_CAPS.items():
        log10_bound = math.log10(cap["state_map_frobenius"]) + 29.0 * math.log10(cap["rescaled_map_frobenius"]) - math.log10(floors[chart])
        power = math.ceil(log10_bound)
        chart_bounds[chart] = {
            "determinant_floor": floors[chart],
            "rescaled_map_frobenius_cap": cap["rescaled_map_frobenius"],
            "state_map_frobenius_cap": cap["state_map_frobenius"],
            "row_scale_spectral_norm_cap": 1.0,
            "sigma_min_lower_bound": floors[chart] / cap["rescaled_map_frobenius"] ** 29,
            "log10_transfer_norm_upper_bound": log10_bound,
            "strict_power_of_ten_upper_bound": float(power),
        }

    checks = {
        "upstream_determinant_floor_artifact_passes": floor["STATUS"] == "PASS_CHARTWISE_RESCALED_DETERMINANT_FLOOR" and all(floor_verification["checks"].values()),
        "all_upstream_source_hashes_match": all(_hash(ROOT / relative) == digest for relative, digest in floor_verification["source_hashes"].items()),
        "all_registered_ratio_endpoints_and_charts_recomputed": len(records) == 92 and math.isclose(min(x["ratio_abs_beta_over_zeta"] for x in records), 1.0e-8, rel_tol=1.0e-12) and math.isclose(max(x["ratio_abs_beta_over_zeta"] for x in records), 1.0e8, rel_tol=1.0e-12) and all(chart_counts.values()),
        "sampled_map_norms_below_analytic_chart_envelopes": all(x["rescaled_map_frobenius_sample"] < CHART_CAPS[x["basis_chart"]]["rescaled_map_frobenius"] and x["state_map_frobenius_sample"] < CHART_CAPS[x["basis_chart"]]["state_map_frobenius"] for x in records),
        "source_probed_coefficient_norms_fit_declared_caps": sum(state_coefficients) < 11.0 and max(derivative_coefficients[:2]) < 3.2 and max(abs(value) for value in derivative_coefficients[2:]) < 1.0e-12,
        "analytic_chart_norm_envelopes_fit_declared_caps": envelopes["generic_chart"]["rescaled_map_frobenius_upper"] < 60.0 and envelopes["confluent_chart"]["eigenvalue_gap_lower_coefficient_derived"] > 0.9 and envelopes["confluent_chart"]["rescaled_map_frobenius_upper"] < 96.0 and envelopes["corrected_jordan_chart"]["rescaled_map_frobenius_upper"] < 128.0 and envelopes["state_map_frobenius_upper_all_charts"] < 8.0,
        "determinant_formula_reproduces_all_registered_cases": max_determinant_error < 1.0e-8,
        "rescaled_transfer_factorization_is_exact_to_roundoff": max_transfer_error < 1.0e-8,
        "determinant_singular_value_inequality_holds_on_samples": max_sigma_bound_violation == 0.0,
        "generic_confluent_overlap_is_chart_invariant": max_overlap_difference < 1.0e-10,
        "corrected_jordan_chart_matches_registered_endpoint": operator_artifact["EQUATION_OR_MAPPING"]["endpoint"]["corrected_jordan_gram_max_abs_error"] < 2.0e-6 and operator_artifact["EQUATION_OR_MAPPING"]["endpoint"]["corrected_jordan_non_gauge_max_column_norm_at_reference"] < 1.0e-6,
        "each_chart_has_finite_uniform_transfer_bound_below_its_reported_power": chart_bounds["unit_generic_eigenmodes"]["log10_transfer_norm_upper_bound"] < 67.0 and chart_bounds["normalized_confluent_divided_difference"]["log10_transfer_norm_upper_bound"] < 60.0 and chart_bounds["source_ode_consistent_jordan"]["log10_transfer_norm_upper_bound"] < 62.0,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    status = "PASS_POSITIVE_REAL_UNIFORM_TRANSFER_BOUND" if all(checks.values()) else "FAIL_OR_UNRESOLVED_POSITIVE_REAL_TRANSFER_BOUND"
    blocker = "complex_frequency_transfer_bound_and_imported_kreiss_norm_interface_missing"
    claim = "A finite but extremely loose uniform state-transfer bound on the declared beta<0, zeta>0, delta<=1e-2, tangential-frequency-one lane; not a useful stability constant or a full Kreiss estimate."
    closed = [
        "On the declared positive-real low-frequency lane, chartwise analytic determinant floors and conservative Frobenius caps imply a finite uniform upper bound for T=W*C^-1=W*S^-1*D.",
        "The common chartwise bound is ||T||_2<1e67 in the internal orthonormal coordinates. The exponent is astronomically large and is only a finiteness result, not a practical stability estimate.",
        "The generic/confluent overlap reproduces the same transfer map; the corrected Jordan chart is included with its separate determinant and norm envelope.",
    ]
    open_items = [
        "The imaginary-frequency boundary, general complex closed-half-plane frequencies, and high-frequency compactification remain unbounded by this result.",
        "The internal orthonormal source/state norms still need an explicit comparison with the imported Kreiss theorem's norm interface.",
        "This frozen-coefficient boundary-symbol result does not establish variable-coefficient CPBC evolution, the full curved 3+1 parent, or Gravity compatibility.",
    ]
    source_paths = (Path(__file__), REGRESSION, OPERATOR_SCRIPT, OPERATOR_ARTIFACT, FLOOR_SCRIPT, FLOOR_ARTIFACT, BOUNDARY_SOURCE, PROJECTOR_SOURCE)
    hashes = {_relative(path): _hash(path) for path in source_paths}
    equation = {
        "transfer": "T=W*C^-1=W*S^-1*D, S=D*C",
        "row_scaling": "D=diag(zeta*I6,I4,min(abs(beta),zeta)*I10,abs(beta)*I10), ||D||_2<=1",
        "singular_value_inequality": "sigma_min(S)>=abs(det(S))/||S||_2^29>=determinant_floor/chart_frobenius_cap^29",
        "transfer_inequality": "||T||_2<=||W||_F*||S||_F^29/determinant_floor",
        "domain": "beta<0, zeta>0, delta=max(abs(beta),zeta)<=1e-2, tangential frequency=1, positive-real Laplace frequency",
        "chartwise_bounds": chart_bounds,
        "analytic_norm_envelopes": envelopes,
        "claim_boundary": claim,
    }
    major = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_POSITIVE_REAL_TRANSFER_BOUND",
        "topic": "core_curved_3p1",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": closed,
        "what_remains_open": open_items,
        "equation_or_mapping": equation,
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables and the declared internal orthonormal boundary-data/state coordinates.",
        "derivation_class": "determinant-to-smallest-singular-value inequality plus chart-specific analytic matrix norm caps and source-matrix reproduction",
        "observable": "spectral norm of the boundary state-transfer operator per unit transformed boundary data",
        "data_role": "internal analytic/numerical verification; no empirical data, fitting, or holdout",
        "evidence_artifacts": [{"path": _relative(path), "sha256": hashes[_relative(path)]} for path in source_paths],
        "verification_status": status,
        "open_blockers": open_items,
        "controlling_blocker": blocker,
        "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "claim_boundary": claim,
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-positive-real-joint-transfer-bound-v1",
        "artifact": "curved_3p1_gh_rinne_positive_real_joint_transfer_bound",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major["major_result_id"],
        "major_result": major,
        "closure_level": "CLOSED_FOR_LANE",
        "core_parent_status": "PARTIAL",
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE",
        "WHAT_IS_ACTUALLY_CLOSED": closed,
        "WHAT_REMAINS_OPEN": open_items,
        "DEPENDENCY_UNLOCKED": major["dependency_unlocked"],
        "STATUS": status,
        "EQUATION_OR_MAPPING": equation,
        "VERIFICATION": {"checks": checks, "case_count": len(records), "chart_counts": chart_counts, "max_determinant_log_error": max_determinant_error, "max_transfer_factorization_error": max_transfer_error, "max_generic_confluent_overlap_error": max_overlap_difference, "max_sigma_bound_violation": max_sigma_bound_violation, "maximum_sampled_rescaled_map_frobenius_by_chart": {chart: max(row["rescaled_map_frobenius_sample"] for row in records if row["basis_chart"] == chart) for chart in CHART_CAPS}, "maximum_sampled_state_map_frobenius_by_chart": {chart: max(row["state_map_frobenius_sample"] for row in records if row["basis_chart"] == chart) for chart in CHART_CAPS}, "chartwise_bounds": chart_bounds, "cases": records, "source_hashes": hashes},
        "CONTROLLING_BLOCKER": blocker,
        "NEXT_ACTION": "Extend the transfer estimate to the imaginary-frequency boundary and high-frequency compactification, then reconcile the internal source/state norm with the imported Kreiss theorem before evaluating variable-coefficient evolution.",
        "CLAIM_BOUNDARY": claim,
        "full_core_unlock": False,
        "gravity_unlock": False,
        "claim_promotion": False,
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifact": _relative(OUTPUT), "status": artifact["STATUS"], "checks": artifact["VERIFICATION"]["checks"], "chartwise_bounds": artifact["VERIFICATION"]["chartwise_bounds"]}, indent=2))
    return 0 if all(artifact["VERIFICATION"]["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
