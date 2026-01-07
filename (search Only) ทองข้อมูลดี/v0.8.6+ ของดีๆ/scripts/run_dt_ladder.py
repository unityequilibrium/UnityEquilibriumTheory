#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, shutil
from pathlib import Path
from typing import Dict, Any, List
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
from uet_core.solver import run_case
from uet_core.logging import init_run_folder, write_meta, write_timeseries, write_summary

def _parse_list(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]

def _case_slug(base: str, integrator: str, dt: float) -> str:
    dt_s = f"{dt:.8g}".replace(".","p")
    return f"{base}__{integrator}__dt{dt_s}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--out", default="dt_ladder_runs")
    ap.add_argument("--ledger", default="")
    ap.add_argument("--max_steps", type=int, default=20000)
    ap.add_argument("--bt_factor", type=float, default=0.5)
    ap.add_argument("--max_backtracks", type=int, default=30)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    out_root = Path(args.out)
    if args.overwrite and out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    ledger_path = Path(args.ledger) if args.ledger else (out_root / "dt_ladder_ledger.csv")

    cols = [
        "base_case_id","band","variant","origin_case_id","origin_fail_code","case_id","model","integrator","dt","T","N","L","seed",
        "status","fail_code","Omega0","OmegaT","DeltaOmega",
        "steps_attempted","steps_accepted","dt_backtracks_total","dt_min",
        "S_C","S_I","run_dir"
    ]

    rows_out: List[Dict[str, Any]] = []

    with Path(args.matrix).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            base_case_id = r["base_case_id"].strip()
            band = (r.get("band","") or "").strip()
            variant = (r.get("variant","") or "").strip()
            origin_case_id = (r.get("origin_case_id","") or "").strip()
            origin_fail_code = (r.get("origin_fail_code","") or "").strip()
            model = r["model"].strip()
            params_str = r["params"].strip()
            N = int(float(r.get("N", "128")))
            L = float(r.get("L", "1.0"))
            T = float(r.get("T", "5.0"))
            seed = int(float(r.get("seed", "0")))
            dt_list = [float(x) for x in _parse_list(r.get("dt_list",""))]
            integrators = _parse_list(r.get("integrators","semiimplicit"))
            stab = {
                "scale": float(r.get("stab_scale","0.5")),
                "margin": float(r.get("stab_margin","0.0")),
                "min": float(r.get("stab_min","0.0")),
                "max": float(r.get("stab_max","1e9")),
            }

            parsed_params = parse_case_params(model, params_str)

            for integrator in integrators:
                for dt in dt_list:
                    case_id = _case_slug(base_case_id, integrator, dt)
                    rng = np.random.default_rng(seed)

                    config = {
                        "case_id": case_id,
                        "model": model,
                        "units": {"mode":"dimensionless"},
                        "domain": {"dim": 2, "L": L, "bc": "periodic"},
                        "grid": {"N": N, "dtype": "float64"},
                        "time": {
                            "dt": dt, "T": T, "max_steps": args.max_steps,
                            "tol_abs": 1e-10, "tol_rel": 1e-10,
                            "backtrack": {"enabled": True, "factor": args.bt_factor, "max_backtracks": args.max_backtracks},
                        },
                        "integrator": {"name": integrator, "mode": "strict", "stabilization": stab},
                        "rng": {"seed": seed, "algorithm":"numpy_pc64"},
                        "params": parsed_params,
                    }
                    # Optional determinism probe tag (does not affect dynamics; used for unique run_id)
                    probe_tag = str(r.get("probe_tag","")).strip()
                    if probe_tag:
                        config["probe"] = {"tag": probe_tag}

                    run_dir, _, _ = init_run_folder(out_root, model, case_id, config)
                    meta = {
                        "base_case_id": base_case_id,
                        "band": band,
                        "variant": variant,
                        "origin_case_id": origin_case_id,
                        "origin_fail_code": origin_fail_code,
                        "integrator": integrator,
                        "dt": dt,
                    }
                    (run_dir / "meta_dt_ladder.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

                    summary, ts = run_case(config, rng)
                    summary["fail_code"] = derive_fail_code(summary)
                    write_meta(run_dir, code_hash="uet_harness_v0.1")
                    write_timeseries(run_dir, ts)
                    write_summary(run_dir, summary)

                    row = {
                        "base_case_id": base_case_id,
                        "band": band,
                        "variant": variant,
                        "origin_case_id": origin_case_id,
                        "origin_fail_code": origin_fail_code,
                        "case_id": case_id,
                        "model": model,
                        "integrator": integrator,
                        "dt": dt,
                        "T": T,
                        "N": N,
                        "L": L,
                        "seed": seed,
                        "status": summary.get("status",""),
                        "fail_code": summary.get("fail_code",""),
                        "Omega0": summary.get("Omega0",""),
                        "OmegaT": summary.get("OmegaT",""),
                        "DeltaOmega": summary.get("DeltaOmega",""),
                        "steps_attempted": summary.get("steps_attempted",""),
                        "steps_accepted": summary.get("steps_accepted",""),
                        "dt_backtracks_total": summary.get("dt_backtracks_total",""),
                        "dt_min": summary.get("dt_min",""),
                        "S_C": summary.get("S_C",""),
                        "S_I": summary.get("S_I",""),
                        "run_dir": str(run_dir),
                    }
                    rows_out.append(row)
                    print(f"[{base_case_id}] {integrator} dt={dt:g} => {row['status']} backtracks={row['dt_backtracks_total']} dt_min={row['dt_min']}")

    with ledger_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in rows_out:
            w.writerow(row)

    print(f"Wrote ledger: {ledger_path}")

if __name__ == "__main__":
    main()
