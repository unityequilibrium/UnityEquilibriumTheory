"""Selected finite-K form-domain/soft noncoercivity derivation diagnostics; no physical admission."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT = TOPIC / "Data/03_Research/fluid_core_o2_continuum_form_contract.json"
OUTPUT = TOPIC / "Result/artifacts/fluid_core_o2_continuum_form_audit.json"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_continuum_form_addendum.json"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative(a, b):
    return float(abs(a - b) / max(abs(a), abs(b), 1e-300))


# Exact sparse polynomial operations. Variables are Ep, Eq, k^2, p^2, q^2;
# all coefficients are rational, so cancellation is not a float tolerance.
def poly_add(*polynomials):
    result = {}
    for polynomial in polynomials:
        for monomial, coefficient in polynomial.items():
            result[monomial] = result.get(monomial, Fraction(0)) + coefficient
    return {m: c for m, c in result.items() if c}


def poly_scale(polynomial, coefficient):
    return {m: c * Fraction(coefficient) for m, c in polynomial.items() if c * coefficient}


def poly_mul(a, b):
    result = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            monomial = tuple(x + y for x, y in zip(ma, mb))
            result[monomial] = result.get(monomial, Fraction(0)) + ca * cb
    return {m: c for m, c in result.items() if c}


def poly_variable(index):
    monomial = [0] * 5
    monomial[index] = 1
    return {tuple(monomial): Fraction(1)}


def cubic_identity():
    ep, eq, kk, pp, qq = [poly_variable(i) for i in range(5)]
    ek = poly_add(ep, eq)
    pdotq = poly_scale(poly_add(kk, poly_scale(pp, -1), poly_scale(qq, -1)), Fraction(1, 2))
    kdotq = poly_scale(poly_add(kk, qq, poly_scale(pp, -1)), Fraction(1, 2))
    kdotp = poly_scale(poly_add(kk, pp, poly_scale(qq, -1)), Fraction(1, 2))
    pressure = poly_add(poly_mul(ek, pdotq), poly_mul(ep, kdotq), poly_mul(eq, kdotp))
    original = poly_add(poly_scale(poly_mul(poly_mul(ek, ep), eq), 6), poly_scale(pressure, -2))
    # E*(k^2-E^2) = F(E) on the exact inverse lower branch.
    fk = poly_mul(ek, poly_add(kk, poly_scale(poly_mul(ek, ek), -1)))
    fp = poly_mul(ep, poly_add(pp, poly_scale(poly_mul(ep, ep), -1)))
    fq = poly_mul(eq, poly_add(qq, poly_scale(poly_mul(eq, eq), -1)))
    rewritten = poly_scale(poly_add(fk, poly_scale(fp, -1), poly_scale(fq, -1)), -2)
    difference = poly_add(original, poly_scale(rewritten, -1))
    missing_pressure = poly_add(difference, poly_scale(poly_mul(ek, pdotq), 2))
    dimensions = [1, 1, 2, 2, 2]
    return {
        "variables": ["Ep", "Eq", "k_squared", "p_squared", "q_squared"],
        "arithmetic": "fractions.Fraction, exact rational polynomial coefficients",
        "difference_monomial_count": len(difference),
        "missing_parent_pressure_negative_control_monomial_count": len(missing_pressure),
        "original_all_monomial_energy_powers": sorted({sum(a * b for a, b in zip(m, dimensions)) for m in original}),
        "rewritten_all_monomial_energy_powers": sorted({sum(a * b for a, b in zip(m, dimensions)) for m in rewritten}),
        "identity": not difference,
        "negative_control_detected": bool(missing_pressure),
        "full_continuum_proof_formalized": False,
    }


def parameters(T, mu, m2, lam, factor):
    r = mu * mu - m2
    B = r + 2 * mu * mu
    if min(T, mu, r, lam, factor) <= 0:
        raise ValueError("positive condensed finite-cutoff parameters required")
    c = float(np.sqrt(r / B))
    return {"T": T, "mu": mu, "m2": m2, "r": r, "B": B,
            "g3": mu * np.sqrt(lam) / B ** 1.5, "c": c, "K": factor * T / c}


def velocity(k, E, a):
    return k / E * (1 - 2 * a["mu"] ** 2 / np.sqrt(a["B"] ** 2 + 4 * a["mu"] ** 2 * k * k))


def F_energy(E, a):
    # Rationalization removes subtraction of two nearly equal positive roots.
    return 4 * a["mu"] ** 2 * E ** 3 / (np.sqrt(a["r"] ** 2 + 4 * a["mu"] ** 2 * E * E) + a["r"])


def measure_bounds(a, epsilon):
    T, c, K = a["T"], a["c"], a["K"]
    if not 0 < epsilon <= K:
        raise ValueError("diagnostic support epsilon must lie in (0,K]")
    h = T / c
    prefactor = 3 * a["g3"] ** 2 * T / (4 * np.pi ** 3 * c ** 5)

    def U(x):
        return x ** 7 / 7 + h * x ** 6 / 3 + h * h * x ** 5 / 5

    H = K ** 5 / 5 + h * K ** 4 / 2 + h * h * K ** 3 / 3
    total = prefactor * U(K) / 2

    def soft_sets(s):
        return prefactor * U(s) / 2, prefactor * s * s * H / 2, prefactor * s * s * H / (2 * c * c)

    wmax = T * T / (6 * np.pi ** 2 * c * c)
    s = float(np.sqrt(epsilon * K))
    ik, ip, iq = soft_sets(s)
    smooth_G = wmax * T * T * (s + epsilon ** 4 / (12 * s ** 3))
    smooth_Q = 3 * T * T * (ik + ip + iq) + 9 * T * T * epsilon ** 4 * total / (4 * s ** 4)
    ik, ip, iq = soft_sets(epsilon)
    M = T
    psi_min = np.exp(-9 / 5) / 3
    bump_Q = 3 * M * M * (ik + ip + iq)
    bump_G_lower = M * M * psi_min ** 2 * epsilon * T * T * np.exp(-2 * epsilon / T) / (18 * np.pi ** 2)
    L = min(K, T / 2)
    momentum_G_lower = T * T * np.exp(-2 * L / T) * L ** 3 / (18 * np.pi ** 2)
    projection_loss_upper = wmax ** 2 * M * M * epsilon ** 4 / (4 * momentum_G_lower)
    projected_G_lower = bump_G_lower - projection_loss_upper
    return {
        "epsilon": epsilon, "split_s": s, "w_density_upper": wmax,
        "event_density_prefactor": prefactor, "event_integral_upper": total,
        "smooth_G_upper": smooth_G, "smooth_Q_upper": smooth_Q,
        "bump_Q_upper": bump_Q, "bump_G_lower": bump_G_lower,
        "momentum_G_lower": momentum_G_lower, "projection_loss_upper": projection_loss_upper,
        "projected_G_lower": projected_G_lower,
        "rayleigh_upper": bump_Q / projected_G_lower if projected_G_lower > 0 else None,
        "physical_relaxation_time": None, "current_response_upper_bound": None,
        "evaluation": "floating evaluation of derived inequalities, not interval certification",
    }


def bump_gram(g, a, epsilon, order):
    xs, ws = np.polynomial.legendre.leggauss(order)
    k = .5 * epsilon * (xs + 1)
    dk = .5 * epsilon * ws
    x = k / epsilon
    psi = x * np.exp(-1 / (1 - x * x))
    A = a["T"] * psi
    E = g.energy(k, a)
    N = 1 / np.expm1(E / a["T"])
    w = k * k * N * (1 + N) / (6 * np.pi ** 2)
    gram = float(np.sum(dk * w * A * A))
    overlap = float(np.sum(dk * w * A * k))
    parent = .5 * a["K"] * (xs + 1)
    dp = .5 * a["K"] * ws
    Ep = g.energy(parent, a)
    npop = 1 / np.expm1(Ep / a["T"])
    Gmomentum = float(np.sum(dp * parent ** 4 * npop * (1 + npop) / (6 * np.pi ** 2)))
    projected = gram - overlap * overlap / Gmomentum
    return {"order": order, "G": gram, "momentum_overlap": overlap,
            "momentum_G": Gmomentum, "projected_G": projected}


def event_diagnostics(g, infrared, a, parent, fractions):
    p = parent * np.asarray(fractions)
    Ek = float(g.energy(parent, a))
    Ep = g.energy(p, a)
    q = g.inverse_energy(Ek - Ep, a)
    Eq = g.energy(q, a)
    factors, P, Q, repairs = infrared.stable_geometry(parent, p, q, a)
    Kvector = np.array([0., 0., parent])
    cubic = a["g3"] * (6 * Ek * Ep * Eq - 2 * (
        Ek * np.einsum("ij,ij->i", P, Q) + Ep * (Q @ Kvector) + Eq * (P @ Kvector)))
    rewritten = -2 * a["g3"] * (F_energy(Ek, a) - F_energy(Ep, a) - F_energy(Eq, a))
    vg = velocity(q, Eq, a)
    nk = 1 / np.expm1(Ek / a["T"])
    npop = 1 / np.expm1(Ep / a["T"])
    qpop = 1 / np.expm1(Eq / a["T"])
    # Density per dk dp, rather than the old Gauss weights per dk d(fraction).
    W = parent ** 2 / (2 * np.pi ** 2) * p * q / (Ep * Eq * vg) * cubic ** 2 / (
        32 * np.pi * Ek * parent) * nk * (1 + npop) * (1 + qpop) / 3
    prefactor = 3 * a["g3"] ** 2 * a["T"] / (4 * np.pi ** 3 * a["c"] ** 5)
    h = a["T"] / a["c"]
    tight_majorant = prefactor * parent * p * q * (p + h) * (q + h)
    coarse_majorant = prefactor * parent ** 2 * p * (parent + h) ** 2
    points = np.r_[parent, p, q]
    energies = g.energy(points, a)
    speeds = velocity(points, energies, a)
    return {
        "parent": parent, "event_count": len(p), "high_precision_gap_events": repairs,
        "minimum_triangle_factor": float(np.min(factors)),
        "source_B_r_mu_relative_error": relative(a["B"], a["r"] + 2 * a["mu"] ** 2),
        "energy_error": float(np.max(abs(Ek - Ep - Eq) / Ek)),
        "geometry_error": max(float(np.max(abs(np.linalg.norm(P, axis=1) - p) / p)),
                              float(np.max(abs(np.linalg.norm(Q, axis=1) - q) / q))),
        "vertex_identity_error": float(np.max(abs(cubic - rewritten) / np.maximum(abs(cubic), abs(rewritten)))),
        "strict_vertex_positive_bracket": bool(np.all(rewritten < 0)),
        "minimum_event_density": float(np.min(W)),
        "maximum_vertex_to_majorant_ratio": float(np.max(abs(cubic) / (12 * abs(a["g3"]) * parent * p * q))),
        "maximum_W_to_tight_majorant_ratio": float(np.max(W / tight_majorant)),
        "maximum_tight_to_coarse_majorant_ratio": float(np.max(tight_majorant / coarse_majorant)),
        "minimum_phase_over_c": float(np.min(energies / points / a["c"])),
        "maximum_phase_velocity": float(np.max(energies / points)),
        "minimum_speed_over_c": float(np.min(speeds / a["c"])),
        "maximum_speed_times_c": float(np.max(speeds * a["c"])),
        "W_first_daughter": float(W[0]), "vertex_first_daughter": float(cubic[0]),
    }


def audit(p, path):
    rules = p["verification"]
    checks, rows, events, errors = {}, [], [], []
    algebra = cubic_identity()

    def flag(name, value):
        checks[name] = {"pass": bool(value)}

    def close(name, value, tolerance):
        checks[name] = {"metric": float(value), "threshold": tolerance,
                        "pass": bool(np.isfinite(value) and value <= tolerance)}

    def positive(name, value):
        checks[name] = {"metric": float(value), "pass": bool(np.isfinite(value) and value > 0)}

    flag("scope", p["record_role"] == "CONDITIONAL_FINITE_CUTOFF_FORM_DOMAIN_AND_NO_UNIFORM_VECTOR_GAP_INTERNAL")
    flag("locked_states", p["mu"] == 1.28 and p["lambda_exploratory"] == .01 and p["temperatures"] == [.002, .004])
    flag("locked_controls", rules["locked_before_first_execution"] is True and
         rules["cutoff_factor"] == 60 and rules["bump_deltas"] == [.001, .0005, .00025, .000125] and
         rules["smooth_deltas"] == [.1, .03, .01, .003] and rules["Gram_orders"] == [64, 128, 256] and
         rules["parent_over_thermal_k"] == [.0001, .01, .1, 1, 10, 60] and
         rules["daughter_fractions"] == [.000001, .01, .25, .5, .75, .99, .999999] and
         rules["energy_scale"] == 2)
    flag("locked_targets", rules["algebra_relative_tolerance"] == 1e-8 and
         rules["event_relative_tolerance"] == 1e-9 and rules["refinement_relative_tolerance"] == .01 and
         rules["max_cutoff_energy_over_radial_gap"] == .1)
    required = {"unbounded_momentum_domain", "all_channel_interacting_domain",
                "source_weighted_current_upper_bound", "formal_verification", "external_math_review",
                "physical_heat_current", "physical_relaxation_time", "physical_frequency_window",
                "physical_UET_operator", "physical_HeII_state", "physical_J04_executed",
                "physical_J05_executed", "physical_J06_executed", "claim_promotion", "dependency_unlock"}
    flag("admission_fields", set(p["admission"]) == required)
    for key in sorted(required):
        flag("boundary/" + key, p["admission"].get(key) is False)
    flag("exact_rational_cubic_identity", algebra["identity"])
    flag("missing_pressure_negative_control", algebra["negative_control_detected"])
    flag("exact_polynomial_unit_closure", algebra["original_all_monomial_energy_powers"] == [3] and
         algebra["rewritten_all_monomial_energy_powers"] == [3])

    prior = json.loads((ROOT / p["infrared_artifact"]).read_text(encoding="utf-8"))
    flag("immutable_prior_source_hashes", all(
        hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == value
        for name, value in prior["input_hashes"].items()))
    flag("prior_finite_targets_pass_without_continuum_admission",
         prior["refinement_gate"]["target_pass"] is True and
         prior["continuum_collision_form_domain_established"] is False and
         prior["continuum_current_upper_bound_established"] is False)
    infrared_contract = json.loads((ROOT / p["infrared_contract"]).read_text(encoding="utf-8"))
    flag("same_kernel_and_states", p["mu"] == infrared_contract["mu"] and
         p["lambda_exploratory"] == infrared_contract["lambda_exploratory"] and
         p["temperatures"] == infrared_contract["temperatures"])

    def finish():
        paths = [path, ROOT / p["card"], REGISTRY, Path(__file__).resolve(),
                 ROOT / p["infrared_contract"], ROOT / p["infrared_verifier"], ROOT / p["infrared_artifact"]]
        paths += [ROOT / name for name in prior["input_hashes"]]
        hashes = {f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else f.name:
                  hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
        passed = bool(rows) and all(c["pass"] for c in checks.values()) and not errors
        return {
            "schema_version": "t010-core-o2-continuum-form-audit-v1", "date": p["date"],
            "status": "PASS_CONDITIONAL_CONTINUUM_FORM_DIAGNOSTIC_ONLY" if passed else "CONTINUUM_FORM_DIAGNOSTIC_FAIL",
            "check_count": len(checks), "passing_check_count": sum(c["pass"] for c in checks.values()),
            "checks": checks, "input_hashes": hashes, "locked_verification": rules,
            "exact_cubic_polynomial_identity": algebra, "pointwise_event_diagnostics": events,
            "state_results": rows, "execution_errors": errors,
            "derivation_scope": {
                "status": "CONDITIONAL_INTERNAL_DERIVATION_SUPPORTED" if passed else "DIAGNOSTIC_OR_SCOPE_FAILURE",
                "selected_finite_cutoff": True, "bounded_trial_majorant": "Q<=9*M^2*I_total<infinity",
                "closed_dense_domain": "maximal radial Delta-pullback domain; card a.e. subsequence argument",
                "smooth_approximation": "explicit G and Q upper bounds with s=sqrt(epsilon*K)",
                "radial_vector_nullspace": "momentum only via W>0 and noncollinear triangles",
                "uniform_vector_gap": "inf on momentum-perp Q/G=0 by compact soft bumps; conditional internal",
                "proof_policy": rules["proof_policy"],
                "formal_verification": False, "independent_math_review": False,
                "interval_certified": False, "full_continuum_inverse_executed": False,
            },
            "unit_powers": {"w_density": 2, "W_density": 2, "W_prefactor": -3, "event_integral": 4,
                            "G": 5, "Q": 6, "Rayleigh": 1, "vertex": 1},
            "selected_finite_cutoff_domain_internal_derivation_supported": passed,
            "no_uniform_vector_gap_internal_derivation_supported": passed,
            "candidate_controller": p["candidate_controller"], "physical_controller": p["physical_controller"],
            "controlling_measured_blocker": p["candidate_controller"] if passed else p["previous_measured_controller"],
            "previous_package": {"artifact": p["infrared_artifact"], "sha256": hashes[p["infrared_artifact"]],
                                 "status": prior["status"], "refinement_gate": prior["refinement_gate"]},
            "continuum_current_upper_bound_established": False, "current_response_divergence_established": False,
            "unbounded_K_domain_established": False, "full_interacting_collision_completed": False,
            "positive_uniform_vector_gap_admitted": False, "physical_relaxation_time": None,
            "physical_frequency_window": None, "physical_heat_current_matched": False,
            "physical_UET_operator_admitted": False, "physical_HeII_state_assigned": False,
            "physical_J04_executed": False, "physical_J05_executed": False, "physical_J06_executed": False,
            "whole_Core_runtime_executed": False, "live_Phi_executed": False,
            "formal_verification": False, "external_math_review": False,
            "claim_promotion": False, "dependency_unlock": False, "thresholds_relaxed": False, "parameters_fitted": False,
            "notes": ["Sampled inequalities support source/unit diagnostics; the continuum statements rely on the explicit card derivation.",
                      "A momentum-only nullspace does not imply a uniform positive spectral gap.",
                      "No uniform gap alone does not imply divergent source-current response or absence of every source-specific hydrodynamic window.",
                      "epsilon changes a smooth trial support, never the collision kernel or cutoff.",
                      "Numerical bounds are floating evaluations, not interval-certified constants or measured transport coefficients.",
                      "No all-channel, infinite-cutoff, interacting-state, material/SI or Core dependency admission."],
        }

    if not all(c["pass"] for c in checks.values()):
        return finish()
    source = json.loads((ROOT / infrared_contract["vector_contract"]).read_text(encoding="utf-8"))
    gal = json.loads((ROOT / source["galerkin_contract"]).read_text(encoding="utf-8"))
    core = json.loads((ROOT / gal["core_source_contract"]).read_text(encoding="utf-8"))
    cfg = core["configuration"]
    m2 = cfg["mass_squared"] / cfg["Z"]
    lam = p["lambda_exploratory"] / cfg["Z"] ** 2
    g = load(ROOT / source["galerkin_verifier"], "continuum_source_galerkin")
    infrared = load(ROOT / p["infrared_verifier"], "continuum_source_infrared")
    tol = rules["algebra_relative_tolerance"]
    try:
        for T in p["temperatures"]:
            a = parameters(T, p["mu"], m2, lam, rules["cutoff_factor"])
            label = str(T)
            close(label + "/cutoff_energy", float(g.energy(a["K"], a) / np.sqrt(2 * a["B"])),
                  rules["max_cutoff_energy_over_radial_gap"])
            for multiplier in rules["parent_over_thermal_k"]:
                e = event_diagnostics(g, infrared, a, multiplier * T / a["c"], rules["daughter_fractions"])
                events.append({"T": T, "parent_over_thermal_k": multiplier, **e})
                key = label + "/event/" + str(multiplier)
                positive(key + "/noncollinear_triangle", e["minimum_triangle_factor"])
                positive(key + "/W_positive", e["minimum_event_density"])
                flag(key + "/nonzero_vertex_bracket", e["strict_vertex_positive_bracket"])
                close(key + "/energy", e["energy_error"], rules["event_relative_tolerance"])
                close(key + "/geometry", e["geometry_error"], rules["event_relative_tolerance"])
                close(key + "/vertex_identity", e["vertex_identity_error"], tol)
                close(key + "/source_parameters", e["source_B_r_mu_relative_error"], 128 * np.finfo(float).eps)
                for metric in ("maximum_vertex_to_majorant_ratio", "maximum_W_to_tight_majorant_ratio",
                               "maximum_tight_to_coarse_majorant_ratio", "maximum_phase_velocity",
                               "maximum_speed_times_c"):
                    close(key + "/" + metric, e[metric] - 1, tol)
                for metric in ("minimum_phase_over_c", "minimum_speed_over_c"):
                    close(key + "/" + metric, 1 - e[metric], tol)
            smooth = [measure_bounds(a, d * T / a["c"]) for d in rules["smooth_deltas"]]
            for name in ("smooth_G_upper", "smooth_Q_upper"):
                values = [r[name] for r in smooth]
                flag(label + "/" + name + "_decreasing", all(x > y > 0 for x, y in zip(values, values[1:])))
            bump = []
            for delta in rules["bump_deltas"]:
                bound = measure_bounds(a, delta * T / a["c"])
                sweep = [bump_gram(g, a, bound["epsilon"], order) for order in rules["Gram_orders"]]
                key = label + "/bump/" + str(delta)
                positive(key + "/projected_G_lower", bound["projected_G_lower"])
                positive(key + "/rayleigh_upper", bound["rayleigh_upper"])
                flag(key + "/actual_Gram_above_lower", sweep[-1]["G"] >= bound["bump_G_lower"])
                flag(key + "/actual_projected_Gram_above_lower", sweep[-1]["projected_G"] >= bound["projected_G_lower"])
                flag(key + "/momentum_Gram_above_lower", sweep[-1]["momentum_G"] >= bound["momentum_G_lower"])
                flag(key + "/projection_loss_below_upper",
                     sweep[-1]["G"] - sweep[-1]["projected_G"] <= bound["projection_loss_upper"])
                for name in ("G", "projected_G", "momentum_G"):
                    close(key + "/refinement/" + name, relative(sweep[-1][name], sweep[-2][name]),
                          rules["refinement_relative_tolerance"])
                bump.append({"delta": delta, "analytic_bounds": bound, "Gram_sweep": sweep})
            flag(label + "/Rayleigh_upper_decreasing",
                 all(x["analytic_bounds"]["rayleigh_upper"] > y["analytic_bounds"]["rayleigh_upper"] > 0
                     for x, y in zip(bump, bump[1:])))
            rows.append({"T": T, "parameters": a, "smooth_bound_sweep": smooth, "bump_countersequence": bump})
        if rows:
            scale = rules["energy_scale"]
            original = rows[-1]
            a = original["parameters"]
            scaled = parameters(a["T"] * scale, a["mu"] * scale, m2 * scale ** 2, lam, rules["cutoff_factor"])
            ref = original["bump_countersequence"][-1]["analytic_bounds"]
            other = measure_bounds(scaled, ref["epsilon"] * scale)
            for name, power in (("w_density_upper", 2), ("event_density_prefactor", -3), ("event_integral_upper", 4),
                                ("smooth_G_upper", 5), ("smooth_Q_upper", 6), ("bump_Q_upper", 6),
                                ("bump_G_lower", 5), ("momentum_G_lower", 5), ("projection_loss_upper", 5),
                                ("projected_G_lower", 5), ("rayleigh_upper", 1)):
                close("scale/" + name, relative(other[name], ref[name] * scale ** power), tol)
            gram = bump_gram(g, scaled, other["epsilon"], rules["Gram_orders"][-1])
            before = original["bump_countersequence"][-1]["Gram_sweep"][-1]
            for name in ("G", "momentum_overlap", "momentum_G", "projected_G"):
                close("scale/actual/" + name, relative(gram[name], before[name] * scale ** 5), tol)
            point = event_diagnostics(g, infrared, a, a["T"] / a["c"], [.25])
            point_scaled = event_diagnostics(g, infrared, scaled, scaled["T"] / scaled["c"], [.25])
            for name, power in (("W_first_daughter", 2), ("vertex_first_daughter", 1)):
                close("scale/event/" + name, relative(point_scaled[name], point[name] * scale ** power), tol)
    except (ValueError, FloatingPointError) as exc:
        errors.append({"type": type(exc).__name__, "message": str(exc)})
        flag("all_requested_controls_executed", False)
    flag("nonempty_complete_states", len(rows) == len(p["temperatures"]) and bool(rows))
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
        print("T", row["T"], "projected Rayleigh upper bounds",
              [v["analytic_bounds"]["rayleigh_upper"] for v in row["bump_countersequence"]], flush=True)
    failed = [(k, v) for k, v in result["checks"].items() if not v["pass"]]
    if failed:
        print("FAIL", failed, flush=True)
    return 0 if result["status"] == "PASS_CONDITIONAL_CONTINUUM_FORM_DIAGNOSTIC_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
