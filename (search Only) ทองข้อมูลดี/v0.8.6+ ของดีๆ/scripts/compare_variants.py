#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, help="ledger_tier1.csv path")
    args = ap.parse_args()

    df = pd.read_csv(args.ledger)
    # Compare base vs dt_half by case_id
    base = df[df["variant"]=="base"].set_index("case_id")
    half = df[df["variant"]=="dt_half"].set_index("case_id")
    common = base.index.intersection(half.index)

    rows = []
    for cid in common:
        b = base.loc[cid]
        h = half.loc[cid]
        rows.append({
            "case_id": cid,
            "model": b["model"],
            "status_base": b["status"],
            "status_dt_half": h["status"],
            "OmegaT_base": b["OmegaT"],
            "OmegaT_dt_half": h["OmegaT"],
            "backtracks_base": b["backtracks_total"],
            "backtracks_dt_half": h["backtracks_total"],
        })
    out = pd.DataFrame(rows)
    print(out.to_string(index=False))

if __name__ == "__main__":
    main()
