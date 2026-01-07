#!/usr/bin/env python
from __future__ import annotations
import argparse, csv
from pathlib import Path
from typing import List, Dict, Any

def parse_list(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix_in", required=True, help="dt_ladder_matrix.csv")
    ap.add_argument("--matrix_out", required=True, help="output csv with expanded seeds")
    ap.add_argument("--seeds", required=True, help="semicolon-separated seeds, e.g. 0;1;2;3;4")
    ap.add_argument("--seed_col", default="seed")
    ap.add_argument("--suffix_mode", choices=["append_seed","none"], default="append_seed",
                    help="append_seed: base_case_id -> base_case_id__s<seed> (unique ids)")
    args = ap.parse_args()

    seeds = [int(x) for x in parse_list(args.seeds)]
    rows: List[Dict[str, Any]] = []

    with Path(args.matrix_in).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames or []
        if args.seed_col not in cols:
            cols.append(args.seed_col)
        for r in rdr:
            rows.append(r)

    out_rows: List[Dict[str, Any]] = []
    for r in rows:
        base_id = (r.get("base_case_id","") or "").strip()
        for s in seeds:
            rr = dict(r)
            rr[args.seed_col] = str(s)
            if args.suffix_mode == "append_seed" and base_id:
                rr["base_case_id"] = f"{base_id}__s{s}"
            out_rows.append(rr)

    out = Path(args.matrix_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"Wrote {out} (rows={len(out_rows)})")

if __name__ == "__main__":
    main()
