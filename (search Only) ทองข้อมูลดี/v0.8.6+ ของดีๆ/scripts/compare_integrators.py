#!/usr/bin/env python
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
import numpy as np

from uet_core.parser import parse_case_params
from uet_core.solver import run_case
from uet_core.logging import init_run_folder, write_meta, write_timeseries, write_summary

def run_one(outdir: Path, case_id: str, model: str, params_str: str, N: int, L: float, dt: float, T: float, seed: int, integrator: str):
    rng = np.random.default_rng(seed)
    parsed = parse_case_params(model, params_str)
    config = {
        "case_id": case_id,
        "model": model,
        "units": {"mode":"dimensionless"},
        "domain": {"dim":2, "L": L, "bc":"periodic"},
        "grid": {"N": N, "dtype":"float64"},
        "time": {"dt": dt, "T": T, "max_steps": 20000, "tol_abs": 1e-10, "tol_rel": 1e-10,
                 "backtrack": {"enabled": True, "factor": 0.5, "max_backtracks": 30}},
        "integrator": {"name": integrator, "mode":"strict",
                       "stabilization": {"scale": 0.5, "margin": 0.0, "min": 0.0, "max": 1e9}},
        "rng": {"seed": seed, "algorithm":"numpy_pc64"},
        "params": parsed,
    }
    run_dir = init_run_folder(outdir, case_id)
    meta = {"case_id": case_id, "model": model, "integrator": integrator}
    _, summary, ts = run_case(config, rng)
    write_meta(run_dir, config, meta)
    write_timeseries(run_dir, ts)
    write_summary(run_dir, summary)
    return summary, run_dir

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="compare_integrators_out")
    ap.add_argument("--case_id", default="cmp")
    ap.add_argument("--model", choices=["C_only","C_I"], required=True)
    ap.add_argument("--params", required=True)
    ap.add_argument("--N", type=int, default=128)
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--dt", type=float, default=1e-2)
    ap.add_argument("--T", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    outdir = Path(args.out)
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)

    print("Running semiimplicit...")
    sum1, d1 = run_one(outdir, args.case_id+"_semi", args.model, args.params, args.N, args.L, args.dt, args.T, args.seed, "semiimplicit")
    print("Running stabilized...")
    sum2, d2 = run_one(outdir, args.case_id+"_stab", args.model, args.params, args.N, args.L, args.dt, args.T, args.seed, "stabilized")

    def short(s): 
        keys = ["status","Omega0","OmegaT","DeltaOmega","dt_backtracks_total","dt_min","steps_accepted","fail_code"]
        return {k: s.get(k,"") for k in keys}

    report = {
        "semiimplicit": {"run_dir": str(d1), **short(sum1)},
        "stabilized": {"run_dir": str(d2), **short(sum2)},
    }
    (outdir/"compare_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
