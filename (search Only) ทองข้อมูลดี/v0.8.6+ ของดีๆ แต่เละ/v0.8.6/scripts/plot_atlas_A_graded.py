#!/usr/bin/env python
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Reuse existing helpers if present in repo; fallback to local copies
try:
    from _plot_common import load_config_for_run, extract_quartic_params, add_density_columns
except Exception:
    import json
    def load_config_for_run(runs_root: Path, run_id: str) -> dict:
        # Try flat path first
        p = runs_root / run_id / "config.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        # Try finding in subdirectories (e.g. model/case_id/run_id)
        matches = list(runs_root.rglob(f"{run_id}/config.json"))
        if matches:
            return json.loads(matches[0].read_text(encoding="utf-8"))
        return {}
    def extract_quartic_params(cfg: dict) -> dict:
        out = {}
        # Check top-level pot or params.pot
        pot = cfg.get("pot")
        if not pot:
            pot = cfg.get("params", {}).get("pot")
            
        if isinstance(pot, dict) and pot.get("type") == "quartic":
            out["a"] = float(pot.get("a", 0.0))
            out["delta"] = float(pot.get("delta") if pot.get("delta") is not None else 0.0)
            out["s"] = float(pot.get("s", 0.0))
        if "kappa" in cfg: out["kappa"] = float(cfg["kappa"])
        if "L" in cfg: out["L"] = float(cfg["L"])
        if "grid" in cfg: out["grid"] = int(cfg["grid"])
        if "dim" in cfg: out["dim"] = int(cfg["dim"])
        return out
    def add_density_columns(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        L = out["L"].fillna(1.0).astype(float) if "L" in out.columns else 1.0
        D = out["dim"].fillna(2).astype(int) if "dim" in out.columns else 2
        vol = (L ** D)
        if "Omega0" in out.columns: out["Omega0_density"] = out["Omega0"] / vol
        if "OmegaT" in out.columns: out["OmegaT_density"] = out["OmegaT"] / vol
        return out

def heatmap(df_piv: pd.DataFrame, title: str, out_path: Path):
    fig = plt.figure()
    ax = plt.gca()
    im = ax.imshow(df_piv.values, aspect="auto", origin="lower")
    ax.set_title(title)
    ax.set_xlabel(df_piv.columns.name or "a")
    ax.set_ylabel(df_piv.index.name or "delta")
    ax.set_xticks(range(len(df_piv.columns)))
    ax.set_xticklabels([str(c) for c in df_piv.columns], rotation=45, ha="right")
    ax.set_yticks(range(len(df_piv.index)))
    ax.set_yticklabels([str(i) for i in df_piv.index])
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)

def main():
    ap = argparse.ArgumentParser(description="Atlas-A report using physics grade (PASS/WARN/FAIL).")
    ap.add_argument("--runs", required=True, help="runs/atlas_A folder")
    ap.add_argument("--out", required=True, help="reports output folder")
    ap.add_argument("--grade_file", default="", help="grades.csv path (default: <runs>/grades.csv)")
    ap.add_argument("--only_grade", default="PASS", choices=["PASS","WARN","FAIL","ALL"], help="Filter by grade")
    args = ap.parse_args()

    runs_root = Path(args.runs)
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    ledger = pd.read_csv(runs_root/"ledger.csv")
    gpath = Path(args.grade_file) if args.grade_file else (runs_root/"grades.csv")
    grades = pd.read_csv(gpath) if gpath.exists() else pd.DataFrame()

    if not grades.empty:
        ledger = ledger.merge(grades[["run_id","grade","reasons"]], on="run_id", how="left")
    else:
        ledger["grade"] = "UNKNOWN"
        ledger["reasons"] = ""

    meta_rows=[]
    for idx, row in ledger.iterrows():
        rid = str(row.get("run_id", ""))
        model = str(row.get("model", ""))
        case_id = str(row.get("case_id", ""))
        
        # Try multiple path patterns
        cfg = {}
        candidates = [
            runs_root / model / case_id / rid / "config.json",  # model/case_id/run_id/
            runs_root / rid / "config.json",                    # run_id/
        ]
        # Also try rglob as fallback
        for cpath in candidates:
            if cpath.exists():
                cfg = json.loads(cpath.read_text(encoding="utf-8"))
                break
        if not cfg:
            matches = list(runs_root.rglob(f"{rid}/config.json"))
            if matches:
                cfg = json.loads(matches[0].read_text(encoding="utf-8"))
        
        p = extract_quartic_params(cfg)
        p["run_id"] = rid
        meta_rows.append(p)
    meta = pd.DataFrame(meta_rows)

    df = ledger.merge(meta, on="run_id", how="left")
    df = add_density_columns(df)
    df.to_csv(out_root/"atlas_A_joined_graded.csv", index=False)

    if args.only_grade != "ALL":
        df = df[df["grade"] == args.only_grade].copy()

    # Only filter by a/delta if they exist and have values
    has_quartic_params = "a" in df.columns and "delta" in df.columns and df["a"].notna().any()
    if has_quartic_params:
        df_plot = df.dropna(subset=["a","delta"]).copy()
        df_plot["a"] = df_plot["a"].astype(float)
        df_plot["delta"] = df_plot["delta"].astype(float)
    else:
        df_plot = df.copy()
        print("WARNING: No quartic parameters (a/delta) found in configs")

    keep = [c for c in ["run_id","case_id","model","status","grade","reasons","a","delta","kappa","s",
                        "Omega0","OmegaT","Omega0_density","OmegaT_density","backtracks_total"] if c in df_plot.columns]
    df_plot[keep].to_csv(out_root/"atlas_summary.csv", index=False)

    for metric in ["OmegaT_density","OmegaT","backtracks_total"]:
        if metric not in df_plot.columns or not has_quartic_params: 
            continue
        piv = df_plot.pivot_table(index="delta", columns="a", values=metric, aggfunc="mean")
        piv.index.name="delta"; piv.columns.name="a"
        heatmap(piv, f"Atlas-A {metric} | grade={args.only_grade}", out_root/f"heatmap_{metric}_grade_{args.only_grade}.png")

    # quick reasons table
    if "reasons" in df_plot.columns:
        top = (df_plot["reasons"].fillna("").astype(str)
                 .str.split("|").explode()
                 .replace("", pd.NA).dropna()
                 .value_counts().head(30).reset_index())
        top.columns = ["reason","count"]
        top.to_csv(out_root/"top_reasons.csv", index=False)

    print(f"Wrote graded report -> {out_root}")

if __name__ == "__main__":
    main()
