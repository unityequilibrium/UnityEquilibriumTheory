#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from typing import Dict, Any

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--presets_in", required=True, help="band_dt_presets*.json or dt_presets*.json")
    ap.add_argument("--updates_csv", required=True, help="preset_update_proposals.csv")
    ap.add_argument("--presets_out", required=True, help="output presets json")
    ap.add_argument("--mode", choices=["band","global"], default="band",
                    help="band: apply rows with (band,model,integrator). global: ignore band column and apply by (model,integrator).")
    ap.add_argument("--min_scale", type=float, default=0.1, help="clamp scales below this")
    ap.add_argument("--max_scale", type=float, default=1.0, help="clamp scales above this")
    ap.add_argument("--apply_only_gate_pass", action="store_true",
                    help="if set, only apply rows where gate_pass_at_recommended_scale==1")
    ap.add_argument("--blocklist_json", default="", help="optional json file with blocklist_band_model_integrator or groups to skip")
    args = ap.parse_args()

    presets = json.loads(Path(args.presets_in).read_text(encoding="utf-8"))

    updates=[]
    with Path(args.updates_csv).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            updates.append(r)
    if not updates:
        raise SystemExit("Empty updates_csv")

    changed=0
    skipped=0
    block = set()
    if args.blocklist_json:
        payload = json.loads(Path(args.blocklist_json).read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            block = set(payload.get("blocklist_band_model_integrator", payload.get("groups", [])) or [])
        elif isinstance(payload, list):
            block = set(payload)


    def clamp(x: float) -> float:
        return max(args.min_scale, min(args.max_scale, x))

    if args.mode == "band":
        # presets[band][model][integrator] = dt
        for u in updates:
            if args.apply_only_gate_pass and str(u.get("gate_pass_at_recommended_scale","0")).strip() not in ("1","True","true"):
                skipped += 1
                continue
            band = (u.get("band","") or "UNLABELED").strip() or "UNLABELED"
            model = (u.get("model","") or "").strip()
            integ = (u.get("integrator","") or "").strip()
            if f"{band}|{model}|{integ}" in block:
                skipped += 1
                continue
            scale = clamp(_f(str(u.get("recommended_scale","nan"))))
            if math.isnan(scale):
                skipped += 1
                continue
            try:
                dt0 = float(presets.get(band, {}).get(model, {}).get(integ, float("nan")))
            except Exception:
                dt0 = float("nan")
            if not (dt0 > 0):
                skipped += 1
                continue
            dt1 = dt0 * scale
            presets.setdefault(band, {}).setdefault(model, {})[integ] = float(dt1)
            changed += 1
    else:
        # presets[model][integrator] = dt
        for u in updates:
            if args.apply_only_gate_pass and str(u.get("gate_pass_at_recommended_scale","0")).strip() not in ("1","True","true"):
                skipped += 1
                continue
            model = (u.get("model","") or "").strip()
            integ = (u.get("integrator","") or "").strip()
            scale = clamp(_f(str(u.get("recommended_scale","nan"))))
            if math.isnan(scale):
                skipped += 1
                continue
            try:
                dt0 = float(presets.get(model, {}).get(integ, float("nan")))
            except Exception:
                dt0 = float("nan")
            if not (dt0 > 0):
                skipped += 1
                continue
            presets.setdefault(model, {})[integ] = float(dt0 * scale)
            changed += 1

    Path(args.presets_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.presets_out).write_text(json.dumps(presets, indent=2), encoding="utf-8")
    print(f"Wrote {args.presets_out} | changed={changed} | skipped={skipped}")

if __name__ == "__main__":
    main()
