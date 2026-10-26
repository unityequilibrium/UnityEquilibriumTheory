"""Round O: local classical mechanical comparator, not a new UET Core law.

Finite open four-atom chain. Exact canonical coordinate identities and local
quadratic conditional thermodynamics are distinct from parent/material validity.
No time integration, Monte Carlo, fit, damping/noise or old science rerun.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from itertools import product
import json
from pathlib import Path
import sys

import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata, load_json

TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
CONTRACT = f"{TOPIC}/calculation_contracts/lattice_mechanical_state_construction.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_lattice_mechanical_state_construction.json"
REPORT = "docs/meta/UET_LATTICE_MECHANICAL_STATE_CONSTRUCTION.md"
SPINS = tuple(product((-1, 1), repeat=4))
L = s.log(2)
A = s.Matrix([-s.Rational(3, 2), -s.Rational(1, 2), s.Rational(1, 2), s.Rational(3, 2)])
E = s.Matrix([[s.Rational(1, 2), 1/s.sqrt(20)],
              [-s.Rational(1, 2), -3/s.sqrt(20)],
              [-s.Rational(1, 2), 3/s.sqrt(20)],
              [s.Rational(1, 2), -1/s.sqrt(20)]])


def _zeros(values):
    for name, value in values.items():
        if s.simplify(value) != 0:
            raise ValueError(f"exact residual failed: {name}: {value}")
    return {name: True for name in values}


def validate_spins(spins):
    if len(spins) != 4 or any(type(v) is not int or v not in (-1, 1) for v in spins):
        raise ValueError("reference requires four exact +/-1 spin labels")


def label(spins):
    return "".join("+" if v == 1 else "-" for v in spins)


def open_bonds():
    return ((0, 1), (1, 2), (2, 3))


def canonical_residuals():
    d, ep, mu, J = s.symbols("d_ref epsilon_star mu J_ref", positive=True)
    phi, u1, u2 = s.symbols("Phi u_1 u_2", real=True)
    q = s.Matrix([phi, u1, u2])
    c = -d*ep*A
    B = c.row_join(E)
    mass = s.simplify(mu*(c.dot(c)))
    p = s.Matrix(s.symbols("p_Phi p_u1 p_u2", real=True))
    # Center-of-mass orthonormal coordinate completes the invertible map.
    Q = s.ones(4, 1)/2
    full = Q.row_join(B)
    inverse_p = s.simplify(full.inv().T)
    metric = s.simplify(B.T*B)
    kinetic = (s.simplify(B*(metric.inv()*p))).dot(s.simplify(B*(metric.inv()*p)))/(2*mu)
    time = d*s.sqrt(mu/J)
    mnorm = s.simplify(mass/(4*J*time**2))
    x = d*(1-ep*phi)*A+E*s.Matrix([u1, u2])
    recovered = (1-A.dot(x)/(d*A.dot(A)))/ep
    end = s.simplify(x[3]-x[0])
    return {
        "basis_orthonormal": s.trace((E.T*E-s.eye(2))**2),
        "basis_has_no_translation": (E.T*s.ones(4, 1)).dot(E.T*s.ones(4, 1)),
        "basis_has_no_affine_copy": (E.T*A).dot(E.T*A),
        "coordinate_inverse": s.trace((full.inv()*full-s.eye(4))**2),
        "canonical_one_form": s.trace((full.T*inverse_p-s.eye(4))**2),
        "phase_space_Jacobian": s.det(full)*s.det(inverse_p)-1,
        "kinetic_from_atoms": kinetic-(p[0]**2/(2*mass)+(p[1]**2+p[2]**2)/(2*mu)),
        "physical_affine_inertia": mass-5*mu*d**2*ep**2,
        "normalized_inertia": mnorm-s.Rational(5, 4)*ep**2,
        "physical_p_equals_EtP": mass/time-J*time*(4*mnorm),
        "velocity_measure_equals_canonical_pushforward": mass/time-(J*time)*(4*mnorm),
        "Phi_observation_operator": recovered-phi,
        "end_readout_contains_hidden_mode": end-(3*d*(1-ep*phi)-u2/s.sqrt(5)),
        "u1_does_not_change_end_readout": s.diff(end, u1),
    }


def general_inertia_residual():
    n = s.Symbol("N", integer=True, positive=True)
    i = s.Symbol("i", integer=True)
    return s.summation((i-(n+1)/2)**2, (i, 1, n))-n*(n**2-1)/12


def parent_potential(spins, positions, D, delta, r0, J, d, nu):
    validate_spins(spins)
    def morse(r):
        return D*(1-s.exp(-delta*(r/r0-1)))**2
    result = sum(morse(positions[j]-positions[i])-morse((j-i)*d)
                 for i in range(4) for j in range(i+1, 4))
    result -= J*s.Rational(1, 4)*sum(
        ((positions[j]-positions[i])/d)**(-nu)*spins[i]*spins[j] for i, j in open_bonds())
    return result


@lru_cache(maxsize=None)
def control_coefficients(spins):
    """Actual locked parent derivatives, in J_ref,d_ref units at Phi=u=0.

    D/J_ref=8, delta=ln2, r0/d_ref=1, nu=2, epsilon_star=1.
    No parameter fitting or modification of the declared control.
    """
    validate_spins(spins)
    V0 = s.Integer(0)
    b, K = s.zeros(2, 1), s.zeros(2)
    Vphi, bphi, Kphi = s.Integer(0), s.zeros(2, 1), s.zeros(2)
    fullH = s.zeros(4)
    for i in range(4):
        for j in range(i+1, 4):
            n = j-i
            y = s.Rational(1, 2)**(n-1)
            f1 = 16*L*(y-y*y)
            f2 = 16*L**2*(2*y*y-y)
            f3 = 16*L**3*(y-4*y*y)
            if n == 1:
                eta = spins[i]*spins[j]
                V0 -= s.Rational(eta, 4)
                f1 += s.Rational(eta, 2)
                f2 -= s.Rational(3*eta, 2)
                f3 += 6*eta
            direction = (E[j, :]-E[i, :]).T
            atom_direction = s.zeros(4, 1)
            atom_direction[j], atom_direction[i] = 1, -1
            b += f1*direction
            K += f2*direction*direction.T
            Vphi -= n*f1
            bphi -= n*f2*direction
            Kphi -= n*f3*direction*direction.T
            fullH += f2*atom_direction*atom_direction.T
    K = s.simplify(K)
    b = s.simplify(b)
    return dict(V0=V0, b=b, K=K, Vphi=s.simplify(Vphi),
                bphi=s.simplify(bphi), Kphi=s.simplify(Kphi), fullH=s.simplify(fullH))


def direct_parent_derivative_residuals(spins):
    """Independent differentiation of the full pair energy for source linkage."""
    phi, u1, u2 = s.symbols("Phi u1 u2", real=True)
    u = s.Matrix([u1, u2])
    x = (1-phi)*A+E*u
    V = parent_potential(spins, x, 8, L, 1, 1, 1, 2)
    at0 = {phi: 0, u1: 0, u2: 0}
    c = control_coefficients(tuple(spins))
    grad = s.Matrix([s.diff(V, t) for t in u])
    hess = s.hessian(V, u)
    values = {"V0": V.subs(at0)-c["V0"],
              "Vphi": s.diff(V, phi).subs(at0)-c["Vphi"]}
    for i in range(2):
        values[f"b_{i}"] = grad[i].subs(at0)-c["b"][i]
        values[f"bphi_{i}"] = s.diff(grad[i], phi).subs(at0)-c["bphi"][i]
        for j in range(2):
            values[f"K_{i}{j}"] = hess[i, j].subs(at0)-c["K"][i, j]
            values[f"Kphi_{i}{j}"] = s.diff(hess[i, j], phi).subs(at0)-c["Kphi"][i, j]
    return values


def positive_log_polynomial(expr):
    """Exact certificate using ln2>1/2, not a floating-point tolerance."""
    poly = s.Poly(s.expand(expr), L)
    z = s.Symbol("z", positive=True)
    rewritten = s.Integer(0)
    for (power,), coefficient in poly.terms():
        if power % 2:
            raise ValueError("positivity certificate expects an even ln2 polynomial")
        rewritten += coefficient*(z+s.Rational(1, 4))**(power//2)
    coeff = s.Poly(s.expand(rewritten), z).all_coeffs()
    return all(v >= 0 for v in coeff) and coeff[-1] > 0


def assert_spd(K):
    if K.shape != (2, 2) or K != K.T:
        raise ValueError("conditional Hessian must be symmetric 2 by 2")
    if not (positive_log_polynomial(K[0, 0]) and positive_log_polynomial(K.det())):
        raise ValueError("conditional Hessian not certified strictly positive")


def shifted_reference(c):
    K, b = c["K"], c["b"]
    assert_spd(K)
    mean = s.simplify(-K.inv()*b)
    effective = s.factor(c["V0"]+(b.T*mean)[0]/2)
    derivative = s.factor(c["Vphi"]+(c["bphi"].T*mean)[0]
                         +(mean.T*c["Kphi"]*mean)[0]/2)
    logA_phi = s.factor(-s.trace(K.inv()*c["Kphi"])/2)
    return dict(mean=mean, effective=effective, derivative=derivative, logA_phi=logA_phi)


def gaussian_residuals():
    a, schur, off, b1, b2 = s.symbols("a schur off b1 b2", positive=True)
    u1, u2 = s.symbols("u1 u2", real=True)
    K = s.Matrix([[a, off], [off, schur+off**2/a]])
    b = s.Matrix([b1, b2])
    u = s.Matrix([u1, u2])
    mean = -K.inv()*b
    v0, v1 = s.symbols("v0 v1", real=True)
    centered = s.expand((u-mean).T*K*(u-mean))[0]/2-(b.T*K.inv()*b)[0]/2
    hessian_form = (u.T*K*u)[0]/2+(b.T*u)[0]
    kB, T, h, mu = s.symbols("k_B T h mu", positive=True)
    z = s.Symbol("z", real=True)
    # Two independent Gaussian position integrals and two momentum integrals.
    Iz = s.integrate(s.exp(-a*z**2/(2*kB*T)), (z, -s.oo, s.oo))
    Is = s.integrate(s.exp(-schur*z**2/(2*kB*T)), (z, -s.oo, s.oo))
    Ip = s.integrate(s.exp(-z**2/(2*mu*kB*T)), (z, -s.oo, s.oo))
    pref = (2*s.pi*kB*T/h)**2*mu/s.sqrt(K.det())
    omega1, omega2 = s.symbols("omega1 omega2", positive=True)
    return {
        "square_completion_with_linear_shift": hessian_form-centered,
        "Gaussian_integrals_match_determinant": Iz*Is*Ip**2/h**2-pref,
        "determinant_under_hidden_orthogonal_rotation": K.det()-a*schur,
        "mode_product_same_measure": pref.subs(schur, mu**2*omega1**2*omega2**2/a)
            -(2*s.pi*kB*T/h)**2/(omega1*omega2),
        "hidden_quadratic_energy": -s.diff(s.log(pref), T)*(-kB*T**2)-2*kB*T,
    }


def mixture_residuals():
    T, kb, c1, c2 = s.symbols("T k_B c1 c2", positive=True)
    E1, E2, kinetic = s.symbols("E1 E2 retained_kinetic", real=True)
    energies, prefactors = (E1, E2), (c1, c2)
    weights = [c*T**2*s.exp(-en/(kb*T)) for c, en in zip(prefactors, energies)]
    Z = sum(weights)
    probs = [w/Z for w in weights]
    F = kinetic-kb*T*s.log(Z)
    U = kinetic+sum(p*en for p, en in zip(probs, energies))+2*kb*T
    S_chain = s.Integer(0)
    for p, en, c in zip(probs, energies, prefactors):
        logp = s.log(c)+2*s.log(T)-en/(kb*T)-s.log(Z)
        S_chain += -kb*p*logp+kb*p*(s.log(c)+2*s.log(T)+2)
    return {"probability_normalization": sum(probs)-1,
            "fixed_state_entropy_chain": -s.diff(F, T)-S_chain,
            "internal_energy_F_plus_TS": F+T*S_chain-U,
            "retained_not_integrated_again": s.diff(F, kinetic)-1}


def force_residuals():
    phi, T, kb = s.symbols("Phi T k_B", positive=True)
    a, d, off, b1, b2, v = [s.Function(n)(phi) for n in ('a', 'd', 'off', 'b1', 'b2', 'v')]
    K = s.Matrix([[a, off], [off, d]])
    b = s.Matrix([b1, b2])
    mean = -K.inv()*b
    eff = v-(b.T*K.inv()*b)[0]/2
    F = eff+kb*T*s.log(K.det())/2  # remaining prefactor has no Phi dependence
    microscopic_force = -s.diff(v, phi)-(s.diff(b, phi).T*mean)[0]
    microscopic_force -= (mean.T*s.diff(K, phi)*mean)[0]/2
    microscopic_force -= kb*T*s.trace(s.diff(K, phi)*K.inv())/2
    mean_force = -s.diff(eff, phi)-kb*T*s.trace(K.inv()*s.diff(K, phi))/2
    return {"mean_microscopic_force": -s.diff(F, phi)-microscopic_force,
            "effective_and_determinant_force": -s.diff(F, phi)-mean_force,
            "Maxwell_force_entropy": s.diff(-s.diff(F, phi), T)-s.diff(-s.diff(F, T), phi)}


def conservative_residuals():
    phi, u1, u2, p, p1, p2 = s.symbols("Phi u1 u2 pPhi pu1 pu2", real=True)
    M, mu = s.symbols("M_Phi_phys mu", positive=True)
    V = s.Function("V")(phi, u1, u2)
    qs, ps = (phi, u1, u2), (p, p1, p2)
    H = p**2/(2*M)+(p1**2+p2**2)/(2*mu)+V
    balance = sum(s.diff(H, q)*s.diff(H, pp)-s.diff(H, pp)*s.diff(H, q) for q, pp in zip(qs, ps))
    return {"Hamiltonian_energy_balance_frozen_spins": balance,
            "Phi_velocity_is_canonical": s.diff(H, p)-p/M}


def collision_witness():
    t = s.Symbol("gap", positive=True)
    gaps = (t, s.Rational(7, 4)-3*t/4, s.Integer(1))
    positions = s.Matrix([0, gaps[0], gaps[0]+gaps[1], sum(gaps)])
    positions -= s.ones(4, 1)*sum(positions)/4
    V = parent_potential((1, 1, 1, 1), positions, 8, L, 1, 1, 1, 2)
    return {"fixed_affine_Phi": A.dot(positions)-5,
            "center_of_mass_removed": sum(positions),
            "attractive_collision_leading_term": s.limit(t**2*V, t, 0)+s.Rational(1, 4)}


def local_bounds(rho, temperature, K, b, kb=1, d=1):
    """Markov tail certificate for a local ball, not a new physical hard core."""
    rho, temperature, kb, d = map(s.sympify, (rho, temperature, kb, d))
    if not (0 <= rho < 1) or not temperature.is_nonnegative:
        raise ValueError("need 0<=rho<1 and nonnegative symbolic/exact T")
    assert_spd(K)
    radius = d*(1-rho)/4
    mean = -K.inv()*b
    eta = s.factor((mean.dot(mean)+kb*temperature*s.trace(K.inv()))/radius**2)
    return dict(radius=radius, eta=eta,
                domain="Eta<1 required for finite log-tail certificate; no forced acceptance.")


def remainder_residuals():
    r, D, delta, r0, J, d, nu = s.symbols('r D delta r0 J d_ref nu', positive=True)
    y = s.exp(-delta*(r/r0-1))
    morse = D*(1-y)**2
    spin = -J*(r/d)**(-nu)/4
    rho = s.Symbol('rho', real=True)
    inside_probability = s.Symbol('p_inside', positive=True)
    radius = d*(1-rho)/4
    gap_lower = d*(1-rho)-s.sqrt(2)*radius
    return {'Morse_third_derivative':s.diff(morse, r, 3)-2*D*(delta/r0)**3*(y-4*y**2),
            'exchange_third_derivative':s.diff(spin, r, 3)-J*nu*(nu+1)*(nu+2)*d**nu/(4*r**(nu+3)),
            'local_gap_factor':gap_lower-d*(1-rho)*(1-s.sqrt(2)/4),
            'Gaussian_tail_value_log':-s.log(inside_probability)-s.log(1/inside_probability)}


def negative_controls():
    c = control_coefficients((1, 1, -1, -1))
    z = shifted_reference(c)
    other = control_coefficients((1, -1, 1, -1))
    T, kb = s.symbols("T k_B", positive=True)
    phi, pi = s.symbols("Phi Pi", real=True)
    canonical_form = 5*pi  # p_Phi at the locked unit-scale geometry, from O4
    wrong_periodic = -s.Rational(1, 4)*4
    actual_open = control_coefficients((1, 1, 1, 1))['V0']
    controls = {
        "retained_affine_mode_counted_as_hidden": s.simplify(3*kb*T-2*kb*T) != 0,
        "flat_velocity_measure_without_Jacobian": s.diff(canonical_form, pi)-1 != 0,
        "velocity_mistaken_for_canonical_momentum": s.simplify(pi-canonical_form) != 0,
        "linear_shift_discarded": s.simplify(c['V0']-z['effective']) != 0,
        "arrangements_assumed_uniform": c['V0'] != other['V0'],
        "stiffness_degeneracy_assumed": s.simplify(c['K'].det()-other['K'].det()) != 0,
        "end_readout_mistaken_for_Phi": E[3, 1]-E[0, 1] != 0,
        "periodic_bond_silently_added": wrong_periodic != actual_open,
        "half_spin_factor_omitted": 4*actual_open != actual_open,
        "Phi_reference_force_deleted": c['Vphi'] != 0,
        "nonSPD_Gaussian_admitted": False,
    }
    try:
        assert_spd(s.diag(1, -1))
    except ValueError:
        controls['nonSPD_Gaussian_admitted'] = True
    if not all(controls.values()):
        raise ValueError("a declared negative convention was not rejected")
    return controls


def calculate():
    rows = []
    flip_ok = True
    for spins in SPINS:
        c = control_coefficients(spins)
        assert_spd(c['K'])
        f = control_coefficients(tuple(-v for v in spins))
        flip_ok &= all(c[name] == f[name] for name in ('V0','b','K','Vphi','bphi','Kphi'))
        rows.append(dict(spins=label(spins), k=sum(v == 1 for v in spins),
                         positive_hidden_Hessian=True,
                         linear_hidden_force_nonzero=c['b'] != s.zeros(2, 1),
                         mixed_affine_hidden_stiffness_nonzero=c['bphi'] != s.zeros(2, 1)))
    if not flip_ok:
        raise ValueError("global spin flip symmetry failed")
    witnesses = []
    for spins in ((1,1,-1,-1), (1,-1,1,-1)):
        c = control_coefficients(spins)
        z = shifted_reference(c)
        witnesses.append(dict(spins=label(spins), k=2, V0=str(c['V0']),
                              b=[str(v) for v in c['b']],
                              K=[[str(c['K'][i,j]) for j in range(2)] for i in range(2)],
                              determinant=str(s.expand(c['K'].det())),
                              retained_force_at_u0=str(-c['Vphi']),
                              shift_energy_nonzero=s.simplify(z['effective']-c['V0']) != 0))
    return dict(completed_rounds=['O0','O1','O2','O3','O4'],
                checks={'coordinates_inertia_measure':_zeros(canonical_residuals()),
                        'general_N_inertia_sum':_zeros({'sum':general_inertia_residual()}),
                        'Gaussian_shift_modes':_zeros(gaussian_residuals()),
                        'spin_vibration_mixture':_zeros(mixture_residuals()),
                        'force_entropy_dictionary':_zeros(force_residuals()),
                        'conservative_energy':_zeros(conservative_residuals()),
                        'parent_source_derivative_link':_zeros(direct_parent_derivative_residuals((1,1,-1,-1))),
                        'unconfined_parent_collision':_zeros(collision_witness()),
                        'local_remainder_tail_identities':_zeros(remainder_residuals())},
                locked_control={'N':4,'D_over_Jref':8,'delta':'ln(2)','nu':2,
                                'dref_over_r0':1,'epsilon_star':1,'Phi':0,
                                'temperature_fit':False},
                spin_controls=rows, global_flip_invariant=flip_ok,
                witness_same_C=witnesses, negative_controls=negative_controls(),
                decisions={
                    'coordinates':'EXACT internal canonical coordinate decomposition; Phi is not end-length alone.',
                    'inertia':'EXACT conditional scale map; Mphys=5*mu*dref^2*epsstar^2, mPhi=5*epsstar^2/4 at N=4.',
                    'quadratic_thermodynamics':'EXACT for the declared SPD conditional quadratic reference; shifted energies and determinants both weight arrangements.',
                    'parent_global_equilibrium':'NOT_ADMITTED: collision witness makes unconfined parent partition divergent; source small-strain law is not globally extended.',
                    'parent_local_approximation':'CONDITIONAL: Taylor and tail bounds require a local domain and eta<1; no universal/material acceptance.',
                    'coarse_kinetics':'NOT_CLOSED: affine-hidden stiffness couples retained response to eliminated state; no damping/noise/spin rates derived.',
                    'Omega_correspondence':'PARTIAL/DIFFERENT: no removal of linear terms, periodic NN versus squared-sum difference preserved; no even-quartic identity.',
                    'material_quantum_regime':'UNRESOLVED: classical/local window, actual parameters and independent specialist review not established.'},
                physical_acceptance=False, unique_UET_discriminator=False,
                new_core_terms=0, new_damping_or_noise=False, trajectories=0,
                old_scientific_verifiers_rerun=False,
                method={'sympy':s.__version__,'arithmetic':'exact','random_samples':0,'parameter_sweep':False},
                analytic_dependencies=[
                    'Canonical one-form and inverse-transpose momentum map preserve Liouville measure.',
                    'ln(2)>1/2 certificates prove positive hidden Hessians at the one locked control; no float tolerance.',
                    'Finite Gaussian integration plus conditional entropy chain gives F,U,S and mean force.',
                    'Collision tube, not merely a zero-measure line, excludes global parent equilibrium.',
                    'Local Taylor remainder and Markov Gaussian tail bound control clipped-parent value error only when prerequisites hold.'],
                limitations=['No full-Phi joint integral, actual material constants or independent validation.',
                             'Reference spin labels have no transition law; no kinetic equilibration proof.',
                             'Conditional classical oscillators are not the paper three-polarization Debye continuum.',
                             'No closure of UET cosmic openness, learning, persistence or physical heat/entropy-production gates.'])


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT), ROOT), **calculate()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='read-only identities and freshness')
    group.add_argument('--emit-report', action='store_true', help='generate only the new compact artifact')
    args = parser.parse_args(argv)
    result = record()
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+'\n'
    if args.emit_report:
        (ROOT/OUTPUT).write_text(payload, encoding='utf-8', newline='\n')
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes() != payload.encode('utf-8'):
        raise ValueError('artifact absent/stale; review before explicit --emit-report')
    print(json.dumps(dict(rounds=result['completed_rounds'],exact_groups=len(result['checks']),
                          spin_configurations=len(result['spin_controls']),
                          negative_controls=len(result['negative_controls']),
                          review=result['contract_review_status'], physical_acceptance=False)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
