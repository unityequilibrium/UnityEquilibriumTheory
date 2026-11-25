"""Test Card T040 prediction method: the parent action's dark-energy w(a) against DESI DR2 BAO and Pantheon+ (topic 0.3).

Models (flat, pressureless matter, radiation neglected at z < 2.5; see uet_frw_background.py):
    LCDM   w = -1                                     free: Omega_m
    UET    thawing psi of the parent action           free: Omega_m, psi_i, m/H0, xi_c on an AI grid; each point
                                                      must pass Cassini, LLR and T001 today (allowed_today)
    CPL    w = w0 + wa (1 - a)                        free: Omega_m, w0, wa
Nuisance, profiled analytically: A = c/(H0 r_d) for BAO (D_M/r_d, D_H/r_d and D_V/r_d are all linear in A), and the
SN offset (absolute magnitude plus H0) in mu = m_b_corr - M.
    chi2_BAO = (d - A t)^T C^-1 (d - A t) minimised over A;  chi2_SN = r^T C^-1 r - (1^T C^-1 r)^2 / (1^T C^-1 1),
    r = m_b_corr - 5 log10[(1 + z_hel) int_0^z_HD dz / E(z)].
Pantheon+ rows with zHD > 0.01 are used, with the matching block of the STAT+SYS covariance (AI choice, the usual
Pantheon+ cosmology cut).
Decision (fixed in docs/standard/tests/T040.json): dchi2_CPL = chi2_min(UET) - chi2_min(CPL);
    PASS if dchi2_CPL <= 4, FAIL if dchi2_CPL > 9, INCONCLUSIVE otherwise.
Reported, not deciding: dchi2_LCDM = chi2_min(LCDM) - chi2_min(UET) and the UET best-fit CPL (w0, wa).

Do not run against the data before the card is APPROVED by the author. The script checks that, and the sha256 of every
data file against docs/standard/data_manifest.json, before it reads any value.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CARD = ROOT / "docs/standard/tests/T040.json"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA = {
    "DESI_DR2_BAO_MEAN": "docs/data/external/cosmology/bao_sn/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt",
    "DESI_DR2_BAO_COV": "docs/data/external/cosmology/bao_sn/desi_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt",
    "PANTHEON_PLUS_HD": "docs/data/external/cosmology/bao_sn/pantheon_plus/Pantheon+SH0ES.dat",
    "PANTHEON_PLUS_COV": "docs/data/external/cosmology/bao_sn/pantheon_plus/Pantheon+SH0ES_STAT+SYS.cov",
}
Z_MIN_SN = 0.01
PASS_MAX, FAIL_MIN = 4.0, 9.0
GRID_XI = (0.0, -0.01, -0.003, 0.003, 0.01, 0.02, 0.03, 0.05)
GRID_PSI = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2)
GRID_M = (0.5, 1.0, 2.0, 3.0, 4.0)
OM_GRID = np.linspace(0.20, 0.42, 23)

frw = importlib.import_module("core.03_lanes.scalar_tensor.uet_frw_background")


def _approved() -> bool:
    card = json.loads(CARD.read_text(encoding="utf-8"))
    return card.get("status") == "APPROVED" and card.get("approval", {}).get("role") == "AUTHOR"


def _check_hashes() -> None:
    manifest = {e["data_id"]: e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]}
    for data_id, rel in DATA.items():
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        if manifest[data_id]["sha256"] != digest or manifest[data_id]["path"] != rel:
            raise RuntimeError(f"{data_id}: file does not match the manifest")


def load():
    rows = [l.split() for l in (ROOT / DATA["DESI_DR2_BAO_MEAN"]).read_text().splitlines()
            if l.strip() and not l.startswith("#")]
    bao_z = np.array([float(r[0]) for r in rows])
    bao_d = np.array([float(r[1]) for r in rows])
    bao_kind = [r[2] for r in rows]
    bao_cov = np.array((ROOT / DATA["DESI_DR2_BAO_COV"]).read_text().split(), float).reshape(len(rows), len(rows))
    lines = (ROOT / DATA["PANTHEON_PLUS_HD"]).read_text().splitlines()
    head = lines[0].split()
    tab = np.array([l.split() for l in lines[1:]])
    col = {name: i for i, name in enumerate(head)}
    z_hd = tab[:, col["zHD"]].astype(float)
    keep = z_hd > Z_MIN_SN
    tokens = (ROOT / DATA["PANTHEON_PLUS_COV"]).read_text().split()
    n = int(tokens[0])
    sn_cov = np.array(tokens[1:], float).reshape(n, n)[np.ix_(keep, keep)]
    return {"bao": (bao_z, bao_d, bao_kind, np.linalg.inv(bao_cov)),
            "sn": (z_hd[keep], tab[keep, col["zHEL"]].astype(float), tab[keep, col["m_b_corr"]].astype(float),
                   np.linalg.inv(sn_cov))}


def _comoving(z_nodes: np.ndarray, inv_e: np.ndarray, z: np.ndarray) -> np.ndarray:
    """int_0^z dz / E on a fine trapezoid grid."""
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (inv_e[1:] + inv_e[:-1]) * np.diff(z_nodes))])
    return np.interp(z, z_nodes, cum)


Z_NODES = np.linspace(0.0, 2.5, 2501)


def e_lcdm(om: float) -> np.ndarray:
    return np.sqrt(om * (1 + Z_NODES) ** 3 + 1 - om)


def e_cpl(om: float, w0: float, wa: float) -> np.ndarray:
    a = 1.0 / (1.0 + Z_NODES)
    de = a ** (-3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - a))
    return np.sqrt(om * (1 + Z_NODES) ** 3 + (1 - om) * de)


def e_uet(om: float, psi_i: float, m_h: float, xi: float):
    """E(z) of the parent action, or None if the point fails the bounds today."""
    if 1.0 + xi * psi_i * psi_i <= 0.3:
        return None
    try:
        bg, h = frw.calibrated(m_h, xi, psi_i, omega_m0=om, steps=1200)
        if not frw.allowed_today(h, xi):
            return None
        N, y = frw.integrate(bg, psi_i, steps=1200)
        H = frw.hubble(bg, y[:, 0], y[:, 1], np.exp(-3.0 * N))
    except (ValueError, OverflowError, ZeroDivisionError):
        return None
    if not np.all(np.isfinite(H)):
        return None
    z_model = np.exp(-N) - 1.0
    return np.interp(Z_NODES, z_model[::-1], (H / H[-1])[::-1])


def chi2(data, e_of_z: np.ndarray) -> float:
    inv_e = 1.0 / e_of_z
    bz, bd, kind, bic = data["bao"]
    dm = _comoving(Z_NODES, inv_e, bz)
    dh = np.interp(bz, Z_NODES, inv_e)
    t = np.array([dm[i] if k == "DM_over_rs" else dh[i] if k == "DH_over_rs" else (bz[i] * dm[i] ** 2 * dh[i]) ** (1 / 3)
                  for i, k in enumerate(kind)])
    amp = (t @ bic @ bd) / (t @ bic @ t)
    r_bao = bd - amp * t
    zhd, zhel, mb, sic = data["sn"]
    r = mb - 5.0 * np.log10((1.0 + zhel) * _comoving(Z_NODES, inv_e, zhd))
    one = np.ones_like(r)
    chi_sn = r @ sic @ r - (one @ sic @ r) ** 2 / (one @ sic @ one)
    return float(r_bao @ bic @ r_bao + chi_sn)


def _best_over_om(f) -> tuple[float, float]:
    vals = [(f(om), om) for om in OM_GRID]
    vals = [v for v in vals if v[0] is not None]
    c, om = min(vals)
    return c, om


def run() -> dict:
    if not _approved():
        raise RuntimeError("Test Card T040 is not APPROVED by the author: refusing to read the comparison data")
    _check_hashes()
    data = load()
    from scipy.optimize import minimize

    lcdm, om_l = _best_over_om(lambda om: chi2(data, e_lcdm(om)))
    best_cpl = None
    for start in ((0.3, -1.0, 0.0), (0.3, -0.8, -0.6), (0.33, -0.7, -1.0), (0.3, -1.1, 0.3)):
        res = minimize(lambda p: chi2(data, e_cpl(p[0], p[1], p[2])) if 0.05 < p[0] < 0.6 else 1e9, start,
                       method="Nelder-Mead", options={"xatol": 1e-5, "fatol": 1e-6, "maxiter": 4000})
        if best_cpl is None or res.fun < best_cpl.fun:
            best_cpl = res
    best_uet = (lcdm, om_l, 0.0, 0.0, 0.0)
    for xi in GRID_XI:
        for psi_i in GRID_PSI:
            for m_h in GRID_M:
                def f(om, psi_i=psi_i, m_h=m_h, xi=xi):
                    e = e_uet(om, psi_i, m_h, xi)
                    return None if e is None else chi2(data, e)
                vals = [(f(om), om) for om in OM_GRID]
                vals = [v for v in vals if v[0] is not None]
                if vals and min(vals)[0] < best_uet[0]:
                    c, om = min(vals)
                    best_uet = (c, om, psi_i, m_h, xi)
    c_uet, om_u, psi_u, m_u, xi_u = best_uet
    w0_u, wa_u = (-1.0, 0.0)
    if psi_u > 0:
        _, h = frw.calibrated(m_u, xi_u, psi_u, omega_m0=om_u, steps=1200)
        w0_u, wa_u = frw.cpl_fit(h)
    d_cpl = c_uet - float(best_cpl.fun)
    outcome = "PASS" if d_cpl <= PASS_MAX else ("FAIL" if d_cpl > FAIL_MIN else "INCONCLUSIVE")
    return {"chi2_lcdm": lcdm, "omega_m_lcdm": float(om_l),
            "chi2_cpl": float(best_cpl.fun), "cpl_best": [float(v) for v in best_cpl.x],
            "chi2_uet": c_uet, "uet_best": {"omega_m": float(om_u), "psi_i": psi_u, "m_over_H0": m_u, "xi": xi_u,
                                            "w0": w0_u, "wa": wa_u},
            "dchi2_cpl": d_cpl, "dchi2_lcdm": lcdm - c_uet, "outcome": outcome,
            "n_bao": int(len(data["bao"][0])), "n_sn": int(len(data["sn"][0]))}


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
