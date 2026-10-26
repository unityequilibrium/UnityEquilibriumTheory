"""Exact homogeneous regime/response/write audit of the existing C/Phi/Pi law.

Offline rational/algebraic work only. No trajectories, numerical roots, parameter
search, old producer execution or Core mutation. Classification proofs accompany
the checks in UET_RETAINED_RESPONSE_REGIME_CLASSIFICATION.md.
"""
from __future__ import annotations

import argparse
import ast
from functools import lru_cache
import importlib
import json
from pathlib import Path
import sys

import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata, load_json

# Pure restricted AST utilities only; never call U's algebra/calculate/main.
u = importlib.import_module("Research_T13_Retained_Response_Requirement_Audit")
TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
STEM = "retained_response_regime_classification"
CONTRACT = f"{TOPIC}/calculation_contracts/{STEM}.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_{STEM}.json"
U_ARTIFACT = f"{TOPIC}/Result/artifacts/t13_retained_response_requirement_audit.json"
CORE = "docs/core/02_equations/matter_space/uet_matter_space.py"
BASELINE = "d6ddc910313028f63828a8bf02897480822c10e3"
C, Phi, Pi, JC, JP = s.symbols("C Phi Pi J_C J_Phi", real=True)
a = s.Symbol("a", real=True)
alpha, g = s.symbols("alpha g", nonnegative=True)
b, beta, mc, mf, tau = s.symbols("b beta M_C M_Phi tau", positive=True)
k, h = s.symbols("k h", positive=True)
v, cstar = s.symbols("v C_star", real=True)
z = s.Symbol("z")
X = s.Symbol("X", nonnegative=True)
Y = s.Symbol("Y", real=True)
Tw = s.Symbol("T_w", positive=True)
t = s.Symbol("u", real=True)
PARAMS = (a, b, alpha, beta, g, mc, mf, tau)
COEX = (s.Rational(3, 8), 1, 1, 1, 2, 1, 1, 1)
SINGLE = (1, 1, 1, 1, 1, 1, 1, 1)


def equal(left, right):
    if isinstance(left, s.MatrixBase) or isinstance(right, s.MatrixBase):
        left, right = s.Matrix(left), s.Matrix(right)
        return left.shape == right.shape and all(equal(x, 0) for x in left-right)
    return s.simplify(s.cancel(left-right)) == 0


def source_domain(text=None):
    """Pin the relevant config checks, fail closed instead of widening a_space."""
    text = text if text is not None else (ROOT/CORE).read_text(encoding="utf-8")
    tree = ast.parse(text)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MatterSpaceConfig")
    post = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__post_init__")
    loops = [n for n in post.body if isinstance(n, ast.For)]
    if len(loops) != 1 or not isinstance(loops[0].iter, ast.Tuple):
        raise ValueError("config positivity policy needs renewed review")
    positive = [n.value for n in loops[0].iter.elts if isinstance(n, ast.Constant)]
    expected = ["b_matter", "kappa_matter", "mobility_matter", "b_space", "kappa_space",
                "mobility_space", "tau_space", "stability_safety", "ledger_tolerance"]
    tests = [ast.unparse(n.test) for n in post.body if isinstance(n, ast.If)]
    if positive != expected or not any(isinstance(n, ast.Compare) and ast.unparse(n) ==
            "float(getattr(self, name)) <= 0.0" for n in ast.walk(loops[0])):
        raise ValueError("strict positive domain changed")
    for condition in ("self.a_space < 0.0", "self.coupling_g < 0.0"):
        if condition not in tests:
            raise ValueError("nonnegative space/coupling domain changed")
    if any("self.a_matter" in value for value in tests):
        raise ValueError("a_matter domain changed")
    return {"positive": positive, "nonnegative": ["a_space", "coupling_g"],
            "a_matter": "finite real; no sign restriction", "homogeneous_gradients": 0}


