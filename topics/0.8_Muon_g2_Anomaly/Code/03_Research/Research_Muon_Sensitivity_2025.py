"""Sensitivity analysis for the 2025 source-locked muon g-2 benchmark."""

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
experimental_json = root_path / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "fermilab_muon_g2_2025_experiment.json"
theory_json = root_path / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "theory" / "muon_g2_theory_2025_total_sm.json"
baseline_package_json = root_path / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "theory" / "muon_g2_baseline_package.json"
engine_path = topic_dir / "Code" / "01_Engine"

if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from Engine_Muon_G2 import UETMuonG2Solver


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def z_score(prediction: float, delta: float, exp_err: float, sm_err: float) -> float:
    combined = math.sqrt(exp_err**2 + sm_err**2)
    return abs(prediction - delta) / combined if combined else float("inf")


def main() -> int:
    legacy = load_json(legacy_json)
    exp = load_json(experimental_json)
    theory = load_json(theory_json)
    baseline_package = load_json(baseline_package_json)

    engine_delta = UETMuonG2Solver().calculate_uet_correction()
    legacy_reference_delta = 2.51e-9
    legacy_delta = legacy["data"]["delta_a_mu"]["value"]
    legacy_error = legacy["data"]["delta_a_mu"]["error"]
    exp_value = exp["data"]["a_mu_exp"]
    exp_error = exp["data"]["combined_error"]
    sm_value = theory["data"]["a_mu_sm_total"]["value"]
    sm_error = theory["data"]["a_mu_sm_total"]["uncertainty"]
    delta_2025 = exp_value - sm_value
    published_delta_2025 = theory["data"]["delta_a_mu_exp_minus_sm"]["value"]
    published_delta_2025_err = theory["data"]["delta_a_mu_exp_minus_sm"]["uncertainty"]
    nominal_engine_z = z_score(engine_delta, delta_2025, exp_error, sm_error)
    nominal_legacy_reference_z = z_score(legacy_reference_delta, delta_2025, exp_error, sm_error)
    legacy_2023_engine_z = abs(engine_delta - legacy_delta) / legacy_error if legacy_error else float("inf")
    legacy_2023_reference_z = abs(legacy_reference_delta - legacy_delta) / legacy_error if legacy_error else float("inf")

    baseline_comparison = [
        {
            "label": "legacy_2023_gap",
            "delta": legacy_delta,
            "uncertainty": legacy_error,
            "engine_z_score": legacy_2023_engine_z,
            "legacy_reference_z_score": legacy_2023_reference_z,
        },
        {
            "label": "published_2025_gap",
            "delta": published_delta_2025,
            "uncertainty": published_delta_2025_err,
            "engine_z_score": abs(engine_delta - published_delta_2025) / published_delta_2025_err if published_delta_2025_err else float("inf"),
            "legacy_reference_z_score": abs(legacy_reference_delta - published_delta_2025) / published_delta_2025_err if published_delta_2025_err else float("inf"),
        },
        {
            "label": "derived_2025_gap",
            "delta": delta_2025,
            "uncertainty": math.sqrt(exp_error**2 + sm_error**2),
            "engine_z_score": nominal_engine_z,
            "legacy_reference_z_score": nominal_legacy_reference_z,
        },
        {
            "label": "null_gap",
            "delta": 0.0,
            "uncertainty": math.sqrt(exp_error**2 + sm_error**2),
            "engine_z_score": abs(engine_delta) / math.sqrt(exp_error**2 + sm_error**2),
            "legacy_reference_z_score": abs(legacy_reference_delta) / math.sqrt(exp_error**2 + sm_error**2),
        },
    ]
    theory_package_comparison = []
    for entry in baseline_package["baselines"]:
        delta = entry["delta_a_mu"]
        uncertainty = entry["combined_uncertainty"]
        theory_package_comparison.append(
            {
                "label": entry["label"],
                "provenance_status": entry["provenance_status"],
                "delta": delta,
                "uncertainty": uncertainty,
                "engine_z_score": abs(engine_delta - delta) / uncertainty if uncertainty else float("inf"),
                "legacy_reference_z_score": abs(legacy_reference_delta - delta) / uncertainty if uncertainty else float("inf"),
                "is_canonical_verification_baseline": entry["label"] == baseline_package["canonical_verification_baseline"],
            }
        )

    sensitivity_grid = []
    for multiplier in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
        adjusted_sm_error = sm_error * multiplier
        engine_z = z_score(engine_delta, delta_2025, exp_error, adjusted_sm_error)
        legacy_z = z_score(legacy_reference_delta, delta_2025, exp_error, adjusted_sm_error)
        sensitivity_grid.append(
            {
                "sm_uncertainty_multiplier": multiplier,
                "adjusted_sm_uncertainty": adjusted_sm_error,
                "engine_z_score_2025": engine_z,
                "legacy_reference_z_score_2025": legacy_z,
                "engine_passes": engine_z < 2.0,
                "legacy_reference_passes": legacy_z < 2.0,
            }
        )

    artifact = generate_artifact(
        topic="0.8_Muon_g2_Anomaly",
        dataset_hash=hash_dataset(
            {
                "legacy_source": str(legacy_json.relative_to(root_path)),
                "experimental_source": str(experimental_json.relative_to(root_path)),
                "theory_source": str(theory_json.relative_to(root_path)),
                "baseline_package": str(baseline_package_json.relative_to(root_path)),
                "engine_delta": engine_delta,
                "legacy_reference_delta": legacy_reference_delta,
            }
        ),
        results={
            "status": "PASS" if nominal_engine_z < 2.0 else "FAIL",
            "delta_a_mu_2025": delta_2025,
            "engine_delta": engine_delta,
            "legacy_reference_delta": legacy_reference_delta,
            "engine_z_score_2025": nominal_engine_z,
            "legacy_reference_z_score_2025": nominal_legacy_reference_z,
            "engine_z_score_legacy_2023_gap": legacy_2023_engine_z,
            "legacy_reference_z_score_legacy_2023_gap": legacy_2023_reference_z,
            "baseline_comparison": baseline_comparison,
            "theory_package_comparison": theory_package_comparison,
            "sensitivity_grid": sensitivity_grid,
        },
        config={
            "experimental_source_locked": str(experimental_json.relative_to(root_path)),
            "theory_source_locked": str(theory_json.relative_to(root_path)),
            "baseline_package": str(baseline_package_json.relative_to(root_path)),
            "engine_path": str((topic_dir / "Code" / "01_Engine" / "Engine_Muon_G2.py").relative_to(root_path)),
        },
        metrics={
            "engine_delta_times_1e9": engine_delta * 1e9,
            "legacy_reference_delta_times_1e9": legacy_reference_delta * 1e9,
            "engine_z_score_2025": nominal_engine_z,
            "legacy_reference_z_score_2025": nominal_legacy_reference_z,
            "published_2025_gap_times_1e9": published_delta_2025 * 1e9,
        },
        thresholds={"max_compatibility_z_score": 2.0},
        notes="Sensitivity grid varies the Standard-Model comparator uncertainty while baseline comparison separates the canonical source-locked 2025 package from historical local diagnostic packages.",
    )
    artifact_path = topic_dir / "Result" / "artifacts" / "muon_g2_2025_sensitivity.json"
    save_artifact(artifact, artifact_path)

    print("=" * 60)
    print("MUON g-2 2025 SENSITIVITY")
    print("=" * 60)
    print(f"2025 delta_a_mu:        {delta_2025*1e9:.3f} x 10^-9")
    print(f"Engine delta:           {engine_delta*1e9:.3f} x 10^-9")
    print(f"Legacy reference delta: {legacy_reference_delta*1e9:.3f} x 10^-9")
    print(f"Engine z-score 2025:    {nominal_engine_z:.2f}")
    print(f"Legacy z-score 2025:    {nominal_legacy_reference_z:.2f}")
    print(f"Published 2025 delta:   {published_delta_2025*1e9:.3f} x 10^-9")
    print(f"Artifact saved to {artifact_path}")
    return 0 if nominal_engine_z < 2.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
