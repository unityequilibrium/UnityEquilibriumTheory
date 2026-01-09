#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo_pack_index", required=True, help="demo_pack/demo_pack_index.csv")
    ap.add_argument("--out", default="demo_pack_report.md")
    args = ap.parse_args()

    df = pd.read_csv(args.demo_pack_index)
    lines = ["# Demo Pack Report", ""]
    if len(df)==0:
        lines.append("_No demos packed._")
    else:
        lines.append(f"- total demos: **{len(df)}**")
        lines.append("")
        # simple table-like section without markdown table
        for _, r in df.iterrows():
            lines.append(f"## {r['model']} — {r['param_id']}")
            lines.append(f"- regime_label: **{r.get('regime_label','')}**")
            lines.append(f"- status: **{r.get('status','')}**")
            lines.append(f"- DeltaOmega: {r.get('DeltaOmega','')}")
            lines.append(f"- backtracks_total: {r.get('backtracks_total','')}")
            lines.append(f"- packed_run_dir: `{r.get('packed_run_dir','')}`")
            lines.append("")
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
