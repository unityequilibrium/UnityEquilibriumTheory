"""Actual finite-q source-response poles in the same fixed-Phi candidate.

Fixed radial nodes and exact complex Cauchy subtraction keep the principal
kernel locally analytic. The retarded sheet uses the accepted spectral cut,
not an assigned width or a change to an older upper-half-plane validator.
"""

from __future__ import annotations

from datetime import datetime, timezone
import gc
import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.optimize import root

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
PREVIOUS_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_Finite_Q_Discontinuity.py"
PREVIOUS_ARTIFACT = PREFIX+"Result/artifacts/t13_hartree_finite_q_discontinuity.json"
D = runpy.run_path(str(ROOT/PREVIOUS_CODE))
P, R, G, F = D["P"], D["R"], D["G"], D["F"]
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_finite_q_poles.json")
SIGNATURE = np.diag([-1., 1., 1., 1.])
SPLIT_RAYS = (.19, .2, .3, .4, .45)
ALTERNATE_RAYS = (.21, .25, .35, .43)
ORDERS = ((64, 24), (96, 32), (128, 40))
ROOT_TOLERANCE = 1e-8
REFINEMENT_TOLERANCE = 2e-5
PHASE_WARD_TOLERANCE = 1e-3
UPPER_REFERENCE_V = .3+.02j
SECOND_SEEDS = P["SEEDS"]


def inverse_shell(ell, mode, mu, a, b):
    """Original outgoing-shell formula in analytic extended arithmetic."""
    ell = np.asarray(ell, np.clongdouble)
    if mode not in range(4):
        raise ValueError("one of four signed modes required")
    residue = np.zeros(ell.shape+(2, 2), np.clongdouble)
    if mu == 0:
        field = 0 if mode in (0, 2) else 1
        rsq = ell*ell-(a if field == 0 else b)
        derivative = 2*ell
        residue[..., field, field] = -1/derivative
    else:
        mu, a, b = map(np.longdouble, (mu, a, b))
        branch = 1 if mode in (1, 2) else -1
        discr = np.sqrt((a-b)**2/4+4*mu*mu*ell*ell)
        rsq = ell*ell-(a+b)/2+branch*discr
        derivative = 2*ell*(1+branch*2*mu*mu/discr)
        det_derivative = 4*ell*(-branch*discr-2*mu*mu)
        residue[..., 0, 0] = ((b-a)/2+branch*discr)/det_derivative
        residue[..., 1, 1] = ((a-b)/2+branch*discr)/det_derivative
        residue[..., 0, 1] = -2j*mu*ell/det_derivative
        residue[..., 1, 0] = 2j*mu*ell/det_derivative
    return rsq, derivative, residue


def occupation_difference(p, ell, incoming, outgoing, t):
    sp, se = (1 if mode >= 2 else -1 for mode in (incoming, outgoing))
    p, ell = np.broadcast_arrays(p, ell)
    if t == 0:
        return np.full(p.shape, .5*(sp-se), np.clongdouble)
    ep, ee = sp*p, se*ell
    if sp == se:
        return sp*np.exp(-ep/t)*(-np.expm1(-(ee-ep)/t))/((-np.expm1(-ep/t))*(-np.expm1(-ee/t)))
    return (sp*np.exp(-ep/t)/(-np.expm1(-ep/t))
            -se*np.exp(-ee/t)/(-np.expm1(-ee/t))+.5*(sp-se))


def joint_polynomial(k, q, p, rp, ell, outgoing, incoming, t, mu, a, b):
    """Sixth vertex is the coefficient of z in the time insertion."""
    k, p, ell = np.broadcast_arrays(k, p, ell)
    rsq, derivative, re = inverse_shell(ell, outgoing, mu, a, b)
    sign = 1 if outgoing >= 2 else -1
    jac = sign*derivative/(2*k*q)
    kz = (rsq-k*k)/(2*q)
    transverse_sq = ((k+q)**2-rsq)*(rsq-(k-q)**2)/(4*q*q)
    vertices = np.zeros(ell.shape+(6, 2, 2), np.clongdouble)
    vertices[..., :3, :, :] = G["BASIS"]
    vertices[..., 3, :, :] = -2*p[..., None, None]*G["ROTATION"]+2j*mu*np.eye(2)
    vertices[..., 4, :, :] = -2j*kz[..., None, None]*G["ROTATION"]
    vertices[..., 5, :, :] = -G["ROTATION"]
    occ = occupation_difference(p, ell, incoming, outgoing, t)
    poly = .5*(occ*jac)[..., None, None]*np.einsum("...aij,...jk,...bkl,...li->...ab", vertices, re, vertices, rp)
    transverse = -transverse_sq*np.einsum("ij,...jk,kl,...li->...", G["ROTATION"], re, G["ROTATION"], rp)*occ*jac
    return poly, transverse


