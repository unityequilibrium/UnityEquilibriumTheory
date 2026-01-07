#!/usr/bin/env python
"""
Value and Conflict Metrics for UET.

Value: สิ่งดีที่ระบบได้รับจากการถึงสมดุล
Conflict: ต้นทุน/อุปสรรคที่ระบบต้องจ่าย
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd
from pathlib import Path
import json


@dataclass
class ValueMetrics:
    """Value metrics from simulation."""
    V_E: float          # Energy-based value: -Ω_final
    V_dE: float         # Energy reduction: Ω_0 - Ω_final
    V_R: float          # Robustness: max phase probability


@dataclass
class ConflictMetrics:
    """Conflict metrics from simulation."""
    C_G: float          # Gradient-cost: Ω_grad_final
    C_F: float          # Friction: backtrack count
    C_O: float          # Oscillation: variance of tail
    C_M: float          # Multi-attractor: 1 - V_R


@dataclass
class ValueConflictReport:
    """Combined V/C metrics."""
    value: ValueMetrics
    conflict: ConflictMetrics
    
    def to_dict(self) -> dict:
        return {
            "V_E": self.value.V_E,
            "V_dE": self.value.V_dE,
            "V_R": self.value.V_R,
            "C_G": self.conflict.C_G,
            "C_F": self.conflict.C_F,
            "C_O": self.conflict.C_O,
            "C_M": self.conflict.C_M,
            # Derived
            "net_value": self.value.V_dE - self.conflict.C_G,
            "efficiency": self.value.V_dE / max(1.0, self.conflict.C_F + 1),
        }


def compute_value_metrics(
    Omega_0: float,
    Omega_final: float,
    phase_counts: Optional[dict] = None,
) -> ValueMetrics:
    """
    Compute Value metrics.
    
    Args:
        Omega_0: Initial energy
        Omega_final: Final energy
        phase_counts: Dict of phase counts (optional, for V_R)
        
    Returns:
        ValueMetrics
    """
    # V_E: Energy-based value (negative of final energy)
    V_E = -Omega_final
    
    # V_dE: Energy reduction (how much energy was released)
    V_dE = Omega_0 - Omega_final
    
    # V_R: Robustness (phase consistency)
    if phase_counts:
        total = sum(phase_counts.values())
        if total > 0:
            V_R = max(phase_counts.values()) / total
        else:
            V_R = 0.0
    else:
        V_R = 1.0  # Single run = 100% consistent
    
    return ValueMetrics(V_E=V_E, V_dE=V_dE, V_R=V_R)


def compute_conflict_metrics(
    Omega_grad_final: float,
    backtrack_count: int,
    Omega_tail: Optional[np.ndarray] = None,
    bias_tail: Optional[np.ndarray] = None,
    V_R: float = 1.0,
) -> ConflictMetrics:
    """
    Compute Conflict metrics.
    
    Args:
        Omega_grad_final: Final gradient energy component
        backtrack_count: Total backtrack count during simulation
        Omega_tail: Last N Omega values for oscillation check
        bias_tail: Last N bias values for oscillation check
        V_R: Robustness value (for C_M calculation)
        
    Returns:
        ConflictMetrics
    """
    # C_G: Gradient-cost (surface tension at end)
    C_G = Omega_grad_final
    
    # C_F: Friction (difficulty of simulation)
    C_F = float(backtrack_count)
    
    # C_O: Oscillation (non-settling)
    if Omega_tail is not None and len(Omega_tail) > 1:
        var_omega = float(np.var(Omega_tail))
        var_bias = float(np.var(bias_tail)) if bias_tail is not None else 0.0
        C_O = var_omega + var_bias
    else:
        C_O = 0.0
    
    # C_M: Multi-attractor conflict
    C_M = 1.0 - V_R
    
    return ConflictMetrics(C_G=C_G, C_F=C_F, C_O=C_O, C_M=C_M)


def compute_vc_from_summary(summary: dict, timeseries: Optional[pd.DataFrame] = None) -> ValueConflictReport:
    """
    Compute full V/C report from summary.json and optional timeseries.
    
    Args:
        summary: summary.json dict
        timeseries: Optional timeseries DataFrame
        
    Returns:
        ValueConflictReport
    """
    Omega_0 = summary.get("Omega0", 0.0)
    Omega_final = summary.get("OmegaT", 0.0)
    backtrack_count = summary.get("dt_backtracks_total", 0)
    
    # Value metrics
    value = compute_value_metrics(Omega_0, Omega_final)
    
    # For Omega_grad_final, we need decomposed energy (not always available)
    Omega_grad_final = 0.0  # Default, would need omega_CI_decomposed
    
    # Tail analysis for oscillation
    Omega_tail = None
    bias_tail = None
    if timeseries is not None and len(timeseries) > 10:
        tail_n = min(20, len(timeseries) // 5)
        Omega_tail = timeseries["Omega"].tail(tail_n).values
        if "bias_CI" in timeseries.columns:
            bias_tail = timeseries["bias_CI"].tail(tail_n).values
    
    # Conflict metrics
    conflict = compute_conflict_metrics(
        Omega_grad_final=Omega_grad_final,
        backtrack_count=backtrack_count,
        Omega_tail=Omega_tail,
        bias_tail=bias_tail,
        V_R=value.V_R,
    )
    
    return ValueConflictReport(value=value, conflict=conflict)


def add_vc_to_summary(case_dir: Path) -> dict:
    """
    Add V/C metrics to an existing summary.json.
    
    Args:
        case_dir: Path to case directory
        
    Returns:
        Updated summary dict with V/C metrics
    """
    summary_path = case_dir / "summary.json"
    timeseries_path = case_dir / "timeseries.csv"
    
    with open(summary_path) as f:
        summary = json.load(f)
    
    timeseries = None
    if timeseries_path.exists():
        timeseries = pd.read_csv(timeseries_path)
    
    vc = compute_vc_from_summary(summary, timeseries)
    
    # Add to summary
    summary.update(vc.to_dict())
    
    # Save updated summary
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    return summary


def batch_add_vc(runs_dir: Path) -> pd.DataFrame:
    """
    Add V/C metrics to all cases in a runs directory.
    
    Returns:
        DataFrame with all summaries including V/C metrics
    """
    summaries = []
    
    for case_dir in runs_dir.iterdir():
        if case_dir.is_dir() and (case_dir / "summary.json").exists():
            try:
                summary = add_vc_to_summary(case_dir)
                summaries.append(summary)
                print(f"✅ Added V/C to {case_dir.name}")
            except Exception as e:
                print(f"❌ Failed for {case_dir.name}: {e}")
    
    return pd.DataFrame(summaries)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Compute Value/Conflict Metrics")
    parser.add_argument("path", help="Path to case directory or runs directory")
    parser.add_argument("--batch", action="store_true", help="Process all cases in directory")
    parser.add_argument("--output", "-o", help="Output CSV for batch mode")
    
    args = parser.parse_args()
    path = Path(args.path)
    
    if args.batch:
        df = batch_add_vc(path)
        if args.output:
            df.to_csv(args.output, index=False)
            print(f"\n📊 Saved to {args.output}")
        else:
            print(df[["case_id", "V_dE", "V_R", "C_F", "C_O", "net_value"]].to_string())
    else:
        summary = add_vc_to_summary(path)
        print("\n📊 Value/Conflict Metrics:")
        print(f"   V_E (Energy value):     {summary.get('V_E', 0):.4f}")
        print(f"   V_dE (Energy released): {summary.get('V_dE', 0):.4f}")
        print(f"   V_R (Robustness):       {summary.get('V_R', 0):.4f}")
        print(f"   C_G (Gradient cost):    {summary.get('C_G', 0):.4f}")
        print(f"   C_F (Friction):         {summary.get('C_F', 0):.0f}")
        print(f"   C_O (Oscillation):      {summary.get('C_O', 0):.6f}")
        print(f"   C_M (Multi-attractor):  {summary.get('C_M', 0):.4f}")
        print(f"   Net Value:              {summary.get('net_value', 0):.4f}")


if __name__ == "__main__":
    main()
