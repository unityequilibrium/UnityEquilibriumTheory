#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math, re
from pathlib import Path
from typing import Dict, Any, List, Tuple

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def parse_dt_scale(variant: str) -> float:
    """
    Extract dt scale from variant string.
    Expected patterns:
      - ..._dt0.5
      - ..._dt0p5 (dot replaced)
      - ..._dt1
    """
    v = (variant or "").strip()
    m = re.search(r"_dt([0-9]+(?:[p\.][0-9]+)?)", v)
    if not m:
        return float("nan")
    s = m.group(1).replace("p",".")
    try:
        return float(s)
    except Exception:
        return float("nan")

def pick_best_scale(rows: List[Dict[str,Any]], min_pass_rate: float, min_ci_lo: float) -> Tuple[float, Dict[str,Any]]:
    """
    Choose smallest dt scale that passes gate; if none passes, choose smallest available scale.
    Assumes each row has pass_rate, ci_lo, variant.
    """
    candidates = []
    for r in rows:
        sc = parse_dt_scale(str(r.get("variant","")))
        pr = _f(str(r.get("pass_rate","nan")))
        lo = _f(str(r.get("ci_lo","nan")))
        n = int(float(str(r.get("n","0")))) if str(r.get("n","")).strip() else 0
        candidates.append((sc, pr, lo, n, r))
    candidates = [c for c in candidates if not math.isnan(c[0]) and c[0] > 0]
    if not candidates:
        return (float("nan"), {})
    # passing set
    passing = [c for c in candidates if c[1] >= min_pass_rate and c[2] >= min_ci_lo]
    if passing:
        passing.sort(key=lambda x: (x[0], -x[3]))  # smallest scale, more samples
        sc, pr, lo, n, r = passing[0]
        r2 = dict(r)
        r2.update({"dt_scale": sc, "gate_pass": 1})
        return (sc, r2)
    # none passes -> choose smallest scale available
    candidates.sort(key=lambda x: (x[0], -x[3]))
    sc, pr, lo, n, r = candidates[0]
    r2 = dict(r)
    r2.update({"dt_scale": sc, "gate_pass": 0})
    return (sc, r2)

def load_band_presets(path: str) -> Dict[str,Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"presets not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))

def get_dt_from_presets(presets: Dict[str,Any], band: str, model: str, integrator: str) -> float:
    try:
        v = presets.get(band, {}).get(model, {}).get(integrator, float("nan"))
        return float(v)
    except Exception:
        return float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant_summary_csv", required=True, help="stress_summary.csv grouped by band_model_integrator_variant")
    ap.add_argument("--out", default="preset_update_proposals.csv")
    ap.add_argument("--band_presets_json", default="", help="band_dt_presets*.json for reference dt values (optional)")
    ap.add_argument("--min_pass_rate", type=float, default=0.95)
    ap.add_argument("--min_ci_lo", type=float, default=0.90)
    ap.add_argument("--prefer_keep_if_pass", action="store_true",
                    help="If dt_scale=1.0 passes, force recommendation=1.0 even if smaller scale also passes.")
    ap.add_argument("--only_groups_json", default="", help="optional json file with {groups:[...]} where group keys are band|model|integrator")
    args = ap.parse_args()

    band_presets = load_band_presets(args.band_presets_json)
    only_groups = None
    if args.only_groups_json:
        only_groups = set(json.loads(Path(args.only_groups_json).read_text(encoding="utf-8")).get("groups", []))

    rows=[]
    with Path(args.variant_summary_csv).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    if not rows:
        raise SystemExit("Empty summary csv")

    # group by (band, model, integrator)
    by_key: Dict[Tuple[str,str,str], List[Dict[str,Any]]] = {}
    for r in rows:
        band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
        model = (r.get("model","") or "").strip()
        integ = (r.get("integrator","") or "").strip()
        variant = (r.get("variant","") or "BASE").strip() or "BASE"
        if args.variant_summary_csv and variant == "BASE":
            # In adaptive runs, should have variant. If BASE, still allow but dt_scale may be NaN.
            pass
        by_key.setdefault((band, model, integ), []).append(r)

    out_rows=[]
    for (band, model, integ), rs in sorted(by_key.items()):
        if only_groups is not None:
            if f"{band}|{model}|{integ}" not in only_groups:
                continue

        # optional "keep if dt=1 passes"
        if args.prefer_keep_if_pass:
            keep = [r for r in rs if abs(parse_dt_scale(str(r.get("variant","")))-1.0) < 1e-12]
            if keep:
                pr = _f(str(keep[0].get("pass_rate","nan")))
                lo = _f(str(keep[0].get("ci_lo","nan")))
                if pr >= args.min_pass_rate and lo >= args.min_ci_lo:
                    chosen = dict(keep[0]); chosen.update({"dt_scale": 1.0, "gate_pass": 1})
                    best_scale = 1.0
                else:
                    best_scale, chosen = pick_best_scale(rs, args.min_pass_rate, args.min_ci_lo)
            else:
                best_scale, chosen = pick_best_scale(rs, args.min_pass_rate, args.min_ci_lo)
        else:
            best_scale, chosen = pick_best_scale(rs, args.min_pass_rate, args.min_ci_lo)

        base_dt = get_dt_from_presets(band_presets, band, model, integ) if band_presets else float("nan")
        rec_dt = base_dt * best_scale if (not math.isnan(base_dt) and not math.isnan(best_scale)) else float("nan")

        reason = "passes_gate" if int(chosen.get("gate_pass",0))==1 else "no_variant_passes_gate_choose_smallest_scale"
        out_rows.append({
            "band": band,
            "model": model,
            "integrator": integ,
            "recommended_scale": best_scale,
            "base_dt_from_presets": base_dt,
            "recommended_dt": rec_dt,
            "gate_pass_at_recommended_scale": int(chosen.get("gate_pass",0)),
            "evidence_variant": chosen.get("variant",""),
            "evidence_pass_rate": _f(str(chosen.get("pass_rate","nan"))),
            "evidence_ci_lo": _f(str(chosen.get("ci_lo","nan"))),
            "evidence_n": int(float(str(chosen.get("n","0")))) if str(chosen.get("n","")).strip() else 0,
            "reason": reason,
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    print(f"Wrote {out} (rows={len(out_rows)})")

if __name__ == "__main__":
    main()