def evaluate_polynomial(poly, z):
    result = poly[..., :5, :5].copy()
    result[..., 3, :] += z*poly[..., 5, :5]
    result[..., :, 3] += z*poly[..., :5, 5]
    result[..., 3, 3] += z*z*poly[..., 5, 5]
    return result


class AngularKernel:
    """Cache frequency polynomials, not fitted response values."""

    def __init__(self, k, q, t, mu, a, b, order=24):
        F["validate"](t, mu, a, b, q, 0j)
        if q <= 0 or isinstance(order, bool) or not isinstance(order, int) or order < 16:
            raise ValueError("positive q and integer angular order>=16 required")
        self.k = np.atleast_1d(np.asarray(k, np.longdouble))
        if np.any(~np.isfinite(self.k)) or np.any(self.k <= 0):
            raise ValueError("positive finite radial nodes required")
        self.q, self.t, self.mu, self.a, self.b = q, t, mu, a, b
        self.p, self.rp = G["extended_poles"](self.k, mu, a, b)
        left = G["extended_poles"](abs(self.k-q), mu, a, b)[0]
        right = G["extended_poles"](self.k+q, mu, a, b)[0]
        x, w = np.polynomial.legendre.leggauss(order)
        x, w = np.asarray((x+1)/2, np.longdouble), np.asarray(w/2, np.longdouble)
        self.polynomial_contact = np.zeros(len(self.k), np.clongdouble)
        self.items = []
        for outgoing in range(4):
            lo, hi = np.minimum(left[:, outgoing], right[:, outgoing]), np.maximum(left[:, outgoing], right[:, outgoing])
            ell = lo[:, None]+(hi-lo)[:, None]*x
            weights = (hi-lo)[:, None]*w
            _, derivative, re = inverse_shell(ell, outgoing, mu, a, b)
            jac = (1 if outgoing >= 2 else -1)*derivative/(2*self.k[:, None]*q)
            self.polynomial_contact += 2*np.sum(weights*np.trace(re, axis1=-2, axis2=-1)*G["occupations"](ell.real, t)*jac, axis=1)
            for incoming in range(4):
                ps, rp = self.p[:, incoming], self.rp[:, incoming]
                poly, tr = joint_polynomial(self.k[:, None], q, ps[:, None], rp[:, None], ell, outgoing, incoming, t, mu, a, b)
                midpoint = (lo+hi)/2
                ref_poly, ref_tr = joint_polynomial(self.k, q, ps, rp, midpoint, outgoing, incoming, t, mu, a, b)
                self.items.append((incoming, outgoing, lo, hi, ell, weights, poly, tr, ref_poly, ref_tr))

    def evaluate(self, frequency):
        if not np.isfinite(frequency):
            raise ValueError("finite complex frequency required")
        z = np.clongdouble(frequency)
        result = np.zeros((len(self.k), 5, 5), np.clongdouble)
        result[:, 3, 3] = self.polynomial_contact
        transverse = np.zeros(len(self.k), np.clongdouble)
        for incoming, outgoing, lo, hi, ell, weights, poly, tr, ref_poly, ref_tr in self.items:
            ps = self.p[:, incoming]
            numerator = evaluate_polynomial(poly, z)
            if incoming == outgoing and self.t > 0:
                ref, tr_ref = joint_polynomial(self.k, self.q, ps, self.rp[:, incoming], ps+z,
                                               outgoing, incoming, self.t, self.mu, self.a, self.b)
                n0 = evaluate_polynomial(ref, z)
            else:
                n0, tr_ref = evaluate_polynomial(ref_poly, z), ref_tr
            denominator = ps[:, None]+z-ell
            if np.any(denominator == 0):
                raise ValueError("exact pole node requires an analytic derivative limit, not a zero-fill")
            integrand = (numerator-n0[:, None]) / denominator[..., None, None]
            ti = (tr-tr_ref[:, None])/denominator
            logarithm = np.log1p((hi-lo)/(ps+z-hi))
            if z.imag == 0:
                inside = (ps+z.real > lo) & (ps+z.real < hi)
                logarithm = logarithm.real-1j*pi*inside
            result += np.sum(weights[..., None, None]*integrand, axis=1)+n0*logarithm[:, None, None]
            transverse += np.sum(weights*ti, axis=1)+tr_ref*logarithm
        return result, transverse


