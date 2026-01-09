#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


S_RE = re.compile(r"\bs\s*=\s*([+-]?\d+(?:\.\d+)?)\b")


def extract_scale_from_config(cfg: dict):
    if isinstance(cfg.get("params"), str):
        m = S_RE.search(cfg["params"])
        if m:
            return float(m.group(1))
    if isinstance(cfg.get("params"), dict):
        p = cfg["params"]
        if "s" in p and isinstance(p["s"], (int, float)):
            return float(p["s"])
        V = p.get("V")
        if isinstance(V, dict) and "s" in V and isinstance(V["s"], (int, float)):
            return float(V["s"])
        if isinstance(V, str):
            m = S_RE.search(V)
            if m:
                return float(m.group(1))
    return None


def extract_scale_fallback(text):
    if not text:
        return None
    m = S_RE.search(str(text))
    if m:
        return float(m.group(1))
    return None


def load_scale(run_dir: Path, ledger_row: dict):
    cfg_path = run_dir / "config.json"
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            s = extract_scale_from_config(cfg)
            if s is not None:
                return s
        except Exception:
            pass

    meta_path = run_dir / "meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if isinstance(meta, dict):
                for k in ("params", "notes", "config"):
                    s = extract_scale_fallback(meta.get(k))
                    if s is not None:
                        return s
        except Exception:
            pass

    for k in ("notes", "case_id"):
        s = extract_scale_fallback(ledger_row.get(k))
        if s is not None:
            return s
    return None


def main():
    ap = argparse.ArgumentParser(description="Tier2 shifted summary: V=Omega-Omega* with Omega*=min_t Omega per run.")
    ap.add_argument("--runs_dir", default="runs_tier2_sweep", help="Runs directory that contains ledger.csv")
    ap.add_argument("--ledger", default="ledger.csv", help="Ledger filename inside runs_dir (default: ledger.csv)")
    ap.add_argument("--out_dir", default="reports/tier2_shifted", help="Output directory for plots and csv")
    ap.add_argument("--timeseries", default="timeseries.csv", help="Timeseries filename (default: timeseries.csv)")
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    ledger_path = runs_dir / args.ledger
    if not ledger_path.exists():
        raise FileNotFoundError(f"Ledger not found: {ledger_path}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ledger = pd.read_csv(ledger_path)

    required = {"run_id", "case_id", "model", "status"}
    missing = [c for c in required if c not in ledger.columns]
    if missing:
        raise KeyError(f"Ledger missing columns {missing}. Columns: {list(ledger.columns)}")

    rows = []
    for _, r in ledger.iterrows():
        model = str(r["model"])
        case_id = str(r["case_id"])
        run_id = str(r["run_id"])
        status = str(r["status"])

        run_dir = runs_dir / model / case_id / run_id
        ts_path = run_dir / args.timeseries
        if not ts_path.exists():
            continue

        df = pd.read_csv(ts_path)
        cols_lower = {c.lower(): c for c in df.columns}
        tcol = cols_lower.get("t")
        ocol = cols_lower.get("omega")
        if tcol is None or ocol is None:
            continue

        omega = df[ocol].astype(float)
        omega_star = float(omega.min())
        omega0 = float(omega.iloc[0])
        omegat = float(omega.iloc[-1])
        V0 = omega0 - omega_star
        VT = omegat - omega_star

        scale = load_scale(run_dir, r.to_dict())
        rows.append({
            "model": model,
            "case_id": case_id,
            "run_id": run_id,
            "status": status,
            "scale": scale,
            "Omega0": omega0,
            "OmegaT": omegat,
            "Omega_star": omega_star,
            "V0": V0,
            "VT": VT,
        })

    if not rows:
        raise RuntimeError("No runs with timeseries.csv found. Check runs_dir and folder structure.")

    tbl = pd.DataFrame(rows)
    out_csv = out_dir / "tier2_shifted_table.csv"
    tbl.to_csv(out_csv, index=False)

    tbl2 = tbl.dropna(subset=["scale"]).copy()
    if tbl2.empty:
        raise RuntimeError("Could not extract scale s from runs. Check config.json/meta.json.")

    g = tbl2.groupby("scale")
    summary = g.agg(
        V0_mean=("V0", "mean"),
        V0_std=("V0", "std"),
        VT_mean=("VT", "mean"),
        VT_std=("VT", "std"),
        n=("VT", "count"),
    ).reset_index().sort_values("scale")

    summary_csv = out_dir / "tier2_shifted_summary.csv"
    summary.to_csv(summary_csv, index=False)

    fig = plt.figure(figsize=(11, 4.5))
    ax1 = fig.add_subplot(121)
    ax1.errorbar(summary["scale"], summary["V0_mean"], yerr=summary["V0_std"], marker="o", capsize=3)
    ax1.set_title("V0 mean ± std by scale (shifted)")
    ax1.set_xlabel("scale (s)")
    ax1.set_ylabel("V0 = Omega0 - Omega*")
    ax1.grid(True)

    ax2 = fig.add_subplot(122)
    ax2.errorbar(summary["scale"], summary["VT_mean"], yerr=summary["VT_std"], marker="o", capsize=3)
    ax2.set_title("VT mean ± std by scale (shifted)")
    ax2.set_xlabel("scale (s)")
    ax2.set_ylabel("VT = OmegaT - Omega*")
    ax2.grid(True)

    fig.tight_layout()
    out_png = out_dir / "tier2_shifted_summary.png"
    fig.savefig(out_png, dpi=220)
    plt.close(fig)

    print("OK")
    print("Saved:", out_csv)
    print("Saved:", summary_csv)
    print("Saved:", out_png)


if __name__ == "__main__":
    main()
