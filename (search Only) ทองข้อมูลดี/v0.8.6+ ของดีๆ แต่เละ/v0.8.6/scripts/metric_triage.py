#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from typing import Dict, Any, List

def parse_list(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]

def _f(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def derive_fail_code_from_summary(summary: dict) -> str:
    st = str(summary.get("status","")).upper()
    if st == "PASS":
        return "PASS"
    fc = str(summary.get("fail_code","")).strip()
    if fc:
        return fc
    fr = summary.get("fail_reasons", []) or []
    if isinstance(fr, list) and fr:
        code = str(fr[0]).strip()
        return code if code else "FAIL"
    return "FAIL"

def quantiles(vals: List[float], qs=(0.1,0.5,0.9)) -> Dict[str,float]:
    vs = sorted([v for v in vals if not math.isnan(v)])
    if not vs:
        return {f"q{int(q*100):02d}": float("nan") for q in qs}
    out={}
    n=len(vs)
    for q in qs:
        idx = int(round((n-1)*q))
        idx = max(0, min(n-1, idx))
        out[f"q{int(q*100):02d}"] = float(vs[idx])
    return out

def add_count(d: Dict[str,int], k: str, inc: int=1):
    d[k] = d.get(k, 0) + inc

def top_counts(d: Dict[str,int], k: int):
    return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:k]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant_summary_csv", required=True)
    ap.add_argument("--monotonic_report_json", default="")
    ap.add_argument("--ledgers", default="")
    ap.add_argument("--thresholds_json", default="")
    ap.add_argument("--out_json", default="metric_triage_report.json")
    ap.add_argument("--out_md", default="metric_triage_report.md")
    ap.add_argument("--top_k", type=int, default=5)
    args = ap.parse_args()

    target_groups = None
    violations = []
    if args.monotonic_report_json:
        rep = json.loads(Path(args.monotonic_report_json).read_text(encoding="utf-8"))
        target_groups = set(rep.get("blocklist_band_model_integrator", []) or [])
        violations = rep.get("violations", []) or []

    # variant summary
    vs_rows=[]
    with Path(args.variant_summary_csv).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            vs_rows.append(r)
    if not vs_rows:
        raise SystemExit("Empty variant summary")

    vs_by_group: Dict[str, Dict[str,Any]] = {}
    for r in vs_rows:
        band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
        model = (r.get("model","") or "").strip()
        integ = (r.get("integrator","") or "").strip()
        gk = f"{band}|{model}|{integ}"
        if target_groups is not None and gk not in target_groups:
            continue
        n = int(float(r.get("n","0") or 0))
        kpass = int(float(r.get("pass","0") or 0))
        pr = _f(r.get("pass_rate","nan"))
        fcj = str(r.get("fail_codes_json","") or "{}")
        try:
            fc = json.loads(fcj) if fcj else {}
        except Exception:
            fc = {}
        ent = vs_by_group.setdefault(gk, {"group": gk, "band": band, "model": model, "integrator": integ,
                                          "n_total": 0, "pass_total": 0, "variants": [], "fail_codes": {}})
        ent["n_total"] += n
        ent["pass_total"] += kpass
        for code, cnt in (fc or {}).items():
            add_count(ent["fail_codes"], str(code), int(cnt))
        ent["variants"].append({"variant": r.get("variant",""), "n": n, "pass": kpass, "pass_rate": pr, "fail_codes": fc})
    for gk, ent in vs_by_group.items():
        ent["variants"] = sorted(ent["variants"], key=lambda x: (x.get("pass_rate",1.0), x.get("n",0)))

    thresholds = {}
    if args.thresholds_json and Path(args.thresholds_json).exists():
        thresholds = json.loads(Path(args.thresholds_json).read_text(encoding="utf-8"))

    # ledger summaries
    run_stats: Dict[str, Dict[str,Any]] = {}
    for lp in [Path(p) for p in parse_list(args.ledgers)]:
        if not lp.exists():
            continue
        with lp.open("r", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
                model = (r.get("model","") or "").strip()
                integ = (r.get("integrator","") or "").strip()
                gk = f"{band}|{model}|{integ}"
                if target_groups is not None and gk not in target_groups:
                    continue
                run_dir = Path(str(r.get("run_dir","")).strip())
                summ_path = run_dir/"summary.json"
                if not summ_path.exists():
                    continue
                try:
                    summ = json.loads(summ_path.read_text(encoding="utf-8"))
                except Exception:
                    continue
                status = str(summ.get("status","")).upper()
                fc = str(r.get("fail_code","")).strip() or derive_fail_code_from_summary(summ)

                dt = _f(r.get("dt","nan"))
                dt_min = _f(summ.get("dt_min", r.get("dt_min","nan")))
                steps_acc = _f(summ.get("steps_accepted", r.get("steps_accepted","nan")))
                bt_total = _f(summ.get("dt_backtracks_total", r.get("dt_backtracks_total","nan")))
                backtracks_density = (bt_total/steps_acc) if (not math.isnan(bt_total) and not math.isnan(steps_acc) and steps_acc>0) else float("nan")
                dt_collapse_ratio = (dt_min/dt) if (not math.isnan(dt_min) and not math.isnan(dt) and dt>0) else float("nan")

                rs = run_stats.setdefault(gk, {"n":0,"pass":0,"fail_codes":{}, "metrics":{
                    "max_energy_increase": [], "energy_increase_count": [],
                    "dt_collapse_ratio": [], "backtracks_density": [],
                    "nan_inf_detected": 0, "blowup_detected": 0
                }})
                rs["n"] += 1
                if status == "PASS":
                    rs["pass"] += 1
                else:
                    add_count(rs["fail_codes"], fc, 1)

                m=rs["metrics"]
                m["max_energy_increase"].append(_f(summ.get("max_energy_increase","nan")))
                m["energy_increase_count"].append(_f(summ.get("energy_increase_count","nan")))
                m["dt_collapse_ratio"].append(dt_collapse_ratio)
                m["backtracks_density"].append(backtracks_density)
                if bool(summ.get("nan_inf_detected", False)): m["nan_inf_detected"] += 1
                if bool(summ.get("blowup_detected", False)): m["blowup_detected"] += 1

    groups=[]
    for gk, ent in sorted(vs_by_group.items()):
        top_fc = top_counts(ent["fail_codes"], args.top_k)
        fc_names = [c for c,_ in top_fc]
        rs = run_stats.get(gk)
        metric_summary={}
        flags=[]
        if rs:
            m=rs["metrics"]
            metric_summary = {
                "n": rs["n"], "pass": rs["pass"], "pass_rate": rs["pass"]/rs["n"] if rs["n"] else float("nan"),
                "top_fail_codes": top_counts(rs["fail_codes"], args.top_k),
                "nan_inf_rate": m["nan_inf_detected"]/rs["n"] if rs["n"] else 0.0,
                "blowup_rate": m["blowup_detected"]/rs["n"] if rs["n"] else 0.0,
                "q_backtracks_density": quantiles(m["backtracks_density"]),
                "q_dt_collapse_ratio": quantiles(m["dt_collapse_ratio"]),
                "q_max_energy_increase": quantiles(m["max_energy_increase"]),
                "q_energy_increase_count": quantiles(m["energy_increase_count"]),
            }
            bd_max=thresholds.get("backtracks_density_max")
            if bd_max is not None:
                vals=[v for v in m["backtracks_density"] if not math.isnan(v)]
                denom=max(1,len(vals))
                frac=sum(1 for v in vals if v>float(bd_max))/denom
                flags.append({"metric":"backtracks_density", "threshold": float(bd_max), "frac_exceed": float(frac)})
            dc_min=thresholds.get("dt_collapse_ratio_min")
            if dc_min is not None:
                vals=[v for v in m["dt_collapse_ratio"] if not math.isnan(v)]
                denom=max(1,len(vals))
                frac=sum(1 for v in vals if v<float(dc_min))/denom
                flags.append({"metric":"dt_collapse_ratio", "threshold": float(dc_min), "frac_below": float(frac)})

        diag=[]
        if any(c in ("NAN_INF","BLOWUP") for c in fc_names):
            diag.append("Dominant failures are NAN/INF or BLOWUP → numerical instability; decrease dt and check caps/potentials.")
        if "ENERGY_INCREASE" in fc_names:
            diag.append("ENERGY_INCREASE appears → Ω monotonicity/backtracking could not find acceptable step; reduce preset dt or tune backtracking/tolerances/stabilization.")
        if rs:
            q90 = metric_summary.get("q_backtracks_density",{}).get("q90", float("nan"))
            q10 = metric_summary.get("q_dt_collapse_ratio",{}).get("q10", float("nan"))
            if (not math.isnan(q90) and q90>0.5) or (not math.isnan(q10) and q10<0.2):
                diag.append("High backtracking density or strong dt collapse in tail → solver working hard; lowering preset dt often improves stability/performance.")
        if not diag:
            diag.append("No single dominant mechanism detected; consider increasing samples or inspecting per-run summaries.")
        groups.append({
            "group": gk, "band": ent["band"], "model": ent["model"], "integrator": ent["integrator"],
            "variant_summary": {"n_total": ent["n_total"], "pass_total": ent["pass_total"],
                              "pass_rate": ent["pass_total"]/ent["n_total"] if ent["n_total"] else float("nan"),
                              "top_fail_codes": top_fc},
            "run_metrics_summary": metric_summary,
            "threshold_flags": flags,
            "diagnosis": diag,
            "worst_variants": ent["variants"][:min(10, len(ent["variants"]))],
        })

    report={"meta":{
        "variant_summary_csv": str(Path(args.variant_summary_csv)),
        "monotonic_report_json": str(Path(args.monotonic_report_json)) if args.monotonic_report_json else "",
        "n_groups": len(groups),
        "ledgers_used": [str(p) for p in parse_list(args.ledgers) if Path(p).exists()],
    },
    "violations_sample": violations[:50],
    "groups": groups,
    "thresholds": thresholds}

    out_json=Path(args.out_json); out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md=[]
    md.append("# Metric Triage Report (R0-E22)\n\n")
    md.append(f"- Groups analyzed: **{len(groups)}**\n")
    if target_groups is not None: md.append("- Restricted to monotonic blocklist groups.\n")
    md.append("\n---\n\n")
    for g in groups:
        md.append(f"## {g['group']}\n")
        vs=g["variant_summary"]
        md.append(f"- Variant summary: n={vs['n_total']} pass_rate={vs['pass_rate']:.3f}\n")
        md.append(f"- Top fail codes (variant agg): {vs['top_fail_codes']}\n")
        rms=g.get("run_metrics_summary",{})
        if rms:
            md.append(f"- Run metrics: n={rms.get('n')} pass_rate={rms.get('pass_rate', float('nan')):.3f} nan_inf_rate={rms.get('nan_inf_rate'):.3f} blowup_rate={rms.get('blowup_rate'):.3f}\n")
            md.append(f"  - q(backtracks_density): {rms.get('q_backtracks_density')}\n")
            md.append(f"  - q(dt_collapse_ratio): {rms.get('q_dt_collapse_ratio')}\n")
            md.append(f"  - q(max_energy_increase): {rms.get('q_max_energy_increase')}\n")
        if g.get("threshold_flags"):
            md.append(f"- Threshold flags: {g['threshold_flags']}\n")
        md.append("- Diagnosis:\n")
        for d in g["diagnosis"]:
            md.append(f"  - {d}\n")
        md.append("- Worst variants:\n")
        for w in g["worst_variants"][:5]:
            md.append(f"  - {w.get('variant')} | n={w.get('n')} pass_rate={_f(w.get('pass_rate')):.3f} fail_codes={w.get('fail_codes')}\n")
        md.append("\n")
    out_md=Path(args.out_md); out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("".join(md), encoding="utf-8")
    print(f"Wrote {out_json} and {out_md}")

if __name__ == "__main__":
    main()
