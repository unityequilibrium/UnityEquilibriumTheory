"""Phase-rotated covariance and its analytic collisionless ray limit.

The six exact zero channels of the tree covariance generator are resolved
by first-order momentum transport, not discarded or given a relaxation rate.
"""

from datetime import datetime, timezone
import json
from math import fsum, isfinite, pi, sqrt
from pathlib import Path
import sys

import numpy as np
import mpmath as mp

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Thermal_Noether_Response as NOE

FQ, VIRT, EFT, TH, INT, MOD, CURV, PREFIX = NOE.FQ, NOE.VIRT, NOE.EFT, NOE.TH, NOE.INT, NOE.MOD, NOE.CURV, NOE.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_collisionless_soft_source_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_collisionless_soft_source.json")
ROTATION = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 0.]])
MATTER_PROJECTOR = np.diag([1., 1., 0.])
MU_GRID, MOMENTA, COSINES = (1.05, 1.2), (.005, .02, .04), (-.6, .3, .8)
TEMPERATURE = .004
RAY_RATIOS = (.5j, 1.5j, .6+.4j)
Q_OVER_P = (1/64, 1/128, 1/256)
ORDERS, ANGULAR_ORDERS, TAILS = (12, 24, 48), (16, 32, 64), (32., 40.)
GATES = {"identity_relative": 1e-9, "method_relative": 1e-7, "covariance_FD_relative": 1e-5,
         "point_soft_relative": 1e-2, "quadrature_relative": 1e-6, "tail_relative": 1e-8,
         "original_causal_leakage": 1e-6}


def stationary_soft_source(ray, state, action):
    if not np.isfinite(ray) or (ray != 0 and ray.imag == 0) or state["xi"] != 0 or state["h"] != 0:
        raise ValueError("zero or non-real ray in stationary h0=0 rest domain required")
    active = (0, 2)
    block = VIRT.matrices(0., state, action)[2][np.ix_(active, active)]
    source = np.linalg.solve(block, [0., 1.])
    chemical = np.linalg.solve(block, [2*state["mu"]*sqrt(state["s"]), 0.])
    susceptibility = state["s"]+2*state["mu"]*sqrt(state["s"])*chemical[0]
    mixed = 2*state["mu"]*sqrt(state["s"])*source[0]
    delta_mu = ray*ray*mixed/(state["s"]-ray*ray*susceptibility)
    delta_xi = -ray*mixed/(state["s"]-ray*ray*susceptibility)
    mean = np.array([source[0]+chemical[0]*delta_mu, 0., source[1]+chemical[1]*delta_mu], dtype=complex)
    theta_coefficient = -1j*delta_xi
    return {"mean": mean, "delta_mu": delta_mu, "delta_xi": delta_xi, "q_theta": theta_coefficient,
            "tree_chi": complex(mean[2]), "tree_chi_static": float(source[1]),
            "tree_chi_fixed_charge": float(source[1]-mixed*mixed/susceptibility),
            "charge_susceptibility": float(susceptibility), "mixed_source_charge": float(mixed)}


def covariance_momentum_jet(p, temperature, state, action):
    FQ.validate(p, p, temperature, state, action)
    mode = MOD.mode(p, state, action)
    energy, unit = mode["omega"], mode["polarization"]
    kinetic, linear, _ = VIRT.matrices(0., state, action)
    velocity = INT.group_velocity(p, state, action)
    de = -2*energy*kinetic+linear
    derivative = 2*p*kinetic+velocity*de
    values, vectors = np.linalg.eigh(VIRT.kernel(p, energy, state, action))
    null = int(np.argmin(abs(values)))
    other = [i for i in range(3) if i != null]
    inverse = (vectors[:, other]/values[other])@vectors[:, other].conjugate().T
    bare = -inverse@derivative@unit
    amplitude = (velocity*(1-float(np.vdot(unit, kinetic@unit).real))+float(np.vdot(unit, de@bare).real))/(2*energy)
    unit_p = bare+amplitude*unit
    vector = np.concatenate([unit, -1j*energy*unit])
    vector_p = np.concatenate([unit_p, -1j*(velocity*unit+energy*unit_p)])
    occupation = TH.bose(energy/temperature) if temperature else 0.
    occupation_p = -occupation*(1+occupation)*velocity/temperature if temperature else 0.
    outer = np.outer(vector, vector.conjugate()).real
    covariance = occupation/energy*outer
    covariance_p = (occupation_p/energy-occupation*velocity/(energy*energy))*outer
    covariance_p += occupation/energy*(np.outer(vector_p, vector.conjugate())+np.outer(vector, vector_p.conjugate())).real
    return covariance, covariance_p


def tree_basis(p, state, action):
    modes = VIRT.tree_modes(p, state, action)
    positive = np.column_stack([np.concatenate([unit, -1j*energy*unit]) for energy, unit in modes])
    basis = np.column_stack([positive, positive.conjugate()])
    inverse = np.linalg.inv(basis)
    eigenvalues = np.array([-1j*energy for energy, _ in modes]+[1j*energy for energy, _ in modes])
    return basis, inverse, eigenvalues


def local_drives(q, z, p, r, state, action):
    mean = FQ.source_response(q, z, state, action)
    theta = mean[1]/sqrt(state["s"])
    delta_mu, delta_xi = -1j*z*theta, 1j*q*theta
    kinetic = VIRT.matrices(0., state, action)[0]
    radial = MOD.cubic_tensor(state, action)[0]*mean[0]+MOD.cubic_tensor(state, action)[2]*mean[2]
    common = -np.linalg.solve(kinetic, radial)+2*state["mu"]*delta_mu*MATTER_PROJECTOR
    left, right = np.zeros((6, 6), dtype=complex), np.zeros((6, 6), dtype=complex)
    # r^2-p^2 remains a physical momentum difference, not a support filter.
    difference = (r-p)*(r+p)
    left[3:, :3] = common+theta*(z*z-difference)*ROTATION
    right[3:, :3] = common+theta*(z*z+difference)*ROTATION
    left[3:, 3:] = right[3:, 3:] = 2j*z*theta*ROTATION
    return left, right, mean, theta, delta_mu, delta_xi


