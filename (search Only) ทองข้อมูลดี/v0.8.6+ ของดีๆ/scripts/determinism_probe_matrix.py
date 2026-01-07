#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from typing import List

def parse_list(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]

def integrator_in_list(integrator: str, integrators_field: str) -> bool:
    integrator = (integrator or "").strip()
    lst = [x.strip() for x in (integrators_field or "").split(";") if x.strip()]
    return (integrator in lst) if integrator else False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrices", required=True, help="semicolon-separated source matrix csvs")
    ap.add_argument("--groups_json", required=True, help="json with groups or blocklist_band_model_integrator")
    ap.add_argument("--out", default="determinism_probe_matrix.csv")
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--max_base_rows", type=int, default=200)
    args = ap.parse_args()

    payload = json.loads(Path(args.groups_json).read_text(encoding="utf-8"))
    groups = payload.get("blocklist_band_model_integrator", payload.get("groups", [])) if isinstance(payload, dict) else payload
    groups = [g for g in (groups or []) if isinstance(g, str)]
    if not groups:
        raise SystemExit("No groups in groups_json")

    bl_map = {}
    for g in groups:
        parts = g.split("|")
        if len(parts) >= 3:
            bm = "|".join(parts[:2])
            bl_map.setdefault(bm, set()).add(parts[2])

    src=[]
    fieldnames=None
    for m in parse_list(args.matrices):
        p=Path(m)
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8") as f:
            rdr=csv.DictReader(f)
            fieldnames = fieldnames or rdr.fieldnames
            for r in rdr:
                band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
                model = (r.get("model","") or "").strip()
                integ_field = (r.get("integrators","") or "").strip()
                bm = f"{band}|{model}"
                if bm in bl_map:
                    if any(integrator_in_list(i, integ_field) for i in bl_map[bm]):
                        src.append(r)

    if not src:
        raise SystemExit("No base rows matched groups in matrices")

    seen=set()
    base_rows=[]
    for r in src:
        key=(r.get("base_case_id",""), r.get("model",""), r.get("band",""),
             r.get("params",""), r.get("N",""), r.get("L",""), r.get("T",""),
             r.get("dt_list",""), r.get("integrators",""), r.get("seed",""))
        if key in seen:
            continue
        seen.add(key)
        base_rows.append(r)
        if len(base_rows) >= args.max_base_rows:
            break

    out_rows=[]
    for r in base_rows:
        for k in range(args.repeats):
            rr=dict(r)
            rr["probe_tag"]=f"rep{k+1:02d}"
            out_rows.append(rr)

    out=Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fn = fieldnames or list(out_rows[0].keys())
    if "probe_tag" not in fn:
        fn = fn + ["probe_tag"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        for r in out_rows:
            w.writerow({k: r.get(k,"") for k in fn})

    print(f"Wrote {out} rows={len(out_rows)} base_rows={len(base_rows)} repeats={args.repeats}")

if __name__ == "__main__":
    main()
