"""
UET Nuclear Binding Test against source-backed local datasets
=============================================================
Uses the topic's AME2020 extracted JSON subset and proton-radius reference JSON.
"""

from __future__ import annotations

import json
import statistics
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
topic_dir = root_path / "docs" / "topics" / "0.5_Nuclear_Binding_Hadrons"
data_dir = topic_dir / "Data" / "03_Research"
engine_path = topic_dir / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from Engine_Nuclear_Binding import UETNuclearBindingEngine


AME_JSON = data_dir / "Data_AME2020_Binding_RawSubset.json"
AME_FULL_JSON = data_dir / "Data_AME2020_Binding_FullParsed.json"
AME_MANIFEST_JSON = data_dir / "Data_AME2020_Benchmark_Manifest.json"
PROTON_RADIUS_JSON = data_dir / "Data_Proton_Radius.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def binding_per_nucleon(be_kev: float, a: int) -> float:
    return (be_kev / 1000.0) / a


def run_test() -> bool:
    print("=" * 72)
    print("UET NUCLEAR BINDING TEST - SOURCE-BACKED AME2020")
    print("Data: AME2020 table-wide parse + raw-derived subset + proton radius")
    print("=" * 72)

    ame = load_json(AME_JSON)
    full_ame = load_json(AME_FULL_JSON)
    manifest = load_json(AME_MANIFEST_JSON)
    proton = load_json(PROTON_RADIUS_JSON)
    engine = UETNuclearBindingEngine()

    print("\n[1] BINDING ENERGY CHECKS")
    print("-" * 72)
    print("| Nucleus | A | Z | Obs BE/A | UET BE/A | Error | Heavy-nucleus gate |")
    print("| :-- | --: | --: | --: | --: | --: | :-- |")

    comparisons = {}
    errors = []
    heavy_errors = []
    light_excluded = []
    heavy_pass = True
    heavy_count = 0
    for symbol, row in ame["data"].items():
        a = row["A"]
        z = row["Z"]
        obs = binding_per_nucleon(row["BE_keV"], a)
        pred = engine.binding_energy_per_nucleon(a, z)
        err = abs(pred - obs) / obs * 100 if obs else 0.0
        heavy_gate = a >= 16
        if heavy_gate:
            heavy_count += 1
            heavy_pass = heavy_pass and (err < 15.0)
            heavy_errors.append(err)
        else:
            light_excluded.append(symbol)
        errors.append(err)
        comparisons[symbol] = {
            "A": a,
            "Z": z,
            "observed_be_per_a_mev": obs,
            "predicted_be_per_a_mev": pred,
            "relative_error_percent": err,
            "heavy_nucleus_gate": heavy_gate,
            "passes": (err < 15.0) if heavy_gate else None,
        }
        print(
            f"| {symbol} | {a} | {z} | {obs:.3f} | {pred:.3f} | {err:.2f}% | "
            f"{'PASS' if comparisons[symbol]['passes'] else ('SKIP' if not heavy_gate else 'FAIL')} |"
        )

    print("\n[2] PROTON RADIUS CHECK")
    print("-" * 72)
    rp_pred = engine.compute_proton_radius()
    rp_obs = proton["data"]["prad_2019_fm"]["value"]
    rp_err = abs(rp_pred - rp_obs) / rp_obs * 100 if rp_obs else 0.0
    rp_pass = rp_err < 5.0
    print(f"UET proton radius: {rp_pred:.6f} fm")
    print(f"PRad 2019:         {rp_obs:.6f} fm")
    print(f"Relative error:    {rp_err:.3f}%")
    print(f"Gate (<5%):        {'PASS' if rp_pass else 'FAIL'}")

    overall = heavy_pass and rp_pass and heavy_count > 0
    print(f"\nRESULT: {'PASS' if overall else 'FAIL'}")

    error_distribution = {
        "mean_error_percent": statistics.fmean(errors) if errors else None,
        "median_error_percent": statistics.median(errors) if errors else None,
        "max_error_percent": max(errors) if errors else None,
        "heavy_mean_error_percent": statistics.fmean(heavy_errors) if heavy_errors else None,
        "heavy_median_error_percent": statistics.median(heavy_errors) if heavy_errors else None,
        "heavy_max_error_percent": max(heavy_errors) if heavy_errors else None,
    }
    worst_cases = sorted(
        [
            {
                "symbol": symbol,
                "A": row["A"],
                "Z": row["Z"],
                "relative_error_percent": row["relative_error_percent"],
                "heavy_nucleus_gate": row["heavy_nucleus_gate"],
            }
            for symbol, row in comparisons.items()
        ],
        key=lambda item: item["relative_error_percent"],
        reverse=True,
    )[:5]

    print("\n[3] COVERAGE SUMMARY")
    print("-" * 72)
    print(f"AME2020 parsed rows with BE/A: {full_ame['parsed_table_count']}")
    print(f"Validation subset rows:        {len(ame['data'])}")
    print(f"Light diagnostic exclusions:   {len(light_excluded)}")
    print(f"Heavy-gate max error:          {error_distribution['heavy_max_error_percent']:.2f}%")

    artifact = generate_artifact(
        topic="0.5_Nuclear_Binding_Hadrons",
        dataset_hash=hash_dataset(
            {
                "ame_json": str(AME_JSON.relative_to(root_path)),
                "ame_full_json": str(AME_FULL_JSON.relative_to(root_path)),
                "ame_manifest_json": str(AME_MANIFEST_JSON.relative_to(root_path)),
                "proton_radius_json": str(PROTON_RADIUS_JSON.relative_to(root_path)),
                "ame_subset_keys": sorted(ame["data"].keys()),
                "parsed_table_count": full_ame["parsed_table_count"],
            }
        ),
        results={
            "status": "PASS" if overall else "FAIL",
            "binding_comparisons": comparisons,
            "coverage": {
                "parsed_table_count": full_ame["parsed_table_count"],
                "validation_subset_count": len(ame["data"]),
                "excluded_light_cases": light_excluded,
                "skipped_no_binding_count": full_ame.get("skipped_no_binding_count"),
                "manifest": manifest,
            },
            "error_distribution": error_distribution,
            "worst_cases": worst_cases,
            "proton_radius": {
                "predicted_fm": rp_pred,
                "observed_fm": rp_obs,
                "relative_error_percent": rp_err,
                "passes": rp_pass,
            },
            "heavy_nuclei_all_pass": heavy_pass,
        },
        config={
            "binding_reference": str(AME_JSON.relative_to(root_path)),
            "full_table_reference": str(AME_FULL_JSON.relative_to(root_path)),
            "benchmark_manifest": str(AME_MANIFEST_JSON.relative_to(root_path)),
            "proton_radius_reference": str(PROTON_RADIUS_JSON.relative_to(root_path)),
            "note": "AME2020 input now has a table-wide parsed layer. The current pass/fail gate still uses a selected validation subset plus coverage metrics.",
        },
        metrics={
            "heavy_nuclei_all_pass": heavy_pass,
            "proton_radius_relative_error_percent": rp_err,
            "parsed_table_count": full_ame["parsed_table_count"],
            "validation_subset_count": len(ame["data"]),
            "excluded_count": len(light_excluded),
            "mean_error_percent": error_distribution["mean_error_percent"],
            "median_error_percent": error_distribution["median_error_percent"],
            "max_error_percent": error_distribution["max_error_percent"],
        },
        thresholds={
            "heavy_nucleus_binding_error_percent_max": 15.0,
            "proton_radius_relative_error_percent_max": 5.0,
        },
        notes="This verifier reads a raw-derived AME2020 subset plus source-backed proton-radius data.",
    )
    artifact_path = topic_dir / "Result" / "artifacts" / "nuclear_binding_source_locked_validation.json"
    save_artifact(artifact, artifact_path)
    print(f"Artifact saved to {artifact_path}")
    return overall


if __name__ == "__main__":
    sys.exit(0 if run_test() else 1)
