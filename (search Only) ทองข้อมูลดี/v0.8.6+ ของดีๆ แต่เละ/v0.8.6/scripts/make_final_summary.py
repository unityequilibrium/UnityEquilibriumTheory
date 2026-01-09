# scripts/make_final_summary.py
from __future__ import annotations

import argparse
import glob
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def _read_csv_safe(path: Path) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(path)
        if df is None or df.empty:
            return None
        # normalize columns
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception:
        return None


def _pick_first_existing(paths: List[Path]) -> List[Path]:
    # keep order stable, dedupe
    seen = set()
    out = []
    for p in paths:
        rp = str(p.resolve())
        if rp not in seen and p.exists() and p.is_file():
            out.append(p)
            seen.add(rp)
    return out


def _find_candidate_files(runs_dir: Path) -> Dict[str, List[Path]]:
    # 1. Search for aggregated validation CSVs first (fast path)
    all_csv = [Path(p) for p in glob.glob(str(runs_dir / "**" / "*.csv"), recursive=True)]
    eq = []
    tr = []
    bi = []
    
    for p in all_csv:
        name = p.name.lower()
        if not name.startswith("validation") and name not in ("bias_summary.csv",):
            continue

        if "transient" in name:
            tr.append(p)
        elif "bias" in name or name == "bias_summary.csv":
            bi.append(p)
        else:
            eq.append(p)

    def prefer(list_in: List[Path], preferred_names: List[str]) -> List[Path]:
        pref = []
        rest = []
        for p in list_in:
            if p.name in preferred_names:
                pref.append(p)
            else:
                rest.append(p)
        return _pick_first_existing(pref + rest)

    eq = prefer(eq, ["validation.csv"])
    tr = prefer(tr, ["validation_transient_v3.csv", "validation_transient_v2.csv", "validation_transient.csv"])
    bi = prefer(bi, ["validation_bias_v2.csv", "validation_bias.csv", "bias_summary.csv"])

    return {"eq": eq, "transient": tr, "bias": bi}


def _coalesce_columns(df: pd.DataFrame) -> pd.DataFrame:
    # if merge created foo_x/foo_y, coalesce into foo
    cols = list(df.columns)
    x_cols = [c for c in cols if c.endswith("_x")]
    for cx in x_cols:
        base = cx[:-2]
        cy = base + "_y"
        if cy in df.columns:
            df[base] = df[cx]
            df.loc[df[base].isna(), base] = df[cy]
            df.drop(columns=[cx, cy], inplace=True, errors="ignore")
    return df


def _ensure_key(df: pd.DataFrame, runs_dir_name: str) -> Optional[pd.DataFrame]:
    if df is None or df.empty:
        return None

    # standardize possible run id columns
    if "run_id" not in df.columns:
        # sometimes might be RunId or id
        for alt in ["RunId", "runid", "id"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "run_id"})
                break

    if "run_id" not in df.columns:
        return None

    df["runs_dir"] = runs_dir_name
    df["run_key"] = df["runs_dir"].astype(str) + "|" + df["run_id"].astype(str)
    return df


def _parse_number_from_case(case_id: str, key: str) -> Optional[float]:
    # try patterns like key_1.0 or key1.0 or key=-1
    pats = [
        rf"{re.escape(key)}[_=](-?\d+(?:\.\d+)?)",
        rf"{re.escape(key)}(-?\d+(?:\.\d+)?)",
    ]
    for pat in pats:
        m = re.search(pat, case_id)
        if m:
            try:
                return float(m.group(1))
            except Exception:
                return None
    return None


def _infer_s_tilt(row: pd.Series) -> Optional[float]:
    # If already have s_tilt, use it
    for col in ["s_tilt", "s", "tilt", "sTilt"]:
        if col in row.index and pd.notna(row[col]):
            try:
                return float(row[col])
            except Exception:
                pass

    case_id = str(row.get("case_id", "") or "")
    if not case_id:
        return None

    # patterns from your naming: sC_<v>, sI_<v>  OR just s_<v>
    sC = _parse_number_from_case(case_id, "sC")
    sI = _parse_number_from_case(case_id, "sI")
    if sC is not None and sI is not None:
        return float(sC - sI)

    s_only = _parse_number_from_case(case_id, "s")
    if s_only is not None:
        # treat as differential if it's "tiltCOnly": sC=s, sI=0
        return float(s_only)

    return None


def _infer_beta(row: pd.Series) -> Optional[float]:
    for col in ["beta", "Beta"]:
        if col in row.index and pd.notna(row[col]):
            try:
                return float(row[col])
            except Exception:
                pass

    case_id = str(row.get("case_id", "") or "")
    if not case_id:
        return None
    b = _parse_number_from_case(case_id, "beta")
    if b is None:
        b = _parse_number_from_case(case_id, "b")
    return b


def _infer_k_ratio(row: pd.Series) -> Optional[float]:
    for col in ["k_ratio", "kr_effective", "kC_over_kI", "kC_kI"]:
        if col in row.index and pd.notna(row[col]):
            try:
                return float(row[col])
            except Exception:
                pass
    case_id = str(row.get("case_id", "") or "")
    if not case_id:
        return None
    kr = _parse_number_from_case(case_id, "kr")
    if kr is None:
        kr = _parse_number_from_case(case_id, "k_ratio")
    return kr


