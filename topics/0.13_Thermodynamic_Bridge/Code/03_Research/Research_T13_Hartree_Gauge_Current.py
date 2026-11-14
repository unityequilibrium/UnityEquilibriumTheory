"""Source/contact-complete current Hessian of the fixed-Phi Hartree candidate.

A is a nondynamical source for the existing O(2) current, not a UET state.
All responses below are static or upper-half-plane. The vacuum F_A^2
contact is fixed by an explicit MS reference, not a measured Kubo input.
"""

from __future__ import annotations

import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.special import zeta

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
FIELD_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_External_Response.py"
FIELD_ARTIFACT = PREFIX+"Result/artifacts/t13_hartree_external_response.json"
F = runpy.run_path(str(ROOT/FIELD_CODE))
H = F["H"]
BASIS = F["BASIS"]
ROTATION = np.array([[0., -1.], [1., 0.]])
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_gauge_current.json")
ORDERS = ((48, 24), (72, 36), (96, 48))
POINT_TOLERANCE = 1e-7
QUADRATURE_TOLERANCE = 2e-5
WARD_TOLERANCE = 2e-5


def occupations(poles, t):
    energy = np.abs(poles)
    thermal = np.zeros_like(energy) if t == 0 else np.exp(-energy/t)/(-np.expm1(-energy/t))
    return np.sign(poles)*(thermal+.5)


def extended_poles(k, mu, a, b):
    """Same internal spectrum; extended arithmetic controls UV cancellation."""
    F["validate"](0., mu, a, b)
    k = np.asarray(k, dtype=np.longdouble)
    if np.any(~np.isfinite(k)) or np.any(k < 0):
        raise ValueError("nonnegative finite momentum required")
    if mu == 0:
        energies = np.stack((np.sqrt(k*k+a), np.sqrt(k*k+b)), axis=-1)
        p = np.stack((-energies[..., 0], -energies[..., 1],
                      energies[..., 0], energies[..., 1]), axis=-1)
        r = np.zeros(p.shape+(2, 2), dtype=np.clongdouble)
        for j, field in enumerate((0, 1, 0, 1)):
            r[..., j, field, field] = -1/(2*p[..., j])
        return p, r
    mu, a, b = map(np.longdouble, (mu, a, b))
    d = np.sqrt((a-b)**2+8*mu*mu*(a+b)+16*mu**4+16*mu*mu*k*k)
    high_sq = k*k+(a+b)/2+2*mu*mu+d/2
    low_sq = (k*k+a)*(k*k+b)/high_sq
    low, high = np.sqrt(low_sq), np.sqrt(high_sq)
    p = np.stack((-high, -low, low, high), axis=-1)
    r = np.zeros(p.shape+(2, 2), dtype=np.clongdouble)
    r[..., 0, 0] = k[..., None]**2+b-p*p
    r[..., 1, 1] = k[..., None]**2+a-p*p
    r[..., 0, 1] = -2j*mu*p
    r[..., 1, 0] = 2j*mu*p
    derivative = 4*p*(p*p-k[..., None]**2-(a+b)/2-2*mu*mu)
    return p, r/derivative[..., None, None]


def frequency_moments(p, ell, t, frequency):
    p, ell = np.broadcast_arrays(p, ell)
    z = np.clongdouble(frequency)
    np_, nl = occupations(p, t), occupations(ell, t)
    if z != 0:
        s0 = -(np_-nl)/(z+p-ell)
    else:
        same = np.sign(p) == np.sign(ell)
        s0 = np.divide(-(np_-nl), p-ell,
                       out=np.zeros(p.shape, dtype=np.longdouble), where=~same).astype(np.clongdouble)
        if t > 0:
            ep, el = np.abs(p), np.abs(ell)
            gap = np.abs(ep-el)
            divided = np.divide(-np.expm1(-gap/t), gap,
                                out=np.full_like(gap, 1/t), where=gap != 0)
            derivative = np.exp(-np.minimum(ep, el)/t)*divided/(
                (-np.expm1(-ep/t))*(-np.expm1(-el/t)))
            s0 = np.where(same, derivative, s0)
    # The polynomial sum of 1 in S2 cancels only after the residue sums.
    s1 = p*s0-nl
    s2 = p*p*s0-(p+ell-z)*nl
    return s0, s1, s2


