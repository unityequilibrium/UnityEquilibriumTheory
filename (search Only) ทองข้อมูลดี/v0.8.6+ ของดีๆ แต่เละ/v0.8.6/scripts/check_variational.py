#!/usr/bin/env python
from __future__ import annotations
import argparse
import numpy as np

from uet_core.parser import parse_case_params
from uet_core.energy import omega_C, omega_CI
from uet_core.variational import mu_C, mu_CI, inner_dx2

def fd_dir_deriv(fun, x, eta, eps=1e-6):
    return (fun(x + eps*eta) - fun(x - eps*eta)) / (2*eps)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["C_only","C_I"], required=True)
    ap.add_argument("--params", required=True, help="params string (same format as matrix)")
    ap.add_argument("--N", type=int, default=64)
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--eps", type=float, default=1e-6)
    ap.add_argument("--amp", type=float, default=0.3, help="random field amplitude")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    params = parse_case_params(args.model, args.params)

    N = args.N
    L = args.L
    eps = args.eps

    max_rel = 0.0
    max_abs = 0.0
    for k in range(args.trials):
        if args.model == "C_only":
            pot = params["pot"]
            kappa = float(params["kappa"])
            C = args.amp * rng.standard_normal((N, N))
            eta = rng.standard_normal((N, N))

            def E(Cx):
                return omega_C(Cx, pot, kappa, L)

            mu = mu_C(C, pot, kappa, L)
            fd = fd_dir_deriv(E, C, eta, eps=eps)
            ip = inner_dx2(mu, eta, L)

            abs_err = abs(fd - ip)
            rel_err = abs_err / max(1e-12, abs(fd), abs(ip))
        else:
            potC = params["potC"]; potI = params["potI"]
            beta = float(params["beta"])
            kC = float(params["kC"]); kI = float(params["kI"])
            C = args.amp * rng.standard_normal((N, N))
            I = args.amp * rng.standard_normal((N, N))
            etaC = rng.standard_normal((N, N))
            etaI = rng.standard_normal((N, N))

            def E_pair(Cx, Ix):
                return omega_CI(Cx, Ix, potC, potI, beta, kC, kI, L)

            fd = (E_pair(C + eps*etaC, I + eps*etaI) - E_pair(C - eps*etaC, I - eps*etaI)) / (2*eps)
            muC, muI = mu_CI(C, I, potC, potI, beta, kC, kI, L)
            ip = inner_dx2(muC, etaC, L) + inner_dx2(muI, etaI, L)

            abs_err = abs(fd - ip)
            rel_err = abs_err / max(1e-12, abs(fd), abs(ip))

        max_abs = max(max_abs, abs_err)
        max_rel = max(max_rel, rel_err)
        print(f"[trial {k+1}/{args.trials}] fd={fd:.6e} ip={ip:.6e} abs_err={abs_err:.3e} rel_err={rel_err:.3e}")

    ok = (max_rel < 5e-4) or (max_abs < 1e-6)
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}  max_rel={max_rel:.3e} max_abs={max_abs:.3e}")
    if not ok:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
