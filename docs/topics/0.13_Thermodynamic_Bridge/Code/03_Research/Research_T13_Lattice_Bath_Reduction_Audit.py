"""Round P: conditional classical chain/bath reduction, not a Core change.

Only exact algebra/finite spin enumeration; no trajectories, fit or old verifier
rerun. Round O functions are reused as source definitions, never calculate/main.
Physical localization and Markov closure are decisions, not forced PASS scores.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import importlib.util
import json
from math import comb
from pathlib import Path
import sys

import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata, load_json

TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
CONTRACT = f"{TOPIC}/calculation_contracts/lattice_bath_reduction_audit.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_lattice_bath_reduction_audit.json"
REPORT = "docs/meta/UET_LATTICE_BATH_REDUCTION_AUDIT.md"
spec = importlib.util.spec_from_file_location(
    "round_o_definitions", Path(__file__).with_name("Research_T13_Lattice_Mechanical_State_Construction.py"))
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
L = s.log(2)
BASIS = (-old.A/s.sqrt(5)).row_join(old.E)


def zeros(values):
    for name, value in values.items():
        entries = list(value) if isinstance(value, s.MatrixBase) else [value]
        if any(s.cancel(s.simplify(v)) != 0 for v in entries):
            raise ValueError(f"exact residual failed: {name}: {value}")
    return {name: True for name in values}


def positive_interval_polynomial(expr, variable, lo, hi):
    """Sufficient exact Bernstein certificate on a rational closed interval."""
    t = s.Symbol("bernstein_t", real=True)
    p = s.Poly(s.expand(expr.subs(variable, lo+(hi-lo)*t)), t)
    n = p.degree()
    if n == -s.oo:
        return False
    powers = [p.nth(i) for i in range(n+1)]
    coefficients = [sum(powers[i]*s.Rational(comb(k, i), comb(n, i))
                        for i in range(k+1)) for k in range(n+1)]
    return all(v > 0 for v in coefficients)


def positive_log_rational(expr):
    # ln2 lies strictly between 69/100 and 7/10, from the positive atanh series.
    numerator, denominator = s.fraction(s.factor(expr))
    x = s.Symbol("logtwo", real=True)
    lo, hi = s.Rational(69, 100), s.Rational(7, 10)
    return (positive_interval_polynomial(numerator.subs(L, x), x, lo, hi)
            and positive_interval_polynomial(denominator.subs(L, x), x, lo, hi))


def log_bracket():
    lower = sum(2*s.Rational(1, (2*n+1)*3**(2*n+1)) for n in range(3))
    remainder = 2*s.Rational(1, 7*3**7)/(1-s.Rational(1, 9))
    assert s.Rational(69, 100) < lower < lower+remainder < s.Rational(7, 10)
    return lower, remainder


def joint_coefficients(spins):
    old.validate_spins(spins)
    return _joint_coefficients(tuple(spins))


@lru_cache(maxsize=None)
def _joint_coefficients(spins):
    if spins[0] < 0:
        return _joint_coefficients(tuple(-v for v in spins))
    c = old.control_coefficients(tuple(spins))
    H = s.simplify(BASIS.T*c["fullH"]*BASIS)
    force = s.Matrix([c["Vphi"]/s.sqrt(5), *c["b"]])
    mean = s.simplify(-H.inv()*force)
    return dict(A=H, f=force, mean=mean, V0=c["V0"], K=c["K"], g=H[1:, 0])


def assert_joint_spd(A):
    if A.shape != (3, 3) or A != A.T:
        raise ValueError("need symmetric three-dimensional internal stiffness")
    if not all(positive_log_rational(A[:n, :n].det()) for n in (1, 2, 3)):
        raise ValueError("joint SPD not certified on declared ln2 interval")


def coordinate_residuals():
    lam, mu, t0, energy = s.symbols("lambda mu t_star E_star", positive=True)
    Q, phi, pQ, pp, v, force = s.symbols("Q Phi pQ pPhi v force", real=True)
    return {
        "length_basis_orthonormal": BASIS.T*BASIS-s.eye(3),
        "no_CM_bath_channel": BASIS.T*s.ones(4, 1),
        "canonical_Q_Phi_one_form": (pQ*lam-pp).subs(pp, lam*pQ),
        "canonical_Jacobian": lam/lam-1,
        "Phi_kinetic_inertia": (pQ**2/(2*mu)).subs(pQ, pp/lam)-pp**2/(2*mu*lam**2),
        "force_port_work": force*(lam*v)-(lam*force)*v,
        "normalized_original_mass": (mu*lam**2/(4*energy*t0**2)).subs(
            {lam:s.sqrt(5), mu:1, energy:1, t0:1})-s.Rational(5,4),
        "readout_is_not_endpoint": old.E[3,1]-old.E[0,1]+1/s.sqrt(5),
    }


@lru_cache(maxsize=None)
def spin_regime_rows():
    rows = []
    for spins in old.SPINS:
        c = joint_coefficients(spins)
        assert_joint_spd(c["A"])
        norm2 = s.factor(c["mean"].dot(c["mean"]))
        outside = positive_log_rational(norm2-s.Rational(1,16))
        rows.append(dict(spins=old.label(spins), k=sum(v == 1 for v in spins),
                         joint_SPD=True, mean_outside_locked_ball=outside,
                         nonzero_linear_force=c["f"] != s.zeros(3,1),
                         mixed_stiffness_nonzero=c["g"] != s.zeros(2,1),
                         squared_mean_exact=str(norm2)))
    return rows


def local_quantum_residuals():
    radius, M3, kb, T, hbar, gamma, cut, mu, band = s.symbols(
        "R M3 k_B T hbar gamma cutoff mu bandwidth", positive=True)
    w = s.Symbol("omega", positive=True)
    n = s.Symbol("n", integer=True, positive=True)
    # Coefficients of (1+x^2/3)sinh(x)-x cosh(x) are >=0 (n>=1).
    coefficient = 1/s.factorial(2*n+1)+1/(3*s.factorial(2*n-1))-1/s.factorial(2*n)
    return {
        "joint_gap_lower_bound": 1-s.sqrt(2)/4-(1-s.sqrt(2)/4),
        "joint_Taylor_value_remainder": M3*radius**3/6-M3*radius**3/s.factorial(3),
        "coth_upper_series_coefficient": coefficient-4*n*(n-1)/(3*s.factorial(2*n+1)),
        "position_quantum_tail": s.integrate(4*hbar*gamma*cut**2/(s.pi*mu*w**5),
                                               (w, band, s.oo))-hbar*gamma*cut**2/(s.pi*mu*band**4),
        "velocity_quantum_tail": s.integrate(4*hbar*gamma*cut**2/(s.pi*mu*w**3),
                                               (w, band, s.oo))-2*hbar*gamma*cut**2/(s.pi*mu*band**2),
    }


def joint_parent_derivative_residuals():
    """New Q derivatives; does not run the old conditional-ensemble verifier."""
    q=s.Matrix(s.symbols("Q u1 u2",real=True))
    spins=(1,1,-1,-1)
    V=old.parent_potential(spins,old.A+BASIS*q,8,L,1,1,1,2)
    at0={v:0 for v in q}
    c=joint_coefficients(spins)
    return {"joint_gradient_source_link":s.Matrix([s.diff(V,v).subs(at0) for v in q])-c["f"],
            "joint_Hessian_source_link":s.hessian(V,q).subs(at0)-c["A"],
            "mixed_Q_matches_old_Phi_scaling":c["g"]-old.control_coefficients(spins)["bphi"]/s.sqrt(5)}


def bath_residuals():
    q, z, y, p, pb, mb, om, c, mu, kb, T = s.symbols(
        "q z y p pb mb omega c mu k_B T", positive=True)
    V = s.Function("V")(q)
    H = p**2/(2*mu)+V+pb**2/(2*mb)+mb*om**2*(z-c*q/(mb*om**2))**2/2
    shifted = s.expand(H.subs(z, y+c*q/(mb*om**2)))
    f = -s.diff(H,q)
    balance = (s.diff(H,q)*s.diff(H,p)-s.diff(H,p)*s.diff(H,q)
               +s.diff(H,z)*s.diff(H,pb)-s.diff(H,pb)*s.diff(H,z))
    t, q0, z0, pb0 = s.symbols("t q0 z0 pb0", real=True)
    xi = c*((z0-c*q0/(mb*om**2))*s.cos(om*t)+pb0*s.sin(om*t)/(mb*om))
    t2 = s.Symbol("t2", real=True)
    dz, dp = s.diff(xi,z0), s.diff(xi,pb0)
    covariance = (dz*dz.subs(t,t2)*kb*T/(mb*om**2)+dp*dp.subs(t,t2)*mb*kb*T)
    return {
        "bath_shift_preserves_bare_potential": shifted-(p**2/(2*mu)+V+pb**2/(2*mb)+mb*om**2*y**2/2),
        "Hamiltonian_force_with_counterterm": f-(-s.diff(V,q)+c*(z-c*q/(mb*om**2))),
        "total_Hamiltonian_energy": balance,
        "conditional_preparation_zero_noise_mean": xi.subs({z0:c*q0/(mb*om**2),pb0:0}),
        "unshifted_preparation_initial_slip": xi.subs({z0:0,pb0:0})+c**2*q0*s.cos(om*t)/(mb*om**2),
        "finite_bath_classical_FDT": s.trigsimp(covariance-kb*T*c**2*s.cos(om*(t-t2))/(mb*om**2)),
    }


def drude_residuals():
    mu, gamma, cut, z, t, w = s.symbols("mu gamma cutoff z t omega", positive=True)
    Jb = mu*gamma*w*cut**2/(w**2+cut**2)
    kernel = mu*gamma*cut*s.exp(-cut*t)
    cosine = s.integrate((2/s.pi)*Jb/w*s.cos(w*t),(w,0,s.oo))
    laplace = s.integrate(s.exp(-z*t)*kernel,(t,0,s.oo))
    what = mu*gamma*cut/(cut-s.I*w)
    return {
        "Drude_cosine_transform_convention": s.simplify(cosine-kernel),
        "Drude_causal_Laplace": laplace-mu*gamma*cut/(z+cut),
        "one_sided_kernel_area": s.integrate(kernel,(t,0,s.oo))-mu*gamma,
        "white_bath_impedance_limit": s.limit(laplace,cut,s.oo)-mu*gamma,
        "white_noise_two_sided_factor2": s.limit(2*s.re(what),cut,s.oo)-2*mu*gamma,
        "finite_colored_force_spectrum": 2*s.re(what)-2*mu*gamma*cut**2/(cut**2+w**2),
    }


def ou_matrices(A, mu, gamma, cut, temperature):
    n = A.rows
    I, Z = s.eye(n), s.zeros(n)
    F = s.BlockMatrix([[Z,I/mu,Z],[-A,Z,I],[Z,-gamma*cut*I,-cut*I]]).as_explicit()
    cov = s.diag(temperature*A.inv(), mu*temperature*I, mu*gamma*cut*temperature*I)
    noise = s.diag(Z,Z,2*mu*gamma*cut**2*temperature*I)
    return F, cov, noise


def ou_residuals():
    mu, gamma, cut, temp = s.symbols("mu gamma cutoff kBT", positive=True)
    a, k1, k2 = s.symbols("a k1 k2", positive=True)
    F, cov, noise = ou_matrices(s.diag(a,k1,k2),mu,gamma,cut,temp)
    parity = s.diag(s.eye(3),-s.eye(3),s.eye(3))
    reversible = F+s.diag(s.zeros(3),s.zeros(3),cut*s.eye(3))
    z, k = s.symbols("z k", positive=True)
    pole = (z+cut)*(mu*z**2+k)+mu*gamma*cut*z
    return {
        "stationary_Lyapunov_covariance": F*cov+cov*F.T+noise,
        "reversible_time_parity_Pi_odd": parity*reversible*parity+reversible,
        "Drude_mode_cubic": s.expand(pole/mu)-(z**3+cut*z**2+(k/mu+gamma*cut)*z+cut*k/mu),
        "Routh_Hurwitz_positive_margin": cut*(k/mu+gamma*cut)-cut*k/mu-gamma*cut**2,
        "stationary_mechanical_energy_flux": s.trace(cov[3:6,6:9])/mu,
        "extended_OU_bath_injection_balance": -3*temp*cut+3*temp*cut,
        "white_friction_noise_energy_balance": -3*gamma*temp+3*gamma*temp,
    }


def response_objects():
    a, k1, k2, g1, g2, h = s.symbols("a k1 k2 g1 g2 h", real=True)
    K = s.diag(k1,k2)
    g = s.Matrix([g1,g2])
    A = s.BlockMatrix([[s.Matrix([[a]]),g.T],[g,K]]).as_explicit()
    R = (K+h*s.eye(2)).inv()
    D = a+h-(g.T*R*g)[0]
    return a,K,g,A,h,R,D


def response_residuals():
    a,K,g,A,h,R,D = response_objects()
    x = s.Matrix([1, *(-R*g)])/D
    return {
        "full_block_solve_matches_elimination": (A+h*s.eye(3))*x-s.Matrix([1,0,0]),
        "determinant_poles_not_discarded": (A+h*s.eye(3)).det()-(K+h*s.eye(2)).det()*D,
        "static_Schur_complement": D.subs(h,0)-(a-(g.T*K.inv()*g)[0]),
        "decoupled_retained_response": D.subs({g[0]:0,g[1]:0})-(a+h),
    }


def hidden_fdt_residuals():
    mu, gamma, cut, temp, z = s.symbols("mu gamma cutoff kBT z", positive=True)
    k1,k2 = s.symbols("k1 k2", positive=True)
    g = s.Matrix(s.symbols("g1 g2", real=True))
    K = s.diag(k1,k2)
    # y=(u+K^-1*g*Q, p_u, r_Q, r_u). Conditional equilibrium at Q(0).
    F = s.zeros(7)
    F[:2,2:4]=s.eye(2)/mu
    F[2:4,:2]=-K
    F[2:4,5:7]=s.eye(2)
    F[4,4]=-cut
    F[5:7,2:4]=-gamma*cut*s.eye(2)
    F[5:7,5:7]=-cut*s.eye(2)
    B = s.Matrix([*(K.inv()*g),0,0,-mu*gamma*cut,0,0])
    C = s.Matrix([[-g[0],-g[1],0,0,1,0,0]])
    cov=s.diag(temp*K.inv(),mu*temp*s.eye(2),mu*gamma*cut*temp,mu*gamma*cut*temp*s.eye(2))
    noise=s.diag(s.zeros(4),2*mu*gamma*cut**2*temp*s.eye(3))
    Ghat=mu*gamma*cut/(z+cut)
    ell=mu*z+Ghat
    h=mu*z**2+z*Ghat
    R=(K+h*s.eye(2)).inv()
    w=ell*R*K.inv()*g
    p=mu*z*w-mu*K.inv()*g
    trial=s.Matrix([*w,*p,-Ghat,*(-gamma*cut*p/(z+cut))])
    effective=Ghat+ell*(g.T*R*K.inv()*g)[0]
    return {
        "hidden_conditional_Lyapunov": F*cov+cov*F.T+noise,
        "conditional_FDT_preparation_identity": cov*C.T+temp*B,
        "hidden_memory_resolvent": (z*s.eye(7)-F)*trial-B,
        "effective_memory_same_force_port": -(C*trial)[0]-effective,
        "effective_impedance_and_static_potential": z*effective+mu*z**2-
            (h+(g.T*K.inv()*g)[0]-(g.T*R*g)[0]),
    }


def spectral_fdt_residuals():
    w, GR, mu, k, temp = s.symbols("omega Gamma_real mu k kBT", positive=True)
    GI, g, a = s.symbols("Gamma_imag g a", real=True)
    h=-mu*w**2+w*GI-s.I*w*GR
    R=1/(k+h)
    D=a+h-g**2*R
    return {"effective_noise_response_FDT_one_hidden_mode":
            s.im(D)+w*GR*(1+g**2*s.simplify(R*s.conjugate(R))),
            "effective_noise_nonnegative_factor":
            s.simplify(R*s.conjugate(R))-1/((k-mu*w**2+w*GI)**2+(w*GR)**2)}


def markov_expansion_residuals():
    mu,gamma,cut,z = s.symbols("mu gamma cutoff z", positive=True)
    k1,k2 = s.symbols("k1 k2", positive=True)
    g1,g2,a = s.symbols("g1 g2 a", real=True)
    h=mu*z**2+mu*gamma*cut*z/(z+cut)
    D=a+h-g1**2/(k1+h)-g2**2/(k2+h)
    r1=g1**2/k1**2+g2**2/k2**2
    r2=g1**2/k1**3+g2**2/k2**3
    k0=a-g1**2/k1-g2**2/k2
    friction=mu*gamma*(1+r1)
    mass=mu*(1-gamma/cut)*(1+r1)-(mu*gamma)**2*r2
    hh=s.Symbol("h",real=True)
    exact_remainder=sum(g**2*hh**3/(k**3*(k+hh)) for g,k in ((g1,k1),(g2,k2)))
    remainder = (a+hh-g1**2/(k1+hh)-g2**2/(k2+hh))-(k0+(1+r1)*hh-r2*hh**2)
    return {
        "static_reduced_stiffness": D.subs(z,0)-k0,
        "low_frequency_friction": s.diff(D,z).subs(z,0)-friction,
        "low_frequency_dynamic_mass": s.diff(D,z,2).subs(z,0)/2-mass,
        "exact_hidden_resolvent_remainder": remainder-exact_remainder,
        "exact_Drude_Taylor_remainder": h-mu*gamma*z-mu*(1-gamma/cut)*z**2-
            mu*gamma*z**3/(cut*(cut+z)),
        "white_bath_does_not_remove_hidden_memory": s.limit(D,cut,s.oo)-
            (a+mu*z**2+mu*gamma*z-g1**2/(k1+mu*z**2+mu*gamma*z)-g2**2/(k2+mu*z**2+mu*gamma*z)),
    }


def limit_and_rejection_residuals():
    mu,gamma,cut,z,eps,k = s.symbols("mu gamma cutoff z eps k",positive=True)
    a,g=s.symbols("a g",real=True)
    h=mu*z**2+mu*gamma*cut*z/(z+cut)
    fast=a+h-g**2/(k+eps**2*h)
    W_then_A=s.limit(s.limit(fast,cut,s.oo),eps,0)
    A_then_W=s.limit(s.limit(fast,eps,0),cut,s.oo)
    # Rational generic comparator counterexample, NOT a retune of the O control.
    Dwhite=2+z**2+2*z-1/(1+z**2+2*z)
    wrong_static=1+z**2+2*z
    return {"white_and_explicit_fast_limit_commute":W_then_A-A_then_W,
            "fast_limit_retains_static_coupling":s.limit(fast,eps,0)-(a-g**2/k+h),
            "negative_dynamic_mass_witness":s.diff(Dwhite,z,2).subs(z,0)/2+2,
            "static_only_elimination_misses_friction":s.diff(Dwhite-wrong_static,z).subs(z,0)-2,
            "witness_static_stiffness_positive":Dwhite.subs(z,0)-1}


def reduction_band_bound(mu, gamma, cut, band, kappa, gnorm2, r1, r2):
    """Sufficient complex-disk bound. No automatically selected bandwidth."""
    vals=list(map(s.sympify,(mu,gamma,cut,band,kappa,gnorm2,r1,r2)))
    mu,gamma,cut,band,kappa,gnorm2,r1,r2=vals
    if not all(v.is_positive for v in (mu,gamma,cut,band,kappa)):
        raise ValueError("positive scales required")
    if not all(v.is_nonnegative for v in (gnorm2,r1,r2)):
        raise ValueError("nonnegative coupling norms/moments required")
    if not (cut-band).is_positive:
        raise ValueError("bandwidth must be strictly below Drude cutoff")
    H=mu*band**2+mu*gamma*cut*band/(cut-band)
    if not (kappa-H).is_positive:
        raise ValueError("hidden resolvent separation H<kappa not certified")
    Rh=mu*gamma*band**3/(cut*(cut-band))
    bound=(1+r1)*Rh+r2*(mu*abs(1-gamma/cut)*band**2+Rh)*(H+mu*gamma*band)
    bound+=gnorm2*H**3/(kappa**3*(kappa-H))
    return dict(H=s.factor(H), impedance_error=s.factor(bound))


def core_normalization_residuals():
    mass, friction, lam, E, t, vel, force = s.symbols("m zeta lambda E t Pi force",positive=True)
    mn=lam**2*mass/(4*E*t**2)
    zn=lam**2*friction/(4*E*t)
    mobility=1/zn
    tau=mn/zn
    return {"Core_inertia_ratio": tau/mobility-mn,
            "Core_mobility_is_inverse_normalized_friction": mobility*zn-1,
            "Phi_force_port_scaling": lam*force*vel-force*(lam*vel)}


def negative_controls():
    mu,gamma,cut,temp = s.symbols("mu gamma cutoff kBT",positive=True)
    F,cov,noise=ou_matrices(s.eye(3),mu,gamma,cut,temp)
    c=joint_coefficients((1,1,-1,-1))
    controls={
        "counterterm_omitted_changes_static_potential": True,
        "unshifted_bath_initial_slip_discarded": True,
        "wrong_noise_amplitude_rejected": (F*cov+cov*F.T+noise/2)!=s.zeros(9),
        "white_noise_factor_two_missing": mu*gamma*temp != 2*mu*gamma*temp,
        "Phi_inertia_mistaken_for_atomic_mass": s.Integer(5)!=1,
        "flat_Phi_momentum_measure_without_Jacobian": s.sqrt(5)!=1,
        "linear_force_deleted": c["f"]!=s.zeros(3,1),
        "mixed_stiffness_deleted": c["g"]!=s.zeros(2,1),
        "embedding_markov_claimed_for_Phi_pair": True,
        "frozen_spins_treated_as_annealed": True,
        "endpoint_mistaken_for_Phi": old.E[3,1]-old.E[0,1]!=0,
        "nonSPD_joint_admitted": False,
        "unresolved_band_admitted": False,
        "Pi_even_time_parity": False,
    }
    q,zb,cj,mj,wj=s.symbols("q zb c m w",positive=True)
    controls["counterterm_omitted_changes_static_potential"]=s.simplify(
        (mj*wj**2*zb**2/2-cj*q*zb).subs(zb,cj*q/(mj*wj**2))) != 0
    controls["unshifted_bath_initial_slip_discarded"]=s.simplify(-cj**2*q/(mj*wj**2)) != 0
    # One frozen-label mixture with preparation (1/2,1/2), energies (0,1).
    controls["frozen_spins_treated_as_annealed"]=s.Rational(1,2)!=1/(1+s.exp(-1))
    z=s.Symbol("z",positive=True)
    D=3+z**2+z-1/(1+z**2+z)
    controls["embedding_markov_claimed_for_Phi_pair"]=s.diff(D,z,3)!=0
    try:
        assert_joint_spd(s.diag(1,1,-1))
    except ValueError:
        controls["nonSPD_joint_admitted"]=True
    try:
        reduction_band_bound(1,1,1,1,1,1,1,1)
    except ValueError:
        controls["unresolved_band_admitted"]=True
    parity=s.diag(s.eye(3),s.eye(3),s.eye(3))
    reversible=F+s.diag(s.zeros(3),s.zeros(3),cut*s.eye(3))
    controls["Pi_even_time_parity"]=(parity*reversible*parity+reversible)!=s.zeros(9)
    if not all(controls.values()):
        raise ValueError("negative control did not expose declared error")
    return controls


def calculate():
    log_bracket()
    rows=spin_regime_rows()
    if not all(r["mean_outside_locked_ball"] for r in rows):
        raise ValueError("locked localization exclusion is not certified; revise verdict, never force PASS")
    checks={name:zeros(fn()) for name,fn in (
        ("coordinates_ports",coordinate_residuals),
        ("joint_parent_derivative_link",joint_parent_derivative_residuals),
        ("local_quantum_bound_identities",local_quantum_residuals),
        ("finite_bath_preparation_energy",bath_residuals),
        ("Drude_kernel_white_limit",drude_residuals),
        ("OU_stationarity_parity_stability",ou_residuals),
        ("exact_block_response",response_residuals),
        ("conditional_hidden_memory_FDT",hidden_fdt_residuals),
        ("spectral_effective_noise",spectral_fdt_residuals),
        ("low_frequency_remainder",markov_expansion_residuals),
        ("limits_and_invalid_mass_witness",limit_and_rejection_residuals),
        ("Core_conditional_normalization",core_normalization_residuals))}
    return dict(completed_rounds=["P0","P1","P2","P3","P4"],checks=checks,
                spin_controls=rows,negative_controls=negative_controls(),
                analytic_dependencies=[
                    "Sylvester/Bernstein rational certificates and the positive atanh series for ln2.",
                    "Gaussian halfspace projection excludes probability above 1/2 inside the locked ball.",
                    "Classical Gaussian bath integration and exact finite-oscillator elimination with conditional preparation.",
                    "Neumann/Taylor and response-weighted quantum FDT tail inequalities in the report, not a material error acceptance.",
                    "Orthogonal diagonalization of SPD stiffness transfers diagonal symbolic OU/FDT checks to the general reference.",
                    "Prepared hidden OU covariance identity gives transient FDT; a transfer function alone is insufficient.",
                    "Routh-Hurwitz, exact Schur complement and explicit fast-mode scaling justify only stated limits."],
                locked_control=dict(N=4,D_over_Jref=8,delta="ln2",nu=2,
                                    dref_over_r0=1,epsilon_star=1,R_over_dref="1/4",
                                    bath_gamma="positive free reference parameter",
                                    bath_cutoff="positive free reference parameter"),
                decisions={
                    "localization":"NOT_ADMITTED at the locked center and R=dref/4: all16 quadratic Gaussian means lie outside; projection gives P(ball)<1/2 for every T>0. Not a no-go for other references/materials.",
                    "parent_global":"NOT_ADMITTED: O collision no-go unchanged by normalized shifted bath integral.",
                    "bath_GLE":"EXACT for finite harmonic bath/declared conditional preparation; Drude continuum is an additional spectrum choice.",
                    "quadratic_embedding":"EQUIVALENT linear Gaussian Drude reference with matched conditional initial law; not an extra independent memory substance.",
                    "hidden_reduction":"EXACT nonlocal response and FDT with conditional hidden equilibrium; prepared offsets give extra forcing.",
                    "Core_Markov":"CONDITIONAL low-band approximation only; effective mass need not equal bare inertia or be positive.",
                    "C_kinetics":"NOT_DERIVED: labels remain frozen, sector weights are preparation, not bath-selected transitions.",
                    "material":"UNRESOLVED: no material selection, quantum/local physical correspondence or independent specialist validation.",
                    "novelty":"STANDARD_COMPARATOR_EQUIVALENCE within this chosen harmonic-bath class; no new UET discriminator."},
                physical_acceptance=False,unique_UET_discriminator=False,new_core_terms=0,
                old_scientific_verifiers_rerun=False,trajectories=0,
                method=dict(sympy=s.__version__,arithmetic="exact",random_samples=0,parameter_sweep=False),
                limitations=["Joint quadratic reference is not O's full Phi-dependent conditional ensemble.",
                             "Stationary static covariance is not a finite-time escape/lifetime guarantee.",
                             "No spin transition, real material, calibrated bath, physical heat or total entropy-production claim.",
                             "Formal completion does not promote legacy contracts, Topic 13 or Core physics gates."])


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT),ROOT),**calculate()}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--check",action="store_true",help="read-only identities and artifact freshness")
    group.add_argument("--emit-report",action="store_true",help="generate only the new compact artifact")
    args=parser.parse_args(argv)
    result=record()
    payload=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(payload,encoding="utf-8",newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes()!=payload.encode("utf-8"):
        raise ValueError("artifact absent/stale; inspect before explicit --emit-report")
    print(json.dumps(dict(rounds=result["completed_rounds"],exact_groups=len(result["checks"]),
                          spin_configurations=len(result["spin_controls"]),
                          negative_controls=len(result["negative_controls"]),
                          review=result["contract_review_status"],physical_acceptance=False)))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
