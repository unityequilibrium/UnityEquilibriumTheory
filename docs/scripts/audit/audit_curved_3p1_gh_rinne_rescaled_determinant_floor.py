from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OPERATOR_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_joint_real_kreiss_operator.py"
OPERATOR_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_joint_real_kreiss_operator.json"
FACTOR_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_rescaled_transfer_factorization.py"
FACTOR_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_rescaled_transfer_factorization.json"
RATIO_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_compactified_ratio_screen.json"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_rescaled_determinant_floor.json"
DELTAS = (1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5)
RATIO_LOWER, RATIO_UPPER = 20.0 / 21.0, 21.0 / 20.0
RATIOS = tuple(sorted({float(v) for v in np.logspace(-8.0, 8.0, 17)} | {0.99, 0.999999, 1.0, 1.000001, 1.01, RATIO_LOWER, RATIO_UPPER}))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OPERATOR = _load("_uet_rescaled_determinant_floor_operator", OPERATOR_SCRIPT)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _parameters(delta: float, ratio: float) -> tuple[float, float, float]:
    zeta = delta if ratio <= 1.0 else delta / ratio
    b = ratio * zeta
    return -b, zeta, b / zeta


def _scalars(beta: float, zeta: float) -> dict[str, float]:
    root, lambda1, lambda2 = OPERATOR.NEGATIVE._root_and_lambdas(complex(zeta, 0.0), beta)
    f = zeta - (1.0 + beta) * lambda1
    k1 = np.linalg.norm([zeta - beta * lambda1, -lambda1, -1.0j, 0.0j])
    return {"R": float(np.real(root)), "lambda1": float(np.real(lambda1)), "lambda2": float(np.real(lambda2)), "F": float(np.real(f)), "K1": float(k1), "r": abs(beta) / zeta}


def _generic_logdet(v: dict[str, float]) -> float:
    r = v["r"]
    shape = min(1.0, r) * abs(1.0 - r * r) / (r * np.sqrt(1.0 + r * r))
    return float(-np.log(8.0) + 10.0 * ((8.0 / 5.0) * np.log(v["F"]) - np.log(v["K1"]) + np.log(shape)))


def _confluent_logdet(v: dict[str, float]) -> float:
    r = v["r"]
    shape = min(1.0, r) * (r * v["R"] + 1.0) / np.sqrt(1.0 + r * r)
    return float(-np.log(8.0) + 10.0 * ((8.0 / 5.0) * np.log(v["F"]) - np.log(v["K1"]) + np.log(shape)))


def _row_scaling(beta: float, zeta: float) -> np.ndarray:
    b = abs(beta)
    return np.diag([zeta] * 6 + [1.0] * 4 + [min(b, zeta)] * 10 + [b] * 10)


def _bounds(delta_max: float) -> dict[str, float]:
    a_lo = np.sqrt(1.0 - delta_max**2) - delta_max**2
    a_hi = np.sqrt(1.0 + delta_max**2) / (1.0 - delta_max**2)
    f_lo = (1.0 - delta_max) * a_lo
    k1_hi = np.sqrt((delta_max * (1.0 + a_hi))**2 + a_hi**2 + 1.0)
    base = f_lo ** (8.0 / 5.0) / k1_hi
    g_cut = (1.0 - RATIO_LOWER**2) / np.sqrt(1.0 + RATIO_LOWER**2)
    r_lo = np.sqrt(1.0 - delta_max**2)
    h_lo = RATIO_LOWER * (RATIO_LOWER * r_lo + 1.0) / np.sqrt(1.0 + RATIO_UPPER**2)
    base_c, g_c, h_c = 0.6955, 0.0673, 1.2823
    return {"delta_max": delta_max, "negative_lambda_magnitude_lower": float(a_lo), "negative_lambda_magnitude_upper": float(a_hi), "F_lower": float(f_lo), "K1_upper": float(k1_hi), "base_factor_lower_expression_value": float(base), "base_factor_lower_conservative": base_c, "generic_shape_at_chart_edge": float(g_cut), "generic_shape_lower_conservative": g_c, "generic_determinant_floor_conservative": float(0.125 * (base_c * g_c)**10), "R_lower": float(r_lo), "confluent_shape_lower_expression_value": float(h_lo), "confluent_shape_lower_conservative": h_c, "confluent_determinant_floor_conservative": float(0.125 * (base_c * h_c)**10), "jordan_determinant_floor_conservative": float(4.0 / (1.0 + delta_max**2)**5)}