class VacuumAngularKernel:
    """Equal-mass reference integrated analytically, with a bounded series.

    Only opposite-sign vacuum poles contribute. Centered shell coordinates
    avoid subtracting k^2 terms in the longitudinal numerator or moments.
    """

    def __init__(self, k, q, mass_sq=1.):
        self.k = np.asarray(k, np.longdouble)
        self.q, self.mass_sq = np.longdouble(q), np.longdouble(mass_sq)
        self.energy = np.sqrt(self.k*self.k+mass_sq)
        self.mid_energy = (np.sqrt((self.k-q)**2+mass_sq)+np.sqrt((self.k+q)**2+mass_sq))/2
        self.half_width = self.k*q/self.mid_energy

    def moments(self, target):
        ratio = self.half_width/target
        if np.any(abs(ratio) >= .05):
            raise ValueError("vacuum centered-moment series outside its declared convergence domain")
        moments = []
        for power in range(5):
            parity = power % 2
            series = sum(ratio**m/(power+m+1) for m in range(parity, parity+32, 2))
            moments.append(2*self.half_width**(power+1)/target*series)
        return moments

    def evaluate(self, frequency):
        z, q, k, h = np.clongdouble(frequency), self.q, self.k, self.half_width
        result = np.zeros((len(k), 5, 5), np.clongdouble)
        result[:, 3, 3] = -4/self.mid_energy
        transverse = np.zeros(len(k), np.clongdouble)
        for sign in (-1, 1):
            p, midpoint = sign*self.energy, -sign*self.mid_energy
            moments = self.moments(p+z-midpoint)
            vertices = np.zeros((len(k), 3, 5, 2, 2), np.clongdouble)
            vertices[:, 0, :3] = G["BASIS"]
            vertices[:, 0, 3] = -(2*p+z)[:, None, None]*G["ROTATION"]
            vertices[:, 0, 4] = (-1j*(q*q-h*h)/q)[:, None, None]*G["ROTATION"]
            vertices[:, 1, 4] = (-2j*midpoint/q)[:, None, None]*G["ROTATION"]
            vertices[:, 2, 4] = -1j/q*G["ROTATION"]
            coefficient = -1/(8*k*q*p)
            for first in range(3):
                for second in range(3):
                    trace = np.einsum("...aij,...bji->...ab", vertices[:, first], vertices[:, second])
                    result += (coefficient*moments[first+second])[:, None, None]*trace
            transverse_poly = (k*k-h**4/(4*q*q), midpoint*h*h/(q*q),
                               -(midpoint*midpoint-h*h/2)/(q*q), -midpoint/(q*q), -np.ones_like(k)/(4*q*q))
            transverse -= sum(transverse_poly[n]*moments[n] for n in range(5))/(2*k*q*p)
        return result, transverse


def direct_angular_moments(k, q, z, example, order=256):
    """Independent unsplit angle and polynomial Matsubara moment identity."""
    F["validate"](example["T"], example["mu"], example["a"], example["b"], q, 0j)
    if q <= 0 or not np.isfinite(z) or complex(z).imag == 0:
        raise ValueError("positive q and nonreal finite frequency required")
    c, weights = np.polynomial.legendre.leggauss(order)
    shifted = np.sqrt(k*k+q*q+2*k*q*c)
    midpoint = k*c+q/2
    p, rp = G["extended_poles"](k, example["mu"], example["a"], example["b"])
    ell, re = G["extended_poles"](shifted, example["mu"], example["a"], example["b"])
    moments = G["frequency_moments"](p[None, :, None], ell[:, None, :], example["T"], z)
    operators = np.zeros((len(c), 2, 5, 2, 2), np.clongdouble)
    operators[:, 0, :3] = G["BASIS"]
    operators[:, 0, 3] = -z*G["ROTATION"]+2j*example["mu"]*np.eye(2)
    operators[:, 0, 4] = -2j*midpoint[:, None, None]*G["ROTATION"]
    operators[:, 1, 3] = -2*G["ROTATION"]
    joint = np.zeros((len(c), 5, 5), np.clongdouble)
    for first in range(2):
        for second in range(2):
            trace = np.einsum("...aij,...tjk,...bkl,sli->...abst", operators[:, first], re, operators[:, second], rp)
            joint -= .5*np.sum(trace*moments[first+second][:, None, None], axis=(-2, -1))
    trace_j = np.einsum("ij,...tjk,kl,sli->...st", G["ROTATION"], re, G["ROTATION"], rp)
    transverse = k*k*(1-c*c)*np.sum(trace_j*moments[0], axis=(-2, -1))
    return R["unpack_joint"](np.asarray(np.sum(weights[:, None, None]*joint, axis=0), complex), complex(np.sum(weights*transverse)))


