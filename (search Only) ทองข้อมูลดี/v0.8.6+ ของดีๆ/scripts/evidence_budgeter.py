#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from typing import Dict, Any, List, Tuple

def _f(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def load_json(p: str) -> Dict[str,Any]:
    if not p:
        return {}
    pp = Path(p)
    if not pp.exists():
        return {}
    try:
        return json.loads(pp.read_text(encoding="utf-8"))
    except Exception:
        return {}

def severity_rank(label: str) -> int:
    m = {"INFO": 0, "WARN": 1, "RISK": 2, "BLOCK": 3}
    return m.get(str(label).upper(), 1)

def parse_variant_summary(path: str) -> Dict[str, Dict[str,Any]]:
    """
    Returns per-group aggregate: group_key=band|model|integrator -> {n_total, pass_total, pass_rate}
    """
    out={}
    p=Path(path)
    with p.open("r", encoding="utf-8") as f:
        rdr=csv.DictReader(f)
        for r in rdr:
            band=(r.get("band","") or "UNLABELED").strip() or "UNLABELED"
            model=(r.get("model","") or "").strip()
            integ=(r.get("integrator","") or "").strip()
            gk=f"{band}|{model}|{integ}"
            n=int(float(r.get("n","0") or 0))
            kpass=int(float(r.get("pass","0") or 0))
            ent=out.setdefault(gk, {"n_total":0,"pass_total":0})
            ent["n_total"] += n
            ent["pass_total"] += kpass
    for gk, ent in out.items():
        n=ent["n_total"]
        ent["pass_rate"] = (ent["pass_total"]/n) if n else float("nan")
    return out

def parse_action_targets(action_plan: Dict[str,Any]) -> List[str]:
    targets=[]
    for g in (action_plan.get("groups", []) or []):
        acts = g.get("recommended_actions", []) or []
        if any(str(a.get("type","")).upper() == "INCREASE_EVIDENCE" for a in acts):
            gg = str(g.get("group","")).strip()
            if not gg:
                gg = f"{g.get('band','')}|{g.get('model','')}|{g.get('integrator','')}"
            if gg:
                targets.append(gg)
    # dedupe preserve order
    seen=set()
    out=[]
    for t in targets:
        if t in seen: 
            continue
        seen.add(t)
        out.append(t)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--action_plan_json", required=True)
    ap.add_argument("--variant_summary_csv", required=True)
    ap.add_argument("--triage_json", default="")
    ap.add_argument("--monotonic_report_json", default="")
    ap.add_argument("--determinism_report_json", default="")
    ap.add_argument("--out_json", default="evidence_budget.json")
    ap.add_argument("--out_md", default="evidence_budget.md")

    # knobs
    ap.add_argument("--base_extra_seeds", type=int, default=10)
    ap.add_argument("--extra_seeds_multiplier_per_round", type=float, default=1.7)
    ap.add_argument("--max_rounds", type=int, default=3)
    ap.add_argument("--max_n_for_evidence", type=int, default=500)
    ap.add_argument("--min_n_to_escalate", type=int, default=80)
    ap.add_argument("--max_total_extra_seeds", type=int, default=200)

    # stop thresholds
    ap.add_argument("--stop_on_unstable", action="store_true")
    ap.add_argument("--stop_on_blowup_rate_ge", type=float, default=0.02)
    ap.add_argument("--stop_on_nan_inf_rate_ge", type=float, default=0.02)

    args = ap.parse_args()

    action_plan = load_json(args.action_plan_json)
    triage = load_json(args.triage_json)
    mono = load_json(args.monotonic_report_json)
    det = load_json(args.determinism_report_json)

    targets = parse_action_targets(action_plan)
    vs = parse_variant_summary(args.variant_summary_csv)

    det_status = str(det.get("status","")).upper()
    det_unstable_rate = float(det.get("meta", {}).get("unstable_rate", 0.0) or 0.0)

    # triage lookup for rates
    tri_by_group = {}
    for g in (triage.get("groups", []) or []):
        tri_by_group[str(g.get("group","")).strip()] = g

    # monotonic violations info (optional)
    blocklist = set(mono.get("blocklist_band_model_integrator", []) or [])
    violations = mono.get("violations", []) or []

    global_hold=False
    global_reasons=[]
    if args.stop_on_unstable and det_status == "UNSTABLE":
        global_hold=True
        global_reasons.append(f"determinism UNSTABLE (unstable_rate={det_unstable_rate:.3f})")

    group_plans=[]
    total_budget=0

    for gk in targets:
        ent_vs = vs.get(gk, {"n_total":0, "pass_rate": float("nan")})
        n_total = int(ent_vs.get("n_total",0) or 0)
        pass_rate = float(ent_vs.get("pass_rate", float("nan")))

        tri_g = tri_by_group.get(gk, {})
        rms = tri_g.get("run_metrics_summary", {}) or {}
        blowup_rate = float(rms.get("blowup_rate", 0.0) or 0.0)
        nan_inf_rate = float(rms.get("nan_inf_rate", 0.0) or 0.0)
        sev = str(tri_g.get("severity","") or tri_g.get("severity", "")).upper()
        if not sev:
            # fall back: if in blocklist treat as BLOCK
            sev = "BLOCK" if gk in blocklist else "INFO"

        decision="RUN"
        reasons=[]

        if global_hold:
            decision="STOP"
            reasons.append("global_hold_due_to_determinism")
        if n_total >= args.max_n_for_evidence:
            decision="STOP"
            reasons.append(f"n_total_ge_{args.max_n_for_evidence}")
        if blowup_rate >= args.stop_on_blowup_rate_ge and blowup_rate > 0:
            decision="STOP"
            reasons.append(f"blowup_rate_ge_{args.stop_on_blowup_rate_ge}")
        if nan_inf_rate >= args.stop_on_nan_inf_rate_ge and nan_inf_rate > 0:
            decision="STOP"
            reasons.append(f"nan_inf_rate_ge_{args.stop_on_nan_inf_rate_ge}")

        # schedule
        rounds = 0
        schedule=[]
        if decision == "RUN":
            # If n is tiny, evidence is usually cheap and helpful
            if n_total < args.min_n_to_escalate:
                base = int(round(args.base_extra_seeds * 2))
                reasons.append("low_n_boost")
            else:
                base = int(round(args.base_extra_seeds * 1))
            # severity heuristic: BLOCK groups get slightly more
            if sev == "BLOCK":
                base = int(round(base * 1.2))
            elif sev in ("RISK","WARN"):
                base = int(round(base * 1.0))
            else:
                base = int(round(base * 0.8))

            base = max(1, base)
            rounds = max(1, min(args.max_rounds, 1 + (0 if n_total > args.min_n_to_escalate else 1)))
            for r in range(rounds):
                schedule.append(int(round(base * (args.extra_seeds_multiplier_per_round ** r))))

        planned = sum(schedule)
        total_budget += planned

        group_plans.append({
            "group": gk,
            "decision": decision,
            "severity": sev,
            "n_total": n_total,
            "pass_rate": pass_rate,
            "blowup_rate": blowup_rate,
            "nan_inf_rate": nan_inf_rate,
            "rounds": rounds,
            "extra_seeds_schedule": schedule,
            "reasons": reasons,
            "in_blocklist": (gk in blocklist),
        })

    # enforce global cap (scale down if needed)
    cap = args.max_total_extra_seeds
    if total_budget > cap and cap > 0:
        scale = cap / float(total_budget)
        new_total=0
        for gp in group_plans:
            if gp["decision"] != "RUN":
                continue
            sched = gp["extra_seeds_schedule"]
            sched2 = [max(1, int(math.floor(s*scale))) for s in sched] if sched else []
            if sched2:
                # keep monotone nondecreasing by enforcing
                for i in range(1,len(sched2)):
                    sched2[i] = max(sched2[i], sched2[i-1])
            gp["extra_seeds_schedule"] = sched2
            gp["scaled_by_global_cap"] = True
            new_total += sum(sched2)
        total_budget = new_total
        global_reasons.append(f"scaled_by_global_cap to {cap}")

    payload = {
        "meta": {
            "action_plan_json": str(Path(args.action_plan_json)),
            "variant_summary_csv": str(Path(args.variant_summary_csv)),
            "triage_json": args.triage_json,
            "monotonic_report_json": args.monotonic_report_json,
            "determinism_report_json": args.determinism_report_json,
            "n_targets": len(targets),
            "n_plans": len(group_plans),
            "total_extra_seeds_planned": total_budget,
            "cap_total_extra_seeds": cap,
        },
        "global": {
            "hold_all_evidence": bool(global_hold),
            "reasons": global_reasons,
            "stop_rules": [
                "STOP if determinism UNSTABLE (optional)",
                f"STOP if n_total >= {args.max_n_for_evidence}",
                f"STOP if blowup_rate >= {args.stop_on_blowup_rate_ge}",
                f"STOP if nan_inf_rate >= {args.stop_on_nan_inf_rate_ge}",
            ],
        },
        "groups": sorted(group_plans, key=lambda x: (0 if x["decision"]=="RUN" else 1, -severity_rank(x["severity"]), x["group"])),
        "violations_sample": violations[:50],
    }

    out_json=Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md=[]
    md.append("# Evidence Budget (R0-E25)\n\n")
    md.append(f"- targets: **{payload['meta']['n_targets']}**\n")
    md.append(f"- total_extra_seeds_planned: **{payload['meta']['total_extra_seeds_planned']}** (cap {cap})\n")
    md.append(f"- hold_all_evidence: **{payload['global']['hold_all_evidence']}**\n")
    if payload["global"]["reasons"]:
        md.append(f"- reasons: {payload['global']['reasons']}\n")
    md.append("\n## Stop rules\n")
    for r in payload["global"]["stop_rules"]:
        md.append(f"- {r}\n")
    md.append("\n---\n\n")
    for g in payload["groups"]:
        md.append(f"## {g['group']}\n")
        md.append(f"- decision: **{g['decision']}**\n")
        md.append(f"- severity: {g['severity']} | in_blocklist={g['in_blocklist']}\n")
        md.append(f"- n_total: {g['n_total']} | pass_rate: {g['pass_rate']:.3f} (if available)\n")
        md.append(f"- blowup_rate: {g['blowup_rate']:.3f} | nan_inf_rate: {g['nan_inf_rate']:.3f}\n")
        md.append(f"- rounds: {g['rounds']} | extra_seeds_schedule: {g['extra_seeds_schedule']}\n")
        if g["reasons"]:
            md.append(f"- reasons: {g['reasons']}\n")
        md.append("\n")
    out_md=Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("".join(md), encoding="utf-8")
    print(f"Wrote {out_json} and {out_md}")

if __name__ == "__main__":
    main()
