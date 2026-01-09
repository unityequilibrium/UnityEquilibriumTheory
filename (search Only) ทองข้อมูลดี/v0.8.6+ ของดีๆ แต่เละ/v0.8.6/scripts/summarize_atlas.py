#!/usr/bin/env python
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import pandas as pd
import numpy as np

def _safe_read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def _extract_params_from_config(cfg: dict) -> dict:
    model = cfg["model"]
    params = cfg["params"]
    out = {}
    if model == "C_only":
        out["kappa"] = float(params["kappa"])
        out["M"] = float(params["M"])
        pot = params["pot"]
        out["a"] = float(pot.get("a", 0.0))
        out["delta"] = float(pot["delta"])
        out["s"] = float(pot.get("s", 0.0))
    elif model == "C_I":
        out["kC"] = float(params["kC"])
        out["kI"] = float(params["kI"])
        out["MC"] = float(params["MC"])
        out["MI"] = float(params["MI"])
        out["beta"] = float(params["beta"])
        potC = params["potC"]; potI = params["potI"]
        out["aC"] = float(potC.get("a", 0.0)); out["deltaC"] = float(potC["delta"]); out["sC"] = float(potC.get("s",0.0))
        out["aI"] = float(potI.get("a", 0.0)); out["deltaI"] = float(potI["delta"]); out["sI"] = float(potI.get("s",0.0))
    return out

def plateau_score(df: pd.DataFrame, frac: float = 0.1) -> float:
    n = len(df)
    if n < 5:
        return float("nan")
    k = max(1, int(n*frac))
    tail = df["dOmega"].to_numpy()[-k:]
    tail = tail[np.isfinite(tail)]
    if len(tail)==0:
        return float("nan")
    return float(np.mean(np.abs(tail)))

def regime_label(df: pd.DataFrame, status: str, eps_range: float, eps_plateau: float, omega0: float) -> str:
    if status == "FAIL":
        return "DIVERGENT"
    # range proxy at final
    rC = None
    if "max_C" in df.columns and "min_C" in df.columns:
        rC = float(df["max_C"].iloc[-1] - df["min_C"].iloc[-1])
    rI = None
    if "max_I" in df.columns and "min_I" in df.columns and df["max_I"].dtype != object:
        try:
            rI = float(df["max_I"].iloc[-1] - df["min_I"].iloc[-1])
        except Exception:
            rI = None
    r = 0.0
    if rC is not None:
        r = max(r, abs(rC))
    if rI is not None:
        r = max(r, abs(rI))

    # plateau criterion
    ps = plateau_score(df)
    plateau = (np.isfinite(ps) and ps < eps_plateau * max(1.0, abs(omega0)))

    if plateau and r < eps_range:
        return "STEADY_UNIFORM"
    if plateau and r >= eps_range:
        return "STEADY_PATTERNED"
    if (not plateau) and r >= eps_range:
        return "COARSENING"
    # ambiguous: decreasing but near uniform and not plateau -> slow approach
    return "COARSENING"

def param_id_from_cfg(cfg: dict, ignore_numeric: bool = True) -> str:
    # Hash parameter-defining fields only (ignore seed/dt/T/grid if ignore_numeric)
    model = cfg["model"]
    dom = cfg.get("domain", {})
    base = {"model": model, "params": cfg.get("params", {})}
    if not ignore_numeric:
        base["time"] = cfg.get("time", {})
        base["grid"] = cfg.get("grid", {})
        base["domain"] = {"dim": dom.get("dim"), "L": dom.get("L"), "bc": dom.get("bc")}
    s = json.dumps(base, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_root", required=True, help="root folder containing atlas run folders")
    ap.add_argument("--out", default="atlas_outputs", help="output folder")
    ap.add_argument("--eps_range", type=float, default=1e-3)
    ap.add_argument("--eps_plateau", type=float, default=1e-8, help="plateau threshold multiplier vs |Omega0|")
    args = ap.parse_args()

    runs_root = Path(args.runs_root)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_folders = sorted(runs_root.rglob("summary.json"))
    rows = []
    for summ_path in run_folders:
        run_dir = summ_path.parent
        try:
            summ = _safe_read_json(summ_path)
            cfg = _safe_read_json(run_dir/"config.json")
            ts = pd.read_csv(run_dir/"timeseries.csv")
        except Exception:
            continue

        model = cfg["model"]
        pid = param_id_from_cfg(cfg, ignore_numeric=True)
        params = _extract_params_from_config(cfg)

        omega0 = float(summ.get("Omega0", np.nan))
        omegat = float(summ.get("OmegaT", np.nan))
        dOmega = omega0 - omegat

        pscore = plateau_score(ts)
        label = regime_label(ts, summ.get("status","FAIL"), args.eps_range, args.eps_plateau, omega0)

        row = {
            "run_id": summ.get("run_id",""),
            "run_dir": str(run_dir),
            "case_id": summ.get("case_id",""),
            "model": model,
            "param_id": pid,
            "seed": int(cfg.get("rng",{}).get("seed", -1)),
            "dt": float(cfg.get("time",{}).get("dt", np.nan)),
            "T": float(cfg.get("time",{}).get("T", np.nan)),
            "grid": int(cfg.get("grid",{}).get("N", -1)),
            "status": summ.get("status",""),
            "fail_reasons": "|".join(summ.get("fail_reasons",[])),
            "warnings": "|".join(summ.get("warnings",[])) if isinstance(summ.get("warnings",[]), list) else str(summ.get("warnings","")),
            "Omega0": omega0,
            "OmegaT": omegat,
            "DeltaOmega": dOmega,
            "plateau_score": pscore,
            "range_C_T": float(ts["max_C"].iloc[-1] - ts["min_C"].iloc[-1]) if ("max_C" in ts.columns and "min_C" in ts.columns) else np.nan,
            "range_I_T": float(ts["max_I"].iloc[-1] - ts["min_I"].iloc[-1]) if ("max_I" in ts.columns and "min_I" in ts.columns and str(ts["max_I"].iloc[-1])!="") else np.nan,
            "backtracks_total": int(summ.get("dt_backtracks_total",0)),
            "dt_min": float(summ.get("dt_min", np.nan)),
            "regime_label": label,
        }
        row.update(params)
        rows.append(row)

    atlas = pd.DataFrame(rows)
    atlas_path = out_dir / "atlas.csv"
    atlas.to_csv(atlas_path, index=False)

    # Summary grouped by param_id
    if len(atlas) > 0:
        def majority_label(x):
            x = x.dropna()
            if len(x)==0:
                return ""
            return x.value_counts().idxmax()

        grp = atlas.groupby(["model","param_id"], as_index=False)
        summ_df = grp.agg(
            seeds=("seed","nunique"),
            pass_frac=("status", lambda s: float((s=="PASS").mean()) if len(s)>0 else 0.0),
            warn_frac=("status", lambda s: float((s=="WARN").mean()) if len(s)>0 else 0.0),
            fail_frac=("status", lambda s: float((s=="FAIL").mean()) if len(s)>0 else 0.0),
            majority_label=("regime_label", majority_label),
            DeltaOmega_mean=("DeltaOmega","mean"),
            DeltaOmega_std=("DeltaOmega","std"),
            plateau_mean=("plateau_score","mean"),
            plateau_std=("plateau_score","std"),
            backtracks_max=("backtracks_total","max"),
        )
        summ_path = out_dir / "atlas_summary.csv"
        summ_df.to_csv(summ_path, index=False)

    print(f"Wrote {atlas_path}")
    print(f"Wrote {out_dir/'atlas_summary.csv'}")

if __name__ == "__main__":
    main()
