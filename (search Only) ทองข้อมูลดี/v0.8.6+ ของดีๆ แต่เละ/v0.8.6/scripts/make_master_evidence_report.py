#!/usr/bin/env python
"""
UET Master Evidence Report Generator
- Reads a run ledger.csv (e.g., runs_tier1_fail_hard/ledger.csv)
- Extracts a 1-page "falsifiability" evidence table
- Auto-locates run directories and generates key FAIL plots
- Writes Markdown (and optionally PDF if reportlab is installed)

Usage (PowerShell):
  python scripts\make_master_evidence_report.py --runs_dir runs_tier1_fail_hard --out_dir reports\master_evidence

Optional:
  python scripts\make_master_evidence_report.py --runs_dir runs_tier1_fail_hard --cases tier1_fail_big_dt,tier1_fail_blowup_delta_neg
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import json

import pandas as pd
import matplotlib.pyplot as plt


DEFAULT_CASES = [
    "tier1_fail_big_dt",
    "tier1_fail_blowup_delta_neg",
    "tier1_fail_neg_kappa",
    "tier1_fail_neg_M",
    "tier1_fail_delta_neg_precheck",
]

RUNTIME_FAIL_CODES = {"ENERGY_INCREASE", "BLOWUP", "NAN_INF"}
STRUCTURAL_FAIL_PREFIX = "COERCIVITY_"


def find_ledger(runs_dir: Path) -> Path:
    p = runs_dir / "ledger.csv"
    if p.exists():
        return p
    # fallback: search
    for cand in runs_dir.rglob("ledger.csv"):
        return cand
    raise FileNotFoundError(f"ledger.csv not found under: {runs_dir}")


def safe_read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def find_run_dir_by_run_id(runs_dir: Path, run_id: str) -> Path | None:
    # Typical layout: runs_dir/<model>/<case_id>/<run_id>/
    # We'll search for a folder that contains summary.json and matches run_id.
    for p in runs_dir.rglob("summary.json"):
        if p.parent.name == run_id:
            return p.parent
    return None


def load_timeseries(run_dir: Path) -> pd.DataFrame:
    ts = run_dir / "timeseries.csv"
    if not ts.exists():
        raise FileNotFoundError(f"timeseries.csv not found: {ts}")
    return pd.read_csv(ts)


def plot_timeseries_basic(df: pd.DataFrame, out_png: Path, title: str) -> None:
    # Expect columns: t, Omega, dOmega (or Omega0??). We'll be defensive.
    tcol = "t" if "t" in df.columns else None
    if tcol is None:
        # fallback: try 'time'
        tcol = "time" if "time" in df.columns else df.columns[0]

    omega_col = "Omega" if "Omega" in df.columns else None
    domega_col = "dOmega" if "dOmega" in df.columns else None

    plt.figure()
    if omega_col:
        plt.plot(df[tcol], df[omega_col], label="Omega")
    if domega_col:
        plt.plot(df[tcol], df[domega_col], label="dOmega")
    if not omega_col and not domega_col:
        # plot something meaningful: first numeric column after t
        for c in df.columns:
            if c == tcol:
                continue
            if pd.api.types.is_numeric_dtype(df[c]):
                plt.plot(df[tcol], df[c], label=c)
                break

    plt.xlabel(tcol)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


def plot_blowup_diagnostics(df: pd.DataFrame, out_png: Path, title: str) -> None:
    # Try to visualize field growth: c_max, max_abs_C, C_2, L4_C, etc.
    tcol = "t" if "t" in df.columns else df.columns[0]
    candidates = [c for c in ["c_max", "max_abs_C", "C_2", "L4_C", "min_C", "max_C"] if c in df.columns]
    plt.figure()
    if candidates:
        for c in candidates[:4]:  # keep readable
            plt.plot(df[tcol], df[c], label=c)
    else:
        # fallback: plot all numeric cols except t (up to 4)
        count = 0
        for c in df.columns:
            if c == tcol:
                continue
            if pd.api.types.is_numeric_dtype(df[c]):
                plt.plot(df[tcol], df[c], label=c)
                count += 1
            if count >= 4:
                break
    plt.xlabel(tcol)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


def write_markdown(report_md: Path, title: str, table_df: pd.DataFrame, plots: list[tuple[str, Path]], notes: list[str]) -> None:
    report_md.parent.mkdir(parents=True, exist_ok=True)
    rel = lambda p: p.as_posix()

    with report_md.open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write("## Evidence table (1 page)\n\n")
        f.write(table_df.to_markdown(index=False))
        f.write("\n\n")
        f.write("## Key plots\n\n")
        for cap, img in plots:
            f.write(f"### {cap}\n\n")
            f.write(f"![{cap}]({rel(img)})\n\n")
        f.write("## Decision criteria\n\n")
        f.write("- Runtime FAIL codes: `ENERGY_INCREASE`, `BLOWUP`, `NAN_INF`\n")
        f.write(f"- Structural FAIL prefix: `{STRUCTURAL_FAIL_PREFIX}*` (checked via coercivity precheck)\n\n")
        if notes:
            f.write("## Notes\n\n")
            for n in notes:
                f.write(f"- {n}\n")
            f.write("\n")


def try_make_pdf(md_path: Path, pdf_path: Path) -> bool:
    # Optional: generate a very simple PDF summary (table + embedded images list)
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
    except Exception:
        return False

    text = md_path.read_text(encoding="utf-8").splitlines()
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    x = 0.8 * inch
    y = height - 0.8 * inch
    line_h = 12

    for line in text:
        if y < 0.8 * inch:
            c.showPage()
            y = height - 0.8 * inch
        # strip markdown formatting a bit
        plain = line.replace("#", "").strip()
        if len(plain) > 110:
            plain = plain[:107] + "..."
        c.drawString(x, y, plain)
        y -= line_h

    c.save()
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_dir", type=str, default="runs_tier1_fail_hard", help="Runs directory containing ledger.csv")
    ap.add_argument("--out_dir", type=str, default="reports/master_evidence", help="Output directory for report + plots")
    ap.add_argument("--cases", type=str, default=",".join(DEFAULT_CASES), help="Comma-separated case_id list to include")
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ledger_path = find_ledger(runs_dir)
    df = safe_read_csv(ledger_path)

    # Normalize missing columns
    for col in ["fail_reasons", "max_energy_increase", "dt_min", "dt_max", "backtracks_total", "Omega0", "OmegaT"]:
        if col not in df.columns:
            df[col] = ""

    cases = [c.strip() for c in args.cases.split(",") if c.strip()]
    df_sel = df[df["case_id"].isin(cases)].copy()

    # Evidence table columns
    cols = ["case_id", "model", "status", "fail_reasons", "max_energy_increase", "dt_min", "dt_max", "backtracks_total", "Omega0", "OmegaT", "run_id"]
    cols = [c for c in cols if c in df_sel.columns]
    table = df_sel[cols].copy()

    # Save evidence table
    evidence_csv = out_dir / "evidence_table.csv"
    table.to_csv(evidence_csv, index=False)

    # Generate plots for the two most illustrative cases if present
    plot_items: list[tuple[str, Path]] = []
    notes: list[str] = [
        f"Ledger source: {ledger_path.as_posix()}",
        f"Evidence table saved: {evidence_csv.as_posix()}",
    ]

    def make_case_plots(case_id: str, extra_blowup: bool=False):
        sub = df_sel[df_sel["case_id"] == case_id]
        if sub.empty:
            notes.append(f"Case not found in ledger: {case_id}")
            return
        # pick first row (if multiple seeds)
        row = sub.iloc[0]
        run_id = str(row["run_id"])
        run_dir = find_run_dir_by_run_id(runs_dir, run_id)
        if run_dir is None:
            notes.append(f"Run dir not found for run_id={run_id} (case={case_id})")
            return
        try:
            ts = load_timeseries(run_dir)
        except Exception as e:
            notes.append(f"timeseries load failed for {case_id} @ {run_dir}: {e}")
            return
        img1 = out_dir / "plots" / f"{case_id}_omega_domega.png"
        plot_timeseries_basic(ts, img1, f"{case_id}: Omega & dOmega")
        plot_items.append((f"{case_id} (Omega & dOmega)", img1))
        if extra_blowup:
            img2 = out_dir / "plots" / f"{case_id}_blowup_diag.png"
            plot_blowup_diagnostics(ts, img2, f"{case_id}: blow-up diagnostics")
            plot_items.append((f"{case_id} (blow-up diagnostics)", img2))

    make_case_plots("tier1_fail_big_dt", extra_blowup=False)
    make_case_plots("tier1_fail_blowup_delta_neg", extra_blowup=True)

    # Add note about structural precheck
    structural_rows = df_sel[df_sel["case_id"].str.contains("precheck", na=False)]
    if not structural_rows.empty:
        notes.append("Structural precheck cases may PASS at runtime; they must be validated with coercivity_check (COERCIVITY_*).")

    report_md = out_dir / "UET_v0_8_5_master_evidence.md"
    write_markdown(report_md, "UET v0.8.5 — Master Evidence (Fail Pack)", table, plot_items, notes)

    # Optional PDF
    report_pdf = out_dir / "UET_v0_8_5_master_evidence.pdf"
    if try_make_pdf(report_md, report_pdf):
        notes.append(f"PDF saved: {report_pdf.as_posix()}")
    else:
        notes.append("PDF not generated (install reportlab to enable).")

    print("OK")
    print("Report:", report_md)
    print("Evidence table:", evidence_csv)
    if report_pdf.exists():
        print("PDF:", report_pdf)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