def source_law(text=None):
    text = text if text is not None else (ROOT/CORE).read_text(encoding="utf-8")
    f = u.functions(text)
    env = {"C": C, "Phi": Phi, "lap_C": 0, "lap_Phi": 0,
           "state.space_rate": Pi, "matter_drive": JC, "space_drive": JP}
    names = {"a_matter": a, "b_matter": b, "a_space": alpha, "b_space": beta,
             "coupling_g": g, "mobility_matter": mc, "mobility_space": mf,
             "tau_space": tau, "kappa_matter": s.Symbol("kappa_C", positive=True),
             "kappa_space": s.Symbol("kappa_Phi", positive=True)}
    env.update({"config."+name: value for name, value in names.items()})
    mu = f["matter_space_chemical_potentials"]
    mu_c = u.expression(u.assignment(mu.body, "mu_C"), env)
    mu_p = u.expression(u.assignment(mu.body, "mu_Phi"), env)
    env.update(mu_matter=mu_c, mu_space=mu_p)
    rhs = f["matter_space_rhs"]
    branches = [n for n in rhs.body if isinstance(n, ast.If) and n.orelse
                and ast.unparse(n.test) == "config.matter_dynamics == 'conserved'"]
    if len(branches) != 1:
        raise ValueError("nonconserved branch ambiguous")
    drift = s.Matrix([u.expression(u.assignment(branches[0].orelse, "dC"), env),
                      u.expression(u.assignment(rhs.body, "dPhi"), env),
                      u.expression(u.assignment(rhs.body, "dPi"), env)])
    potential = u.expression(u.assignment(f["matter_space_free_energy"].body, "local_density"), env)
    return potential, s.Matrix([mu_c, mu_p]), drift


def validate_parameters(values):
    if len(values) != len(PARAMS):
        raise ValueError("eight exact coefficients required")
    values = tuple(s.sympify(x) for x in values)
    if any(x.has(s.Float) or x.is_finite is not True or x.is_real is not True for x in values):
        raise ValueError("use finite exact real coefficients, not floating diagnostics")
    aa, bb, al, be, gg, mmc, mmf, tt = values
    if not all(x > 0 for x in (bb, be, mmc, mmf, tt)) or al < 0 or gg < 0:
        raise ValueError("outside canonical domain; in particular a_space<0 is forbidden")
    return values


def regime(values):
    """Exact decision tree; it does not search for roots or select parameters."""
    aa, bb, al, be, gg, *_ = validate_parameters(values)
    A, B = gg**2/(2*bb)-al, gg*aa/(2*bb)
    delta = s.factor(4*A**3-27*be*B**2)
    if gg == 0:
        name = "decoupled_pair" if aa < 0 else "decoupled_origin"
        positive = 0  # nonzero states here have Phi=0, not a positive-Phi root
        minimum_pairs = int(aa < 0)
        origin_min = aa >= 0
    elif aa < 0:
        name, positive, minimum_pairs, origin_min = "one_nonzero_pair", 1, 1, False
    elif aa == 0:
        name = "critical_pair" if A > 0 else "critical_origin"
        positive, minimum_pairs, origin_min = int(A > 0), int(A > 0), A <= 0
    elif A > 0 and delta > 0:
        name, positive, minimum_pairs, origin_min = "coexistence", 2, 1, True
    elif A > 0 and delta == 0:
        name, positive, minimum_pairs, origin_min = "saddle_node_boundary", 1, 0, True
    else:
        name, positive, minimum_pairs, origin_min = "origin_only", 0, 0, True
    return {"regime": name, "A": str(A), "B": str(B), "discriminant_numerator": str(delta),
            "positive_Phi_roots_distinct": positive, "nonzero_minimum_pairs": minimum_pairs,
            "origin_is_strict_minimum": bool(origin_min),
            "origin_nonhyperbolic": bool(origin_min and (aa == 0 or al == 0)),
            "root_search": False}


