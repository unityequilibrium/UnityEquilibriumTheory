"""Restricted finite-ring spin/strain comparator, not a revised UET Core law.

Imported nearest-neighbor Hamiltonian; finite periodic control, fixed-k ensemble
and retained mechanical spectator are explicitly conditional choices. No rates,
trajectories, measurements, fitting, large-N or full-phonon reproduction.
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
CONTRACT = f"{TOPIC}/calculation_contracts/spin_strain_correspondence.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_spin_strain_correspondence.json"
REPORT = "docs/meta/UET_SPIN_STRAIN_CORRESPONDENCE_AUDIT.md"
REGRESSION_N = (4, 6)


def validate_population(N, k=None):
    if type(N) is not int or N < 4:
        raise ValueError("finite-ring domain requires integer N >= 4")
    if k is not None and (type(k) is not int or not 0 <= k <= N):
        raise ValueError("k must be an integer in [0,N]")


def ring_bonds(N):
    validate_population(N)
    return tuple((i, (i+1) % N) for i in range(N))


def bond_sum(spins):
    validate_population(len(spins))
    if any(type(x) is not int or x not in (-1, 1) for x in spins):
        raise ValueError("normalized spins must be exact integers +/-1")
    return sum(spins[i]*spins[j] for i, j in ring_bonds(len(spins)))


def histograms(N):
    validate_population(N)
    groups = {k: Counter() for k in range(N+1)}
    for spins in product((-1, 1), repeat=N):
        groups[sum(x == 1 for x in spins)][bond_sum(spins)] += 1
    return groups


def partition_from_histogram(hist, w):
    return sum(count*w**B for B, count in sorted(hist.items()))


def conditional(N, k):
    validate_population(N, k)
    w = s.Symbol("w", positive=True)  # w=exp(x), x=Jcal/(kBT); physical w>1
    hist = histograms(N)[k]
    Q = partition_from_histogram(hist, w)
    mean = sum(count*B*w**B for B, count in hist.items())/Q
    second = sum(count*B**2*w**B for B, count in hist.items())/Q
    return dict(N=N, k=k, w=w, hist=hist, G=s.Integer(comb(N, k)),
                Q=Q, mean=s.cancel(mean), variance=s.cancel(second-mean**2))


def _zeros(values):
    for name, value in values.items():
        if s.simplify(value) != 0:
            raise ValueError(f"exact identity failed: {name}: {value}")
    return {name: True for name in values}


def source_normalization_residuals(N, spin_factor=s.Rational(1, 4), bond_factor=1):
    """Use actual Si=si/2 sums, not just two copies of a quoted energy."""
    Jpaper = s.Symbol("J_paper", positive=True)
    values = {}
    for index, spins in enumerate(product((-1, 1), repeat=N)):
        half = [s.Rational(x, 2) for x in spins]
        source = -Jpaper*sum(half[i]*half[j] for i, j in ring_bonds(N))
        normalized = -Jpaper*spin_factor*bond_factor*bond_sum(spins)
        values[str(index)] = normalized-source
    return values


def probability_residuals(N, k):
    c = conditional(N, k)
    w, Q, mean, var, G = (c[x] for x in ("w", "Q", "mean", "variance", "G"))
    # Per-configuration p is w**B/Q; histogram count is NOT another probability.
    entropy, KL, chain = s.Integer(0), s.Integer(0), s.Integer(0)
    q = s.Symbol("q", positive=True)
    for B, count in c["hist"].items():
        p = w**B/Q
        logp = B*s.log(w)-s.log(Q)
        entropy -= count*p*logp
        KL += count*p*(logp+s.log(G))
        chain -= count*q*p*(s.log(q)+logp)
    return {
        "conditional_normalization": sum(n*w**B/Q for B, n in c["hist"].items())-1,
        "mean_from_log_partition": w*s.diff(Q, w)/Q-mean,
        "variance_from_mean_response": w*s.diff(mean, w)-var,
        "entropy_from_micro_probabilities": entropy-(s.log(Q)-s.log(w)*mean),
        "log_count_minus_KL": entropy-s.log(G)+KL,
        "retained_intrinsic_chain_density": chain+q*s.log(q)-q*entropy,
    }


def ensemble_residuals(N):
    w = s.Symbol("w", positive=True)
    groups = histograms(N)
    coarse = sum(partition_from_histogram(h, w) for h in groups.values())
    direct = sum(w**bond_sum(spins) for spins in product((-1, 1), repeat=N))
    transfer = s.Matrix([[w, 1/w], [1/w, w]])
    return {"micro_equals_sum_restricted": coarse-direct,
            "finite_ring_transfer_trace_not_infinite_limit": coarse-s.trace(transfer**N),
            "zero_coupling_counts": coarse.subs(w, 1)-2**N}


def thermodynamic_residuals():
    T, kB = s.symbols("T k_B", positive=True)
    phi = s.Symbol("Phi", real=True)
    J = s.Function("Jcal")(phi)  # fixed-coordinate J has no explicit T dependence
    Hret = s.Function("Hret")(phi)
    z = s.Symbol("x", real=True)
    L = s.Function("logQ")
    x = J/(kB*T)
    mean = s.diff(L(z), z).subs(z, x)
    var = s.diff(L(z), z, 2).subs(z, x)
    F = Hret-kB*T*L(x)
    U = Hret-J*mean
    Sint = kB*(L(x)-x*mean)
    force = -s.diff(Hret, phi)+s.diff(J, phi)*mean
    target = -J*s.diff(J, phi)*var/(kB*T**2)
    beta = s.Symbol("beta", positive=True)
    return {
        "S_from_fixed_state_T_derivative": -s.diff(F, T)-Sint,
        "U_equals_F_plus_TS": F+T*Sint-U,
        "beta_derivative_U": s.diff(beta*F.subs(T, 1/(kB*beta)), beta)-U.subs(T, 1/(kB*beta)),
        "force_from_F": -s.diff(F, phi)-force,
        "Phi_entropy_from_conditional_variance": s.diff(Sint, phi)-target,
        "Maxwell_force_entropy": s.diff(force, T)-s.diff(Sint, phi),
    }


def direct_N4_thermal_residuals():
    """Direct finite Q derivative, independent of the generic logQ chain proof."""
    J, kB, T = s.symbols("Jcal k_B T", positive=True)
    w = s.Symbol("w", positive=True)
    c = conditional(4, 2)
    Q = c["Q"].subs(c["w"], s.exp(J/(kB*T)))
    F = -kB*T*s.log(Q)
    mean = c["mean"].subs(c["w"], s.exp(J/(kB*T)))
    variance = c["variance"].subs(c["w"], s.exp(J/(kB*T)))
    S = kB*s.log(Q)-J*mean/T
    return {
        "direct_S_derivative": -s.diff(F, T)-S,
        "direct_U_mean_energy": F+T*S+J*mean,
        "direct_J_entropy_derivative": s.diff(S, J)+J*variance/(kB*T**2),
        "N4_partition_witness": c["Q"]-(4+2/w**4),
        "N4_mean_witness": c["mean"]+4/(2*w**4+1),
        "N4_variance_witness": c["variance"]-32*w**4/(2*w**4+1)**2,
    }


def strain_reference():
    eps, phi = s.symbols("epsilon Phi", real=True)
    eps_star, nu, J0, E = s.symbols("epsilon_star nu J_0 E_star", positive=True)
    # All fractional-power statements are restricted to 1+eps>0 and 1-eps_star*phi>0.
    J_eps = J0*(1+eps)**(-nu)/4
    J_phi = J0*(1-eps_star*phi)**(-nu)/4
    J_aff = J0*(1+nu*eps_star*phi)/4
    return dict(eps=eps, phi=phi, eps_star=eps_star, nu=nu, J0=J0, E=E,
                J_eps=J_eps, J_phi=J_phi, J_aff=J_aff)


def strain_residuals():
    r = strain_reference()
    ep, ph, e, nu, J0 = (r[k] for k in ("eps", "phi", "eps_star", "nu", "J0"))
    return {
        "compression_coordinate": r["J_eps"].subs(ep, -e*ph)-r["J_phi"],
        "positive_compression_exchange_derivative": s.diff(r["J_phi"], ph)-J0*nu*e*(1-e*ph)**(-nu-1)/4,
        "affine_value_at_reference": r["J_phi"].subs(ph, 0)-r["J_aff"].subs(ph, 0),
        "affine_derivative_at_reference": s.diff(r["J_phi"], ph).subs(ph, 0)-s.diff(r["J_aff"], ph),
        "Taylor_curvature": s.diff(r["J_eps"], ep, 2)-J0*nu*(nu+1)*(1+ep)**(-nu-2)/4,
    }


def direct_source_N4_residuals():
    """Bind the actual source power law to direct F derivatives at Phi=0."""
    r = strain_reference()
    T, kB = s.symbols("T k_B", positive=True)
    c = conditional(4, 2)
    J = r["J_phi"]
    Q = c["Q"].subs(c["w"], s.exp(J/(kB*T)))
    F = -kB*T*s.log(Q)
    force0 = (-s.diff(F, r["phi"])).subs(r["phi"], 0)
    entropy_phi0 = s.diff(-s.diff(F, T), r["phi"]).subs(r["phi"], 0)
    w0 = s.exp(r["J0"]/(4*kB*T))
    Jprime0 = r["J0"]*r["nu"]*r["eps_star"]/4
    target = -(r["J0"]/4)*Jprime0*c["variance"].subs(c["w"], w0)/(kB*T**2)
    return {"source_Q_force": force0-Jprime0*c["mean"].subs(c["w"], w0),
            "source_Q_Phi_entropy": entropy_phi0-target,
            "source_Q_Maxwell": s.diff(force0, T)-entropy_phi0}


def old_mean_field_residuals():
    r = strain_reference()
    N = s.Symbol("N", integer=True, positive=True)
    m = s.Symbol("m", real=True)
    j0 = r["J0"]/(2*r["E"])
    gamma = r["J0"]*r["nu"]*r["eps_star"]/(2*r["E"])
    old = -N*r["E"]*(j0+gamma*r["phi"])*m**2/2
    offdiag_pairs = (N**2*m**2-N)/2
    diagonal = -(j0+gamma*r["phi"])*r["E"]/2
    pair_rep = -(j0+gamma*r["phi"])*r["E"]*offdiag_pairs/N+diagonal
    return {"coordination_two_affine_parameter_map": old+N*r["J_aff"]*m**2,
            "old_square_diagonal_is_retained": old-pair_rep,
            "diagonal_Phi_derivative_not_discarded": s.diff(diagonal, r["phi"])+r["E"]*gamma/2}


def folding_residuals(N):
    w = s.Symbol("w", positive=True)
    groups = histograms(N)
    values = {}
    for k in range(N+1):
        values[f"flip_{k}"] = partition_from_histogram(groups[k], w)-partition_from_histogram(groups[N-k], w)
    folded = sum(partition_from_histogram(groups[k], w)*(1 if 2*k == N else 2)
                 for k in range(N//2+1))
    values["fold_preserves_partition_without_zero_double"] = folded-sum(partition_from_histogram(h, w) for h in groups.values())
    return values


def delta_bound(N, k, J, Jaff):
    """Exact energy envelope; no entropy/Taylor error added a second time."""
    validate_population(N, k)
    J, Jaff = s.sympify(J), s.sympify(Jaff)
    if J.is_positive is not True or Jaff.is_real is not True:
        raise ValueError("J must be positive and Jaff real")
    m = s.Rational(2*k-N, N)
    hist = histograms(N)[k]
    HM = -N*Jaff*m**2
    endpoints = (min(hist), max(hist))
    delta = s.Max(*(s.Abs(-J*B-HM) for B in endpoints))
    return dict(delta=delta, HM=HM, B_min=endpoints[0], B_max=endpoints[1])


def bound_checks(N):
    # One exact rational unit control, not a parameter sweep or material fit.
    J, Jaff = s.Rational(3, 2), s.Rational(5, 4)
    for k, hist in histograms(N).items():
        bound = delta_bound(N, k, J, Jaff)
        deviations = [-J*B-bound["HM"] for B in hist]
        if any(not -bound["delta"] <= d <= bound["delta"] for d in deviations):
            raise ValueError("delta does not enclose all configuration energies")
        if bound["delta"] != max(abs(d) for d in deviations):
            raise ValueError("convex endpoint maximum differs from exact maximum")
    # Generic envelope proof is in report: e^-beta*delta <= average <= e^beta*delta.
    return {"N": N, "endpoint_envelope_all_classes": True,
            "exact_control_J": "3/2", "exact_control_Jaff": "5/4"}


def N4_limits_and_bounds():
    c = conditional(4, 2)
    w = c["w"]
    sint = s.log(c["Q"])-s.log(w)*c["mean"]
    J, Ja = s.symbols("Jcal Jaff", positive=True)
    delta = delta_bound(4, 2, J, Ja)["delta"]
    return {
        "zero_coupling_or_high_T_entropy": sint.subs(w, 1)-s.log(6),
        "low_T_fixed_J_entropy_ground_degeneracy": s.limit(sint, w, s.oo)-s.log(4),
        "uniformity_fails_for_finite_positive_x": c["Q"]-6-(2/w**4-2),
        "central_delta_is_four_J": delta-4*J,
        "upper_Q_envelope_certificate": c["Q"]-6/w**4-4*(1-1/w**4),
        "lower_F_difference_certificate": 6-c["Q"]-2*(1-1/w**4),
    }


def negative_controls():
    c = conditional(4, 2)
    w = c["w"]
    S = s.log(c["Q"])-s.log(w)*c["mean"]
    r = strain_reference()
    bad = {
        "wrong_spin_normalization": any(v != 0 for v in source_normalization_residuals(4, spin_factor=1).values()),
        "double_counted_bonds": any(v != 0 for v in source_normalization_residuals(4, bond_factor=2).values()),
        "uniform_entropy_at_nonuniform_weights": s.simplify(S.subs(w, 2)-s.log(6)) != 0,
        "wrong_strain_orientation": s.simplify(s.diff(r["J_eps"].subs(r["eps"], r["eps_star"]*r["phi"]), r["phi"]).subs(r["phi"], 0)
            -s.diff(r["J_phi"], r["phi"]).subs(r["phi"], 0)) != 0,
        "unconstrained_partition_used_for_fixed_k": sum(partition_from_histogram(h, w) for h in histograms(4).values()).subs(w, 1) != c["Q"].subs(w, 1),
        "discarded_conditional_interaction_energy": c["mean"].subs(w, 2) != 0,
        "zero_class_doubled": c["Q"].subs(w, 1) != 2*c["Q"].subs(w, 1),
        "histogram_entropy_omits_micro_degeneracy": s.log(6) != -s.Rational(2, 3)*s.log(s.Rational(2, 3))-s.Rational(1, 3)*s.log(s.Rational(1, 3)),
    }
    if not all(bad.values()):
        raise ValueError("a deliberate wrong convention was not detected")
    return bad


def calculate():
    finite = []
    for N in REGRESSION_N:
        groups = histograms(N)
        if any(sum(h.values()) != comb(N, k) for k, h in groups.items()):
            raise ValueError("class counts differ from binomial multiplicity")
        source_checks = _zeros(source_normalization_residuals(N))
        finite.append({"N": N, "configurations": 2**N,
                       "source_spin_and_bonds": {"checked_configurations": len(source_checks), "all_exact_residuals_zero": all(source_checks.values())},
                       "partition": _zeros(ensemble_residuals(N)),
                       "conditional_classes": {str(k): _zeros(probability_residuals(N, k)) for k in groups},
                       "folding": _zeros(folding_residuals(N)), "energy_envelope": bound_checks(N)})
    if histograms(4)[2] != Counter({0: 4, -4: 2}):
        raise ValueError("minimal fixed-C energy-splitting witness changed")
    checks = {
        "fixed_coordinate_thermodynamics": _zeros(thermodynamic_residuals()),
        "direct_N4_derivatives_and_fluctuations": _zeros(direct_N4_thermal_residuals()),
        "strain_law_sign_and_Taylor_curvature": _zeros(strain_residuals()),
        "actual_source_N4_force_entropy": _zeros(direct_source_N4_residuals()),
        "old_mean_field_map_and_diagonal": _zeros(old_mean_field_residuals()),
        "N4_limits_and_energy_free_energy_envelope": _zeros(N4_limits_and_bounds()),
    }
    return {
        "completed_rounds": ["N0", "N1", "N2", "N3"], "checks": checks,
        "finite_ring_controls": finite, "negative_controls": negative_controls(),
        "witness": {"N": 4, "k": 2, "C_over_sC": "0", "bond_multiplicity": {"-4": 2, "0": 4},
                    "Q": "4+2*exp(-4*x)", "mean_B": "-4/(2*exp(4*x)+1)",
                    "variance_B": "32*exp(4*x)/(2*exp(4*x)+1)^2", "x": "Jcal/(k_B*T)"},
        "decisions": {
            "uniform_counting": "Valid only for equal conditional energies (or beta*J=0 limit); NN fixed-k classes generally have nonuniform weights. M remains valid for its own chosen squared-sum energy.",
            "Phi_dependent_intrinsic_entropy": "Spin configurations alone give dPhi S_int=-Jcal*Jcal_prime*Var(B)/(k_B*T^2); no added hidden Phi degree of freedom or information substance.",
            "microscopic_equivalence": "DIFFERENT: NN ring and M squared-sum are not exact finite-N realizations of each other; explicit fixed-C witness suffices.",
            "affine_exchange": "APPROXIMATE in a declared small-strain window, with Taylor bound; not an all-Phi coupling identity.",
            "full_Phi_Pi": "UNRESOLVED: physical elastic/phonon potential, zero/reference convention, mode inertia and state/measure mapping are not derived by this spin-sector calculation.",
            "comparator": "Imported standard statistical mechanics; no UET-specific discriminator or physical data validation.",
        },
        "physical_acceptance": False, "unique_UET_discriminator": False,
        "new_core_terms": 0, "kinetic_law_added": False, "observational_rows": 0,
        "old_scientific_verifiers_rerun": False,
        "method": {"sympy": s.__version__, "arithmetic": "exact", "random_samples": 0,
                   "parameter_sweep": False, "finite_ring_is_not_full_paper_reproduction": True},
        "analytic_dependencies": [
            "Finite canonical Gibbs/KL identity and positivity; T-independent fixed-coordinate Hamiltonian.",
            "Positive conditional bond variance and chain rule give entropy/force consistency.",
            "Convex endpoint energy envelope gives a log-partition value bound for any finite class.",
            "Taylor second-derivative supremum on |epsilon|<=rho<1 supplies exchange-value remainder.",
            "Lattice/phonon and external-force/ensemble distinctions are audited from source, not newly computed.",
        ],
        "limitations": ["No actual material mapping, calibration or independent specialist approval.",
                        "Hret is the common M spectator, not derived physical lattice internal energy.",
                        "No dynamics, fast-equilibration proof, trajectory heat, entropy production or memory lifetime.",
                        "No all-R strain integral, thermodynamic-limit phase claim or force bound from energy envelope.",
                        "No full lattice entropy is set to zero or added to old Omega automatically."],
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
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(payload, encoding="utf-8", newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes() != payload.encode("utf-8"):
        raise ValueError("artifact absent/stale; review changes before explicit --emit-report")
    print(json.dumps({"rounds": result["completed_rounds"], "exact_groups": len(result["checks"]),
                      "finite_N": list(REGRESSION_N), "negative_controls": len(result["negative_controls"]),
                      "review": result["contract_review_status"], "physical_acceptance": False,
                      "artifact": OUTPUT}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
