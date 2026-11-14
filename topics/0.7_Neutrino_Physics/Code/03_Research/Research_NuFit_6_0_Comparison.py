"""
UET Neutrino Physics Test against NuFIT 6.0
===========================================
Checks UET-style neutrino parameters against an extracted official NuFIT 6.0 benchmark.
"""

from __future__ import annotations

import json
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
topic_dir = root_path / "docs" / "topics" / "0.7_Neutrino_Physics"
external_json = root_path / "docs" / "data" / "external" / "particle_physics" / "nufit" / "official" / "nufit_v60_parameters_extracted.json"
provenance_json = root_path / "docs" / "data" / "external" / "particle_physics" / "nufit" / "official" / "nufit_v60_provenance_validation.json"
katrin_json = root_path / "docs" / "data" / "external" / "particle_physics" / "katrin" / "katrin_latest_results_2025.json"

engine_path = topic_dir / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from Engine_Mixing_Neutrino import UETNeutrinoMixingSolver
from Engine_Neutrino import UETNeutrinoSolver


def load_nufit() -> dict:
    return json.loads(external_json.read_text(encoding="utf-8"))


def load_katrin() -> dict:
    return json.loads(katrin_json.read_text(encoding="utf-8"))


def load_provenance() -> dict:
    if not provenance_json.exists():
        return {
            "schema_validation_status": "MISSING",
            "manual_review_required": True,
            "problems": ["Run docs/scripts/data/validate_nufit_v60_provenance.py"],
        }
    return json.loads(provenance_json.read_text(encoding="utf-8"))


def uet_geometric_angles(solver: UETNeutrinoSolver) -> dict:
    """Return the current engine angle outputs.

    Earlier versions of this verifier used a benchmark-compatible local angle package.
    That made the benchmark pass less meaningful because it was not testing the engine
    path declared in the topic docs. The verifier now checks the live engine output.
    """
    theta12, theta23, theta13, delta_cp = solver.pmns_angles_geometric()
    return {
        "theta12_deg": float(theta12),
        "theta23_deg": float(theta23),
        "theta13_deg": float(theta13),
        "delta_cp_deg": float(delta_cp),
        "source": "Engine_Neutrino.UETNeutrinoSolver.pmns_angles_geometric",
    }


def in_range(value: float, lower: float, upper: float) -> bool:
    return bool(lower <= value <= upper)


def compare_to_variant(label: str, variant: dict, geometric: dict, runtime: dict) -> dict:
    params = variant["normal_ordering"]
    results = {}
    for key in ("theta12_deg", "theta23_deg", "theta13_deg"):
        ref = params[key]
        pred = geometric[key]
        results[key] = {
            "mode": "geometric_uet",
            "predicted": pred,
            "best_fit": ref["best_fit"],
            "within_3sigma": in_range(pred, ref["3sigma_min"], ref["3sigma_max"]),
            "distance_from_best_fit": abs(pred - ref["best_fit"]),
            "range_3sigma": [ref["3sigma_min"], ref["3sigma_max"]],
        }

    splittings = {
        "delta_m21_sq_1e5_eV2": runtime["dm21_sq"] * 1e5,
        "delta_m3l_sq_1e3_eV2": runtime["dm31_sq"] * 1e3,
    }
    for key, pred in splittings.items():
        ref = params[key]
        results[key] = {
            "mode": "runtime_benchmark_param",
            "predicted": pred,
            "best_fit": ref["best_fit"],
            "within_3sigma": in_range(pred, ref["3sigma_min"], ref["3sigma_max"]),
            "distance_from_best_fit": abs(pred - ref["best_fit"]),
            "range_3sigma": [ref["3sigma_min"], ref["3sigma_max"]],
        }
    return {"label": label, "results": results}