@lru_cache(maxsize=1)
def algebra():
    potential = a*C**2/2+b*C**4/4+alpha*Phi**2/2+beta*Phi**4/4-g*C**2*Phi/2
    force = s.Matrix([s.diff(potential, C), s.diff(potential, Phi)])
    drift = s.Matrix([-mc*force[0]+JC, Pi, (-Pi-mf*force[1]+JP)/tau])
    Hess = s.hessian(potential, (C, Phi))
    A, B = g**2/(2*b)-alpha, g*a/(2*b)
    cubic = beta*Phi**3-A*Phi+B
    valley = alpha*Phi**2/2+beta*Phi**4/4-(g*Phi-a)**2/(4*b)
    L = s.Matrix([[-mc*k, mc*v, 0], [0, 0, 1], [mf*v/tau, -mf*h/tau, -1/tau]])
    ports = s.Matrix([[1, 0], [0, 0], [0, 1/tau]])
    readouts = s.Matrix([[1, 0, 0], [2*cstar, 0, 0], [0, 1, 0], [0, 0, 1]])
    denominator = (z+mc*k)*(tau*z**2+z+mf*h)-mc*mf*v**2
    transfer = s.Matrix([[tau*z**2+z+mf*h, mc*v],
                         [2*cstar*(tau*z**2+z+mf*h), 2*cstar*mc*v],
                         [mf*v, z+mc*k], [mf*v*z, z*(z+mc*k)]])/denominator
    energy = s.Matrix([[k, -v, 0], [-v, h, 0], [0, 0, tau/mf]])
    loss_c = s.Matrix([[k, -v, 0]])
    loss_pi = s.Matrix([[0, 0, 1]])
    return {"potential": potential, "force": force, "drift": drift, "Hessian": Hess,
            "A": A, "B": B, "cubic": cubic, "valley": valley, "L": L, "ports": ports,
            "readouts": readouts, "D": denominator, "T": transfer, "energy": energy,
            "loss_c": loss_c, "loss_pi": loss_pi}


def integrate_polynomial(expr):
    return s.factor(sum(coef/s.Integer(power[0]+1) for power, coef in s.Poly(s.expand(expr), t).terms()))


@lru_cache(maxsize=1)
def write_algebra():
    S = 10*t**3-15*t**4+6*t**5
    rate, acceleration = s.diff(S, t)/Tw, s.diff(S, t, 2)/Tw**2
    mu_c_reduced = a*S+b*X*S**3-g*Y*S**2
    mu_phi = alpha*Y*S+beta*Y**3*S**3-g*X*S**2/2
    pi = Y*rate
    jc_reduced = rate+mc*mu_c_reduced
    jp = tau*Y*acceleration+pi+mf*mu_phi
    energy = (a*X*S**2/2+b*X**2*S**4/4+alpha*Y**2*S**2/2+beta*Y**4*S**4/4
              -g*X*Y*S**3/2+tau*pi**2/(2*mf))
    dissipation = mc*X*mu_c_reduced**2+pi**2/mf
    power = X*mu_c_reduced*jc_reduced+pi*jp/mf
    return {"S": S, "rate": rate, "acceleration": acceleration, "mu_C_over_Ci": mu_c_reduced,
            "mu_Phi": mu_phi, "Pi": pi, "J_C_over_Ci": jc_reduced, "J_Phi": jp,
            "energy": energy, "dissipation": dissipation, "power": power,
            "integrated_dissipation": s.factor(Tw*integrate_polynomial(dissipation)),
            "integrated_work": s.factor(Tw*integrate_polynomial(power))}


