# scripts/merge_summaries.py
import argparse
import os
import pandas as pd
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True, help="List of input CSV files")
    ap.add_argument("--out", required=True, help="Output CSV file path")
    args = ap.parse_args()

    rows = []
    for p_str in args.inputs:
        p = Path(p_str)
        if not p.exists():
            continue
        try:
            df = pd.read_csv(p)
            # Add source identifier (similar to inline script logic)
            tag = p.name.replace("_UET_final_summary.csv", "").replace(".csv", "")
            df["run_set"] = tag
            rows.append(df)
        except Exception as e:
            print(f"Skipping {p}: {e}")

    if not rows:
        print("No valid data to merge.")
        return

    out_df = pd.concat(rows, ignore_index=True)
    
    # Ensure output directory exists
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    
    out_df.to_csv(args.out, index=False)
    print(f"Wrote: {args.out} rows={len(out_df)} cols={len(out_df.columns)}")

if __name__ == "__main__":
    main()
