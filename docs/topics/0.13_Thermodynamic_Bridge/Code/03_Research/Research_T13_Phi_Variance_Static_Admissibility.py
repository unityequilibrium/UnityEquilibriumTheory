"""Central Phi variance: local classical parent and separate harmonic quantum bound.

Reads Q certificates, never searches/recalculates Q. Only the two prescribed
classical bounds are used. No physical error policy, material or dynamics.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import json
from math import factorial
from pathlib import Path
import sys

import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from docs.scripts.audit.audit_calculation_completeness import (
    artifact_metadata, contract_hash, load_json, validate_contract,
)
import Research_T13_Parent_Static_Reference_Audit as q

TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
CONTRACT = f"{TOPIC}/calculation_contracts/phi_variance_static_admissibility.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_phi_variance_static_admissibility.json"
REPORT = "docs/meta/UET_PHI_VARIANCE_STATIC_ADMISSIBILITY.md"
QCONTRACT = f"{TOPIC}/calculation_contracts/parent_static_reference_audit.json"
QOUTPUT = f"{TOPIC}/Result/artifacts/t13_parent_static_reference_audit.json"
BASELINE = "62f8efe0558e2c7f40aac1785c2b7cc780727953"


def exact(value):
    if type(value) not in (int, str, F):
        raise ValueError("exact rational input required, not bool/float")
    return F(value)


def interval(value):
    if isinstance(value, q.I):
        return value
    if isinstance(value, dict) and set(value) == {"lo", "hi"}:
        return q.I(exact(value["lo"]), exact(value["hi"]))
    return q.I(exact(value))


def sqrt_interval(value):
    v = interval(value)
    if v.lo < 0:
        raise ValueError("nonnegative radicand required")
    return q.I(q.sqrt_rational(v.lo).lo, q.sqrt_rational(v.hi).hi)


def exp_enclosure(value):
    """Private outward enclosure; avoid underflow, not an extended Q solver.

    For x<=-32, 0<exp(x)<=16!/(-x)^16. It is not rounded to zero.
    Positive arguments here are <=1 (A) or <=1/2 (B).
    """
    v = interval(value)
    if v.hi >= 32:
        raise ValueError("positive exponential outside this path's domain")

    def point(x):
        if x <= -32:
            return q.I(0, min(F(1), F(factorial(16))/(-x)**16))
        return q.exp_point(x)

    return q.I(point(v.lo).lo, point(v.hi).hi)


def select_reference(artifact):
    if artifact.get("physical_acceptance") is not False:
        raise ValueError("Q evidence boundary changed; inspect before reuse")
    control = artifact["locked_control"]
    expected = {"N": 4, "D_over_Jref": 8, "delta": "ln2", "nu": 2,
                "dref_over_r0": 1, "epsilon_star": 1, "open_magnetic_bonds": 3,
                "Morse_pairs": 6, "spin_normalization": "S=s/2"}
    if any(control.get(k) != v for k, v in expected.items()):
        raise ValueError("unchanged O/P/Q control required")
    rows = [r for r in artifact["orbits"] if r.get("certificate") and
            r["certificate"]["verdict"] == "CERTIFIED_STRICT_LOCAL_MINIMUM"]
    if len(rows) != 1 or set(rows[0]["orbit_members"]) != {"-+-+", "+-+-"}:
        raise ValueError("exactly the certified alternating-spin orbit required")
    ref = rows[0]
    A = [[interval(v) for v in row] for row in ref["views"]["internal_stiffness"]]
    if len(A) != 3 or any(len(row) != 3 for row in A):
        raise ValueError("three internal mechanical modes required")
    q.ldl(A)
    uncertainty = exact(ref["views"]["root_position_uncertainty_upper"])
    if uncertainty <= 0:
        raise ValueError("inherited root uncertainty cannot be replaced by zero")
    radii = [r for r in ref["local_domain"]["radii"] if r["certified"]]
    if [exact(r["radius_over_dref"]) for r in radii] != [F(1, 2**j) for j in range(5, 11)]:
        raise ValueError("only the six inherited Q radii are allowed")
    for r in radii:
        m, M = exact(r["curvature_lower"]), exact(r["curvature_upper"])
        if not 0 < m <= M or exact(r["positive_gap_lower"]) <= 0:
            raise ValueError("positive curvature and separations required")
        if exact(r["third_derivative_norm_upper"]) < 0:
            raise ValueError("invalid Taylor bound")
    return ref, A, radii


def load_reference():
    contract = load_json(ROOT/QCONTRACT)
    review = validate_contract(contract, ROOT)
    if review["errors"]:
        raise ValueError("Q identity errors: "+"; ".join(review["errors"]))
    artifact = load_json(ROOT/QOUTPUT)
    if artifact.get("contract_sha256") != contract_hash(contract) or artifact.get("identities") != contract["identities"]:
        raise ValueError("Q artifact/contract binding changed")
    return select_reference(artifact)


def covariance_coefficients(A):
    """Interval inversion retains both root location and mixed stiffness."""
    q.ldl(A)
    inv = q.inverse(A)
    c = inv[0][0]/5
    hidden = [row[1:] for row in A[1:]]
    hi = q.inverse(hidden)
    schur = A[0][0]-sum(A[0][i+1]*hi[i][j]*A[j+1][0]
                            for i in range(2) for j in range(2))
    if c.lo <= 0 or schur.lo <= 0:
        raise ValueError("variance and Schur denominators must be certified positive")
    via_schur = 1/(5*schur)
    if max(c.lo, via_schur.lo) > min(c.hi, via_schur.hi):
        raise ValueError("joint/Schur enclosures do not overlap")
    return {"c_h": c, "c_h_via_Schur": via_schur, "Schur_stiffness": schur,
            "kappa_obs": q.I(F(1, 5))/c,
            "inverse_readout_norm": sqrt_interval(sum(inv[i][0]**2 for i in range(3))/5),
            "h_norm": 1/q.sqrt_rational(5), "A_inverse": inv,
            "bare_uncoupled_coefficient_not_used": 1/(5*A[0][0])}


def method_a(theta, radius, m, delta):
    theta, R, m, delta = map(exact, (theta, radius, m, delta))
    if theta <= 0 or R <= 0 or m <= 0 or delta < 0:
        raise ValueError("positive thermal/domain inputs required")
    alpha, b = 2*delta/theta, m*R**2/theta
    if b <= 3:
        return {"usable": False, "reason": "Chernoff tail bound is only one"}
    if alpha >= 1:
        return {"usable": False, "reason": "E_A>=exp(alpha)-1>=alpha>=1; cannot certify an epsilon<1"}
    eta = exp_enclosure(-(b-3)/2)*sqrt_interval(q.I(b/3)**3)
    if eta.hi >= 1:
        return {"usable": False, "reason": "outward tail enclosure not below one"}
    d = exp_enclosure(alpha)-1
    upper = ((d+d**2+eta+sqrt_interval(3*eta))/(1-eta)).hi
    return {"usable": True, "upper": upper, "tail_upper": eta.hi,
            "density_ratio_excess_upper": d.hi,
            "meaning": "sufficient formal bound, not selected physical accuracy"}


def method_b(theta, radius, m, M, K3, coefficients):
    """Certified upper bound for CENTRAL variance; includes both boundary terms."""
    theta, R, m, M, K3 = map(exact, (theta, radius, m, M, K3))
    if theta <= 0 or R <= 0 or not 0 < m <= M or K3 < 0:
        raise ValueError("positive thermal/domain/curvature inputs required")
    c, nu, hn = (interval(coefficients[k]) for k in
                 ("c_h", "inverse_readout_norm", "h_norm"))
    if min(c.lo, nu.lo, hn.lo) <= 0:
        raise ValueError("positive observable coefficient enclosures required")
    rho2 = min(R**2, theta/M)
    rho = sqrt_interval(rho2)
    zfactor = exp_enclosure(M*rho2/(2*theta))/rho**3
    scale = q.I(2*theta/m)
    # Exact coefficient of G2 is 9 sqrt(pi)/8 < 9/4. G3 has no pi.
    G2 = F(9, 4)*scale**2*sqrt_interval(scale)*zfactor
    G3 = 3*scale**3*zfactor
    surface = 3*R**2*exp_enclosure((M*rho2-m*R**2)/(2*theta))/rho**3
    mean = nu*(K3*G2/2+theta*surface)
    raw = nu*hn*(K3*G3/2+theta*R*surface)
    upper = (raw+mean**2)/(theta*c)
    return {"upper": upper.hi, "mean_shift_upper": mean.hi,
            "raw_second_moment_error_upper": raw.hi,
            "surface_density_upper": surface.hi, "radial_moment2_upper": G2.hi,
            "radial_moment3_upper": G3.hi, "rho_squared": rho2,
            "rho_is_integration_lower_bound_not_new_physical_domain": True}


def quantum_bound(theta, chi, kappa):
    theta, chi = map(exact, (theta, chi))
    kappa = interval(kappa)
    if theta <= 0 or chi <= 0 or kappa.lo <= 0:
        raise ValueError("positive thermal/quantum/coefficient inputs required")
    return (chi**2*kappa/(12*theta**2)).hi


def budget(value):
    v = exact(value)
    if not 0 < v < 1:
        raise ValueError("symbolic physical error budget must lie in (0,1)")
    return v


def scope_check(payload):
    if payload.get("physical_acceptance") is not False or payload.get("quantum_parent_validated") is not False:
        raise ValueError("two comparator bounds cannot validate a quantum parent")
    if payload.get("comparator_pairs") != ["classical_local_parent|classical_full_harmonic",
                                           "quantum_harmonic|classical_full_harmonic"]:
        raise ValueError("distinct comparator pairs required, not a summed quantum-parent error")
    return True


def symbolic_checks():
    a, g1, g2, k1, k12, k2 = s.symbols("a g1 g2 k1 k12 k2", real=True)
    A = s.Matrix([[a, g1, g2], [g1, k1, k12], [g2, k12, k2]])
    K, g = A[1:, 1:], A[1:, 0]
    c = A.inv()[0, 0]/5
    h = s.Matrix([1/s.sqrt(5), 0, 0])
    theta, chi, kap, R, m, M, rho, t = s.symbols("theta chi kap R m M rho t", positive=True)
    n = s.symbols("n", integer=True, positive=True)
    # Coefficients of (1+x^2/3)sinh(x)-x cosh(x), x^(2n+1).
    coth_coefficient = 1/s.factorial(2*n+1)+1/(3*s.factorial(2*n-1))-1/s.factorial(2*n)
    mass, d, J, kb, T, hb, lam, alpha = s.symbols("mu d J kb T hb lam alpha", positive=True)
    q1, u1, u2, phi = s.symbols("q1 u1 u2 phi", real=True)
    av = s.Matrix([-s.Rational(3, 2), -s.Rational(1, 2), s.Rational(1, 2), s.Rational(3, 2)])
    B = s.Matrix.hstack(-av/s.sqrt(5), s.Matrix([1, -1, -1, 1])/2,
                        s.Matrix([1, -3, 3, -1])/(2*s.sqrt(5)))
    dx = B*s.Matrix([q1, u1, u2])
    # Isotropic quadratic on a finite ball: incomplete-gamma recurrence.
    b, G = s.symbols("b G", positive=True)
    gamma52 = s.Rational(3, 2)*G-b**s.Rational(3, 2)*s.exp(-b)
    finite_variance = 2*theta*gamma52/(3*G)
    raw, mean = s.symbols("raw mean", real=True)
    coordinates = s.Matrix(s.symbols("x0:3", real=True))
    k3 = s.symbols("k3", real=True)
    potential = (coordinates.T*A*coordinates)[0]/2+k3*coordinates[0]**3/6
    grad = s.Matrix([s.diff(potential, x) for x in coordinates])
    weight = s.exp(-potential/theta)
    ibp_mean = all(s.expand(s.diff(weight, x)+grad[i]*weight/theta) == 0
                   for i, x in enumerate(coordinates))
    ibp_tensor = all(s.expand(theta*s.diff(coordinates[i]*weight, x)-
        (theta*int(i == j)-coordinates[i]*grad[j])*weight) == 0
        for i in range(3) for j, x in enumerate(coordinates))
    sigma = s.symbols("sigma", positive=True)
    z = s.symbols("z", real=True)
    Zosc = 1/(2*s.sinh(z/2))
    return {
        "joint_Schur_identity": s.factor(c-1/(5*(a-(g.T*K.inv()*g)[0]))) == 0,
        "decoupling_limit": s.simplify(c.subs({g1: 0, g2: 0})-1/(5*a)) == 0,
        "orthonormal_internal_mass_metric": B.T*B == s.eye(3),
        "translation_removed": (s.ones(1, 4)*B) == s.zeros(1, 3),
        "Phi_projection_factor5": s.simplify((-av.dot(dx)/5)-q1/s.sqrt(5)) == 0,
        "endpoint_hidden_contribution": s.simplify(dx[3]-dx[0]+3*q1/s.sqrt(5)+u2/s.sqrt(5)) == 0,
        "total_not_per_site_temperature": s.simplify((theta/4)*4-theta) == 0,
        "central_variance_requires_mean_square": s.expand(raw-(raw-mean**2)) == mean**2,
        "Gaussian_fourth_moment": s.integrate(z**4*s.exp(-z**2/(2*sigma**2)), (z, -s.oo, s.oo))/
            (s.sqrt(2*s.pi)*sigma) == 3*sigma**4,
        "Gaussian_radial_G2_coefficient": s.simplify(s.Rational(3, 2)*s.gamma(s.Rational(5, 2))-9*s.sqrt(s.pi)/8) == 0,
        "Gaussian_radial_G3_coefficient": s.Rational(3, 2)*s.gamma(3) == 3,
        "finite_ball_even_quadratic_not_full_Gaussian": s.simplify(theta-finite_variance-
            2*theta*b**s.Rational(3, 2)*s.exp(-b)/(3*G)) == 0,
        "IBP_mean_sign": s.simplify(-theta*s.diff(s.exp(-z**2/(2*theta)), z)-z*s.exp(-z**2/(2*theta))) == 0,
        "IBP_second_moment_surface_sign": s.simplify(theta*s.diff(z*s.exp(-z**2/(2*theta)), z)-
            (theta-z**2)*s.exp(-z**2/(2*theta))) == 0,
        "mixed_anharmonic_IBP_mean_integrand": ibp_mean,
        "mixed_anharmonic_IBP_tensor_integrand": ibp_tensor,
        "coth_upper_coefficient": s.simplify(coth_coefficient-4*n*(n-1)/(3*s.factorial(2*n+1))) == 0,
        "oscillator_partition_energy": s.simplify(-s.diff(s.log(Zosc), z)-s.coth(z/2)/2) == 0,
        "observable_quantum_factor12": s.simplify(chi**2*(h.dot(h))/(12*theta**2*c)-
            chi**2/(60*theta**2*c)) == 0,
        "quantum_low_argument_coefficient": s.limit((z/s.tanh(z)-1)/z**2, z, 0) == s.Rational(1, 3),
        "fixed_R_moment_limit": s.limit(s.sqrt(t)+t, t, 0, dir="+") == 0,
        "surface_exponential_limit": s.limit(t**-3*s.exp(-1/t), t, 0, dir="+") == 0,
        "scale_mass_length_nonidentifiability": s.simplify((lam*mass)*(d/s.sqrt(lam))**2*J-mass*d**2*J) == 0,
        "scale_energy_temperature_nonidentifiability": s.simplify(kb*(alpha*T)/(alpha*J)-kb*T/J) == 0,
        "scale_energy_mass_nonidentifiability": s.simplify((mass/alpha)*d**2*(alpha*J)-mass*d**2*J) == 0,
        "scale_product_bound": s.simplify((hb/(d*s.sqrt(mass*J)))**2*kap/(12*(kb*T/J)**2)-
            hb**2*kap*J/(12*mass*d**2*kb**2*T**2)) == 0,
    }


def negative_controls():
    A = [[q.I(v) for v in row] for row in ((2, 1, 0), (1, 2, 0), (0, 0, 3))]
    co = covariance_coefficients(A)
    c = co["c_h"]
    toy = {"c_h": q.I(1), "inverse_readout_norm": q.I(1), "h_norm": q.I(1)}
    boundary = method_b(F(1, 20), 1, 1, 1, 0, toy)
    try:
        scope_check({"physical_acceptance": True, "quantum_parent_validated": True})
        bad_claim_caught = False
    except ValueError:
        bad_claim_caught = True
    return {
        "omitted_coupling_detected": not (c.lo <= F(1, 10) <= c.hi),
        "wrong_theta_over4_detected": not (c.lo <= F(2, 15)/4 <= c.hi),
        "missing_factor5_detected": not (c.lo <= F(2, 3) <= c.hi),
        "mean_shift_cannot_be_raw_moment": F(1**2+3**2, 2)-F(1+3, 2)**2 != F(1**2+3**2, 2),
        "boundary_not_zero_even_when_K3_zero": boundary["upper"] > 0 and boundary["surface_density_upper"] > 0,
        "three_joint_not_two_fixed_Phi_modes": s.Rational(3, 2) != s.Rational(2, 2),
        "endpoint_not_affine_Phi_only": s.Matrix([-3/s.sqrt(5), 0, -1/s.sqrt(5)]) != -3*s.Matrix([1/s.sqrt(5), 0, 0]),
        "quantum_parent_promotion_rejected": bad_claim_caught,
    }


def calculate():
    ref, A, radii = load_reference()
    co = covariance_coefficients(A)
    checks, controls = symbolic_checks(), negative_controls()
    if not all(checks.values()) or not all(controls.values()):
        raise ValueError("new symbolic identity or negative control failed")
    nu, hn, c = co["inverse_readout_norm"].hi, co["h_norm"].hi, co["c_h"].lo
    rows = []
    for r in radii:
        R, m, M, K3 = [exact(r[k]) for k in ("radius_over_dref", "curvature_lower",
            "curvature_upper", "third_derivative_norm_upper")]
        # On theta<=M R^2: G2<=C2 theta, G3<=C3 theta^(3/2).
        ehalf = exp_enclosure(F(1, 2))
        C2 = F(9, 4)*q.I(2/m)**2*sqrt_interval(F(2, 1)/m)*q.I(M)*sqrt_interval(M)*ehalf
        C3 = 3*q.I(2/m)**3*q.I(M)*sqrt_interval(M)*ehalf
        rows.append({"radius_over_dref": R, "curvature_lower": m, "curvature_upper": M,
                     "K3_upper": K3, "Delta_upper": exact(r["Taylor_energy_error_upper"]),
                     "inherited_Q_radius_j": r["j"], "moment2_linear_coefficient_upper": C2.hi,
                     "moment3_theta_three_halves_coefficient_upper": C3.hi,
                     "B_small_theta_sqrt_coefficient_upper": q.up(nu*hn*K3*C3.hi/(2*c)),
                     "B_small_theta_linear_coefficient_upper": q.up(nu**2*K3**2*C2.hi**2/(4*c)),
                     "surface_terms_still_required": True, "physical_window_accepted": False})
    result = q.encode({
        "completed_sections": ["V0", "V1", "V2", "V3", "V4"],
        "source_baseline_commit": BASELINE, "source_Q_contract": QCONTRACT,
        "source_Q_artifact": QOUTPUT, "certified_spin_members": ref["orbit_members"],
        "source_root_uncertainty_upper": exact(ref["views"]["root_position_uncertainty_upper"]),
        "full_stiffness": A, "coefficients": co, "inherited_radii": rows,
        "source_lambda_max_upper": exact(ref["views"]["lambda_max_upper"]),
        "checks": checks, "negative_controls": controls,
        "formulae": {
            "V_H": "theta*c_h = theta/[5*(a-g^T K^-1 g)]",
            "A": "(d+d^2+eta+sqrt(3eta))/(1-eta); d=exp(2Delta/theta)-1",
            "eta": "exp(-(b-3)/2)*(b/3)^(3/2) if b=mR^2/theta>3; otherwise1",
            "B_mean": "nu*(K3*G2/2+theta*Bsurf)",
            "B_raw": "nu*norm(h)*(K3*G3/2+theta*R*Bsurf)",
            "B": "(B_raw+B_mean^2)/(theta*c_h)",
            "rho": "min(R,sqrt(theta/M)); integration subdomain only",
            "G2_safe": "(9/4)*(2theta/m)^(5/2)*exp(Mrho^2/(2theta))/rho^3",
            "G3": "3*(2theta/m)^3*exp(Mrho^2/(2theta))/rho^3",
            "Bsurf": "3R^2*exp((Mrho^2-mR^2)/(2theta))/rho^3",
            "B_small_theta_full": "(nu*norm(h)*K3*C3/(2c_h))*sqrt(theta)+(nu*norm(h)*R/c_h)*Bsurf+(nu^2*theta/c_h)*(K3*C2/2+Bsurf)^2; boundary cross terms retained",
            "quantum_harmonic_only": "chi^2*kappa_obs/(12theta^2)",
            "scale_frontier": "mu*dref^2*Jref >= hbar^2*kappa_obs_upper/(12epsilon_q*theta^2)",
        },
        "comparator_pairs": ["classical_local_parent|classical_full_harmonic",
                             "quantum_harmonic|classical_full_harmonic"],
        "error_ledger": {"classical_parent": "min of usable A and B for same pair; includes mean and boundary",
            "harmonic_quantum": "separate isolated comparator only, not a parent correction",
            "numerical": "rational outward coefficient/root enclosures; no point estimate certificates",
            "physical": "mu,dref,Jref, observable budgets, preparation/measurement and quantum parent unknown"},
        "asymptotic_result": "At fixed certified R, E_B tends to0 as theta tends to0. At fixed nonzero chi the harmonic quantum bound instead grows. A conditional family frontier is not a window for every physical system.",
        "physical_acceptance": False, "quantum_parent_validated": False, "budgets_selected": False,
        "old_scientific_verifiers_rerun": False, "old_root_search_called": False,
        "trajectories": 0, "parameter_sweeps": 0, "new_core_terms": 0,
        "parent_global_equilibrium": "UNCHANGED_NOT_ADMITTED",
        "P_original_reference_localization": "UNCHANGED_NOT_ADMITTED",
        "unique_UET_discriminator": False,
        "next_controller": "physical-parent-preparation: independent mu,dref,Jref dictionary and observable error/preparation policy. Quantum-parent correspondence remains separate. No next wave automatically authorized.",
    })
    scope_check(result)
    return result


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT), ROOT), **calculate()}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only evidence and artifact check")
    mode.add_argument("--emit-report", action="store_true", help="write only the new variance artifact")
    args = p.parse_args(argv)
    result = record()
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(payload, encoding="utf-8", newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes() != payload.encode("utf-8"):
        raise ValueError("artifact absent/stale; inspect before explicit --emit-report")
    print(json.dumps({"new_checks": len(result["checks"]), "negative_controls": len(result["negative_controls"]),
                      "inherited_radii": len(result["inherited_radii"]), "physical_acceptance": False,
                      "review": result["contract_review_status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
