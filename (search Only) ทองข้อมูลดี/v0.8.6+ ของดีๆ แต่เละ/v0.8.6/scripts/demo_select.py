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
    ap.add_argument("--atlas_csv", required=True, help="atlas_outputs/atlas.csv (one row per run)")
    ap.add_argument("--out", default="demo_candidates.csv")
    ap.add_argument("--variant", default="base", help="use only this variant if column exists")
    ap.add_argument("--min_pass_frac", type=float, default=1.0, help="minimum PASS fraction (WARN excluded)")
    ap.add_argument("--max_warn_frac", type=float, default=0.2)
    ap.add_argument("--max_backtracks", type=int, default=200)
    ap.add_argument("--min_majority_frac", type=float, default=0.9)
    ap.add_argument("--max_entropy", type=float, default=0.2)
    ap.add_argument("--min_deltaomega", type=float, default=1e-6, help="minimum mean DeltaOmega (non-trivial dynamics)")
    ap.add_argument("--top_k", type=int, default=10)
    args = ap.parse_args()

    df = pd.read_csv(args.atlas_csv)

    # Filter to base variant if present
    if "variant" in df.columns:
        df = df[df["variant"] == args.variant].copy()

    # Require regime_label
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
        majority_label = vc.idxmax() if len(vc)>0 else ""
        majority_frac = float(vc.max()) if len(vc)>0 else 0.0
        ent = basin_entropy(g["regime_label"])

        dOmega_mean = float(np.nanmean(g["DeltaOmega"])) if "DeltaOmega" in g.columns else float("nan")
        dOmega_std = float(np.nanstd(g["DeltaOmega"])) if "DeltaOmega" in g.columns else float("nan")

        # Gate
        ok = True
        reasons = []
        if fail_frac > 0:
            ok = False; reasons.append("HAS_FAILS")
        if pass_frac < args.min_pass_frac:
            ok = False; reasons.append("LOW_PASS_FRAC")
        if warn_frac > args.max_warn_frac:
            ok = False; reasons.append("HIGH_WARN_FRAC")
        if bt_max > args.max_backtracks:
            ok = False; reasons.append("HIGH_BACKTRACKS")
        if majority_frac < args.min_majority_frac:
            ok = False; reasons.append("LOW_MAJORITY_FRAC")
        if ent > args.max_entropy:
            ok = False; reasons.append("HIGH_ENTROPY")
        if np.isnan(dOmega_mean) or dOmega_mean < args.min_deltaomega:
            ok = False; reasons.append("LOW_DELTAOMEGA")

        rows.append({
            "model": model,
            "param_id": pid,
            "seeds": int(g["seed"].nunique()) if "seed" in g.columns else len(g),
            "pass_frac": pass_frac,
            "warn_frac": warn_frac,
            "fail_frac": fail_frac,
            "majority_label": majority_label,
            "majority_frac": majority_frac,
            "basin_entropy": ent,
            "backtracks_max": bt_max,
            "DeltaOmega_mean": dOmega_mean,
            "DeltaOmega_std": dOmega_std,
            "gate_ok": int(ok),
            "gate_reasons": "|".join(reasons),
        })

    out = pd.DataFrame(rows)
    # Rank: prefer larger DeltaOmega, penalize backtracks and entropy
    out["score"] = out["DeltaOmega_mean"].fillna(0.0) - 1e-6*out["backtracks_max"].fillna(0.0) - 0.1*out["basin_entropy"].fillna(0.0)

    out_sorted = out.sort_values(["gate_ok","score"], ascending=[False,False])
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_sorted.to_csv(out_path, index=False)

    # Top-K gated selection
    top = out_sorted[out_sorted["gate_ok"]==1].head(args.top_k).copy()
    sel_path = out_path.with_name(out_path.stem.replace("candidates","selected") + ".csv")
    top.to_csv(sel_path, index=False)

    print(f"Wrote {out_path} ({len(out_sorted)} groups)")
    print(f"Wrote {sel_path} (top {len(top)} gated demo groups)")

if __name__ == "__main__":
    main()
