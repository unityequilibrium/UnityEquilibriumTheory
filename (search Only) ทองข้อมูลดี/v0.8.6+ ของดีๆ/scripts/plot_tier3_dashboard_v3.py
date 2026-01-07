import argparse
import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def infer_grid(row) -> int | None:
    """
    Try to infer grid from case_id / run_id.
    Expected patterns like: ..._g32_... or ..._g64_...
    """
    for key in ("case_id", "run_id"):
        s = str(row.get(key, "") or "")
        m = re.search(r"(?:^|[_-])g(\d+)(?:[_-]|$)", s)
        if m:
            return int(m.group(1))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, help="path to ledger.csv (inside runs_... folder)")
    ap.add_argument("--out", required=True, help="output folder")
    args = ap.parse_args()

    ledger_path = Path(args.ledger)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(ledger_path)

    # Ensure minimal columns exist
    for c in ("run_id", "case_id", "model", "status"):
        if c not in df.columns:
            raise RuntimeError(f"ledger is missing required column: {c}")

    # Add grid if missing or try to infer from case_id
    if "grid" not in df.columns:
        df["grid"] = df["case_id"].str.extract(r"_g(\d+)", expand=False)
    
    df["grid"] = pd.to_numeric(df["grid"], errors="coerce")
    
    # Drop rows where grid couldn't be determined (instead of -1 fallback)
    df = df.dropna(subset=["grid"])
    df["grid"] = df["grid"].astype(int)

    # 1) counts_by_grid_model_status.csv
    counts = (
        df.groupby(["grid", "model", "status"])
          .size()
          .reset_index(name="n")
          .sort_values(["grid", "model", "status"])
    )
    counts.to_csv(out_dir / "counts_by_grid_model_status.csv", index=False)

    # 2) backtracks_by_case.csv (ถ้ามีคอลัมน์นี้)
    if "backtracks_total" in df.columns:
        bt = df[["grid", "case_id", "model", "status", "backtracks_total"]].copy()
        bt.to_csv(out_dir / "backtracks_by_case.csv", index=False)

    # 3) omega_by_grid.csv + plot (ถ้ามี Omega0/OmegaT)
    omega_cols = [c for c in ("Omega0", "OmegaT", "Omega0_density", "OmegaT_density") if c in df.columns]
    if omega_cols:
        omega = (
            df.groupby(["grid", "model"])[omega_cols]
              .mean(numeric_only=True)
              .reset_index()
              .sort_values(["grid", "model"])
        )
        omega.to_csv(out_dir / "omega_by_grid.csv", index=False)

        # simple plot: mean Omega0/OmegaT by grid for each model
        for oc in omega_cols:
            plt.figure()
            for model, sub in omega.groupby("model"):
                plt.plot(sub["grid"], sub[oc], marker="o", label=str(model))
            title_suffix = " (per unit area)" if "density" in oc else " (total)"
            plt.title(f"{oc} mean by grid{title_suffix}")
            plt.xlabel("grid")
            plt.ylabel(oc)
            plt.legend()
            plt.tight_layout()
            plt.savefig(out_dir / f"{oc.lower()}_by_grid.png", dpi=150)
            plt.close()

    print(f"[OK] Wrote dashboard outputs to: {out_dir}")


if __name__ == "__main__":
    main()
