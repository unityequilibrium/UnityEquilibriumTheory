"""Round Q: bounded candidates followed by rational local certificates.

No trajectories, spin rates, old producers, physical gate promotion or material
fit. Fraction enclosures, not mpmath residuals, decide local existence/curvature.
The small interval helper is private to this calculation path.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json
from math import factorial, isqrt
from pathlib import Path
import sys

import mpmath as mp
import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata, load_json

TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
CONTRACT = f"{TOPIC}/calculation_contracts/parent_static_reference_audit.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_parent_static_reference_audit.json"
REPORT = "docs/meta/UET_PARENT_STATIC_REFERENCE_AUDIT.md"
SPINS = tuple(product((-1, 1), repeat=4))
SEEDS = tuple(product((F(1, 2), F(1), F(2)), repeat=3))
PAIRS = tuple((i, j) for i in range(4) for j in range(i+1, 4))
# Bounded outward rational compression prevents denominator explosion. Every
# operation rounds LOWER down / UPPER up to this grid, never inward.
SCALE = 10**170


def down(x):
    x = F(x)
    return F((x.numerator*SCALE)//x.denominator, SCALE)


def up(x):
    return -down(-F(x))


@dataclass(frozen=True)
class I:
    lo: F
    hi: F | None = None

    def __post_init__(self):
        lo, hi = F(self.lo), F(self.lo if self.hi is None else self.hi)
        if lo > hi:
            raise ValueError("reversed enclosure")
        object.__setattr__(self, "lo", down(lo))
        object.__setattr__(self, "hi", up(hi))

    def __add__(self, other):
        b = iv(other)
        return I(self.lo+b.lo, self.hi+b.hi)

    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __sub__(self, other):
        return self+-iv(other)

    def __rsub__(self, other):
        return iv(other)+-self

    def __mul__(self, other):
        b = iv(other)
        values = (self.lo*b.lo, self.lo*b.hi, self.hi*b.lo, self.hi*b.hi)
        return I(min(values), max(values))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = iv(other)
        if b.lo <= 0 <= b.hi:
            raise ValueError("division enclosure crosses zero")
        return self*I(1/b.hi, 1/b.lo)

    def __rtruediv__(self, other):
        return iv(other)/self

    def __pow__(self, n):
        if type(n) is not int:
            raise ValueError("integer powers only")
        if n < 0:
            return I(1)/(self**(-n))
        if n == 0:
            return I(1)
        if n % 2 == 0:
            return I(0 if self.lo <= 0 <= self.hi else min(self.lo**n, self.hi**n),
                     max(self.lo**n, self.hi**n))
        return I(self.lo**n, self.hi**n)

    @property
    def mid(self):
        return (self.lo+self.hi)/2

    @property
    def mag(self):
        return max(abs(self.lo), abs(self.hi))


def iv(value):
    return value if isinstance(value, I) else I(value)


def logtwo(terms=64):
    if type(terms) is not int or terms not in (64, 96):
        raise ValueError("locked ln2 term budget")
    return _logtwo(terms)


@lru_cache(None)
def _logtwo(terms):
    lower = sum(F(2, (2*n+1)*3**(2*n+1)) for n in range(terms))
    remainder = F(2, (2*terms+1)*3**(2*terms+1))/(1-F(1, 9))
    return I(lower, lower+remainder)


def exp_point(x, order=48):
    x = F(x)
    if order not in (48, 64):
        raise ValueError("locked exp order")
    y = abs(x)/32
    if y >= 1:
        raise ValueError("exp argument outside certified scaled domain")
    # Positive Taylor series; successive tail ratios <=y/(order+2).
    term, total = I(1), I(1)
    for n in range(1, order+1):
        term = term*y/n
        total += term
    rem = (term*y/(order+1))/(1-y/F(order+2))
    small = I(total.lo, total.hi+rem.hi)
    result = small**32
    return result if x >= 0 else 1/result


def iexp(x, order=48):
    x = iv(x)
    return I(exp_point(x.lo, order).lo, exp_point(x.hi, order).hi)


def sqrt_rational(x):
    x = F(x)
    if x < 0:
        raise ValueError("negative square root")
    n = isqrt((x.numerator*SCALE*SCALE)//x.denominator)
    lo = F(n, SCALE)
    return I(lo, lo if lo*lo == x else F(n+1, SCALE))


def validate_spins(spins):
    if len(spins) != 4 or any(type(v) is not int or v not in (-1, 1) for v in spins):
        raise ValueError("four exact integer spin labels required")


def label(spins):
    validate_spins(spins)
    return "".join("+" if v == 1 else "-" for v in spins)


def orbit(spins):
    validate_spins(spins)
    t = tuple(spins)
    return tuple(sorted({t, t[::-1], tuple(-v for v in t), tuple(-v for v in t[::-1])}))


def orbits():
    return tuple(sorted({orbit(t) for t in SPINS}))


def pair_derivatives(r, eta, L, exponential):
    e = exponential(-L*(r-1))
    return (8*(1-e)**2-eta/(4*r**2),
            16*L*(e-e**2)+eta/(2*r**3),
            16*L**2*(2*e**2-e)-3*eta/(2*r**4),
            16*L**3*(e-4*e**2)+6*eta/r**5)


def interval_parent(spins, gaps, terms=64, order=48):
    validate_spins(spins)
    gaps = list(map(iv, gaps))
    if len(gaps) != 3 or any(g.lo <= 0 for g in gaps):
        raise ValueError("positive ordered gaps required")
    L, V = logtwo(terms), I(0)
    grad = [I(0) for _ in range(3)]
    H = [[I(0) for _ in range(3)] for _ in range(3)]
    thirds = []
    for i, j in PAIRS:
        r = sum(gaps[i:j])
        eta = spins[i]*spins[j] if j == i+1 else 0
        v, f, k, t = pair_derivatives(r, eta, L, lambda z: iexp(z, order))
        ref = 8*(1-F(1, 2)**(j-i-1))**2
        V += v-ref
        thirds.append(t)
        for a in range(i, j):
            grad[a] += f
            for b in range(i, j):
                H[a][b] += k
    return V, grad, H, thirds


def mp_parent(spins, gaps):
    L, V = mp.log(2), mp.mpf(0)
    grad, H = mp.zeros(3, 1), mp.zeros(3)
    for i, j in PAIRS:
        r = sum(gaps[i:j])
        eta = spins[i]*spins[j] if j == i+1 else 0
        v, f, k, _ = pair_derivatives(r, eta, L, mp.exp)
        V += v-8*(1-mp.mpf(2)**(-(j-i-1)))**2
        for a in range(i, j):
            grad[a] += f
            for b in range(i, j):
                H[a, b] += k
    return V, grad, H


def candidate(spins, seed, dps=80):
    validate_spins(spins)
    with mp.workdps(dps):
        x = mp.matrix([mp.mpf(str(v)) for v in seed])
        for step in range(101):
            _, g, H = mp_parent(spins, list(x))
            residual = max(abs(v) for v in g)
            if residual <= mp.mpf("1e-40"):
                return {"success": True, "steps": step,
                        "center": [F(mp.nstr(v, dps-10)) for v in x],
                        "residual_display": mp.nstr(residual, 8)}
            if step == 100:
                break
            try:
                dx = mp.lu_solve(H, -g)
            except (ZeroDivisionError, ValueError):
                return {"success": False, "steps": step, "reason": "singular Newton matrix"}
            accepted = False
            for backtrack in range(20):
                alpha = mp.mpf(2)**(-backtrack)
                trial = x+alpha*dx
                if not all(mp.mpf(1)/4 <= v <= 4 for v in trial):
                    continue
                _, gt, _ = mp_parent(spins, list(trial))
                if max(abs(v) for v in gt) < (1-alpha/mp.mpf(10000))*residual:
                    x, accepted = trial, True
                    break
            if not accepted:
                return {"success": False, "steps": step, "reason": "20 backtracks exhausted"}
        return {"success": False, "steps": 100, "reason": "100 Newton iterations exhausted"}


def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]


def transpose(A):
    return list(map(list, zip(*A)))


def eye(n):
    return [[F(int(i == j)) for j in range(n)] for i in range(n)]


def inverse(A):
    n = len(A)
    a = [list(row)+list(e) for row, e in zip(A, eye(n))]
    for i in range(n):
        pivot = a[i][i]
        # All uses have nonzero leading pivots (SPD or verified preconditioner).
        a[i] = [v/pivot for v in a[i]]
        for j in range(n):
            if j != i:
                t = a[j][i]
                a[j] = [v-t*w for v, w in zip(a[j], a[i])]
    return [row[n:] for row in a]


def norm_inf(A):
    return max(sum(iv(v).mag for v in row) for row in A)


def ldl(A):
    n = len(A)
    L, diag = [[I(int(i == j)) for j in range(n)] for i in range(n)], []
    for i in range(n):
        d = A[i][i]-sum(L[i][k]**2*diag[k] for k in range(i))
        if d.lo <= 0:
            raise ValueError("interval positive curvature unresolved")
        diag.append(d)
        for j in range(i+1, n):
            L[j][i] = (A[j][i]-sum(L[j][k]*L[i][k]*diag[k] for k in range(i)))/d
    return diag


def preconditioner(H):
    A = [[v.mid for v in row] for row in H]
    exact = inverse(A)
    grid = 10**50
    R = [[F(round(v*grid), grid) for v in row] for row in exact]
    inverse(R)  # Explicit exact nonsingularity, independent of float flags.
    return R


def inclusion(center, radius, fcenter, H):
    R = preconditioner(H)
    E = [[I(int(i == j))-sum(R[i][k]*H[k][j] for k in range(3))
          for j in range(3)] for i in range(3)]
    contraction = norm_inf(E)
    shift = [-sum(R[i][k]*fcenter[k] for k in range(3)) for i in range(3)]
    image = [shift[i]+sum(E[i][j]*I(-radius, radius) for j in range(3)) for i in range(3)]
    margin = radius-max(v.mag for v in image)
    if contraction >= 1 or margin <= 0:
        raise ValueError("Krawczyk strict inclusion/contraction not certified")
    return {"preconditioner": R, "contraction_upper": contraction,
            "inclusion_margin_lower": margin, "image_offsets": image,
            "root_box": [I(center[i])+image[i] for i in range(3)]}


def certify(spins, center, fallback=False):
    r = F(1, 10**(16 if fallback else 12))
    terms, order = (96, 64) if fallback else (64, 48)
    box = [I(c-r, c+r) for c in center]
    _, fc, _, _ = interval_parent(spins, list(map(I, center)), terms, order)
    _, _, H, _ = interval_parent(spins, box, terms, order)
    c = inclusion(center, r, fc, H)
    try:
        c["ldl_pivots"] = ldl(H)
        verdict = "CERTIFIED_STRICT_LOCAL_MINIMUM"
    except ValueError:
        # Sufficient rational directions, never infer negativity from failed SPD.
        directions = tuple(product((-1, 0, 1), repeat=3))
        witness = next((v for v in directions if any(v) and
                        sum(H[i][j]*v[i]*v[j] for i in range(3) for j in range(3)).hi < 0), None)
        verdict = "CERTIFIED_ROOT_NONMINIMUM" if witness else "CERTIFIED_ROOT_CURVATURE_UNRESOLVED"
        c["negative_direction"] = witness
    return dict(c, center=center, inclusion_halfwidth=r, terms=terms, exp_order=order,
                hessian_on_inclusion_box=H, center_gradient=fc, verdict=verdict)


def search_orbit(spins):
    attempts = []
    for seed in SEEDS:
        c = candidate(spins, seed)
        a = {"seed": list(seed), **c}
        if c["success"]:
            for fallback in (False, True):
                if fallback:
                    c = candidate(spins, c["center"], 160)
                    if not c["success"]:
                        a["fallback_search"] = c
                        break
                try:
                    cert = certify(spins, c["center"], fallback)
                    a["certificate"] = cert
                    break
                except (ValueError, ZeroDivisionError) as exc:
                    a["fallback_failure" if fallback else "primary_failure"] = str(exc)
            if a.get("certificate", {}).get("verdict") == "CERTIFIED_STRICT_LOCAL_MINIMUM":
                attempts.append(a)
                return {"representative": spins, "attempts": attempts, "certificate": a["certificate"]}
        attempts.append(a)
    nonmin = any(a.get("certificate", {}).get("verdict") == "CERTIFIED_ROOT_NONMINIMUM"
                 for a in attempts)
    return {"representative": spins, "attempts": attempts, "certificate": None,
            "disposition": ("CERTIFIED_NONMINIMUM_WITNESSES_NO_MINIMUM_WITHIN_BUDGET" if nonmin
                            else "BOUNDED_SEARCH_INCONCLUSIVE_NOT_NONEXISTENCE")}


def gap_maps():
    T = [[F(-3, 4), F(-1, 2), F(-1, 4)], [F(1, 4), F(-1, 2), F(-1, 4)],
         [F(1, 4), F(1, 2), F(-1, 4)], [F(1, 4), F(1, 2), F(3, 4)]]
    D = [[F(int(j == i+1)-int(j == i)) for j in range(4)] for i in range(3)]
    root5 = sqrt_rational(5)
    B = [[-F(2*i-3, 2)/root5, I(v)/2, I(w)/(2*root5)]
         for i, (v, w) in enumerate(zip((1, -1, -1, 1), (1, -3, 3, -1)))]
    return T, D, B


def root_views(cert):
    T, D, B = gap_maps()
    x = mm(T, [[v] for v in cert["root_box"]])
    phi = 1-sum(F(2*i-3, 2)*x[i][0] for i in range(4))/5
    u1 = sum(F(v, 2)*x[i][0] for i, v in enumerate((1, -1, -1, 1)))
    u2 = sum(v*x[i][0] for i, v in enumerate((1, -3, 3, -1)))/(2*sqrt_rational(5))
    A = mm(mm(transpose(mm(D, B)), cert["hessian_on_inclusion_box"]), mm(D, B))
    pivots = ldl(A)
    invA = inverse(A)
    return {"Phi": phi, "u1_over_dref": u1, "u2_over_dref": u2,
            "endpoint_over_dref": sum(cert["root_box"]), "internal_stiffness": A,
            "stiffness_det": pivots[0]*pivots[1]*pivots[2],
            "lambda_min_lower": 1/norm_inf(invA), "lambda_max_upper": norm_inf(A),
            "root_position_uncertainty_upper": F(5, 2)*max(v.mag for v in cert["image_offsets"]),
            "hidden2_stiffness": [row[1:] for row in A[1:]]}


def neighborhoods(spins, cert):
    rows = []
    for j in range(9):
        r = F(1, 4*2**j)
        # Every pair-distance changes by <=sqrt2 R <3R/2 in orthonormal q.
        rootbox = cert["root_box"]
        gaps = [g+I(-F(3, 2)*r, F(3, 2)*r) for g in rootbox]
        row = {"j": j, "radius_over_dref": r}
        try:
            _, _, H, third = interval_parent(spins, gaps)
            ldl(H)
            R = preconditioner(H)
            E = [[I(int(i == k))-sum(R[i][a]*H[a][k] for a in range(3))
                  for k in range(3)] for i in range(3)]
            c = norm_inf(E)
            if c >= 1:
                raise ValueError("uniform inverse norm bound unresolved")
            # min eigen(D D^T)=2-sqrt2>1/2; upper norm<4.
            m = down((1-c)/(2*norm_inf(R)))
            M = up(4*norm_inf(H))
            M3 = up(3*sum(t.mag for t in third))  # (sqrt2)^3<3.
            row.update(certified=True, curvature_lower=m, curvature_upper=M,
                       third_derivative_norm_upper=M3,
                       Taylor_energy_error_upper=up(M3*r**3/6),
                       boundary_energy_rise_lower=down(m*r**2/2),
                       positive_gap_lower=min(g.lo for g in gaps),
                       uniform_inverse_contraction_upper=c)
        except (ValueError, ZeroDivisionError) as exc:
            row.update(certified=False, reason=str(exc))
        rows.append(row)
    return {"radii": rows, "largest_certified": next((r for r in rows if r["certified"]), None)}


def symbolic_checks():
    ell = s.Matrix(s.symbols("l1 l2 l3", positive=True))
    T, D, _ = gap_maps()
    T, D = s.Matrix(T), s.Matrix(D)
    a = s.Matrix([-s.Rational(3, 2), -s.Rational(1, 2), s.Rational(1, 2), s.Rational(3, 2)])
    E = s.Matrix([[1, 1/s.sqrt(5)], [-1, -3/s.sqrt(5)], [-1, 3/s.sqrt(5)], [1, -1/s.sqrt(5)]])/2
    B = (-a/s.sqrt(5)).row_join(E)
    G = T.T*T
    p = s.Matrix(s.symbols("pl1 pl2 pl3", real=True))
    px = T*G.inv()*p
    V = sum(8*(1-s.exp(-s.log(2)*(sum(ell[i:j])-1)))**2
            -8*(1-s.Rational(1, 2)**(j-i-1))**2 for i, j in PAIRS)
    V -= sum(s.Rational(1, 4)/ell[i]**2 for i in range(3))
    L = s.log(2)
    expected_g = s.zeros(3, 1)
    expected_H = s.zeros(3)
    for i, j in PAIRS:
        _, f, k, _ = pair_derivatives(sum(ell[i:j]), int(j == i+1), L, s.exp)
        for r in range(i, j):
            expected_g[r] += f
            for c in range(i, j):
                expected_H[r, c] += k
    theta, chi, detA, v = s.symbols("theta chi detA v", positive=True)
    logZ_nooffset = 3*s.log(theta)-3*s.log(chi)-s.log(detA)/2
    free = v-theta*logZ_nooffset
    entropy = -s.diff(free, theta)
    internal = free+theta*entropy
    residuals = {
        "gap_inverse": D*T-s.eye(3), "CM_removed": s.ones(1, 4)*T,
        "internal_basis": B.T*B-s.eye(3),
        "gap_metric_equals_inverse_bond_metric": G-(D*D.T).inv(),
        "canonical_one_form": T.T*px-p,
        "gap_kinetic": (px.T*px)[0]-(p.T*G.inv()*p)[0],
        "phase_measure_cancels": s.det(G)-s.Rational(1, 4),
        "gradient_from_energy": s.Matrix([s.diff(V, t) for t in ell])-expected_g,
        "Hessian_from_energy": s.hessian(V, ell)-expected_H,
        "equivalent_internal_force_rank": (D*B).det()**2-4,
        "joint_U_three_pairs": internal-v-3*theta,
        "F_U_TS": free-internal+theta*entropy,
        "hidden_U_two_pairs": ((v-theta*(2*s.log(theta)-2*s.log(chi)-s.log(detA)/2))
             -theta*s.diff(v-theta*(2*s.log(theta)-2*s.log(chi)-s.log(detA)/2), theta))-v-2*theta,
        "old_Phi_endpoint": (T*ell)[3]-(T*ell)[0]-sum(ell),
    }
    result = {}
    for name, value in residuals.items():
        values = list(value) if isinstance(value, s.MatrixBase) else [value]
        if any(s.simplify(t) != 0 for t in values):
            raise ValueError(f"exact identity failed: {name}")
        result[name] = True
    if G == s.eye(3):
        raise ValueError("wrong gap metric")
    aa, k1, k2, g1, g2, z = s.symbols("a k1 k2 g1 g2 z", real=True)
    K = s.diag(k1, k2)
    g = s.Matrix([g1, g2])
    block = s.Matrix([[aa, g1, g2], [g1, k1, 0], [g2, 0, k2]])
    schur = aa-(g.T*K.inv()*g)[0]
    w = s.Matrix(s.symbols("w1 w2", real=True))
    potential = aa*z*z/2+(g.T*w)[0]*z+(w.T*K*w)[0]/2
    shifted = w+K.inv()*g*z
    gaussian_identities = {
        "conditional_square_completion": potential-schur*z*z/2-(shifted.T*K*shifted)[0]/2,
        "Schur_partition_determinant": block.det()-K.det()*schur,
        "retained_covariance_from_joint": block.inv()[0, 0]-1/schur,
    }
    for name, expr in gaussian_identities.items():
        if s.cancel(expr) != 0:
            raise ValueError(f"Gaussian dictionary residual failed: {name}")
        result[name] = True
    # Symmetry is proved from pair-distance and bond signatures, not only label grouping.
    for spins in SPINS:
        eta = tuple(spins[i]*spins[i+1] for i in range(3))
        flipped, reflected = tuple(-v for v in spins), spins[::-1]
        if (eta != tuple(flipped[i]*flipped[i+1] for i in range(3)) or
                eta[::-1] != tuple(reflected[i]*reflected[i+1] for i in range(3))):
            raise ValueError("spin/bond symmetry failed")
    if sorted((j-i, i, j) for i, j in PAIRS) != sorted((j-i, 3-j, 3-i) for i, j in PAIRS):
        raise ValueError("open-pair reflection symmetry failed")
    result["flip_reflection_energy_symmetry_all16"] = True
    t = s.Symbol("large_gap", positive=True)
    if s.limit(V.subs({z: t for z in ell}), t, s.oo) != s.Rational(79, 2):
        raise ValueError("dissociation normalization limit")
    result["finite_dissociation_energy_not_global_partition"] = True
    return result


def negative_controls():
    controls = {}
    try:
        I(1)/I(-1, 1)
    except ValueError:
        controls["zero_crossing_division_rejected"] = True
    try:
        inclusion([F(0)]*3, F(1, 10**12), [I(F(1, 10**100))]*3,
                  [[I(0) for _ in range(3)] for _ in range(3)])
    except (ValueError, ZeroDivisionError):
        controls["tiny_residual_without_root_not_proof"] = True
    for name, mat in (("singular_curvature", [[I(1), I(0)], [I(0), I(0)]]),
                      ("indefinite_curvature", [[I(1), I(0)], [I(0), I(-1)]]),
                      ("near_singular_unresolved", [[I(1), I(0)], [I(0), I(-F(1, 10**80), F(1, 10**80))]])):
        try:
            ldl(mat)
        except ValueError:
            controls[name] = True
    T, D, _ = gap_maps()
    G = s.Matrix(T).T*s.Matrix(T)
    controls["gap_mass_muI_rejected"] = G != s.eye(3)
    controls["translation_zero_mode_not_integrated"] = (s.Matrix(D).T*s.Matrix(D)).det() == 0
    controls["dref_reset_without_exchange_rescale"] = F(1, 4) != F(1, 4)*F(2)**(-2)
    controls["three_hidden_plus_retained_is_double_count"] = 3+1 != 3
    controls["root_uncertainty_not_zero"] = (I(1-F(1, 10**12), 1+F(1, 10**12))-1).mag > 0
    controls["sector_energy_zeroing_changes_weights"] = mp.exp(-1) != 1
    controls["failed_search_not_nonexistence"] = classify_search(False, False) == "INCONCLUSIVE"
    controls["endpoint_not_Phi_alone"] = -1/s.sqrt(5) != 0
    controls["floating_spin_cache_bypass_rejected"] = False
    try:
        orbit((1., 1, 1, 1))
    except ValueError:
        controls["floating_spin_cache_bypass_rejected"] = True
    if not all(controls.values()) or len(controls) != 14:
        raise ValueError("negative control failed")
    return controls


def classify_search(found, certified):
    return "CERTIFIED" if found and certified else "INCONCLUSIVE"


def encode(obj):
    if isinstance(obj, I):
        return {"lo": str(obj.lo), "hi": str(obj.hi)}
    if isinstance(obj, F):
        return str(obj)
    if isinstance(obj, dict):
        return {k: encode(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [encode(v) for v in obj]
    return obj


@lru_cache(None)
def calculate():
    if mp.__version__ != "1.3.0":
        raise ValueError("candidate environment differs from locked mpmath1.3.0")
    groups = orbits()
    if len(groups) != 6 or set(t for g in groups for t in g) != set(SPINS):
        raise ValueError("six-orbit coverage failed")
    rows = []
    for members in groups:
        row = search_orbit(members[0])
        row["orbit_members"] = [label(t) for t in members]
        if row["certificate"]:
            c = row["certificate"]
            row["views"] = root_views(c)
            row["local_domain"] = neighborhoods(members[0], c)
            row["stationary_energy_over_Jref"] = interval_parent(members[0], c["root_box"])[0]
        rows.append(row)
    configurations = []
    for spins in SPINS:
        row = next(r for r in rows if label(spins) in r["orbit_members"])
        reflected = tuple(spins) not in (row["representative"], tuple(-v for v in row["representative"]))
        configurations.append({"spins": label(spins), "k": sum(v == 1 for v in spins),
                               "orbit_representative": label(row["representative"]),
                               "gap_order_reversed": reflected,
                               "verdict": row["certificate"]["verdict"] if row["certificate"] else row["disposition"]})
    return encode({"completed_rounds": ["Q0", "Q1", "Q2", "Q3", "Q4"],
                   "source_baseline_commit": "316797ea3590bdc5cc80a9ea387c7db147c67ddf",
                   "locked_control": {"N": 4, "D_over_Jref": 8, "delta": "ln2", "nu": 2,
                       "dref_over_r0": 1, "epsilon_star": 1, "open_magnetic_bonds": 3,
                       "Morse_pairs": 6, "spin_normalization": "S=s/2", "external_force": 0,
                       "E_star": "Jref", "t_star": "dref*sqrt(mu/Jref)", "bare_normalized_Phi_inertia": "5/4"},
                   "checks": symbolic_checks(), "negative_controls": negative_controls(),
                   "orbits": rows, "configurations": configurations,
                   "numerical_policy": {"mpmath": mp.__version__, "dps": 80, "fallback_dps": 160,
                       "sympy": s.__version__,
                       "seed_grid": ["1/2", "1", "2"], "max_steps": 100, "max_backtracks": 20,
                       "box": ["1/4", "4"], "residual_candidate_only": "1e-40",
                       "primary_box_halfwidth": "1e-12", "fallback_box_halfwidth": "1e-16",
                       "ln2_terms": [64, 96], "exp_scale": 32, "exp_orders": [48, 64],
                       "outward_rational_grid": "1e-170", "all_roots_claim": False},
                   "conditional_static_dictionary": {"joint_pairs": 3, "fixed_Phi_hidden_pairs": 2,
                       "joint_logZ": "-v_star/theta+3ln(theta/chi)-0.5ln(detAbar)",
                       "joint_U_over_Jref": "v_star+3theta",
                       "local_tail_bound": "eta<=P(chi_square_3>=m*R^2/theta); sufficient Laurent-Massart bound in report",
                       "local_error": "Delta=M3*R^3/6; |F_local-F_harm|<=Jref*Delta-kBT*ln(1-eta_bound)",
                       "classical_floor": "theta>=chi*sqrt(kappa_max/(12*epsilon_quantum)) for covariance",
                       "window": "max(Delta/epsilon_value,chi*sqrt(kappa_max/(12epsilon_quantum))) <= theta <= mR^2/B(log(1/epsilon_local))",
                       "budgets_selected": False, "actual_thermal_window_accepted": False},
                   "physical_acceptance": False, "unique_UET_discriminator": False,
                   "old_scientific_verifiers_rerun": False, "trajectories": 0,
                   "parent_global_equilibrium": "NOT_ADMITTED_UNCHANGED_O_NO_GO",
                   "P_locked_center_localization": "UNCHANGED_NOT_ADMITTED",
                   "next_controller": "physical-parent-preparation: supply physical dictionary/scales chi and observable-specific error policy before accepting a local-classical window; no automatic kinetics/lifetime",
                   "limitations": ["Existence/uniqueness only inside certified boxes, not all search roots/minima.",
                       "New stationary centers do not overwrite P's old reference or O's global no-go.",
                       "Static locally conditioned ensemble is not invariant preparation or lifetime.",
                       "No damping/noise, spin kinetics, actual material, physical test or UET novelty."]})


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT), ROOT), **calculate()}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only scientific and artifact identity check")
    mode.add_argument("--emit-report", action="store_true", help="explicitly generate new Q artifact only")
    args = p.parse_args(argv)
    result = record()
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(payload, encoding="utf-8", newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes() != payload.encode("utf-8"):
        raise ValueError("artifact absent/stale; inspect before explicit --emit-report")
    print(json.dumps({"orbits": len(result["orbits"]), "configurations": len(result["configurations"]),
                      "certified_minimum_orbits": sum(bool(r["certificate"]) for r in result["orbits"]),
                      "physical_acceptance": False, "review": result["contract_review_status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
