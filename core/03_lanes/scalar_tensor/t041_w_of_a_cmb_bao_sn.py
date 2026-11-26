"""Test Card T041 prediction method: the parent action's thawing dark energy against Planck 2018 distance priors plus
DESI DR2 BAO and Pantheon+ (option B of T040; topic 0.3).

Models (flat; matter, radiation r = omega_r / omega_m and the dark sector; background from uet_frw_cmb.py, wave C2):
    LCDM   free: Omega_m, omega_b, omega_m
    CPL    w = w0 + wa (1 - a)                          free: Omega_m, w0, wa, omega_b, omega_m
    UET    thawing psi released at rest at z = 1e6       free: Lambda_eff (sets Omega_m), omega_b, omega_m, on the
           grid of T040 in xi_c, psi_i and m/H0 (m/H0 measured with the H0 of Omega_m = 0.30); each point must pass
           Cassini, LLR and T001 today.
CMB: chi2 = (x - d)^T C^-1 (x - d) for x = (R, l_A, omega_b) of Chen, Huang & Wang (2019), base LambdaCDM block,
Planck 2018 TT,TE,EE+lowE; n_s row and column dropped (marginalised); asymmetric errors symmetrised as the mean of
the two sides (AI choice); C_ij = rho_ij sigma_i sigma_j. Model values as the paper prescribes:
    R = sqrt(Omega_m) H0 D_M(z*) / c,  l_A = pi D_M(z*) / r_s(z*),  z* from the Hu & Sugiyama fit.
BAO and SN exactly as in T040 (amplitude c/(H0 r_d) and SN offset profiled analytically; zHD > 0.01).
Decision (fixed in docs/standard/tests/T041.json): dchi2_CPL = chi2_min(UET) - chi2_min(CPL) on BAO + SN + CMB;
    PASS if dchi2_CPL <= 4, FAIL if dchi2_CPL > 9, INCONCLUSIVE otherwise.
Reported, not deciding: dchi2_LCDM = chi2_min(LCDM) - chi2_min(UET), the UET best point and its CPL (w0, wa),
and the CMB part of each chi2.

Do not run against the data before the card is APPROVED by the author. The script checks that, and the sha256 of every
data file against docs/standard/data_manifest.json, before it reads any value.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CARD = ROOT / "docs/standard/tests/T041.json"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CMB_ID = "CHEN2019_DISTANCE_PRIORS_TEX"
DATA = {
    CMB_ID: "docs/data/external/cosmology/cmb_priors/chen2019/private/distance-priors-2018.tex",
    "DESI_DR2_BAO_MEAN": "docs/data/external/cosmology/bao_sn/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt",
    "DESI_DR2_BAO_COV": "docs/data/external/cosmology/bao_sn/desi_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt",
    "PANTHEON_PLUS_HD": "docs/data/external/cosmology/bao_sn/pantheon_plus/Pantheon+SH0ES.dat",
    "PANTHEON_PLUS_COV": "docs/data/external/cosmology/bao_sn/pantheon_plus/Pantheon+SH0ES_STAT+SYS.cov",
}
PASS_MAX, FAIL_MIN = 4.0, 9.0
GRID_XI = (0.0, -0.01, -0.003, 0.003, 0.01, 0.02, 0.03, 0.05)
GRID_PSI = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2)
GRID_M = (0.5, 1.0, 2.0, 3.0, 4.0)
STEPS = 1500
H0_REF = 1.0 / math.sqrt(3.0 * 0.30)

cmbm = importlib.import_module("core.03_lanes.scalar_tensor.uet_frw_cmb")
t040 = importlib.import_module("core.03_lanes.scalar_tensor.t040_w_of_a_bao_sn")
Z_NODES = t040.Z_NODES


def _approved() -> bool:
    card = json.loads(CARD.read_text(encoding="utf-8"))
    return card.get("status") == "APPROVED" and card.get("approval", {}).get("role") == "AUTHOR"


def _check_hashes() -> None:
    manifest = {e["data_id"]: e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]}
    for data_id, rel in DATA.items():
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        if manifest[data_id]["sha256"] != digest or manifest[data_id]["path"] != rel:
            raise RuntimeError(f"{data_id}: file does not match the manifest")


_NUM = r"-?\d+(?:\.\d+)?"


def _cell_value(cell: str) -> tuple[float, float]:
    """'$a\\pm b$' -> (a, b); '$a^{+p}_{-m}$' -> (a, (p + m) / 2)."""
    c = cell.replace(" ", "")
    m = re.fullmatch(rf"\$({_NUM})\\pm({_NUM})\$", c)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.fullmatch(rf"\$({_NUM})\^\{{\+({_NUM})\}}_\{{-({_NUM})\}}\$", c)
    if m:
        return float(m.group(1)), 0.5 * (float(m.group(2)) + float(m.group(3)))
    raise ValueError(f"cannot read the value cell {cell!r}")


def parse_priors(tex: str) -> tuple[np.ndarray, np.ndarray]:
    """Mean and covariance of (R, l_A, omega_b) from the base LambdaCDM block of the distance-prior table."""
    start = tex.index(r"\begin{tabular}{cccccc}")
    block = tex[start:].split(r"\hline\hline")[1]   # first model block: base LambdaCDM
    head, body = block.split(r"\hline", 1)
    if r"$\Lambda$CDM &" not in head or "Omega_k" in head or "A_" in head:
        raise ValueError("first block is not the base LambdaCDM block")
    rows = [r.strip() for r in body.split(r"\\") if r.strip()]
    keys = [r"$R$", r"$l_\textrm{A}$", r"$\Omega_b h^2$"]
    mean, sig, corr = [], [], []
    for key, row in zip(keys, rows[:3]):
        cells = [c.strip() for c in row.split("&")]
        if cells[0] != key:
            raise ValueError(f"row label {cells[0]!r}, expected {key!r}")
        v, s = _cell_value(cells[1])
        mean.append(v)
        sig.append(s)
        corr.append([float(c.strip("$")) for c in cells[2:5]])
    rho = np.array(corr)
    if not np.allclose(rho, rho.T, atol=1e-12) or not np.allclose(np.diag(rho), 1.0):
        raise ValueError("correlation block is not a symmetric matrix with unit diagonal")
    s = np.array(sig)
    return np.array(mean), rho * np.outer(s, s)


def load():
    data = t040.load()
    mean, cov = parse_priors((ROOT / DATA[CMB_ID]).read_text(encoding="utf-8"))
    data["cmb"] = (mean, np.linalg.inv(cov))
    return data


# ---- analytic-E models (LCDM, CPL) with radiation -------------------------------------------------------------

_X, _WG = np.polynomial.legendre.leggauss(2000)


def _de_cpl(a, w0, wa):
    return a ** (-3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - a))


def _analytic(Om, w0, wa, omega_b, omega_m):
    """E(z) on Z_NODES and (R, l_A) for a flat model with E^2 = Om a^-3 + Or a^-4 + (1 - Om - Or) f_DE(a)."""
    Or = Om * cmbm.r_ratio(omega_m)

    def E(a):
        return np.sqrt(Om * a**-3 + Or * a**-4 + (1.0 - Om - Or) * _de_cpl(a, w0, wa))

    a_s = 1.0 / (1.0 + cmbm.z_star(omega_b, omega_m))
    u = 0.5 * math.log(a_s) * (1.0 - _X)
    au = np.exp(u)
    D = float(0.5 * -math.log(a_s) * np.sum(_WG / (au * E(au))))         # H0 D_M / c
    aa = 0.5 * a_s * (_X + 1.0)
    cs = 1.0 / np.sqrt(3.0 * (1.0 + 0.75 * omega_b / cmbm.OMEGA_GAMMA * aa))
    rs = float(0.5 * a_s * np.sum(_WG * cs / (aa * aa * E(aa))))          # H0 r_s / c
    return E(1.0 / (1.0 + Z_NODES)), math.sqrt(Om) * D, math.pi * D / rs


def _uet(lam_eff, omega_b, omega_m, psi_i, m_h, xi):
    """E(z) on Z_NODES and (R, l_A), or None if the point fails the bounds today or the run breaks down."""
    r = cmbm.r_ratio(omega_m)
    md = cmbm.Model(lam_eff, (m_h * H0_REF) ** 2, 0.0, xi, r)
    try:
        rn = cmbm.run(md, psi_i, steps=STEPS)
        if not np.all(np.isfinite(rn.H)):
            return None
        F0, dF0 = float(md.F(rn.psi[-1])), float(md.dF(rn.psi[-1]))
        gamma_m1 = -dF0 * dF0 / (F0 + 2.0 * dF0 * dF0)
        gdot = -dF0 * float(rn.pi[-1]) / F0 / rn.H0
        lo, hi = (2.0, 2.4)
        if abs(gamma_m1) >= 2.3e-5 or abs(gdot) >= 2.2e-3 or lo <= xi <= hi:
            return None
        ang = cmbm.cmb_angle(md, rn, omega_b, omega_m)
    except (ValueError, OverflowError, ZeroDivisionError, IndexError):
        return None
    z = np.exp(-rn.N) - 1.0
    sel = z <= Z_NODES[-1] + 0.5
    E = np.interp(Z_NODES, z[sel][::-1], (rn.H[sel] / rn.H0)[::-1])
    return E, math.sqrt(rn.omega_m0) * rn.H0 * ang.D_M, math.pi / ang.theta_star, rn.omega_m0, m_h * H0_REF / rn.H0


def _chi2_all(data, E, R, lA, omega_b) -> tuple[float, float]:
    mean, icov = data["cmb"]
    d = np.array([R, lA, omega_b]) - mean
    c_cmb = float(d @ icov @ d)
    return t040.chi2(data, E) + c_cmb, c_cmb


def run() -> dict:
    if not _approved():
        raise RuntimeError("Test Card T041 is not APPROVED by the author: refusing to read the comparison data")
    _check_hashes()
    data = load()
    from scipy.optimize import minimize
    opts = {"xatol": 1e-7, "fatol": 1e-5, "maxiter": 3000}

    def f_lcdm(p):
        if not (0.05 < p[0] < 0.6 and 0.005 < p[1] < 0.05 and 0.05 < p[2] < 0.3):
            return 1e9
        E, R, lA = _analytic(p[0], -1.0, 0.0, p[1], p[2])
        return _chi2_all(data, E, R, lA, p[1])[0]

    lcdm = min((minimize(f_lcdm, s, method="Nelder-Mead", options=opts) for s in
                ((0.31, 0.0224, 0.142), (0.29, 0.0226, 0.140))), key=lambda r: r.fun)

    def f_cpl(p):
        if not (0.05 < p[0] < 0.6 and 0.005 < p[3] < 0.05 and 0.05 < p[4] < 0.3):
            return 1e9
        E, R, lA = _analytic(p[0], p[1], p[2], p[3], p[4])
        return _chi2_all(data, E, R, lA, p[3])[0]

    cpl = min((minimize(f_cpl, s, method="Nelder-Mead", options=opts) for s in
               ((0.31, -1.0, 0.0, 0.0224, 0.142), (0.31, -0.8, -0.6, 0.0224, 0.142),
                (0.33, -0.7, -1.0, 0.0223, 0.143), (0.30, -1.1, 0.3, 0.0224, 0.141))), key=lambda r: r.fun)

    om0 = float(lcdm.x[0])
    best = None
    for xi in GRID_XI:
        for psi_i in GRID_PSI:
            if 1.0 + xi * psi_i * psi_i <= 0.3:
                continue
            for m_h in GRID_M:
                def f(p, psi_i=psi_i, m_h=m_h, xi=xi):
                    if not (0.005 < p[1] < 0.05 and 0.05 < p[2] < 0.3):
                        return 1e9
                    out = _uet(p[0], p[1], p[2], psi_i, m_h, xi)
                    return 1e9 if out is None else _chi2_all(data, out[0], out[1], out[2], p[1])[0]
                start = ((1.0 - om0) / om0, float(lcdm.x[1]), float(lcdm.x[2]))
                res = minimize(f, start, method="Nelder-Mead",
                               options={"xatol": 1e-6, "fatol": 1e-4, "maxiter": 400})
                if res.fun < 1e8 and (best is None or res.fun < best[0]):
                    best = (float(res.fun), [float(v) for v in res.x], psi_i, m_h, xi)
    c_uet, p_uet, psi_u, m_u, xi_u = best
    out = _uet(p_uet[0], p_uet[1], p_uet[2], psi_u, m_u, xi_u)
    _, cmb_uet = _chi2_all(data, out[0], out[1], out[2], p_uet[1])
    # CPL summary of the UET best point (same C1 window 0.4 <= a <= 1)
    md = cmbm.Model(p_uet[0], (m_u * H0_REF) ** 2, 0.0, xi_u, cmbm.r_ratio(p_uet[2]))
    rn = cmbm.run(md, psi_u, steps=STEPS)
    sel = rn.N >= math.log(0.4)
    a = np.exp(rn.N[sel])
    F0 = float(md.F(rn.psi[-1]))
    Hdot, _ = cmbm.accelerations(md, rn.psi[sel], rn.pi[sel], a, rn.H[sel])
    rho_de = 3.0 * F0 * rn.H[sel] ** 2 - a**-3 - md.r * a**-4
    p_de = -2.0 * F0 * Hdot - a**-3 - 4.0 / 3.0 * md.r * a**-4 - rho_de
    (w0_u, wa_u), *_ = np.linalg.lstsq(np.column_stack([np.ones(sel.sum()), 1.0 - a]), p_de / rho_de, rcond=None)
    E_l, R_l, lA_l = _analytic(*lcdm.x[:1], -1.0, 0.0, *lcdm.x[1:])
    E_c, R_c, lA_c = _analytic(*cpl.x)
    d_cpl = c_uet - float(cpl.fun)
    outcome = "PASS" if d_cpl <= PASS_MAX else ("FAIL" if d_cpl > FAIL_MIN else "INCONCLUSIVE")
    return {"chi2_lcdm": float(lcdm.fun), "lcdm_best": [float(v) for v in lcdm.x],
            "chi2_cmb_lcdm": _chi2_all(data, E_l, R_l, lA_l, lcdm.x[1])[1],
            "chi2_cpl": float(cpl.fun), "cpl_best": [float(v) for v in cpl.x],
            "chi2_cmb_cpl": _chi2_all(data, E_c, R_c, lA_c, cpl.x[3])[1],
            "chi2_uet": c_uet, "chi2_cmb_uet": cmb_uet,
            "uet_best": {"lambda_eff": p_uet[0], "omega_b": p_uet[1], "omega_m": p_uet[2], "Omega_m": out[3],
                         "psi_i": psi_u, "m_over_H0_label": m_u, "m_over_H0_actual": out[4], "xi": xi_u,
                         "w0": float(w0_u), "wa": float(wa_u)},
            "dchi2_cpl": d_cpl, "dchi2_lcdm": float(lcdm.fun) - c_uet, "outcome": outcome,
            "n_bao": int(len(data["bao"][0])), "n_sn": int(len(data["sn"][0])), "n_cmb": 3}


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