def fixed_radial_nodes(q, example, order, rays=SPLIT_RAYS):
    if isinstance(order, bool) or not isinstance(order, int) or order < 32:
        raise ValueError("integer radial order>=32 required")
    if not rays or any(not .19 <= ray <= .45 for ray in rays):
        raise ValueError("declared positive local split rays required")
    endpoints = []
    for ray in rays:
        endpoints += R["radial_endpoints"](q, q*ray, example["mu"], example["a"], example["b"])
    scale = np.longdouble(max(example["mu"], sqrt(example["a"]), sqrt(example["b"]), 1.))
    splits = np.unique(np.r_[0., np.asarray(endpoints)/(scale+np.asarray(endpoints)), 1.])
    nodes, weights = np.polynomial.legendre.leggauss(order)
    u, weights = np.asarray((nodes+1)/2, np.longdouble), np.asarray(weights/2, np.longdouble)
    ks, measures = [], []
    for lo, hi in zip(splits[:-1], splits[1:]):
        if hi == 1:
            r = np.sqrt((1-u)*(1+u))
            x, dx = lo+(hi-lo)*(1-r), (hi-lo)*u/r
        else:
            x, dx = lo+(hi-lo)*np.sin(pi*u/2)**2, (hi-lo)*pi/2*np.sin(pi*u)
        k = scale*x/(1-x)
        ks.append(k)
        measures.append(weights*dx*scale/(1-x)**2*k*k/(4*pi*pi))
    return np.concatenate(ks), np.concatenate(measures), [float(s) for s in splits]


def lower_reciprocity(loops):
    return {"bubble": loops["bubble"].conj().T,
            "mixed": loops["reverse"].conj().T@SIGNATURE,
            "reverse": SIGNATURE@loops["mixed"].conj().T,
            "loop_current": SIGNATURE@loops["loop_current"].conj().T@SIGNATURE}


def vacuum_reference(q, z, mass_sq=1., scale=1.):
    x, w = np.polynomial.legendre.leggauss(128)
    x, w = (x+1)/2, w/2
    invariant = q*q-z*z
    logs = np.log((mass_sq+x*(1-x)*invariant)/scale**2)
    bubble = np.sum(w*logs)/(16*pi*pi)*np.eye(3)
    coefficient = -np.sum(w*(1-2*x)**2*logs)/(16*pi*pi)
    qe = np.array([-1j*z, q, 0., 0.])
    return bubble, coefficient*(invariant*np.eye(4)-np.outer(qe, qe))


def response(q, z, example, loops):
    """Same block equations, independently allowed local lower continuation."""
    mu, a, b, s, coupling = (example[key] for key in ("mu", "a", "b", "s", "u_canonical"))
    _, kernel, vertices = F["source_vertices"](s, coupling)
    bubble = loops["bubble"]
    covariance = np.eye(3)-kernel@bubble
    internal = np.array([[q*q+a-z*z, 2j*mu*z], [-2j*mu*z, q*q+b-z*z]])
    field = internal+.5*vertices.T@bubble@np.linalg.solve(covariance, vertices)
    forward, reverse, aa = G["classical_vertices"](q, z, mu, s)
    forward += .5*vertices.T@np.linalg.solve(np.eye(3)-bubble@kernel, loops["mixed"])
    reverse += .5*loops["reverse"]@np.linalg.solve(covariance, vertices)
    aa += loops["loop_current"]+.5*loops["reverse"]@kernel@np.linalg.solve(np.eye(3)-bubble@kernel, loops["mixed"])
    radial = field[0, 0]
    phase = field[1, 1]-field[1, 0]*field[0, 1]/radial
    radial_current = aa-np.outer(reverse[:, 0], forward[0])/radial
    qe = np.array([-1j*z, q, 0., 0.])
    source_phase = qe@radial_current@qe/s
    return {"phase_coefficient": complex(phase/q**2), "radial_inverse": complex(radial),
            "covariance_determinant": complex(np.linalg.det(covariance)),
            "covariance_min_singular_value": float(np.linalg.svd(covariance, compute_uv=False)[-1]),
            "uneliminated_scaled_determinant": complex(np.linalg.det(covariance)*np.linalg.det(field)/q**2),
            "phase_current_Ward_disagreement": float(abs(phase-source_phase)/q**2),
            "field": field, "radial_current": radial_current}


