#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, re
from pathlib import Path
from typing import Dict, Any, List

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix_in", required=True)
    ap.add_argument("--band_map", required=True)
    ap.add_argument("--matrix_out", required=True)
    ap.add_argument("--key_col", default="base_case_id", help="column in matrix to match band_map.base_case_id")
    ap.add_argument("--band_col", default="band", help="band column name to write")
    ap.add_argument("--extract_from_case_id", action="store_true", help="if set, derive key from case_id by splitting at '__'")
    ap.add_argument("--case_id_col", default="case_id", help="column used when --extract_from_case_id")
    ap.add_argument("--default_band", default="UNLABELED")
    args = ap.parse_args()

    band_of: Dict[str, str] = {}
    with Path(args.band_map).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        if not rdr.fieldnames or "base_case_id" not in rdr.fieldnames or "band" not in rdr.fieldnames:
            raise SystemExit("band_map must have columns: base_case_id, band")
        for r in rdr:
            base = str(r.get("base_case_id","")).strip()
            band = str(r.get("band","")).strip()
            if base:
                band_of[base] = band

    rows: List[Dict[str, Any]] = []
    with Path(args.matrix_in).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames or []
        for r in rdr:
            rows.append(r)

    if not rows:
        raise SystemExit("Empty matrix_in")

    if args.band_col not in cols:
        cols.append(args.band_col)

    def derive_key(r):
        if args.extract_from_case_id:
            cid = str(r.get(args.case_id_col,"")).strip()
            return cid.split("__")[0] if cid else ""
        return str(r.get(args.key_col,"")).strip()

    changed = 0
    for r in rows:
        key = derive_key(r)
        band = band_of.get(key, args.default_band)
        if r.get(args.band_col, "") != band:
            r[args.band_col] = band
            changed += 1

    out = Path(args.matrix_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote {out} | band_applied_rows={changed}")

if __name__ == "__main__":
    main()
