"""
Muon g-2 benchmark shift diagnosis
==================================
Topic: 0.8 Muon g-2 Anomaly
Goal: Quantify why the topic moved from a legacy pass to a strict 2025 fail.
"""

from __future__ import annotations

import json
import math
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


root_path = ROOT_PATH
topic_dir = root_path / "docs" / "topics" / "0.8_Muon_g2_Anomaly"
legacy_json = topic_dir / "Data" / "03_Research" / "fermilab_g2_2023.json"
exp_2025_json = root_path / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "fermilab_muon_g2_2025_experiment.json"
theory_2025_json = (
    root_path
    / "docs"
    / "data"
    / "external"
    / "particle_physics"
    / "muon_g2"
    / "theory"
    / "muon_g2_theory_2025_total_sm.json"
)
engine_path = topic_dir / "Code" / "01_Engine"

if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from Engine_Muon_G2 import UETMuonG2Solver


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def legacy_uet_reference() -> float:
    return 2.51e-9


def engine_uet_prediction() -> float:
    solver = UETMuonG2Solver()
    return solver.calculate_uet_correction()


def main() -> int:
    legacy = load_json(legacy_json)
    exp_2025 = load_json(exp_2025_json)
    theory_2025 = load_json(theory_2025_json)

    legacy_delta = legacy["data"]["delta_a_mu"]["value"]
    legacy_error = legacy["data"]["delta_a_mu"]["error"]
    exp_value_2025 = exp_2025["data"]["a_mu_exp"]
    exp_error_2025 = exp_2025["data"]["combined_error"]
    sm_value_2025 = theory_2025["data"]["a_mu_sm_total"]["value"]
    sm_error_2025 = theory_2025["data"]["a_mu_sm_total"]["uncertainty"]

    derived_delta_2025 = exp_value_2025 - sm_value_2025
    derived_error_2025 = math.sqrt(exp_error_2025**2 + sm_error_2025**2)
    legacy_reference_delta = legacy_uet_reference()
    engine_delta = engine_uet_prediction()

    legacy_reference_z_2023 = abs(legacy_reference_delta - legacy_delta) / legacy_error
    legacy_reference_z_2025 = abs(legacy_reference_delta - derived_delta_2025) / derived_error_2025
    engine_z_2025 = abs(engine_delta - derived_delta_2025) / derived_error_2025

    artifact = generate_artifact(
        topic="0.8_Muon_g2_Anomaly",
        dataset_hash=hash_dataset(
            {
                "legacy_source": str(legacy_json.relative_to(root_path)),
                "experiment_2025_source": str(exp_2025_json.relative_to(root_path)),
                "theory_2025_source": str(theory_2025_json.relative_to(root_path)),
            }
        ),
        results={
            "legacy_delta_a_mu": legacy_delta,
            "legacy_error": legacy_error,
            "legacy_reference_delta": legacy_reference_delta,
            "legacy_reference_z_score_2023": legacy_reference_z_2023,
            "legacy_reference_z_score_2025": legacy_reference_z_2025,
            "derived_delta_a_mu_2025": derived_delta_2025,
            "derived_error_2025": derived_error_2025,
            "engine_uet_delta": engine_delta,
            "engine_z_score_2025": engine_z_2025,
            "delta_shift": derived_delta_2025 - legacy_delta,
            "relative_gap_retention_percent": (derived_delta_2025 / legacy_delta) * 100.0,
        },
        config={
            "legacy_comparator": str(legacy_json.relative_to(root_path)),
            "experiment_2025_source_locked": str(exp_2025_json.relative_to(root_path)),
            "theory_2025_source_locked": str(theory_2025_json.relative_to(root_path)),
        },
        metrics={
            "legacy_delta_times_1e9": legacy_delta * 1e9,
            "derived_delta_2025_times_1e9": derived_delta_2025 * 1e9,
            "gap_shift_times_1e9": (derived_delta_2025 - legacy_delta) * 1e9,
            "legacy_reference_times_1e9": legacy_reference_delta * 1e9,
            "engine_uet_delta_times_1e9": engine_delta * 1e9,
            "legacy_reference_z_score_2023": legacy_reference_z_2023,
            "legacy_reference_z_score_2025": legacy_reference_z_2025,
            "engine_z_score_2025": engine_z_2025,
            "relative_gap_retention_percent": (derived_delta_2025 / legacy_delta) * 100.0,
        },
        thresholds={"max_compatibility_z_score": 2.0},
        notes=(
            "This diagnosis compares the older 2023 legacy discrepancy package against the "
            "strict 2025 source-locked experiment-plus-theory benchmark."
        ),
    )

    out_path = topic_dir / "Result" / "artifacts" / "muon_g2_benchmark_shift.json"
    save_artifact(artifact, out_path)

    print("=" * 60)
    print("MUON g-2 BENCHMARK SHIFT DIAGNOSIS")
    print("=" * 60)
    print(f"Legacy delta_a_mu:       {legacy_delta*1e9:.3f} x 10^-9")
    print(f"Strict 2025 delta_a_mu:  {derived_delta_2025*1e9:.3f} x 10^-9")
    print(f"Gap retention:           {(derived_delta_2025 / legacy_delta) * 100.0:.2f}%")
    print(f"Gap shift:               {(derived_delta_2025 - legacy_delta)*1e9:.3f} x 10^-9")
    print(f"Legacy hardcoded UET:    {legacy_reference_delta*1e9:.3f} x 10^-9")
    print(f"Current engine UET:      {engine_delta*1e9:.3f} x 10^-9")
    print(f"Legacy hardcoded z (2023): {legacy_reference_z_2023:.2f}")
    print(f"Legacy hardcoded z (2025): {legacy_reference_z_2025:.2f}")
    print(f"Current engine z (2025):   {engine_z_2025:.2f}")
    print(f"Artifact saved to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