def _compute_derived(df: pd.DataFrame) -> pd.DataFrame:
    # numeric conversions where possible
    for c in ["MC", "MI", "Omega0", "OmegaT", "Omega", "OmegaT_mean", "t_relax", "AUC_E_norm", "slope_init", "Omega_half"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Mr_effective = MI/MC (your earlier definition)
    if "Mr_effective" not in df.columns:
        if "MC" in df.columns and "MI" in df.columns:
            df["Mr_effective"] = df["MI"] / df["MC"]
    else:
        df["Mr_effective"] = pd.to_numeric(df["Mr_effective"], errors="coerce")

    # if Mr_input exists keep it
    for c in ["Mr_input", "Mr_from_id"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # fill beta/s_tilt/k_ratio if missing
    if "case_id" not in df.columns:
        df["case_id"] = ""

    if "beta" not in df.columns:
        df["beta"] = np.nan
    df["beta"] = df.apply(lambda r: _infer_beta(r) if pd.isna(r["beta"]) else r["beta"], axis=1)

    if "s_tilt" not in df.columns:
        df["s_tilt"] = np.nan
    df["s_tilt"] = df.apply(lambda r: _infer_s_tilt(r) if pd.isna(r["s_tilt"]) else r["s_tilt"], axis=1)

    if "k_ratio" not in df.columns:
        df["k_ratio"] = np.nan
    df["k_ratio"] = df.apply(lambda r: _infer_k_ratio(r) if pd.isna(r["k_ratio"]) else r["k_ratio"], axis=1)

    # normalize grade_bias naming
    if "grade_bias" not in df.columns:
        for alt in ["gradeBias", "bias_grade", "grade"]:
            if alt in df.columns:
                # careful: don't override main grade; only use if clearly bias file
                if alt != "grade":
                    df["grade_bias"] = df[alt]
                break

    # normalize sign_C naming if present
    if "sign_C" in df.columns:
        df["sign_C"] = df["sign_C"].astype(str)

    return df


def _merge_frames(frames: List[pd.DataFrame]) -> Optional[pd.DataFrame]:
    frames = [f for f in frames if f is not None and not f.empty]
    if not frames:
        return None
    base = frames[0]
    for nxt in frames[1:]:
        base = base.merge(nxt, on=["run_key", "run_id", "runs_dir"], how="outer", suffixes=("_x", "_y"))
        base = _coalesce_columns(base)
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_glob", default="runs_*", help='Glob for runs directories, e.g. "runs_*" or "runs_param_*"')
    ap.add_argument("--out", default="reports/UET_final_summary.csv", help="Output CSV path")
    args = ap.parse_args()

    root = Path(".").resolve()
    runs_dirs = [Path(p) for p in glob.glob(str(root / args.runs_glob)) if Path(p).is_dir()]

    if not runs_dirs:
        raise SystemExit(f"No runs dirs matched: {args.runs_glob}")

    all_merged = []

    for rd in sorted(runs_dirs, key=lambda p: p.name):
        files = _find_candidate_files(rd)
        eq_paths = files["eq"]
        tr_paths = files["transient"]
        bi_paths = files["bias"]

        def load_concat(paths: List[Path]) -> Optional[pd.DataFrame]:
            dfs = []
            for p in paths:
                df = _read_csv_safe(p)
                if df is None:
                    continue
                df = _ensure_key(df, rd.name)
                if df is None:
                    continue
                # keep which file it came from (debug)
                df["source_csv"] = str(p.relative_to(root))
                dfs.append(df)
            if not dfs:
                return None
            out = pd.concat(dfs, ignore_index=True)
            # if same run_key appears multiple times (multiple validation files),
            # keep the last non-null per column by grouping.
            out = out.sort_values(["run_key", "source_csv"])
            out = out.groupby(["run_key", "run_id", "runs_dir"], as_index=False).last()
            return out

        eq_df = load_concat(eq_paths)
        tr_df = load_concat(tr_paths)
        bi_df = load_concat(bi_paths)

        merged = _merge_frames([eq_df, tr_df, bi_df])
        if merged is None or merged.empty:
            continue

        all_merged.append(merged)

    if not all_merged:
        raise SystemExit("No data merged. Check that your validation CSVs contain 'run_id'.")

    final = pd.concat(all_merged, ignore_index=True)
    final = _compute_derived(final)

    # light cleanup: prefer a stable column order (keep unknowns at end)
    preferred = [
        "runs_dir", "run_dir", "run_id", "case_id", "model", "seed",
        "status", "grade", "reasons",
        "beta", "s_tilt", "k_ratio", "kappa", "delta", "asym",
        "MC", "MI", "Mr_input", "Mr_effective", "Mscale",
        "Omega0", "OmegaT", "max_energy_increase", "backtracks_total",
        "t_relax", "slope_init", "AUC_E_norm", "Omega_half",
        "mean_C", "mean_I", "bias_CI", "grade_bias", "sign_C",
        "accepted", "backtracks",
        "source_csv",
    ]
    cols = list(final.columns)
    ordered = [c for c in preferred if c in cols] + [c for c in cols if c not in preferred]
    final = final[ordered]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(out_path, index=False)
    print(f"Wrote: {out_path}  rows={len(final)} cols={len(final.columns)}")


if __name__ == "__main__":
    main()
