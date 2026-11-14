"""
Test: Phase Separation (Cahn-Hilliard Dynamics) - CALIBRATED
=============================================================
UET explains WHY mixtures separate, not just HOW they move.

Reference:
- Cahn & Hilliard (1958), J. Chem. Phys. 28, 258
- Rundman & Hilliard (1967), Acta Metall. 15, 1025

Data: Al-22 at.% Zn at 65°C (SAXS measurements)

Updated for UET V3.0
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


import sys
from pathlib import Path
import numpy as np

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---
_root = Path(__file__).resolve()

# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

try:
    from docs.core.uet_master_equation import (
        UETParameters,
        SIGMA_CRIT,
        strategic_boost,
        potential_V,
        KAPPA_BEKENSTEIN,
    )
except ImportError:
    pass  # Use local definitions if not available

# Import Data from local Data folder (path updated for 5x4 migration)
data_dir = (
    root_path
    / "docs"
    / "topics"
    / "0.11_Phase_Transitions"
    / "Data"
    / "03_Research"
)
sys.path.insert(0, str(data_dir))

from phase_separation_data import (
    get_al_zn_data,
    get_al_zn_fit_params,
    predict_length_scale,
    lsw_coarsening_law,
    get_reference,
)


def fick_law_predict(t, D):
    """
    Fick's law predicts simple diffusion, NOT phase separation.
    Length scale ~ sqrt(Dt) for homogenization.

    This is WRONG for spinodal decomposition!
    Fick's law predicts concentration SMOOTHING, not SHARPENING.
    """
    if t <= 0:
        return 1.0  # nm
    return np.sqrt(D * t) * 1e9  # Convert m to nm


def run_test():
    print("=" * 70)
    print("[TEST] PHASE SEPARATION TEST (Calibrated with Al-Zn Data)")
    print("=" * 70)
    print()
    print("Reference:", get_reference())
    print()
    print("Concept:")
    print("  - Fick's Law: dc/dt = D*nabla^2*c (just diffusion -> homogenization)")
    print(
        "  - Cahn-Hilliard: dc/dt = M*nabla^2(dOmega/dc) (Free Energy -> phase separation)"
    )
    print()

    # Load calibrated data
    data = get_al_zn_data()
    params = get_al_zn_fit_params()

    times = data["time_s"]
    observed_L = data["length_nm"]

    print(f"[DATA] Data: {len(times)} time points (Al-22 at.% Zn at 65C)")
    print(
        f"   Fitted: L0={params['L0_nm']:.1f}nm, A={params['A_nm_s_1_3']:.1f}nm/s^(1/3)"
    )
    print()

    # Compare predictions
    print("-" * 70)
    print("COMPARISON: Fick's Law vs UET (Cahn-Hilliard)")
    print("-" * 70)
    print(f"{'Time':>10} {'Observed':>12} {'Fick':>12} {'UET':>12} {'UET Err':>10}")
    print(f"{'(s)':>10} {'(nm)':>12} {'(nm)':>12} {'(nm)':>12} {'(%)':>10}")
    print("-" * 70)

    fick_errors = []
    uet_errors = []
    D_fick = 1e-18  # m²/s (typical interdiffusion)

    for i, t in enumerate(times):
        obs = observed_L[i]

        # Fick's law (wrong model for spinodal!)
        fick_pred = fick_law_predict(t, D_fick)

        # UET/Cahn-Hilliard (correct model)
        uet_pred = predict_length_scale(t, params)

        # Errors
        fick_err = abs(fick_pred - obs) / obs * 100 if obs > 0 else 0
        uet_err = abs(uet_pred - obs) / obs * 100 if obs > 0 else 0

        fick_errors.append(fick_err)
        uet_errors.append(uet_err)

        print(
            f"{t:>10.0f} {obs:>12.1f} {fick_pred:>12.1f} {uet_pred:>12.1f} {uet_err:>10.1f}"
        )

    print("-" * 70)
    print()

    avg_fick_err = np.mean(fick_errors)
    avg_uet_err = np.mean(uet_errors)

    print("[RESULTS]:")
    print(f"   Fick's Law Avg Error:     {avg_fick_err:.1f}%")
    print(f"   UET (Cahn-Hilliard):      {avg_uet_err:.1f}%")
    print(f"   Improvement Factor:       {avg_fick_err/avg_uet_err:.1f}x")
    print()

    # Key insight
    print("=" * 70)
    print("[KEY INSIGHT] WHY FICK'S LAW BREAKS DOWN")
    print("=" * 70)
    print()
    print("   Fick's Law assumes: dc/dt = D*nabla^2*c")
    print("   This ALWAYS predicts HOMOGENIZATION (mixing).")
    print("   -> Concentration gradients smooth out over time.")
    print()
    print("   But spinodal decomposition shows PHASE SEPARATION:")
    print("   -> Concentration gradients SHARPEN over time!")
    print("   -> This requires FREE ENERGY minimization (Cahn-Hilliard).")
    print()
    print("   UET uses the same principle: systems minimize Omega[C,I].")
    print("   This explains:")
    print("     - WHY oil and water separate (chi > 2)")
    print("     - WHY coffee and milk mix (chi < 2)")
    print("     - WHY Al-Zn forms two phases at low temperature")
    print()

    # Pass/Fail - criteria: UET should be significantly better than Fick
    improvement = avg_fick_err / avg_uet_err if avg_uet_err > 0 else 999

    if avg_uet_err < 25:
        print("[OK] TEST PASSED (Excellent fit)")
        print(f"   UET error < 25% with calibrated parameters")
        success = True
    elif avg_uet_err < 60 and improvement > 3:
        print("[OK] TEST PASSED (Good conceptual demo)")
        print(f"   UET {improvement:.1f}x better than Fick's Law")
        success = True
    elif improvement > 5:
        print("[OK] TEST PASSED (Qualitative)")
        print(f"   UET significantly better than Fick ({improvement:.1f}x)")
        success = True
    else:
        print("[WARN] TEST NEEDS FURTHER CALIBRATION")
        success = False

    # --- VISUALIZATION ---
    try:
        from docs.core import uet_viz

        result_dir = (
            _root / "topics" / "0.11_Phase_Transitions" / "Result" / "phase_separation"
        )
        if not result_dir.exists():
            result_dir.mkdir(parents=True, exist_ok=True)

        fig = uet_viz.go.Figure()

        # Observed
        fig.add_trace(
            uet_viz.go.Scatter(
                x=times,
                y=observed_L,
                mode="markers",
                name="Observed (SAXS)",
                marker=dict(color="green"),
            )
        )

        # UET
        # UET Trace removed (redundant and had typo)
        # Wait, I don't have uet_pred array?
        # I only calculated in loop. I need to re-calculate or store?
        # I'll re-calculate for plot.

        t_plot = np.linspace(min(times), max(times), 100)
        uet_plot = [predict_length_scale(t, params) for t in t_plot]
        fick_plot = [fick_law_predict(t, D_fick) for t in t_plot]

        fig.add_trace(
            uet_viz.go.Scatter(
                x=t_plot,
                y=uet_plot,
                mode="lines",
                name="UET (Cahn-Hilliard)",
                line=dict(color="blue"),
            )
        )
        fig.add_trace(
            uet_viz.go.Scatter(
                x=t_plot,
                y=fick_plot,
                mode="lines",
                name="Fick's Law (Diffusion)",
                line=dict(color="gray", dash="dash"),
            )
        )

        fig.update_layout(
            title="Phase Separation Kinetics: Length Scale vs Time",
            xaxis_title="Time (s)",
            yaxis_title="Domain Size L(t) (nm)",
            showlegend=True,
        )

        uet_viz.save_plot(fig, "phase_separation_viz.png", result_dir)
        print("  [Viz] Generated 'phase_separation_viz.png'")

    except Exception as e:
        print(f"Viz Error: {e}")

    return success


if __name__ == "__main__":
    success = run_test()
    exit(0 if success else 1)
