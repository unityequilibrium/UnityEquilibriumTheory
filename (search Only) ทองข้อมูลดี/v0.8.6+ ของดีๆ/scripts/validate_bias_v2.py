# scripts/validate_bias_v2.py
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Optional, Tuple

import numpy as np
import pandas as pd


NUM_RE = r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"


def _as_float(x: Any) -> Optional[float]:
    try:
        if x is None or x == "":
            return None
        return float(x)
    except Exception:
        return None


def _extract_s_from_any(obj: Any) -> Optional[float]:
    """
    Robustly extract 's' from:
    - dict structures like {'type':'quartic','a':1,'delta':1,'s':...}
    - nested dicts like {'params': {'s':...}} or {'kwargs': {'s':...}}
    - strings like "quartic(a=1, delta=1, s=-2)"
    """
    if obj is None:
        return None

    if isinstance(obj, (int, float, np.number)):
        return float(obj)

    if isinstance(obj, str):
        m = re.search(rf"\bs\s*=\s*({NUM_RE})\b", obj)
        return float(m.group(1)) if m else None

    if isinstance(obj, dict):
        # direct
        if "s" in obj:
            return _as_float(obj.get("s"))

        # common nesting
        for k in ("params", "kwargs", "args"):
            if k in obj:
                s = _extract_s_from_any(obj.get(k))
                if s is not None:
                    return s

        # sometimes potential is wrapped
        for k in ("pot", "V", "potential"):
            if k in obj:
                s = _extract_s_from_any(obj.get(k))
                if s is not None:
                    return s

    return None


def _extract_s_from_case_id(case_id: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Fallback: parse from case_id patterns like:
      param_CI_sC_-2_...
      param_CI_sI_+1_...
      ... s_-2 ...
    Returns (sC, sI).
    """
    sC = None
    sI = None

    mC = re.search(rf"sC_({NUM_RE})", case_id)
    if mC:
        sC = float(mC.group(1))

    mI = re.search(rf"sI_({NUM_RE})", case_id)
    if mI:
        sI = float(mI.group(1))

    # generic fallback (rare)
    if sC is None and sI is None:
        m = re.search(rf"(?:^|_)s_({NUM_RE})(?:_|$)", case_id)
        if m:
            sC = float(m.group(1))

    return sC, sI


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _find_runs(runs_dir: Path):
    # assume each run leaf folder contains config.json
    for cfg in runs_dir.rglob("config.json"):
        run_dir = cfg.parent
        ts = run_dir / "timeseries.csv"
        yield run_dir, cfg, ts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="runs directory (e.g. runs_param_CI_s_v2)")
    ap.add_argument("--out_csv", required=True, help="output csv path")
    ap.add_argument("--out_json", default="", help="optional output json summary path")
    ap.add_argument("--bias_eps", type=float, default=1e-6, help="threshold for SYM vs BIAS")
    args = ap.parse_args()

    runs_dir = Path(args.runs)
    out_csv = Path(args.out_csv)
    out_json = Path(args.out_json) if args.out_json else None

    rows = []
    issues = []

    for run_dir, cfg_path, ts_path in _find_runs(runs_dir):
        cfg = _load_json(cfg_path)
        case_id = str(cfg.get("case_id", ""))

        # read last row of timeseries
        if not ts_path.exists():
            issues.append({"run_dir": str(run_dir), "case_id": case_id, "reason": "NO_TIMESERIES"})
            continue

        try:
            df = pd.read_csv(ts_path)
            if df.empty:
                issues.append({"run_dir": str(run_dir), "case_id": case_id, "reason": "EMPTY_TIMESERIES"})
                continue
            last = df.iloc[-1].to_dict()
        except Exception as e:
            issues.append({"run_dir": str(run_dir), "case_id": case_id, "reason": f"BAD_TIMESERIES: {e}"})
            continue

        mean_C = _as_float(last.get("mean_C"))
        mean_I = _as_float(last.get("mean_I"))
        bias_CI = _as_float(last.get("bias_CI"))

        # extract s from nested params
        params = cfg.get("params", {}) or {}
        potC = params.get("potC", None)
        potI = params.get("potI", None)

        sC = _extract_s_from_any(potC)
        sI = _extract_s_from_any(potI)

        # fallback from case_id if still missing
        if sC is None and sI is None and case_id:
            fsC, fsI = _extract_s_from_case_id(case_id)
            sC = sC if sC is not None else fsC
            sI = sI if sI is not None else fsI

        # define a convenient "s_tilt" (signed):
        # - if sC exists, use it
        # - else if only sI exists, use -sI (so that sC=-sI gives same sign convention)
        s_tilt = sC if sC is not None else (-sI if sI is not None else None)
        s_pair_ok = (sC is not None and sI is not None and abs(sC + sI) < 1e-9)

        grade_bias = ""
        if bias_CI is None:
            grade_bias = "UNKNOWN"
        elif abs(bias_CI) <= args.bias_eps:
            grade_bias = "SYM"
        elif bias_CI > 0:
            grade_bias = "BIAS_C"
        else:
            grade_bias = "BIAS_I"

        rows.append({
            "run_dir": str(run_dir),
            "case_id": case_id,
            "s_C": sC,
            "s_I": sI,
            "s_tilt": s_tilt,
            "s_pair_ok": bool(s_pair_ok),
            "mean_C": mean_C,
            "mean_I": mean_I,
            "bias_CI": bias_CI,
            "grade_bias": grade_bias,
            "Omega": _as_float(last.get("Omega")),
            "t": _as_float(last.get("t")),
            "accepted": _as_float(last.get("accepted")),
            "backtracks": _as_float(last.get("backtracks")),
        })

    out = pd.DataFrame(rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)

    summary = {
        "runs_dir": str(runs_dir),
        "out_csv": str(out_csv),
        "grade_counts": out["grade_bias"].value_counts(dropna=False).to_dict() if not out.empty else {},
        "issues_count": len(issues),
        "issues_preview": issues[:20],
    }

    if out_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Wrote:", out_csv)
    print("Grade counts:", summary["grade_counts"])
    if issues:
        print("Issues:", len(issues), "(preview first 5)")
        for it in issues[:5]:
            print(" -", it)


if __name__ == "__main__":
    main()
