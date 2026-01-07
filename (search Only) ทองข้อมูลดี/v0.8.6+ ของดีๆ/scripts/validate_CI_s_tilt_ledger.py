import argparse, re
from pathlib import Path
import pandas as pd
import numpy as np

def parse_family_s(case_id: str):
    for key in ["param_CI_sC","param_CI_sI","param_CI_sOpp"]:
        m = re.match(rf"({key})_(-?\d+)_seed\d+", case_id)
        if m:
            return m.group(1), float(m.group(2))
    return "unknown", float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, help="path to ledger.csv")
    ap.add_argument("--out_csv", default="", help="output csv (default next to ledger)")
    ap.add_argument("--rel_tol", type=float, default=0.01, help="relative tolerance vs expected OmegaT per (family,s)")
    ap.add_argument("--abs_tol", type=float, default=1e-3, help="absolute tolerance vs expected OmegaT per (family,s)")
    args = ap.parse_args()

    ledger_path = Path(args.ledger)
    df = pd.read_csv(ledger_path)

    fam=[]
    sval=[]
    for cid in df["case_id"].astype(str):
        f,s = parse_family_s(cid)
        fam.append(f); sval.append(s)
    df["family"]=fam
    df["s"]=sval

    # Basic health checks
    ok_status = (df["status"]=="PASS")
    ok_energy = (df.get("max_energy_increase", 0.0) <= 0.0)

    # Expected OmegaT per (family,s): robust median across seeds (PASS only)
    ref = (
        df[ok_status]
        .groupby(["family","s"])["OmegaT"]
        .median()
        .rename("OmegaT_ref")
        .reset_index()
    )
    df = df.merge(ref, on=["family","s"], how="left")

    # mismatch test
    tol = args.abs_tol + args.rel_tol*np.abs(df["OmegaT_ref"].to_numpy())
    resid = (df["OmegaT"] - df["OmegaT_ref"]).to_numpy()
    mismatch = np.abs(resid) > tol

    # For s=0, enforce near-zero OmegaT (since tilt is zero)
    s0_mask = (df["s"]==0)
    s0_bad = np.abs(df["OmegaT"].to_numpy()) > 1e-3

    grades=[]
    reasons=[]
    for i,row in df.iterrows():
        if row["status"] != "PASS":
            grades.append("FAIL"); reasons.append("STATUS_FAIL"); continue
        if row.get("max_energy_increase",0.0) > 0.0:
            grades.append("WARN"); reasons.append("ENERGY_INCREASE"); continue
        if row["family"]=="unknown" or not np.isfinite(row["s"]):
            grades.append("WARN"); reasons.append("UNKNOWN_CASE"); continue
        if row["s"]==0 and s0_bad[i]:
            grades.append("WARN"); reasons.append("S0_NOT_ZERO"); continue
        if mismatch[i]:
            grades.append("WARN"); reasons.append("OMEGAT_OUTLIER"); continue
        grades.append("PASS"); reasons.append("")

    out = pd.DataFrame({
        "run_id": df.get("run_id", ""),
        "case_id": df["case_id"],
        "family": df["family"],
        "s": df["s"],
        "status": df["status"],
        "grade": grades,
        "reasons": reasons,
        "OmegaT": df["OmegaT"],
        "OmegaT_ref": df["OmegaT_ref"],
        "OmegaT_resid": resid,
        "max_energy_increase": df.get("max_energy_increase", 0.0),
    })

    if not args.out_csv:
        args.out_csv = str(ledger_path.with_name("validation_tilt_ledger.csv"))
    out.to_csv(args.out_csv, index=False)

    print("Grades:", out["grade"].value_counts().to_dict())
    print("Wrote:", args.out_csv)

if __name__ == "__main__":
    main()
