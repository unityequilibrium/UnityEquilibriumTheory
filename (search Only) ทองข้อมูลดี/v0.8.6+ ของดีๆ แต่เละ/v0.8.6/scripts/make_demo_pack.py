#!/usr/bin/env python
from __future__ import annotations
import argparse, shutil, json
from pathlib import Path
import pandas as pd
import numpy as np
import subprocess

def _pick_best(g: pd.DataFrame) -> pd.Series:
    # prefer PASS, then minimal backtracks, then larger DeltaOmega
    g2 = g.copy()
    # status rank: PASS=0, WARN=1, FAIL=9
    rank = g2["status"].map({"PASS":0,"WARN":1,"FAIL":9}).fillna(9).to_numpy()
    g2["_rank"] = rank
    g2["_bt"] = pd.to_numeric(g2.get("backtracks_total", 0), errors="coerce").fillna(0).to_numpy()
    g2["_dO"] = pd.to_numeric(g2.get("DeltaOmega", 0.0), errors="coerce").fillna(0.0).to_numpy()
    g2 = g2.sort_values(["_rank","_bt","_dO"], ascending=[True,True,False])
    return g2.iloc[0]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo_selected", required=True, help="demo_selected.csv from demo_select.py")
    ap.add_argument("--atlas_csv", required=True, help="atlas_outputs/atlas.csv")
    ap.add_argument("--runs_root", required=True, help="root folder with run artifacts (e.g., atlas_runs_stage2)")
    ap.add_argument("--out", default="demo_pack", help="output folder for demo pack")
    ap.add_argument("--variant", default="base", help="variant to use if column exists")
    ap.add_argument("--make_plots", action="store_true", help="run plot_run.py for each packed run")
    args = ap.parse_args()

    demo = pd.read_csv(args.demo_selected)
    atlas = pd.read_csv(args.atlas_csv)

    if "variant" in atlas.columns:
        atlas = atlas[atlas["variant"]==args.variant].copy()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    runs_root = Path(args.runs_root)

    packed_rows = []
    for _, r in demo.iterrows():
        model = str(r["model"])
        pid = str(r["param_id"])
        g = atlas[(atlas["model"]==model) & (atlas["param_id"]==pid)].copy()
        if len(g)==0:
            continue
        best = _pick_best(g)
        run_dir = None
        if "run_dir" in best and isinstance(best["run_dir"], str) and best["run_dir"]:
            run_dir = Path(best["run_dir"])
        else:
            # reconstruct expected path
            case_id = str(best["case_id"])
            run_id = str(best["run_id"])
            run_dir = runs_root / model / case_id / run_id

        if not run_dir.exists():
            # try to find by run_id
            rid = str(best["run_id"])
            hits = list(runs_root.rglob(f"{rid}/summary.json"))
            if hits:
                run_dir = hits[0].parent
        if not run_dir.exists():
            continue

        dest = out_root / model / pid / str(best["run_id"])
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(run_dir, dest)

        packed_rows.append({
            "model": model,
            "param_id": pid,
            "case_id": str(best["case_id"]),
            "run_id": str(best["run_id"]),
            "status": str(best.get("status","")),
            "regime_label": str(best.get("regime_label","")),
            "DeltaOmega": float(best.get("DeltaOmega", np.nan)),
            "backtracks_total": int(best.get("backtracks_total", 0)),
            "packed_run_dir": str(dest),
        })

        if args.make_plots:
            # call plot_run.py from scripts folder relative to this file
            here = Path(__file__).resolve().parent
            plot_script = here / "plot_run.py"
            try:
                subprocess.run(["python", str(plot_script), "--run_dir", str(dest)], check=False)
            except Exception:
                pass

    pack_index = pd.DataFrame(packed_rows)
    pack_index.to_csv(out_root / "demo_pack_index.csv", index=False)

    # Create a markdown index
    md_lines = ["# Demo Pack Index", ""]
    for row in packed_rows:
        md_lines.append(f"## {row['model']} — {row['param_id']}")
        md_lines.append(f"- run_id: `{row['run_id']}`")
        md_lines.append(f"- case_id: `{row['case_id']}`")
        md_lines.append(f"- status: **{row['status']}**")
        md_lines.append(f"- regime_label: **{row['regime_label']}**")
        md_lines.append(f"- DeltaOmega: {row['DeltaOmega']}")
        md_lines.append(f"- backtracks_total: {row['backtracks_total']}")
        md_lines.append(f"- folder: `{row['packed_run_dir']}`")
        md_lines.append("")
    (out_root / "README_DEMOS.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote demo pack to {out_root} with {len(packed_rows)} runs")

if __name__ == "__main__":
    main()
