#!/usr/bin/env python
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

try:
    from _plot_common import load_config_for_run, extract_quartic_params, add_density_columns
except Exception:
    import json
    def load_config_for_run(runs_root: Path, run_id: str) -> dict:
        p = runs_root / run_id / "config.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    def extract_quartic_params(cfg: dict) -> dict:
        out = {}
        if isinstance(cfg.get("pot"), dict) and cfg["pot"].get("type") == "quartic":
            out["a"] = float(cfg["pot"].get("a", 0.0))
            out["delta"] = float(cfg["pot"].get("delta"))
            out["s"] = float(cfg["pot"].get("s", 0.0))
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

def lineplot(df: pd.DataFrame, x: str, y: str, group: str, title: str, out_path: Path):
    fig = plt.figure()
    ax = plt.gca()
    for g, sub in df.groupby(group):
        sub = sub.sort_values(x)
        ax.plot(sub[x].values, sub[y].values, marker="o", label=str(g))
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)

def guess_group(case_id: str) -> str:
    for tag in ["P1","P2","P3"]:
        if case_id.startswith(f"atlasB_{tag}_") or f"_{tag}_" in case_id:
            return tag
    return "all"

def main():
    ap = argparse.ArgumentParser(description="Atlas-B/C report using physics grade.")
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--grade_file", default="", help="grades.csv path (default: <runs>/grades.csv)")
    ap.add_argument("--only_grade", default="PASS", choices=["PASS","WARN","FAIL","ALL"])
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
            runs_root / model / case_id / rid / "config.json",
            runs_root / rid / "config.json",
        ]
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
        p["group"] = guess_group(case_id)
        meta_rows.append(p)
    meta = pd.DataFrame(meta_rows)

    df = ledger.merge(meta, on="run_id", how="left")
    df = add_density_columns(df)
    df.to_csv(out_root/"atlas_joined_graded.csv", index=False)

    if args.only_grade != "ALL":
        df = df[df["grade"] == args.only_grade].copy()

    # detect sweep var
    sweep = None
    if "kappa" in df.columns and df["kappa"].nunique(dropna=True) > 1:
        sweep = "kappa"
    if "s" in df.columns and df["s"].nunique(dropna=True) > 1:
        if sweep is None or df["s"].nunique(dropna=True) >= df["kappa"].nunique(dropna=True):
            sweep = "s"
    if sweep is None:
        print("No sweep variable detected (kappa or s).")
        return

    keep = [c for c in ["run_id","case_id","model","status","grade","reasons","group","a","delta","kappa","s",
                        "Omega0","OmegaT","Omega0_density","OmegaT_density","backtracks_total"] if c in df.columns]
    df[keep].to_csv(out_root/"atlas_summary.csv", index=False)

    for metric in ["OmegaT_density","OmegaT","backtracks_total"]:
        if metric not in df.columns: 
            continue
        lineplot(df.dropna(subset=[sweep,metric]), x=sweep, y=metric, group="group",
                 title=f"{Path(args.runs).name}: {metric} vs {sweep} | grade={args.only_grade}",
                 out_path=out_root/f"line_{metric}_vs_{sweep}_grade_{args.only_grade}.png")

    # reasons
    top = (df["reasons"].fillna("").astype(str)
             .str.split("|").explode()
             .replace("", pd.NA).dropna()
             .value_counts().head(30).reset_index())
    top.columns = ["reason","count"]
    top.to_csv(out_root/"top_reasons.csv", index=False)

    print(f"Wrote graded report -> {out_root}")

if __name__ == "__main__":
    main()