def finite_local_covariance(p, cosine, q, ray, temperature, state, action):
    if not isfinite(cosine) or abs(cosine) > 1 or q <= 0 or not isfinite(q) or not np.isfinite(ray) or ray.imag == 0:
        raise ValueError("physical angle, positive q and non-real ray required")
    r = sqrt((p-q)**2+2*p*q*(1+cosine))
    z = ray*q
    left, right, mean, theta, dmu, dxi = local_drives(q, z, p, r, state, action)
    ap, cp = FQ.evolution_and_covariance(p, temperature, state, action)
    ar, cr = FQ.evolution_and_covariance(r, temperature, state, action)
    rhs = left@cp+cr@right.T
    operator = -1j*z*np.eye(36)-np.kron(ar, np.eye(6))-np.kron(np.eye(6), ap)
    local = np.linalg.solve(operator, rhs.reshape(36)).reshape(6, 6)
    transformation = theta*np.block([[ROTATION, np.zeros((3, 3))], [-1j*z*ROTATION, ROTATION]])
    old = local+transformation@cp+cr@transformation.T
    contact = NOE.pair_contact((cp+cr)/2, state, action)[0]
    force = .5*np.einsum("iab,ab->i", MOD.cubic_tensor(state, action), local[:3, :3])
    moments = NOE.moments(local, p, r, q, state, action)
    trace_p, trace_r = float(np.trace(cp[:2, :2])), float(np.trace(cr[:2, :2]))
    gauge_current = .5j*(2*p*cosine+q)*theta*(trace_r-trace_p)
    density = moments["density"]+dmu*(trace_p+trace_r)/2
    current = moments["current"]+gauge_current
    susceptibility = -mean[[0, 2]]@(force+contact@mean)[[0, 2]]+dmu*density+dxi*current
    return {"local_covariance": local, "cartesian_covariance": old, "pair_chi": complex(susceptibility), "r": r}


def soft_system(p, ray, temperature, state, action):
    source = stationary_soft_source(ray, state, action)
    cp, cp_p = covariance_momentum_jet(p, temperature, state, action)
    basis, inverse, eigenvalues = tree_basis(p, state, action)
    kinetic = VIRT.matrices(0., state, action)[0]
    cubic, mean, theta = MOD.cubic_tensor(state, action), source["mean"], source["q_theta"]
    radial = cubic[0]*mean[0]+cubic[2]*mean[2]
    common = -np.linalg.solve(kinetic, radial)+2*state["mu"]*source["delta_mu"]*MATTER_PROJECTOR
    raw_phase = complex(common[1, 1])
    # The stationary radial row gives 2*u*v*d_sigma-g*d_Phi=2*mu*d_mu.
    common[1, 1] = 0.
    base, left_angle, right_angle = (np.zeros((6, 6), dtype=complex) for _ in range(3))
    base[3:, :3], base[3:, 3:] = common, 2j*ray*theta*ROTATION
    left_angle[3:, :3], right_angle[3:, :3] = -2*p*theta*ROTATION, 2*p*theta*ROTATION
    left_p, right_p, generator_p = np.zeros_like(base), np.zeros_like(base), np.zeros_like(base)
    left_p[3:, :3] = theta*(ray*ray-1)*ROTATION
    right_p[3:, :3] = theta*(ray*ray+1)*ROTATION
    generator_p[3:, :3] = -2*p*np.eye(3)
    rhs0 = [inverse@value@inverse.T for value in (base@cp+cp@base.T, left_angle@cp+cp@right_angle.T)]
    rhs1 = [inverse@value@inverse.T for value in (left_p@cp+cp@right_p.T, cp_p@base.T, cp_p@right_angle.T)]
    drift = inverse@generator_p@basis
    nonzero = [np.zeros((6, 6), dtype=complex) for _ in range(2)]
    zero_pairs = {(i, i+3) for i in range(3)} | {(i+3, i) for i in range(3)}
    zero_drive_error = 0.
    scale = sum(np.linalg.norm(value) for value in rhs0)
    for i in range(6):
        for j in range(6):
            if (i, j) in zero_pairs:
                for value in rhs0:
                    zero_drive_error = max(zero_drive_error, float(abs(value[i, j])/scale) if scale else float(abs(value[i, j])))
            else:
                for value, force in zip(nonzero, rhs0):
                    value[i, j] = force[i, j]/(-eigenvalues[i]-eigenvalues[j])
    numerator = [rhs1[0], rhs1[1]+drift@nonzero[0], rhs1[2]+drift@nonzero[1]]
    return {"cp": cp, "cp_p": cp_p, "basis": basis, "source": source,
            "off": nonzero, "numerator": numerator, "drift": drift, "zero_pairs": zero_pairs,
            "zero_drive_error": zero_drive_error, "raw_stationary_phase_cancellation": raw_phase,
            "contact": NOE.pair_contact(cp, state, action)[0]}


def soft_covariance(p, cosine, ray, temperature, state, action, prepared=None):
    if not isfinite(cosine) or abs(cosine) > 1:
        raise ValueError("physical cosine required")
    system = soft_system(p, ray, temperature, state, action) if prepared is None else prepared
    total = system["off"][0]+cosine*system["off"][1]
    numerator = sum(value*cosine**k for k, value in enumerate(system["numerator"]))
    for i, j in system["zero_pairs"]:
        denominator = -1j*ray-cosine*system["drift"][i, i]
        if denominator == 0:
            if ray != 0 or system["numerator"][0][i, j] != 0 or system["numerator"][2][i, j] != 0:
                raise ValueError("unresolved resonant transport channel, no width assigned")
            total[i, j] = system["numerator"][1][i, j]/(-system["drift"][i, i])
        else:
            total[i, j] = numerator[i, j]/denominator
    basis = system["basis"]
    return basis@total@basis.T, system["source"], system["zero_drive_error"]


def angular_transport_moments(a, b):
    if a == 0 or not np.isfinite(a) or not np.isfinite(b):
        raise ValueError("nonzero off-real transport parameter required")
    if b != 0 and (a/b).imag == 0 and abs((a/b).real) <= 1:
        raise ValueError("real angular pole requires a separate boundary-value prescription")
    ratio = b/a
    if abs(ratio) < .25:
        result = []
        for power in range(4):
            value = 0j
            for order in range(64):
                if (order+power) % 2 == 0:
                    value += (-ratio)**order/(order+power+1)/a
            result.append(value)
        return np.array(result)
    first = (np.log1p(ratio)-np.log1p(-ratio))/(2*b)
    values = [first]
    for power in range(1, 4):
        polynomial = 1/power if (power-1) % 2 == 0 else 0.
        values.append((polynomial-a*values[-1])/b)
    return np.array(values)


