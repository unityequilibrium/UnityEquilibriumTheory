"""
UET Heavy Nuclei Test - Liquid Drop Surface Bridge
====================================================
Extension to cover heavy nuclei (A > 100) binding energies.

Bridge Equation:
    Ω = V(C) + κ|∇C|² + βCI + σ·A^(2/3)·f(C)
                              ↑
              Liquid Drop Surface term

The surface term adds nuclear surface contribution that pure UET soliton misses.

Data: AME2020 (Atomic Mass Evaluation)
DOI: 10.1088/1674-1137/abddaf
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

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


from docs.core.uet_glass_box import UETPathManager

import json
import numpy as np






# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def load_nuclei_data():
    """Load AME2020 heavy nuclei data."""
    # Define Data Path
    data_path = (
        root_path
        / "docs"
        / "topics"
        / "0.16_Heavy_Nuclei"
        / "Data"
        / "03_Research"
        / "ame2020_heavy"
        / "ame2020_heavy.json"
    )
    if not data_path.exists():
        data_path = root_path / "Data" / "03_Research" / "ame2020_heavy.json"

    if not data_path.exists():
        raise FileNotFoundError(f"Data not found at {data_path}")

    with open(data_path) as f:
        return json.load(f)


# --- SETUP ENGINE ---
ENGINE_PATH = (
    root_path / "docs" / "topics" / "0.16_Heavy_Nuclei" / "Code" / "01_Engine"
)
if str(ENGINE_PATH) not in sys.path:
    sys.path.append(str(ENGINE_PATH))

try:
    from Engine_Heavy_Nuclei import UETHeavyNucleiEngine

    engine = UETHeavyNucleiEngine()
except ImportError as e:
    print(f"CRITICAL: Failed to import Engine_Heavy_Nuclei: {e}")
    sys.exit(1)


def uet_soliton_be(Z, A):
    """
    Legacy Pure UET soliton model for binding energy.
    Included for comparison only.
    """
    return 8.5 * A - 0.5 * Z * (Z - 1) / (A ** (1 / 3))


def uet_liquid_drop_bridge(Z, A):
    """Bridge to the Central Engine."""
    return engine.uet_bridge_be(Z, A)


def run_test():
    """Test UET+Surface against heavy nuclei binding energies."""
    print("=" * 70)
    print("UET HEAVY NUCLEI TEST")
    print("Extension: Liquid Drop Surface Bridge Term")
    print("Data: AME2020 (DOI: 10.1088/1674-1137/abddaf)")
    print("=" * 70)

    data = load_nuclei_data()
    nuclei = data["nuclei"]

    print(f"\nTotal nuclei: {len(nuclei)} (all A > 100)")

    print("\n[1] COMPARISON: Pure Soliton vs UET+Surface")
    print("-" * 70)
    print(
        f"| {'Nucleus':<10} | {'BE_exp':>10} | {'Soliton':>10} | {'UET+LD':>10} | {'Err%':>7} |"
    )
    print("-" * 70)

    results = []
    for n in nuclei:
        Z, A = n["Z"], n["A"]
        BE_exp = n["BE_MeV"]

        BE_soliton = uet_soliton_be(Z, A)
        BE_uet_ld = uet_liquid_drop_bridge(Z, A)

        err_soliton = abs(BE_soliton - BE_exp) / BE_exp * 100
        err_uet_ld = abs(BE_uet_ld - BE_exp) / BE_exp * 100

        results.append(err_uet_ld < 5)

        status = "✓" if err_uet_ld < 5 else "~"
        print(
            f"| {n['name']:<10} | {BE_exp:>10.1f} | {BE_soliton:>10.1f} | {BE_uet_ld:>10.1f} | {err_uet_ld:>6.2f}% {status}|"
        )

    print("-" * 70)

    passed = sum(results)
    pass_rate = passed / len(results) * 100

    print(f"\n[2] SUMMARY")
    print("-" * 70)
    print(
        f"  UET + Liquid Drop Surface: {pass_rate:.0f}% pass ({passed}/{len(results)})"
    )

    print("\n[3] BRIDGE EQUATION")
    print("-" * 70)
    print(
        """
    Ω = V(C) + κ|∇C|² + βCI + σ·A^(2/3)·f(C)
                              ↑
              Surface term (from Bethe-Weizsacker)
    
    σ = 17.8 MeV (nuclear surface tension)
    
    UET Interpretation:
    - Surface = C-field gradient discontinuity at nucleus boundary
    - σ relates κ to nuclear physics scales
    - Bridges UET with established liquid drop model
    """
    )

    print("=" * 70)
    overall = pass_rate >= 70
    print(
        f"RESULT: {'PASS' if overall else 'NEEDS WORK'} - UET+Surface explains heavy nuclei"
    )
    print("=" * 70)

    # ---------------------------------------------------------
    # VISUALIZATION INJECTION
    # ---------------------------------------------------------
    try:
        import docs.core.uet_viz as viz
        import plotly.graph_objects as go

        # Path: 3 levels up from script to topic root
        TOPIC_DIR = Path(__file__).resolve().parent.parent.parent

        # Prepare Data
        x_A = []
        y_exp = []
        y_uet = []
        names = []

        # Sort by Mass Number A
        sorted_nuclei = sorted(nuclei, key=lambda x: x["A"])

        for n in sorted_nuclei:
            A = n["A"]
            Z = n["Z"]
            x_A.append(A)

            # Binding Energy PER NUCLEON
            y_exp.append(n["BE_MeV"] / A)
            y_uet.append(uet_liquid_drop_bridge(Z, A) / A)
            names.append(n["name"])

        # Create Figure
        fig = go.Figure()

        # 1. Experimental Data
        fig.add_trace(
            go.Scatter(
                x=x_A,
                y=y_exp,
                mode="markers",
                name="Experimental Data (AME2020)",
                text=names,
                marker=dict(size=8, color="cyan", opacity=0.7),
            )
        )

        # 2. UET+LD Prediction
        fig.add_trace(
            go.Scatter(
                x=x_A,
                y=y_uet,
                mode="lines",
                name="UET + Liquid Drop Surface",
                line=dict(color="orange", width=3),
            )
        )

        # Layout
        fig.update_layout(
            title="Heavy Nuclei Binding Energy per Nucleon (UET+Surface Bridge)",
            xaxis_title="Mass Number (A)",
            yaxis_title="Binding Energy / Nucleon (MeV)",
            template="plotly_dark",
        )

        # Save to Logger's run directory (Standardized)
        result_dir = Path(engine.logger.run_dir)
        viz.save_plot(fig, "heavy_binding_viz.png", str(result_dir))
        print(f"  [Viz] Generated 'heavy_binding_viz.png' in {result_dir}")

    except Exception as e:
        print(f"  [Viz] Error: {e}")
        import traceback

        traceback.print_exc()

    return overall


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
