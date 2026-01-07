#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

def basin_entropy(labels: pd.Series) -> float:
    labels = labels.dropna()
    if len(labels) == 0:
        return float("nan")
    p = labels.value_counts(normalize=True)
    return float(-(p*np.log(p)).sum())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--atlas_csv", required=True, help="atlas_outputs/atlas.csv")
    ap.add_argument("--out", default="bands.csv")
    ap.add_argument("--variant", default="base")
    ap.add_argument("--safe_pass", type=float, default=0.95)
    ap.add_argument("--safe_majority", type=float, default=0.9)
    ap.add_argument("--safe_backtracks", type=int, default=200)
    ap.add_argument("--interesting_entropy", type=float, default=0.4)
    ap.add_argument("--interesting_majority_max", type=float, default=0.85)
    args = ap.parse_args()

    df = pd.read_csv(args.atlas_csv)
    if "variant" in df.columns:
        df = df[df["variant"]==args.variant].copy()

    if "regime_label" not in df.columns:
        raise SystemExit("atlas.csv missing regime_label. Run summarize_atlas.py first.")

    grp = df.groupby(["model","param_id"], as_index=False)
    rows = []
    for (model, pid), g in grp:
        status = g["status"]
        pass_frac = float((status=="PASS").mean()) if len(status)>0 else 0.0
        warn_frac = float((status=="WARN").mean()) if len(status)>0 else 0.0
        fail_frac = float((status=="FAIL").mean()) if len(status)>0 else 0.0
        bt_max = int(np.nanmax(g["backtracks_total"])) if "backtracks_total" in g.columns else 0

        vc = g["regime_label"].value_counts(normalize=True)
        maj_label = vc.idxmax() if len(vc)>0 else ""
        maj_frac = float(vc.max()) if len(vc)>0 else 0.0
        ent = basin_entropy(g["regime_label"])

        dOmega_mean = float(np.nanmean(g["DeltaOmega"])) if "DeltaOmega" in g.columns else float("nan")

        # Categorize
        if fail_frac > 0 or pass_frac < 0.5:
            band = "UNSAFE"
        else:
            is_safe = (fail_frac==0 and pass_frac>=args.safe_pass and maj_frac>=args.safe_majority and bt_max<=args.safe_backtracks)
            is_interesting = (fail_frac==0 and pass_frac>=0.8 and (ent>=args.interesting_entropy or maj_frac<=args.interesting_majority_max or maj_label=="COARSENING"))
            if is_safe:
                band = "SAFE"
            elif is_interesting:
                band = "INTERESTING"
            else:
                band = "TRANSITION"

        rows.append({
            "model": model,
            "param_id": pid,
            "seeds": int(g["seed"].nunique()) if "seed" in g.columns else len(g),
            "band": band,
            "pass_frac": pass_frac,
            "warn_frac": warn_frac,
            "fail_frac": fail_frac,
            "majority_label": maj_label,
            "majority_frac": maj_frac,
            "basin_entropy": ent,
            "backtracks_max": bt_max,
            "DeltaOmega_mean": dOmega_mean,
        })

    out = pd.DataFrame(rows).sort_values(["band","backtracks_max","basin_entropy"], ascending=[True,False,False])
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"Wrote {out_path} with {len(out)} groups")

if __name__ == "__main__":
    main()
