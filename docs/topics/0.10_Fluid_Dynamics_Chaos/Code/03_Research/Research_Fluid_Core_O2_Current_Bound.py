"""Conditional selected finite-K current finiteness; analytic bounds, no material admission."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT = TOPIC / "Data/03_Research/fluid_core_o2_current_bound_contract.json"
OUTPUT = TOPIC / "Result/artifacts/fluid_core_o2_current_bound_audit.json"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_current_bound_addendum.json"


def load(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative(a, b):
    return float(abs(a - b) / max(abs(a), abs(b), 1e-300))


def lower_constants(a):
    T, K, mu, B, r, c = (a[k] for k in ("T", "K", "mu", "B", "r", "c"))
    if min(T, K, mu, B, r, c, a["g3"]) <= 0 or B != r + 2 * mu * mu or c != float(np.sqrt(r / B)):
        raise ValueError("same positive condensed source parameters required")
    S = np.sqrt(B * B + 4 * mu * mu * K * K)
    R = np.sqrt(r * r + 4 * mu * mu * K * K)
    eta = 8 * mu ** 4 / (S * (B + S) ** 2)
    sigma = 3 * c * eta * K * K / 32
    nu = 12 * a["g3"] * mu * mu * c ** 3 / R
    beta = c * nu ** 2 * T * T * np.exp(-K / T) * K ** 3 / (3072 * np.pi ** 3)
    alpha = beta * sigma
    ell = K / 4
    rho_L = (K / 4) ** 4 / 4
    rho_H = (K ** 4 - (K / 2) ** 4) / 4
    C_P = 1 / ell + 2 * K ** 3 / rho_L + 2 * rho_H / (rho_L * ell)
    D = 4 * mu ** 4 / B ** 3
    wmax = T * T / (6 * np.pi ** 2 * c * c)
    B_upper = wmax ** 2 * D ** 2 * K ** 6 / 2
    if not alpha > 0:
        raise ValueError("floating analytic lower constant underflowed; no numerical certificate")
    return {"eta": float(eta), "sigma": float(sigma), "nu": float(nu), "beta": float(beta),
            "alpha": float(alpha), "C_P": float(C_P), "D": float(D), "wmax": float(wmax),
            "B_upper": float(B_upper), "R_upper": float(2 * C_P * B_upper / alpha),
            "evaluation": "floating analytic formulas; not interval certificates"}


def current_quadrature(g, a, order):
    xs, ws = np.polynomial.legendre.leggauss(order)
    k, dk = a["K"] * (xs + 1) / 2, a["K"] * ws / 2
    E = g.energy(k, a)
    N = 1 / np.expm1(E / a["T"])
    w = k * k * N * (1 + N) / (6 * np.pi ** 2)
    S = np.sqrt(a["B"] ** 2 + 4 * a["mu"] ** 2 * k * k)
    d = 8 * a["mu"] ** 4 * k * k / (a["B"] * S * (S + a["B"]))
    weight = dk * w * k * k
    momentum_G = float(np.sum(weight))
    dbar = float(np.sum(weight * d) / momentum_G)
    J = k * (d - dbar)
    source_G = float(np.sum(dk * w * J * J))
    overlap = float(np.sum(dk * w * k * J))
    raw_overlap = float(np.sum(weight * (a["c"] ** 2 + d)))
    soft = a["K"] * np.asarray([1e-3, 1e-4, 1e-5, 1e-6])
    Eso = g.energy(soft, a)
    Nso = 1 / np.expm1(Eso / a["T"])
    wso = soft * soft * Nso * (1 + Nso) / (6 * np.pi ** 2)
    Sso = np.sqrt(a["B"] ** 2 + 4 * a["mu"] ** 2 * soft * soft)
    dso = 8 * a["mu"] ** 4 * soft * soft / (a["B"] * Sso * (Sso + a["B"]))
    wzero = a["T"] ** 2 / (6 * np.pi ** 2 * a["c"] ** 2)
    soft_errors = [relative(value, wzero ** 2 * dbar ** 2) for value in wso ** 2 * (dso - dbar) ** 2]
    # The exact frame is the integral definition, not this finite Gauss sum.
    return {"order": order, "dbar": dbar, "momentum_G": momentum_G, "source_G": source_G,
            "B_J": float(np.sum(dk * w * w * J * J / k)),
            "source_frame_error": abs(overlap) / np.sqrt(momentum_G * source_G),
            "unprojected_momentum_overlap": raw_overlap,
            "unprojected_source_bound_possible": False,
            "soft_dual_integrand_over_k_limit_errors": soft_errors,
            "source_identity_error": float(np.max(abs(g.energy(k, a) * (
                k / E * (1 - 2 * a["mu"] ** 2 / S)) / k - (a["c"] ** 2 + d)) / (a["c"] ** 2 + d))),
            "frame_role": "quadrature diagnostic of exact integral-defined kinetic frame, not a material frame"}


def patch_events(g, continuum, infrared, a, parents, daughters, constants):
    records = []
    for parent in parents:
        k = parent * a["K"]
        p = a["K"] * np.asarray(daughters)
        if np.any(p <= 0) or np.any(p >= k) or np.any(k - p < a["K"] / 4 * (1 - 1e-14)):
            raise ValueError("patch must retain k-p>=K/4 and interior daughters")
        Ek, Ep = float(g.energy(k, a)), g.energy(p, a)
        q = g.inverse_energy(Ek - Ep, a)
        Eq = g.energy(q, a)
        factors, P, Q, repairs = infrared.stable_geometry(k, p, q, a)
        Kvec = np.array([0., 0., k])
        V = a["g3"] * (6 * Ek * Ep * Eq - 2 * (Ek * np.einsum("ij,ij->i", P, Q)
                  + Ep * (Q @ Kvec) + Eq * (P @ Kvec)))
        vq = continuum.velocity(q, Eq, a)
        nk, npop, nq = (1 / np.expm1(e / a["T"]) for e in (Ek, Ep, Eq))
        W = k * p * q * V ** 2 * nk * (1 + npop) * (1 + nq) / (192 * np.pi ** 3 * Ek * Ep * Eq * vq)
        cos = np.einsum("ij,ij->i", P, Q) / (p * q)
        sin2 = np.linalg.norm(np.cross(P, Q), axis=1) ** 2 / (p * p * q * q)
        angular_ratios = []
        for left, right in ((1., -1.), (1., 2.), (0., 1.)):
            actual = np.linalg.norm(left * P + right * Q, axis=1) ** 2
            lower = sin2 * (left * left * p * p + right * right * q * q) / 2
            angular_ratios.append(float(np.min(actual / lower)))
        records.append({"parent_over_K": parent, "event_count": len(p), "precision_gap_events": repairs,
            "minimum_triangle_factor": float(np.min(factors)),
            "energy_error": float(np.max(abs(Ek - Ep - Eq) / Ek)),
            "geometry_error": max(float(np.max(abs(np.linalg.norm(P, axis=1) - p) / p)),
                                  float(np.max(abs(np.linalg.norm(Q, axis=1) - q) / q))),
            "raw_momentum_collision_error": float(np.max(np.linalg.norm(Kvec - P - Q, axis=1) / k)),
            "minimum_sin2_over_sigma": float(np.min(sin2 / constants["sigma"])),
            "minimum_vertex_over_lower": float(np.min(abs(V) / (constants["nu"] * k * p * q))),
            "minimum_W_over_beta_p": float(np.min(W / (constants["beta"] * p))),
            "minimum_W_sin2_over_alpha_p": float(np.min(W * sin2 / (constants["alpha"] * p))),
            "minimum_angular_bound_ratio": min(angular_ratios),
            "angular_eigenvalue_bound_error": float(np.max(np.maximum(0, sin2 / 2 - (1 - abs(cos))))),
            "minimum_q_over_K": float(np.min(q / a["K"])),
            "source_event_normalization": "same192pi^3 denominator, including original identical daughters and angular1/3"})
    return records


def exact_gap_identity(c):
    k, p = c.poly_variable(0), c.poly_variable(1)
    add, mul, scale = c.poly_add, c.poly_mul, c.poly_scale
    q = add(k, scale(p, -1))
    terms = add(mul(p, add(mul(k, k), scale(mul(p, p), -1))),
                mul(q, add(mul(k, k), scale(mul(q, q), -1))))
    rhs = scale(mul(mul(k, p), q), 3)
    difference = add(terms, scale(rhs, -1))
    negative = add(terms, scale(mul(mul(k, p), q), -2))
    return {"arithmetic": "exact rational sparse polynomials", "difference_monomial_count": len(difference),
            "wrong_factor_negative_control_monomial_count": len(negative),
            "identity": not difference, "negative_control_detected": bool(negative)}


def audit(p, path):
    rules = p["verification"]
    checks, rows, errors = {}, [], []
    def flag(name, value):
        checks[name] = {"pass": bool(value)}
    def close(name, metric, tolerance):
        checks[name] = {"metric": float(metric), "threshold": tolerance,
                        "pass": bool(np.isfinite(metric) and metric <= tolerance)}
    def positive(name, metric):
        checks[name] = {"metric": float(metric), "pass": bool(np.isfinite(metric) and metric > 0)}
    flag("scope", p["record_role"] == "CONDITIONAL_SELECTED_FINITE_CUTOFF_CURRENT_UPPER_BOUND_INTERNAL")
    flag("locked_states", p["mu"] == 1.28 and p["lambda_exploratory"] == .01 and p["temperatures"] == [.002, .004])
    controls = {"locked_before_first_execution": True, "cutoff_factor": 60,
        "patch1_parent_over_K": [.5, .625, .75, .875, 1.],
        "patch1_daughter_over_K": [1e-6, .001, .05, .125, .249999],
        "patch2_parent_over_K": [.75, .875, 1.], "patch2_daughter_over_K": [.25, .375, .5],
        "current_orders": [64, 128, 256], "energy_scale": 2,
        "algebra_relative_tolerance": 1e-8, "event_relative_tolerance": 1e-9,
        "refinement_relative_tolerance": .01, "max_cutoff_energy_over_radial_gap": .1}
    flag("locked_controls_and_targets", all(rules.get(k) == v for k, v in controls.items()))
    required = {"formal_verification", "external_math_review", "interval_certification", "useful_relative_error_certificate",
        "strong_Hilbert_inverse", "unbounded_momentum_domain", "all_channel_interacting_domain", "physical_heat_current",
        "physical_relaxation_time", "physical_frequency_window", "physical_UET_operator", "physical_HeII_state",
        "physical_J04_executed", "physical_J05_executed", "physical_J06_executed", "claim_promotion", "dependency_unlock"}
    flag("admission_fields", set(p["admission"]) == required)
    for name in sorted(required):
        flag("boundary/" + name, p["admission"].get(name) is False)
    card = ROOT / p["card"]
    flag("preregistered_card", hashlib.sha256(card.read_bytes()).hexdigest() ==
         "5fccaf6def52afaf8d4c2615f1fb255507d542bdeab50687a59956748f79db2f")
    flag("preregistered_registry", hashlib.sha256(REGISTRY.read_bytes()).hexdigest() ==
         "e467f7e0a225429c1f833a42b81d67e1c0db9dc0f1347f556282fe9e5ddab5d8")
    prior = json.loads((ROOT / p["continuum_artifact"]).read_text(encoding="utf-8"))
    flag("prior_sources_fresh", all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == value
                                  for name, value in prior["input_hashes"].items()))
    flag("prior_conditional_domain_and_no_gap", prior["status"] == "PASS_CONDITIONAL_CONTINUUM_FORM_DIAGNOSTIC_ONLY"
         and prior["selected_finite_cutoff_domain_internal_derivation_supported"]
         and prior["no_uniform_vector_gap_internal_derivation_supported"] and not prior["physical_heat_current_matched"])
    def finish():
        paths = [path, card, REGISTRY, Path(__file__).resolve(), ROOT / p["continuum_contract"],
                 ROOT / p["continuum_verifier"], ROOT / p["continuum_artifact"]] + [ROOT / n for n in prior["input_hashes"]]
        hashes = {f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else f.name:
                  hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
        passed = len(rows) == 2 and all(c["pass"] for c in checks.values()) and not errors
        return {"schema_version": "t010-core-o2-current-bound-audit-v1", "date": p["date"],
            "status": "PASS_CONDITIONAL_SELECTED_CURRENT_BOUND_ONLY" if passed else "SELECTED_CURRENT_BOUND_DIAGNOSTIC_FAIL",
            "check_count": len(checks), "passing_check_count": sum(c["pass"] for c in checks.values()),
            "checks": checks, "input_hashes": hashes, "locked_verification": rules, "state_results": rows,
            "execution_errors": errors, "unit_powers": {"eta": -2, "sigma": 0, "nu": -2, "beta": 1, "alpha": 1,
                "C_P": -1, "D": -2, "wmax": 2, "B_upper": 6, "R_upper": 4, "B_J": 6, "source_G": 5},
            "selected_current_finiteness_internal_derivation_supported": bool(passed),
            "selected_current_upper_bound_internal_derivation_supported": bool(passed),
            "continuum_current_upper_bound_established": False, "useful_relative_error_certified": False,
            "formal_verification": False, "external_math_review": False, "interval_certified": False,
            "full_continuum_inverse_executed": False, "strong_Hilbert_inverse_established": False,
            "positive_uniform_vector_gap_admitted": False, "current_response_divergence_established": False,
            "physical_heat_current_matched": False, "physical_UET_operator_admitted": False,
            "physical_HeII_state_assigned": False, "physical_relaxation_time": None, "physical_frequency_window": None,
            "physical_J04_executed": False, "physical_J05_executed": False, "physical_J06_executed": False,
            "whole_Core_runtime_executed": False, "live_Phi_executed": False,
            "claim_promotion": False, "dependency_unlock": False, "thresholds_relaxed": False, "parameters_fitted": False,
            "physical_controller": p["physical_controller"], "controlling_measured_blocker": p["candidate_controller"],
            "notes": ["Analytic patch constants are not sampled minima; diagnostics do not replace the card proof.",
                "Finite conservative current ratio bound is not a useful relative-error certificate or strong Hilbert inverse.",
                "Exact integral frame is distinct from finite Gauss projection and from microscopic material heat current.",
                "No formal, independent, interval, infinite-cutoff/all-channel or physical admission."]}
    if not all(c["pass"] for c in checks.values()):
        return finish()
    c = load(ROOT / p["continuum_verifier"], "current_bound_continuum")
    ic = json.loads((ROOT / p["continuum_contract"]).read_text(encoding="utf-8"))
    ir = json.loads((ROOT / ic["infrared_contract"]).read_text(encoding="utf-8"))
    vc = json.loads((ROOT / ir["vector_contract"]).read_text(encoding="utf-8"))
    gc = json.loads((ROOT / vc["galerkin_contract"]).read_text(encoding="utf-8"))
    cc = json.loads((ROOT / gc["core_source_contract"]).read_text(encoding="utf-8"))["configuration"]
    m2, lam = cc["mass_squared"] / cc["Z"], p["lambda_exploratory"] / cc["Z"] ** 2
    g = load(ROOT / vc["galerkin_verifier"], "current_bound_galerkin")
    ir_module = load(ROOT / ic["infrared_verifier"], "current_bound_infrared")
    identity = exact_gap_identity(c)
    flag("exact_gap_polynomial_identity", identity["identity"])
    flag("wrong_factor_negative_control", identity["negative_control_detected"])
    try:
        for T in p["temperatures"]:
            a = c.parameters(T, p["mu"], m2, lam, rules["cutoff_factor"])
            bound = lower_constants(a)
            key = str(T)
            close(key + "/cutoff_energy", float(g.energy(a["K"], a) / np.sqrt(2 * a["B"])), rules["max_cutoff_energy_over_radial_gap"])
            for name in ("eta", "sigma", "nu", "beta", "alpha", "C_P", "D", "B_upper", "R_upper"):
                positive(key + "/constant/" + name, bound[name])
            events = []
            for patch in (1, 2):
                records = patch_events(g, c, ir_module, a, rules[f"patch{patch}_parent_over_K"], rules[f"patch{patch}_daughter_over_K"], bound)
                for index, e in enumerate(records):
                    prefix = key + "/patch" + str(patch) + "/" + str(index)
                    positive(prefix + "/triangle", e["minimum_triangle_factor"])
                    for name in ("energy_error", "geometry_error", "raw_momentum_collision_error"):
                        close(prefix + "/" + name, e[name], rules["event_relative_tolerance"])
                    for name in ("minimum_sin2_over_sigma", "minimum_vertex_over_lower", "minimum_W_over_beta_p",
                                 "minimum_W_sin2_over_alpha_p", "minimum_angular_bound_ratio"):
                        close(prefix + "/" + name, 1 - e[name], rules["algebra_relative_tolerance"])
                    close(prefix + "/angular_eigenvalue", e["angular_eigenvalue_bound_error"], rules["algebra_relative_tolerance"])
                    close(prefix + "/q_patch", .25 - e["minimum_q_over_K"], rules["algebra_relative_tolerance"])
                    events.append({"patch": patch, **e})
            sweep = [current_quadrature(g, a, n) for n in rules["current_orders"]]
            for v in sweep:
                prefix = key + "/current/" + str(v["order"])
                close(prefix + "/frame", v["source_frame_error"], rules["algebra_relative_tolerance"])
                close(prefix + "/identity", v["source_identity_error"], rules["algebra_relative_tolerance"])
                positive(prefix + "/unprojected_null_obstruction", v["unprojected_momentum_overlap"])
                positive(prefix + "/source_dual_norm", v["B_J"])
                close(prefix + "/dual_upper", v["B_J"] / bound["B_upper"] - 1, rules["algebra_relative_tolerance"])
                close(prefix + "/soft_dual_integrand_O_k", v["soft_dual_integrand_over_k_limit_errors"][-1], rules["refinement_relative_tolerance"])
                flag(prefix + "/frame_in_analytic_range", 0 < v["dbar"] < bound["D"] * a["K"] ** 2)
            for name in ("dbar", "B_J", "source_G", "momentum_G"):
                close(key + "/refinement/" + name, relative(sweep[-1][name], sweep[-2][name]), rules["refinement_relative_tolerance"])
            rows.append({"T": T, "parameters": a, "analytic_constants": bound, "patch_events": events,
                         "current_sweep": sweep, "exact_gap_polynomial_identity": identity,
                         "useful_relative_error_certificate": False})
        a = rows[-1]["parameters"]
        scale = rules["energy_scale"]
        scaled = c.parameters(a["T"] * scale, a["mu"] * scale, m2 * scale ** 2, lam, rules["cutoff_factor"])
        other = lower_constants(scaled)
        for name, power in (("eta", -2), ("sigma", 0), ("nu", -2), ("beta", 1), ("alpha", 1),
                            ("C_P", -1), ("D", -2), ("wmax", 2), ("B_upper", 6), ("R_upper", 4)):
            close("scale/" + name, relative(other[name], rows[-1]["analytic_constants"][name] * scale ** power), rules["algebra_relative_tolerance"])
        q = current_quadrature(g, scaled, rules["current_orders"][-1])
        for name, power in (("dbar", 0), ("momentum_G", 5), ("source_G", 5), ("B_J", 6), ("unprojected_momentum_overlap", 5)):
            close("scale/current/" + name, relative(q[name], rows[-1]["current_sweep"][-1][name] * scale ** power), rules["algebra_relative_tolerance"])
    except (ValueError, FloatingPointError) as exc:
        errors.append({"type": type(exc).__name__, "message": str(exc)})
        flag("all_requested_controls_executed", False)
    flag("complete_states", len(rows) == 2)
    return finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-json", type=Path, default=CONTRACT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    path = args.contract_json.resolve()
    result = audit(json.loads(path.read_text(encoding="utf-8")), path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(result["status"], result["passing_check_count"], "/", result["check_count"], flush=True)
    for row in result["state_results"]:
        print("T", row["T"], "conditional conservative R_upper", row["analytic_constants"]["R_upper"], flush=True)
    failed = [(k, v) for k, v in result["checks"].items() if not v["pass"]]
    if failed:
        print("FAIL", failed, flush=True)
    return 0 if result["status"] == "PASS_CONDITIONAL_SELECTED_CURRENT_BOUND_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
