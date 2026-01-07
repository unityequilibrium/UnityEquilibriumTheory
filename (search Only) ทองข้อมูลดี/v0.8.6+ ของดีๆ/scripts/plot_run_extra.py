#!/usr/bin/env python
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True, help="path to a run folder containing timeseries.csv")
    ap.add_argument("--out_dir", default="", help="where to save plots (default: <run_dir>/plots)")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    ts_path = run_dir / "timeseries.csv"
    if not ts_path.exists():
        raise SystemExit(f"timeseries.csv not found at {ts_path}")

    out_dir = Path(args.out_dir) if args.out_dir else (run_dir / "plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(ts_path)

    # dt over time
    if "dt" in df.columns:
        plt.figure()
        plt.plot(df["t"], df["dt"])
        plt.xlabel("t")
        plt.ylabel("dt")
        plt.title("dt vs t")
        plt.savefig(out_dir / "dt_t.png", dpi=150, bbox_inches="tight")
        plt.close()

    # backtracks per step
    if "backtracks" in df.columns:
        plt.figure()
        plt.plot(df["t"], df["backtracks"])
        plt.xlabel("t")
        plt.ylabel("backtracks")
        plt.title("backtracks vs t")
        plt.savefig(out_dir / "backtracks_t.png", dpi=150, bbox_inches="tight")
        plt.close()

    # accepted step indicator
    if "accepted" in df.columns:
        plt.figure()
        plt.plot(df["t"], df["accepted"])
        plt.xlabel("t")
        plt.ylabel("accepted (0/1)")
        plt.title("accepted vs t")
        plt.savefig(out_dir / "accepted_t.png", dpi=150, bbox_inches="tight")
        plt.close()

    print(f"Wrote extra plots to {out_dir}")

if __name__ == "__main__":
    main()
