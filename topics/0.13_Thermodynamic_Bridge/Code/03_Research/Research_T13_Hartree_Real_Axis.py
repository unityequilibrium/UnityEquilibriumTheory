"""Retarded angular principal value and exact on-shell Hartree loop cuts.

No imaginary width is assigned on the real axis. A is still a nondynamical
O2 source; the declared stationary witnesses and current subtraction are kept.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
CURRENT_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_Gauge_Current.py"
CURRENT_ARTIFACT = PREFIX+"Result/artifacts/t13_hartree_gauge_current.json"
G = runpy.run_path(str(ROOT/CURRENT_CODE))
F = G["F"]
H = G["H"]
BASIS = G["BASIS"]
ROTATION = G["ROTATION"]
SOURCE_METRIC = np.diag([1., 1., 1., -1., 1.])
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_real_axis.json")
ORDERS = ((48, 48), (64, 64), (80, 80))
POINT_TOLERANCE = G["POINT_TOLERANCE"]
QUADRATURE_TOLERANCE = G["QUADRATURE_TOLERANCE"]
WARD_TOLERANCE = G["WARD_TOLERANCE"]


def validate(q, frequency, t, mu, a, b):
    F["validate"](t, mu, a, b, q, 0j)
    if q == 0:
        raise ValueError("q>0 required for this angular reduction; q=0 is a separate limit")
    if not np.isfinite(frequency) or complex(frequency).imag < 0:
        raise ValueError("finite real or upper-half-plane frequency required")


def inverse_shell(ell, index, mu, a, b):
    """Invert the same internal dispersion, without adding or changing a gap."""
    ell = np.asarray(ell, np.longdouble)
    if index not in (0, 1, 2, 3):
        raise ValueError("one of four declared pole branches required")
    residue = np.zeros(ell.shape+(2, 2), np.clongdouble)
    if mu == 0:
        field = 0 if index in (0, 2) else 1
        k_sq = ell*ell-(a if field == 0 else b)
        derivative = 2*ell
        residue[..., field, field] = -1/derivative
    else:
        mu, a, b = map(np.longdouble, (mu, a, b))
        branch = 1 if index in (1, 2) else -1
        discriminant = np.sqrt((a-b)**2/4+4*mu*mu*ell*ell)
        k_sq = ell*ell-(a+b)/2+branch*discriminant
        derivative = 2*ell*(1+branch*2*mu*mu/discriminant)
        determinant_derivative = 4*ell*(-branch*discriminant-2*mu*mu)
        residue[..., 0, 0] = ((b-a)/2+branch*discriminant)/determinant_derivative
        residue[..., 1, 1] = ((a-b)/2+branch*discriminant)/determinant_derivative
        residue[..., 0, 1] = -2j*mu*ell/determinant_derivative
        residue[..., 1, 0] = 2j*mu*ell/determinant_derivative
    return k_sq, derivative, residue


def shell_coefficient(k, q, p, rp, ell, index, frequency, t, mu, a, b):
    """Numerator times exact dc/dell; source order is mass(3), time, long."""
    k, p, ell = np.broadcast_arrays(k, p, ell)
    k_sq, derivative, re = inverse_shell(ell, index, mu, a, b)
    jacobian = np.abs(derivative)/(2*k*q)
    kz = (k_sq-k*k)/(2*q)
    transverse_sq = ((k+q)**2-k_sq)*(k_sq-(k-q)**2)/(4*q*q)
    operators = np.zeros(ell.shape+(5, 2, 2), np.clongdouble)
    operators[..., :3, :, :] = BASIS
    operators[..., 3, :, :] = -(2*p+frequency)[..., None, None]*ROTATION+2j*mu*np.eye(2)
    operators[..., 4, :, :] = -2j*kz[..., None, None]*ROTATION
    coefficient = np.einsum("...aij,...jk,...bkl,...li->...ab", operators, re, operators, rp)
    occupation = G["occupations"](p, t)-G["occupations"](ell, t)
    coefficient *= (.5*occupation*jacobian)[..., None, None]
    transverse = -transverse_sq*np.einsum("ij,...jk,kl,...li->...", ROTATION, re, ROTATION, rp)*occupation*jacobian
    return coefficient, transverse


def angular_kernel(k, q, frequency, t, mu, a, b, order=48):
    """Cauchy subtraction in the outgoing pole energy, not width smearing."""
    validate(q, frequency, t, mu, a, b)
    if isinstance(order, bool) or not isinstance(order, int) or order < 16:
        raise ValueError("integer angular order>=16 required")
    k = np.atleast_1d(np.asarray(k, np.longdouble))
    if np.any(~np.isfinite(k)) or np.any(k <= 0):
        raise ValueError("positive finite radial nodes required")
    z = np.clongdouble(frequency)
    p, residues = G["extended_poles"](k, mu, a, b)
    limits1 = G["extended_poles"](np.abs(k-q), mu, a, b)[0]
    limits2 = G["extended_poles"](k+q, mu, a, b)[0]
    nodes, weights = np.polynomial.legendre.leggauss(order)
    nodes = np.asarray((nodes+1)/2, np.longdouble)
    weights = np.asarray(weights/2, np.longdouble)
    result = np.zeros(k.shape+(5, 5), np.clongdouble)
    transverse = np.zeros(k.shape, np.clongdouble)
    cuts = {name: [np.zeros_like(result), np.zeros_like(transverse)] for name in ("pair", "scattering")}
    for index in range(4):
        lo = np.minimum(limits1[:, index], limits2[:, index])
        hi = np.maximum(limits1[:, index], limits2[:, index])
        ell = lo[:, None]+(hi-lo)[:, None]*nodes[None, :]
        w = (hi-lo)[:, None]*weights[None, :]
        ks, derivative, re = inverse_shell(ell, index, mu, a, b)
        jacobian = np.abs(derivative)/(2*k[:, None]*q)
        # S2's surviving polynomial is -2 Tr(I_cov(P+Q)) in the time/time loop.
        result[:, 3, 3] += 2*np.sum(w*np.trace(re, axis1=-2, axis2=-1)*G["occupations"](ell, t)*jacobian, axis=1)
        for incoming in range(4):
            ps = p[:, incoming]
            rp = residues[:, incoming, :, :]
            target = ps+z.real
            inside = (target > lo) & (target < hi)
            if np.any((target == lo) | (target == hi)) and z.imag == 0:
                raise ValueError("radial node is an exact cut endpoint; split radial integration there")
            reference = np.where(inside, target, (lo+hi)/2)
            numerator, tn = shell_coefficient(k[:, None], q, ps[:, None], rp[:, None, :, :], ell,
                                              index, z, t, mu, a, b)
            n0, t0 = shell_coefficient(k, q, ps, rp, reference, index, z, t, mu, a, b)
            denominator = ps[:, None]+z-ell
            integrand = np.divide(numerator-n0[:, None, :, :], denominator[..., None, None],
                                  out=np.zeros_like(numerator), where=denominator[..., None, None] != 0)
            ti = np.divide(tn-t0[:, None], denominator, out=np.zeros_like(tn), where=denominator != 0)
            if np.any(denominator == 0):
                step = np.minimum(reference-lo, hi-reference)*1e-5
                plus, tp = shell_coefficient(k, q, ps, rp, reference+step, index, z, t, mu, a, b)
                minus, tm = shell_coefficient(k, q, ps, rp, reference-step, index, z, t, mu, a, b)
                for row, column in np.argwhere(denominator == 0):
                    integrand[row, column] = -(plus[row]-minus[row])/(2*step[row])
                    ti[row, column] = -(tp[row]-tm[row])/(2*step[row])
            # log1p preserves the UV difference of nearly equal logarithms.
            logarithm = np.log1p((hi-lo)/(ps+z-hi))
            if z.imag == 0:
                logarithm = logarithm.real-1j*pi*inside
            result += np.sum(w[..., None, None]*integrand, axis=1)+n0*logarithm[:, None, None]
            transverse += np.sum(w*ti, axis=1)+t0*logarithm
            if z.imag == 0:
                name = "pair" if (incoming < 2) != (index < 2) else "scattering"
                cuts[name][0] -= pi*n0*inside[:, None, None]
                cuts[name][1] -= pi*t0*inside
    return result, transverse, cuts


def unpack_joint(joint, transverse):
    bubble = 2*joint[..., :3, :3]
    mixed = np.zeros(joint.shape[:-2]+(3, 4), complex)
    reverse = np.zeros(joint.shape[:-2]+(4, 3), complex)
    current = np.zeros(joint.shape[:-2]+(4, 4), complex)
    mixed[..., :, :2] = 2*joint[..., :3, 3:5]
    reverse[..., :2, :] = 2*joint[..., 3:5, :3]
    current[..., :2, :2] = joint[..., 3:5, 3:5]
    current[..., 2, 2] = current[..., 3, 3] = transverse
    return np.asarray(bubble, complex), mixed, reverse, current


def direct_angular_check(k, q, frequency, t, mu, a, b, order=128):
    validate(q, frequency, t, mu, a, b)
    if complex(frequency).imag == 0:
        raise ValueError("unsplit angular quadrature is only an independent upper-half-plane check")
    c, w = np.polynomial.legendre.leggauss(order)
    shifted = np.sqrt(k*k+q*q+2*k*q*c)
    bubble = np.sum(w[:, None, None]*F["point_bubble"](k, shifted, t, mu, a, b, frequency), axis=0)
    mixed, reverse, current = G["point_gauge"](k, shifted, k*c+q/2, t, mu, a, b, frequency)
    transverse = G["point_transverse"](k, shifted, k*k*(1-c*c), t, mu, a, b, frequency)
    expected = (bubble, np.sum(w[:, None, None]*mixed, axis=0), np.sum(w[:, None, None]*reverse, axis=0),
                np.sum(w[:, None, None]*current, axis=0))
    joint, tr, _ = angular_kernel(k, q, frequency, t, mu, a, b, order=64)
    actual = unpack_joint(joint[0], tr[0])
    return {"joint_max_error": float(max(np.max(np.abs(actual[0]-expected[0])),
                                         np.max(np.abs(actual[1][:, :2]-expected[1])),
                                         np.max(np.abs(actual[2][:2, :]-expected[2])))),
            "current_block_error": float(np.max(np.abs(actual[3][:2, :2]-expected[3]))),
            "transverse_error": float(abs(actual[3][2, 2]-np.sum(w*transverse)))}


def radial_endpoints(q, omega, mu, a, b, scan_order=512):
    """Kinematic endpoints are quadrature splits, not excluded momentum bands."""
    validate(q, omega, 0., mu, a, b)
    if isinstance(scan_order, bool) or not isinstance(scan_order, int) or scan_order < 128:
        raise ValueError("endpoint scan order>=128 required")
    scale = max(mu, sqrt(a), sqrt(b), q, abs(omega), 1.)
    grid = np.unique(np.r_[0., q, np.geomspace(q/10000, scale*1000, scan_order)])
    incoming = G["extended_poles"](grid, mu, a, b)[0]
    roots = [q]
    for side in (-1, 1):
        outgoing = G["extended_poles"](np.abs(grid+side*q), mu, a, b)[0]
        for first in range(4):
            for second in range(4):
                values = omega+incoming[:, first]-outgoing[:, second]
                for j in np.flatnonzero(values[:-1]*values[1:] < 0):
                    def function(k):
                        return float(omega+G["extended_poles"](k, mu, a, b)[0][first]
                                     -G["extended_poles"](abs(k+side*q), mu, a, b)[0][second])
                    root = brentq(function, grid[j], grid[j+1], xtol=1e-12)
                    if not any(np.isclose(root, value, atol=1e-10, rtol=1e-8) for value in roots):
                        roots.append(root)
    return sorted(roots)


def vacuum_reference(q, frequency, mass_sq=1., scale=1.):
    """4D Feynman parameter PV with analytic imaginary pair phase space."""
    validate(q, frequency, 0., 0., mass_sq, mass_sq)
    if min(mass_sq, scale) <= 0:
        raise ValueError("positive vacuum reference scales required")
    z = complex(frequency)
    invariant = q*q-z*z
    if z.imag > 0:
        x, w = np.polynomial.legendre.leggauss(128)
        x, w = (x+1)/2, w/2
        logs = np.log((mass_sq+x*(1-x)*invariant)/scale**2)
        bubble_scalar = np.sum(w*logs)/(16*pi*pi)
        coefficient = -np.sum(w*(1-2*x)**2*logs)/(16*pi*pi)
    else:
        s = z.real*z.real-q*q
        roots = []
        beta = 0.
        if s >= 4*mass_sq:
            beta = sqrt(1-4*mass_sq/s)
            roots = sorted(set(((1-beta)/2, (1+beta)/2)))
        def logarithm(x):
            return np.log(abs((mass_sq+x*(1-x)*invariant.real)/scale**2))
        real_bubble = quad(logarithm, 0., 1., points=roots, epsabs=1e-11)[0]
        real_current = quad(lambda x: (1-2*x)**2*logarithm(x), 0., 1., points=roots, epsabs=1e-11)[0]
        bubble_scalar = real_bubble/(16*pi*pi)-1j*np.sign(z.real)*beta/(16*pi)
        coefficient = -real_current/(16*pi*pi)+1j*np.sign(z.real)*beta**3/(48*pi)
    qe = np.array([-1j*z, q, 0., 0.])
    current = coefficient*(invariant*np.eye(4)-np.outer(qe, qe))
    return bubble_scalar*np.eye(3), current


def radial_nodes(q, omega, mu, a, b, auxiliary, order, scan_order=512):
    if isinstance(order, bool) or not isinstance(order, int) or order < 16:
        raise ValueError("integer radial order>=16 required")
    endpoints = radial_endpoints(q, omega, mu, a, b, scan_order)
    endpoints += radial_endpoints(q, omega, 0., auxiliary**2, auxiliary**2, scan_order)
    mapping = np.longdouble(max(mu, sqrt(a), sqrt(b), abs(omega), auxiliary, 1.))
    splits = np.unique(np.r_[0., np.asarray(endpoints)/(mapping+np.asarray(endpoints)), 1.])
    nodes, weights = np.polynomial.legendre.leggauss(order)
    u, w = np.asarray((nodes+1)/2, np.longdouble), np.asarray(weights/2, np.longdouble)
    ks, measures = [], []
    for lo, hi in zip(splits[:-1], splits[1:]):
        if hi == 1:
            # k~(1-u)^(-1/2) makes the subtracted dk/k^3 UV tail regular.
            # The entire [left,infinity) interval remains integrated.
            root = np.sqrt((1-u)*(1+u))
            x = lo+(hi-lo)*(1-root)
            dx = (hi-lo)*u/root
        else:
            x = lo+(hi-lo)*np.sin(pi*u/2)**2
            dx = (hi-lo)*pi/2*np.sin(pi*u)
        k = mapping*x/(1-x)
        measure = w*dx*mapping/(1-x)**2*k*k/(4*pi*pi)
        ks.append(k)
        measures.append(measure)
    return np.concatenate(ks), np.concatenate(measures), [float(v) for v in splits]


def direct_on_shell_cut(k, q, omega, t, mu, a, b):
    """Solve outgoing angular energy conservation, independently of inverse_shell/PV."""
    validate(q, omega, t, mu, a, b)
    if complex(omega).imag != 0 or not np.isfinite(k) or k <= 0:
        raise ValueError("real frequency and positive finite momentum required")
    omega = float(np.real(omega))
    incoming, r_in = F["poles_and_residues"](k, mu, a, b)
    cuts = {name: [np.zeros((5, 5), complex), 0j] for name in ("pair", "scattering")}
    shell_residuals, jacobian_checks = [], []
    for first, p in enumerate(incoming):
        target = omega+p
        for second in range(4):
            def shell(c):
                shifted = sqrt(k*k+q*q+2*k*q*c)
                return F["poles_and_residues"](shifted, mu, a, b)[0][second]
            left, right = shell(-1.), shell(1.)
            if not min(left, right) < target < max(left, right):
                continue
            c = brentq(lambda angle: shell(angle)-target, -1., 1., xtol=1e-13)
            shifted = sqrt(k*k+q*q+2*k*q*c)
            outgoing, r_out = F["poles_and_residues"](shifted, mu, a, b)
            ell = outgoing[second]
            if mu == 0:
                slope = k*q/abs(ell)
            else:
                d = sqrt((a-b)**2+8*mu*mu*(a+b)+16*mu**4+16*mu*mu*shifted*shifted)
                branch = 1 if second in (0, 3) else -1
                slope = k*q*abs(1+branch*4*mu*mu/d)/abs(ell)
            step = min(1e-5, (1-abs(c))/4)
            finite_difference = abs((shell(c+step)-shell(c-step))/(2*step))
            jacobian_checks.append(abs(finite_difference/slope-1))
            shell_residuals.append(abs(ell-target))
            operators = np.zeros((5, 2, 2), complex)
            operators[:3] = BASIS
            operators[3] = -(2*p+omega)*ROTATION+2j*mu*np.eye(2)
            operators[4] = -2j*(k*c+q/2)*ROTATION
            occupation = G["occupations"](p, t)-G["occupations"](ell, t)
            numerator = np.einsum("aij,jk,bkl,li->ab", operators, r_out[second], operators, r_in[first])
            transverse = -k*k*(1-c*c)*np.trace(ROTATION@r_out[second]@ROTATION@r_in[first])*occupation
            name = "pair" if (first < 2) != (second < 2) else "scattering"
            cuts[name][0] -= pi*.5*numerator*occupation/slope
            cuts[name][1] -= pi*transverse/slope
    return cuts, {"shell_residual": float(max(shell_residuals, default=0.)),
                  "relative_slope_FD_disagreement": float(max(jacobian_checks, default=0.)),
                  "active_shell_count": len(shell_residuals)}


def retarded_loops(q, frequency, t, mu, a, b, radial_order=48, angular_order=48,
                   auxiliary=1., scale=1., scan_order=512):
    validate(q, frequency, t, mu, a, b)
    if not np.isfinite(auxiliary+scale) or min(auxiliary, scale) <= 0:
        raise ValueError("positive finite subtraction references required")
    z = complex(frequency)
    k, measure, splits = radial_nodes(q, z.real, mu, a, b, auxiliary, radial_order, scan_order)
    actual, transverse, cuts = angular_kernel(k, q, z, t, mu, a, b, angular_order)
    reference, tr_ref, _ = angular_kernel(k, q, z, 0., 0., auxiliary**2, auxiliary**2, angular_order)
    difference = actual-reference
    transverse -= tr_ref
    covariance = G["point_covariance"](k, t, mu, a, b)-G["point_covariance"](k, 0., 0., auxiliary**2, auxiliary**2)
    contact = 2*np.trace(covariance, axis1=-2, axis2=-1)
    difference[:, 3, 3] += contact
    difference[:, 4, 4] += contact
    transverse += contact
    joint = np.asarray(np.sum(measure[:, None, None]*difference, axis=0), complex)
    tr = complex(np.sum(measure*transverse))
    bubble_ref, current_ref = vacuum_reference(q, z, auxiliary**2, scale)
    bubble, mixed, reverse, current = unpack_joint(joint, tr)
    bubble += bubble_ref
    current += current_ref
    current[1:, 1:] += G["spatial_surface_contact"](mu, a, b, auxiliary)*np.eye(3)
    spectral = {}
    if z.imag == 0:
        for name in ("pair", "scattering"):
            # The unsubtracted cut is finite; do not call reference cancellation loss.
            cj = np.asarray(np.sum(measure[:, None, None]*cuts[name][0], axis=0), complex)
            ct = complex(np.sum(measure*cuts[name][1]))
            spectral[name] = unpack_joint(cj, ct)
    return {"bubble": bubble, "mixed": mixed, "reverse": reverse, "loop_current": current,
            "cuts": spectral, "radial_splits": splits}


def reoptimized_response(q, frequency, mu, a, b, s, coupling, loops):
    validate(q, frequency, 0., mu, a, b)
    z = complex(frequency)
    _, kernel, vertices = F["source_vertices"](s, coupling)
    bubble = loops["bubble"]
    internal = np.array([[q*q+a-z*z, 2j*mu*z], [-2j*mu*z, q*q+b-z*z]])
    field = internal+.5*vertices.T@bubble@np.linalg.solve(np.eye(3)-kernel@bubble, vertices)
    forward, reverse, aa = G["classical_vertices"](q, z, mu, s)
    forward += .5*vertices.T@np.linalg.solve(np.eye(3)-bubble@kernel, loops["mixed"])
    reverse += .5*loops["reverse"]@np.linalg.solve(np.eye(3)-kernel@bubble, vertices)
    aa += loops["loop_current"]+.5*loops["reverse"]@kernel@np.linalg.solve(np.eye(3)-bubble@kernel, loops["mixed"])
    current = aa-reverse@np.linalg.solve(field, forward)
    return field, forward, reverse, aa, current


def spectral_current(current):
    """Euclidean A0=i A_density continuation, not a fitted spectral projection."""
    conversion = np.diag([1j, 1., 1., 1.])
    physical = conversion@current@conversion
    spectral = (physical-physical.conj().T)/(2j)
    return spectral, np.linalg.eigvalsh(-spectral)


def max_loop_difference(first, second):
    return float(max(np.max(np.abs(first[key]-second[key]))
                     for key in ("bubble", "mixed", "reverse", "loop_current")))


def point_cut_check(k, q, omega, t, mu, a, b):
    joint, transverse, cuts = angular_kernel(k, q, omega, t, mu, a, b, order=64)
    direct, details = direct_on_shell_cut(k, q, omega, t, mu, a, b)
    error = max(max(np.max(np.abs(cuts[name][0][0]-direct[name][0])),
                    abs(cuts[name][1][0]-direct[name][1])) for name in cuts)
    discontinuity = (joint[0]-SOURCE_METRIC@joint[0].conj().T@SOURCE_METRIC)/(2j)
    exact = cuts["pair"][0][0]+cuts["scattering"][0][0]
    details.update({"k": k, "q": q, "omega": omega,
                    "direct_delta_vs_PV_cut_disagreement": float(error),
                    "PV_source_metric_discontinuity_disagreement": float(np.max(np.abs(discontinuity-exact))),
                    "transverse_discontinuity_disagreement": float(abs(transverse[0].imag-cuts["pair"][1][0]-cuts["scattering"][1][0])),
                    "pair_norm": float(np.linalg.norm(cuts["pair"][0][0])),
                    "scattering_norm": float(np.linalg.norm(cuts["scattering"][0][0]))})
    return details


def integrated_delta_cut(q, omega, t, mu, a, b, order=48):
    """Independent tan-mapped radial integration of direct angular delta roots."""
    validate(q, omega, t, mu, a, b)
    if complex(omega).imag != 0 or isinstance(order, bool) or not isinstance(order, int) or order < 16:
        raise ValueError("real frequency and integer cut order>=16 required")
    scale = max(mu, sqrt(a), sqrt(b), abs(omega), 1.)
    endpoints = radial_endpoints(q, float(np.real(omega)), mu, a, b)
    splits = [0.]+[2/pi*np.arctan(k/scale) for k in endpoints]+[1.]
    nodes, weights = np.polynomial.legendre.leggauss(order)
    joint = {name: np.zeros((5, 5), complex) for name in ("pair", "scattering")}
    transverse = {name: 0j for name in joint}
    for lo, hi in zip(splits[:-1], splits[1:]):
        x = lo+(hi-lo)*(nodes+1)/2
        w = weights*(hi-lo)/2
        k = scale*np.tan(pi*x/2)
        measure = w*scale*pi/2/np.cos(pi*x/2)**2*k*k/(4*pi*pi)
        for value, weight in zip(k, measure):
            cuts, _ = direct_on_shell_cut(float(value), q, omega, t, mu, a, b)
            for name in joint:
                joint[name] += weight*cuts[name][0]
                transverse[name] += weight*cuts[name][1]
    return {name: unpack_joint(joint[name], transverse[name]) for name in joint}


def predecessor_hashes_match(record):
    """Do not silently accept a changed upstream calculation by renewing its hash."""
    return all(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
               for item in record["evidence_artifacts"]+record["protected_evidence_hashes"])


def audit():
    predecessor = json.loads((ROOT/CURRENT_ARTIFACT).read_text(encoding="utf-8"))
    lineage_matches = predecessor_hashes_match(predecessor)
    protected_before = {item["path"]: item["sha256"]
                        for item in predecessor["protected_evidence_hashes"]}
    examples = []
    for e in predecessor["examples"]:
        t, mu, a, b, s, coupling = (e[key] for key in ("T", "mu", "a", "b", "s", "u_canonical"))
        point_checks = [point_cut_check(.3, .08, omega, t, mu, a, b)
                        for omega in (.015, .15, .4, -.15)]
        upper = retarded_loops(.08, .15+.1j, t, mu, a, b, radial_order=80, angular_order=80)
        old_bubble = F["finite_bubble"](.08, .15+.1j, t, mu, a, b)
        old_mixed, old_reverse, old_current = G["gauge_loops"](.08, .15+.1j, t, mu, a, b)
        upper_error = max_loop_difference(upper, {"bubble": old_bubble, "mixed": old_mixed,
                                                "reverse": old_reverse, "loop_current": old_current})
        angular_checks = [direct_angular_check(k, .08, .15+.1j, t, mu, a, b) for k in (.05, .3, 1.2)]
        rows = []
        for q, omega in ((.08, .015), (.08, .15), (.08, .4), (.16, .03), (.16, .3)):
            approximations = [retarded_loops(q, omega, t, mu, a, b, radial_order=n, angular_order=m)
                              for n, m in ORDERS]
            loops = approximations[-1]
            response = reoptimized_response(q, omega, mu, a, b, s, coupling, loops)
            _, eigenvalues = spectral_current(response[-1])
            cut_sum = [sum(loops["cuts"][name][j] for name in ("pair", "scattering")) for j in range(4)]
            signed = (np.eye(3), np.eye(3), np.diag([-1., 1., 1., 1.]), np.diag([-1., 1., 1., 1.]))
            discontinuities = [
                (loops["bubble"]-loops["bubble"].conj().T)/(2j),
                (loops["mixed"]-loops["reverse"].conj().T@signed[2])/(2j),
                (loops["reverse"]-signed[2]@loops["mixed"].conj().T)/(2j),
                (loops["loop_current"]-signed[3]@loops["loop_current"].conj().T@signed[3])/(2j),
            ]
            residual = max(float(np.max(np.abs(discontinuities[j]-cut_sum[j]))) for j in range(4))
            endpoints1 = radial_endpoints(q, omega, mu, a, b, 512)
            endpoints2 = radial_endpoints(q, omega, mu, a, b, 1024)
            endpoint_error = float(np.max(np.abs(np.asarray(endpoints1)-endpoints2))) if len(endpoints1) == len(endpoints2) else 1.
            rows.append({"q": q, "omega": omega,
                         "external_field_inverse": F["complex_matrix"](response[0]),
                         "onshell_current": F["complex_matrix"](response[-1]),
                         "cut_bubbles": {name: F["complex_matrix"](loops["cuts"][name][0]) for name in loops["cuts"]},
                         "cut_norms": {name: float(np.linalg.norm(loops["cuts"][name][0])) for name in loops["cuts"]},
                         "quadrature_refinements": [max_loop_difference(approximations[j], approximations[j-1]) for j in (1, 2)],
                         "Ward_residuals": G["ward_residuals"](q, omega, s, response),
                         "covariance_Ward_residual": G["covariance_ward"](q, omega, t, mu, a, b, loops["bubble"], loops["mixed"]),
                         "loop_discontinuity_vs_exact_cut": residual,
                         "minus_physical_current_spectral_eigenvalues": eigenvalues.tolist(),
                         "radial_endpoints": endpoints1, "endpoint_scan_refinement": endpoint_error,
                         "radial_compact_splits": loops["radial_splits"]})
        base = retarded_loops(.08, .15, t, mu, a, b, radial_order=80, angular_order=80)
        alternate = retarded_loops(.08, .15, t, mu, a, b, radial_order=80, angular_order=80, auxiliary=1.3)
        negative = retarded_loops(.08, -.15, t, mu, a, b, radial_order=80, angular_order=80)
        neg_response = reoptimized_response(.08, -.15, mu, a, b, s, coupling, negative)
        pos_response = reoptimized_response(.08, .15, mu, a, b, s, coupling, base)
        # In this Euclidean-source convention the time continuation and q parity cancel.
        reality = float(np.max(np.abs(neg_response[-1]-pos_response[-1].conj())))
        integrated = integrated_delta_cut(.08, .15, t, mu, a, b)
        delta_error = float(max(np.max(np.abs(integrated[name][j]-base["cuts"][name][j]))
                                for name in integrated for j in range(4)))
        widths = []
        exact_angular = angular_kernel(.3, .08, .15, t, mu, a, b, 80)[0][0]
        for eta in (.02, .01, .005, .0025):
            finite = angular_kernel(.3, .08, .15+1j*eta, t, mu, a, b, 80)[0][0]
            widths.append({"eta_verification_only": eta, "angular_distance_to_exact_limit": float(np.linalg.norm(finite-exact_angular))})
        cold = retarded_loops(.08, .015, 0., mu, a, b, radial_order=48, angular_order=48)
        factor = 1.7
        scaled = retarded_loops(.08*factor, .15*factor, t*factor, mu*factor, a*factor**2, b*factor**2,
                                radial_order=80, angular_order=80, auxiliary=factor, scale=factor)
        scale_error = float(max(np.max(np.abs(scaled[key]-base[key]*factor**power))
                                for key, power in (("bubble", 0), ("mixed", 1), ("reverse", 1), ("loop_current", 2))))
        examples.append({"T": t, "mu": mu, "Phi_fixed": e["Phi_fixed"], "s": s, "a": a, "b": b,
                         "u_canonical": coupling,
                         "point_cut_checks": point_checks, "independent_angular_checks": angular_checks,
                         "upper_half_plane_predecessor_disagreement": upper_error, "responses": rows,
                         "independent_integrated_delta_cut_disagreement": delta_error,
                         "auxiliary_reference_disagreement": max_loop_difference(base, alternate),
                         "retarded_current_reality_residual": reality, "unit_scaling_disagreement": scale_error,
                         "zero_temperature_scattering_norm": float(np.linalg.norm(cold["cuts"]["scattering"][0])),
                         "upper_half_plane_to_exact_angular_limit": widths})
    vacuum = []
    for omega in (.4, 2.):
        actual = retarded_loops(.08, omega, 0., 0., .7, .7, radial_order=96, angular_order=96)
        expected_bubble, expected_current = vacuum_reference(.08, omega, .7)
        s_invariant = omega*omega-.08**2
        beta = sqrt(1-4*.7/s_invariant) if s_invariant > 4*.7 else 0.
        vacuum.append({"omega": omega, "pair_beta": beta,
                       "bubble_Feynman_disagreement": float(np.max(np.abs(actual["bubble"]-expected_bubble))),
                       "current_Feynman_disagreement": float(np.max(np.abs(actual["loop_current"]-expected_current))),
                       "pair_cut_normalization_disagreement": float(np.max(np.abs(actual["cuts"]["pair"][0]+np.eye(3)*beta/(16*pi))))})
    rows = [row for e in examples for row in e["responses"]]
    points = [row for e in examples for row in e["point_cut_checks"]]
    checks = {
        "accepted_same_prescription_current_predecessor": predecessor["closure_level"] == "CLOSED_FOR_LANE" and all(predecessor["checks"].values()) and predecessor["full_core_unlock"] is False,
        "predecessor_declared_hash_lineage_matches": lineage_matches,
        "independent_delta_roots_match_PV_discontinuity": all(max(p["direct_delta_vs_PV_cut_disagreement"], p["PV_source_metric_discontinuity_disagreement"], p["transverse_discontinuity_disagreement"], p["shell_residual"]) < POINT_TOLERANCE for p in points),
        "on_shell_Jacobian_matches_forward_dispersion_difference": all(p["relative_slope_FD_disagreement"] < 1e-6 for p in points),
        "independent_upper_half_plane_angular_kernel": all(max(c.values()) < POINT_TOLERANCE for e in examples for c in e["independent_angular_checks"]),
        "new_PV_matches_committed_upper_half_plane_method": all(e["upper_half_plane_predecessor_disagreement"] < QUADRATURE_TOLERANCE for e in examples),
        "independent_integrated_phase_space_cuts": all(e["independent_integrated_delta_cut_disagreement"] < QUADRATURE_TOLERANCE for e in examples),
        "real_axis_vacuum_below_and_above_pair_threshold": all(max(v["bubble_Feynman_disagreement"], v["current_Feynman_disagreement"], v["pair_cut_normalization_disagreement"]) < POINT_TOLERANCE for v in vacuum),
        "real_axis_quadrature_refinement": all(r["quadrature_refinements"][-1] < QUADRATURE_TOLERANCE for r in rows),
        "kinematic_endpoint_scan_refinement_on_declared_grid": all(r["endpoint_scan_refinement"] < POINT_TOLERANCE for r in rows),
        "integrated_loop_spectral_discontinuity": all(r["loop_discontinuity_vs_exact_cut"] < QUADRATURE_TOLERANCE for r in rows),
        "reoptimized_real_axis_source_and_current_Ward": all(max(r["Ward_residuals"].values()) < WARD_TOLERANCE and r["covariance_Ward_residual"] < WARD_TOLERANCE for r in rows),
        "physical_current_loss_positive_on_declared_positive_frequency_grid": all(min(r["minus_physical_current_spectral_eigenvalues"]) >= -POINT_TOLERANCE for r in rows),
        "cold_scattering_cut_absent": all(e["zero_temperature_scattering_norm"] == 0 for e in examples),
        "auxiliary_reference_independence": all(e["auxiliary_reference_disagreement"] < QUADRATURE_TOLERANCE for e in examples),
        "negative_frequency_current_reality": all(e["retarded_current_reality_residual"] < QUADRATURE_TOLERANCE for e in examples),
        "natural_energy_scaling_not_SI_mapping": all(e["unit_scaling_disagreement"] < QUADRATURE_TOLERANCE for e in examples),
        "verification_eta_approaches_exact_PV_not_output_width": all(all(y["angular_distance_to_exact_limit"] < x["angular_distance_to_exact_limit"] for x, y in zip(e["upper_half_plane_to_exact_angular_limit"], e["upper_half_plane_to_exact_angular_limit"][1:])) for e in examples),
        "protected_predecessor_and_core_hashes_unchanged": all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h for p, h in protected_before.items()),
    }
    passed = all(checks.values())
    evidence = (CURRENT_ARTIFACT, CURRENT_CODE, G["FIELD_ARTIFACT"], G["FIELD_CODE"],
                F["BACKGROUND_ARTIFACT"], F["BACKGROUND_CODE"], F["MATCH_ARTIFACT"], F["MATCH_CODE"],
                Path(__file__).relative_to(ROOT).as_posix())
    record = {
        "schema_version": "t13-fixed-phi-hartree-real-axis-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "major_result_id": "T13_FIXED_PHI_HARTREE_REAL_AXIS_RESPONSE",
        "topic": "0.13", "branch_id": predecessor["branch_id"],
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "verification_status": "PASS_SCOPED_HARTREE_REAL_AXIS_RESPONSE" if passed else "FAIL_HARTREE_REAL_AXIS_RESPONSE",
        "what_is_closed": ["exact_retarded_angular_PV_and_pair_scattering_cuts", "independent_direct_on_shell_phase_space_verification", "full_domain_subtracted_real_axis_loop_and_reoptimized_current_on_declared_grid", "real_axis_contact_Ward_vacuum_reality_and_unit_checks"],
        "equation_or_mapping": "int_L^U g(ell)/(omega+p-ell+i0) dell = int (g-g_star)/(omega+p-ell) dell + g_star log| (omega+p-L)/(omega+p-U) | - i*pi*g_star; Pi=Gamma_AA-Gamma_Aphi*Gamma_phiphi^-1*Gamma_phiA",
        "units": {"q_omega_T_mu_A": "E", "s_a_b": "E^2", "J_covariance_bubble": "dimensionless", "Y_mixed": "E", "Gamma_current_spectral_density": "E^2", "g_mass_mass": "E^-3", "g_mass_source": "E^-2", "g_source_source": "E^-1", "radial_measure": "E^3", "dell_divided_by_denominator": "dimensionless"},
        "derivation_class": "EXACT_ANGULAR_CAUCHY_REDUCTION_OF_DECLARED_HARTREE_SOURCE_LOOPS_WITH_NUMERICAL_FULL_DOMAIN_RADIAL_QUADRATURE",
        "observable": "conditional_O2_current_and_external_field_response_not_material_temperature_or_heat_flux",
        "data_role": "DERIVED_FIXED_NATURAL_UNIT_WITNESSES_NO_EMPIRICAL_ROWS",
        "state_variables": ["existing_O2_Cartesian_fields_at_fixed_Phi"],
        "excluded_variables": ["R_gen", "R_obs", "nondynamical_A_source"],
        "equation_registry_ids": ["t13.diagnostic.hartree_real_axis_Cauchy", "t13.diagnostic.hartree_on_shell_source_cut"],
        "examples": examples, "vacuum_reference_checks": vacuum, "checks": checks,
        "thresholds": {"point_and_vacuum_absolute": POINT_TOLERANCE, "radial_quadrature_absolute": QUADRATURE_TOLERANCE, "Ward_absolute": WARD_TOLERANCE, "on_shell_slope_relative": 1e-6},
        "config": {"orders": ORDERS, "vacuum_order": 96, "endpoint_scans": [512, 1024], "output_imaginary_width": 0., "radial_domain": "0<=k<infinity", "UV_mapping": "x=lo+(1-lo)*(1-sqrt(1-u^2))", "eta_is_only_a_verification_sequence": True},
        "numerical_arithmetic": {"longdouble_mantissa_bits": int(np.finfo(np.longdouble).nmant), "cancellation_safe_log1p_and_on_shell_residue_identity": True, "numerical_errors_are_not_physical_uncertainties": True, "certified_numerical_error_bound": False},
        "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in evidence],
        "protected_evidence_hashes": [{"path": p, "sha256": h} for p, h in protected_before.items()],
        "source_contact_convention": predecessor["source_contact_convention"],
        "method_references": [{"url": "https://arxiv.org/pdf/hep-ph/0203008", "locator": "external action/source Ward construction", "role": "established_method_not_UET_novelty"}, {"url": "https://arxiv.org/pdf/hep-ph/9802370", "locator": "IV pair/scattering spectral delta functions and branch-cut dynamics", "role": "method_context_different_scalar_QED_model_not_UET_validation"}],
        "open_blockers": ["global_collective_poles_and_IR_truncation_control", "full_covariant_nonuniform_regulator_RG_and_action_input", "joint_Phi_global_state_and_material_source_detector_map", "normal_component_heat_current_SK_KMS_and_collision_transport", "independent_measurement_and_source_uncertainty"],
        "controlling_blocker": "global_spectral_truncation_regulator_joint_Phi_material_and_transport_matching_not_closed",
        "dependency_unlocked": ["same_candidate_global_spectral_and_joint_state_matching_only"],
        "real_axis_limit_admitted": passed, "real_axis_admission_scope": "two_fixed_Phi_witnesses_and_ten_positive_frequency_q_points_not_global",
        "global_real_axis_stability_proved": False, "controlled_truncation_error_established": False,
        "gauge_current_vertex_computed": True, "physical_current_contact_normalization_admitted": False,
        "full_covariant_counterterm_match": False, "RG_invariance_established": False,
        "joint_Phi_stationarity_derived": False, "physical_Kubo_emitted": False,
        "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False,
        "core_composition_gate_overwritten": False, "claim_promotion": False,
        "parameter_fitting": False, "imposed_Ward_projection": False, "clipping": False, "IR_filter": False,
        "artificial_width": False, "internal_gap_used_as_physical_Goldstone_mass": False,
        "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
        "causal_leakage_threshold_changed": False, "xie_2026_accessed": False,
        "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
        "claim_boundary": "Fixed-Phi Hartree rest-frame real-axis loop/current response on a declared grid under the inherited source-contact convention. Not a global pole/stability or truncation proof, collision width, physical Kubo/heat/entropy/SK-KMS, material He-II/graphite prediction, finite-cone repair or global UET closure. Internal Hartree gaps do not erase the preceding massless/composite infrared boundary.",
    }
    record["report"] = {
        "MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"], "WHAT_REMAINS_OPEN": record["open_blockers"],
        "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
        "WHAT_CHANGED": "Computed exact angular real-axis PV and spectral cuts with independent delta roots, full-domain radial subtraction and same-current reoptimization.",
        "EQUATION_OR_MAPPING": record["equation_or_mapping"],
        "VERIFICATION": "Independent angular/delta/vacuum methods; Ward, refinement, signed-frequency and scale checks without assigned output width.",
        "CONTROLLING_BLOCKER": record["controlling_blocker"],
        "NEXT_ACTION": "Analyze global collective spectral/IR and approximation/regulator/action limits, then joint Phi/material/source/detector and heat-current matching. Do not repeat the same declared-grid calculation.",
        "CLAIM_BOUNDARY": record["claim_boundary"],
    }
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "max_Ward": max(max(r["Ward_residuals"].values()) for e in result["examples"] for r in e["responses"])}, indent=2))
