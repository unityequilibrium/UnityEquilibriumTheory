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
    ap.add_argument("--out", default="boundary_candidates.csv")
    ap.add_argument("--bt_threshold", type=int, default=300, help="backtracks boundary threshold")
    ap.add_argument("--entropy_threshold", type=float, default=0.4, help="basin entropy threshold for multistability suspicion")
    ap.add_argument("--label_mix_threshold", type=float, default=0.8, help="majority label fraction below this => mixed")
    args = ap.parse_args()

    df = pd.read_csv(args.atlas_csv)

    # Use only base variants if variant column exists; otherwise take all.
    if "variant" in df.columns:
        dfb = df[df["variant"]=="base"].copy()
    else:
        dfb = df.copy()

    # If regime_label missing, user must run summarize_atlas first.
    if "regime_label" not in dfb.columns:
        raise SystemExit("atlas.csv missing 'regime_label'. Run summarize_atlas.py first.")

    grp = dfb.groupby(["model","param_id"], as_index=False)
    rows = []
    for (model, pid), g in grp:
        status = g["status"]
        pass_frac = float((status=="PASS").mean()) if len(status)>0 else 0.0
        warn_frac = float((status=="WARN").mean()) if len(status)>0 else 0.0
        fail_frac = float((status=="FAIL").mean()) if len(status)>0 else 0.0
        bt_max = int(np.nanmax(g["backtracks_total"])) if "backtracks_total" in g.columns else 0

        # label distribution
        vc = g["regime_label"].value_counts(normalize=True)
        majority_label = vc.idxmax() if len(vc)>0 else ""
        majority_frac = float(vc.max()) if len(vc)>0 else 0.0
        ent = basin_entropy(g["regime_label"])

        # simple heuristics for boundary candidates
        reasons = []
        if bt_max >= args.bt_threshold:
            reasons.append("STIFFNESS_BACKTRACKS")
        if majority_frac < args.label_mix_threshold:
            reasons.append("LABEL_MIX")
        if ent >= args.entropy_threshold:
            reasons.append("BASIN_ENTROPY")
        if fail_frac > 0:
            reasons.append("HAS_FAILS")

        if len(reasons) == 0:
            continue

        rows.append({
            "model": model,
            "param_id": pid,
            "pass_frac": pass_frac,
            "warn_frac": warn_frac,
            "fail_frac": fail_frac,
            "majority_label": majority_label,
            "majority_frac": majority_frac,
            "basin_entropy": ent,
            "backtracks_max": bt_max,
            "reasons": "|".join(reasons),
        })

    out = pd.DataFrame(rows).sort_values(["backtracks_max","basin_entropy","fail_frac"], ascending=[False,False,False])
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"Wrote {out_path} with {len(out)} candidate param_id rows")

if __name__ == "__main__":
    main()
