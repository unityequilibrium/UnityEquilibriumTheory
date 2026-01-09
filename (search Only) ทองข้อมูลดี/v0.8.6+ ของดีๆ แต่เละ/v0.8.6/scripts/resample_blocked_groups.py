#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, hashlib, math
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set

def parse_list(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]

def hseed(s: str) -> int:
    # deterministic 32-bit
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:8], 16)

def integrator_in_list(integrator: str, integrators_field: str) -> bool:
    integrator = (integrator or '').strip()
    lst = [x.strip() for x in (integrators_field or '').split(';') if x.strip()]
    return (integrator in lst) if integrator else False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrices", required=True, help="semicolon-separated matrix csv files to source rows from")
    ap.add_argument("--blocklist_json", required=True, help="monotonic_report.json containing blocklist_band_model_integrator")
    ap.add_argument("--out", default="resample_matrix.csv")
    ap.add_argument("--extra_seeds", type=int, default=10, help="how many new seeds per existing row")
    ap.add_argument("--seed_start", type=int, default=100000, help="base seed offset")
    ap.add_argument("--seed_span", type=int, default=100000000, help="span for hashing seeds")
    ap.add_argument("--dedupe_ledger", default="", help="optional semicolon-separated ledgers to avoid duplicate seeds")
    ap.add_argument("--max_rows", type=int, default=20000)
    args = ap.parse_args()

    block = json.loads(Path(args.blocklist_json).read_text(encoding="utf-8"))
    bl = set(block.get("blocklist_band_model_integrator", block.get("groups", [])) or [])
    bl_map = {}
    for g in bl:
        parts = g.split("|")
        if len(parts) >= 3:
            bm = "|".join(parts[:2])
            integ = parts[2]
            bl_map.setdefault(bm, set()).add(integ)
    if not bl:
        raise SystemExit("Blocklist empty; nothing to resample")

    # Load existing seeds from ledgers if provided
    existing: Set[Tuple[str,str,str,str,int]] = set()
    for led in parse_list(args.dedupe_ledger):
        p = Path(led)
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                base = (r.get("base_case_id","") or "").strip()
                model = (r.get("model","") or "").strip()
                integ = (r.get("integrator","") or "").strip()
                dt = (r.get("dt","") or "").strip()
                try:
                    seed = int(float(r.get("seed","0") or 0))
                except Exception:
                    seed = 0
                existing.add((base, model, integ, dt, seed))

    # Read source matrices and keep rows in blocklisted groups
    src_rows=[]
    cols=None
    for m in parse_list(args.matrices):
        p = Path(m)
        if not p.exists():
            raise SystemExit(f"Missing matrix: {p}")
        with p.open("r", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            cols = cols or rdr.fieldnames
            for r in rdr:
                band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
                model = (r.get("model","") or "").strip()
                integrators_field = (r.get("integrators","") or "").strip()
                bm = f"{band}|{model}"
                if bm in bl_map:
                    for integ in bl_map[bm]:
                        if integrator_in_list(integ, integrators_field):
                            rr = dict(r)
                            rr["_blocked_integrator"] = integ
                            src_rows.append(rr)
                            break

    if not src_rows:
        raise SystemExit("No rows found in matrices for blocklist groups")

    out_rows=[]
    used=0
    for r in src_rows:
        # Determine dt value from dt_list if single; else, cannot dedupe precisely; still okay.
        dt_list = (r.get("dt_list","") or "").strip()
        dt = dt_list.split(";")[0].strip() if dt_list else ""
        base = (r.get("base_case_id","") or "").strip()
        model = (r.get("model","") or "").strip()
        integrators_field = (r.get("integrators","") or "").strip()
        blocked_integ = (r.get("_blocked_integrator","") or "").strip()
        integrator_for_key = blocked_integ if blocked_integ else integrators_field
        # Existing seed list in matrix may already include this seed; we'll avoid duplicates by ledger set if provided.
        try:
            seed0 = int(float((r.get("seed","0") or 0)))
        except Exception:
            seed0 = 0

        # Generate extra seeds deterministically
        for j in range(args.extra_seeds):
            seed = args.seed_start + (hseed(f"{base}|{model}|{integrator_for_key}|{dt}|{seed0}|{j}") % args.seed_span)
            # avoid same as seed0
            if seed == seed0:
                seed += 1
            if existing and (base, model, integrator_for_key, dt, seed) in existing:
                continue
            rr = dict(r)
            rr["seed"] = str(seed)
            out_rows.append(rr)
            used += 1
            if used >= args.max_rows:
                break
        if used >= args.max_rows:
            break

    if not out_rows:
        raise SystemExit("No new rows generated (maybe all seeds duplicated)")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # use columns from first out row if cols None
    fieldnames = cols or list(out_rows[0].keys())
    # ensure all keys exist
    for k in out_rows[0].keys():
        if k not in fieldnames:
            fieldnames.append(k)

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rr in out_rows:
            w.writerow({k: rr.get(k,"") for k in fieldnames})

    print(f"Wrote {out} rows={len(out_rows)} block_groups={len(bl)}")

if __name__ == "__main__":
    main()
