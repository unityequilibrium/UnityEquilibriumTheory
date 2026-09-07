"""Reproducible Topic 13 cubic-Goldstone projected-current research diagnostic.

This is the declared A=2, Phi=1, mu^2=5 natural-unit candidate, not the
production fixed-Phi EOS. No material data or holdout files are inputs.
A converged finite-basis response is not full transport or Core acceptance.
The collision event integral counts each parent decay once, with identical
daughters divided by 2; its quadratic form also generates crossed processes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from math import factorial
from pathlib import Path
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
mu = math.sqrt(5.0)
V = np.array([[[12, 0, -1], [0, 4, 0], [-1, 0, 0]], [[0, 4, 0], [4, 0, -1], [0, -1, 0]], [[-1, 0, 0], [0, -1, 0], [0, 0, 6]]], complex)
V4 = np.array([np.diag([6, 2, 0]), np.diag([2, 6, 0]), np.diag([0, 0, 6])])

def modes(k):
    """Three positive modes of the fixed live-Phi tree candidate, not the legacy EOS."""
    if not math.isfinite(k) or k <= 0:
        raise ValueError("Mode momentum must be positive and finite.")
    x = k * k
    ys = np.sort(np.roots([1, -(3 * x + 32), 3 * x * x + 44 * x + 108, -x * (x * x + 12 * x + 28)]).real)
    if np.any(ys <= 0):
        raise ValueError(('nonpositive mode', k, ys))
    es = np.sqrt(ys)
    rs = []
    for e in es:
        Q = np.array([[x + 8 - e * e, 2j * mu * e, -2], [-2j * mu * e, x - e * e, 0], [-2, 0, x + 4 - e * e]], complex)
        ev, U = np.linalg.eigh(Q)
        u = U[:, np.argmin(abs(ev))]
        Qp = np.array([[-2 * e, 2j * mu, 0], [-2j * mu, -2 * e, 0], [0, 0, -2 * e]], complex)
        norm = float((-np.vdot(u, Qp @ u)).real)
        if norm <= 0:
            raise ValueError(('bad residue', k, e, norm))
        rs.append(u / math.sqrt(norm))
    return (es, np.array(rs))

def bose(e, T):
    y = e / T
    return 0.0 if y > 700 else 1 / math.expm1(y)

def gold(k):
    es, rs = modes(k)
    return (es[0], rs[0])

def momentum_at_energy(e):
    """Invert the Goldstone dispersion below the first gapped threshold."""
    if not math.isfinite(e) or not 0 < e < math.sqrt(16-2*math.sqrt(37)):
        raise ValueError("Energy is outside the declared single-root interval.")
    y = e * e
    roots = np.roots([1, 12 - 3 * y, 28 - 44 * y + 3 * y * y, -y * (y * y - 32 * y + 108)])
    positives = [r.real for r in roots if abs(r.imag) < 1e-12 and r.real > 0]
    if len(positives) != 1:
        raise ValueError(('nonunique momentum', e, roots))
    return math.sqrt(positives[0])

def velocity(k):
    e, _ = gold(k)
    x = k * k
    y = e * e
    yp = (3 * y * y - (6 * x + 44) * y + (3 * x * x + 24 * x + 28)) / (3 * y * y - 2 * (3 * x + 32) * y + 3 * x * x + 44 * x + 108)
    return k * yp / e

def basis(k, scale, N):
    return np.array([(k / scale) ** j / math.sqrt(factorial(2 * j + 4)) for j in [-1] + list(range(1, N))])

def assemble(T, order, split_order, cutoff, N=4):
    """Integrate the positive event form, then remove momentum before solving.

    The angular average is Delta(h_i) dot Delta(h_j)/3. Constant F gives
    exactly zero event difference. Basis convergence is not implied by radial
    quadrature convergence; both controls are exposed in the output.
    """
    if not math.isfinite(T) or T <= 0 or (not math.isfinite(cutoff)) or (not 0 < cutoff <= 1.6):
        raise ValueError('Require positive temperature and 0 < cutoff <= 1.6 for this declared candidate.')
    for value in (order, split_order, N):
        if isinstance(value, bool) or int(value) != value:
            raise ValueError('Orders and basis size must be integers.')
    if min(order, split_order) < 8 or not 1 <= N <= 10:
        raise ValueError('Orders must be >=8 and basis size within 1..10.')
    c = math.sqrt(7 / 27)
    scale = T / c
    pn, pw = leggauss(order)
    ks = (pn + 1) * cutoff / 2
    kw = pw * cutoff / 2
    fn, fw = leggauss(split_order)
    fs = (fn + 1) / 2
    fw = fw / 2
    G = np.zeros((N, N))
    S = np.zeros(N)
    means = np.zeros(N)
    norm0 = Ecurrent0 = Ecurrent2 = 0.0
    C = np.zeros((N, N))
    bad = 0
    max_er = 0.0
    for p, wp in zip(ks, kw):
        ep, rp = gold(p)
        np_ = bose(ep, T)
        fp = basis(p, scale, N)
        v = velocity(p)
        FE = ep * v / p
        weight = wp * p ** 4 / (6 * math.pi ** 2) * np_ * (1 + np_)
        G += weight * np.outer(fp, fp)
        S += weight * fp * FE
        means += weight * fp
        norm0 += weight
        Ecurrent0 += weight * FE
        Ecurrent2 += weight * FE * FE
        for f, wf in zip(fs, fw):
            q = f * p
            eq, rq = gold(q)
            er = ep - eq
            r = momentum_at_energy(er)
            er_check, rr = gold(r)
            fq = basis(q, scale, N)
            fr = basis(r, scale, N)
            product = (p + q - r) * (p + q + r) * (r - p + q) * (r + p - q)
            if product < 0:
                raise ValueError(('triangle negative', p, f, product))
            qx = math.sqrt(product) / (2 * p)
            qz = (p * p + q * q - r * r) / (2 * p)
            dx = qx * (fr - fq)
            dz = p * (fp - fr) + qz * (fr - fq)
            M = np.einsum('ijk,i,j,k', V, rp, rq.conj(), rr.conj())
            pref = q * r / (4 * math.pi * p * velocity(r)) * abs(M) ** 2
            nq = bose(eq, T)
            nr = bose(er, T)
            flux = np_ * (1 + nq) * (1 + nr)
            wc = wp * p * p / (2 * math.pi ** 2) * (p * wf) * pref * flux / 3
            C += wc * (np.outer(dx, dx) + np.outer(dz, dz))
            max_er = max(max_er, abs(ep - eq - er_check))
    G -= np.outer(means, means) / norm0
    S -= means * Ecurrent0 / norm0
    current_proj = Ecurrent2 - Ecurrent0 ** 2 / norm0
    results = []
    for n in range(1, N + 1):
        g = G[:n, :n]
        coll = C[:n, :n]
        s = S[:n]
        L = np.linalg.cholesky(g)
        B = np.linalg.solve(L, coll)
        B = np.linalg.solve(L, B.T).T
        z = np.linalg.solve(L, s)
        eig = np.linalg.eigvalsh(B)
        if eig[0] <= 0:
            raise ValueError(('nonpositive projected collision', eig))
        response = float(z @ np.linalg.solve(B, z))
        results.append(dict(basis_size=n, response=response, response_over_T2=response / T ** 2, min_rate=float(eig[0]), max_rate=float(eig[-1]), condition=float(eig[-1] / eig[0])))
    return dict(T=T, order=order, split_order=split_order, cutoff=cutoff, current_momentum_coefficient=Ecurrent0 / norm0, projected_current_fraction=current_proj / Ecurrent2, results=results, max_energy_residual=max_er, momentum_null_construction='F=constant -> dx=dz=0 exactly; projected out before inversion', claim='Projected quasiparticle energy-current moment only; not the complete Noether heat current or physical conductivity')

def canonical_current_checks():
    """Compare actual repository currents with the implicit dispersion derivative."""
    from docs.core.uet_covariant_matter import CovariantMatterConfig, coupled_matter_stress_tensor, matter_noether_current
    from docs.core.uet_covariant_response import CovariantResponseConfig, response_stress_tensor
    metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    mc = CovariantMatterConfig(matter_kinetic=1.0, matter_mass_sq=2.0, matter_quartic=1.0, response_coupling=1.0)
    rc = CovariantResponseConfig(epsilon_nc=1.0, response_kinetic=1.0, response_mass_sq=1.0, response_quartic=1.0)
    rows = []
    for k in [0.001, 0.01, 0.1, 0.5]:
        es, rs = modes(k)
        for index, (e, r) in enumerate(zip(es, rs)):
            currents = []
            amp = 0.01
            for angle in np.arange(64) * 2 * math.pi / 64:
                z = r * np.exp(1j * angle)
                v = 2 * amp * z.real
                dt = 2 * amp * (-1j * e * z).real
                dz = 2 * amp * (1j * k * z).real
                fields = np.array([2 + v[0], -v[1]])
                gradients = np.zeros((2, 4))
                gradients[:, 0] = [dt[0] - mu * v[1], -dt[1] - mu * (2 + v[0])]
                gradients[:, 3] = [dz[0], -dz[1]]
                phigrad = np.array([dt[2], 0, 0, dz[2]])
                stress = coupled_matter_stress_tensor(metric, metric, fields, gradients, 1 + v[2], rc, mc) + response_stress_tensor(metric, metric, phigrad, 1 + v[2], rc)
                current = matter_noether_current(metric, fields, gradients, mc)
                currents.append(-stress[0, 3] - mu * current[3])
            measured = float(np.mean(currents)) / amp ** 2
            x = k * k
            y = e * e
            yp = (3 * y * y - (6 * x + 44) * y + (3 * x * x + 24 * x + 28)) / (3 * y * y - 2 * (3 * x + 32) * y + 3 * x * x + 44 * x + 108)
            expected = k * yp
            rows.append(dict(k=k, mode=index, canonical_current_average=measured, E_v_from_implicit_dispersion=expected, relative_error=abs(measured - expected) / abs(expected)))
    return rows

def build_report(*, quick=False):
    """Keep numerical reproducibility separate from physical acceptance."""
    configs = (
        [(24, 24, .8, 3), (40, 40, .8, 3)] if quick else
        [(40, 40, .8, 7), (80, 64, 1.2, 10), (96, 80, 1.6, 10)]
    )
    rows = [assemble(.01, p, q, cutoff, N=n) for p, q, cutoff, n in configs]
    current_checks = canonical_current_checks()
    paths = [
        "docs/core/uet_covariant_matter.py",
        "docs/core/uet_covariant_response.py",
        "docs/scripts/audit/audit_topic13_goldstone_projected_current.py",
    ]
    checks = {
        "positive_projected_rates": all(
            v["min_rate"] > 0 for row in rows for v in row["results"]
        ),
        "variational_sequence_nondecreasing": all(
            all(b["response"] >= a["response"] * (1-1e-9)
                for a, b in zip(row["results"], row["results"][1:]))
            for row in rows
        ),
        "event_energy_conservation": bool(
            max(row["max_energy_residual"] for row in rows) < 1e-12
        ),
        "canonical_current_mapping": bool(
            max(row["relative_error"] for row in current_checks) < 1e-8
        ),
        "current_has_nonzero_momentum_overlap": all(
            row["current_momentum_coefficient"] > 0 for row in rows
        ),
    }
    latest = rows[-1]["results"]
    return {
        "schema_version": "t13-projected-current-research-v1",
        "major_result_id": "T13_GOLDSTONE_PROJECTED_CURRENT_COLLISION_CANDIDATE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "PARTIAL",
        "verification_status": (
            "INTERNAL_NUMERICAL_CANDIDATE_NOT_FULL_TRANSPORT"
            if all(checks.values()) else "FAIL_INTERNAL_DIAGNOSTIC"
        ),
        "what_is_closed": [
            "Cubic Goldstone collision form assembled with exact momentum null direction.",
            "Chemical-work-subtracted current checked against canonical modules.",
            "Quadrature and basis refinement are reported separately.",
        ],
        "what_remains_open": [
            "Certified infinite-basis error bound",
            "Remaining scattering and higher-loop channels",
            "Condensate/charge and material heat-frame closure",
            "SI alpha, source provenance, full SK/KMS",
            "Existing fixed-Phi EOS repair and acceptance-scope repair",
        ],
        "equation_or_mapping": {
            "current": "J_K^i=T^{0i}-mu*N^i; tree mode contribution E_a*v_a^i",
            "projection": "J_perp=J_K-<J_K,P>/<P,P>*P with Bose occupation covariance",
            "collision": "C_ij=integral dGamma*X_eq*Delta(h_i)*Delta(h_j)",
            "equilibrium_flux": "X_eq=n_p*(1+n_q)*(1+n_r)",
            "basis": "h_i=k_z*F_i; F includes x^-1,x,x^2,..., x=k/(T/c)",
            "null_direction": "Constant F is momentum; projected before inversion",
            "response": "R_N=S_N^T*C_N^-1*S_N; finite variational response only",
        },
        "ontology": {
            "C": "not a phonon count or signed charge",
            "Phi": "effective response",
            "R_gen": "derived trace, excluded from state",
            "R_obs": "excluded from dynamics",
        },
        "variable_definitions": {
            "sigma": "radial Cartesian O(2) perturbation",
            "pi": "angular Cartesian perturbation pi=-A*delta(theta), not response-rate Pi",
            "deltaPhi": "effective-response perturbation",
            "N^mu": "Noether charge current, not C",
        },
        "units": {
            "lane": "natural",
            "temperature_momentum_mode_energy": "energy; temperature is not kelvin",
            "sigma_pi_deltaPhi": "energy",
            "R": "energy^4",
            "R_over_T2": "energy^2; not an SI conductivity",
            "projected_rate": "energy = inverse natural time",
        },
        "physical_correspondence": (
            "Canonical flat rotating scalar action -> quasiparticle kinetic current; "
            "material heat-frame and SI correspondence remain open."
        ),
        "derivation_class": "TREE_ACTION_CUBIC_KINETIC_APPROXIMATION",
        "derivation_boundary": "Leading Golden Rule, single Goldstone channel, finite Galerkin basis.",
        "equation_registry_status": "DIAGNOSTIC_ONLY_NOT_A_PHYSICAL_GATE_INPUT",
        "observable": "momentum-projected chemical-work-subtracted energy current",
        "data_role": "INTERNAL_DERIVED_NUMERICAL_COMPARISON",
        "state_variables": ["sigma", "pi", "deltaPhi"],
        "excluded_variables": ["R_gen", "R_obs"],
        "source_hashes": {
            p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths
        },
        "evidence_artifacts": [{"path": paths[-1], "role": "standalone reproducer"}],
        "checks": checks,
        "config": {"A": 2, "Phi": 1, "mu_squared": 5, "T": .01, "quick": quick},
        "galerkin_rows": rows,
        "canonical_current_checks": current_checks,
        "basis_last_relative_change": abs(
            latest[-1]["response"]/latest[-2]["response"]-1
        ),
        "open_blockers": [
            "Physical transport closure unproven",
            "No certified infinite-basis/continuum bound",
            "Material source and calibration unresolved",
        ],
        "controlling_blocker": "Current/condensate/material matching and collision completeness.",
        "next_action": "Repair fixed-Phi EOS; validate full current/transport mapping.",
        "dependency_unlocked": "Diagnostic work only; no physical downstream unlock",
        "full_core_unlock": False,
        "claim_promotion": False,
        "holdout_access": False,
        "parameter_fitting": False,
        "thresholds_changed": False,
        "reproducibility_status": "Standalone script and numerical configuration persisted.",
        "claim_boundary": (
            "Not physical conductivity, full constitutive transport, "
            "external validation or Full Topic 13 closure."
        ),
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = build_report(quick=args.quick)
    payload = json.dumps(report, indent=2, allow_nan=False) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    else:
        print(payload, end='')
    return 0 if all(report['checks'].values()) else 1
if __name__ == '__main__':
    raise SystemExit(main())