def point_gauge(k1, k2, midpoint_longitudinal, t, mu, a, b, frequency=0j):
    F["validate"](t, mu, a, b, frequency=frequency)
    k1, k2, kz = np.broadcast_arrays(np.asarray(k1, np.longdouble),
                                    np.asarray(k2, np.longdouble),
                                    np.asarray(midpoint_longitudinal, np.longdouble))
    if np.any(~np.isfinite(kz)):
        raise ValueError("finite longitudinal midpoint required")
    p, rp = extended_poles(k1, mu, a, b)
    ell, re = extended_poles(k2, mu, a, b)
    moments = frequency_moments(p[..., :, None], ell[..., None, :], t, frequency)
    vertices = np.zeros(k1.shape+(2, 2, 2, 2), dtype=np.clongdouble)
    # axes: spacetime component (0,longitudinal), x polynomial (0,1), matrix
    vertices[..., 0, 0, :, :] = -np.clongdouble(frequency)*ROTATION+2j*mu*np.eye(2)
    vertices[..., 0, 1, :, :] = -2*ROTATION
    vertices[..., 1, 0, :, :] = -2j*kz[..., None, None]*ROTATION
    mixed = np.zeros(k1.shape+(3, 2), dtype=np.clongdouble)
    reverse = np.zeros(k1.shape+(2, 3), dtype=np.clongdouble)
    current = np.zeros(k1.shape+(2, 2), dtype=np.clongdouble)
    for alpha in range(2):
        for power in range(2):
            v = vertices[..., alpha, power, :, :]
            direct = np.einsum("cij,...tjk,...kl,...sli->...cst", BASIS, re, v, rp)
            backward = np.einsum("...ij,...tjk,ckl,...sli->...cst", v, re, BASIS, rp)
            mixed[..., :, alpha] -= np.sum(direct*moments[power][..., None, :, :], axis=(-2, -1))
            reverse[..., alpha, :] -= np.sum(backward*moments[power][..., None, :, :], axis=(-2, -1))
            for beta in range(2):
                for second_power in range(2):
                    other = vertices[..., beta, second_power, :, :]
                    product = np.einsum("...ij,...tjk,...kl,...sli->...st", v, re, other, rp)
                    current[..., alpha, beta] -= .5*np.sum(product*moments[power+second_power], axis=(-2, -1))
    return mixed, reverse, current


def point_covariance(k, t, mu, a, b):
    p, r = extended_poles(k, mu, a, b)
    return -np.sum(r*occupations(p, t)[..., :, None, None], axis=-3)


def point_transverse(k1, k2, transverse_sq, t, mu, a, b, frequency=0j):
    F["validate"](t, mu, a, b, frequency=frequency)
    if np.any(~np.isfinite(transverse_sq)) or np.any(np.asarray(transverse_sq) < 0):
        raise ValueError("finite nonnegative transverse momentum squared required")
    p, rp = extended_poles(k1, mu, a, b)
    ell, re = extended_poles(k2, mu, a, b)
    s0 = frequency_moments(p[..., :, None], ell[..., None, :], t, frequency)[0]
    product = np.einsum("ij,...tjk,kl,...sli->...st", ROTATION, re, ROTATION, rp)
    return transverse_sq*np.sum(product*s0, axis=(-2, -1))


def spatial_surface_contact(mu, a, b, auxiliary):
    """UV IBP boundary of frequency-first 3D subtraction, not a Ward fit.

    k^3 Tr[int(dnu/2pi)G]=k^2-Tr(M)/4+O(k^-2).
    A covariant regulator sets the full 4D total derivative to zero.
    Removing its residual spatial boundary restores that convention.
    """
    return (a+b+2*mu*mu-2*auxiliary*auxiliary)/(24*pi*pi)


