#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, time
from pathlib import Path
import pandas as pd
import numpy as np

from uet_core.parser import parse_case_params
from uet_core.solver import run_case, StrictSettings
from uet_core.logging import init_run_folder, write_meta, write_timeseries, write_summary

def _write_ledger_header_if_needed(ledger_path: Path):
    exists = ledger_path.exists()
    f = open(ledger_path, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if not exists:
        w.writerow(["run_id","variant","case_id","model","status","fail_reasons","Omega0","OmegaT","max_energy_increase","dt_min","dt_max","backtracks_total","config_hash","code_hash","notes"])
    return f, w

def run_one(out_root: Path, row: dict, L: float, variant: str, dt_override: float | None = None) -> dict:
    case_id = str(row["case_id"])
    model = str(row["model"])
    N = int(row["grid"])
    dt = float(row["dt"]) if dt_override is None else float(dt_override)
    T = float(row["T"])
    seed = int(row["seed"])
    params_str = str(row["params"])

    parsed = parse_case_params(model, params_str)

    config = {
        "case_id": case_id,
        "model": model,
        "units": {"mode":"dimensionless"},
        "domain": {"dim": int(row.get("dim",2)), "L": L, "bc": str(row.get("bc","periodic"))},
        "grid": {"N": N, "dtype":"float64"},
        "time": {"dt": dt, "T": T, "max_steps": 500000,
                 "tol_abs": 1e-10, "tol_rel": 1e-10,
                 "backtrack": {"enabled": True, "factor": 0.5, "max_backtracks": 20}},
        "integrator": {"name": str(row.get("integrator","semiimplicit")), "mode":"strict"},
        "rng": {"seed": seed, "algorithm":"numpy_pc64"},
        "params": parsed
    }

    run_dir, run_id, cfg_hash = init_run_folder(out_root, model, case_id, config)
    config["run_id"] = run_id
    config["config_hash"] = cfg_hash

    meta = write_meta(run_dir, code_hash="uet_harness_v0.1.2")
    config["code_hash"] = meta["code_hash"]

    rng = np.random.default_rng(seed)
    settings = StrictSettings()

    t0 = time.time()
    summary, rows_ts = run_case(config, rng, strict=settings)
    summary["runtime_s"] = time.time() - t0
    summary["run_id"] = run_id
    summary["config_hash"] = cfg_hash
    summary["code_hash"] = meta["code_hash"]

    write_timeseries(run_dir, rows_ts)
    write_summary(run_dir, summary)

    summary["_variant"] = variant
    summary["_dt_used"] = dt
    return summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True, help="Full test matrix CSV (Tier-1)")
    ap.add_argument("--golden", required=True, help="Golden set CSV with case_id list")
    ap.add_argument("--out", default="runs_golden")
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--dt_refine", action="store_true", help="also run dt/2 refinement for each case")
    ap.add_argument("--max_cases", type=int, default=999999)
    args = ap.parse_args()

    df = pd.read_csv(args.matrix)
    gdf = pd.read_csv(args.golden)
    golden_ids = set(gdf["case_id"].astype(str).tolist())

    df_g = df[df["case_id"].astype(str).isin(golden_ids)].copy()
    df_g = df_g.sort_values("case_id")

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    ledger_path = out_root / "ledger_golden.csv"
    ledger_f, ledger_w = _write_ledger_header_if_needed(ledger_path)

    count = 0
    for _, r in df_g.iterrows():
        if count >= args.max_cases:
            break
        row = r.to_dict()
        base_sum = run_one(out_root, row, args.L, variant="base", dt_override=None)
        ledger_w.writerow([
            base_sum["run_id"], "base", base_sum["case_id"], base_sum["model"], base_sum["status"], "|".join(base_sum["fail_reasons"]),
            base_sum["Omega0"], base_sum["OmegaT"], base_sum["max_energy_increase"],
            base_sum["dt_min"], base_sum["dt_max"], base_sum["dt_backtracks_total"],
            base_sum["config_hash"], base_sum["code_hash"], ""
        ])
        ledger_f.flush()
        print(f"[G{count+1}] {base_sum['case_id']} -> {base_sum['status']} (backtracks={base_sum['dt_backtracks_total']})")

        if args.dt_refine:
            dt_half = float(row["dt"]) / 2.0
            ref_sum = run_one(out_root, row, args.L, variant="dt_half", dt_override=dt_half)
            ledger_w.writerow([
                ref_sum["run_id"], "dt_half", ref_sum["case_id"], ref_sum["model"], ref_sum["status"], "|".join(ref_sum["fail_reasons"]),
                ref_sum["Omega0"], ref_sum["OmegaT"], ref_sum["max_energy_increase"],
                ref_sum["dt_min"], ref_sum["dt_max"], ref_sum["dt_backtracks_total"],
                ref_sum["config_hash"], ref_sum["code_hash"], ""
            ])
            ledger_f.flush()
            print(f"      refine(dt/2) -> {ref_sum['status']} (backtracks={ref_sum['dt_backtracks_total']})")

        count += 1

    ledger_f.close()
    print(f"Done. Wrote {ledger_path}")

if __name__ == "__main__":
    main()
