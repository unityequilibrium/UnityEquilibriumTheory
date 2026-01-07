# scripts/make_cross_matrices_ci.py
from __future__ import annotations
from pathlib import Path
import re
import pandas as pd

COLS = ["case_id","tier","model","dim","bc","integrator","grid","dt","T","seed","max_steps","params","notes"]

def _fmt_tag(x: float) -> str:
    # 0.1 -> 0p1, 0.01 -> 0p01, 3.0 -> 3
    s = f"{x}".rstrip("0").rstrip(".")
    return s.replace(".", "p")

def _s_tag(s: float) -> str:
    if s == 0: return "s0"
    sign = "sp" if s > 0 else "sm"
    mag = abs(int(s)) if float(s).is_integer() else _fmt_tag(abs(s))
    return f"{sign}{mag}"

def _extract_unique_vals_from_matrix(path: Path):
    df = pd.read_csv(path)
    betas, svals, kCs, deltas = set(), set(), set(), set()
    for ps in df["params"].astype(str).tolist():
        mb = re.search(r"beta=([0-9\.eE+-]+)", ps)
        if mb: betas.add(float(mb.group(1)))
        # VC quartic(...)
        mv = re.search(r"VC=quartic\(([^)]*)\)", ps.replace(" ", ""))
        if mv:
            inside = mv.group(1)
            md = re.search(r"delta=([0-9\.eE+-]+)", inside)
            ms = re.search(r"s=([0-9\.eE+-]+)", inside)
            if md: deltas.add(float(md.group(1)))
            if ms: svals.add(float(ms.group(1)))
        mkc = re.search(r"kC=([0-9\.eE+-]+)", ps)
        if mkc: kCs.add(float(mkc.group(1)))
    return sorted(betas), sorted(svals), sorted(kCs), sorted(deltas)

def _base_fields(seed: int):
    return dict(model="C_I", dim=2, bc="periodic", integrator="semiimplicit",
                grid=64, dt=0.001, T=0.6, seed=seed, max_steps=300000)

def main():
    root = Path(".")
    mdir = root / "matrices"
    mdir.mkdir(exist_ok=True)

    # --- derive grids from existing matrices if present (fallback to safe defaults) ---
    betas = [0.0, 0.1, 0.3, 1.0, 3.0]
    svals = [-2.0, -1.0, 0.0, 1.0, 2.0]
    rvals = [0.1, 0.3, 1.0, 3.0, 10.0, 30.0]   # kC=r, kI=1/r
    dvals = [0.01, 0.1, 0.3, 1.0, 3.0, 10.0]

    # pull betas/s from prior beta×s cross-sweep if exists
    p_bs = mdir / "UET_Cross_CI_beta_s_sweep_seed10.csv"
    if p_bs.exists():
        b2, s2, _, _ = _extract_unique_vals_from_matrix(p_bs)
        if b2: betas = b2
        if s2: svals = s2

    # pull r grid from k_ratio sweep if exists (kC values)
    p_kr = mdir / "UET_Param_CI_k_ratio_sweep.csv"
    if p_kr.exists():
        _, _, kCs, _ = _extract_unique_vals_from_matrix(p_kr)
        if kCs: rvals = kCs

    # pull delta grid from delta sweep if exists (from VC quartic delta)
    p_d = mdir / "UET_Param_CI_delta_sweep.csv"
    if p_d.exists():
        _, _, _, ds = _extract_unique_vals_from_matrix(p_d)
        if ds: dvals = ds

    seeds = range(10)

    # --- 1) beta × k_ratio ---
    rows = []
    for beta in betas:
        btag = _fmt_tag(beta)
        for r in rvals:
            rtag = _fmt_tag(r)
            kC = r
            kI = 1.0 / r
            for seed in seeds:
                case_id = f"param_CI_bk_b{btag}_r{rtag}_seed{seed}"
                params = (
                    f"kC={kC},kI={kI},MC=1,MI=1,beta={beta},"
                    f"VC=quartic(a=1,delta=1,s=0),VI=quartic(a=1,delta=1,s=0)"
                )
                row = {"case_id":case_id,"tier":"param_CI_betaXk_ratio","params":params,
                       "notes":"CROSS-SWEEP | beta × k_ratio | symmetric VC/VI | seed10"}
                row.update(_base_fields(seed))
                rows.append(row)
    pd.DataFrame(rows, columns=COLS).to_csv(mdir / "UET_Cross_CI_beta_k_ratio_seed10.csv", index=False)

    # --- 2) beta × delta (symmetric delta on both pots) ---
    rows = []
    for beta in betas:
        btag = _fmt_tag(beta)
        for d in dvals:
            dtag = _fmt_tag(d)
            for seed in seeds:
                case_id = f"param_CI_bd_b{btag}_d{dtag}_seed{seed}"
                params = (
                    f"kC=1,kI=1,MC=1,MI=1,beta={beta},"
                    f"VC=quartic(a=1,delta={d},s=0),VI=quartic(a=1,delta={d},s=0)"
                )
                row = {"case_id":case_id,"tier":"param_CI_betaXdelta","params":params,
                       "notes":"CROSS-SWEEP | beta × delta | symmetric VC/VI | seed10"}
                row.update(_base_fields(seed))
                rows.append(row)
    pd.DataFrame(rows, columns=COLS).to_csv(mdir / "UET_Cross_CI_beta_delta_seed10.csv", index=False)

    # --- 3) s × delta (optional; beta fixed at 0.5 like your single sweeps) ---
    rows = []
    beta_fixed = 0.5
    for s in svals:
        stag = _s_tag(s)
        for d in dvals:
            dtag = _fmt_tag(d)
            for seed in seeds:
                case_id = f"param_CI_sd_{stag}_d{dtag}_seed{seed}"
                params = (
                    f"kC=1,kI=1,MC=1,MI=1,beta={beta_fixed},"
                    f"VC=quartic(a=1,delta={d},s={s}),VI=quartic(a=1,delta={d},s={s})"
                )
                row = {"case_id":case_id,"tier":"param_CI_sXdelta","params":params,
                       "notes":"CROSS-SWEEP | s × delta | symmetric VC/VI | beta=0.5 | seed10"}
                row.update(_base_fields(seed))
                rows.append(row)
    pd.DataFrame(rows, columns=COLS).to_csv(mdir / "UET_Cross_CI_s_delta_seed10.csv", index=False)

    print("Wrote:")
    print(" -", mdir / "UET_Cross_CI_beta_k_ratio_seed10.csv")
    print(" -", mdir / "UET_Cross_CI_beta_delta_seed10.csv")
    print(" -", mdir / "UET_Cross_CI_s_delta_seed10.csv")

if __name__ == "__main__":
    main()
