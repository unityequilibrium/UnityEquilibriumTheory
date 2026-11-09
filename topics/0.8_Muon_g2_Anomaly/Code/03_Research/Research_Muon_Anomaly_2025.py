"""
UET Muon g-2 Anomaly Research (2025 source-locked experiment + theory)
======================================================================
Topic: 0.8 Muon g-2 Anomaly
Goal: Compare the UET anomaly prediction against the source-locked 2025 experimental
result and the source-locked Muon g-2 Theory Initiative 2025 Standard-Model comparator.
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
experimental_json = root_path / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "fermilab_muon_g2_2025_experiment.json"
theory_json = root_path / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "theory" / "muon_g2_theory_2025_total_sm.json"
engine_path = topic_dir / "Code" / "01_Engine"
LEGACY_UET_REFERENCE_DELTA = 2.51e-9

if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from Engine_Muon_G2 import UETMuonG2Solver


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def uet_muon_anomaly() -> float:
    solver = UETMuonG2Solver()
    return solver.calculate_uet_correction()


def run_research() -> bool:
    print("=" * 60)
    print("UET MUON g-2 ANOMALY RESEARCH")
    print("Data: 2025 source-locked experiment + 2025 source-locked theory comparator")
    print("=" * 60)

    exp_data = load_json(experimental_json)
    theory_data = load_json(theory_json)

    a_exp = exp_data["data"]["a_mu_exp"]
    exp_err = exp_data["data"]["combined_error"]
    a_sm = theory_data["data"]["a_mu_sm_total"]["value"]
    sm_err = theory_data["data"]["a_mu_sm_total"]["uncertainty"]

    delta_val = a_exp - a_sm
    delta_err = math.sqrt(exp_err**2 + sm_err**2)
    sigma = delta_val / delta_err if delta_err else float("inf")
    uet_delta = uet_muon_anomaly()
    legacy_reference_delta = LEGACY_UET_REFERENCE_DELTA
    deviation = abs(uet_delta - delta_val)
    z_score = deviation / delta_err if delta_err else float("inf")
    legacy_reference_z_score = abs(legacy_reference_delta - delta_val) / delta_err if delta_err else float("inf")

    print(f"Experimental a_mu (2025):         {a_exp:.12f}")
    print(f"Experimental combined error:      {exp_err:.3e}")
    print(f"SM comparator (WP25):            {a_sm:.12f}")
    print(f"SM comparator uncertainty:        {sm_err:.3e}")
    print(f"Derived delta_a_mu:               {delta_val*1e9:.3f} x 10^-9")
    print(f"Derived significance:             {sigma:.2f} sigma")
    print(f"UET engine prediction for excess: {uet_delta*1e9:.3f} x 10^-9")
    print(f"Difference (UET - derived delta): {deviation*1e9:.3f} x 10^-9")
    print(f"Compatibility z-score:            {z_score:.2f} sigma")

    passes = z_score < 2.0
    print("PASS" if passes else "FAIL")

    artifact = generate_artifact(
        topic="0.8_Muon_g2_Anomaly",
        dataset_hash=hash_dataset(
            {
                "experimental_source": str(experimental_json.relative_to(root_path)),
                "theory_source": str(theory_json.relative_to(root_path)),
                "a_mu_exp_2025": a_exp,
                "a_mu_sm_wp25": a_sm,
            }
        ),
        results={
            "status": "PASS" if passes else "FAIL",
            "a_mu_exp_2025": a_exp,
            "a_mu_sm_wp25": a_sm,
            "delta_a_mu_derived": delta_val,
            "delta_error_derived": delta_err,
            "significance_sigma_derived": sigma,
            "engine_delta": uet_delta,
            "legacy_reference_delta": legacy_reference_delta,
            "deviation": deviation,
            "engine_z_score_2025": z_score,
            "legacy_reference_z_score_2025": legacy_reference_z_score,
            "z_score": z_score,
        },
        config={
            "experimental_source_locked": str(experimental_json.relative_to(root_path)),
            "theory_source_locked": str(theory_json.relative_to(root_path)),
        },
        metrics={
            "delta_a_mu_derived_times_1e9": delta_val * 1e9,
            "engine_delta_times_1e9": uet_delta * 1e9,
            "legacy_reference_delta_times_1e9": legacy_reference_delta * 1e9,
            "engine_z_score_2025": z_score,
            "legacy_reference_z_score_2025": legacy_reference_z_score,
            "z_score": z_score,
            "significance_sigma_derived": sigma,
        },
        thresholds={"max_compatibility_z_score": 2.0},
        notes=(
            "Both the experimental and theory comparator inputs are now source-locked to 2025 references. "
            "The UET comparator is taken from Engine_Muon_G2 rather than a topic-local hardcoded anomaly constant."
        ),
    )
    artifact_path = topic_dir / "Result" / "artifacts" / "muon_g2_2025_validation.json"
    save_artifact(artifact, artifact_path)
    print(f"Artifact saved to {artifact_path}")
    return passes


if __name__ == "__main__":
    sys.exit(0 if run_research() else 1)