def reference_coefficient(q, frequency, mass_sq=1., scale=1., order=128):
    F["validate"](0., 0., mass_sq, mass_sq, q, frequency)
    if min(mass_sq, scale) <= 0 or not np.isfinite(scale):
        raise ValueError("positive finite reference mass squared and scale required")
    x, w = np.polynomial.legendre.leggauss(order)
    x, w = (x+1)/2, w/2
    z = complex(frequency)
    invariant = q*q-z*z
    return -np.sum(w*(1-2*x)**2*np.log((mass_sq+x*(1-x)*invariant)/scale**2))/(16*pi*pi)


def reference_current(q, frequency, mass_sq=1., scale=1., order=128):
    """Independent 4D equal-mass vacuum MS current including seagull."""
    z = complex(frequency)
    qe = np.array([-1j*z, q, 0., 0.])
    invariant = q*q-z*z
    return reference_coefficient(q, z, mass_sq, scale, order)*(invariant*np.eye(4)-np.outer(qe, qe))


def gauge_loops(q, frequency, t, mu, a, b, radial_order=96, angular_order=48,
                auxiliary=1., scale=1., routing="symmetric", remove_surface=True):
    F["validate"](t, mu, a, b, q, frequency)
    if routing not in ("symmetric", "one_sided"):
        raise ValueError("declared momentum routing required")
    if min(auxiliary, scale) <= 0 or not np.isfinite(auxiliary+scale):
        raise ValueError("positive finite source subtraction references required")
    if any(isinstance(n, bool) or not isinstance(n, int) or n < 16 for n in (radial_order, angular_order)):
        raise ValueError("integer quadrature orders >=16 required")
    x, w = np.polynomial.legendre.leggauss(radial_order)
    x, w = np.asarray((x+1)/2, np.longdouble), np.asarray(w/2, np.longdouble)
    mapping = np.longdouble(max(mu, sqrt(a), sqrt(b), t, auxiliary))
    k = mapping*x/(1-x)
    c, cw = np.polynomial.legendre.leggauss(angular_order)
    c, cw = np.asarray(c, np.longdouble), np.asarray(cw, np.longdouble)
    kk = k[:, None]
    if routing == "symmetric":
        k1 = np.sqrt(kk*kk+q*q/4-kk*q*c[None, :])
        k2 = np.sqrt(kk*kk+q*q/4+kk*q*c[None, :])
        kz = kk*c[None, :]
    else:
        k1 = np.broadcast_to(kk, (len(k), len(c)))
        k2 = np.sqrt(kk*kk+q*q+2*kk*q*c[None, :])
        kz = kk*c[None, :]+q/2
    mixed, reverse, current = point_gauge(k1, k2, kz, t, mu, a, b, frequency)
    _, _, reference = point_gauge(k1, k2, kz, 0., 0., auxiliary**2, auxiliary**2, frequency)
    transverse_sq = kk*kk*(1-c[None, :]**2)
    transverse = point_transverse(k1, k2, transverse_sq, t, mu, a, b, frequency)
    transverse -= point_transverse(k1, k2, transverse_sq, 0., 0., auxiliary**2, auxiliary**2, frequency)
    covariance = point_covariance(k, t, mu, a, b)
    reference_covariance = point_covariance(k, 0., 0., auxiliary**2, auxiliary**2)
    contact = np.trace(covariance-reference_covariance, axis1=-2, axis2=-1)
    current -= reference
    current += contact[:, None, None, None]*np.eye(2)
    transverse += contact[:, None]
    measure = mapping*w[:, None]/(1-x[:, None])**2*kk*kk*cw[None, :]/(4*pi*pi)
    integrate = lambda value: np.asarray(np.sum(measure[..., None, None]*value, axis=(0, 1)), complex)
    reference_tensor = reference_current(q, frequency, auxiliary**2, scale)
    loop = integrate(current)+reference_tensor[:2, :2]
    transverse_loop = complex(np.sum(measure*transverse))+reference_tensor[2, 2]
    if remove_surface:
        surface = spatial_surface_contact(mu, a, b, auxiliary)
        loop[1, 1] += surface
        transverse_loop += surface
    full = np.zeros((4, 4), complex)
    full[:2, :2] = loop
    full[2, 2] = full[3, 3] = transverse_loop
    full_mixed = np.zeros((3, 4), complex)
    full_reverse = np.zeros((4, 3), complex)
    full_mixed[:, :2], full_reverse[:2, :] = integrate(mixed), integrate(reverse)
    return full_mixed, full_reverse, full


