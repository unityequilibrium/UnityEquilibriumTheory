"""
UET Nuclear Binding full-table diagnostic against AME2020 parsed coverage.

This script does not replace the strict validation subset gate. It provides a
table-wide diagnostic view so the repo can honestly report how the engine
behaves outside the curated benchmark nuclei.
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


AME_FULL_JSON = data_dir / "Data_AME2020_Binding_FullParsed.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def binding_per_nucleon(be_kev: float, a: int) -> float:
    return (be_kev / 1000.0) / a


def summarize(errors: list[float]) -> dict:
    if not errors:
        return {
            "count": 0,
            "mean_error_percent": None,
            "median_error_percent": None,
            "max_error_percent": None,
            "p90_error_percent": None,
        }

    ordered = sorted(errors)
    p90_index = min(len(ordered) - 1, int(0.9 * (len(ordered) - 1)))
    return {
        "count": len(errors),
        "mean_error_percent": statistics.fmean(errors),
        "median_error_percent": statistics.median(errors),
        "max_error_percent": max(errors),
        "p90_error_percent": ordered[p90_index],
    }


def run_diagnostic() -> bool:
    print("=" * 76)
    print("UET NUCLEAR BINDING FULL-TABLE DIAGNOSTIC")
    print("Data: AME2020 parsed table-wide coverage")
    print("=" * 76)

    full_ame = load_json(AME_FULL_JSON)
    engine = UETNuclearBindingEngine()

    all_errors: list[float] = []
    heavy_errors: list[float] = []
    light_errors: list[float] = []
    worst_cases: list[dict] = []
    heavy_under_15 = 0
    heavy_total = 0

    for symbol, row in full_ame["data"].items():
        a = row["A"]
        z = row["Z"]
        obs = binding_per_nucleon(row["BE_keV"], a)
        pred = engine.binding_energy_per_nucleon(a, z)
        err = abs(pred - obs) / obs * 100 if obs else 0.0
        all_errors.append(err)

        case = {
            "symbol": symbol,
            "A": a,
            "Z": z,
            "observed_be_per_a_mev": obs,
            "predicted_be_per_a_mev": pred,
            "relative_error_percent": err,
            "heavy_nucleus_gate": a >= 16,
        }
        worst_cases.append(case)

        if a >= 16:
            heavy_total += 1
            heavy_errors.append(err)
            if err < 15.0:
                heavy_under_15 += 1
        else:
            light_errors.append(err)

    worst_cases = sorted(worst_cases, key=lambda item: item["relative_error_percent"], reverse=True)[:15]

    summary = {
        "all_nuclei": summarize(all_errors),
        "heavy_nuclei_A_ge_16": summarize(heavy_errors),
        "light_nuclei_A_lt_16": summarize(light_errors),
        "heavy_nuclei_under_15_percent_count": heavy_under_15,
        "heavy_nuclei_total_count": heavy_total,
        "heavy_nuclei_under_15_percent_fraction": (heavy_under_15 / heavy_total) if heavy_total else None,
    }

    print("\n[1] COVERAGE")
    print("-" * 76)
    print(f"Parsed AME2020 rows with BE/A:      {summary['all_nuclei']['count']}")
    print(f"Heavy nuclei (A >= 16):             {summary['heavy_nuclei_A_ge_16']['count']}")
    print(f"Light nuclei (A < 16):              {summary['light_nuclei_A_lt_16']['count']}")
    print(f"Heavy nuclei under 15% error:       {heavy_under_15}/{heavy_total}")

    print("\n[2] ERROR SUMMARY")
    print("-" * 76)
    print(
        f"All nuclei mean/median/max:         "
        f"{summary['all_nuclei']['mean_error_percent']:.2f}% / "
        f"{summary['all_nuclei']['median_error_percent']:.2f}% / "
        f"{summary['all_nuclei']['max_error_percent']:.2f}%"
    )
    print(
        f"Heavy nuclei mean/median/max:       "
        f"{summary['heavy_nuclei_A_ge_16']['mean_error_percent']:.2f}% / "
        f"{summary['heavy_nuclei_A_ge_16']['median_error_percent']:.2f}% / "
        f"{summary['heavy_nuclei_A_ge_16']['max_error_percent']:.2f}%"
    )
    print(
        f"Light nuclei mean/median/max:       "
        f"{summary['light_nuclei_A_lt_16']['mean_error_percent']:.2f}% / "
        f"{summary['light_nuclei_A_lt_16']['median_error_percent']:.2f}% / "
        f"{summary['light_nuclei_A_lt_16']['max_error_percent']:.2f}%"
    )

    print("\n[3] WORST CASES")
    print("-" * 76)
    print("| Nucleus | A | Z | Error | Heavy gate |")
    print("| :-- | --: | --: | --: | :-- |")
    for case in worst_cases[:10]:
        print(
            f"| {case['symbol']} | {case['A']} | {case['Z']} | "
            f"{case['relative_error_percent']:.2f}% | {case['heavy_nucleus_gate']} |"
        )

    artifact = generate_artifact(
        topic="0.5_Nuclear_Binding_Hadrons",
        dataset_hash=hash_dataset(
            {
                "full_table_reference": str(AME_FULL_JSON.relative_to(root_path)),
                "parsed_table_count": summary["all_nuclei"]["count"],
                "heavy_total": heavy_total,
            }
        ),
        results={
            "status": "DIAGNOSTIC",
            "summary": summary,
            "worst_cases": worst_cases,
        },
        config={
            "full_table_reference": str(AME_FULL_JSON.relative_to(root_path)),
            "note": (
                "This artifact is a table-wide diagnostic layer. It does not replace the strict "
                "selected-subset pass/fail verifier."
            ),
        },
        metrics={
            "parsed_table_count": summary["all_nuclei"]["count"],
            "heavy_nuclei_count": summary["heavy_nuclei_A_ge_16"]["count"],
            "light_nuclei_count": summary["light_nuclei_A_lt_16"]["count"],
            "heavy_nuclei_under_15_percent_fraction": summary["heavy_nuclei_under_15_percent_fraction"],
            "all_nuclei_mean_error_percent": summary["all_nuclei"]["mean_error_percent"],
            "heavy_nuclei_mean_error_percent": summary["heavy_nuclei_A_ge_16"]["mean_error_percent"],
            "light_nuclei_mean_error_percent": summary["light_nuclei_A_lt_16"]["mean_error_percent"],
        },
        thresholds={"heavy_nucleus_reference_error_percent": 15.0},
        notes=(
            "Use this artifact to describe broad engine behavior across the parsed AME2020 table. "
            "Use the source-locked subset verifier for the strict pass/fail gate."
        ),
    )
    artifact_path = topic_dir / "Result" / "artifacts" / "nuclear_binding_full_table_diagnostic.json"
    save_artifact(artifact, artifact_path)
    print(f"Artifact saved to {artifact_path}")
    return True


if __name__ == "__main__":
    sys.exit(0 if run_diagnostic() else 1)
