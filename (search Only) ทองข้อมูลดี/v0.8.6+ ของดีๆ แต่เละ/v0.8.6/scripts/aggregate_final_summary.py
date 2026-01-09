#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggregate all UET runs into a single table:
- pulls params from config.json (supports nested potC/potI)
- pulls last-row observables from timeseries.csv
- computes bias grades + sign grades
- computes transient metrics directly from timeseries Omega(t)

Usage:
  python scripts/aggregate_final_summary.py --runs runs_betaXs --out runs_betaXs/UET_final_summary.csv --bias_eps 1e-6
"""

from __future__ import annotations
import argparse, json, os, math, re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None: return None
        if isinstance(x, str) and x.strip() == "": return None
        v = float(x)
        if math.isnan(v) or math.isinf(v): return None
        return v
    except Exception:
        return None


def _load_json(p: Path) -> Dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _find_runs(runs_dir: Path):
    for cfg in runs_dir.rglob("config.json"):
        run_dir = cfg.parent
        ts = run_dir / "timeseries.csv"
        yield run_dir, cfg, ts


def _parse_quartic_string(pot_str: str) -> Dict[str, Optional[float]]:
    """Parse 'quartic(a=1,delta=1,s=-2)' -> {a:1, delta:1, s:-2}"""
    out = {"a": None, "delta": None, "s": None}
    if not isinstance(pot_str, str):
        return out
    m = re.search(r"quartic\s*\(([^)]+)\)", pot_str)
    if not m:
        return out
    inside = m.group(1)
    for part in inside.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = _safe_float(v.strip())
    return out


def _extract_pot_params(params: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """Extract a, delta, s from potC/potI (both dict and string format)"""
    out = {"a_C": None, "a_I": None, "delta_C": None, "delta_I": None, "s_C": None, "s_I": None}
    
    # Try VC/VI first, then potC/potI
    potC = params.get("VC") or params.get("potC")
    potI = params.get("VI") or params.get("potI")
    
    # Parse C
    if isinstance(potC, dict):
        out["a_C"] = _safe_float(potC.get("a"))
        out["delta_C"] = _safe_float(potC.get("delta"))
        out["s_C"] = _safe_float(potC.get("s"))
    elif isinstance(potC, str):
        qC = _parse_quartic_string(potC)
        out["a_C"] = qC["a"]
        out["delta_C"] = qC["delta"]
        out["s_C"] = qC["s"]
    
    # Parse I
    if isinstance(potI, dict):
        out["a_I"] = _safe_float(potI.get("a"))
        out["delta_I"] = _safe_float(potI.get("delta"))
        out["s_I"] = _safe_float(potI.get("s"))
    elif isinstance(potI, str):
        qI = _parse_quartic_string(potI)
        out["a_I"] = qI["a"]
        out["delta_I"] = qI["delta"]
        out["s_I"] = qI["s"]
    
    # Compute s_tilt (prefer s_C, fallback to s_I)
    if out["s_C"] is not None:
        out["s_tilt"] = out["s_C"]
    elif out["s_I"] is not None:
        out["s_tilt"] = out["s_I"]
    else:
        out["s_tilt"] = None
    
    # Compute unified delta (if both same)
    if out["delta_C"] is not None and out["delta_I"] is not None:
        if out["delta_C"] == out["delta_I"]:
            out["delta"] = out["delta_C"]
        else:
            out["delta"] = None  # asymmetric
    elif out["delta_C"] is not None:
        out["delta"] = out["delta_C"]
    elif out["delta_I"] is not None:
        out["delta"] = out["delta_I"]
    else:
        out["delta"] = None
    
    return out


def _transient_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute simple transient metrics from timeseries:
    - slope_init: linear slope of Omega in first 10% of samples
    - AUC_E_norm: area under normalized Omega decay (Omega shifted)
    - Omega_half: Omega at mid index
    - t_relax: time when Omega <= Omega_final + 0.05*(Omega0-Omega_final) (5% band)
    """
    out = {"slope_init": None, "AUC_E_norm": None, "Omega_half": None, "t_relax": None}
    if "Omega" not in df.columns or "t" not in df.columns:
        return out

    t = pd.to_numeric(df["t"], errors="coerce").to_numpy()
    E = pd.to_numeric(df["Omega"], errors="coerce").to_numpy()
    ok = np.isfinite(t) & np.isfinite(E)
    t = t[ok]; E = E[ok]
    if len(E) < 5:
        return out

    E0 = E[0]; Ef = E[-1]
    out["Omega_half"] = float(E[len(E)//2])

    # slope_init (first 10%)
    n0 = max(3, int(0.1 * len(E)))
    try:
        x = t[:n0]; y = E[:n0]
        A = np.vstack([x, np.ones_like(x)]).T
        m, _b = np.linalg.lstsq(A, y, rcond=None)[0]
        out["slope_init"] = float(m)
    except Exception:
        pass

    # AUC_E_norm
    denom = (E0 - Ef)
    if abs(denom) > 1e-15:
        En = (E - Ef) / denom
        try:
            out["AUC_E_norm"] = float(np.trapezoid(En, t))
        except Exception:
            pass

    # t_relax (5% band)
    target = Ef + 0.05 * (E0 - Ef)
    idx = np.where(E <= target)[0]
    if len(idx) > 0:
        out["t_relax"] = float(t[idx[0]])
    
    # t_relax_flag: check if informative (not at first step)
    dt_est = float(t[1] - t[0]) if len(t) > 1 else 0.001
    if out["t_relax"] is not None and out["t_relax"] <= dt_est * 1.5:
        out["t_relax_flag"] = "NOT_INFORMATIVE"
    else:
        out["t_relax_flag"] = "OK"

    return out


def _grade_sign(x: Optional[float], eps: float) -> str:
    if x is None: return "NA"
    if x > eps: return "POS"
    if x < -eps: return "NEG"
    return "ZERO"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="Runs directory (contains many run folders with config.json)")
    ap.add_argument("--out", default="", help="Output CSV path (default: <runs>/UET_final_summary.csv)")
    ap.add_argument("--bias_eps", type=float, default=1e-6, help="Bias epsilon for SYM")
    ap.add_argument("--sign_eps", type=float, default=1e-4, help="Sign epsilon for POS/NEG/ZERO")
    args = ap.parse_args()

    runs_dir = Path(args.runs)
    out_path = Path(args.out) if args.out else (runs_dir / "UET_final_summary.csv")

    rows = []
    issues = []

    for run_dir, cfg_path, ts_path in _find_runs(runs_dir):
        if not ts_path.exists():
            issues.append({"run_dir": str(run_dir), "reason": "NO_TIMESERIES"})
            continue

        cfg = _load_json(cfg_path)
        params = cfg.get("params") or {}
        if not isinstance(params, dict):
            params = {}

        # read timeseries
        try:
            df = pd.read_csv(ts_path)
            if df.empty:
                issues.append({"run_dir": str(run_dir), "reason": "EMPTY_TIMESERIES"})
                continue
        except Exception as e:
            issues.append({"run_dir": str(run_dir), "reason": f"BAD_TIMESERIES: {e}"})
            continue

        last = df.iloc[-1].to_dict()
        mean_C = _safe_float(last.get("mean_C"))
        mean_I = _safe_float(last.get("mean_I"))
        bias_CI = _safe_float(last.get("bias_CI"))
        if bias_CI is None and (mean_C is not None and mean_I is not None):
            bias_CI = mean_C - mean_I

        # grades
        if bias_CI is None:
            grade_bias = "NA"
        elif abs(bias_CI) <= args.bias_eps:
            grade_bias = "SYM"
        elif bias_CI > 0:
            grade_bias = "BIAS_C"
        else:
            grade_bias = "BIAS_I"

        sign_C = _grade_sign(mean_C, args.sign_eps)
        sign_I = _grade_sign(mean_I, args.sign_eps)

        # extract nested pot params (delta, s from VC/VI or potC/potI)
        pot_params = _extract_pot_params(params)

        # derived ratios
        kC = _safe_float(params.get("kC")); kI = _safe_float(params.get("kI"))
        MC = _safe_float(params.get("MC")); MI = _safe_float(params.get("MI"))
        k_ratio = (kC / kI) if (kC is not None and kI not in (None, 0.0)) else None
        Mr = (MC / MI) if (MC is not None and MI not in (None, 0.0)) else None

        # transient metrics
        tr = _transient_metrics(df)
        
        # delta: prefer from pot_params, fallback to top-level params
        delta_val = pot_params.get("delta") or _safe_float(params.get("delta"))

        rows.append({
            "run_dir": str(run_dir),
            "case_id": cfg.get("case_id", ""),
            "model": cfg.get("model", ""),
            "status": cfg.get("status", ""),
            # key params
            "beta": _safe_float(params.get("beta")),
            "kappa": _safe_float(params.get("kappa")),
            "M": _safe_float(params.get("M")),
            "delta": delta_val,
            "delta_C": pot_params.get("delta_C"),
            "delta_I": pot_params.get("delta_I"),
            "asym": _safe_float(params.get("asym")),
            "kC": kC, "kI": kI, "k_ratio": k_ratio,
            "MC": MC, "MI": MI, "Mr": Mr,
            "s_C": pot_params.get("s_C"), "s_I": pot_params.get("s_I"), "s_tilt": pot_params.get("s_tilt"),
            # last observables
            "t_end": _safe_float(last.get("t")),
            "Omega": _safe_float(last.get("Omega")),
            "OmegaT": _safe_float(last.get("OmegaT")),
            "accepted": _safe_float(last.get("accepted")),
            "backtracks": _safe_float(last.get("backtracks")),
            # bias
            "mean_C": mean_C, "mean_I": mean_I, "bias_CI": bias_CI,
            "grade_bias": grade_bias, "sign_C": sign_C, "sign_I": sign_I,
            # transient
            **tr,
        })

    out = pd.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    print("Wrote:", out_path)
    print("Rows:", len(out))
    if issues:
        print("Issues:", len(issues), "(preview 5)")
        for it in issues[:5]:
            print(" -", it)


if __name__ == "__main__":
    main()