def classical_vertices(q, frequency, mu, s):
    z = complex(frequency)
    v = np.array([sqrt(s), 0.])
    rv = ROTATION@v
    forward = np.column_stack((-z*rv+2j*mu*v, -1j*q*rv, np.zeros(2), np.zeros(2)))
    reverse = np.vstack((z*rv+2j*mu*v, 1j*q*rv, np.zeros(2), np.zeros(2)))
    return forward, reverse, s*np.eye(4, dtype=complex)


def source_hessians(q, frequency, mu, a, b, s, coupling, bubble, loops):
    if q == 0 and frequency == 0:
        raise ValueError("uniform Goldstone direction is singular; use radial-only charge derivative")
    mixed, backward, aa_loop = loops
    _, kernel, vertices = F["source_vertices"](s, coupling)
    forward, reverse, aa_tree = classical_vertices(q, frequency, mu, s)
    forward += .5*vertices.T@np.linalg.solve(np.eye(3)-bubble@kernel, mixed)
    reverse += .5*backward@np.linalg.solve(np.eye(3)-kernel@bubble, vertices)
    aa = aa_tree+aa_loop+.5*backward@kernel@np.linalg.solve(np.eye(3)-bubble@kernel, mixed)
    field = F["external_inverse"](q, frequency, mu, a, b, s, coupling, bubble)
    return field, forward, reverse, aa, aa-reverse@np.linalg.solve(field, forward)


def uniform_charge_check(t, mu, r, coupling, s, a, b, step=1e-4):
    """Independent stationary-potential second derivative at fixed action mass."""
    if not np.isfinite(step) or step <= 0 or step >= mu:
        raise ValueError("positive finite derivative step smaller than mu required")
    loops = gauge_loops(0., 0j, t, mu, a, b)
    bubble = F["static_finite_bubble"](t, mu, a, b)
    _, kernel, vertices = F["source_vertices"](s, coupling)
    forward, reverse, aa = classical_vertices(0., 0j, mu, s)
    forward += .5*vertices.T@np.linalg.solve(np.eye(3)-bubble@kernel, loops[0])
    reverse += .5*loops[1]@np.linalg.solve(np.eye(3)-kernel@bubble, vertices)
    aa += loops[2]+.5*loops[1]@kernel@np.linalg.solve(np.eye(3)-bubble@kernel, loops[0])
    field = F["external_inverse"](0., 0j, mu, a, b, s, coupling, bubble)
    susceptibility = aa[0, 0]-reverse[0, 0]*forward[0, 0]/field[0, 0]
    mass_sq = mu*mu-r
    potentials = []
    for shift in (-step, 0., step):
        mup = mu+shift
        rp = mup*mup-mass_sq
        solution = H["stationary_background"](t, mup, rp, coupling)
        if np.max(np.abs(solution["residual"])) > H["ROOT_TOLERANCE"]:
            raise ValueError("independent envelope root not stationary")
        potentials.append(solution["potential"])
    envelope = -(potentials[2]-2*potentials[1]+potentials[0])/(step*step)
    return {"step": step, "source_susceptibility": float(susceptibility.real),
            "envelope_susceptibility": float(envelope),
            "relative_disagreement": float(abs(susceptibility/envelope-1)),
            "uniform_spatial_stiffness": float(aa[1, 1].real),
            "phase_density_mixing_residual": float(max(abs(forward[1, 0]), abs(reverse[0, 1]))),
            "protocol": "fixed physical action mass, not fixed shifted r or internal a,b"}


def covariance_ward(q, frequency, t, mu, a, b, bubble, mixed):
    loops = H["loop_integrals"](t, mu, a, b)
    rotated_covariance = np.array([0., 0., sqrt(2)*(loops["phase"]-loops["sigma"])])
    commutator = np.array([0., 0., sqrt(2)*(b-a)])
    iq = np.array([complex(frequency), 1j*q, 0., 0.])
    return float(np.max(np.abs(mixed@iq-(rotated_covariance-bubble@commutator))))