def run_test() -> bool:
    print("=" * 72)
    print("UET NEUTRINO PHYSICS TEST - NUFIT 6.0")
    print("Data: Official NuFIT 6.0 parameter-table benchmark")
    print("=" * 72)

    dataset = load_nufit()
    provenance = load_provenance()
    katrin = load_katrin()
    solver = UETNeutrinoMixingSolver()
    runtime = solver.NUFIT_PARAMS
    mass_solver = UETNeutrinoSolver()
    geometric = uet_geometric_angles(mass_solver)
    predicted_mass_eV = mass_solver.predict_neutrino_mass()
    katrin_limit_eV = katrin["data"]["mass_limit_eV_c2"]

    variants = dataset["variants"]
    comparisons = [
        compare_to_variant("ic19_without_sk_atm", variants["ic19_without_sk_atm"], geometric, runtime),
        compare_to_variant("ic24_with_sk_atm", variants["ic24_with_sk_atm"], geometric, runtime),
    ]

    print("\n[1] GEOMETRIC ANGLE CHECKS")
    print("-" * 72)
    print("| Variant | Parameter | UET | Best fit | 3sigma range | In range |")
    print("| :-- | :-- | --: | --: | :-- | :-- |")
    for comparison in comparisons:
        for key in ("theta12_deg", "theta23_deg", "theta13_deg"):
            row = comparison["results"][key]
            print(
                f"| {comparison['label']} | {key} | {row['predicted']:.3f} | {row['best_fit']:.3f} | "
                f"{row['range_3sigma'][0]:.3f} -> {row['range_3sigma'][1]:.3f} | {row['within_3sigma']} |"
            )

    print("\n[2] MASS-SPLITTING CHECKS")
    print("-" * 72)
    print("| Variant | Parameter | Runtime | Best fit | 3sigma range | In range |")
    print("| :-- | :-- | --: | --: | :-- | :-- |")
    for comparison in comparisons:
        for key in ("delta_m21_sq_1e5_eV2", "delta_m3l_sq_1e3_eV2"):
            row = comparison["results"][key]
            print(
                f"| {comparison['label']} | {key} | {row['predicted']:.3f} | {row['best_fit']:.3f} | "
                f"{row['range_3sigma'][0]:.3f} -> {row['range_3sigma'][1]:.3f} | {row['within_3sigma']} |"
            )

    print("\n[3] DIRECT MASS-LIMIT CHECK (KATRIN 2025)")
    print("-" * 72)
    print(f"Official KATRIN upper limit: < {katrin_limit_eV:.2f} eV/c^2")
    print(f"Current UET engine mass scale: {predicted_mass_eV:.6g} eV")
    katrin_pass = predicted_mass_eV < katrin_limit_eV
    print(f"KATRIN compatibility: {'PASS' if katrin_pass else 'FAIL'}")

    print("\n[4] NUFIT PROVENANCE GUARD")
    print("-" * 72)
    provenance_pass = provenance.get("schema_validation_status") == "PASS"
    print(f"Checked-transcription provenance status: {provenance.get('schema_validation_status')}")
    print(f"Manual review required: {provenance.get('manual_review_required')}")
    if provenance.get("problems"):
        print(f"Problems: {provenance['problems']}")
    print(f"Provenance guard: {'PASS' if provenance_pass else 'FAIL'}")

    geometric_pass = all(
        any(comparison["results"][key]["within_3sigma"] for comparison in comparisons)
        for key in ("theta12_deg", "theta23_deg", "theta13_deg")
    )
    splitting_pass = all(
        any(comparison["results"][key]["within_3sigma"] for comparison in comparisons)
        for key in ("delta_m21_sq_1e5_eV2", "delta_m3l_sq_1e3_eV2")
    )
    overall = geometric_pass and splitting_pass and katrin_pass and provenance_pass
    failed_angles = [
        key
        for key in ("theta12_deg", "theta23_deg", "theta13_deg")
        if not any(comparison["results"][key]["within_3sigma"] for comparison in comparisons)
    ]

    print("\n[5] INTERPRETATION")
    print("-" * 72)
    print(
        "Angles are checked as live UET engine outputs against official NuFIT 6.0 ranges.\n"
        "Mass splittings are checked separately as runtime benchmark-fed parameters, not yet as\n"
        "first-principles derivations. The direct KATRIN mass-limit check is stricter: it probes\n"
        "the absolute mass-scale engine path rather than the oscillation benchmark layer."
    )
    print(f"\nRESULT: {'PASS' if overall else 'FAIL'}")

    artifact = generate_artifact(
        topic="0.7_Neutrino_Physics",
        dataset_hash=hash_dataset(
            {
                "source_locked_reference": str(external_json.relative_to(root_path)),
                "nufit_provenance": provenance,
                "theta12": geometric["theta12_deg"],
                "theta23": geometric["theta23_deg"],
                "theta13": geometric["theta13_deg"],
                "angle_source": geometric["source"],
                "dm21_sq": runtime["dm21_sq"],
                "dm31_sq": runtime["dm31_sq"],
                "katrin_limit_eV": katrin_limit_eV,
                "predicted_mass_eV": predicted_mass_eV,
            }
        ),
        results={
            "status": "PASS" if overall else "FAIL",
            "claim_class": "C internal benchmark gate" if overall else "model-hardening blocker",
            "geometric_angles": geometric,
            "runtime_benchmark_params": {"dm21_sq": runtime["dm21_sq"], "dm31_sq": runtime["dm31_sq"]},
            "absolute_mass_scale": {
                "predicted_mass_eV": predicted_mass_eV,
                "katrin_limit_eV_c2": katrin_limit_eV,
                "passes": katrin_pass,
            },
            "comparisons": comparisons,
            "nufit_provenance": provenance,
            "geometric_pass": geometric_pass,
            "splitting_pass": splitting_pass,
            "katrin_pass": katrin_pass,
            "provenance_pass": provenance_pass,
            "failure_analysis": {
                "failed_live_angle_gates": failed_angles,
                "model_action": (
                    "revise or derive the live geometric angle path before using this topic "
                    "as support for mass-generation or unity-scale claims"
                )
                if failed_angles
                else "no live angle failure in this run",
                "downstream_dependency_policy": {
                    "0.17_Mass_Generation": "inherits angle-gate blocker until the live model passes NuFIT ranges",
                    "0.23_Unity_Scale_Link": "may cite this artifact as a constraint, not as positive unification evidence",
                    "0.0_Grand_Unification": "must list this as an integration limitation while status is FAIL",
                },
            },
        },
        config={
            "source_locked_reference": str(external_json.relative_to(root_path)),
            "nufit_provenance_reference": str(provenance_json.relative_to(root_path)),
            "katrin_source_locked_reference": str(katrin_json.relative_to(root_path)),
            "note": "NuFIT 6.0 values are maintained as a checked-transcription JSON guarded by source hashes and schema validation; the KATRIN limit is extracted from the official 2025 KATRIN results page; angle checks use live Engine_Neutrino outputs.",
        },
        metrics={
            "engine_angles_all_within_any_3sigma": geometric_pass,
            "engine_angle_fail_count": len(failed_angles),
            "runtime_splittings_all_within_any_3sigma": splitting_pass,
            "predicted_mass_eV": predicted_mass_eV,
            "katrin_limit_eV_c2": katrin_limit_eV,
            "nufit_schema_validation_status": provenance.get("schema_validation_status"),
        },
        thresholds={
            "engine_angles_within_any_3sigma": True,
            "runtime_splittings_within_any_3sigma": True,
            "predicted_mass_less_than_katrin_limit": True,
        },
        notes=(
            "This test distinguishes live UET engine angle outputs from runtime benchmark-fed mass splittings. "
            "It also checks the direct absolute-mass engine path against the official 2025 KATRIN limit. "
            "A fail constrains downstream core-theory claims until the live geometric angle path is repaired."
        ),
    )
    artifact_path = topic_dir / "Result" / "artifacts" / "nufit_6_0_validation.json"
    save_artifact(artifact, artifact_path)
    print(f"Artifact saved to {artifact_path}")
    return overall


if __name__ == "__main__":
    sys.exit(0 if run_test() else 1)
