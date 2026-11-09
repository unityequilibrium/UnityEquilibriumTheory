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

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---
from pathlib import Path
import sys

try:
    from docs.core.uet_glass_box import UETPathManager
except ImportError:
    pass

import math


def run_test():
    print("=" * 70)
    print("UET HIGGS MECHANISM VISUALIZATION")
    print("=" * 70)

    # UET interprets Higgs Potential V(C) as Information Capacity Limit
    # V(phi) = -mu^2 phi^2 + lambda phi^4
    # UET: V(C) = -alpha C^2 + beta C^4

    # --- VISUALIZATION ---
    try:
        from docs.core import uet_viz

        result_dir = (
            UETPathManager.get_result_dir(
                topic_id="0.6",
                experiment_name="Higgs_Mechanism",
                pillar="03_Research",
                category="showcase",
            )
            / "higgs_mass"
        )
        if not result_dir.exists():
            result_dir.mkdir(parents=True, exist_ok=True)

        import numpy as np

        phi = np.linspace(-300, 300, 100)  # GeV (VEV scale)
        # Standard fit
        v = 246.0
        lam = 0.13
        mu2 = lam * v**2
        V_sm = -mu2 * phi**2 + lam * phi**4

        # UET Information Potential (Slight correction needed?)
        # For now, UET matches SM form but interprets 'phi' as Capacity 'C'

        fig = uet_viz.go.Figure()
        fig.add_trace(
            uet_viz.go.Scatter(x=phi, y=V_sm, mode="lines", name="Higgs Potential")
        )

        # Mark VEV
        fig.add_trace(
            uet_viz.go.Scatter(
                x=[v, -v],
                y=[-mu2 * v**2 + lam * v**4] * 2,
                mode="markers",
                name="Vacuum State (VEV)",
                marker=dict(size=10, color="red"),
            )
        )

        fig.update_layout(
            title="Higgs Potential V(φ) [UET Information Capacity]",
            xaxis_title="Field Value φ (GeV)",
            yaxis_title="Potential V(φ)",
        )
        uet_viz.save_plot(fig, "higgs_potential.png", result_dir)
        print("  [Viz] Generated 'higgs_potential.png'")

        return True

    except Exception as e:
        print(f"Viz Error: {e}")
        return False


if __name__ == "__main__":
    run_test()