def soft_angular(p, ray, temperature, state, action, angular_order=None, prepared=None):
    system = soft_system(p, ray, temperature, state, action) if prepared is None else prepared
    if angular_order is not None:
        if angular_order < 2:
            raise ValueError("declared angular rule required")
        angles, weights = np.polynomial.legendre.leggauss(angular_order)
        return complex(sum(weight*soft_point(p, angle, ray, temperature, state, action, system)["chi"]/2 for angle, weight in zip(angles, weights)))
    average = system["off"][0].copy()
    weighted = system["off"][1]/3
    numerator, drift = system["numerator"], system["drift"]
    # Six opposite-frequency pairs are exact transport channels, not a cutoff.
    for i, j in system["zero_pairs"]:
        b = -drift[i, i]
        if ray == 0:
            if numerator[0][i, j] != 0 or numerator[2][i, j] != 0 or b == 0:
                raise ValueError("static transport cancellation must be explicit")
            average[i, j], weighted[i, j] = numerator[1][i, j]/b, 0.
        else:
            moments = angular_transport_moments(-1j*ray, b)
            average[i, j] = sum(numerator[k][i, j]*moments[k] for k in range(3))
            weighted[i, j] = sum(numerator[k][i, j]*moments[k+1] for k in range(3))
    basis, source = system["basis"], system["source"]
    averaged = basis@average@basis.T
    angular_weighted = basis@weighted@basis.T
    force = .5*np.einsum("iab,ab->i", MOD.cubic_tensor(state, action), averaged[:3, :3])
    mean, dmu, dxi = source["mean"], source["delta_mu"], source["delta_xi"]
    density = NOE.moments(averaged, p, p, 0., state, action)["density"]+dmu*np.trace(system["cp"][:2, :2])
    current = 1j*p*(angular_weighted[0, 1]-angular_weighted[1, 0])+dxi*p*np.trace(system["cp_p"][:2, :2])/3
    return complex(-mean[[0, 2]]@(force+system["contact"]@mean)[[0, 2]]+dmu*density+dxi*current)


def soft_point(p, cosine, ray, temperature, state, action, prepared=None):
    system = soft_system(p, ray, temperature, state, action) if prepared is None else prepared
    covariance, source, zero_error = soft_covariance(p, cosine, ray, temperature, state, action, system)
    cp, cp_p, contact = system["cp"], system["cp_p"], system["contact"]
    mean, dmu, dxi = source["mean"], source["delta_mu"], source["delta_xi"]
    force = .5*np.einsum("iab,ab->i", MOD.cubic_tensor(state, action), covariance[:3, :3])
    moments = NOE.moments(covariance, p, p, 0., state, action)
    # q0 geometry picks p_z=0; the ray limit retains the actual angle.
    current = 1j*p*cosine*(covariance[0, 1]-covariance[1, 0])
    current += dxi*p*cosine*cosine*np.trace(cp_p[:2, :2])
    density = moments["density"]+dmu*np.trace(cp[:2, :2])
    susceptibility = -mean[[0, 2]]@(force+contact@mean)[[0, 2]]+dmu*density+dxi*current
    return {"chi": complex(susceptibility), "local_covariance": covariance, "zero_drive_error": zero_error}


def soft_thermal(ray, temperature, state, action, order=24, angular_order=None, tail=40.):
    TH.validate(.02, temperature, state, action, order)
    stationary_soft_source(ray, state, action)
    if angular_order is not None and angular_order < 2:
        raise ValueError("declared angular rule required")
    if temperature == 0:
        return 0j
    c, value = INT.dispersion_coefficients(state, action)["c"], 0j
    for x, weight in TH.radial_nodes(order, tail):
        p = temperature*x/c
        angular = soft_angular(p, ray, temperature, state, action, angular_order)
        value += weight*temperature/c*p*p/(2*pi*pi)*angular
    return complex(value)


def centre(p, cosine, q):
    if not all(isfinite(x) for x in (p, cosine, q)) or p <= 0 or q < 0 or abs(cosine) > 1:
        raise ValueError("physical positive momentum, angle and nonnegative q required")
    magnitude = sqrt(p*p+p*q*cosine+q*q/4)
    if magnitude == 0:
        raise ValueError("zero centre is outside the acoustic-mode domain")
    return magnitude, (p*cosine+q/2)/magnitude


def pair_from_centre(k, cosine, q):
    centre(k, cosine, q)
    p = sqrt(k*k-k*q*cosine+q*q/4)
    if p == 0:
        raise ValueError("zero internal momentum is outside the acoustic domain")
    return p, (k*cosine-q/2)/p