@lru_cache(maxsize=1)
def controls():
    aa = algebra(); subs = dict(zip(PARAMS, COEX)); root = s.sqrt(13)
    ys = [-(root+1)/4, s.Rational(1, 2), (root-1)/4]
    branches = []
    for yy in ys:
        xx = s.simplify((g*Phi-a).subs(subs).subs(Phi, yy)/subs[b])
        admissible = bool(xx > 0 and yy > 0)
        det = s.simplify((2*b*((g*Phi-a)/b)*s.diff(aa["cubic"], Phi)).subs(subs).subs(Phi, yy))
        branches.append({"Phi": str(yy), "C_squared": str(xx), "admissible": admissible,
                         "hessian_det": str(det), "disposition": "inadmissible" if not admissible else
                         "strict_minimum_pair" if det > 0 else "saddle_pair"})
    high = ys[-1]; xx = s.simplify((2*high-s.Rational(3, 8)))
    hh = s.simplify(1+3*high**2); kk=2*xx; vv2=4*xx
    det=s.simplify(kk*hh-vv2)
    gain=s.simplify(hh/det); zero_gain=s.Rational(8, 3)
    delta_e=s.simplify(aa["valley"].subs(subs).subs(Phi, high))
    wp=write_algebra(); write_sub={**subs, X:xx, Y:high, Tw:s.Integer(1)}
    loss=s.simplify(wp["integrated_dissipation"].subs(write_sub))
    work=s.simplify(wp["integrated_work"].subs(write_sub))
    return {"coexistence": regime(COEX), "noncoexistence": regime(SINGLE), "branches": branches,
            "high_Phi": high, "high_C_squared": xx, "high_det": det,
            "high_h": hh, "high_C_JC_DC_gain": gain, "origin_C_JC_DC_gain": zero_gain,
            "gain_difference": s.simplify(gain-zero_gain), "final_energy_difference": delta_e,
            "write_dissipation": loss, "write_work": work,
            "saddle_Phi": s.Rational(1, 2)}


def inherited_u_check():
    old=load_json(ROOT/U_ARTIFACT)
    if old.get("old_producers_rerun") is not False or old.get("physical_acceptance") is not False:
        raise ValueError("U scope changed; review before reuse")
    aa=algebra(); cc, rr=s.symbols("c r", positive=True)
    expected=s.Matrix([[s.sympify(x, locals={"c":cc,"r":rr,"z":z}) for x in row]
                       for row in old["exact_response"]["positive_branch"]])
    substituted=aa["T"].subs({mc:1,mf:1,tau:1,k:2*cc**2,h:1+3*rr**2,v:cc,cstar:cc})
    if not equal(substituted,expected):
        raise ValueError("general response fails to recover U")
    return {"path":U_ARTIFACT, "rerun":False, "response_recovered":True,
            "scope":"same-Phi signed pair, separate readout and one port at a time; no mixed-protocol extension"}


