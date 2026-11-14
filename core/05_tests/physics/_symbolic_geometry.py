"""Independent sympy geometry and action helpers for physics tests.

Built from textbook definitions (Misner-Thorne-Wheeler conventions,
signature (-,+,+,+)). Nothing here imports the UET code under test, so the
derivation checks compare the implementation against an independent route.
"""

from __future__ import annotations

import sympy as sp

T, X, Y, ZC = sp.symbols("t x y z", real=True)
COORDS = (T, X, Y, ZC)


def christoffel(g: sp.Matrix, ginv: sp.Matrix, coords=COORDS):
    """Gamma^a_{bc} = 1/2 g^{ad}(d_b g_{dc} + d_c g_{db} - d_d g_{bc})."""
    n = len(coords)
    dg = [[[sp.diff(g[i, j], coords[k]) for k in range(n)] for j in range(n)] for i in range(n)]
    return [[[sum(ginv[a, d] * (dg[d][c][b] + dg[d][b][c] - dg[b][c][d]) for d in range(n) if ginv[a, d] != 0) / 2
              for c in range(n)] for b in range(n)] for a in range(n)]


def ricci_tensor(gamma, coords=COORDS) -> sp.Matrix:
    """R_{bd} = d_a G^a_{db} - d_d G^a_{ab} + G^a_{ae} G^e_{db} - G^a_{de} G^e_{ab}."""
    n = len(coords)
    ric = sp.zeros(n, n)
    for b in range(n):
        for d in range(n):
            ric[b, d] = sum(
                sp.diff(gamma[a][d][b], coords[a]) - sp.diff(gamma[a][a][b], coords[d])
                + sum(gamma[a][a][e] * gamma[e][d][b] - gamma[a][d][e] * gamma[e][a][b] for e in range(n))
                for a in range(n)
            )
    return ric


def block_inverse(g: sp.Matrix) -> sp.Matrix:
    """Inverse of a metric whose only off-diagonal entries are g[0,1] = g[1,0]."""
    det01 = g[0, 0] * g[1, 1] - g[0, 1] ** 2
    inv = sp.zeros(4, 4)
    inv[0, 0], inv[1, 1] = g[1, 1] / det01, g[0, 0] / det01
    inv[0, 1] = inv[1, 0] = -g[0, 1] / det01
    inv[2, 2], inv[3, 3] = 1 / g[2, 2], 1 / g[3, 3]
    return inv


def block_det(g: sp.Matrix):
    return (g[0, 0] * g[1, 1] - g[0, 1] ** 2) * g[2, 2] * g[3, 3]


def einstein_and_scalar(g: sp.Matrix, coords=COORDS):
    ginv = block_inverse(g)
    gamma = christoffel(g, ginv, coords)
    ric = ricci_tensor(gamma, coords)
    scalar = sum(ginv[a, b] * ric[a, b] for a in range(len(coords)) for b in range(len(coords)))
    return ric - g * scalar / 2, scalar, gamma, ginv


def covariant_hessian(f, gamma, coords=COORDS) -> sp.Matrix:
    """nabla_a nabla_b f = d_a d_b f - Gamma^c_{ab} d_c f."""
    n = len(coords)
    return sp.Matrix(n, n, lambda a, b: sp.diff(f, coords[a], coords[b])
                     - sum(gamma[c][a][b] * sp.diff(f, coords[c]) for c in range(n)))


def box(f, g: sp.Matrix, ginv: sp.Matrix, coords=COORDS):
    """box f = (1/sqrt(-g)) d_mu (sqrt(-g) g^{mu nu} d_nu f)."""
    root = sp.sqrt(-block_det(g))
    n = len(coords)
    return sum(sp.diff(root * sum(ginv[m, v] * sp.diff(f, coords[v]) for v in range(n)), coords[m])
               for m in range(n)) / root


def euler_lagrange_at(Ltilde, placeholders, concrete, coords, point, prec=40):
    """Euler-Lagrange expression of one field, evaluated at a point.

    ``placeholders`` = (f, (f_t, f_x, f_y, f_z)) symbols used in ``Ltilde``;
    ``concrete`` maps every placeholder of every field to an explicit expression
    in the coordinates. Returns dL/df - sum_mu d_mu (dL/d(d_mu f)).
    """
    value_sym, grad_syms = placeholders
    total = sp.diff(Ltilde, value_sym).xreplace(concrete).evalf(prec, subs=point)
    for mu, gs in enumerate(grad_syms):
        flux = sp.diff(Ltilde, gs).xreplace(concrete)
        total -= sp.diff(flux, coords[mu]).evalf(prec, subs=point)
    return total


def derivative_values(funcs: dict, var, at: float, max_order: int = 5) -> dict:
    """Map f(var) and its derivatives up to ``max_order`` to numbers at ``at``."""
    out = {}
    for f, expr in funcs.items():
        for order in range(max_order, 0, -1):
            out[sp.Derivative(f, (var, order))] = sp.Float(sp.diff(expr, var, order).subs(var, at), 50)
        out[f] = sp.Float(expr.subs(var, at), 50)
    return out


def parent_lagrangian_scalar(R, phi, grad_phi_sq, chi_sq, grad_chi_sq, p):
    """Theory Card UET-PARENT-ACTION-001 integrand (before sqrt(-g)), from the card text."""
    delta = phi - p["phi_star"]
    F = 1 + p["epsilon"] * p["xi"] * delta**2
    U = p["rho_star"] + p["mu2"] * delta**2 / 2 + p["lambda_phi"] * delta**4 / 4
    W = p["m2"] * chi_sq / 2 + p["lambda_chi"] * chi_sq**2 / 4
    return (F * (R - 2 * p["Lambda"]) / (2 * p["kappa"])
            - p["epsilon"] * (p["k"] * grad_phi_sq / 2 + U)
            - p["Z"] * grad_chi_sq / 2 - W
            + p["epsilon"] * p["h"] * delta * chi_sq / 2)
