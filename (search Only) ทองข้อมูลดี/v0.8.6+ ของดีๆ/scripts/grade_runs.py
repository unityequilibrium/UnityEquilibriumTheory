#!/usr/bin/env python
from __future__ import annotations
import argparse, json, math, csv
from pathlib import Path
from typing import Dict, Any, List

def f(x, default=float("nan")):
    try:
        return float(x)
    except Exception:
        return default

def load_json(p: Path) -> Dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def read_timeseries(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as fh:
        rdr = csv.DictReader(fh)
        return [r for r in rdr]

def compute_ts_metrics(ts: List[Dict[str, Any]], eps_tight: float) -> Dict[str, float]:
    if not ts:
        return {"dOmega_max": float("nan"), "dOmega_median": float("nan"), "tight_frac": float("nan")}
    acc = [r for r in ts if str(r.get("accepted","1")) in ("1","True","true")]
    if not acc:
        acc = ts
    dO = [f(r.get("dOmega","nan")) for r in acc]
    dO = [v for v in dO if not math.isnan(v)]
    if not dO:
        return {"dOmega_max": float("nan"), "dOmega_median": float("nan"), "tight_frac": float("nan")}
    dO_sorted = sorted(dO)
    med = dO_sorted[len(dO_sorted)//2]
    tight = sum(1 for v in dO if abs(v) <= eps_tight) / len(dO)
    return {"dOmega_max": max(dO), "dOmega_median": med, "tight_frac": tight}

def grade_one(summary: Dict[str, Any], ts_m: Dict[str, float], cfg: Dict[str, Any], th: Dict[str, float]) -> tuple[str, str]:
    reasons = []
    status = str(summary.get("status","")).upper()

    if bool(summary.get("nan_inf_detected", False)):
        return "FAIL", "nan_inf_detected"
    if bool(summary.get("blowup_detected", False)):
        return "FAIL", "blowup_detected"

    max_abs_C = f(summary.get("max_abs_C", "nan"))
    if not math.isnan(max_abs_C) and max_abs_C > th["C_max_fail"]:
        return "FAIL", f"max_abs_C>{th['C_max_fail']}"

    dt_nom = f(cfg.get("dt","nan"))
    dt_min = f(summary.get("dt_min","nan"))
    if (not math.isnan(dt_nom)) and (not math.isnan(dt_min)) and dt_nom > 0:
        ratio = dt_min / dt_nom
        if ratio < th["dt_collapse_fail"]:
            return "FAIL", f"dt_collapse_ratio<{th['dt_collapse_fail']}"
        if ratio < th["dt_collapse_warn"]:
            reasons.append(f"dt_collapse_ratio<{th['dt_collapse_warn']}")

    bt = f(summary.get("dt_backtracks_total","nan"))
    steps_acc = f(summary.get("steps_accepted","nan"))
    if (not math.isnan(bt)) and (not math.isnan(steps_acc)) and steps_acc > 0:
        btd = bt / steps_acc
        if btd > th["backtracks_density_fail"]:
            return "FAIL", f"backtracks_density>{th['backtracks_density_fail']}"
        if btd > th["backtracks_density_warn"]:
            reasons.append(f"backtracks_density>{th['backtracks_density_warn']}")

    max_inc = f(summary.get("max_energy_increase","nan"))
    inc_count = int(summary.get("energy_increase_count", 0) or 0)

    Omega0 = f(summary.get("Omega0","nan"))
    scale = abs(Omega0) if (not math.isnan(Omega0) and abs(Omega0) > 1.0) else 1.0
    tol_inc = th["dOmega_tol_rel"] * scale + th["dOmega_tol_abs"]

    dOmega_max = ts_m.get("dOmega_max", float("nan"))
    if not math.isnan(dOmega_max):
        if dOmega_max > tol_inc:
            return "FAIL", f"dOmega_max>{tol_inc:.3e}"
        if dOmega_max > th["dOmega_warn_rel"] * scale + th["dOmega_tol_abs"]:
            reasons.append("monotonic_wiggle")
    else:
        if (not math.isnan(max_inc)) and max_inc > tol_inc:
            return "FAIL", f"max_energy_increase>{tol_inc:.3e}"
        if inc_count > th["inc_count_warn"]:
            reasons.append("energy_increase_count_high")

    tight_frac = ts_m.get("tight_frac", float("nan"))
    if not math.isnan(tight_frac):
        if tight_frac < th["tight_frac_fail"]:
            reasons.append(f"not_converged(tight<{th['tight_frac_fail']})")
        elif tight_frac < th["tight_frac_warn"]:
            reasons.append(f"weak_convergence(tight<{th['tight_frac_warn']})")

    if status == "FAIL":
        return "FAIL", "runner_fail|" + "|".join(reasons) if reasons else "runner_fail"
    if reasons:
        return "WARN", "|".join(reasons)
    return "PASS", ""

def main():
    ap = argparse.ArgumentParser(description="Grade runs with physics-aware PASS/WARN/FAIL using summary.json + timeseries.csv.")
    ap.add_argument("--runs", required=True, help="runs folder containing ledger.csv and run subfolders by run_id")
    ap.add_argument("--out", default="", help="output csv (default: <runs>/grades.csv)")
    ap.add_argument("--eps_tight", type=float, default=1e-12, help="tightness epsilon for |dOmega|")

    ap.add_argument("--C_max_fail", type=float, default=50.0)
    ap.add_argument("--dt_collapse_fail", type=float, default=1e-6)
    ap.add_argument("--dt_collapse_warn", type=float, default=1e-3)
    ap.add_argument("--backtracks_density_fail", type=float, default=2.0)
    ap.add_argument("--backtracks_density_warn", type=float, default=0.5)
    ap.add_argument("--dOmega_tol_abs", type=float, default=1e-12)
    ap.add_argument("--dOmega_tol_rel", type=float, default=1e-8)
    ap.add_argument("--dOmega_warn_rel", type=float, default=1e-10)
    ap.add_argument("--inc_count_warn", type=int, default=3)
    ap.add_argument("--tight_frac_fail", type=float, default=0.20)
    ap.add_argument("--tight_frac_warn", type=float, default=0.60)
    ap.add_argument("--write", action="store_true", help="Write grade and reasons back to summary.json for each run")
    args = ap.parse_args()

    runs = Path(args.runs)
    ledger = runs/"ledger.csv"
    if not ledger.exists():
        raise SystemExit(f"ledger not found: {ledger}")

    out = Path(args.out) if args.out else (runs/"grades.csv")

    th = {
        "C_max_fail": args.C_max_fail,
        "dt_collapse_fail": args.dt_collapse_fail,
        "dt_collapse_warn": args.dt_collapse_warn,
        "backtracks_density_fail": args.backtracks_density_fail,
        "backtracks_density_warn": args.backtracks_density_warn,
        "dOmega_tol_abs": args.dOmega_tol_abs,
        "dOmega_tol_rel": args.dOmega_tol_rel,
        "dOmega_warn_rel": args.dOmega_warn_rel,
        "inc_count_warn": args.inc_count_warn,
        "tight_frac_fail": args.tight_frac_fail,
        "tight_frac_warn": args.tight_frac_warn,
    }

    import pandas as pd
    df = pd.read_csv(ledger)

    rows=[]
    for _, r in df.iterrows():
        run_id = str(r.get("run_id","")).strip()
        run_dir = runs/run_id
        sum_p = run_dir/"summary.json"
        summ = load_json(sum_p)
        cfg = load_json(run_dir/"config.json")
        ts = read_timeseries(run_dir/"timeseries.csv")
        ts_m = compute_ts_metrics(ts, eps_tight=args.eps_tight)

        grade, reasons = grade_one(summ, ts_m, cfg, th)

        # Update summary.json if --write is set
        if args.write and sum_p.exists():
            try:
                # Reload fresh to avoid overwriting other fields if concurrent
                with open(sum_p, 'r', encoding='utf-8') as f_in:
                    actual_summ = json.load(f_in)
                
                actual_summ["status"] = grade
                actual_summ["reasons"] = reasons
                actual_summ["verification_gates"] = {
                    "nan_check": "FAIL" if actual_summ.get("nan_inf_detected") else "PASS",
                    "monotone": "FAIL" if "dOmega_max" in reasons or "monotonic" in reasons else "PASS",
                    "dt_collapse": "FAIL" if "dt_collapse" in reasons else "PASS"
                }
                
                with open(sum_p, 'w', encoding='utf-8') as f_out:
                    json.dump(actual_summ, f_out, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Failed to write to {sum_p}: {e}")

        rows.append({
            "run_id": run_id,
            "case_id": r.get("case_id",""),
            "model": r.get("model",""),
            "status_runner": r.get("status",""),
            "grade": grade,
            "reasons": reasons,
            "Omega0": summ.get("Omega0", r.get("Omega0","")),
            "OmegaT": summ.get("OmegaT", r.get("OmegaT","")),
            "max_energy_increase": summ.get("max_energy_increase", r.get("max_energy_increase","")),
            "energy_increase_count": summ.get("energy_increase_count", ""),
            "dt_min": summ.get("dt_min", r.get("dt_min","")),
            "dt_max": summ.get("dt_max", r.get("dt_max","")),
            "dt_backtracks_total": summ.get("dt_backtracks_total", r.get("dt_backtracks_total","")),
            "steps_accepted": summ.get("steps_accepted",""),
            "max_abs_C": summ.get("max_abs_C",""),
            "dOmega_max": ts_m.get("dOmega_max", float("nan")),
            "dOmega_median": ts_m.get("dOmega_median", float("nan")),
            "tight_frac": ts_m.get("tight_frac", float("nan")),
        })

    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {out} (rows={len(rows)})")

if __name__ == "__main__":
    main()
