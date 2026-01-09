import argparse, math
from pathlib import Path
import pandas as pd
import numpy as np

ENERGY_EPS = 1e-10   # หรือ 1e-11 ก็ได้ (ของมึงเจอแค่ ~1e-12)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="runs directory containing ledger.csv")
    ap.add_argument("--out_csv", default="", help="output csv path (default: runs/validation_stress.csv)")
    ap.add_argument("--max_backtracks", type=int, default=0, help="warn if backtracks_total > this (0 means require 0)")
    ap.add_argument("--omega_nan_fail", action="store_true", help="fail if OmegaT or Omega0 is NaN")
    args = ap.parse_args()

    runs = Path(args.runs)
    ledger = pd.read_csv(runs/"ledger.csv")

    grades=[]
    reasons=[]
    for _,row in ledger.iterrows():
        if str(row.get("status","")) != "PASS":
            grades.append("FAIL"); reasons.append("STATUS_FAIL"); continue
        # energy monotonicity: max_energy_increase should be <= 0 (or extremely tiny numerical noise)
        mei = float(row.get("max_energy_increase", 0.0))
        if mei > ENERGY_EPS:
            grades.append("WARN"); reasons.append("ENERGY_INCREASE"); continue
        bt = int(row.get("backtracks_total", 0))
        if bt > int(args.max_backtracks):
            grades.append("WARN"); reasons.append("BACKTRACKS"); continue
        if args.omega_nan_fail:
            if not np.isfinite(float(row.get("OmegaT", float("nan")))) or not np.isfinite(float(row.get("Omega0", float("nan")))):
                grades.append("FAIL"); reasons.append("OMEGA_NAN"); continue
        grades.append("PASS"); reasons.append("")

    out = pd.DataFrame({
        "run_id": ledger.get("run_id", ""),
        "case_id": ledger["case_id"],
        "model": ledger.get("model",""),
        "status": ledger.get("status",""),
        "grade": grades,
        "reasons": reasons,
        "Omega0": ledger.get("Omega0", np.nan),
        "OmegaT": ledger.get("OmegaT", np.nan),
        "max_energy_increase": ledger.get("max_energy_increase", 0.0),
        "backtracks_total": ledger.get("backtracks_total", 0),
        "dt_min": ledger.get("dt_min", np.nan),
        "dt_max": ledger.get("dt_max", np.nan),
        "grid": ledger.get("grid", np.nan),
        "T": ledger.get("T", np.nan),
    })

    if not args.out_csv:
        args.out_csv = str(runs/"validation_stress.csv")
    out.to_csv(args.out_csv, index=False)
    print("Grades:", out["grade"].value_counts().to_dict())
    print("Wrote:", args.out_csv)

if __name__ == "__main__":
    main()