class FiniteQKernel:
    def __init__(self, example, q, radial_order=64, angular_order=24, rays=SPLIT_RAYS):
        D["validate"](q, .3, example, radial_order)
        self.example, self.q, self.radial_order, self.angular_order = example, q, radial_order, angular_order
        k, self.measure, self.splits = fixed_radial_nodes(q, example, radial_order, rays)
        self.actual = AngularKernel(k, q, example["T"], example["mu"], example["a"], example["b"], angular_order)
        self.reference = VacuumAngularKernel(k, q)
        cov = G["point_covariance"](k, example["T"], example["mu"], example["a"], example["b"])-G["point_covariance"](k, 0., 0., 1., 1.)
        self.contact = 2*np.trace(cov, axis1=-2, axis2=-1)

    def principal_loops(self, v, direct_lower=False):
        v = complex(v)
        if not np.isfinite(v):
            raise ValueError("finite complex velocity required")
        if v.imag < 0:
            D["validate"](self.q, v, self.example, self.radial_order)
            if not direct_lower:
                return lower_reciprocity(self.principal_loops(v.conjugate()))
        z = self.q*v
        actual, transverse = self.actual.evaluate(z)
        reference, tr_ref = self.reference.evaluate(z)
        difference = actual-reference
        difference[:, 3, 3] += self.contact
        difference[:, 4, 4] += self.contact
        transverse += self.contact-tr_ref
        joint = np.asarray(np.sum(self.measure[:, None, None]*difference, axis=0), complex)
        tr = complex(np.sum(self.measure*transverse))
        bubble, mixed, reverse, current = R["unpack_joint"](joint, tr)
        bubble_ref, current_ref = vacuum_reference(self.q, z)
        bubble += bubble_ref
        current += current_ref
        current[1:, 1:] += G["spatial_surface_contact"](self.example["mu"], self.example["a"], self.example["b"], 1.)*np.eye(3)
        return {"bubble": bubble, "mixed": mixed, "reverse": reverse, "loop_current": current}

    def response(self, v, sheet="retarded_local", contour="horizontal"):
        if sheet not in ("retarded_local", "principal_lower"):
            raise ValueError("declared local sheet required")
        v = complex(v)
        loops = self.principal_loops(v)
        if v.imag < 0 and sheet == "retarded_local":
            density, _ = D["spectral_tail"](self.q, v, self.example, self.radial_order, contour)
            loops = {key: loops[key]-2j*pi*density[key] for key in loops}
        return response(self.q, self.q*v, self.example, loops)

    def pole(self, seed):
        def equations(values):
            value = self.response(complex(*values))["phase_coefficient"]
            return [value.real, value.imag]
        result = root(equations, [complex(seed).real, complex(seed).imag], tol=1e-9)
        pole = complex(*result.x)
        residual = abs(self.response(pole)["phase_coefficient"])
        if residual > ROOT_TOLERANCE or pole.imag >= 0:
            raise ValueError(f"actual finite-q pole not established: residual={residual}")
        return pole, float(residual)


def derivative_check(kernel, pole):
    rows = []
    for h in (1e-4, 5e-5):
        dx = (kernel.response(pole+h)["phase_coefficient"]-kernel.response(pole-h)["phase_coefficient"])/(2*h)
        dy = (kernel.response(pole+1j*h)["phase_coefficient"]-kernel.response(pole-1j*h)["phase_coefficient"])/(2j*h)
        rows.append({"step": h, "real_direction_derivative": F["complex_matrix"](np.asarray(dx)),
                     "imag_direction_derivative": F["complex_matrix"](np.asarray(dy)),
                     "Cauchy_Riemann_disagreement": float(abs(dx-dy))})
    derivative = G["unpack"](rows[-1]["real_direction_derivative"])
    return {"runs": rows, "derivative_modulus": float(abs(derivative)),
            "derivative_refinement": float(abs(derivative-G["unpack"](rows[0]["real_direction_derivative"]))),
            "local_inverse_residue_in_v": F["complex_matrix"](np.asarray(1/derivative))}


def angular_audit(example):
    rows = []
    for k in (.09, .3, 1.2):
        kernel = AngularKernel([k], .04, example["T"], example["mu"], example["a"], example["b"], 48)
        upper = .04*(.3+.1j)
        values = {}
        for name, z in (("upper", upper), ("lower", upper.conjugate())):
            joint, transverse = kernel.evaluate(z)
            actual = dict(zip(("bubble", "mixed", "reverse", "loop_current"), R["unpack_joint"](joint[0], transverse[0])))
            direct = dict(zip(actual, direct_angular_moments(k, .04, z, example)))
            values[name] = actual
            rows.append({"k": k, "q": .04, "half_plane": name,
                         "independent_moment_errors": D["errors"](actual, direct)})
        rows.append({"k": k, "source_signature_reciprocity_errors": D["errors"](values["lower"], lower_reciprocity(values["upper"]))})
    return rows


