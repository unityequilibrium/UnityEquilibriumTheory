# scripts/validate_transient_v3.py
from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def _split_top_level(s: str, sep: str = ",") -> List[str]:
    out, buf, depth = [], [], 0
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def _parse_kv_string(params: str) -> Dict[str, Any]:
    kv: Dict[str, Any] = {}
    for tok in _split_top_level(params, ","):
        if not tok or "=" not in tok:
            continue
        k, v = tok.split("=", 1)
        k = k.strip()
        v = v.strip()
        # try numeric
        try:
            if re.fullmatch(r"[+-]?\d+(\.\d+)?([eE][+-]?\d+)?", v):
                kv[k] = float(v)
            else:
                kv[k] = v
        except Exception:
            kv[k] = v
    return kv


def _parse_quartic(obj: Any) -> Dict[str, float]:
    """
    Supports:
      - "quartic(a=1,delta=1,s=-2)"
      - dict-ish configs (best-effort)
    """
    if obj is None:
        return {}
    if isinstance(obj, dict):
        # common shapes:
        # {kind:"quartic", a:1, delta:1, s:0} or {name:"quartic", params:{...}}
        if "params" in obj and isinstance(obj["params"], dict):
            d = obj["params"]
        else:
            d = obj
        out = {}
        for k in ("a", "delta", "s"):
            if k in d:
                try:
                    out[k] = float(d[k])
                except Exception:
                    pass
        return out

    s = str(obj)
    m = re.search(r"\bquartic\s*\((.*)\)\s*$", s)
    if not m:
        return {}
    inside = m.group(1).strip()
    out: Dict[str, float] = {}
    for tok in _split_top_level(inside, ","):
        if "=" not in tok:
            continue
        k, v = tok.split("=", 1)
        k = k.strip()
        v = v.strip()
        try:
            out[k] = float(v)
        except Exception:
            pass
    return out


def _load_config_params(run_dir: Path) -> Dict[str, Any]:
    cfg_path = run_dir / "config.json"
    if not cfg_path.exists():
        return {}

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    params = cfg.get("params", {})

    kv: Dict[str, Any] = {}
    if isinstance(params, str):
        kv.update(_parse_kv_string(params))
    elif isinstance(params, dict):
        kv.update(params)

    # also merge top-level if present
    for k in ("MC", "MI", "kC", "kI", "beta", "kappa", "M", "Mr", "kr", "k_ratio"):
        if k in cfg and k not in kv:
            kv[k] = cfg[k]

    # potentials: try multiple keys
    VC = kv.get("VC") or kv.get("potC") or cfg.get("VC") or cfg.get("potC")
    VI = kv.get("VI") or kv.get("potI") or cfg.get("VI") or cfg.get("potI")

    qC = _parse_quartic(VC)
    qI = _parse_quartic(VI)

    # canonical outputs
    out: Dict[str, Any] = dict(kv)

    out["a_C"] = qC.get("a", np.nan)
    out["a_I"] = qI.get("a", np.nan)
    out["delta_C"] = qC.get("delta", np.nan)
    out["delta_I"] = qI.get("delta", np.nan)
    out["s_C"] = qC.get("s", np.nan)
    out["s_I"] = qI.get("s", np.nan)

    # s_tilt: prefer C; if both finite and differ, keep both and set s_tilt = mean
    sC = out["s_C"]
    sI = out["s_I"]
    if np.isfinite(sC) and np.isfinite(sI):
        out["s_tilt"] = float((sC + sI) / 2.0) if (sC != sI) else float(sC)
    elif np.isfinite(sC):
        out["s_tilt"] = float(sC)
    elif np.isfinite(sI):
        out["s_tilt"] = float(sI)
    else:
        out["s_tilt"] = np.nan

    # asym: explicit param wins; else delta_I - delta_C
    if "delta_asym" in out:
        try:
            out["asym"] = float(out["delta_asym"])
        except Exception:
            out["asym"] = np.nan
    else:
        dC = out["delta_C"]
        dI = out["delta_I"]
        if np.isfinite(dC) and np.isfinite(dI):
            out["asym"] = float(dI - dC)
        else:
            out["asym"] = np.nan

    # Mr_effective and k_ratio (do not rely on case_id)
    try:
        MC = float(out.get("MC", np.nan))
        MI = float(out.get("MI", np.nan))
        out["Mr_effective"] = float(MI / MC) if (np.isfinite(MC) and np.isfinite(MI) and MC != 0) else np.nan
    except Exception:
        out["Mr_effective"] = np.nan

    try:
        kC = float(out.get("kC", np.nan))
        kI = float(out.get("kI", np.nan))
        out["k_ratio"] = float(kC / kI) if (np.isfinite(kC) and np.isfinite(kI) and kI != 0) else np.nan
    except Exception:
        out["k_ratio"] = np.nan

    # helpful ids
    out["case_id_cfg"] = cfg.get("case_id", "")
    out["run_id_cfg"] = cfg.get("run_id", cfg.get("band", ""))
    out["model_cfg"] = cfg.get("model", "")
    return out


def _pick_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    cols = set(df.columns)
    for c in candidates:
        if c in cols:
            return c
    # case-insensitive fallback
    lower_map = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lower_map:
            return lower_map[c.lower()]
    return None