def extended_gaussian_state(p, temperature, state, action, digits=50, context=None):
    """Same tree polynomial and symplectic normalization, without binary64 cancellation."""
    FQ.validate(p, p, temperature, state, action)
    ctx = mp.mp.clone() if context is None else context
    ctx.dps = digits
    real = lambda value: ctx.mpf(str(value))
    p, temperature = real(p), real(temperature)
    mu, s, vcurv = (real(state[k]) for k in ("mu", "s", "V_curvature"))
    u, g, eps, kp, lam = (real(action[k]) for k in ("u", "gamma", "epsilon", "response_kinetic", "response_quartic"))
    kp *= eps
    if g == 0:
        raise ValueError("extended tree basis requires the declared nonzero coupling; decoupling control uses Cartesian equations")
    v = ctx.sqrt(s)
    kinetic = ctx.diag([1, 1, kp])
    potential = ctx.matrix([[2*u*s, 0, -g*v], [0, 0, 0], [-g*v, 0, vcurv]])
    linear = ctx.matrix([[0, 2j*mu, 0], [-2j*mu, 0, 0], [0, 0, 0]])
    rotation = ctx.matrix([[0, -1, 0], [1, 0, 0], [0, 0, 0]])
    cubic = [ctx.matrix([[6*u*v, 0, -g], [0, 2*u*v, 0], [-g, 0, 0]]),
             ctx.matrix([[0, 2*u*v, 0], [2*u*v, 0, -g], [0, -g, 0]]),
             ctx.diag([-g, -g, 6*eps*lam*(real(state["Phi"])-real(action["Phi_reference"]))])]
    def polynomial(e):
        aa, bb, dd = 2*u*s+p*p-e, p*p-e, vcurv+kp*(p*p-e)
        return (aa*bb-4*mu*mu*e)*dd-g*g*s*bb
    def polynomial_e(e):
        aa, bb, dd = 2*u*s+p*p-e, p*p-e, vcurv+kp*(p*p-e)
        return -(aa+bb+4*mu*mu)*dd-kp*(aa*bb-4*mu*mu*e)+g*g*s
    # The low-p curvature fixed point is not a full-domain root algorithm.
    k64, l64, v64 = VIRT.matrices(float(p), state, action)
    companion = np.block([[np.zeros((3, 3)), np.eye(3)], [np.linalg.solve(k64, v64), np.linalg.solve(k64, l64)]])
    seeds = np.linalg.eigvals(companion)
    energies64 = sorted(value.real for value in seeds if value.real > 0)
    if len(energies64) != 3 or max(abs(seeds.imag)) > 1e-9:
        raise ValueError("three real positive tree frequencies required for extended roots")
    root_scale = (1+p*p+2*u*s+vcurv+4*mu*mu)**3*max(1, kp)
    energies, units = [], []
    for energy in energies64:
        e = ctx.findroot(lambda value: polynomial(value)/root_scale, real(energy)**2,
                         df=lambda value: polynomial_e(value)/root_scale, solver="newton")
        energy = ctx.sqrt(e)
        dd = vcurv+kp*(p*p-e)
        denominator = 2*u*s+p*p-e-g*g*s/dd
        aa, bb = 2*mu*energy/denominator, g*v*2*mu*energy/(denominator*dd)
        norm = 1+aa*aa+kp*bb*bb+2*mu*aa/energy
        if energy <= 0 or norm <= 0:
            raise ValueError("positive exact tree mode and symplectic norm required")
        units.append(ctx.matrix([-1j*aa, 1, -1j*bb])/ctx.sqrt(norm))
        energies.append(energy)
    energy, unit = energies[0], units[0]
    e = energy*energy
    aa0, bb0, dd = 2*u*s+p*p-e, p*p-e, vcurv+kp*(p*p-e)
    polynomial_p = 2*p*((aa0+bb0)*dd+kp*(aa0*bb0-4*mu*mu*e)-g*g*s)
    velocity = -polynomial_p/(2*energy*polynomial_e(e))
    dd_p = 2*kp*(p-energy*velocity)
    denominator = aa0-g*g*s/dd
    denominator_p = 2*(p-energy*velocity)+g*g*s*dd_p/(dd*dd)
    aa = 2*mu*energy/denominator
    aa_p = 2*mu*(velocity*denominator-energy*denominator_p)/(denominator*denominator)
    bb, bb_p = g*v*aa/dd, g*v*(aa_p/dd-aa*dd_p/(dd*dd))
    norm = 1+aa*aa+kp*bb*bb+2*mu*aa/energy
    norm_p = 2*aa*aa_p+2*kp*bb*bb_p+2*mu*(aa_p/energy-aa*velocity/(energy*energy))
    unit_p = ctx.matrix([-1j*aa_p, 0, -1j*bb_p])/ctx.sqrt(norm)-unit*norm_p/(2*norm)
    vector = ctx.matrix(list(unit)+list(-1j*energy*unit))
    vector_p = ctx.matrix(list(unit_p)+list(-1j*(velocity*unit+energy*unit_p)))
    occupation = 1/ctx.expm1(energy/temperature) if temperature else ctx.mpf(0)
    occupation_p = -occupation*(1+occupation)*velocity/temperature if temperature else ctx.mpf(0)
    outer = ctx.matrix(6, 6)
    outer_p = ctx.matrix(6, 6)
    for i in range(6):
        for j in range(6):
            outer[i, j] = ctx.re(vector[i]*ctx.conj(vector[j]))
            outer_p[i, j] = ctx.re(vector_p[i]*ctx.conj(vector[j])+vector[i]*ctx.conj(vector_p[j]))
    covariance = outer*occupation/energy
    covariance_p = outer*(occupation_p/energy-occupation*velocity/(energy*energy))+outer_p*occupation/energy
    basis, eigenvalues = ctx.matrix(6, 6), []
    for column in range(6):
        index = column % 3
        signed_energy = energies[index] if column < 3 else -energies[index]
        signed_unit = units[index] if column < 3 else units[index].conjugate()
        for row in range(3):
            basis[row, column], basis[row+3, column] = signed_unit[row], -1j*signed_energy*signed_unit[row]
        eigenvalues.append(-1j*signed_energy)
    return {"ctx": ctx, "real": real, "p": p, "mu": mu, "s": s, "v": v, "kinetic": kinetic,
            "potential": potential, "linear": linear, "rotation": rotation, "cubic": cubic, "quartic_phi": eps*lam,
            "covariance": covariance, "covariance_p": covariance_p, "basis": basis, "inverse": basis**-1,
            "eigenvalues": eigenvalues, "group_velocity": velocity}


def extended_source(blocks, ray):
    ctx, mu, v, s = (blocks[k] for k in ("ctx", "mu", "v", "s"))
    ray = ctx.mpc(str(float(complex(ray).real)), str(float(complex(ray).imag)))
    active = (0, 2)
    block = ctx.matrix([[blocks["potential"][i, j] for j in active] for i in active])
    source = ctx.lu_solve(block, ctx.matrix([0, 1]))
    chemical = ctx.lu_solve(block, ctx.matrix([2*mu*v, 0]))
    susceptibility, mixed = s+2*mu*v*chemical[0], 2*mu*v*source[0]
    dmu, dxi = ray*ray*mixed/(s-ray*ray*susceptibility), -ray*mixed/(s-ray*ray*susceptibility)
    mean = ctx.matrix([source[0]+chemical[0]*dmu, 0, source[1]+chemical[1]*dmu])
    return mean, dmu, dxi, -1j*dxi, ray


def extended_contact(blocks, covariance):
    ctx, cubic = blocks["ctx"], blocks["cubic"]
    force = ctx.matrix([sum(cubic[i][a, b]*covariance[a, b] for a in range(3) for b in range(3))/2 for i in range(3)])
    seagull = ctx.matrix(3, 3)
    u = cubic[0][0, 0]/(6*blocks["v"])
    seagull[0, 0], seagull[1, 1] = u*(3*covariance[0, 0]+covariance[1, 1]), u*(covariance[0, 0]+3*covariance[1, 1])
    seagull[0, 1] = seagull[1, 0] = u*(covariance[0, 1]+covariance[1, 0])
    seagull[2, 2] = 3*blocks["quartic_phi"]*covariance[2, 2]
    active = (0, 2)
    shift = ctx.lu_solve(ctx.matrix([[blocks["potential"][i, j] for j in active] for i in active]), -ctx.matrix([force[i] for i in active]))
    return seagull+cubic[0]*shift[0]+cubic[2]*shift[1]


