"""Static conditional state-counting reference; NOT a new Core Hamiltonian.

Exact algebra and finite enumeration accompany the analytic proofs in the report.
No kinetics, bath elimination, trajectories, measured data or parameter fitting.
Only --emit-report writes the named compact artifact; --check is read-only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import product
import json
from math import comb
from pathlib import Path
import sys

import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata, load_json

TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
CONTRACT = f"{TOPIC}/calculation_contracts/joint_state_measure_construction.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_joint_state_measure_construction.json"
REPORT = "docs/meta/UET_JOINT_STATE_MEASURE_CONSTRUCTION.md"
REGRESSION_N = (2, 3, 4, 8)


def validate_population(N, k=None):
    """Finite population, never a continuous C on all of R."""
    if type(N) is not int or N < 2:
        raise ValueError("N must be an integer >= 2")
    if k is not None and (type(k) is not int or not 0 <= k <= N):
        raise ValueError("k must be an integer in [0,N]")


def multiplicity(N, k):
    validate_population(N, k)
    return s.Integer(comb(N, k))


def magnetization(N, k):
    validate_population(N, k)
    return s.Rational(2*k-N, N)


def reference():
    N = s.Symbol("N", integer=True, positive=True)  # analytic domain additionally N >= 2
    k = s.Symbol("k", integer=True, nonnegative=True)  # k <= N is a constraint
    m, C, Phi, P, Pi = s.symbols("m C Phi P Pi", real=True)
    E, kB, T, sc, j0, tau, MP, bP = s.symbols(
        "E_star k_B T s_C j_0 tau M_Phi b_Phi", positive=True)
    gamma, aP = s.symbols("gamma a_Phi", nonnegative=True)
    mass, theta = tau/MP, kB*T/E
    vP = aP*Phi**2/2+bP*Phi**4/4
    bare = -(j0+gamma*Phi)*m**2/2+vP
    H = E*(N*bare+P**2/(2*N*mass))
    G = s.binomial(N, k)
    F = H-kB*T*s.log(G)
    return dict(N=N, k=k, m=m, C=C, Phi=Phi, P=P, Pi=Pi, E=E, kB=kB, T=T,
                sc=sc, j0=j0, tau=tau, MP=MP, bP=bP, gamma=gamma, aP=aP,
                mass=mass, theta=theta, vP=vP, bare=bare, H=H, G=G, F=F)


def energy_for_count(N, k, r=None):
    validate_population(N, k)
    r = reference() if r is None else r
    return r["H"].subs({r["N"]: N, r["m"]: magnetization(N, k)})


def _zeros(values):
    for name, value in values.items():
        if s.simplify(value) != 0:
            raise ValueError(f"exact identity failed: {name}: {value}")
    return {name: True for name in values}


def thermodynamic_residuals(free_energy=None):
    r = reference()
    F = r["F"] if free_energy is None else free_energy
    H, T, kB, G = r["H"], r["T"], r["kB"], r["G"]
    Sint = -s.diff(F, T)  # fixed retained coordinates, coefficients and measure
    beta = s.Symbol("beta", positive=True)
    Fbeta = F.subs(T, 1/(kB*beta))
    return {
        "intrinsic_entropy_from_T_derivative": Sint-kB*s.log(G),
        "internal_energy_from_F_plus_TS": F+T*Sint-H,
        "beta_derivative_internal_energy": s.diff(beta*Fbeta, beta)-H,
        "restricted_log_partition": -F/(kB*T)-(s.log(G)-H/(kB*T)),
        "interaction_once": s.diff(H, r["gamma"])+r["E"]*r["N"]*r["Phi"]*r["m"]**2/2,
    }


def entropy_residuals():
    q, G, kB = s.symbols("q G k_B", positive=True)
    p_micro = q/G
    chain = -G*p_micro*s.log(p_micro)+q*s.log(q)-q*s.log(G)
    r = reference()
    Z = s.Symbol("Z", positive=True)
    logq = -r["F"]/(r["kB"]*r["T"])-s.log(Z)
    ensemble_density = q*r["F"]+r["kB"]*r["T"]*q*logq
    return {
        "uniform_conditional_normalization": G/G-1,
        "micro_retained_intrinsic_entropy_density": s.expand_log(kB*chain, force=True),
        "ensemble_free_energy_density_at_Gibbs":
            ensemble_density+r["kB"]*r["T"]*q*s.log(Z),
    }


def normalization_residuals(energy=None, jacobian=None):
    r = reference()
    H = r["H"] if energy is None else energy
    N, mass, Pi, P = r["N"], r["mass"], r["Pi"], r["P"]
    Pmap = N*mass*Pi
    J = s.diff(Pmap, Pi) if jacobian is None else jacobian
    per_site = H.subs(P, Pmap)/(N*r["E"])
    Fpi = (H-r["kB"]*r["T"]*s.log(r["G"])).subs(P, Pmap)
    fref = r["bare"]+mass*Pi**2/2-r["theta"]*s.log(r["G"])/N
    return {
        "total_to_per_site_storage": per_site-r["bare"]-mass*Pi**2/2,
        "coarse_free_energy_per_site": Fpi/(N*r["E"])-fref,
        "theta_over_N_in_Gibbs_exponent": Fpi/(r["kB"]*r["T"])-fref/(r["theta"]/N),
        "P_to_Pi_pushforward_measure": J-N*mass,
        "inverse_coordinate_mapping": Pmap.subs(Pi, P/(N*mass))-P,
    }


def quartic_bridge_residuals():
    """Reuse old coefficient map; check its NEW thermal split, not old fixtures."""
    r = reference()
    C, sc, th, T = r["C"], r["sc"], r["theta"], r["T"]
    aC, bC, g = (th-r["j0"])/sc**2, th/(3*sc**4), r["gamma"]/sc**2
    omega4 = aC*C**2/2+bC*C**4/4+r["vP"]-g*C**2*r["Phi"]/2
    f4 = omega4-th*s.log(2)+r["mass"]*r["Pi"]**2/2
    Hpi = r["H"].subs({r["P"]: r["N"]*r["mass"]*r["Pi"], r["m"]: C/sc})
    F4 = r["N"]*r["E"]*f4
    Sint4 = -s.diff(F4, T)
    target_entropy = r["N"]*r["kB"]*(s.log(2)-C**2/(2*sc**2)-C**4/(12*sc**4))
    return {
        "old_coefficient_map_in_fixed_C_coordinates":
            omega4.subs(C, sc*r["m"])-r["vP"]
            -(th-r["j0"]-r["gamma"]*r["Phi"])*r["m"]**2/2-th*r["m"]**4/12,
        "quartic_intrinsic_entropy_keeps_ln2": Sint4-target_entropy,
        "quartic_U_uses_thermal_coefficients_not_frozen_values": F4+T*Sint4-Hpi,
        "coupling_temperature_derivative_zero_in_this_reference": s.diff(g, T),
    }


def finite_population_checks(N):
    """Exact independent configuration enumeration, not a trajectory/sample."""
    validate_population(N)
    counts = Counter(sum(x == 1 for x in spins) for spins in product((-1, 1), repeat=N))
    weights = s.symbols(f"w0:{N+1}")
    micro_sum = sum(weights[sum(x == 1 for x in spins)] for spins in product((-1, 1), repeat=N))
    coarse_sum = sum(multiplicity(N, k)*weights[k] for k in range(N+1))
    if s.expand(micro_sum-coarse_sum) != 0:
        raise ValueError("micro/coarse weighted sum differs")
    if any(counts[k] != multiplicity(N, k) for k in range(N+1)):
        raise ValueError("multiplicity differs from configuration enumeration")
    for k in range(N+1):
        q = s.Rational(k, N)
        # Endpoint convention x^0=1; no evaluation of log(0) is needed.
        Bk = multiplicity(N, k)*q**k*(1-q)**(N-k)
        B = [multiplicity(N, ell)*q**ell*(1-q)**(N-ell) for ell in range(N+1)]
        if sum(B) != 1 or Bk != max(B) or not s.Rational(1, N+1) <= Bk <= 1:
            raise ValueError("finite-N mode/bound certificate fails")
    return {"N": N, "configurations": 2**N, "coarse_classes": N+1,
            "enumerated_multiplicity_and_weight_sum": True,
            "exact_rational_entropy_bound_certificate": True}


def finite_bound_residuals():
    N, k, ell = s.symbols("N k ell", integer=True, nonnegative=True)
    Bk, h, G = s.symbols("B_k h G", positive=True)
    difference = (N-ell)*k-(ell+1)*(N-k)
    return {
        "neighbor_mode_ratio_numerator": difference-(N*(k-ell-1)+k),
        "last_increasing_neighbor": difference.subs(ell, k-1)-k,
        "first_decreasing_neighbor": difference.subs(ell, k)-(k-N),
        "log_bound_conversion": h-s.log(G)/N-(-s.log(Bk)/N)
            .subs(s.log(Bk), s.log(G)-N*h),
    }


def tail_bound_residuals():
    # t=|Phi|, b>0, a=(gamma/b)^(1/3)>=0. The factorization proves Young's bound.
    t, a = s.symbols("t a", nonnegative=True)
    return {"coercive_quartic_linear_factorization":
            t**4-4*a**3*t+3*a**4-(t-a)**2*(t**2+2*a*t+3*a**2)}


def pair_convention_residuals():
    r = reference()
    pair_sum = (r["N"]**2*r["m"]**2-r["N"])/2
    off_diagonal = -r["E"]*(r["j0"]+r["gamma"]*r["Phi"])*pair_sum/r["N"]
    diagonal = -r["E"]*(r["j0"]+r["gamma"]*r["Phi"])/2
    binary_energy = -r["E"]*r["N"]*(r["j0"]+r["gamma"]*r["Phi"])*r["m"]**2/2
    return {"square_of_sum_equals_pairs_plus_diagonal": binary_energy-off_diagonal-diagonal,
            "diagonal_is_not_Phi_constant": s.diff(diagonal, r["Phi"])+r["E"]*r["gamma"]/2}


def folded_groups(N):
    validate_population(N)
    groups = {}
    for k in range(N+1):
        groups.setdefault(abs(2*k-N), []).append(k)
    return groups


def folded_multiplicity(N, magnitude):
    groups = folded_groups(N)
    if type(magnitude) is not int or magnitude not in groups:
        raise ValueError("magnitude must be an admitted |2k-N| grid value")
    return sum(multiplicity(N, k) for k in groups[magnitude])


def folding_checks(N):
    r = reference()
    groups = folded_groups(N)
    for magnitude, ks in groups.items():
        if len(ks) not in (1, 2):
            raise ValueError("incorrect fold")
        if any(s.simplify(energy_for_count(N, k, r)-energy_for_count(N, ks[0], r)) != 0 for k in ks):
            raise ValueError("energy is not even under sign folding")
        expected = multiplicity(N, ks[0])*(1 if magnitude == 0 else 2)
        if folded_multiplicity(N, magnitude) != expected:
            raise ValueError("folded multiplicity incorrect")
    if sum(folded_multiplicity(N, a) for a in groups) != 2**N:
        raise ValueError("fold does not preserve total states")
    return {"N": N, "magnitude_classes": len(groups), "counts_and_even_energy": True}


def folding_entropy_residuals():
    q, G, kB = s.symbols("q G k_B", positive=True)
    # Each signed class has probability q and conditional multiplicity G at equilibrium.
    signed_ret = -2*q*s.log(q)
    folded_ret = -2*q*s.log(2*q)
    signed_int, folded_int = 2*q*s.log(G), 2*q*s.log(2*G)
    return {"lost_sign_entropy_moves_into_intrinsic_for_uniform_fold":
            s.expand_log(kB*(signed_ret+signed_int-folded_ret-folded_int), force=True)}


def decoupling_residuals():
    r = reference()
    spin = -r["E"]*r["N"]*r["j0"]*r["m"]**2/2
    response = r["E"]*(r["N"]*r["vP"]+r["P"]**2/(2*r["N"]*r["mass"]))
    return {
        "gamma_zero_energy_factorizes": r["H"].subs(r["gamma"], 0)-spin-response,
        "gamma_zero_intrinsic_multiplicity_is_spin_only": s.diff(r["G"], r["Phi"]),
        "signed_energy_even": r["H"].subs(r["m"], -r["m"])-r["H"],
    }


def negative_controls():
    r = reference()
    H, F, kBT = r["H"], r["F"], r["kB"]*r["T"]
    wrong_H = H+r["E"]*r["P"]**2/(2*r["mass"])*(1-1/r["N"])
    checks = {
        "omitted_multiplicity": thermodynamic_residuals(H)["intrinsic_entropy_from_T_derivative"],
        "double_multiplicity": thermodynamic_residuals(F-kBT*s.log(r["G"]))["intrinsic_entropy_from_T_derivative"],
        "wrong_N_in_kinetic_storage": normalization_residuals(energy=wrong_H)["total_to_per_site_storage"],
        "omitted_Jacobian": normalization_residuals(jacobian=s.Integer(1))["P_to_Pi_pushforward_measure"],
        "double_interaction": -r["E"]*r["N"]*r["gamma"]*r["Phi"]*r["m"]**2/2,
        "wrong_interaction_sign": r["E"]*r["N"]*r["gamma"]*r["Phi"]*r["m"]**2,
    }
    rejected = {name: s.simplify(value) != 0 for name, value in checks.items()}
    rejected["zero_class_double_count"] = 2*multiplicity(4, 2) != folded_multiplicity(4, 0)
    rejected["magnitude_not_invertible"] = abs(magnetization(3, 0)) == abs(magnetization(3, 3)) and magnetization(3, 0) != magnetization(3, 3)
    if not all(rejected.values()):
        raise ValueError("a declared negative mutation was not rejected")
    return rejected


def calculate():
    groups = {
        "conditional_thermodynamic_dictionary": _zeros(thermodynamic_residuals()),
        "entropy_and_ensemble_accounting": _zeros(entropy_residuals()),
        "cell_measure_and_kinetic_normalization": _zeros(normalization_residuals()),
        "old_quartic_map_new_thermal_split": _zeros(quartic_bridge_residuals()),
        "finite_N_bound_algebra": _zeros(finite_bound_residuals()),
        "analytic_normalizability_certificate": _zeros(tail_bound_residuals()),
        "explicit_pair_diagonal_convention": _zeros(pair_convention_residuals()),
        "signed_magnitude_entropy_accounting": _zeros(folding_entropy_residuals()),
        "zero_coupling_and_sign_symmetry": _zeros(decoupling_residuals()),
    }
    return {
        "completed_rounds": ["M0", "M1", "M2", "M3"], "checks": groups,
        "finite_enumeration": [finite_population_checks(N) for N in REGRESSION_N],
        "magnitude_folding": [folding_checks(N) for N in REGRESSION_N],
        "negative_controls": negative_controls(),
        "decisions": {
            "static_reference": "Conditional finite-N F/U/intrinsic-entropy dictionary closes for the chosen energy and fixed measure.",
            "Omega_correspondence": "Finite-grid exact coarse free energy; old quartic is a controlled large-N/small-m approximation only, not an exact all-R law.",
            "comparator": "Chosen binary mean-field energy plus retained Phi/P is a standard equilibrium construction; no unique UET discriminator.",
            "physical_Phi_entropy": "UNKNOWN; absence of additional hidden Phi states is a definition of this example only.",
            "old_HIST_F": "Physical intrinsic-entropy-correspondence remains open; old contracts/gates unchanged.",
            "next_question": "Does a separately justified physical retained-state/energy/measure map realize this conditional dictionary? No next model or dynamics started.",
        },
        "physical_acceptance": False, "unique_UET_discriminator": False,
        "new_core_terms": 0, "observational_rows": 0, "kinetic_law_added": False,
        "old_scientific_verifiers_rerun": False,
        "method": {"sympy": s.__version__, "arithmetic": "exact", "random_samples": 0,
                   "population_cases_are_regressions_not_general_proof": True},
        "analytic_dependencies": [
            "Restricted uniform conditioning and entropy chain rule use the declared microstate classes/measure.",
            "Finite-N bound uses the binomial mode and normalization proof, including endpoints.",
            "Tail certificate plus admitted parameter/domain signs establishes finite partition integrals.",
            "Old Taylor bounds from Argument 14.4 are reused, not rerun or extended to finite-N force derivatives.",
        ],
        "limitations": [
            "No independent specialist review or physical/SI calibration.",
            "No full stochastic process, relaxation/time-scale-separation proof, heat trajectory or entropy-production law.",
            "No full entropy counting of the physical Phi/Pi sector or Gaussian cross-lane addition.",
            "No finite-N force bound inferred from a free-energy value bound.",
            "Static dependence/readout is not learning, memory lifetime or cosmological openness.",
        ],
    }


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT), ROOT), **calculate()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only identities and artifact freshness")
    mode.add_argument("--emit-report", action="store_true", help="generate only the named compact artifact")
    args = parser.parse_args(argv)
    result = record()
    serialized = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(serialized, encoding="utf-8", newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes() != serialized.encode("utf-8"):
        raise ValueError("artifact absent/stale; review changes before explicit --emit-report")
    print(json.dumps({"rounds": result["completed_rounds"], "exact_groups": len(result["checks"]),
                      "finite_N": list(REGRESSION_N), "negative_controls": len(result["negative_controls"]),
                      "contract_review": result["contract_review_status"],
                      "physical_acceptance": False, "artifact": OUTPUT}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