def _safe_polyfit_slope(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return np.nan
    # if all x equal -> no slope
    if np.allclose(x, x[0]):
        return np.nan
    try:
        p = np.polyfit(x, y, 1)
        return float(p[0])
    except Exception:
        return np.nan


def _t_relax(t: np.ndarray, omega: np.ndarray) -> float:
    if len(t) == 0:
        return np.nan
    om_f = float(omega[-1])
    # absolute tolerance (final omega can be ~0)
    tol = max(1e-6, 1e-3 * abs(om_f) + 1e-12)
    idx = np.where(np.abs(omega - om_f) <= tol)[0]
    return float(t[idx[0]]) if len(idx) else float(t[-1])


def _omega_at_time(t: np.ndarray, omega: np.ndarray, target: float) -> float:
    if len(t) == 0:
        return np.nan
    if target <= t[0]:
        return float(omega[0])
    if target >= t[-1]:
        return float(omega[-1])
    return float(np.interp(target, t, omega))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="Root directory containing runs (recursive search).")
    ap.add_argument("--out_csv", default=None, help="Output CSV path.")
    ap.add_argument("--json", action="store_true", help="Also write summary JSON.")
    args = ap.parse_args()

    runs_root = Path(args.runs).resolve()
    out_csv = Path(args.out_csv).resolve() if args.out_csv else (runs_root / "validation_transient_v3.csv")
    out_json = out_csv.with_suffix(".json")

    rows: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []

    ts_paths = list(runs_root.rglob("timeseries.csv"))
    if not ts_paths:
        raise SystemExit(f"No timeseries.csv found under: {runs_root}")

    for ts_path in ts_paths:
        run_dir = ts_path.parent
        cfg_path = run_dir / "config.json"
        if not cfg_path.exists():
            # skip non-leaf artifacts
            continue

        rel = run_dir.relative_to(runs_root)
        run_id = rel.parts[0] if len(rel.parts) >= 1 else ""
        case_id = rel.parts[1] if len(rel.parts) >= 2 else run_dir.name

        base: Dict[str, Any] = {
            "run_id": run_id,
            "case_id": case_id,
            "run_dir": str(run_dir),
            "timeseries_path": str(ts_path),
        }

        # read config-derived params (THIS is where s/asym comes from)
        cfgp = _load_config_params(run_dir)
        base.update({
            "model": cfgp.get("model_cfg", ""),
            "case_id_cfg": cfgp.get("case_id_cfg", ""),
            "MC": cfgp.get("MC", np.nan),
            "MI": cfgp.get("MI", np.nan),
            "kC": cfgp.get("kC", np.nan),
            "kI": cfgp.get("kI", np.nan),
            "beta": cfgp.get("beta", np.nan),
            "Mr_effective": cfgp.get("Mr_effective", np.nan),
            "k_ratio": cfgp.get("k_ratio", np.nan),
            "s_tilt": cfgp.get("s_tilt", np.nan),
            "asym": cfgp.get("asym", np.nan),
            "delta_C": cfgp.get("delta_C", np.nan),
            "delta_I": cfgp.get("delta_I", np.nan),
            "s_C": cfgp.get("s_C", np.nan),
            "s_I": cfgp.get("s_I", np.nan),
        })

        # read timeseries
        try:
            df = pd.read_csv(ts_path)
        except Exception:
            row = dict(base)
            row.update({"grade": "FAIL", "reasons": "BAD_TIMESERIES_CSV"})
            rows.append(row)
            continue

        tcol = _pick_col(df, ["t", "time"])
        ocol = _pick_col(df, ["Omega", "omega", "Omega_CI", "Omega_total"])
        ecol = _pick_col(df, ["E", "energy", "Energy"])

        if tcol is None or ocol is None:
            row = dict(base)
            row.update({"grade": "FAIL", "reasons": "NO_T_OR_OMEGA"})
            rows.append(row)
            continue

        t = df[tcol].to_numpy(dtype=float)
        omega = df[ocol].to_numpy(dtype=float)
        E = df[ecol].to_numpy(dtype=float) if ecol is not None else None

        # transient metrics
        t_end = float(t[-1]) if len(t) else np.nan
        t_mid = float(t[0] + 0.5 * (t[-1] - t[0])) if len(t) else np.nan

        # slope init on first 10 points
        n0 = min(10, len(t))
        slope_init = _safe_polyfit_slope(t[:n0], omega[:n0]) if n0 >= 2 else np.nan

        trelax = _t_relax(t, omega)
        omega0 = float(omega[0]) if len(omega) else np.nan
        omegaT = float(omega[-1]) if len(omega) else np.nan
        omega_half = _omega_at_time(t, omega, t_mid) if np.isfinite(t_mid) else np.nan

        auc_E_norm = np.nan
        if E is not None and len(E) >= 2 and np.isfinite(t_end):
            dt = float(t[-1] - t[0])
            if dt > 0:
                auc = float(np.trapz(E, t))
                E0 = float(abs(E[0])) if abs(E[0]) > 0 else 1.0
                auc_E_norm = float(auc / (E0 * dt))

        row = dict(base)
        row.update({
            "grade": "PASS",
            "reasons": "OK",
            "t_end": t_end,
            "t_relax": trelax,
            "slope_init": slope_init,
            "Omega0": omega0,
            "OmegaT": omegaT,
            "Omega_half": omega_half,
            "AUC_E_norm": auc_E_norm,
            "t_col": tcol,
            "omega_col": ocol,
            "E_col": (ecol or ""),
        })
        rows.append(row)

    out_df = pd.DataFrame(rows)
    out_df.to_csv(out_csv, index=False)
    print(f"Wrote: {out_csv}")

    if args.json:
        grade_counts = out_df["grade"].value_counts(dropna=False).to_dict() if "grade" in out_df.columns else {}
        payload = {
            "runs_dir": str(runs_root),
            "out_csv": str(out_csv),
            "grade_counts": grade_counts,
            "issues": issues,
        }
        out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote: {out_json}")


if __name__ == "__main__":
    main()
