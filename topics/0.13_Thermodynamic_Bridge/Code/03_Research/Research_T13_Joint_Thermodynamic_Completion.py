"""Exact checks for a conditional thermostat, NOT a new stochastic Core law.

No solver, random samples, measured data or fit. The report supplies the boundary,
measure and analytic arguments that finite symbolic tests cannot certify alone.
Only --emit-report writes the compact generated artifact; --check is read-only.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys

import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata, load_json

TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
CONTRACT = f"{TOPIC}/calculation_contracts/joint_thermodynamic_completion.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_joint_thermodynamic_completion.json"
CORE = "docs/core/02_equations/matter_space/uet_matter_space.py"


def reference():
    C, Phi, Pi = s.symbols("C Phi Pi", real=True)
    aC, aP, g, JC, JP = s.symbols("a_C a_Phi g J_C J_Phi", real=True)
    bC, bP, MC, MP, tau, theta = s.symbols(
        "b_C b_Phi M_C M_Phi tau Theta", positive=True)
    omega = aC*C**2/2 + bC*C**4/4 + aP*Phi**2/2 + bP*Phi**4/4 - g*C**2*Phi/2
    muC, muP = s.diff(omega, C), s.diff(omega, Phi)
    energy = omega + tau*Pi**2/(2*MP)
    drift = s.Matrix([-MC*muC+JC, Pi, (-Pi-MP*muP+JP)/tau])
    noise = s.Matrix([[s.sqrt(2*MC*theta), 0], [0, 0],
                      [0, s.sqrt(2*MP*theta)/tau]])
    return dict(C=C, Phi=Phi, Pi=Pi, aC=aC, aP=aP, g=g, JC=JC, JP=JP,
                bC=bC, bP=bP, MC=MC, MP=MP, tau=tau, theta=theta,
                omega=omega, muC=muC, muP=muP, energy=energy, drift=drift,
                noise=noise, state=(C, Phi, Pi), DC=MC*theta, DP=MP*theta/tau**2)


def generator(f, r, c_noise_scale=1, pi_noise_scale=1):
    """Backward Itô generator; scales multiply diffusion, not noise amplitude."""
    C, _, Pi = r["state"]
    return s.expand(sum(a*s.diff(f, x) for a, x in zip(r["drift"], r["state"]))
                    + c_noise_scale*r["DC"]*s.diff(f, C, 2)
                    + pi_noise_scale*r["DP"]*s.diff(f, Pi, 2))


def _exact_zeros(expressions):
    result = {k: s.simplify(v) for k, v in expressions.items()}
    failed = {k: str(v) for k, v in result.items() if v != 0}
    if failed:
        raise ValueError(f"exact identity failed: {failed}")
    return {k: str(v) for k, v in result.items()}


def core_projection_residuals(source_text=None):
    """Read actual Core expressions in the declared homogeneous unit-cell limit.

    A tiny explicit AST interpreter projects integrals to one cell and spatial
    derivatives to zero. It neither imports/executes Core nor tests other lanes.
    Unsupported source changes fail closed instead of silently accepting a mirror.
    """
    r = reference()
    source_text = source_text if source_text is not None else (ROOT/CORE).read_text(encoding="utf-8-sig")
    tree = ast.parse(source_text)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    values = {
        "state.C": r["C"], "state.space_response": r["Phi"], "state.space_rate": r["Pi"],
        "config.a_matter": r["aC"], "config.b_matter": r["bC"],
        "config.a_space": r["aP"], "config.b_space": r["bP"],
        "config.coupling_g": r["g"], "config.mobility_matter": r["MC"],
        "config.mobility_space": r["MP"], "config.tau_space": r["tau"],
        "config.kappa_matter": s.Symbol("kappa_C"), "config.kappa_space": s.Symbol("kappa_Phi"),
        "C": r["C"], "Phi": r["Phi"], "dx": s.Integer(1), "spacing": s.Integer(1),
        "lap_C": s.Integer(0), "lap_Phi": s.Integer(0),
        "mu_matter": r["muC"], "mu_space": r["muP"],
        "matter_drive": r["JC"], "space_drive": r["JP"],
    }

    def evaluate(n):
        name = ast.unparse(n)
        if name in values:
            return values[name]
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            return s.Rational(str(n.value))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -evaluate(n.operand)
        if isinstance(n, ast.Tuple):
            return tuple(evaluate(x) for x in n.elts)
        if isinstance(n, ast.BinOp):
            a, b = evaluate(n.left), evaluate(n.right)
            operations = {ast.Add: lambda: a+b, ast.Sub: lambda: a-b,
                          ast.Mult: lambda: a*b, ast.Div: lambda: a/b, ast.Pow: lambda: a**b}
            if type(n.op) in operations:
                return operations[type(n.op)]()
        if isinstance(n, ast.Call):
            fn = ast.unparse(n.func)
            if fn in {"float", "integral_1d"}:
                return evaluate(n.args[0])
            if fn == "np.square":
                return evaluate(n.args[0])**2
            if fn == "gradient_energy_integral_1d":
                return s.Integer(0)
            if fn == "matter_space_free_energy":
                return values["projected_omega"]
            if fn == "state.space_rate.copy":
                return r["Pi"]
        raise ValueError(f"unsupported homogeneous Core expression: {name}")

    def assignment(fn, name, nodes=None):
        nodes = functions[fn].body if nodes is None else nodes
        for n in nodes:
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
                return evaluate(n.value)
        raise ValueError(f"missing Core assignment: {fn}:{name}")

    def nonconserved_body(fn):
        nodes = [n for n in functions[fn].body if isinstance(n, ast.If)
                 and ast.unparse(n.test) == "config.matter_dynamics == 'conserved'"]
        branches = [n.orelse for n in nodes if n.orelse]
        if len(branches) != 1:
            raise ValueError(f"ambiguous nonconserved Core branch: {fn}")
        return branches[0]

    def returned(fn):
        returns = [n for n in functions[fn].body if isinstance(n, ast.Return)]
        if len(returns) != 1:
            raise ValueError(f"ambiguous Core return: {fn}")
        return evaluate(returns[0].value)

    # Bind actual return expressions too; matching an unused local is insufficient.
    values["local_density"] = assignment("matter_space_free_energy", "local_density")
    for name in ("local", "matter_gradient", "space_gradient"):
        values[name] = assignment("matter_space_free_energy", name)
    values["projected_omega"] = returned("matter_space_free_energy")
    values["mu_C"] = assignment("matter_space_chemical_potentials", "mu_C")
    values["mu_Phi"] = assignment("matter_space_chemical_potentials", "mu_Phi")
    values["mu_matter"], values["mu_space"] = returned("matter_space_chemical_potentials")
    values["kinetic"] = assignment("matter_space_extended_energy", "kinetic")
    values["dC"] = assignment("matter_space_rhs", "dC", nonconserved_body("matter_space_rhs"))
    for name in ("dPhi", "dPi"):
        values[name] = assignment("matter_space_rhs", name)
    rhs = returned("matter_space_rhs")
    values["sigma_matter"] = assignment("matter_space_dissipation", "sigma_matter", nonconserved_body("matter_space_dissipation"))
    values["sigma_space"] = assignment("matter_space_dissipation", "sigma_space")
    sigma = returned("matter_space_dissipation")
    projected = {
        "omega": values["projected_omega"],
        "muC": values["mu_matter"], "muP": values["mu_space"],
        "energy": returned("matter_space_extended_energy"),
        "dC": rhs[0], "dPhi": rhs[1], "dPi": rhs[2],
        "returned_muC": rhs[3], "returned_muP": rhs[4],
        "sigmaC": sigma[0], "sigmaPi": sigma[1], "sigma_total": sigma[2],
    }
    expected = dict(omega=r["omega"], muC=r["muC"], muP=r["muP"], energy=r["energy"],
                    dC=r["drift"][0], dPhi=r["Pi"], dPi=r["drift"][2],
                    returned_muC=r["muC"], returned_muP=r["muP"],
                    sigmaC=r["MC"]*r["muC"]**2, sigmaPi=r["Pi"]**2/r["MP"],
                    sigma_total=r["MC"]*r["muC"]**2+r["Pi"]**2/r["MP"])
    return {k: s.simplify(v-expected[k]) for k, v in projected.items()}


def first_law_residuals(heat_sign=1):
    r = reference()
    C, Phi, Pi = r["state"]
    MC, MP, tau, theta = (r[k] for k in ("MC", "MP", "tau", "theta"))
    muC, JC, JP = (r[k] for k in ("muC", "JC", "JP"))
    aC = r["drift"][0]
    fC, fP = JC/MC, JP/MP
    bC, bP = r["noise"][0, 0], r["noise"][2, 1]
    # Work/heat as Stratonovich coefficients in the two independent Wiener ports.
    w_dt, w_C, w_P = fC*aC+fP*Pi, fC*bC, s.Integer(0)
    qC_dt = (fC-muC)*aC-r["DC"]*s.diff(muC, C)
    qP_dt = Pi**2/MP-theta/tau
    q_C, q_P = (fC-muC)*bC, -s.sqrt(2*theta/MP)*Pi
    # Conversion of dE=grad(E) o dX adds these two Itô terms.
    correction = MC*theta*s.diff(r["omega"], C, 2)+theta/tau
    deterministic = -MC*muC**2-Pi**2/MP+muC*JC+Pi*JP/MP
    return {
        "ito_energy_drift": generator(r["energy"], r)-deterministic-correction,
        "work_minus_heat_dt": generator(r["energy"], r)-w_dt+heat_sign*(qC_dt+qP_dt),
        "work_minus_heat_C_noise": muC*bC-w_C+heat_sign*q_C,
        "work_minus_heat_Pi_noise": tau*Pi*bP/MP-w_P+heat_sign*q_P,
        "ito_stratonovich_energy_correction": correction-
            (s.diff(r["energy"], C, 2)*bC**2+s.diff(r["energy"], Pi, 2)*bP**2)/2,
        "no_independent_Phi_noise": sum(r["noise"][1, j]**2 for j in range(2)),
    }


def coarse_free_energy_residuals():
    """Same one-temperature drift, different admissible intrinsic-entropy ledgers."""
    r = reference()
    temperature, T0, kappa = s.symbols("vartheta Theta_0 kappa", positive=True)
    Phi, Pi = r["Phi"], r["Pi"]
    intrinsic = kappa*Phi**2
    F = r["omega"]+(T0-temperature)*intrinsic
    U = s.simplify(F-temperature*s.diff(F, temperature))
    qref = s.Symbol("q_ref")
    qphysical = qref-2*T0*kappa*Phi*Pi
    return {
        "same_F_at_reference_bath": F.subs(temperature, T0)-r["omega"],
        "intrinsic_entropy_definition": -s.diff(F, temperature)-intrinsic,
        "internal_energy_differs": U-r["omega"]-T0*intrinsic,
        "first_law_intrinsic_heat_correction":
            2*T0*kappa*Phi*Pi+qphysical-qref,
    }


def stationary_residual(c_noise_scale=1, pi_noise_scale=1):
    """L* rho_G / rho_G, using log derivatives, with equilibrium sources zero."""
    r = reference()
    logp = -r["energy"]/r["theta"]
    drift = r["drift"].subs({r["JC"]: 0, r["JP"]: 0})
    result = sum(-s.diff(a, x)-a*s.diff(logp, x) for a, x in zip(drift, r["state"]))
    for x, D in [(r["C"], c_noise_scale*r["DC"]), (r["Pi"], pi_noise_scale*r["DP"])]:
        result += D*(s.diff(logp, x)**2+s.diff(logp, x, 2))
    return s.factor(result)


def parity_split(r, pi_parity=-1):
    if pi_parity not in (-1, 1):
        raise ValueError("parity must be -1 or +1")
    parity = (1, 1, pi_parity)
    transformed = {x: e*x for x, e in zip(r["state"], parity)}
    reversed_drift = s.Matrix([e*a.subs(transformed, simultaneous=True)
                              for e, a in zip(parity, r["drift"])])
    return ((r["drift"]-reversed_drift)/2, (r["drift"]+reversed_drift)/2)


def parity_residuals(pi_parity=-1):
    r = reference()
    rev, irr = parity_split(r, pi_parity)
    target_rev = s.Matrix([0, r["Pi"], (-r["MP"]*r["muP"]+r["JP"])/r["tau"]])
    target_irr = s.Matrix([r["drift"][0], 0, -r["Pi"]/r["tau"]])
    return {**{f"reversible_{i}": rev[i]-target_rev[i] for i in range(3)},
            **{f"irreversible_{i}": irr[i]-target_irr[i] for i in range(3)},
            "divergence_reversible_drift": sum(s.diff(a, x) for a, x in zip(rev, r["state"]))}


def equilibrium_current_residuals():
    r = reference()
    rev, irr = parity_split(r)
    logp = -r["energy"]/r["theta"]
    D = (r["DC"], 0, r["DP"])
    result = {f"irreversible_current_over_density_{i}":
              (irr[i]-D[i]*s.diff(logp, x)).subs({r["JC"]: 0, r["JP"]: 0})
              for i, x in enumerate(r["state"])}
    result["reversible_current_divergence_over_density"] = sum(
        s.diff(a, x)+a*s.diff(logp, x) for a, x in zip(rev, r["state"])).subs({r["JP"]: 0})
    return result


def coercivity_residuals():
    """Exact sum-of-squares lower bound; integrability argument is in the report."""
    r = reference()
    C, Phi, Pi = r["state"]
    bC, bP, aC, aP, g = (r[k] for k in ("bC", "bP", "aC", "aP", "g"))
    eps = bC/8
    B = aP/2-g**2/(2*bC)
    squares = ((s.sqrt(eps)*C**2-g*Phi/(4*s.sqrt(eps)))**2
               +(s.sqrt(bC)*C**2/4+aC/s.sqrt(bC))**2
               +(s.sqrt(bP/8)*Phi**2+B/(2*s.sqrt(bP/8)))**2)
    lower = bC*C**4/16+bP*Phi**4/8+r["tau"]*Pi**2/(2*r["MP"])-aC**2/bC-2*B**2/bP
    return {"energy_minus_coercive_lower_bound_is_sum_of_squares": r["energy"]-lower-squares}


def entropy_residuals():
    """Exact local algebra. Reversible entropy integrates to zero by div a_rev=0.

    Boundary integrals are analytic assumptions, not evaluated finite samples.
    Heat-current forms equal R1 Itô means up to the displayed total derivatives.
    """
    r = reference()
    p = s.Symbol("rho", positive=True)
    uC, uP = s.symbols("partial_C_logrho partial_Pi_logrho", real=True)
    MC, MP, tau, theta, Pi = (r[k] for k in ("MC", "MP", "tau", "theta", "Pi"))
    aC, DC, DP = r["drift"][0], r["DC"], r["DP"]
    m = tau/MP
    jC = p*(aC-DC*uC)
    jP = p*(-Pi/tau-DP*uP)
    qC, qY = (aC/MC)*jC, -m*Pi*jP
    fCminusmu = aC/MC
    qC_ito = (fCminusmu*aC-DC*s.diff(r["muC"], r["C"]))*p
    qY_ito = (Pi**2/MP-theta/tau)*p
    derivative_C = -s.diff(r["muC"], r["C"])*p+fCminusmu*p*uC
    derivative_Pi = p+Pi*p*uP
    return {
        "C_entropy_plus_heat_equals_current_square":
            -jC*uC+qC/theta-jC**2/(DC*p),
        "Y_irreversible_entropy_plus_heat_equals_current_square":
            -jP*uP+qY/theta-jP**2/(DP*p),
        "C_current_heat_minus_Ito_heat_is_boundary_derivative": qC-qC_ito+DC*derivative_C,
        "Y_current_heat_minus_Ito_heat_is_boundary_derivative": qY-qY_ito-m*DP*derivative_Pi,
    }


def gaussian_pi_variance():
    r = reference()
    Pi = r["Pi"]
    density = s.exp(-r["tau"]*Pi**2/(2*r["MP"]*r["theta"]))
    return s.simplify(s.integrate(Pi**2*density, (Pi, -s.oo, s.oo)) /
                      s.integrate(density, (Pi, -s.oo, s.oo)))


def r2_checks():
    r = reference()
    return {
        "R2_Gibbs_stationarity": _exact_zeros({"Fokker_Planck_residual_over_Gibbs": stationary_residual()}),
        "R2_time_reversal": _exact_zeros(parity_residuals()),
        "R2_equilibrium_currents": _exact_zeros(equilibrium_current_residuals()),
        "R2_normalizability_SOS": _exact_zeros(coercivity_residuals()),
        "R2_entropy_production": _exact_zeros(entropy_residuals()),
        "R2_positive_friction_at_equilibrium": _exact_zeros({
            "Pi_variance_minus_Gibbs_value": gaussian_pi_variance()-r["MP"]*r["theta"]/r["tau"],
            "Pi_friction_loss_minus_Theta_over_tau": gaussian_pi_variance()/r["MP"]-r["theta"]/r["tau"]}),
    }


def generator_partition_residuals():
    r = reference()
    C, Phi, Pi = r["state"]
    f = s.Function("f")(C, Phi, Pi)
    LC = r["drift"][0]*s.diff(f, C)+r["DC"]*s.diff(f, C, 2)
    LY = Pi*s.diff(f, Phi)+r["drift"][2]*s.diff(f, Pi)+r["DP"]*s.diff(f, Pi, 2)
    covariance = r["noise"]*r["noise"].T
    return {"L_equals_LC_plus_LY": generator(f, r)-LC-LY,
            "C_Pi_quadratic_covariation": covariance[0, 2],
            "C_Phi_quadratic_covariation": covariance[0, 1]}


def information_residuals():
    """Fixed-measure chain rule and current-based flow, not a universal I state.

    Marginal entropy integrands are lifted to the joint domain. The Y balance
    includes a reversible entropy divergence, which integrates to zero, NOT a
    pointwise zero or an omitted reversible information current.
    """
    r = reference()
    p, pC, pY, Z = s.symbols("rho rho_C rho_Y Z", positive=True)
    uC, uF, uP, vC, vF, vP = s.symbols("u_C u_Phi u_Pi v_C v_Phi v_Pi", real=True)
    theta, Pi = r["theta"], r["Pi"]
    rev, _ = parity_split(r)
    jC = p*(r["drift"][0]-r["DC"]*uC)
    jF = p*Pi
    jPirr = p*(-Pi/r["tau"]-r["DP"]*uP)
    jPrev = p*rev[2]
    jP = jPirr+jPrev
    IC = jC*(uC-vC)
    IY = jF*(uF-vF)+jP*(uP-vP)
    SC = -jC*vC
    SY = -jF*vF-jP*vP
    Sjoint = -jC*uC-jF*uF-jP*uP
    qC = r["drift"][0]*jC/r["MC"]
    qY = -r["tau"]*Pi*jPirr/r["MP"]
    chain = -p*s.log(p)+p*s.log(pC)+p*s.log(pY)+p*s.log(p/(pC*pY))
    return {
        "joint_marginal_entropy_chain_rule": s.expand_log(chain, force=True),
        "entropy_rate_chain_rule_with_all_currents": Sjoint-SC-SY+IC+IY,
        "C_partial_second_law": SC+qC/theta-IC-jC**2/(r["DC"]*p),
        "Y_partial_second_law_up_to_reversible_entropy_divergence":
            SY+qY/theta-IY-jPirr**2/(r["DP"]*p)+jF*uF+jPrev*uP,
        "reversible_Y_drift_divergence": s.diff(rev[1], r["Phi"])+s.diff(rev[2], Pi),
        "ensemble_free_energy_relative_entropy_identity":
            p*r["energy"]+theta*p*s.log(p)+theta*p*s.log(Z)
            -theta*p*(s.log(p)+r["energy"]/theta+s.log(Z)),
    }


def gibbs_dependence_residuals():
    r = reference()
    C, Phi, Pi = r["state"]
    EC = r["aC"]*C**2/2+r["bC"]*C**4/4
    EY = r["aP"]*Phi**2/2+r["bP"]*Phi**4/4+r["tau"]*Pi**2/(2*r["MP"])
    logp = -r["energy"]/r["theta"]
    return {
        "zero_coupling_energy_separates": r["energy"].subs(r["g"], 0)-EC-EY,
        "C_reflection_symmetry": r["energy"].subs(C, -C)-r["energy"],
        "C_Phi_cross_moment_integrand_odd": C*Phi+(-C)*Phi,
        "nonzero_dependence_witness": s.diff(logp, C, Phi)-r["g"]*C/r["theta"],
        "Pi_independent_of_C_at_Gibbs": s.diff(logp, C, Pi),
        "Pi_independent_of_Phi_at_Gibbs": s.diff(logp, Phi, Pi),
    }


def comparator_residuals():
    r = reference()
    m, gamma = r["tau"]/r["MP"], 1/r["MP"]
    fC, fPhi = r["JC"]/r["MC"], r["JP"]/r["MP"]
    return {
        "overdamped_C_force_port": r["drift"][0]-r["MC"]*(-r["muC"]+fC),
        "underdamped_mass_friction_force_port": m*r["drift"][2]+gamma*r["Pi"]+r["muP"]-fPhi,
        "force_noise_amplitude": m*r["noise"][2, 1]-s.sqrt(2*gamma*r["theta"]),
        "C_noise_amplitude": r["noise"][0, 0]-s.sqrt(2*r["MC"]*r["theta"]),
        "velocity_state": r["drift"][1]-r["Pi"],
        "same_energy": r["energy"]-r["omega"]-m*r["Pi"]**2/2,
    }


def normalization_residuals():
    N = s.Symbol("N", integer=True, positive=True)
    epsilon0, theta_site = s.symbols("epsilon_0 theta_site", positive=True)
    Eref = s.Symbol("E_ref", real=True)
    return {"total_energy_over_kBT_equals_per_site_exponent":
            N*epsilon0*Eref/(epsilon0*theta_site)-Eref/(theta_site/N)}


def r3_checks():
    return {
        "R3_generator_partition": _exact_zeros(generator_partition_residuals()),
        "R3_entropy_information_flow": _exact_zeros(information_residuals()),
        "R3_equilibrium_dependence_not_covariance": _exact_zeros(gibbs_dependence_residuals()),
        "R3_standard_comparator": _exact_zeros(comparator_residuals()),
        "R3_cell_normalization": _exact_zeros(normalization_residuals()),
    }


def calculate():
    checks = {
        "core_homogeneous_projection": _exact_zeros(core_projection_residuals()),
        "R1_first_law": _exact_zeros(first_law_residuals()),
        "R1_free_energy_nonuniqueness": _exact_zeros(coarse_free_energy_residuals()),
        **r2_checks(),
        **r3_checks(),
    }
    if all(s.simplify(v) == 0 for v in first_law_residuals(-1).values()):
        raise ValueError("wrong heat sign was not rejected")
    if stationary_residual(c_noise_scale=2) == 0 or stationary_residual(pi_noise_scale=2) == 0:
        raise ValueError("wrong diffusion was not rejected")
    if all(s.simplify(v) == 0 for v in parity_residuals(pi_parity=1).values()):
        raise ValueError("wrong Pi parity was not rejected")
    return {
        "completed_rounds": ["R0", "R1", "R2", "R3"], "checks": checks,
        "negative_controls": {"wrong_heat_sign_rejected": True, "wrong_C_diffusion_rejected": True,
                              "wrong_Pi_diffusion_rejected": True, "wrong_Pi_parity_rejected": True},
        "interpretation": "Conditional REF-E consistency and exact matched standard-Langevin equivalence. Sigma is not total entropy production; mutual information is a derived statistical quantity, not the author's universal information. HIST-F physical heat remains underdetermined without intrinsic entropy/measure.",
        "decisions": {
            "REF_E": "consistent under declared thermostat, parity, measure and boundary assumptions",
            "HIST_F": "additional thermal/microscopic correspondence required; one-temperature heat nonuniqueness proved",
            "comparator": "exact same generator/state/source/readout implies no UET-label discrimination",
            "not_inferred": ["unique mobility or coupling", "universal information ontology", "physical material validation",
                             "cosmological openness, learning or persistence", "finite-temperature memory lifetime"],
            "one_next_question": "Can one explicit joint coarse-graining/thermal measure realize the existing Omega family and fix intrinsic entropy without fitting or extra Core terms? Not started here."},
        "physical_acceptance": False, "new_core_terms": 0, "observational_rows": 0,
        "old_scientific_verifiers_rerun": False, "unique_UET_discriminator": False,
        "method": {"sympy": s.__version__, "arithmetic": "exact", "samples": 0},
        "limitations": ["No SI/microscopic correspondence", "No independent specialist review",
                        "Density smoothness, tail and finite-integral assumptions are analytic conditions, not sampled tests",
                        "Quartic R-domain diffusion is not the finite-N bounded binary process",
                        "No stochastic trajectory, finite-temperature retention lifetime or spatial/conserved proof"],
    }


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT), ROOT), **calculate()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only exact checks and artifact freshness")
    mode.add_argument("--emit-report", action="store_true", help="generate only the named compact artifact")
    args = parser.parse_args(argv)
    result = record()
    serialized = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(serialized, encoding="utf-8", newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes() != serialized.encode("utf-8"):
        raise ValueError("artifact absent/stale; review changed evidence before explicit --emit-report")
    print(json.dumps({"rounds": result["completed_rounds"], "exact_groups": len(result["checks"]),
                      "contract_review": result["contract_review_status"],
                      "physical_acceptance": False, "artifact": OUTPUT}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
