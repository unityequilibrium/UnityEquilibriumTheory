#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from typing import Dict, Any, List

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def _fmt(x: float) -> str:
    return f"{x:.12g}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix_in", required=True, help="atlas matrix csv in")
    ap.add_argument("--matrix_out", required=True, help="atlas matrix csv out")
    ap.add_argument("--band_presets_json", required=True, help="band_dt_presets.json")
    ap.add_argument("--global_presets_json", default="", help="optional dt_presets.json fallback")
    ap.add_argument("--band_col", default="band", help="column in matrix that identifies band")
    ap.add_argument("--model_col", default="model")
    ap.add_argument("--integrator_col", default="integrator")
    ap.add_argument("--dt_col", default="dt")
    ap.add_argument("--mode", choices=["overwrite","fill_missing","cap_to_preset"], default="cap_to_preset")
    ap.add_argument("--default_dt", type=float, default=float("nan"))
    args = ap.parse_args()

    band_presets = json.loads(Path(args.band_presets_json).read_text(encoding="utf-8"))
    global_presets = {}
    if args.global_presets_json:
        global_presets = json.loads(Path(args.global_presets_json).read_text(encoding="utf-8"))

    rows: List[Dict[str, Any]] = []
    with Path(args.matrix_in).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames or []
        for r in rdr:
            rows.append(r)
    if not rows:
        raise SystemExit("Empty matrix_in")
    if args.dt_col not in cols:
        raise SystemExit(f"matrix_in must have '{args.dt_col}' column")

    changed = 0
    missing_band = 0
    missing_preset = 0

    def pick_preset(band: str, model: str, integ: str) -> float:
        # band->model->integ
        v = band_presets.get(band, {}).get(model, {}).get(integ, float("nan"))
        if not (isinstance(v, float) or isinstance(v, int)):
            try:
                v = float(v)
            except Exception:
                v = float("nan")
        if not math.isnan(v):
            return float(v)
        # fallback global
        v2 = global_presets.get(model, {}).get(integ, float("nan"))
        try:
            v2 = float(v2)
        except Exception:
            v2 = float("nan")
        if not math.isnan(v2):
            return float(v2)
        return float(args.default_dt)

    for r in rows:
        band = str(r.get(args.band_col, "")).strip()
        model = str(r.get(args.model_col, "")).strip()
        integ = str(r.get(args.integrator_col, "semiimplicit")).strip()
        dt_old = _f(str(r.get(args.dt_col, "")))

        if not band:
            missing_band += 1
            band = "UNLABELED"

        preset = pick_preset(band, model, integ)
        if math.isnan(preset):
            missing_preset += 1
            continue

        def set_dt(val: float):
            nonlocal changed
            r[args.dt_col] = _fmt(val)
            changed += 1

        if args.mode == "overwrite":
            set_dt(preset)
        elif args.mode == "fill_missing":
            if math.isnan(dt_old) or dt_old <= 0.0:
                set_dt(preset)
        else:  # cap_to_preset
            if math.isnan(dt_old) or dt_old <= 0.0:
                set_dt(preset)
            else:
                set_dt(min(dt_old, preset))

    out = Path(args.matrix_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote {out} | changed={changed} | missing_band_rows={missing_band} | missing_preset_rows={missing_preset}")

if __name__ == "__main__":
    main()