def counterterm_check(q, frequency, mu, a, b, s, coupling, bubble, loops, D):
    w, _, _ = F["source_vertices"](s, coupling)
    _, bare_kernel = F["CT"]["symmetric_tensor_projection"](coupling, D)
    bare_bubble = bubble+D*np.eye(3)
    vertex = np.linalg.inv(np.linalg.inv(bare_kernel)-bare_bubble)
    forward, reverse, aa = classical_vertices(q, frequency, mu, s)
    forward += .5*w.T@vertex@loops[0]
    reverse += .5*loops[1]@vertex@w
    aa += loops[2]+.5*loops[1]@vertex@loops[0]
    actual = source_hessians(q, frequency, mu, a, b, s, coupling, bubble, loops)
    return float(max(np.max(np.abs(forward-actual[1])), np.max(np.abs(reverse-actual[2])),
                     np.max(np.abs(aa-actual[3]))))


def direct_frequency_check(k1, k2, kz, t, mu, a, b, harmonic=1, terms=1024):
    F["validate"](t, mu, a, b)
    if t <= 0 or harmonic not in (0, 1) or terms < 32:
        raise ValueError("positive T, harmonic 0/1 and terms>=32 required")
    omega = 2*pi*t*harmonic
    mixed, reverse, current = np.zeros((3, 2), complex), np.zeros((2, 3), complex), np.zeros((2, 2), complex)
    for n in range(-terms, terms+1):
        nu = 2*pi*t*n
        g = np.linalg.inv(F["euclidean_kernel"](nu, k1, mu, a, b))
        shifted = np.linalg.inv(F["euclidean_kernel"](nu+omega, k2, mu, a, b))
        v = [-1j*(2*nu+omega)*ROTATION+2j*mu*np.eye(2), -2j*kz*ROTATION]
        for alpha in range(2):
            mixed[:, alpha] -= t*np.einsum("cij,jk,kl,li->c", BASIS, shifted, v[alpha], g)
            reverse[alpha, :] -= t*np.einsum("ij,jk,ckl,li->c", v[alpha], shifted, BASIS, g)
            for beta in range(2):
                current[alpha, beta] -= .5*t*np.trace(v[alpha]@shifted@v[beta]@g)
    current[0, 0] -= 8*t*zeta(2., terms+1)/(2*pi*t)**2
    exact = point_gauge(k1, k2, kz, t, mu, a, b, 1j*omega)
    return {"harmonic": harmonic, "terms": terms,
            "mixed_disagreement": float(np.max(np.abs(mixed-exact[0]))),
            "reverse_disagreement": float(np.max(np.abs(reverse-exact[1]))),
            "current_disagreement": float(np.max(np.abs(current-exact[2])))}


def unpack(matrix):
    return np.asarray(matrix["real"])+1j*np.asarray(matrix["imaginary"])


def ward_residuals(q, frequency, s, hessians):
    field, forward, reverse, aa, current = hessians
    iq = np.array([complex(frequency), 1j*q, 0., 0.])
    rv = np.array([0., sqrt(s)])
    return {"field_source": float(np.max(np.abs(forward@iq-field@rv))),
            "source_source": float(np.max(np.abs(aa@iq-reverse@rv))),
            "onshell_current": float(np.max(np.abs(current@iq))),
            "left_current": float(np.max(np.abs(iq@current)))}


