"""
Electroweak Higgs-branch diagnosis
==================================
Compares the legacy raw-angle Higgs branch against the current running-angle
branch and records why the updated branch closes the PDG mismatch without
changing the runtime kappa.
"""

from __future__ import annotations

import math
import sqlite3
import sys
from pathlib import Path


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


from docs import ROOT_PATH
from docs.core.reproducibility import generate_artifact, hash_dataset, save_artifact
from docs.core.uet_parameters import get_params


root_path = ROOT_PATH
topic_dir = root_path / "docs" / "topics" / "0.6_Electroweak_Physics"
engine_path = topic_dir / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from Engine_Electroweak import UETElectroweakSolver, V_EW


PDG_DB = root_path / "docs" / "data" / "external" / "particle_physics" / "pdg" / "pdg-2025-v0.2.2.sqlite"


def load_higgs_mass() -> float:
    con = sqlite3.connect(PDG_DB)
    cur = con.cursor()
    particle = cur.execute("select pdgid from pdgparticle where name='H' limit 1").fetchone()
    if not particle:
        raise KeyError("PDG Higgs entry not found")
    pdgid = particle[0]
    row = cur.execute(
        """
        select value from pdgdata
        where pdgid=? and edition='2025' and in_summary_table=1
        order by sort
        limit 1
        """,
        (pdgid + "M",),
    ).fetchone()
    con.close()
    if not row:
        raise KeyError("PDG Higgs mass not found")
    return float(row[0])


def run_test() -> bool:
    print("=" * 72)
    print("UET ELECTROWEAK HIGGS-BRANCH DIAGNOSIS")
    print("=" * 72)

    params = get_params("0.6")
    solver = UETElectroweakSolver(params=params)
    result = solver.solve()
    pdg_h = load_higgs_mass()

    sin2_seed = 0.25
    _, sin2_running, _ = solver.weinberg_angle_geometric()
    legacy_lambda = params.kappa * sin2_seed
    current_lambda = params.kappa * sin2_running
    legacy_higgs_mass = math.sqrt(2 * legacy_lambda) * V_EW
    current_higgs_mass = math.sqrt(2 * current_lambda) * V_EW
    legacy_relative_error_percent = abs(legacy_higgs_mass - pdg_h) / pdg_h * 100.0
    current_relative_error_percent = abs(current_higgs_mass - pdg_h) / pdg_h * 100.0

    print(f"Runtime kappa:         {params.kappa:.9f}")
    print(f"Legacy Higgs mass:     {legacy_higgs_mass:.6f} GeV")
    print(f"Current Higgs mass:    {result.m_Higgs_predicted:.6f} GeV")
    print(f"PDG Higgs mass:        {pdg_h:.6f} GeV")
    print(f"Legacy rel. error:     {legacy_relative_error_percent:.3f}%")
    print(f"Current rel. error:    {current_relative_error_percent:.3f}%")
    print(f"Running sin^2(theta):  {sin2_running:.9f}")

    artifact = generate_artifact(
        topic="0.6_Electroweak_Physics",
        dataset_hash=hash_dataset(
            {
                "pdg_db": str(PDG_DB.relative_to(root_path)),
                "runtime_kappa": params.kappa,
                "legacy_higgs_mass": legacy_higgs_mass,
                "current_higgs_mass": result.m_Higgs_predicted,
                "pdg_higgs_mass": pdg_h,
            }
        ),
        results={
            "status": "DIAGNOSIS",
            "runtime_kappa": params.kappa,
            "sin2_theta_w_running": sin2_running,
            "legacy_higgs_mass": legacy_higgs_mass,
            "current_higgs_mass": result.m_Higgs_predicted,
            "pdg_higgs_mass": pdg_h,
            "legacy_relative_error_percent": legacy_relative_error_percent,
            "current_relative_error_percent": current_relative_error_percent,
        },
        config={
            "source_locked_reference": str(PDG_DB.relative_to(root_path)),
            "legacy_higgs_formula": "m_H = sqrt(2 * kappa * 0.25) * V_EW",
            "current_higgs_formula": "m_H = sqrt(2 * kappa * sin2_theta_W_running) * V_EW",
        },
        metrics={
            "legacy_relative_error_percent": legacy_relative_error_percent,
            "current_relative_error_percent": current_relative_error_percent,
        },
        thresholds={"advisory_only": True},
        notes=(
            "Diagnostic artifact only. It compares the legacy raw-angle Higgs branch "
            "against the current running-angle branch under the same runtime kappa."
        ),
    )
    artifact_path = topic_dir / "Result" / "artifacts" / "electroweak_higgs_diagnosis.json"
    save_artifact(artifact, artifact_path)
    print(f"Artifact saved to {artifact_path}")
    return True


if __name__ == "__main__":
    sys.exit(0 if run_test() else 1)