def extended_projection(blocks, covariance, mean, dmu, dxi, current, contact):
    force = blocks["ctx"].matrix([sum(blocks["cubic"][i][a, b]*covariance[a, b] for a in range(3) for b in range(3))/2 for i in range(3)])
    density = blocks["mu"]*(covariance[0, 0]+covariance[1, 1])+(covariance[0, 4]+covariance[4, 0]-covariance[1, 3]-covariance[3, 1])/2
    density += dmu*(blocks["covariance"][0, 0]+blocks["covariance"][1, 1])
    force += contact*mean
    return -mean[0]*force[0]-mean[2]*force[2]+dmu*density+dxi*current


def extended_soft(p, cosine, ray, temperature, state, action, angular=False, digits=50, prepared=None):
    stationary_soft_source(ray, state, action)
    if not isfinite(cosine) or abs(cosine) > 1:
        raise ValueError("physical cosine required")
    blocks = extended_gaussian_state(p, temperature, state, action, digits) if prepared is None else prepared
    ctx, covariance, covariance_p, inverse, basis = (blocks[k] for k in ("ctx", "covariance", "covariance_p", "inverse", "basis"))
    mean, dmu, dxi, theta, ray = extended_source(blocks, ray)
    common = -(blocks["kinetic"]**-1)*(blocks["cubic"][0]*mean[0]+blocks["cubic"][2]*mean[2])+ctx.diag([2*blocks["mu"]*dmu, 2*blocks["mu"]*dmu, 0])
    common[1, 1] = 0
    base, angle, left_p, right_p, generator_p = (ctx.matrix(6, 6) for _ in range(5))
    for i in range(3):
        for j in range(3):
            rotation = blocks["rotation"][i, j]
            base[i+3, j], base[i+3, j+3] = common[i, j], 2j*ray*theta*rotation
            angle[i+3, j] = -2*blocks["p"]*theta*rotation
            left_p[i+3, j], right_p[i+3, j] = theta*(ray*ray-1)*rotation, theta*(ray*ray+1)*rotation
        generator_p[i+3, i] = -2*blocks["p"]
    rhs0 = [inverse*(base*covariance+covariance*base.T)*inverse.T, inverse*(angle*covariance-covariance*angle.T)*inverse.T]
    rhs1 = [inverse*(left_p*covariance+covariance*right_p.T)*inverse.T, inverse*covariance_p*base.T*inverse.T, -inverse*covariance_p*angle.T*inverse.T]
    drift = inverse*generator_p*basis
    off = [ctx.matrix(6, 6), ctx.matrix(6, 6)]
    zero_pairs = {(i, i+3) for i in range(3)} | {(i+3, i) for i in range(3)}
    for i in range(6):
        for j in range(6):
            if (i, j) not in zero_pairs:
                for k in range(2):
                    off[k][i, j] = rhs0[k][i, j]/(-blocks["eigenvalues"][i]-blocks["eigenvalues"][j])
    numerator = [rhs1[0], rhs1[1]+drift*off[0], rhs1[2]+drift*off[1]]
    if angular:
        average, weighted = off[0].copy(), off[1]/3
        for i, j in zero_pairs:
            a, b = -1j*ray, -drift[i, i]
            if ray == 0:
                average[i, j], weighted[i, j] = numerator[1][i, j]/b, 0
            else:
                moments = [(ctx.log(1+b/a)-ctx.log(1-b/a))/(2*b)]
                # Extended precision makes the exact recursion well conditioned at this grid.
                for k in range(1, 4):
                    moments.append(((ctx.mpf(1)/k if (k-1) % 2 == 0 else 0)-a*moments[-1])/b)
                average[i, j] = sum(numerator[k][i, j]*moments[k] for k in range(3))
                weighted[i, j] = sum(numerator[k][i, j]*moments[k+1] for k in range(3))
        result, weighted = basis*average*basis.T, basis*weighted*basis.T
        current = 1j*blocks["p"]*(weighted[0, 1]-weighted[1, 0])+dxi*blocks["p"]*(covariance_p[0, 0]+covariance_p[1, 1])/3
    else:
        t = blocks["real"](cosine)
        result = off[0]+t*off[1]
        for i, j in zero_pairs:
            if ray == 0:
                result[i, j] = numerator[1][i, j]/(-drift[i, i])
            else:
                result[i, j] = sum(numerator[k][i, j]*t**k for k in range(3))/(-1j*ray-t*drift[i, i])
        result = basis*result*basis.T
        current = 1j*blocks["p"]*t*(result[0, 1]-result[1, 0])+dxi*blocks["p"]*t*t*(covariance_p[0, 0]+covariance_p[1, 1])
    chi = extended_projection(blocks, result, mean, dmu, dxi, current, extended_contact(blocks, covariance))
    return {"chi": complex(chi), "local_covariance": np.array(result.tolist(), dtype=complex)}


