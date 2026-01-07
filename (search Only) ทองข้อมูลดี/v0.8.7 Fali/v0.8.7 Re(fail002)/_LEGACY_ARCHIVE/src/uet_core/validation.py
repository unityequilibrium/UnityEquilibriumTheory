"""
Validation utilities for UET harness runs.

Design goals:
- Lightweight, no hard dependency on "expected PASS/FAIL" labels in matrices
- Provide actionable FAIL/WARN codes for debugging
- Avoid assuming any physics beyond what the harness already outputs

Contract:
A "run dir" contains: config.json, timeseries.csv, summary.json
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import json
import numpy as np
import pandas as pd
from typing import NamedTuple, Protocol

class GateResult(NamedTuple):
    id: str
    status: str  # "PASS", "FAIL", "WARN"
    value: float
    tolerance: float
    message: str

@dataclass
class Issue:
    level: str   # "FAIL" | "WARN"
    code: str
    message: str

def _fail(code: str, msg: str) -> Issue:
    return Issue("FAIL", code, msg)

def _warn(code: str, msg: str) -> Issue:
    return Issue("WARN", code, msg)

def overall_grade(issues: List[Issue]) -> str:
    if any(i.level == "FAIL" for i in issues):
        return "FAIL"
    if any(i.level == "WARN" for i in issues):
        return "WARN"
    return "PASS"

def validate_artifacts(run_dir: Path) -> Tuple[Optional[dict], Optional[pd.DataFrame], Optional[dict], List[Issue]]:
    issues: List[Issue] = []
    run_dir = Path(run_dir)

    cfg_p = run_dir / "config.json"
    ts_p  = run_dir / "timeseries.csv"
    sum_p = run_dir / "summary.json"

    if not cfg_p.exists():
        issues.append(_fail("MISSING_CONFIG", f"Missing {cfg_p.name}"))
        return None, None, None, issues
    if not ts_p.exists():
        issues.append(_fail("MISSING_TIMESERIES", f"Missing {ts_p.name}"))
        return None, None, None, issues
    if not sum_p.exists():
        issues.append(_fail("MISSING_SUMMARY", f"Missing {sum_p.name}"))
        return None, None, None, issues

    try:
        cfg = json.loads(cfg_p.read_text(encoding="utf-8"))
    except Exception as e:
        issues.append(_fail("BAD_CONFIG_JSON", f"Failed to parse config.json: {e}"))
        return None, None, None, issues

    try:
        df = pd.read_csv(ts_p)
    except Exception as e:
        issues.append(_fail("BAD_TIMESERIES_CSV", f"Failed to read timeseries.csv: {e}"))
        return cfg, None, None, issues

    try:
        summ = json.loads(sum_p.read_text(encoding="utf-8"))
    except Exception as e:
        issues.append(_fail("BAD_SUMMARY_JSON", f"Failed to parse summary.json: {e}"))
        return cfg, df, None, issues

    # Basic schema checks
    required_cols = {"step", "t", "Omega", "dt", "accepted", "backtracks"}
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        issues.append(_fail("TIMESERIES_MISSING_COLS", f"timeseries.csv missing cols: {missing}"))

    required_sum = {"status", "Omega0", "OmegaT", "steps_total", "steps_accepted", "dt_backtracks_total"}
    miss_sum = [k for k in required_sum if k not in summ]
    if miss_sum:
        issues.append(_fail("SUMMARY_MISSING_KEYS", f"summary.json missing keys: {miss_sum}"))

    # Finite checks
    if "Omega" in df.columns:
        try:
            omega = pd.to_numeric(df["Omega"], errors="coerce")
            if not np.isfinite(omega.dropna().to_numpy()).all():
                issues.append(_fail("OMEGA_NAN_INF", "Omega contains NaN/Inf in timeseries."))
        except Exception:
            issues.append(_warn("OMEGA_NONNUMERIC", "Omega column could not be coerced to numeric."))

    return cfg, df, summ, issues

def validate_additivity(df: pd.DataFrame) -> List[Issue]:
    """
    In this harness, "additivity" is interpreted as internal consistency between:
    - summary Omega0/OmegaT and timeseries endpoints (accepted steps)
    Not a physics claim; purely an artifact consistency check.
    """
    issues: List[Issue] = []
    if df is None or df.empty:
        issues.append(_fail("EMPTY_TIMESERIES", "timeseries.csv is empty"))
        return issues
    if "accepted" in df.columns:
        acc = df[df["accepted"] == 1]
    else:
        acc = df
    if acc.empty:
        issues.append(_fail("NO_ACCEPTED_STEPS", "No accepted steps recorded (accepted==1)."))
        return issues

    # nothing else to do here without summary; validate_conflict handles endpoints if summary passed
    return issues

def validate_monotone(df: pd.DataFrame, cfg: dict) -> List[Issue]:
    issues: List[Issue] = []
    if df is None or df.empty or "Omega" not in df.columns:
        return issues
    # Use accepted steps only (reject steps can show non-monotone attempts)
    if "accepted" in df.columns:
        df2 = df[df["accepted"] == 1].copy()
    else:
        df2 = df.copy()
    if len(df2) < 3:
        return issues

    omega = pd.to_numeric(df2["Omega"], errors="coerce").to_numpy()
    omega = omega[np.isfinite(omega)]
    if len(omega) < 3:
        return issues

    d = np.diff(omega)
    # Tolerances: scale with typical magnitude
    scale = max(1.0, float(np.nanmax(np.abs(omega))))
    tol = float((cfg.get("time", {}) or {}).get("tol_abs", 1e-10)) * 10.0 + 1e-12 * scale
    max_inc = float(np.nanmax(d))
    if max_inc > tol:
        # strict mode tends to expect descent; mark WARN by default, FAIL if large
        if max_inc > 1e-6 * scale:
            issues.append(_fail("OMEGA_INCREASE_LARGE", f"Omega increased by max {max_inc:.3g} (> {tol:.3g})."))
        else:
            issues.append(_warn("OMEGA_INCREASE", f"Omega not strictly monotone; max increase {max_inc:.3g} (> {tol:.3g})."))
    return issues

def validate_dt_backtracks(summary: dict, cfg: dict) -> List[Issue]:
    issues: List[Issue] = []
    if summary is None:
        return issues
    bt = int(summary.get("dt_backtracks_total", 0) or 0)
    steps = int(summary.get("steps_total", 0) or 0)
    max_bt = int(((cfg.get("time", {}) or {}).get("backtrack", {}) or {}).get("max_backtracks", 0) or 0)

    if bt < 0:
        issues.append(_fail("BACKTRACK_NEG", "dt_backtracks_total < 0 (invalid)."))
        return issues

    if max_bt > 0 and steps > 0:
        # soft expectation: average backtracks per step should be small
        avg = bt / max(1, steps)
        if avg > max(5.0, 0.5 * max_bt):
            issues.append(_warn("BACKTRACK_HEAVY", f"Heavy backtracking: total={bt}, steps={steps}, avg={avg:.2f}/step."))
        if avg > max(20.0, 0.9 * max_bt):
            issues.append(_fail("BACKTRACK_PATHOLOGICAL", f"Pathological backtracking: avg={avg:.2f}/step."))

    dt_min = float(summary.get("dt_min", 0.0) or 0.0)
    if dt_min > 0.0 and dt_min < 1e-12:
        issues.append(_warn("DT_MIN_TINY", f"dt_min extremely small ({dt_min:.3g}); likely stiffness/instability."))

    return issues

def validate_plateau(df: pd.DataFrame) -> List[Issue]:
    issues: List[Issue] = []
    if df is None or df.empty or "Omega" not in df.columns:
        return issues
    if "accepted" in df.columns:
        df2 = df[df["accepted"] == 1].copy()
    else:
        df2 = df.copy()
    if len(df2) < 20:
        return issues

    omega = pd.to_numeric(df2["Omega"], errors="coerce").to_numpy()
    omega = omega[np.isfinite(omega)]
    if len(omega) < 20:
        return issues

    tail = omega[-20:]
    diffs = np.diff(tail)
    scale = max(1.0, float(np.nanmax(np.abs(tail))))
    drift = float(np.nanmean(np.abs(diffs)))
    if drift > 1e-6 * scale:
        issues.append(_warn("NO_PLATEAU", f"Tail drift not small: mean|ΔΩ|={drift:.3g} (scale={scale:.3g})."))
    return issues

def validate_conflict(summary: dict, df: pd.DataFrame) -> List[Issue]:
    issues: List[Issue] = []
    if summary is None or df is None or df.empty:
        return issues

    status = str(summary.get("status", "")).upper()
    nan_inf = bool(summary.get("nan_inf_detected", False))
    blowup = bool(summary.get("blowup_detected", False))

    if status == "PASS" and (nan_inf or blowup):
        issues.append(_fail("PASS_WITH_NAN_OR_BLOWUP", "summary says PASS but nan_inf/blowup flag is true."))

    # Endpoint consistency (Omega0/OmegaT vs timeseries)
    if "Omega" in df.columns:
        if "accepted" in df.columns:
            acc = df[df["accepted"] == 1]
        else:
            acc = df
        if not acc.empty:
            omega0_ts = float(pd.to_numeric(acc["Omega"], errors="coerce").iloc[0])
            omegaT_ts = float(pd.to_numeric(acc["Omega"], errors="coerce").iloc[-1])
            try:
                omega0 = float(summary.get("Omega0", np.nan))
                omegaT = float(summary.get("OmegaT", np.nan))
                scale = max(1.0, abs(omega0), abs(omegaT), abs(omega0_ts), abs(omegaT_ts))
                if np.isfinite(omega0) and np.isfinite(omega0_ts) and abs(omega0 - omega0_ts) > 1e-7 * scale:
                    issues.append(_warn("OMEGA0_MISMATCH", f"Omega0 mismatch: summary={omega0:.6g} ts={omega0_ts:.6g}"))
                if np.isfinite(omegaT) and np.isfinite(omegaT_ts) and abs(omegaT - omegaT_ts) > 1e-7 * scale:
                    issues.append(_warn("OMEGAT_MISMATCH", f"OmegaT mismatch: summary={omegaT:.6g} ts={omegaT_ts:.6g}"))
            except Exception:
                pass

    # PASS requires at least one accepted step
    if status == "PASS":
        sa = int(summary.get("steps_accepted", 0) or 0)
        if sa <= 0:
            issues.append(_fail("PASS_WITHOUT_ACCEPTED", "PASS but steps_accepted==0."))

    return issues


# --- New Gate Definitions ---

def no_nan_gate(df: pd.DataFrame, cfg: dict) -> GateResult:
    """Check for NaN or Inf in the timeseries, ignoring optional empty columns."""
    if df is None or df.empty:
        return GateResult("no_nan", "FAIL", 0.0, 0.0, "Empty timeseries")
    
    # We only care about core columns or columns that actually have numeric data
    # Optional columns in C_only (like mean_I) might be empty strings which pandas reads as NaN
    core_cols = ["step", "t", "Omega", "dt", "accepted", "backtracks"]
    available_core = [c for c in core_cols if c in df.columns]
    
    for col in available_core:
        vals = pd.to_numeric(df[col], errors="coerce").to_numpy()
        if not np.isfinite(vals).all():
            return GateResult("no_nan", "FAIL", 1.0, 0.0, f"NaN/Inf detected in core column: {col}")
    
    # For other columns, only fail if they are NOT entirely NaN (meaning something went wrong during valid run)
    other_cols = [c for c in df.columns if c not in core_cols]
    for col in other_cols:
        series = pd.to_numeric(df[col], errors="coerce")
        if series.notnull().any(): # If it has at least one number
            if not np.isfinite(series.dropna().to_numpy()).all():
                return GateResult("no_nan", "FAIL", 1.0, 0.0, f"NaN/Inf detected in column: {col}")
    
    return GateResult("no_nan", "PASS", 0.0, 0.0, "All values are finite")

def monotone_omega_gate(df: pd.DataFrame, cfg: dict) -> GateResult:
    """Ensure Omega is mostly decreasing (for UET)."""
    issues = validate_monotone(df, cfg)
    status = overall_grade(issues)
    
    # Extract max increase for the 'value' field
    if df is not None and "Omega" in df.columns:
        if "accepted" in df.columns:
            omega = df[df["accepted"] == 1]["Omega"].to_numpy()
        else:
            omega = df["Omega"].to_numpy()
        if len(omega) > 1:
            max_inc = float(np.max(np.diff(omega)))
        else:
            max_inc = 0.0
    else:
        max_inc = 0.0
        
    tol = float((cfg.get("time", {}) or {}).get("tol_abs", 1e-10)) * 10.0
    msg = issues[0].message if issues else "Omega is monotone"
    return GateResult("monotone_omega", status, max_inc, tol, msg)

def com_drift_gate(df: pd.DataFrame, cfg: dict) -> GateResult:
    """Check Center-of-Mass drift (displacement <= 1e-4 L)."""
    if df is None or "com" not in df.columns:
        return GateResult("com_drift", "WARN", 0.0, 0.0, "COM metric not recorded")
    
    com_vals = df["com"].dropna().to_numpy()
    if len(com_vals) < 2:
        return GateResult("com_drift", "PASS", 0.0, 0.0, "Not enough COM data")
    
    L = float((cfg.get("domain", {}) or {}).get("L", 1.0))
    drift = float(np.max(np.abs(com_vals - com_vals[0])))
    tol = 1e-4 * L
    
    status = "PASS" if drift <= tol else "FAIL"
    return GateResult("com_drift", status, drift, tol, f"COM drift: {drift:.3g} (tol={tol:.3g})")

def dt_convergence_gate(df: pd.DataFrame, cfg: dict) -> GateResult:
    """Check if final dt is within safe bounds computed by auto_scale."""
    if df is None or "dt" not in df.columns:
        return GateResult("dt_convergence", "WARN", 0.0, 0.0, "dt column missing")
    
    final_dt = float(df["dt"].iloc[-1])
    # Note: A real convergence check would compare dt vs dt/2 runs.
    # Here we just check if it stayed below initial dt or some safety factor.
    init_dt = float((cfg.get("time", {}) or {}).get("dt", 0.1))
    
    status = "PASS" if final_dt <= init_dt * 1.01 else "WARN"
    return GateResult("dt_convergence", status, final_dt, init_dt, f"Final dt={final_dt:.3g} (init={init_dt:.3g})")

def uet_smoke_gate(df: pd.DataFrame, cfg: dict) -> GateResult:
    """Pass if the timeseries exists and has data (meaning run finished)."""
    if df is not None and not df.empty:
        return GateResult("uet_smoke", "PASS", 1.0, 1.0, "Run completed successfully")
    return GateResult("uet_smoke", "FAIL", 0.0, 1.0, "Run did not produce timeseries data")

def determinism_gate(run_dir: Path, cfg: dict) -> GateResult:
    """
    Placeholder for determinism check.
    In a full implementation, this would compare the current run to a baseline.
    """
    return GateResult("determinism", "WARN", 0.0, 0.0, "Determinism check requires comparison run (TODO)")

# --- Gate Registry and Runner ---

GATES_MAP = {
    "no_nan": no_nan_gate,
    "monotone_omega": monotone_omega_gate,
    "com_drift": com_drift_gate,
    "dt_convergence": dt_convergence_gate,
    "uet_smoke": uet_smoke_gate,
}

def run_gates(run_dir: Path, out_path: Optional[Path] = None) -> List[GateResult]:
    """
    Load artifacts from run_dir, execute requested gates from config,
    and save report to gate_report.json.
    """
    run_dir = Path(run_dir)
    cfg, df, summ, base_issues = validate_artifacts(run_dir)
    
    if cfg is None:
        return [GateResult("loading", "FAIL", 0.0, 0.0, "Failed to load config for gates")]
    
    requested_gates = (cfg.get("validation", {}) or {}).get("gates", [])
    if not requested_gates:
        # Default gates if none specified
        requested_gates = ["no_nan", "uet_smoke"]
    
    results = []
    for gate_id in requested_gates:
        if isinstance(gate_id, dict):
            gate_id = gate_id.get("id")
            
        if gate_id in GATES_MAP:
            results.append(GATES_MAP[gate_id](df, cfg))
        elif gate_id == "determinism":
            results.append(determinism_gate(run_dir, cfg))
        else:
            results.append(GateResult(gate_id, "WARN", 0.0, 0.0, f"Unknown gate: {gate_id}"))
            
    # Save report
    if out_path or run_dir:
        report_path = out_path if out_path else run_dir / "gate_report.json"
        report = {
            "summary": {
                "overall_status": overall_grade([Issue(r.status, r.id, r.message) for r in results]),
                "gates_passed": sum(1 for r in results if r.status == "PASS"),
                "gates_total": len(results)
            },
            "gates": [r._asdict() for r in results]
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
    return results