@lru_cache(maxsize=1)
def symbolic_checks():
    aa, w, ctl = algebra(), write_algebra(), controls()
    sp=s.Symbol("Phi_d", positive=True)
    stat_c2=(g*Phi-a)/b
    # Substitution C^2=X avoids introducing a spurious negative-square root.
    force_phi=s.expand(aa["force"][1]).subs(C**2, stat_c2)
    full_det=s.expand(aa["Hessian"].det()).subs(C**4, stat_c2**2).subs(C**2, stat_c2)
    loss=mc*aa["loss_c"].T*aa["loss_c"]+aa["loss_pi"].T*aa["loss_pi"]/mf
    dc=aa["T"].extract([0,2],[0,1]).subs(z,0)
    H=s.Matrix([[k,-v],[-v,h]])
    readout=s.Matrix([C,C**2,Phi,Pi]).jacobian([C,Phi,Pi])
    endpoint_force=s.Matrix([a+b*X-g*Y, alpha*Y+beta*Y**3-g*X/2])
    high_sub=dict(zip(PARAMS,COEX)); high_sub.update({X:ctl["high_C_squared"],Y:ctl["high_Phi"]})
    E=aa["potential"]+tau*Pi**2/(2*mf)
    ledger=-mc*aa["force"][0]**2-Pi**2/mf+aa["force"][0]*JC+Pi*JP/mf
    jac=aa["drift"].jacobian([C,Phi,Pi])
    written_drift=aa["drift"].subs({C:cstar*w["S"],Phi:Y*w["S"],Pi:w["Pi"],
        JC:cstar*w["J_C_over_Ci"],JP:w["J_Phi"]},simultaneous=True).subs(X,cstar**2)
    lifted=s.Matrix([[-mc*aa["Hessian"][0,0],-mc*aa["Hessian"][0,1],0],
                     [0,0,1],[-mf*aa["Hessian"][1,0]/tau,-mf*aa["Hessian"][1,1]/tau,-1/tau]])
    return {
        "source_mu_and_potential_from_same_generator": equal(source_law()[0],aa["potential"]) and equal(source_law()[1],aa["force"]),
        "canonical_homogeneous_rhs": equal(source_law()[2],aa["drift"]),
        "source_domain_preserved": source_domain()["nonnegative"]==["a_space","coupling_g"],
        "origin_kept_before_dividing_C": equal(aa["force"].subs({C:0,Phi:0}),s.zeros(2,1)),
        "stationary_cubic_is_original_Phi_force": equal(force_phi,aa["cubic"]),
        "nonzero_Hessian_CC_is_2bC_squared": equal(aa["Hessian"][0,0].subs(C**2,stat_c2),2*b*stat_c2),
        "full_Hessian_determinant_is_2bC_squared_pprime": equal(full_det,2*b*stat_c2*s.diff(aa["cubic"],Phi)),
        "cubic_discriminant_not_used_without_admissibility": equal(s.discriminant(aa["cubic"],Phi),beta*(4*aa["A"]**3-27*beta*aa["B"]**2)) and not ctl["branches"][0]["admissible"],
        "admissible_positive_root_equivalence": equal(stat_c2-2*Phi*(alpha+beta*Phi**2)/g,-2*aa["cubic"]/g),
        "static_valley_derivative_not_dynamic_law": equal(s.diff(aa["valley"],Phi),aa["cubic"]),
        "critical_complete_square": equal(aa["potential"].subs(a,0), b*(C**2-g*Phi/b)**2/4-aa["A"]*Phi**2/2+beta*Phi**4/4),
        "saddle_node_has_nonzero_cubic_leading_term": equal(s.diff(aa["valley"],Phi,3).subs(Phi,sp)/6,beta*sp),
        "alpha_zero_origin_has_local_positive_bound": equal(aa["potential"].subs(alpha,0)-(a*C**2/4+b*C**4/4+beta*Phi**4/4), C**2*(a/4-g*Phi/2)),
        "full_jacobian_from_old_RHS": equal(jac,lifted),
        "source_ports_include_tau": equal(aa["drift"].jacobian([JC,JP]),aa["ports"]),
        "readouts_are_baseline_derivatives": equal(readout.subs(C,cstar),aa["readouts"]),
        "full_resolvent_equals_eliminated_transfer": equal(aa["readouts"]*(z*s.eye(3)-aa["L"]).inv()*aa["ports"],aa["T"]),
        "characteristic_denominator_has_tau_factor": equal((z*s.eye(3)-aa["L"]).det(),aa["D"]/tau),
        "negative_Hessian_det_implies_positive_real_pole": equal(aa["D"].subs(z,0),mc*mf*(k*h-v**2)) and s.Poly(aa["D"],z).LC()==tau,
        "DC_is_Hessian_inverse_with_source_mobilities": equal(dc,H.inv()*s.diag(1/mc,1/mf)),
        "zero_nonzero_CJC_transfer_difference": equal(aa["T"][0,0]-1/(z+mc*a),
            mc*((a-k)*(tau*z**2+z+mf*h)+mf*v**2)/(aa["D"]*(z+mc*a))),
        "quadratic_energy_stability_identity": equal(aa["L"].T*aa["energy"]+aa["energy"]*aa["L"],-2*loss),
        "zero_loss_mode_excluded_when_Hessian_SPD": equal(s.Matrix.vstack(aa["loss_pi"],aa["L"][2,:],aa["loss_c"]).det(),mf*(k*h-v**2)/tau),
        "signed_pair_symmetry_includes_sources_readouts": equal(aa["T"].subs({v:-v,cstar:-cstar}, simultaneous=True),s.diag(-1,1,1,1)*aa["T"]*s.diag(-1,1)),
        "U_response_recovered_without_old_producer": inherited_u_check()["response_recovered"],
        "coexistence_control_exact_factorization": equal(aa["cubic"].subs(dict(zip(PARAMS,COEX))), (2*Phi-1)*(4*Phi**2+2*Phi-3)/8),
        "coexistence_roots_satisfy_original_pair": all(equal(x,0) for x in endpoint_force.subs(high_sub)),
        "two_controls_have_different_classification": ctl["coexistence"]["regime"]=="coexistence" and ctl["noncoexistence"]["regime"]=="origin_only",
        "gain_contrast_is_not_only_baseline": equal(ctl["gain_difference"],(1376*s.sqrt(13)-1196)/2067) and 344**2*13>299**2,
        "positive_high_branch_energy_not_equal_energy": equal(ctl["final_energy_difference"],(-83+26*s.sqrt(13))/256) and 26**2*13>83**2,
        "algebraic_minimum_has_positive_Hessian": equal(ctl["high_det"],(73*s.sqrt(13)-247)/32) and 73**2*13>247**2,
        "full_state_pointwise_energy_ledger": equal(s.Matrix([s.diff(E,x) for x in [C,Phi,Pi]]).dot(aa["drift"]),ledger),
        "quintic_endpoint_state_rate_acceleration": all(equal(s.diff(w["S"],t,n).subs(t,j), int(n==0 and j==1)) for n in [0,1,2] for j in [0,1]),
        "prescribed_write_satisfies_full_RHS": equal(written_drift,s.Matrix([cstar*w["rate"],w["Pi"],Y*w["acceleration"]])),
        "write_inputs_and_endpoint_sources": equal(w["J_C_over_Ci"].subs(t,0),0) and equal(w["J_Phi"].subs(t,0),0) and equal(w["J_C_over_Ci"].subs(t,1),mc*endpoint_force[0]) and equal(w["J_Phi"].subs(t,1),mf*endpoint_force[1]),
        "write_path_pointwise_ledger": equal(s.diff(w["energy"],t)/Tw+w["dissipation"]-w["power"],0),
        "independently_integrated_write_balance": equal(w["integrated_work"]-w["integrated_dissipation"], w["energy"].subs(t,1)-w["energy"].subs(t,0)),
        "positive_Pi_loss_for_nonzero_target": equal(Tw*integrate_polynomial(w["Pi"]**2/mf),10*Y**2/(7*mf*Tw)),
        "exact_regression_write_balance": equal(ctl["write_work"]-ctl["write_dissipation"],ctl["final_energy_difference"]),
        "zero_target_has_zero_work_loss": equal(w["integrated_work"].subs({X:0,Y:0}),0) and equal(w["integrated_dissipation"].subs({X:0,Y:0}),0),
    }


