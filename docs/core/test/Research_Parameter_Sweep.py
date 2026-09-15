"""
UET Research Parameter Sweep (The "Brutal Tester" Restoration)
==============================================================
Replicates the rigorous "Cross-Sweep" methodology from v0.9.0.

Objective:
    Map the Stability Phase Space of the UET Master Equation (V3.0).
    Compare the interaction of:
    - Beta (Competition/Feedback)
    - Gamma_J (Interaction/Exchange) [Mapped from Legacy 's']

Output:
    A CSV matrix (UET_V3_Parameter_Matrix.csv) detailing:
    - Stability (Stable/Exploded)
    - Final Energy (Omega)
    - Complexity (Gradients)
    - Information Density (I_total)

This restores the "Glass Box" visibility into the engine's phase space.
"""

import numpy as np
import pandas as pd
import sys

from docs.core.core_paths import repo_root as _repo_root


# === SETUP: Import Core Engine ===
REPO_ROOT = _repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from docs.core.uet_master_equation import UETParameters, UETMasterEquation

# === CONFIGURATION ===
BETA_RANGE = np.linspace(1.0, 5.0, 20)  # Competition Strength
GAMMA_J_RANGE = np.linspace(
    0.0, 1.0, 20
)  # Interaction/Exchange Strength ('s' in legacy)
STEPS = 500  # Enough to see divergence
DT = 0.01

OUTPUT_FILE = REPO_ROOT / "Data" / "03_Research" / "UET_V3_Parameter_Matrix.csv"


def run_single_experiment(beta, gamma_J):
    """Run a single parameter point simulation."""
    params = UETParameters(
        beta=beta, gamma_J=gamma_J, alpha=1.0, kappa=0.1, C0=0.0  # Standard Stiffness
    )

    engine = UETMasterEquation(params)

    # Init Fields (Perturbed Zero)
    nx = 32  # Keep it fast for sweep
    C = np.random.normal(0, 0.1, nx)
    J_in = np.ones(nx) * 0.1
    J_out = np.ones(nx) * 0.1
    I = np.random.normal(0, 0.1, nx)  # Information field

    # Run
    for _ in range(STEPS):
        try:
            C = engine.step(C, dt=DT, dx=0.1, I=I, J_in=J_in, J_out=J_out)
        except Exception as e:
            return {"status": "CRASH", "omega": np.nan, "C_max": np.nan}

        # Check blowup
        if np.max(np.abs(C)) > 100.0:
            return {"status": "EXPLODED", "omega": np.nan, "C_max": np.max(np.abs(C))}

    # Final Metrics
    omega = engine.compute_omega(C, dx=0.1, I=I, J_in=J_in, J_out=J_out)

    return {
        "status": "STABLE",
        "omega": omega,
        "C_max": np.max(np.abs(C)),
        "C_std": np.std(C),
        "I_coupling_strength": np.mean(C * I),
    }


def main():
    print(f"🚀 Starting UET V3 Parameter Sweep (The 'Brutal' Matrix)...")
    print(
        f"   Beta Range: {BETA_RANGE[0]} - {BETA_RANGE[-1]} ({len(BETA_RANGE)} steps)"
    )
    print(
        f"   Gamma_J Range: {GAMMA_J_RANGE[0]} - {GAMMA_J_RANGE[-1]} ({len(GAMMA_J_RANGE)} steps)"
    )
    print(f"   Total Runs: {len(BETA_RANGE) * len(GAMMA_J_RANGE)}")

    results = []

    # Create Data Dir if not exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Loop
    total_runs = len(BETA_RANGE) * len(GAMMA_J_RANGE)
    count = 0
    print(f"   Progress: 0/{total_runs}", end="\r")

    for beta in BETA_RANGE:
        for gamma_J in GAMMA_J_RANGE:
            res = run_single_experiment(beta, gamma_J)

            row = {
                "beta": beta,
                "gamma_J": gamma_J,
                "status": res["status"],
                "omega_final": res["omega"],
                "C_max": res["C_max"],
                "C_std": res.get("C_std", 0.0),
                "I_coupling": res.get("I_coupling_strength", 0.0),
            }
            results.append(row)
            count += 1
            if count % 10 == 0:
                print(f"   Progress: {count}/{total_runs}", end="\r")

    # Save
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✅ Sweep Complete!")
    print(f"💾 Data Saved: {OUTPUT_FILE}")
    print(f"   Stable Runs: {len(df[df['status']=='STABLE'])}")
    print(f"   Exploded Runs: {len(df[df['status']=='EXPLODED'])}")

    # Quick Analysis
    stable_df = df[df["status"] == "STABLE"]
    if not stable_df.empty:
        best_run = stable_df.loc[stable_df["omega_final"].idxmin()]
        print(f"\n🏆 Best Stability Candidate:")
        print(f"   Beta: {best_run['beta']:.2f}")
        print(f"   Gamma_J: {best_run['gamma_J']:.2f}")
        print(f"   Omega: {best_run['omega_final']:.4f}")


if __name__ == "__main__":
    main()