def extended_finite(p, cosine, q, ray, temperature, state, action, digits=50):
    finite_local_covariance(p, cosine, q, ray, temperature, state, action)
    blocks = extended_gaussian_state(p, temperature, state, action, digits)
    ctx, real = blocks["ctx"], blocks["real"]
    p, q, t = real(p), real(q), real(cosine)
    ray = ctx.mpc(str(float(complex(ray).real)), str(float(complex(ray).imag)))
    z, r = ray*q, ctx.sqrt(p*p+2*p*q*t+q*q)
    other = extended_gaussian_state(r, temperature, state, action, digits, context=ctx)
    mean = ctx.lu_solve(blocks["potential"]+(q*q-z*z)*blocks["kinetic"]+z*blocks["linear"], ctx.matrix([0, 0, 1]))
    theta, dmu, dxi = mean[1]/blocks["v"], -1j*z*mean[1]/blocks["v"], 1j*q*mean[1]/blocks["v"]
    common = -(blocks["kinetic"]**-1)*(blocks["cubic"][0]*mean[0]+blocks["cubic"][2]*mean[2])+ctx.diag([2*blocks["mu"]*dmu, 2*blocks["mu"]*dmu, 0])
    common[1, 1] = (q*q-z*z)*mean[0]/blocks["v"]
    left, right = ctx.matrix(6, 6), ctx.matrix(6, 6)
    for i in range(3):
        for j in range(3):
            rotation = blocks["rotation"][i, j]
            left[i+3, j] = common[i, j]+theta*(z*z-r*r+p*p)*rotation
            right[i+3, j] = common[i, j]+theta*(z*z+r*r-p*p)*rotation
            left[i+3, j+3] = right[i+3, j+3] = 2j*z*theta*rotation
    rhs = other["inverse"]*(left*blocks["covariance"]+other["covariance"]*right.T)*blocks["inverse"].T
    for i in range(6):
        for j in range(6):
            rhs[i, j] /= -1j*z-other["eigenvalues"][i]-blocks["eigenvalues"][j]
    result = other["basis"]*rhs*blocks["basis"].T
    cp, cr = blocks["covariance"], other["covariance"]
    current = 1j*(2*p*t+q)*(result[0, 1]-result[1, 0])/2+1j*(2*p*t+q)*theta*(cr[0, 0]+cr[1, 1]-cp[0, 0]-cp[1, 1])/2
    chi = extended_projection(blocks, result, mean, dmu, dxi, current, extended_contact(blocks, (cp+cr)/2))
    chi += dmu*dmu*(cr[0, 0]+cr[1, 1]-cp[0, 0]-cp[1, 1])/2
    return {"chi": complex(chi), "local_covariance": np.array(result.tolist(), dtype=complex)}


def extended_thermal(ray, temperature, state, action, order=24, tail=40., digits=50):
    TH.validate(.02, temperature, state, action, order)
    stationary_soft_source(ray, state, action)
    if temperature == 0:
        return 0j
    c = INT.dispersion_coefficients(state, action)["c"]
    values = []
    for x, weight in TH.radial_nodes(order, tail):
        p = temperature*x/c
        values.append(weight*temperature/c*p*p/(2*pi*pi)*extended_soft(p, 0., ray, temperature, state, action, angular=True, digits=digits)["chi"])
    return complex(sum(values))


def full_domain_nodes(order, split):
    """Bose momentum domain is [0,infinity); split is not a physical cutoff."""
    yield from TH.radial_nodes(order, split)
    nodes, weights = np.polynomial.legendre.leggauss(order)
    for node, weight in zip(nodes, weights):
        t = (node+1)/2
        yield split+t/(1-t), weight/(2*(1-t)**2)


def full_domain_thermal_batch(rays, temperature, state, action, order=24, split=40., digits=50):
    TH.validate(.02, temperature, state, action, order)
    for ray in rays:
        stationary_soft_source(ray, state, action)
    if temperature == 0:
        return [{"chi": 0j, "truncated_chi": 0j, "tail_chi": 0j} for _ in rays]
    c = INT.dispersion_coefficients(state, action)["c"]
    core, tail = [[] for _ in rays], [[] for _ in rays]
    for x, weight in full_domain_nodes(order, split):
        p = temperature*x/c
        blocks = extended_gaussian_state(p, temperature, state, action, digits)
        for i, ray in enumerate(rays):
            chi = extended_soft(p, 0., ray, temperature, state, action, angular=True, digits=digits, prepared=blocks)["chi"]
            term = weight*temperature/c*p*p/(2*pi*pi)*chi
            (core if x < split else tail)[i].append(term)
    accurate_sum = lambda values: complex(fsum(value.real for value in values), fsum(value.imag for value in values))
    return [{"chi": accurate_sum(core[i]+tail[i]), "truncated_chi": accurate_sum(core[i]), "tail_chi": accurate_sum(tail[i])} for i in range(len(rays))]