def protocol():
    return {"same_coefficients_for_histories":True,"ports_applied_separately":True,
            "baseline_subtracted":True,"primary_readout":"C","response":"infinitesimal_at_SPD_minimum",
            "physical_acceptance":False,"lifetime_claim":False,"topology_learning":False,"new_UET_discriminator":False,
            "absolute_C_derivative_at_origin":False,"static_elimination_as_dynamics":False,
            "zero_gain_relative_error":False,"write_clock":"normalized; T_w>0, regression T_w=1 not one second"}


def validate_protocol(p):
    if p != protocol():
        raise ValueError("locked response/write/comparator scope changed")


def validate_history_coefficients(left, right):
    left, right = validate_parameters(left), validate_parameters(right)
    if left != right:
        raise ValueError("different source coefficients are external retuning, not written state")


def rejected(call):
    try:
        call()
    except ValueError:
        return True
    return False


def negative_controls():
    aa=algebra(); ctl=controls(); hp=aa["T"]
    flips=["same_coefficients_for_histories","ports_applied_separately","baseline_subtracted",
           "physical_acceptance","lifetime_claim","topology_learning","new_UET_discriminator","absolute_C_derivative_at_origin",
           "static_elimination_as_dynamics","zero_gain_relative_error"]
    bads={}
    for key in flips:
        p=protocol();p[key]=not p[key]
        bads[key+"_scope_guard"]=rejected(lambda p=p:validate_protocol(p))
    d=list(COEX);d[2]=-1
    retuned=list(COEX);retuned[4]+=1
    bads.update({
        "negative_a_space_rejected": rejected(lambda:validate_parameters(d)),
        "actual_history_coefficient_retuning_rejected": rejected(lambda:validate_history_coefficients(COEX,retuned)),
        "negative_square_root_not_admitted": not ctl["branches"][0]["admissible"],
        "baseline_difference_not_a_gain_proof": not equal(cstar,-cstar) and equal(hp[0,0].subs(v,-v),hp[0,0]),
        "missing_source_mobility_changes_DC": not equal(hp[0,0].subs(z,0),h/(k*h-v**2)),
        "missing_source_tau_changes_resolvent": not equal(aa["readouts"]*(z*s.eye(3)-aa["L"]).inv()*s.Matrix([[1,0],[0,0],[0,1]]),hp),
        "static_response_cannot_replace_frequency_response": not equal(hp[0,0],hp[0,0].subs(z,0)),
        "instantaneous_Phi_elimination_changes_response": not equal(hp[0,0],1/(z+mc*(k-v**2/h))),
        "origin_squared_readout_derivative_is_zero": s.diff(C**2,C).subs(C,0)==0,
        "origin_absolute_readout_one_sided_derivatives_disagree": s.limit(s.Abs(C)/C,C,0,dir="+") != s.limit(s.Abs(C)/C,C,0,dir="-"),
        "omitted_C_squared_readout_factor_changes_transfer": not equal(hp[1,0],hp[0,0]),
        "wrong_JPhi_work_normalization_breaks_ledger": not equal(Pi*JP/mf,Pi*JP),
        "higher_local_minimum_is_not_global": equal(ctl["final_energy_difference"],(-83+26*s.sqrt(13))/256) and 26**2*13>83**2,
        "quintic_is_not_infinitely_smooth_after_extension": s.diff(write_algebra()["S"],t,3).subs(t,0)!=0,
    })
    return bads


