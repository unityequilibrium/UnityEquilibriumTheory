#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def pick_omega_star(series: pd.Series, mode: str, q: float) -> float:
    if mode == "min":
        return float(series.min())
    if mode == "final":
        return float(series.iloc[-1])
    if mode == "quantile":
        return float(series.quantile(q))
    raise ValueError(f"Unknown mode: {mode}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot shifted Lyapunov-like V(t)=Omega(t)-Omega*(s).")
    ap.add_argument("--run_dir", required=True, help="Path to a single run folder that contains timeseries.csv")
    ap.add_argument("--timeseries", default="timeseries.csv", help="Timeseries filename (default: timeseries.csv)")
    ap.add_argument("--star", choices=["min", "final", "quantile"], default="min",
                    help="How to estimate Omega*(s): min(Omega), final Omega(T), or quantile (default: min)")
    ap.add_argument("--q", type=float, default=0.05, help="Quantile for --star quantile (default: 0.05)")
    ap.add_argument("--out_dir", default=None, help="Where to save plots (default: same as run_dir)")
    ap.add_argument("--prefix", default=None, help="Filename prefix (default: run_dir name)")
    ap.add_argument("--semilogy", action="store_true", help="Also save semilogy plot of V(t) (with epsilon).")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    ts_path = run_dir / args.timeseries
    if not ts_path.exists():
        raise FileNotFoundError(f"timeseries not found: {ts_path}")

    df = pd.read_csv(ts_path)

    cols_lower = {c.lower(): c for c in df.columns}
    tcol = cols_lower.get("t")
    ocol = cols_lower.get("omega")
    docol = cols_lower.get("domega")

    if tcol is None:
        raise KeyError(f"Column 't' not found in {ts_path}. Columns: {list(df.columns)}")
    if ocol is None:
        raise KeyError(f"Column 'Omega' not found in {ts_path}. Columns: {list(df.columns)}")

    t = df[tcol].astype(float)
    omega = df[ocol].astype(float)
    omega_star = pick_omega_star(omega, args.star, args.q)
    V = omega - omega_star

    out_dir = Path(args.out_dir) if args.out_dir else run_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix if args.prefix else run_dir.name

    # Omega and V (twin axis)
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(t, omega, label="Omega")
    ax1.set_xlabel("t")
    ax1.set_ylabel("Omega")
    ax2 = ax1.twinx()
    ax2.plot(t, V, label="V=Omega-Omega*", linestyle="--")
    ax2.set_ylabel("V")
    ax1.set_title(f"{prefix}: Omega & V  (Omega*={omega_star:.6g}, mode={args.star})")
    ax1.grid(True)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")
    fig.tight_layout()
    p1 = out_dir / f"{prefix}_omega_V.png"
    fig.savefig(p1, dpi=220)
    plt.close(fig)

    # V only
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(t, V)
    ax.set_xlabel("t")
    ax.set_ylabel("V=Omega-Omega*")
    ax.set_title(f"{prefix}: V(t)  (Omega*={omega_star:.6g})")
    ax.grid(True)
    fig.tight_layout()
    p2 = out_dir / f"{prefix}_V.png"
    fig.savefig(p2, dpi=220)
    plt.close(fig)

    # dOmega if exists
    if docol is not None:
        domega = df[docol].astype(float)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(t, domega)
        ax.set_xlabel("t")
        ax.set_ylabel("dOmega")
        ax.set_title(f"{prefix}: dOmega(t)")
        ax.grid(True)
        fig.tight_layout()
        p3 = out_dir / f"{prefix}_dOmega.png"
        fig.savefig(p3, dpi=220)
        plt.close(fig)

    # Semilogy |V|
    if args.semilogy:
        eps = max(1e-12, float(V.abs().min()) * 1e-3)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.semilogy(t, (V.abs() + eps))
        ax.set_xlabel("t")
        ax.set_ylabel("|V| + eps (log)")
        ax.set_title(f"{prefix}: |V| semilogy (eps={eps:.3g})")
        ax.grid(True)
        fig.tight_layout()
        p4 = out_dir / f"{prefix}_V_semilogy.png"
        fig.savefig(p4, dpi=220)
        plt.close(fig)

    print("OK")
    print("Omega*:", omega_star, "mode:", args.star)
    print("Saved:", p1)
    print("Saved:", p2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
