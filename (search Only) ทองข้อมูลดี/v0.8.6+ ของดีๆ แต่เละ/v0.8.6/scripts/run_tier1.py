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
        w.writerow(["run_id","variant","case_id","model","status","fail_reasons","Omega0","OmegaT","max_energy_increase",
                    "dt_used","grid_used","dt_min","dt_max","backtracks_total","config_hash","code_hash","notes"])
    return f, w

def run_one(out_root: Path, row: dict, L: float, variant: str, dt_override: float | None = None, N_override: int | None = None) -> dict:
    case_id = str(row["case_id"])
    model = str(row["model"])
    N = int(row["grid"]) if N_override is None else int(N_override)
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

    meta = write_meta(run_dir, code_hash="uet_harness_v0.1.3")
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
    summary["_grid_used"] = N
    return summary

def classify_summary(summary: dict, eps_range: float = 1e-3) -> str:
    # crude: divergent if FAIL; else steady if range small; else patterned
    if summary.get("status") == "FAIL":
        return "DIVERGENT"
    # This relies on timeseries min/max in summary (max_abs is not enough).
    # We approximate from max_abs: if max_abs small, likely steady, but we keep unknown.
    # Better: caller should use classify_run.py for run-folder classification.
    return "UNKNOWN"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True, help="Tier-1 CSV test matrix")
    ap.add_argument("--out", default="runs_tier1")
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--dt_refine", action="store_true", help="run dt/2 variant for every case (mandatory gate)")
    ap.add_argument("--grid_refine_policy", choices=["none","golden","boundary","all"], default="boundary",
                    help="grid refinement selection policy")
    ap.add_argument("--golden", default="", help="Golden set CSV (needed if policy=golden)")
    ap.add_argument("--backtracks_threshold", type=int, default=200, help="boundary policy threshold")
    ap.add_argument("--max_cases", type=int, default=999999)
    args = ap.parse_args()

    df = pd.read_csv(args.matrix)
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    golden_ids = set()
    if args.grid_refine_policy == "golden":
        if not args.golden:
            raise SystemExit("--golden required when grid_refine_policy=golden")
        gdf = pd.read_csv(args.golden)
        golden_ids = set(gdf["case_id"].astype(str).tolist())

    ledger_path = out_root / "ledger_tier1.csv"
    ledger_f, ledger_w = _write_ledger_header_if_needed(ledger_path)

    settings = StrictSettings()
    count = 0
    for _, r in df.iterrows():
        if count >= args.max_cases:
            break
        row = r.to_dict()
        case_id = str(row["case_id"])
        model = str(row["model"])
        N = int(row["grid"])
        dt = float(row["dt"])

        # base
        base_sum = run_one(out_root, row, args.L, variant="base", dt_override=None, N_override=None)
        ledger_w.writerow([base_sum["run_id"],"base",case_id,model,base_sum["status"],"|".join(base_sum["fail_reasons"]),
                           base_sum["Omega0"],base_sum["OmegaT"],base_sum["max_energy_increase"],
                           base_sum["_dt_used"],base_sum["_grid_used"],
                           base_sum["dt_min"],base_sum["dt_max"],base_sum["dt_backtracks_total"],
                           base_sum["config_hash"],base_sum["code_hash"],""])
        ledger_f.flush()
        print(f"[T1-{count+1}] {case_id} -> {base_sum['status']} (bt={base_sum['dt_backtracks_total']})")
        if base_sum["status"] == "FAIL":
            print("STOP: base FAIL")
            break

        # dt refine
        if args.dt_refine:
            dt_half = dt/2.0
            ref_sum = run_one(out_root, row, args.L, variant="dt_half", dt_override=dt_half, N_override=None)
            ledger_w.writerow([ref_sum["run_id"],"dt_half",case_id,model,ref_sum["status"],"|".join(ref_sum["fail_reasons"]),
                               ref_sum["Omega0"],ref_sum["OmegaT"],ref_sum["max_energy_increase"],
                               ref_sum["_dt_used"],ref_sum["_grid_used"],
                               ref_sum["dt_min"],ref_sum["dt_max"],ref_sum["dt_backtracks_total"],
                               ref_sum["config_hash"],ref_sum["code_hash"],""])
            ledger_f.flush()
            print(f"        dt/2 -> {ref_sum['status']} (bt={ref_sum['dt_backtracks_total']})")
            if ref_sum["status"] == "FAIL":
                print("STOP: dt_half FAIL")
                break

        # grid refine policy
        do_grid = False
        if args.grid_refine_policy == "all":
            do_grid = True
        elif args.grid_refine_policy == "golden":
            do_grid = case_id in golden_ids
        elif args.grid_refine_policy == "boundary":
            # boundary if heavy backtracking or WARN
            do_grid = (base_sum["dt_backtracks_total"] >= args.backtracks_threshold) or (base_sum["status"] == "WARN")

        if do_grid:
            N2 = N*2
            # stability: default dt unchanged; user can rerun if needed
            gsum = run_one(out_root, row, args.L, variant="grid_double", dt_override=dt, N_override=N2)
            ledger_w.writerow([gsum["run_id"],"grid_double",case_id,model,gsum["status"],"|".join(gsum["fail_reasons"]),
                               gsum["Omega0"],gsum["OmegaT"],gsum["max_energy_increase"],
                               gsum["_dt_used"],gsum["_grid_used"],
                               gsum["dt_min"],gsum["dt_max"],gsum["dt_backtracks_total"],
                               gsum["config_hash"],gsum["code_hash"],"policy="+args.grid_refine_policy])
            ledger_f.flush()
            print(f"        grid*2 -> {gsum['status']} (N={N2}, bt={gsum['dt_backtracks_total']})")
            if gsum["status"] == "FAIL":
                print("STOP: grid_double FAIL")
                break

        count += 1

    ledger_f.close()
    print(f"Done. Wrote {ledger_path}")

if __name__ == "__main__":
    main()