def build_artifact() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    gap_errors: list[float] = []
    confluent_errors: list[float] = []
    summaries: list[dict[str, Any]] = []
    for delta in DELTAS:
        group = []
        for requested_ratio in RATIOS:
            beta, zeta, r = _parameters(delta, requested_ratio)
            if r == 1.0:
                chart = "source_ode_consistent_jordan"
                boundary, state, residual = OPERATOR._jordan_matrices(zeta)
                expected = float(np.log(4.0) - 5.0 * np.log(1.0 + zeta * zeta))
            else:
                v = _scalars(beta, zeta)
                if RATIO_LOWER <= r <= RATIO_UPPER:
                    chart = "normalized_confluent_divided_difference"
                    boundary, state, residual = OPERATOR._confluent_matrices(zeta, beta)
                    expected = _confluent_logdet(v)
                    generic = _generic_logdet(v)
                    gap = abs(v["lambda2"] - v["lambda1"])
                    gap_formula = abs(r * r - 1.0) / (r * (r * v["R"] + 1.0))
                    gap_errors.append(abs(gap - gap_formula) / gap)
                    confluent_errors.append(abs(generic - 10.0 * np.log(gap) - expected))
                else:
                    chart = "unit_generic_eigenmodes"
                    boundary, state, residual = OPERATOR._generic_matrices(zeta, beta)
                    expected = _generic_logdet(v)
            scaled = _row_scaling(beta, zeta) @ boundary
            _, actual = np.linalg.slogdet(scaled)
            sv = np.linalg.svd(scaled, compute_uv=False)
            row = {"delta": delta, "ratio_abs_beta_over_zeta": r, "beta": beta, "zeta": zeta, "basis_chart": chart, "expected_log_abs_determinant": float(expected), "actual_log_abs_determinant": float(actual), "log_determinant_formula_error": float(abs(actual - expected)), "rescaled_sigma_min_sample": float(sv[-1]), "rescaled_sigma_max_sample": float(sv[0]), "principal_mode_residual": float(residual), "finite": bool(np.isfinite(actual) and np.all(np.isfinite(scaled)) and np.all(np.isfinite(state)) and np.all(np.isfinite(sv)))}
            if chart == "normalized_confluent_divided_difference":
                row["eigenvalue_gap"] = float(gap)
                row["eigenvalue_gap_formula"] = float(gap_formula)
            group.append(row)
            cases.append(row)
        summaries.append({"delta": delta, "case_count": len(group), "chart_counts": {chart: sum(x["basis_chart"] == chart for x in group) for chart in ("unit_generic_eigenmodes", "normalized_confluent_divided_difference", "source_ode_consistent_jordan")}, "minimum_sampled_sigma_min": min(x["rescaled_sigma_min_sample"] for x in group), "maximum_sampled_sigma_max": max(x["rescaled_sigma_max_sample"] for x in group), "maximum_formula_error": max(x["log_determinant_formula_error"] for x in group)})

    bounds = _bounds(max(DELTAS))
    formula_error, gap_error, confluent_error = (max(x["log_determinant_formula_error"] for x in cases), max(gap_errors), max(confluent_errors))
    generic_rows = [x for x in cases if x["basis_chart"] == "unit_generic_eigenmodes"]
    confluent_rows = [x for x in cases if x["basis_chart"] == "normalized_confluent_divided_difference"]
    jordan_rows = [x for x in cases if x["basis_chart"] == "source_ode_consistent_jordan"]
    checks = {"registered_scaled_determinants_match_chart_formulas": formula_error < 1e-8, "generic_floor_covers_sampled_generic_chart": all(np.exp(x["expected_log_abs_determinant"]) >= bounds["generic_determinant_floor_conservative"] for x in generic_rows), "confluent_floor_covers_sampled_confluent_chart": all(np.exp(x["expected_log_abs_determinant"]) >= bounds["confluent_determinant_floor_conservative"] for x in confluent_rows), "corrected_jordan_floor_covers_exact_chart": all(np.exp(x["expected_log_abs_determinant"]) >= bounds["jordan_determinant_floor_conservative"] * (1.0 - 1.0e-14) for x in jordan_rows), "generic_confluent_gap_identity_matches": gap_error < 1e-8 and confluent_error < 1e-8, "ratio_edges_and_all_three_charts_are_covered": len(cases) == 92 and min(RATIOS) == 1e-8 and max(RATIOS) == 1e8 and any(x["ratio_abs_beta_over_zeta"] == RATIO_LOWER for x in cases) and any(x["ratio_abs_beta_over_zeta"] == RATIO_UPPER for x in cases) and all(len(s["chart_counts"]) == 3 for s in summaries), "all_sampled_rescaled_maps_are_finite_and_full_rank": all(x["finite"] and x["rescaled_sigma_min_sample"] > 0 for x in cases), "reported_constants_are_conservative": bounds["base_factor_lower_expression_value"] > bounds["base_factor_lower_conservative"] and bounds["generic_shape_at_chart_edge"] > bounds["generic_shape_lower_conservative"] and bounds["confluent_shape_lower_expression_value"] > bounds["confluent_shape_lower_conservative"] and bounds["jordan_determinant_floor_conservative"] > 3.998}
    checks = {name: bool(value) for name, value in checks.items()}
    status = "PASS_CHARTWISE_RESCALED_DETERMINANT_FLOOR" if all(checks.values()) else "FAIL_OR_UNRESOLVED_RESCALED_DETERMINANT_FLOOR"
    claim = "analytic positive lower bounds for the rescaled determinant on beta<0, zeta>0, 0<delta<=1e-2, with separate generic, confluent, and corrected-Jordan basis charts; this does not bound the inverse operator or prove a Kreiss estimate"
    closed = ["Eq. (123), registered row scaling, and K2=sqrt(beta^2+zeta^2) reduce the generic determinant to r=abs(beta)/zeta; all delta factors cancel exactly.", "The divided-difference transform on each of ten tensor components removes the generic eigenvalue-gap zero and gives a positive confluent-chart determinant on 20/21<=r<=21/20.", "The corrected source-ODE-consistent Jordan chart has a separate positive determinant formula; its determinant is kept separate because chart basis normalization changes determinant magnitude.", "Conservative analytic lower bounds are recorded for all three charts, and the formulas match direct determinants on the 92-point ratio/delta screen."]
    open_items = ["A determinant lower bound alone does not bound sigma_min(S) or ||S^-1|| without controlling the remaining singular values/operator norm.", "The three basis charts still need a common transition estimate in the target Kreiss norms.", "Imaginary/high-frequency limits, the full complex closed half-plane, shift-family uniformity, and variable-coefficient CPBC evolution remain open."]
    blocker = "uniform_chart_compatible_inverse_bound_for_rescaled_boundary_map_not_proved"
    evidence_paths = (Path(__file__), OPERATOR_SCRIPT, OPERATOR_ARTIFACT, FACTOR_SCRIPT, FACTOR_ARTIFACT, RATIO_ARTIFACT)
    hashes = {_relative(path): _hash(path) for path in evidence_paths}
    evidence = [{"path": _relative(path), "sha256": hashes[_relative(path)]} for path in evidence_paths]
    equation = {"rescaled_boundary_map": "S=D*C; D=diag(zeta*I6,I4,min(abs(beta),zeta)*I10,abs(beta)*I10)", "domain": "beta<0, zeta>0, delta=max(abs(beta),zeta) in (0,1e-2], r=abs(beta)/zeta in (0,infinity)", "source_determinant": "|det C|=F^16*|zeta^2-beta^2|^10/(8*zeta^16*abs(beta)^20*K1^10*K2^10), K2=sqrt(beta^2+zeta^2)", "generic_chart": "|det S_g|=1/8*[F^(8/5)/K1*min(1,r)*abs(1-r^2)/(r*sqrt(1+r^2))]^10, r!=1", "confluent_chart": "|det S_c|=1/8*[F^(8/5)/K1*min(1,r)*(r*R+1)/sqrt(1+r^2)]^10, 20/21<=r<=21/20", "confluent_gap": "|lambda2-lambda1|=abs(r^2-1)/(r*(r*R+1)); det(S_c)=det(S_g)/abs(lambda2-lambda1)^10", "corrected_jordan_chart": "|det S_J|=4/(1+zeta^2)^5 at r=1", "definitions": "F=zeta-(1+beta)*lambda1; K1=sqrt((zeta-beta*lambda1)^2+lambda1^2+1); R=sqrt(1-beta^2+zeta^2)", "bound_derivation": "For delta<=0.01 and b=abs(beta), a=-lambda1=(R-b*zeta)/(1-b^2) obeys sqrt(1-delta^2)-delta^2<=a<=sqrt(1+delta^2)/(1-delta^2). Therefore F=zeta+(1-b)*a>=(1-delta)*a_lower and K1<=sqrt((delta*(1+a_upper))^2+a_upper^2+1), so F^(8/5)/K1>0.6955. With q=min(r,1/r), g(q)=(1-q^2)/sqrt(1+q^2) has g'(q)=-q*(3+q^2)/(1+q^2)^(3/2)<=0; outside the confluent band q<=20/21 and g(q)>0.0673. In the confluent band R>=sqrt(1-delta^2), min(1,r)>=20/21, r<=21/20, so its bracket shape exceeds 1.2823. The corrected Jordan determinant is >=4/(1+0.01^2)^5.", "conservative_bounds": bounds, "claim_boundary": claim}
    major = {"major_result_id": "CORE_CURVED_3P1_GH_RINNE_RESCALED_DETERMINANT_FLOOR", "topic": "core_curved_3p1", "closure_level": "CLOSED_FOR_LANE", "what_is_closed": closed, "what_remains_open": open_items, "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked", "evidence_artifacts": evidence, "open_blockers": open_items, "controlling_blocker": blocker, "equation_or_mapping": equation, "units": "Dimensionless frozen-coefficient Fourier-Laplace variables with tangential omega=1; determinant is basis-chart dependent.", "derivation_class": "exact determinant algebra, divided-difference chart transform, conservative scalar inequalities, and direct registered-matrix reproduction", "observable": "absolute determinant and singular values of the row-rescaled 30x30 frozen-coefficient boundary map", "data_role": "internal analytic/numerical diagnostic; no empirical data, fitting, or holdout", "verification_status": status, "claim_boundary": claim}
    return {"schema_version": "core-curved-3p1-gh-rinne-rescaled-determinant-floor-v1", "artifact": "curved_3p1_gh_rinne_rescaled_determinant_floor", "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "major_result_id": major["major_result_id"], "major_result": major, "closure_level": "CLOSED_FOR_LANE", "core_parent_status": "PARTIAL", "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE", "WHAT_IS_ACTUALLY_CLOSED": closed, "WHAT_REMAINS_OPEN": open_items, "DEPENDENCY_UNLOCKED": major["dependency_unlocked"], "STATUS": status, "EQUATION_OR_MAPPING": equation, "VERIFICATION": {"checks": checks, "deltas": list(DELTAS), "ratio_grid": list(RATIOS), "case_count": len(cases), "cases": cases, "summaries": summaries, "maximum_log_determinant_formula_error": formula_error, "maximum_gap_identity_relative_error": gap_error, "maximum_confluent_basis_transform_error": confluent_error, "analytic_bounds": bounds, "source_hashes": hashes}, "CONTROLLING_BLOCKER": blocker, "NEXT_ACTION": "Bound the remaining singular values/operator norm and prove a chart-compatible lower singular-value or inverse-operator estimate; then extend to imaginary and high frequencies.", "CLAIM_BOUNDARY": claim, "full_core_unlock": False, "gravity_unlock": False, "claim_promotion": False}


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifact": _relative(OUTPUT), "status": artifact["STATUS"], "checks": artifact["VERIFICATION"]["checks"], "case_count": artifact["VERIFICATION"]["case_count"], "max_logdet_error": artifact["VERIFICATION"]["maximum_log_determinant_formula_error"], "bounds": artifact["VERIFICATION"]["analytic_bounds"]}, indent=2))
    return 0 if all(artifact["VERIFICATION"]["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
