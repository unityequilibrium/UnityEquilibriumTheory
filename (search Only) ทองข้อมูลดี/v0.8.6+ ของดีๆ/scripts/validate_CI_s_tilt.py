
import argparse, re, math
from pathlib import Path
import pandas as pd
import numpy as np

def parse_family_and_s(case_id: str):
    m = re.match(r"(param_CI_sC)_(-?\d+)_seed\d+", case_id)
    if m: return m.group(1), float(m.group(2))
    m = re.match(r"(param_CI_sI)_(-?\d+)_seed\d+", case_id)
    if m: return m.group(1), float(m.group(2))
    m = re.match(r"(param_CI_sOpp)_(-?\d+)_seed\d+", case_id)
    if m: return m.group(1), float(m.group(2))
    return "unknown", float("nan")

def load_timeseries(run_dir: Path):
    # prefer timeseries.csv, else first csv starting with timeseries
    p = run_dir/"timeseries.csv"
    if p.exists():
        return pd.read_csv(p)
    cand = sorted(run_dir.glob("timeseries*.csv"))
    if cand:
        return pd.read_csv(cand[0])
    return None

def plateau_flags(ts: pd.DataFrame, window: int, plateau_tol: float):
    # plateau if mean |dOmega| and std(dOmega) small in last window
    if ts is None or len(ts) < max(10, window//2):
        return False, {"plateau": False, "reason": "NO_TIMESERIES"}
    tail = ts.tail(window)
    if "dOmega" not in tail.columns or "Omega" not in tail.columns:
        return False, {"plateau": False, "reason": "MISSING_COLUMNS"}
    mean_abs = float(np.mean(np.abs(tail["dOmega"].to_numpy())))
    std = float(np.std(tail["dOmega"].to_numpy()))
    omega_end = float(tail["Omega"].iloc[-1])
    # normalized slope (avoid division by tiny)
    denom = max(1.0, abs(omega_end))
    norm_slope = mean_abs/denom
    ok = (mean_abs <= plateau_tol) or (norm_slope <= plateau_tol)
    return ok, {
        "plateau": ok,
        "mean_abs_dOmega": mean_abs,
        "std_dOmega": std,
        "Omega_end": omega_end,
        "norm_slope": norm_slope
    }

def fit_alpha(df: pd.DataFrame):
    # Fit OmegaT ≈ -alpha*s^2 (least squares), using s!=0
    sub = df[(df["s"] != 0) & np.isfinite(df["s"]) & (df["status"] == "PASS") & (df["plateau_ok"] == True)]
    if len(sub) < 4:
        return float("nan"), len(sub)
    s2 = (sub["s"].to_numpy()**2)
    y = -sub["OmegaT"].to_numpy()
    # alpha = argmin || alpha*s2 - y ||^2
    alpha = float(np.dot(s2, y) / np.dot(s2, s2))
    return alpha, len(sub)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="runs directory (contains ledger.csv and run_id subfolders)")
    ap.add_argument("--out_csv", default="", help="output validation csv path")
    ap.add_argument("--window", type=int, default=400)
    ap.add_argument("--plateau_tol", type=float, default=1e-5)
    ap.add_argument("--rel_tol", type=float, default=0.05)
    ap.add_argument("--abs_tol", type=float, default=0.02)
    args = ap.parse_args()

    runs = Path(args.runs)
    ledger = pd.read_csv(runs/"ledger.csv")

    # enrich with family + s + plateau
    fam=[]
    sval=[]
    plateau=[]
    mean_abs=[]
    norm_slope=[]
    ts_missing=0
    for _,row in ledger.iterrows():
        family, s = parse_family_and_s(str(row["case_id"]))
        fam.append(family); sval.append(s)
        run_id = row["run_id"]
        ts = load_timeseries(runs/str(run_id))
        ok, meta = plateau_flags(ts, args.window, args.plateau_tol)
        plateau.append(ok)
        mean_abs.append(meta.get("mean_abs_dOmega", float("nan")))
        norm_slope.append(meta.get("norm_slope", float("nan")))
        if meta.get("reason") == "NO_TIMESERIES":
            ts_missing += 1

    ledger["family"]=fam
    ledger["s"]=sval
    ledger["plateau_ok"]=plateau
    ledger["mean_abs_dOmega"]=mean_abs
    ledger["norm_slope"]=norm_slope

    # fit alpha per family
    alphas={}
    counts={}
    for family in ["param_CI_sC","param_CI_sI","param_CI_sOpp"]:
        a, n = fit_alpha(ledger[ledger["family"]==family])
        alphas[family]=a
        counts[family]=n

    # score mismatch vs fitted curve
    pred=[]
    resid=[]
    mismatch=[]
    for _,row in ledger.iterrows():
        family=row["family"]
        s=row["s"]
        a=alphas.get(family, float("nan"))
        if not np.isfinite(a) or not np.isfinite(s):
            p=float("nan")
        else:
            p = -a*(s**2)
        pred.append(p)
        r = float(row["OmegaT"] - p) if np.isfinite(p) else float("nan")
        resid.append(r)
        tol = args.abs_tol + args.rel_tol*abs(p) if np.isfinite(p) else float("nan")
        mm = (abs(r) > tol) if np.isfinite(tol) else True
        mismatch.append(mm)

    ledger["OmegaT_pred"]=pred
    ledger["OmegaT_resid"]=resid
    ledger["mismatch"]=mismatch

    # grade
    grades=[]
    reasons=[]
    for _,row in ledger.iterrows():
        if row["status"] != "PASS":
            grades.append("FAIL"); reasons.append("STATUS_FAIL"); continue
        if not row["plateau_ok"]:
            grades.append("WARN"); reasons.append("NO_PLATEAU"); continue
        # For s=0 we expect OmegaT near 0; keep strict
        if row["s"] == 0:
            if abs(row["OmegaT"]) > 1e-3:
                grades.append("WARN"); reasons.append("S0_NOT_ZERO")
            else:
                grades.append("PASS"); reasons.append("")
            continue
        if row["mismatch"]:
            grades.append("WARN"); reasons.append("OMEGAT_NOT_ON_CURVE"); continue
        grades.append("PASS"); reasons.append("")

    out = pd.DataFrame({
        "run_id": ledger["run_id"],
        "case_id": ledger["case_id"],
        "family": ledger["family"],
        "s": ledger["s"],
        "status": ledger["status"],
        "grade": grades,
        "reasons": reasons,
        "OmegaT": ledger["OmegaT"],
        "OmegaT_pred": ledger["OmegaT_pred"],
        "OmegaT_resid": ledger["OmegaT_resid"],
        "plateau_ok": ledger["plateau_ok"],
        "mean_abs_dOmega": ledger["mean_abs_dOmega"],
        "norm_slope": ledger["norm_slope"],
    })

    if not args.out_csv:
        args.out_csv = str(runs/"validation_tilt.csv")
    out.to_csv(args.out_csv, index=False)

    # print summary
    print("Fitted alphas:", alphas)
    print("Fit counts:", counts)
    print("Grades:", out["grade"].value_counts().to_dict())
    print("Wrote:", args.out_csv)

if __name__ == "__main__":
    main()