def audit(progress=None):
    predecessor = json.loads((ROOT/PREVIOUS_ARTIFACT).read_text(encoding="utf-8"))
    examples = []
    for e in predecessor["examples"]:
        example = {key: e[key] for key in ("T", "mu", "Phi_fixed", "a", "b", "s", "u_canonical")}
        soft_pole = G["unpack"](e["complex_density_runs"][0]["velocity_reference_is_prior_soft_pole_not_finite_q_pole"])
        q_rows = []
        for q in D["Q_GRID"]:
            runs = []
            for radial_order, angular_order in ORDERS:
                kernel = FiniteQKernel(example, q, radial_order, angular_order)
                pole, residual = kernel.pole(soft_pole)
                result = kernel.response(pole)
                runs.append({"radial_order": radial_order, "angular_order": angular_order,
                             "velocity_pole": F["complex_matrix"](np.asarray(pole)), "frequency_pole": F["complex_matrix"](np.asarray(q*pole)),
                             "inverse_residual": residual, "phase_current_Ward_disagreement": result["phase_current_Ward_disagreement"],
                             "radial_inverse": F["complex_matrix"](np.asarray(result["radial_inverse"])),
                             "covariance_determinant": F["complex_matrix"](np.asarray(result["covariance_determinant"])),
                             "covariance_min_singular_value": result["covariance_min_singular_value"],
                             "uneliminated_scaled_determinant_residual": float(abs(result["uneliminated_scaled_determinant"])),
                             "fixed_radial_splits": kernel.splits})
                if progress:
                    progress(f"mu={e['mu']}, q={q}, order={radial_order}/{angular_order}: pole {pole}, residual {residual}")
                if (radial_order, angular_order) != ORDERS[-1]:
                    del kernel
                    gc.collect()
            second_seed_results = [kernel.pole(seed)[0] for seed in SECOND_SEEDS]
            principal = kernel.principal_loops(pole)
            direct_lower = kernel.principal_loops(pole, direct_lower=True)
            upper = kernel.principal_loops(UPPER_REFERENCE_V)
            original_rows = []
            for old_order in (64, 96, 128):
                original = R["retarded_loops"](q, q*UPPER_REFERENCE_V, example["T"], example["mu"], example["a"], example["b"], old_order, 64)
                original_rows.append({"original_radial_order": old_order,
                                      "loop_disagreements": D["errors"](upper, {key: original[key] for key in upper})})
            _, density_checks = D["spectral_tail"](q, pole, example, ORDERS[-1][0])
            alternate_tail = kernel.response(pole, contour="return_to_real")["phase_coefficient"]
            derivatives = derivative_check(kernel, pole)
            wrong_sheet = abs(kernel.response(pole, sheet="principal_lower")["phase_coefficient"])
            q_rows.append({"q": q, "pole_runs": runs,
                           "pole_refinements": [float(abs(G["unpack"](runs[i]["velocity_pole"])-G["unpack"](runs[i-1]["velocity_pole"]))) for i in (1, 2)],
                           "second_seed_disagreements": [float(abs(value-pole)) for value in second_seed_results],
                           "direct_lower_reciprocity_disagreement": D["errors"](principal, direct_lower),
                           "original_upper_reference": original_rows,
                           "alternate_tail_inverse_residual": float(abs(alternate_tail)),
                           "local_density_domain_checks_at_actual_pole": density_checks,
                           "principal_lower_negative_control_residual": float(wrong_sheet),
                           "simple_pole_derivative": derivatives, "difference_from_soft_pole": float(abs(pole-soft_pole))})
            del kernel
            gc.collect()
        alternative = FiniteQKernel(example, D["Q_GRID"][0], *ORDERS[-1], rays=ALTERNATE_RAYS)
        alt_pole, _ = alternative.pole(soft_pole)
        alternative_error = abs(alt_pole-G["unpack"](q_rows[0]["pole_runs"][-1]["velocity_pole"]))
        del alternative
        gc.collect()
        examples.append(example | {"soft_pole_reference": F["complex_matrix"](np.asarray(soft_pole)), "finite_q_runs": q_rows,
                                   "alternate_fixed_grid_q": D["Q_GRID"][0], "alternate_fixed_grid_pole_disagreement": float(alternative_error),
                                   "independent_angular_moment_checks": angular_audit(example)})
    vacuum_ks = np.array([.02, .2, 1., 20., 150.])
    vacuum = VacuumAngularKernel(vacuum_ks, .04)
    vacuum_actual = vacuum.evaluate(.012+.003j)
    vacuum_original = R["angular_kernel"](vacuum_ks, .04, .012+.003j, 0., 0., 1., 1., 64)
    vacuum_errors = {"joint": float(np.max(abs(vacuum_actual[0]-vacuum_original[0]))),
                     "transverse": float(np.max(abs(vacuum_actual[1]-vacuum_original[1])))}
    checks = {
        "accepted_predecessor_and_protected_lineage": predecessor["closure_level"] == "CLOSED_FOR_LANE" and all(predecessor["checks"].values()) and R["predecessor_hashes_match"](predecessor),
        "independent_upper_and_lower_frequency_moment_identity": all(max(row["independent_moment_errors"].values()) < 1e-7 for e in examples for row in e["independent_angular_moment_checks"] if "independent_moment_errors" in row),
        "source_signature_point_and_integrated_reciprocity": all(max(row["direct_lower_reciprocity_disagreement"].values()) < 1e-9 for e in examples for row in e["finite_q_runs"]) and all(max(row["source_signature_reciprocity_errors"].values()) < 1e-9 for e in examples for row in e["independent_angular_moment_checks"] if "source_signature_reciprocity_errors" in row),
        "analytic_vacuum_reference_matches_original": max(vacuum_errors.values()) < 1e-9,
        "original_upper_reference_agreement": all(max(row["original_upper_reference"][-1]["loop_disagreements"].values()) < REFINEMENT_TOLERANCE for e in examples for row in e["finite_q_runs"]),
        "actual_finite_q_simple_pole_without_assigned_width": all(run["inverse_residual"] < ROOT_TOLERANCE and G["unpack"](run["velocity_pole"]).imag < 0 for e in examples for row in e["finite_q_runs"] for run in row["pole_runs"]),
        "orders_seeds_and_alternate_fixed_grid_agree": all(max(row["pole_refinements"]+row["second_seed_disagreements"]) < REFINEMENT_TOLERANCE for e in examples for row in e["finite_q_runs"]) and all(e["alternate_fixed_grid_pole_disagreement"] < REFINEMENT_TOLERANCE for e in examples),
        "phase_current_Ward_without_projection": all(run["phase_current_Ward_disagreement"] < PHASE_WARD_TOLERANCE for e in examples for row in e["finite_q_runs"] for run in row["pole_runs"]),
        "elimination_denominators_not_false_pole": all(abs(G["unpack"](run["radial_inverse"])) > .01 and abs(G["unpack"](run["covariance_determinant"])) > .01 and run["covariance_min_singular_value"] > .01 and run["uneliminated_scaled_determinant_residual"] < ROOT_TOLERANCE for e in examples for row in e["finite_q_runs"] for run in row["pole_runs"]),
        "simple_derivative_and_local_Cauchy_Riemann": all(row["simple_pole_derivative"]["derivative_modulus"] > 1e-3 and row["simple_pole_derivative"]["derivative_refinement"] < REFINEMENT_TOLERANCE and max(run["Cauchy_Riemann_disagreement"] for run in row["simple_pole_derivative"]["runs"]) < REFINEMENT_TOLERANCE for e in examples for row in e["finite_q_runs"]),
        "two_complex_tail_paths_agree_at_actual_pole": all(row["alternate_tail_inverse_residual"] < ROOT_TOLERANCE for e in examples for row in e["finite_q_runs"]),
        "principal_lower_is_not_retarded_pole": all(row["principal_lower_negative_control_residual"] > 1e-3 for e in examples for row in e["finite_q_runs"]),
        "finite_q_pole_approaches_soft_without_being_substituted": all(e["finite_q_runs"][2]["difference_from_soft_pole"] < e["finite_q_runs"][1]["difference_from_soft_pole"] < e["finite_q_runs"][0]["difference_from_soft_pole"] and e["finite_q_runs"][0]["difference_from_soft_pole"] > 1e-6 for e in examples),
        "actual_pole_sampled_density_domain": all(c["shell_root_residual"] < 1e-11 and c["minimum_outgoing_energy_real"] > 0 and c["minimum_Bose_denominator"] > .01 for e in examples for row in e["finite_q_runs"] for c in row["local_density_domain_checks_at_actual_pole"]),
        "protected_evidence_hashes_unchanged": all(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in predecessor["protected_evidence_hashes"])}
    passed = all(checks.values())
    record = {"schema_version": "t13-hartree-finite-q-poles-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
              "major_result_id": "T13_FIXED_PHI_HARTREE_FINITE_Q_LANDAU_POLES", "topic": "0.13", "branch_id": predecessor["branch_id"],
              "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL", "verification_status": "PASS_SCOPED_FINITE_Q_POLES" if passed else "FAIL_FINITE_Q_POLES",
              "what_is_closed": ["fixed_grid_principal_kernel_with_complex_Cauchy_subtraction", "independent_lower_source_signature_reciprocity_and_exact_vacuum_reference", "actual_finite_q_complex_phase_poles_at_six_declared_points", "finite_q_to_soft_pole_approach_with_denominator_Ward_and_local_analyticity_checks"],
              "equation_or_mapping": "B_L(q,z)=B_principal_lower(q,z)-2*pi*i*D(q,z/q); Gamma_phase=Gamma_pp-Gamma_pr*Gamma_rp/Gamma_rr; Gamma_phase(q,z_pole)=0; det_full=det(I-K_cov*J)*det(Gamma_field)",
              "units": {"q_z_T_mu": "E", "v": "dimensionless", "field_inverse": "E^2", "bubble": "dimensionless", "mixed": "E", "current": "E^2", "full_determinant": "E^4", "scaled_determinant": "E^2"},
              "derivation_class": "SAME_ACTION_FINITE_Q_LOCAL_CAUCHY_CONTINUATION_AND_NUMERICAL_POLE", "observable": "conditional_phase_resolvent_pole_not_material_sound_or_heat_transport", "data_role": "DERIVED_NO_EMPIRICAL_ROWS",
              "equation_registry_ids": ["t13.diagnostic.hartree_finite_q_principal_kernel", "t13.diagnostic.hartree_finite_q_phase_pole"],
              "examples": examples, "checks": checks, "vacuum_reference_check": vacuum_errors,
              "runtime_arithmetic": {"longdouble_bits": np.finfo(np.longdouble).bits, "clongdouble_itemsize": np.dtype(np.clongdouble).itemsize, "extended_precision_not_assumed": True},
              "config": {"q_grid": D["Q_GRID"], "orders": ORDERS, "split_rays": SPLIT_RAYS, "alternate_split_rays": ALTERNATE_RAYS,
                         "initial_seed": "accepted prior soft pole, not a substituted finite-q answer", "second_seeds": [[v.real, v.imag] for v in SECOND_SEEDS],
                         "upper_reference_velocity": F["complex_matrix"](np.asarray(UPPER_REFERENCE_V)), "lower_domain": D["LOCAL_DOMAIN"],
                         "radial_domain": "0<=k<infinity", "assigned_output_width": None, "vacuum_centered_series_terms": 16, "vacuum_max_ratio_required": .05},
              "thresholds": {"root_absolute": ROOT_TOLERANCE, "refinement_absolute": REFINEMENT_TOLERANCE, "phase_current_Ward_absolute": PHASE_WARD_TOLERANCE, "causal_leakage_unchanged": 1e-6},
              "evidence_artifacts": [{"path": path, "sha256": hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for path in (PREVIOUS_ARTIFACT, PREVIOUS_CODE, Path(__file__).relative_to(ROOT).as_posix())],
              "protected_evidence_hashes": predecessor["protected_evidence_hashes"],
              "open_blockers": ["certified_global_complex_domain_and_stability", "controlled_Hartree_truncation_and_regulator_RG_full_action", "joint_Phi_stationarity_and_material_source_detector", "independent_thermal_scale_and_physical_heat_collision_KMS_entropy_transport"],
              "controlling_blocker": "global_domain_Hartree_remainder_joint_Phi_material_transport_not_closed",
              "dependency_unlocked": ["same_candidate_global_domain_approximation_action_and_joint_Phi_research_only"],
              "finite_q_complex_pole_computed": bool(passed), "conditional_collisionless_soft_pole_inherited": True,
              "certified_global_stability": False, "certified_global_contour_homotopy": False, "physical_mode_speed_emitted": False, "collision_rate_emitted": False,
              "controlled_truncation_error_established": False, "joint_Phi_stationarity_derived": False, "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False, "claim_promotion": False,
              "parameter_fitting": False, "artificial_width": False, "clipping": False, "IR_filter": False, "imposed_Ward_projection": False, "xie_2026_accessed": False,
              "prior_Xie_context_exposure_review": "REVIEW_REQUIRED", "core_composition_gate_overwritten": False, "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
              "excluded_variables": ["R_gen", "R_obs", "nondynamical_A"],
              "claim_boundary": "Actual local finite-q collisionless phase poles at two unchanged fixed-Phi witnesses and q=.04/.02/.01, with independent algebra/cuts/source reciprocity and numerical convergence. Not global stability, a controlled Hartree remainder, joint-Phi/material sound, physical collision/Kubo/SK-KMS/heat/entropy, SI normalization, empirical validation or Full Topic13."}
    record["report"] = {"MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"], "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"], "WHAT_REMAINS_OPEN": record["open_blockers"],
                        "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"], "WHAT_CHANGED": "Computed actual fixed-grid finite-q retarded-sheet phase poles; independently checked moment/source algebra, reference and denominator/refinement controls.",
                        "EQUATION_OR_MAPPING": record["equation_or_mapping"], "VERIFICATION": checks, "CONTROLLING_BLOCKER": record["controlling_blocker"],
                        "NEXT_ACTION": "Control global domain and Hartree/action approximation obligations before joint-Phi/material/thermal-input and heat-current admission; do not repeat unchanged pole roots.", "CLAIM_BOUNDARY": record["claim_boundary"]}
    return record


if __name__ == "__main__":
    result = audit(progress=lambda message: print(message, flush=True))
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2), flush=True)
