#!/usr/bin/env python
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Dict, Any, List, Tuple

def severity_rank(label: str) -> int:
    m = {"INFO": 0, "WARN": 1, "RISK": 2, "BLOCK": 3}
    return m.get(str(label).upper(), 1)

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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--triage_json", required=True)
    ap.add_argument("--monotonic_report_json", default="")
    ap.add_argument("--determinism_report_json", default="")
    ap.add_argument("--out_json", default="action_plan.json")
    ap.add_argument("--out_md", default="action_plan.md")
    ap.add_argument("--hold_apply_if_unstable", action="store_true")
    ap.add_argument("--hold_apply_if_blowup_rate_ge", type=float, default=0.02)
    ap.add_argument("--hold_apply_if_nan_inf_rate_ge", type=float, default=0.02)
    ap.add_argument("--energy_dt_multiplier", type=float, default=0.7)
    ap.add_argument("--blowup_dt_multiplier", type=float, default=0.5)
    ap.add_argument("--naninf_dt_multiplier", type=float, default=0.5)
    ap.add_argument("--backtrack_dt_multiplier", type=float, default=0.85)
    ap.add_argument("--max_actions_per_group", type=int, default=6)
    ap.add_argument("--top_k_failcodes", type=int, default=5)
    args = ap.parse_args()

    tri = load_json(args.triage_json)
    mono = load_json(args.monotonic_report_json)
    det = load_json(args.determinism_report_json)

    blocklist = set(mono.get("blocklist_band_model_integrator", []) or [])
    det_status = str(det.get("status","")).upper()
    det_unstable_rate = float(det.get("meta", {}).get("unstable_rate", 0.0) or 0.0)

    global_hold = False
    global_reasons: List[str] = []
    if args.hold_apply_if_unstable and det_status == "UNSTABLE":
        global_hold = True
        global_reasons.append(f"determinism_report.status=UNSTABLE (unstable_rate={det_unstable_rate:.3f})")

    groups_out=[]
    worst_sev="INFO"

    for g in tri.get("groups", []) or []:
        group = str(g.get("group","")).strip()
        band = str(g.get("band","")).strip()
        model = str(g.get("model","")).strip()
        integ = str(g.get("integrator","")).strip()

        sev="INFO"
        reasons=[]
        actions=[]

        if group in blocklist:
            sev="BLOCK"
            reasons.append("monotonic_blocklist")
            actions.append({"type":"INCREASE_EVIDENCE","note":"Increase seeds/jitters/cases for this group until monotonic OK."})

        vs_fc = g.get("variant_summary", {}).get("top_fail_codes", []) or []
        rs_fc = g.get("run_metrics_summary", {}).get("top_fail_codes", []) or []
        fc = rs_fc if rs_fc else vs_fc
        fc = [(str(a), int(b)) for a,b in (fc or [])][:args.top_k_failcodes]
        fc_names = [c for c,_ in fc]

        rms = g.get("run_metrics_summary", {}) or {}
        blowup_rate = float(rms.get("blowup_rate", 0.0) or 0.0)
        nan_inf_rate = float(rms.get("nan_inf_rate", 0.0) or 0.0)
        q_bd = (rms.get("q_backtracks_density", {}) or {}).get("q90", None)
        q_dc = (rms.get("q_dt_collapse_ratio", {}) or {}).get("q10", None)

        if ("BLOWUP" in fc_names) or (blowup_rate >= args.hold_apply_if_blowup_rate_ge and blowup_rate > 0):
            if severity_rank(sev) < severity_rank("BLOCK"):
                sev="BLOCK"
            reasons.append(f"blowup_detected (rate={blowup_rate:.3f})")
            actions.append({"type":"DECREASE_DT_PRESET","multiplier":args.blowup_dt_multiplier,
                            "note":"Reduce dt preset; investigate caps/potentials; keep conservative policy."})
            actions.append({"type":"ENABLE_NUMERIC_GUARDS","note":"Consider enabling/clamping numeric guards (caps, safe exp/log, bounded potentials) to prevent blowups."})
            if blowup_rate >= args.hold_apply_if_blowup_rate_ge:
                global_hold=True
                global_reasons.append(f"blowup_rate_ge_{args.hold_apply_if_blowup_rate_ge} in {group}")

        if ("NAN_INF" in fc_names) or (nan_inf_rate >= args.hold_apply_if_nan_inf_rate_ge and nan_inf_rate > 0):
            if severity_rank(sev) < severity_rank("BLOCK"):
                sev="BLOCK"
            reasons.append(f"nan_inf_detected (rate={nan_inf_rate:.3f})")
            actions.append({"type":"DECREASE_DT_PRESET","multiplier":args.naninf_dt_multiplier,
                            "note":"Reduce dt preset; check overflow/underflow; verify stability caps."})
            actions.append({"type":"ENABLE_NUMERIC_GUARDS","note":"Consider enabling/clamping numeric guards (caps, safe exp/log) to avoid NAN/INF propagation."})
            if nan_inf_rate >= args.hold_apply_if_nan_inf_rate_ge:
                global_hold=True
                global_reasons.append(f"nan_inf_rate_ge_{args.hold_apply_if_nan_inf_rate_ge} in {group}")

        if "ENERGY_INCREASE" in fc_names:
            if severity_rank(sev) < severity_rank("RISK"):
                sev="RISK"
            reasons.append("energy_increase_failures")
            actions.append({"type":"DECREASE_DT_PRESET","multiplier":args.energy_dt_multiplier,
                            "note":"Energy monotonicity failures; smaller dt often fixes; tune backtracking/tolerances."})
            actions.append({"type":"TUNE_BACKTRACKING","note":"If dt reduction is insufficient, consider increasing backtracking budget / tightening acceptance checks / adjusting tolerances."})

        try:
            if q_bd is not None and float(q_bd) > 0.5:
                if severity_rank(sev) < severity_rank("WARN"):
                    sev="WARN"
                reasons.append(f"high_backtracks_density_q90={float(q_bd):.3f}")
                actions.append({"type":"DECREASE_DT_PRESET","multiplier":args.backtrack_dt_multiplier,
                                "note":"High backtracking density; slightly smaller dt improves acceptance and speed."})
                actions.append({"type":"TUNE_BACKTRACKING","note":"Backtracking is doing heavy work; consider raising max_backtracks or revisiting acceptance thresholds."})
        except Exception:
            pass

        try:
            if q_dc is not None and float(q_dc) < 0.2:
                if severity_rank(sev) < severity_rank("WARN"):
                    sev="WARN"
                reasons.append(f"strong_dt_collapse_q10={float(q_dc):.3f}")
                actions.append({"type":"DECREASE_DT_PRESET","multiplier":args.backtrack_dt_multiplier,
                                "note":"Severe dt collapse; choose smaller preset dt to avoid repeated backtracks."})
        except Exception:
            pass

        if det_status == "UNSTABLE":
            if severity_rank(sev) < severity_rank("BLOCK"):
                sev="BLOCK"
            reasons.append("global_nondeterminism_suspected")
            actions.append({"type":"DETERMINISM_DIAGNOSE",
                            "note":"Determinism probe found inconsistent outcomes; fix solver determinism before auto-apply."})

        if len(actions) > args.max_actions_per_group:
            actions = actions[:args.max_actions_per_group]

        groups_out.append({
            "group": group or f"{band}|{model}|{integ}",
            "band": band, "model": model, "integrator": integ,
            "severity": sev,
            "dominant_fail_codes": fc,
            "reasons": reasons,
            "recommended_actions": actions
        })
        if severity_rank(sev) > severity_rank(worst_sev):
            worst_sev = sev

    payload = {
        "meta": {
            "triage_json": str(Path(args.triage_json)),
            "monotonic_report_json": args.monotonic_report_json,
            "determinism_report_json": args.determinism_report_json,
            "n_groups": len(groups_out),
            "worst_severity": worst_sev
        },
        "global": {
            "hold_apply": bool(global_hold),
            "reasons": global_reasons
        },
        "groups": sorted(groups_out, key=lambda r: (-severity_rank(r["severity"]), r["group"]))
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md=[]
    md.append("# Action Plan (R0-E23)\n\n")
    md.append(f"- worst_severity: **{payload['meta']['worst_severity']}**\n")
    md.append(f"- hold_apply: **{payload['global']['hold_apply']}**\n")
    if payload["global"]["reasons"]:
        md.append(f"- reasons: {payload['global']['reasons']}\n")
    md.append("\n---\n\n")
    for g in payload["groups"]:
        md.append(f"## {g['group']}\n")
        md.append(f"- severity: **{g['severity']}**\n")
        md.append(f"- dominant_fail_codes: {g['dominant_fail_codes']}\n")
        if g["reasons"]:
            md.append(f"- reasons: {g['reasons']}\n")
        md.append("- recommended_actions:\n")
        for a in g["recommended_actions"]:
            md.append(f"  - {a}\n")
        md.append("\n")

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("".join(md), encoding="utf-8")
    print(f"Wrote {out_json} and {out_md} | hold_apply={global_hold} worst={worst_sev}")

if __name__ == "__main__":
    main()
