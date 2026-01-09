#!/usr/bin/env python
from __future__ import annotations
import argparse, time
from pathlib import Path
import json
import numpy as np


def derive_fail_code(summary: dict) -> str:
    st = str(summary.get("status","")).upper()
    if st == "PASS":
        return "PASS"
    fc = str(summary.get("fail_code","")).strip()
    if fc:
        return fc
    fr = summary.get("fail_reasons", []) or []
    if isinstance(fr, list) and len(fr) > 0:
        code = str(fr[0]).strip()
        return code if code else "FAIL"
    return "FAIL"

from uet_core.parser import parse_case_params
from uet_core.solver import run_case, StrictSettings
from uet_core.logging import init_run_folder, write_meta, write_timeseries, write_summary
from uet_core.validation import run_gates
from uet_core.feedback import analyze_run

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case_id", required=True)
    ap.add_argument("--model", required=True, choices=["C_only","C_I"])
    ap.add_argument("--params", required=True, help="params string from matrix")
    ap.add_argument("--out", default="runs")
    ap.add_argument("--progress_every_steps", type=int, default=0, help="Also print progress every N steps (0 disables).")
    ap.add_argument("--progress_every_s", type=float, default=0.0, help="Print progress every N seconds (0 disables).")
    ap.add_argument("--wall_timeout_s", type=float, default=0.0, help="Wall timeout seconds (0 disables).")
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--N", type=int, default=32)
    ap.add_argument("--dt", type=float, default=5e-4)
    ap.add_argument("--T", type=float, default=0.2)
    ap.add_argument("--max_steps", type=int, default=200000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    parsed = parse_case_params(args.model, args.params)

    config = {
        "case_id": args.case_id,
        "model": args.model,
        "units": {"mode":"dimensionless"},
        "domain": {"dim":2, "L": args.L, "bc":"periodic"},
        "grid": {"N": args.N, "dtype":"float64"},
        "time": {"dt": args.dt, "T": args.T, "max_steps": args.max_steps,
                 "tol_abs": 1e-10, "tol_rel": 1e-10,
                 "backtrack": {"enabled": True, "factor": 0.5, "max_backtracks": 20}},
        "integrator": {"name":"semiimplicit", "mode":"strict"},
        "rng": {"seed": args.seed, "algorithm":"numpy_pc64"},
        "params": parsed
    }

    out_root = Path(args.out)
    run_dir, run_id, cfg_hash = init_run_folder(out_root, args.model, args.case_id, config)
    config["run_dir"] = str(run_dir)
    config["config_hash"] = cfg_hash

    meta = write_meta(run_dir, code_hash="uet_harness_v0.1")
    config["code_hash"] = meta["code_hash"]

    rng = np.random.default_rng(args.seed)

    t0 = time.time()
    summary, rows = run_case(config, rng, strict=StrictSettings())
    summary["fail_code"] = derive_fail_code(summary)
    summary["runtime_s"] = time.time() - t0
    summary["run_id"] = run_id
    summary["config_hash"] = cfg_hash
    summary["code_hash"] = meta["code_hash"]

    write_timeseries(run_dir, rows)
    write_summary(run_dir, summary)
    
    # Run validation gates automatically
    print("\nRunning Validation Gates...")
    run_gates(run_dir)
    

    # 5. Feedback Analysis (Dynamics)
    from uet_core.feedback import analyze_run
    print("Running Feedback Analysis...") # Added this print statement back for clarity
    analyze_run(run_dir)
    
    # 6. Generate Static Report (Server-free Dashboard)
    from uet_core.export import export_static_dashboard
    print("Generating Static Dashboard...")
    export_static_dashboard(run_dir)

    # 7. Update Unified Studio Hub
    from uet_core.index_gen import generate_studio_hub
    print("Updating UET Studio Hub...")
    generate_studio_hub()

    print(f"\n[Done] Results saved to: {run_dir}")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