def audit():
    action, point_rows, jet_rows, transform_rows, thermal_rows, angular_rows, precision_rows = EFT.controls(), [], [], [], [], [], []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        c = INT.dispersion_coefficients(state, action)["c"]
        for p in MOMENTA:
            covariance, derivative = covariance_momentum_jet(p, TEMPERATURE, state, action)
            step = p*1e-4
            plus = FQ.evolution_and_covariance(p+step, TEMPERATURE, state, action)[1]
            minus = FQ.evolution_and_covariance(p-step, TEMPERATURE, state, action)[1]
            jet_rows.append({"mu": mu, "p": p, "step": step,
                             "covariance_error": VIRT.matrix_error(covariance, FQ.evolution_and_covariance(p, TEMPERATURE, state, action)[1]),
                             "derivative_error": VIRT.matrix_error(derivative, (plus-minus)/(2*step))})
            for ratio in RAY_RATIOS:
                ray = c*ratio
                system = soft_system(p, ray, TEMPERATURE, state, action)
                for cosine in COSINES:
                    fixed = soft_point(p, cosine, ray, TEMPERATURE, state, action, system)
                    differences, fixed_centre = [], []
                    extended_target = extended_soft(p, cosine, ray, TEMPERATURE, state, action)
                    for q_ratio in Q_OVER_P:
                        q = p*q_ratio
                        finite = finite_local_covariance(p, cosine, q, ray, TEMPERATURE, state, action)
                        k, t = centre(p, cosine, q)
                        centred = soft_point(k, t, ray, TEMPERATURE, state, action)
                        tree = FQ.source_response(q, ray*q, state, action)
                        differences.append({"q_over_p": q_ratio, "q": q, "centre_p": k, "centre_cosine": t,
                            "finite_chi": VIRT.encode_complex(finite["pair_chi"]), "centred_soft_chi": VIRT.encode_complex(centred["chi"]),
                            "raw_fixed_p_chi_error": INT.relative(finite["pair_chi"], fixed["chi"]),
                            "raw_fixed_p_covariance_error": VIRT.matrix_error(finite["local_covariance"], fixed["local_covariance"]),
                            "centred_chi_error": INT.relative(finite["pair_chi"], centred["chi"]),
                            "centred_covariance_error": VIRT.matrix_error(finite["local_covariance"], centred["local_covariance"]),
                            "tree_source_ray_error": VIRT.matrix_error(tree[[0, 2], None], system["source"]["mean"][[0, 2], None])})
                        paired_p, paired_cosine = pair_from_centre(p, cosine, q)
                        matched = extended_finite(paired_p, paired_cosine, q, ray, TEMPERATURE, state, action)
                        fixed_centre.append({"q_over_centre_p": q_ratio, "left_p": paired_p, "left_cosine": paired_cosine,
                            "q": q, "finite_chi": VIRT.encode_complex(matched["chi"]), "chi_error": INT.relative(matched["chi"], extended_target["chi"]),
                            "covariance_error": VIRT.matrix_error(matched["local_covariance"], extended_target["local_covariance"])})
                    point_rows.append({"mu": mu, "p": p, "cosine": cosine, "ray": VIRT.encode_complex(ray),
                        "soft_chi": VIRT.encode_complex(fixed["chi"]), "zero_drive_error": fixed["zero_drive_error"],
                        "raw_stationary_phase_cancellation": VIRT.encode_complex(system["raw_stationary_phase_cancellation"]),
                        "extended_method_error": INT.relative(fixed["chi"], extended_target["chi"]), "differences": differences, "fixed_centre_differences": fixed_centre})
        # The independent Cartesian scalar is checked away from ill-conditioned tiny-q cancellation.
        for p, r, q in NOE.MOMENTUM_TRIPLES[:3]:
            cosine = (r*r-p*p-q*q)/(2*p*q)
            for z in NOE.FREQUENCIES:
                local = finite_local_covariance(p, cosine, q, z/q, TEMPERATURE, state, action)
                drive = FQ.source_response(q, z, state, action)
                old, average, _ = NOE.covariance_response(p, r, z, TEMPERATURE, drive, state, action)
                contact = NOE.pair_contact(average, state, action)[0]
                direct = FQ.source_response(q, -z, state, action)@(FQ.paired_bubble(p, r, z, TEMPERATURE, state, action)-contact)@drive
                transform_rows.append({"mu": mu, "p": p, "r": r, "q": q, "z": VIRT.encode_complex(z),
                    "covariance_error": VIRT.matrix_error(old, local["cartesian_covariance"]), "projection_error": INT.relative(direct, local["pair_chi"])})
        for ray in (0j,)+tuple(c*w for w in RAY_RATIOS):
            reference = soft_angular(.02, ray, TEMPERATURE, state, action)
            values = [soft_angular(.02, ray, TEMPERATURE, state, action, n) for n in ANGULAR_ORDERS]
            angular_rows.append({"mu": mu, "ray": VIRT.encode_complex(ray), "analytic_chi": VIRT.encode_complex(reference),
                "orders": ANGULAR_ORDERS, "errors": [INT.relative(x, reference) for x in values], "finest_difference": INT.relative(values[-1], values[-2])})
        scale = INT.dispersion_coefficients(state, action)["dispersion_scale"]
        for divisor in (256, 512):
            temperature = c*scale/divisor
            rays = (0j,)+tuple(c*w for w in RAY_RATIOS)
            batches = [full_domain_thermal_batch(rays, temperature, state, action, n, TAILS[-1]) for n in ORDERS]
            short_batch = full_domain_thermal_batch(rays, temperature, state, action, ORDERS[-1], TAILS[0])
            for index, ray in enumerate(rays):
                values = [batch[index]["chi"] for batch in batches]
                short_tail = short_batch[index]["chi"]
                target = CURV.thermal_response(temperature, state, action, ORDERS[-1])["chi_thermal"] if ray == 0 else None
                thermal_rows.append({"mu": mu, "T": temperature, "T_scale_divisor": divisor, "ray": VIRT.encode_complex(ray),
                    "orders": ORDERS, "values": [VIRT.encode_complex(x) for x in values], "refinement_errors": [INT.relative(values[i+1], values[i]) for i in range(2)],
                    "full_domain_split": TAILS[-1], "tail_complement": VIRT.encode_complex(batches[-1][index]["tail_chi"]),
                    "truncated_32_40_error_retained": INT.relative(batches[-1][index]["truncated_chi"], short_batch[index]["truncated_chi"]),
                    "tail_error": INT.relative(values[-1], short_tail), "pressure_hessian_target": float(target) if target is not None else None,
                    "static_hessian_error": INT.relative(values[-1], target) if target is not None else None})
        ray = (.6+.4j)*c
        low = extended_soft(.02, .3, ray, TEMPERATURE, state, action, digits=35)
        high = extended_soft(.02, .3, ray, TEMPERATURE, state, action, digits=50)
        precision_rows.append({"mu": mu, "digits": [35, 50], "source_error": INT.relative(low["chi"], high["chi"]),
                               "covariance_error": VIRT.matrix_error(low["local_covariance"], high["local_covariance"])})
    checks = {
        "analytic_covariance_and_momentum_jet": all(row["covariance_error"] < GATES["identity_relative"] and row["derivative_error"] < GATES["covariance_FD_relative"] for row in jet_rows),
        "exact_zero_channel_drive_cancellation": all(row["zero_drive_error"] < GATES["identity_relative"] for row in point_rows),
        "local_rotation_matches_cartesian_covariance_and_projection": all(max(row["covariance_error"], row["projection_error"]) < GATES["method_relative"] for row in transform_rows),
        "centred_soft_covariance_and_source_converge": all(max(row["differences"][-1]["centred_covariance_error"], row["differences"][-1]["centred_chi_error"], row["differences"][-1]["tree_source_ray_error"]) < GATES["point_soft_relative"] for row in point_rows),
        "fixed_centre_refinement_improves_covariance_and_chi": all(all(row["fixed_centre_differences"][i+1][key] < row["fixed_centre_differences"][i][key] for i in range(2)) for row in point_rows for key in ("covariance_error", "chi_error")),
        "extended_precision_agrees_and_fixed_centre_error_is_small": all(row["extended_method_error"] < GATES["method_relative"] and max(row["fixed_centre_differences"][-1]["chi_error"], row["fixed_centre_differences"][-1]["covariance_error"]) < GATES["point_soft_relative"] for row in point_rows) and all(max(row["source_error"], row["covariance_error"]) < GATES["method_relative"] for row in precision_rows),
        "analytic_angular_transport_matches_quadrature": all(max(row["errors"][-1], row["finest_difference"]) < GATES["method_relative"] for row in angular_rows),
        "radial_refinement": all(row["refinement_errors"][-1] < GATES["quadrature_relative"] for row in thermal_rows),
        "full_domain_split_and_tail_complement": all(row["tail_error"] < GATES["tail_relative"] for row in thermal_rows),
        "independent_static_pressure_hessian": all(row["static_hessian_error"] < GATES["identity_relative"] for row in thermal_rows if row["static_hessian_error"] is not None),
    }
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY, PREFIX+"Code/03_Research/test_t13_collisionless_soft_source.py"]
    protected = [PREFIX+"Result/artifacts/t13_thermal_noether_response.json", PREFIX+"Code/03_Research/Research_T13_Thermal_Noether_Response.py",
                 PREFIX+"Result/artifacts/t13_finite_q_thermal_source.json", PREFIX+"Result/artifacts/t13_thermal_source_curvature.json",
                 PREFIX+"Result/artifacts/t13_collisionless_soft_source_first_failure.json"]+list(EFT.ACTION_PATHS)
    passed = all(checks.values())
    record = {"major_result_id": "T13_GAUSSIAN_COLLISIONLESS_SOFT_RAY_SOURCE_RESPONSE", "topic": "0.13_Thermodynamic_Bridge", "branch_id": VIRT.BRANCH,
        "created_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "verification_status": "PASS_SCOPED_COLLISIONLESS_SOFT_SOURCE" if passed else "FAIL_SCOPED_COLLISIONLESS_SOFT_SOURCE",
        "what_is_closed": "Analytic Gaussian collisionless source ray including six exact streaming channels, centred finite-q convergence and independent static pressure-Hessian endpoint, conditional on checks",
        "equation_or_mapping": "z=w*q; X_zero=(N0+t*N1+t^2*N2)/(-i*w-t*H_ii); angular logarithmic moments integrate streaming denominators without a collision rate",
        "units": {"p_q_z_mu_T": "E", "ray_group_velocity": "E^0", "h": "E^3", "Phi": "E", "integrated_chi_Phi_per_h": "E^-2"},
        "derivation_class": "DERIVED_SINGULAR_PERTURBATION_OF_NAMED_GAUSSIAN_COVARIANCE", "observable": "conditional complex-frequency natural-unit action-source susceptibility, not physical temperature or heat response",
        "data_role": "DERIVED_NOT_CALIBRATION", "action_controls": action, "checks": checks,
        "point_examples": point_rows, "covariance_jet_examples": jet_rows, "rotation_examples": transform_rows, "angular_examples": angular_rows, "thermal_examples": thermal_rows, "precision_examples": precision_rows,
        "declared_grids": {"mu": MU_GRID, "momenta": MOMENTA, "cosines": COSINES, "point_T": TEMPERATURE,
            "ray_over_sound_speed": [VIRT.encode_complex(w) for w in RAY_RATIOS], "q_over_p": Q_OVER_P, "orders": ORDERS,
            "angular_orders": ANGULAR_ORDERS, "tails": TAILS, "thermal_scale_divisors": [256, 512], "momentum_FD_fraction": 1e-4, "locked_before_first_audit": True},
        "thresholds": GATES, "matching_convention": "Exact vector centre k=p_vector+q_vector/2; convergence sequence holds k fixed. Raw fixed-p/moving-centre errors retained, not fitted shifts",
        "numerical_repair": {"first_failure_preserved": True, "original_grids_and_thresholds_unchanged": True,
            "corrected_protocol_declared_after_first_failure_before_corrected_audit": True,
            "fixed_centre_protocol_corrected": True, "finite_truncated_tail_gate_still_fails": any(row["truncated_32_40_error_retained"] > GATES["tail_relative"] for row in thermal_rows),
            "momentum_integral": "Full [0,infinity) Bose domain; 32/40 are numerical split positions with explicit rational-map tail complement, not causal cone padding",
            "precision_digits": 50, "precision_control_digits": 35, "precision_is_not_physical_input_accuracy": True},
        "angular_evaluation": "Logarithmic moments or convergent fixed 64-term series when abs(b/a)<1/4; static removable numerator resolved analytically, no filter",
        "equation_registry_ids": [x["id"] for x in json.loads((ROOT/REGISTRY).read_text())["entries"]],
        "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
        "controlling_blocker": "full_interacting_work_entropy_and_physical_heat_source_transport_open",
        "open_blockers": ["full_interacting_vacuum_thermal_matching_and_truncation_control", "second_order_source_work_entropy_and_dissipative_balance",
                          "collision_operator_and_hydrodynamic_transport", "independent_material_heat_source_readout_scale_and_uncertainty"],
        "dependency_unlocked": ["source_work_entropy_and_physical_heat_source_mapping_research_only"] if passed else [],
        "gaussian_collisionless_soft_ray_response_closed": passed, "static_pressure_endpoint_checked_for_prescription": passed,
        "full_loop_source_current_Ward_closed": False, "full_energy_exchange_ledger_closed": False, "full_collision_operator_computed": False,
        "physical_Kubo_emitted": False, "full_SK_KMS_matching_closed": False, "full_off_shell_source_matching_closed": False,
        "full_real_self_energy_matched": False, "full_two_loop_pressure_computed": False, "all_parent_modes_and_quantum_Phi_loops_included": False,
        "independent_alpha_Phi_K_admitted": False, "controlled_full_action_truncation_error_established": False,
        "full_core_unlock": False, "core_composition_gate_overwritten": False, "claim_promotion": False,
        "state_variables": ["classical_tree_radial_phase_Phi_fluctuations_and_covariance_velocities"], "excluded_variables": ["C", "UET_Pi", "R_gen", "R_obs"],
        "parameter_fitting": False, "assigned_width": False, "assigned_relaxation_time": False, "clipping": False, "cone_padding": False,
        "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED", "original_causal_status": "FAILED_CONSERVED_C_BASELINE_NOT_RETESTED_OR_REPAIRED",
        "primary_references": ["https://arxiv.org/abs/cond-mat/0307246", "https://arxiv.org/abs/2310.01988"],
        "claim_boundary": "Named acoustic-populated Gaussian soft ray and declared complex-frequency grids only. Full-domain momentum translation and source convention explicit; not continuum-interacting proof, hydrodynamic collisions, second-order heating/entropy, physical readout/alpha/Kubo or Full Topic13/Core/global closure."}
    fields = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(fields, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"],
        "Resolved exact streaming channels and derived angular/static source limit", record["equation_or_mapping"], checks, record["controlling_blocker"],
        "Actual source work/heat-readout and independent material mapping; interacting/collision/entropy completion without assigned rates", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"]}, indent=2))
    raise SystemExit(0 if all(record["checks"].values()) else 1)
