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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix_in", required=True, help="atlas matrix csv in")
    ap.add_argument("--presets_json", required=True, help="dt_presets.json from extract_dt_presets.py")
    ap.add_argument("--matrix_out", required=True, help="atlas matrix csv out")
    ap.add_argument("--mode", choices=["overwrite","fill_missing","cap_to_preset"], default="overwrite",
                    help="overwrite: always set dt to preset (if available); fill_missing: only if dt empty/0; cap_to_preset: dt=min(dt, preset)")
    ap.add_argument("--default_dt", type=float, default=float("nan"),
                    help="used if preset missing for a row (only affects overwrite/fill_missing when dt is missing)")
    args = ap.parse_args()

    presets = json.loads(Path(args.presets_json).read_text(encoding="utf-8"))

    rows: List[Dict[str, Any]] = []
    with Path(args.matrix_in).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames or []
        for r in rdr:
            rows.append(r)

    if not rows:
        raise SystemExit("Empty matrix_in")

    if "dt" not in cols:
        raise SystemExit("matrix_in must have a 'dt' column")

    changed = 0
    missing_preset = 0
    for r in rows:
        model = str(r.get("model","")).strip()
        integ = str(r.get("integrator","semiimplicit")).strip()
        dt_old = _f(str(r.get("dt","")))
        preset = presets.get(model, {}).get(integ, float("nan"))

        if math.isnan(preset):
            missing_preset += 1
            # optional default
            preset = args.default_dt

        def set_dt(val):
            nonlocal changed
            if math.isnan(val):
                return
            # preserve formatting
            r["dt"] = f"{val:.12g}"
            changed += 1

        if args.mode == "overwrite":
            if not math.isnan(preset):
                set_dt(preset)
        elif args.mode == "fill_missing":
            if (math.isnan(dt_old) or dt_old <= 0.0) and (not math.isnan(preset)):
                set_dt(preset)
        else:  # cap_to_preset
            if not math.isnan(preset):
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

    print(f"Wrote {out} | changed {changed} rows | missing_preset_rows={missing_preset}")

if __name__ == "__main__":
    main()