def audit():
    old = json.loads((ROOT/F["BACKGROUND_ARTIFACT"]).read_text(encoding="utf-8"))
    field_record = json.loads((ROOT/FIELD_ARTIFACT).read_text(encoding="utf-8"))
    examples = []
    for e, prior in zip(old["examples"], field_record["examples"]):
        t, mu, coupling = e["T"], e["mu"], e["u_canonical"]
        s, a, b = (e["background"][key] for key in ("s", "a", "b"))
        rows = []
        for previous in prior["responses"]:
            q, z = previous["q"], complex(*previous["frequency"])
            bubble = unpack(previous["bubble"])
            runs = [gauge_loops(q, z, t, mu, a, b, n, m) for n, m in ORDERS]
            loops = runs[-1]
            hessians = source_hessians(q, z, mu, a, b, s, coupling, bubble, loops)
            one_sided = gauge_loops(q, z, t, mu, a, b, routing="one_sided")
            omitted_surface = tuple(np.copy(value) for value in loops)
            omitted_surface[2][1:, 1:] -= spatial_surface_contact(mu, a, b, 1.)*np.eye(3)
            omitted_contact = tuple(np.copy(value) for value in hessians)
            omitted_contact[3][...] -= s*np.eye(4)
            opposite = gauge_loops(q, -z.conjugate(), t, mu, a, b)
            rows.append({"q": q, "frequency": [z.real, z.imag],
                         "mixed_covariance_source": F["complex_matrix"](loops[0]),
                         "reverse_mixed_source": F["complex_matrix"](loops[1]),
                         "loop_source_Hessian": F["complex_matrix"](loops[2]),
                         "field_source_Hessian": F["complex_matrix"](hessians[1]),
                         "source_source_Hessian": F["complex_matrix"](hessians[3]),
                         "onshell_current": F["complex_matrix"](hessians[4]),
                         "covariance_Ward_residual": covariance_ward(q, z, t, mu, a, b, bubble, loops[0]),
                         "Ward_residuals": ward_residuals(q, z, s, hessians),
                         "last_quadrature_disagreement": float(max(np.max(np.abs(runs[-1][i]-runs[-2][i])) for i in range(3))),
                         "routing_disagreement": float(max(np.max(np.abs(one_sided[i]-loops[i])) for i in range(3))),
                         "counterterm_residual": max(counterterm_check(q, z, mu, a, b, s, coupling, bubble, loops, D) for D in (-.03, .04)),
                         "current_reality_residual": float(np.max(np.abs(opposite[2]-loops[2].conjugate()))),
                         "omit_spatial_UV_surface_Ward": ward_residuals(q, z, s, source_hessians(q, z, mu, a, b, s, coupling, bubble, omitted_surface))["source_source"],
                         "omit_classical_seagull_Ward": ward_residuals(q, z, s, omitted_contact)["source_source"]})
        reference_runs = [gauge_loops(.08, .15+.1j, t, mu, a, b, auxiliary=aux) for aux in (.8, 1., 1.3)]
        charge = [uniform_charge_check(t, mu, e["r"], coupling, s, a, b, h) for h in (1e-4, 5e-5)]
        surface_boundary = []
        for k in (40., 80., 160.):
            actual = point_covariance(k, 0., mu, a, b)
            ref = point_covariance(k, 0., 0., 1., 1.)
            limit = float((k**3*np.trace(actual-ref)).real)
            expected = -(a+b+2*mu*mu-2)/4
            surface_boundary.append({"k": k, "boundary": limit, "analytic_limit": expected,
                                     "absolute_error": abs(limit-expected)})
        examples.append({"T": t, "mu": mu, "Phi_fixed": e["Phi_fixed"], "s": s, "a": a, "b": b,
                         "u_canonical": coupling, "responses": rows, "charge_envelope": charge,
                         "matrix_frequency_checks": [direct_frequency_check(.4, .55, .2, t, mu, a, b, h) for h in (0, 1)],
                         "auxiliary_reference_disagreement": float(max(np.max(np.abs(run[i]-reference_runs[1][i])) for run in reference_runs for i in range(3))),
                         "UV_surface_boundary": surface_boundary})
    vacuum = []
    for q, z in ((.16, 0j), (.08, .15+.1j), (0., .3j)):
        for auxiliary in (.8, 1., 1.3):
            direct = gauge_loops(q, z, 0., 0., .7, .7, auxiliary=auxiliary)[2]
            reference = reference_current(q, z, .7)
            vacuum.append({"q": q, "frequency": [z.real, z.imag], "auxiliary": auxiliary,
                           "four_dimensional_current_disagreement": float(np.max(np.abs(direct-reference)))})
    rows = [row for e in examples for row in e["responses"]]
    checks = {
        "accepted_same_prescription_predecessors": all(v["closure_level"] == "CLOSED_FOR_LANE" and all(v["checks"].values()) and v["full_core_unlock"] is False for v in (old, field_record)),
        "actual_mixed_and_current_frequency_sums": all(max(v[k] for k in ("mixed_disagreement", "reverse_disagreement", "current_disagreement")) < POINT_TOLERANCE for e in examples for v in e["matrix_frequency_checks"]),
        "four_dimensional_vacuum_contact_reference": all(v["four_dimensional_current_disagreement"] < POINT_TOLERANCE for v in vacuum),
        "analytic_UV_surface_boundary_not_Ward_projection": all(e["UV_surface_boundary"][-1]["absolute_error"] < 1e-4 and e["UV_surface_boundary"][-1]["absolute_error"] < e["UV_surface_boundary"][0]["absolute_error"] for e in examples),
        "source_covariance_Ward": all(v["covariance_Ward_residual"] < WARD_TOLERANCE for v in rows),
        "reoptimized_field_source_and_current_Ward": all(max(v["Ward_residuals"].values()) < WARD_TOLERANCE for v in rows),
        "current_counterterm_source_replay": all(v["counterterm_residual"] < 1e-9 for v in rows),
        "frequency_first_UV_surface_negative_control": all(v["omit_spatial_UV_surface_Ward"] > WARD_TOLERANCE for v in rows),
        "classical_seagull_negative_control": all(v["omit_classical_seagull_Ward"] > WARD_TOLERANCE for v in rows),
        "rest_frame_current_routing_and_quadrature": all(max(v["last_quadrature_disagreement"], v["routing_disagreement"]) < QUADRATURE_TOLERANCE for v in rows),
        "auxiliary_reference_independence": all(e["auxiliary_reference_disagreement"] < QUADRATURE_TOLERANCE for e in examples),
        "current_source_reality": all(v["current_reality_residual"] < QUADRATURE_TOLERANCE for v in rows),
        "density_current_matches_stationary_envelope": all(v["relative_disagreement"] < 2e-5 and v["phase_density_mixing_residual"] < 1e-9 for e in examples for v in e["charge_envelope"]),
        "uniform_current_stiffness_positive_at_witnesses": all(v["uniform_spatial_stiffness"] > 0 for e in examples for v in e["charge_envelope"]),
    }
    evidence = (FIELD_CODE, FIELD_ARTIFACT, F["BACKGROUND_ARTIFACT"], F["MATCH_ARTIFACT"],
                Path(__file__).relative_to(ROOT).as_posix())
    protected = tuple(p["path"] for p in field_record["protected_evidence_hashes"])
    passed = all(checks.values())
    record = {
        "major_result_id": "T13_FIXED_PHI_HARTREE_SOURCE_COMPLETE_CURRENT",
        "topic": "0.13", "branch_id": old["branch_id"],
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "verification_status": "PASS_REST_FRAME_HARTREE_SOURCE_CURRENT" if passed else "FAIL_HARTREE_SOURCE_CURRENT",
        "what_is_closed": ["computed_mixed_and_four_component_rest_frame_current_response", "source_covariance_and_mean_field_reoptimization", "derived_seagull_and_frequency_first_UV_surface_contact", "actual_Ward_transversality_without_projection", "uniform_density_thermodynamic_envelope_matching"],
        "equation_or_mapping": "deltaI=(I-J_F*K)^-1*(J_F*L*deltavarphi+Y*deltaA); Gamma_AA=s*I+loop_AA+Ybar*[K^-1-J_F]^-1*Y/2; Pi=Gamma_AA-Gamma_Aphi*Gamma_phiphi^-1*Gamma_phiA",
        "units": {"A_Q_varphi": "E", "Y_and_L": "E", "Gamma_current_and_stiffness": "E^2", "current_density": "E^3", "K_J_and_F_squared_coefficient": "dimensionless"},
        "derivation_class": "SOURCE_DERIVED_HARTREE_REST_FRAME_WITH_DECLARED_VACUUM_CONTACT_SUBTRACTION",
        "observable": "conditional_O2_Noether_current_and_density_not_heat_flux_or_material_temperature",
        "data_role": "DERIVED_FIXED_NATURAL_UNIT_WITNESSES_NO_EMPIRICAL_ROWS",
        "state_variables": ["existing_O2_Cartesian_fields_at_fixed_Phi"],
        "excluded_variables": ["R_gen", "R_obs", "nondynamical_A_source"],
        "equation_registry_ids": ["t13.diagnostic.hartree_gauge_source_current", "t13.diagnostic.hartree_vacuum_source_contact"],
        "component_order": ["Euclidean_time", "longitudinal", "transverse_x", "transverse_y"],
        "examples": examples, "vacuum_reference_checks": vacuum, "checks": checks,
        "thresholds": {"direct_frequency_and_vacuum": POINT_TOLERANCE, "quadrature": QUADRATURE_TOLERANCE, "Ward": WARD_TOLERANCE},
        "numerical_arithmetic": {"longdouble_mantissa_bits": int(np.finfo(np.longdouble).nmant), "numerical_errors_are_not_physical_uncertainties": True},
        "source_contact_convention": {"renormalization_scale": 1., "finite_F_A_squared_coefficient_at_scale": 0., "role": "DECLARED_SUBTRACTION_CONVENTION_NOT_MICROSCOPIC_INPUT", "scale_change": "d(loop_Pi)/d(log Qren)=(Q_E^2*I-Q_E*Q_E^T)/(24*pi^2); compensating source-contact running is not full UET RG matching", "spatial_surface": "[Tr(M)-2*M0^2]/(24*pi^2) from the UV IBP boundary, not fitted to Ward residuals"},
        "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in evidence],
        "protected_evidence_hashes": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in protected],
        "method_references": [{"url": "https://arxiv.org/pdf/hep-ph/0203008", "locator": "II/III local source Ward and external effective action", "role": "established_method_not_UET_novelty"}, {"url": "https://arxiv.org/pdf/1410.1337", "locator": "symmetry and translation preserving regularization", "role": "regulator_obligation_not_full_match"}],
        "open_blockers": ["real_axis_spectral_IR_and_truncation_control", "full_covariant_nonuniform_regulator_RG_and_action_input", "joint_Phi_global_state_and_material_source_detector_map", "normal_component_heat_current_SK_KMS_and_collision_transport", "independent_measurement_and_source_uncertainty"],
        "controlling_blocker": "real_axis_regulator_joint_Phi_material_and_transport_matching_not_closed",
        "dependency_unlocked": ["same_candidate_real_axis_and_joint_state_matching_only"],
        "gauge_current_vertex_computed": passed, "rest_frame_current_Ward_verified": passed,
        "imposed_Ward_projection": False, "physical_current_contact_normalization_admitted": False,
        "full_covariant_counterterm_match": False, "RG_invariance_established": False,
        "real_axis_limit_admitted": False, "physical_Kubo_emitted": False,
        "joint_Phi_stationarity_derived": False, "controlled_truncation_error_established": False,
        "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False,
        "core_composition_gate_overwritten": False, "claim_promotion": False,
        "parameter_fitting": False, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
        "clipping": False, "IR_filter": False, "internal_gap_used_as_physical_Goldstone_mass": False,
        "causal_leakage_threshold_changed": False, "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
        "claim_boundary": "Computed rest-frame current/source Hessian of the fixed-Phi Hartree candidate under an explicit MS vacuum-contact convention. Not physical heat flux, microscopic Kubo/SK-KMS, complete covariant/RG construction, real-axis response, material He-II/TTG prediction or global UET closure.",
    }
    record["report"] = {
        "MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"], "WHAT_REMAINS_OPEN": record["open_blockers"],
        "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
        "WHAT_CHANGED": "Computed actual mixed/current loops, seagulls, UV surface and source/mean-field response with unchanged stationary witnesses.",
        "EQUATION_OR_MAPPING": record["equation_or_mapping"],
        "VERIFICATION": "Independent matrix sums, 4D vacuum contact, thermodynamic envelope, Ward and omitted-contact/surface controls.",
        "CONTROLLING_BLOCKER": record["controlling_blocker"],
        "NEXT_ACTION": "Close real-axis/error and full regulator/RG/action input, joint Phi and material/heat-current admission; do not repeat the same rest-frame current calculation.",
        "CLAIM_BOUNDARY": record["claim_boundary"],
    }
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "Ward_max": max(max(v["Ward_residuals"].values()) for e in result["examples"] for v in e["responses"])}, indent=2))
