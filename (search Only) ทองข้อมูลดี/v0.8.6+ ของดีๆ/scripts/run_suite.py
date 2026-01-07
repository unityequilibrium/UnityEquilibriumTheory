#!/usr/bin/env python
from __future__ import annotations
import argparse, time, csv
from pathlib import Path
import pandas as pd
import numpy as np

from _bootstrap import ensure_repo_on_path
ensure_repo_on_path()

from uet_core.parser import parse_case_params
from uet_core.solver import run_case, StrictSettings
from uet_core.logging import init_run_folder, write_meta, write_timeseries, write_summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True, help="CSV test matrix")
    ap.add_argument("--out", default="runs")
    ap.add_argument("--progress_every_steps", type=int, default=0, help="Also print progress every N steps (0 disables).")
    ap.add_argument("--progress_every_s", type=float, default=0.0, help="Print progress every N seconds (0 disables).")
    ap.add_argument("--wall_timeout_s", type=float, default=0.0, help="Per-case wall timeout seconds (0 disables).")
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--max_cases", type=int, default=999999)
    args = ap.parse_args()

    df = pd.read_csv(args.matrix)
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    ledger_path = out_root / "ledger.csv"
    ledger_exists = ledger_path.exists()
    ledger_f = open(ledger_path, "a", newline="", encoding="utf-8")
    ledger_w = csv.writer(ledger_f)
    if not ledger_exists:
        ledger_w.writerow(["run_id","case_id","model","grid","status","fail_reasons","Omega0","OmegaT","Omega0_density","OmegaT_density","max_energy_increase","dt_min","dt_max","backtracks_total","config_hash","code_hash","notes"])

    settings = StrictSettings()

    count = 0
    for _, row in df.iterrows():
        if count >= args.max_cases:
            break
        case_id = str(row["case_id"])
        model = str(row["model"])
        N = int(row["grid"])
        dt = float(row["dt"])
        T = float(row.get('T', row.get('t_end', row.get('t', 2.0))))
        seed = int(row["seed"])
        params_str = str(row["params"])

        # Parse model params
        parsed = parse_case_params(model, params_str)

        config = {
            "case_id": case_id,
            "model": model,
            "units": {"mode":"dimensionless"},
            "domain": {"dim": int(row.get("dim",2)), "L": args.L, "bc": str(row.get("bc","periodic"))},
            "grid": {"N": N, "dtype":"float64"},
            "time": {"dt": dt, "T": T, "max_steps": 500000,
                     "tol_abs": 1e-6, "tol_rel": 1e-6,
                     "progress_every_steps": args.progress_every_steps,
                     "progress_every_s": args.progress_every_s,
                     "backtrack": {"enabled": True, "factor": 0.5, "max_backtracks": 20}},
            "integrator": {"name": str(row.get("integrator","semiimplicit")), "mode":"strict"},
            "rng": {"seed": seed, "algorithm":"numpy_pc64"},
            "params": parsed
        }

        run_dir, run_id, cfg_hash = init_run_folder(out_root, model, case_id, config)
        config["run_id"] = run_id
        config["config_hash"] = cfg_hash

        meta = write_meta(run_dir, code_hash="uet_harness_v0.1")
        config["code_hash"] = meta["code_hash"]

        rng = np.random.default_rng(seed)

        t0 = time.time()
        summary, rows = run_case(config, rng, strict=settings)
        summary["runtime_s"] = time.time() - t0
        summary["run_id"] = run_id
        summary["config_hash"] = cfg_hash
        summary["code_hash"] = meta["code_hash"]

        write_timeseries(run_dir, rows)
        write_summary(run_dir, summary)

        ledger_w.writerow([
            run_id, case_id, model, N, summary["status"], "|".join(summary["fail_reasons"]),
            summary["Omega0"], summary["OmegaT"], summary["Omega0_density"], summary["OmegaT_density"],
            summary["max_energy_increase"],
            summary["dt_min"], summary["dt_max"], summary["dt_backtracks_total"],
            cfg_hash, meta["code_hash"], ""
        ])
        ledger_f.flush()

        print(f"[{count+1}] {case_id} {model} -> {summary['status']} (backtracks={summary['dt_backtracks_total']})")
        count += 1

    ledger_f.close()

if __name__ == "__main__":
    main()