def strings(value):
    if isinstance(value,s.MatrixBase):return [[str(x) for x in row] for row in value.tolist()]
    if isinstance(value,s.Basic):return str(value)
    if isinstance(value,dict):return {key:strings(x) for key,x in value.items()}
    if isinstance(value,(tuple,list)):return [strings(x) for x in value]
    return value


def calculate():
    # Re-read actual source even if the pure symbolic algebra is cached.
    domain=source_domain()
    validate_history_coefficients(COEX,COEX)
    if not equal(source_law()[2],algebra()["drift"]):raise ValueError("canonical RHS differs")
    checks, neg=symbolic_checks(),negative_controls()
    if not all(checks.values()) or not all(neg.values()):
        raise ValueError("exact audit failed: "+str([key for key,value in {**checks,**neg}.items() if not value]))
    aa, ctl, w=algebra(),controls(),write_algebra()
    inherited=inherited_u_check()
    rows=[
        ["g=0,a>=0","origin strict global min; nonhyperbolic if a=0 or alpha=0"],
        ["g=0,a<0","signed global-minimum pair, Phi=0; alpha=0 gives nonhyperbolic minima"],
        ["g>0,a<0","one positive-Phi root, signed SPD global-minimum pair; origin unstable"],
        ["g>0,a=0,A<=0","origin unique strict global min, degenerate"],
        ["g>0,a=0,A>0","Phi=sqrt(A/beta), signed SPD global minima; origin not minimum"],
        ["g>0,a>0; A<=0 or Delta<0","origin only minimum"],
        ["g>0,a>0,A>0,Delta=0","origin min plus positive double-root pair, not minima (cubic leading term)"],
        ["g>0,a>0,A>0,Delta>0","origin min, smaller-positive-root saddle pair, larger-positive-root SPD minimum pair"],
    ]
    return strings({"source_baseline_commit":BASELINE,"sympy_version":s.__version__,
        "protocol":protocol(),"source_domain":domain,"checks":checks,"negative_controls":neg,
        "classification":{"A":aa["A"],"B":aa["B"],"p":aa["cubic"],"rows":rows,
            "nonzero_admissibility":"g>0 requires Phi>0 and C^2=(g*Phi-a)/b>0; g=0 handled separately",
            "Hessian_rule":"H_CC=2*b*C^2; det(H)=2*b*C^2*p'(Phi)",
            "global_rule":"coercive quartic; compare V_high=alpha*Phi_high^2/2+beta*Phi_high^4/4-(g*Phi_high-a)^2/(4*b) with 0; sign decides global minima, not noise lifetime",
            "degenerate_boundaries":"leading energy terms, not zero-eigenvalue rejection; alpha=0 origin can be strict nonlinear minimum"},
        "exact_controls":{"coexistence_parameters":dict(zip([str(x) for x in PARAMS],COEX)),
            "noncoexistence_parameters":dict(zip([str(x) for x in PARAMS],SINGLE)),**ctl},
        "response":{"L":aa["L"],"B":aa["ports"],"K":aa["readouts"],"D":aa["D"],"transfer":aa["T"],
            "DC_rows_C_Phi":aa["T"].extract([0,2],[0,1]).subs(z,0),
            "denominator_domain":"det(zI-L)=D/tau; no poles Re(z)>=0 for k>0,kh-v^2>0 by quadratic energy and full-rank zero-loss witness; not applied to degenerate edges",
            "origin_cross_gain":0,"nonzero_cross_gain":"M_C*g*C_star/D(z); DC=g*C_star/[M_Phi*det(H)]",
            "coexistence_comparison_domain":"a>0,alpha>0,A>0,Delta>0 for origin and high branch both SPD; C/J_Phi DC zero versus nonzero; C/J_C DC differs iff a*h_high!=det(H_high), no universal ordering/frequency claim",
            "absolute_readout":"abs(C) is not differentiable at origin; modulus of transfer is a separate comparison"},
        "write":{"common_start":[0,0,0],"S":w["S"],"J_C_over_Ci":w["J_C_over_Ci"],"J_Phi":w["J_Phi"],
            "integrated_dissipation":w["integrated_dissipation"],"integrated_work":w["integrated_work"],
            "scope":"finite exact polynomial reachability under both old write ports; sources continuous to zero at stationary endpoints, not C-infinity; no apparatus/preparation/lifetime claim",
            "regression_zero_target":{"work":0,"dissipation":0,"final_energy":0},
            "unequal_energy_and_cost_reported":True},"U_reuse":inherited,
        "comparator":"EQUIVALENT: same quartic generator, mixed gradient/inertial dynamics, sources and readouts as standard nonlinear multistable comparator; no UET-specific constraint added",
        "physical_acceptance":False,"new_model_terms":0,"parameter_sweeps":0,"numerical_roots":0,
        "trajectories":0,"old_producers_rerun":False,"physics_gates_changed":False,
        "new_UET_discriminator":False,"structural_topology_learning_proved":False,
        "next_controller":"physical-parent-preparation unchanged; quantum-parent-correspondence remains separate. A sourced restriction/readout/preparation that distinguishes the existing comparator is needed before a new physical or structural-learning claim; no automatic next wave."})


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT),ROOT),**calculate()}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--check",action="store_true",help="read-only exact checks and artifact comparison")
    mode.add_argument("--emit-report",action="store_true",help="write this artifact only")
    args=parser.parse_args(argv)
    result=record();payload=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(payload,encoding="utf-8",newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes()!=payload.encode("utf-8"):
        raise ValueError("artifact missing/stale; review before explicit --emit-report")
    print(json.dumps({"checks":len(result["checks"]),"negative_controls":len(result["negative_controls"]),
                      "review":result["contract_review_status"],"physical_acceptance":False}))
    return 0


if __name__=="__main__":raise SystemExit(main())
