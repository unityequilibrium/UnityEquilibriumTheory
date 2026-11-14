"""
Download Real Superconductor Critical Temperature Data
=======================================================
Sources:
1. NIMS SuperCon Database (MatNavi)
2. UCI Machine Learning Database (Hamidieh)
3. MIT Experimental Data

References:
- McMillan equation: Tc = (ΘD/1.45) * exp(-1.04(1+λ)/(λ-μ*(1+0.62λ)))
- Allen-Dynes modification for strong coupling
- BCS theory for conventional superconductors

Updated: 2026-01-02
"""

import json
import os
from pathlib import Path
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256


TOPIC_DIR = Path("docs/topics/0.4_Superconductivity_Superfluids")
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_4_superconductivity_superfluids_verification.json"
SOURCE_LOCK_PATH = DATA_DIR / "source_lock_manifest.json"

# Real experimental data from literature
# Sources: Kittel (Solid State Physics), Nature reviews, Physical Review Letters

SUPERCONDUCTOR_DATA = {
    "description": "Real experimental superconductor data with references",
    "sources": [
        "NIMS SuperCon Database",
        "MIT Junior Lab",
        "Kittel Solid State Physics 8th Ed",
        "McMillan (1968) Phys. Rev. 167, 331",
    ],
    "superconductors": [
        # ======= TYPE-I (Classical BCS) =======
        {
            "name": "Aluminum (Al)",
            "Tc_K": 1.175,
            "Tc_uncertainty": 0.002,
            "Theta_D_K": 428,
            "type": "Type-I",
            "lambda_ep": 0.43,  # Electron-phonon coupling
            "mu_star": 0.10,  # Coulomb pseudopotential
            "source": "McMillan 1968",
        },
        {
            "name": "Mercury (Hg)",
            "Tc_K": 4.15,
            "Tc_uncertainty": 0.01,
            "Theta_D_K": 72,
            "type": "Type-I",
            "lambda_ep": 1.6,
            "mu_star": 0.10,
            "source": "Onnes 1911 / Kittel",
        },
        {
            "name": "Lead (Pb)",
            "Tc_K": 7.19,
            "Tc_uncertainty": 0.02,
            "Theta_D_K": 105,
            "type": "Type-I",
            "lambda_ep": 1.55,
            "mu_star": 0.12,
            "source": "MIT Junior Lab",
        },
        {
            "name": "Vanadium (V)",
            "Tc_K": 5.36,
            "Tc_uncertainty": 0.13,
            "Theta_D_K": 380,
            "type": "Type-II",
            "lambda_ep": 0.80,
            "mu_star": 0.11,
            "source": "MIT Junior Lab",
        },
        {
            "name": "Niobium (Nb)",
            "Tc_K": 9.25,
            "Tc_uncertainty": 0.02,
            "Theta_D_K": 275,
            "type": "Type-II",
            "lambda_ep": 1.04,
            "mu_star": 0.12,
            "source": "Kittel / MIT",
        },
        {
            "name": "Tin (Sn)",
            "Tc_K": 3.72,
            "Tc_uncertainty": 0.01,
            "Theta_D_K": 200,
            "type": "Type-I",
            "lambda_ep": 0.72,
            "mu_star": 0.10,
            "source": "Kittel",
        },
        {
            "name": "Indium (In)",
            "Tc_K": 3.41,
            "Tc_uncertainty": 0.01,
            "Theta_D_K": 112,
            "type": "Type-I",
            "lambda_ep": 0.81,
            "mu_star": 0.10,
            "source": "Kittel",
        },
        # ======= A15 Compounds =======
        {
            "name": "Nb3Sn",
            "Tc_K": 18.3,
            "Tc_uncertainty": 0.2,
            "Theta_D_K": 280,
            "type": "A15",
            "lambda_ep": 1.8,
            "mu_star": 0.13,
            "source": "Matthias 1954",
        },
        {
            "name": "Nb3Ge",
            "Tc_K": 23.2,
            "Tc_uncertainty": 0.3,
            "Theta_D_K": 300,
            "type": "A15",
            "lambda_ep": 2.1,
            "mu_star": 0.13,
            "source": "Gavaler 1973",
        },
        # ======= MgB2 (Two-Gap) =======
        {
            "name": "MgB2",
            "Tc_K": 39.0,
            "Tc_uncertainty": 0.5,
            "Theta_D_K": 800,
            "type": "Two-Gap",
            "lambda_ep": 0.87,  # Weighted average
            "mu_star": 0.10,
            "source": "Nagamatsu 2001 Nature",
        },
        # ======= HIGH-Tc CUPRATES (Non-BCS) =======
        {
            "name": "YBCO (YBa2Cu3O7)",
            "Tc_K": 92.0,
            "Tc_uncertainty": 2.0,
            "Theta_D_K": 400,
            "type": "High-Tc Cuprate",
            "lambda_ep": None,  # Not applicable - different mechanism
            "mu_star": None,
            "source": "Wu 1987 PRL",
            "note": "Non-BCS mechanism",
        },
        {
            "name": "BSCCO-2223",
            "Tc_K": 110.0,
            "Tc_uncertainty": 2.0,
            "Theta_D_K": 400,
            "type": "High-Tc Cuprate",
            "lambda_ep": None,
            "mu_star": None,
            "source": "Maeda 1988",
            "note": "Non-BCS mechanism",
        },
    ],
    "formulas": {
        "BCS_weak_coupling": "Tc = 1.13 * Theta_D * exp(-1/λ)",
        "McMillan_1968": "Tc = (Theta_D/1.45) * exp(-1.04*(1+λ)/(λ-μ*(1+0.62*λ)))",
        "Allen_Dynes": "Tc = (f1*f2*ω_log/1.2) * exp(-1.04*(1+λ)/(λ-μ*(1+0.62*λ)))",
        "UET_extension": "Pending - need Information field coupling",
    },
}


def save_data(
    output_dir="docs/topics/0.4_Superconductivity_Superfluids/Data/03_Research",
):
    """Save real superconductor data to JSON."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_path = Path(output_dir) / "real_superconductor_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(SUPERCONDUCTOR_DATA, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved: {output_path}")
    print(f"   {len(SUPERCONDUCTOR_DATA['superconductors'])} superconductors")
    return output_path


def mcmillan_tc(theta_D, lambda_ep, mu_star=0.10):
    """
    McMillan equation for critical temperature.

    Tc = (Theta_D / 1.45) * exp(-1.04(1+λ) / (λ - μ*(1+0.62λ)))

    Valid for: λ < 1.5 (weak to intermediate coupling)
    """
    import numpy as np

    if lambda_ep is None or lambda_ep <= mu_star * (1 + 0.62 * lambda_ep):
        return None  # Not applicable

    exponent = -1.04 * (1 + lambda_ep) / (lambda_ep - mu_star * (1 + 0.62 * lambda_ep))
    return (theta_D / 1.45) * np.exp(exponent)


def inverse_mcmillan_lambda(theta_D, target_tc, mu_star=0.10, low=0.05, high=5.0):
    """Find lambda_ep that reproduces target_tc for the declared theta_D and mu_star."""
    if target_tc <= 0 or theta_D <= 0:
        return None

    threshold = mu_star / max(1 - 0.62 * mu_star, 1e-12)
    low = max(low, threshold + 1e-6)
    lo_val = mcmillan_tc(theta_D, low, mu_star)
    hi_val = mcmillan_tc(theta_D, high, mu_star)
    if lo_val is None or hi_val is None or target_tc < lo_val or target_tc > hi_val:
        return None

    for _ in range(100):
        mid = (low + high) / 2
        mid_val = mcmillan_tc(theta_D, mid, mu_star)
        if mid_val is None:
            low = mid
        elif mid_val < target_tc:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def test_mcmillan():
    """Test McMillan equation against real data."""
    import numpy as np

    print("=" * 70)
    print("🔬 McMillan Equation Test (Real Data)")
    print("=" * 70)

    results = []
    rows = []
    for sc in SUPERCONDUCTOR_DATA["superconductors"]:
        if sc.get("lambda_ep") is None:
            continue

        tc_pred = mcmillan_tc(sc["Theta_D_K"], sc["lambda_ep"], sc.get("mu_star", 0.10))
        if tc_pred is None:
            continue

        tc_obs = sc["Tc_K"]
        error = abs(tc_pred - tc_obs) / tc_obs * 100
        lambda_required = inverse_mcmillan_lambda(
            sc["Theta_D_K"],
            tc_obs,
            sc.get("mu_star", 0.10),
        )
        lambda_delta = None if lambda_required is None else sc["lambda_ep"] - lambda_required
        lambda_ratio = None if not lambda_required else sc["lambda_ep"] / lambda_required
        status = "✅" if error < 20 else "⚠️"

        print(
            f"{sc['name']:20} | Tc_obs={tc_obs:6.2f}K | Tc_McM={tc_pred:6.2f}K | λ={sc['lambda_ep']:.2f} | Err={error:5.1f}% {status}"
        )
        results.append(error)
        rows.append(
            {
                "name": sc["name"],
                "type": sc["type"],
                "Tc_observed_K": tc_obs,
                "Tc_mcmillan_K": float(tc_pred),
                "lambda_ep": sc["lambda_ep"],
                "lambda_required_for_observed_tc": None if lambda_required is None else float(lambda_required),
                "lambda_delta_vs_required": None if lambda_delta is None else float(lambda_delta),
                "lambda_ratio_vs_required": None if lambda_ratio is None else float(lambda_ratio),
                "mu_star": sc.get("mu_star", 0.10),
                "relative_error_percent": float(error),
                "within_20_percent": bool(error < 20),
                "source": sc.get("source", "unknown"),
            }
        )

    avg_err = np.mean(results)
    print("-" * 70)
    print(f"Average Error: {avg_err:.1f}%")
    return float(avg_err), rows


def hash_file(path: Path) -> str | None:
    return sha256(path.read_bytes()).hexdigest() if path.exists() else None


def load_source_lock() -> dict:
    if not SOURCE_LOCK_PATH.exists():
        return {
            "status": "MISSING",
            "path": str(SOURCE_LOCK_PATH),
            "external_source_records": [],
            "derived_inputs": [],
        }
    return json.loads(SOURCE_LOCK_PATH.read_text(encoding="utf-8"))


def source_record_hashes(source_lock: dict) -> list[dict]:
    hashes = []
    for record_path in source_lock.get("external_source_records", []):
        path = Path(record_path)
        hashes.append(
            {
                "path": record_path,
                "sha256": hash_file(path),
                "status": "present" if path.exists() else "missing",
            }
        )
    return hashes


def analyze_failures(avg_err: float, rows: list[dict]) -> dict:
    failed_rows = [row for row in rows if not row["within_20_percent"]]
    worst_rows = sorted(
        rows,
        key=lambda row: row["relative_error_percent"],
        reverse=True,
    )[:5]
    return {
        "model_gate_status": "PASS" if avg_err <= 20.0 and not failed_rows else "FAIL",
        "primary_failure_reason": (
            "Raw McMillan benchmark exceeds the fixed average and per-material 20 percent error gates."
            if failed_rows
            else "No model-gate failure detected."
        ),
        "failed_material_count": len(failed_rows),
        "worst_materials": [
            {
                "name": row["name"],
                "relative_error_percent": row["relative_error_percent"],
                "type": row["type"],
                "source": row["source"],
            }
            for row in worst_rows
        ],
        "interpretation": "This is evidence that the current raw parameter package is not an accepted prediction gate; it is not evidence against every UET superconductivity mechanism.",
    }


def parameter_mismatch_summary(rows: list[dict]) -> dict:
    lambda_rows = [
        row for row in rows if row.get("lambda_required_for_observed_tc") is not None
    ]
    overestimated = [
        row for row in lambda_rows if row["lambda_ep"] > row["lambda_required_for_observed_tc"]
    ]
    underestimated = [
        row for row in lambda_rows if row["lambda_ep"] < row["lambda_required_for_observed_tc"]
    ]
    largest_abs_delta = sorted(
        lambda_rows,
        key=lambda row: abs(row["lambda_delta_vs_required"]),
        reverse=True,
    )[:5]
    return {
        "diagnostic": "inverse McMillan lambda audit",
        "interpretation": (
            "Holding theta_D and mu_star fixed, lambda_required_for_observed_tc is the "
            "coupling needed to reproduce observed Tc. Large deltas identify row-level "
            "parameter mismatch or missing Allen-Dynes/material-specific physics."
        ),
        "rows_with_inverse_solution": len(lambda_rows),
        "lambda_overestimated_count": len(overestimated),
        "lambda_underestimated_count": len(underestimated),
        "largest_lambda_mismatches": [
            {
                "name": row["name"],
                "lambda_ep": row["lambda_ep"],
                "lambda_required_for_observed_tc": row["lambda_required_for_observed_tc"],
                "lambda_delta_vs_required": row["lambda_delta_vs_required"],
                "relative_error_percent": row["relative_error_percent"],
            }
            for row in largest_abs_delta
        ],
    }


def write_artifact(output_path: Path, avg_err: float, rows: list[dict]) -> None:
    data_path = DATA_DIR / "real_superconductor_data.json"
    source_lock = load_source_lock()
    failure_analysis = analyze_failures(avg_err, rows)
    status = failure_analysis["model_gate_status"]
    artifact = {
        "schema_version": "1.2",
        "topic": "0.4_Superconductivity_Superfluids",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.4_Superconductivity_Superfluids/Code/03_Research/Experiment_Superconductor_Data.py",
        "status": status,
        "run_status": "PASS",
        "model_gate_status": status,
        "blocker_class": "model-baseline failure" if status == "FAIL" else None,
        "claim_class": "C internal baseline diagnostic" if status == "PASS" else "model-baseline blocker",
        "inputs": [
            {
                "path": str(data_path),
                "sha256": hash_file(data_path),
                "role": "raw McMillan superconductivity benchmark working copy",
                "data_class": "topic-local working copy generated from in-script rows",
            }
        ],
        "source_lock": {
            "path": str(SOURCE_LOCK_PATH),
            "sha256": hash_file(SOURCE_LOCK_PATH),
            "external_source_records": source_record_hashes(source_lock),
            "derived_inputs": source_lock.get("derived_inputs", []),
        },
        "thresholds": {
            "average_relative_error_percent_max": 20.0,
            "per_material_relative_error_percent_max": 20.0,
        },
        "metrics": {
            "average_relative_error_percent": avg_err,
            "materials_tested": len(rows),
            "materials_within_20_percent": sum(1 for row in rows if row["within_20_percent"]),
        },
        "failure_analysis": failure_analysis,
        "parameter_mismatch_audit": parameter_mismatch_summary(rows),
        "results": rows,
        "limitations": [
            "This is a raw McMillan baseline check, not a UET first-principles prediction.",
            "Several lambda_ep and mu_star values are literature/curated working-copy inputs.",
            "High-Tc cuprates with non-BCS mechanisms are skipped by this baseline.",
            "The source-lock manifest records formula and dataset provenance targets, but raw NIMS MDR files are not yet mirrored.",
        ],
        "next_model_hardening_tasks": [
            "Use the inverse-McMillan lambda audit to identify which row-level lambda_ep/Theta_D inputs need upstream normalization.",
            "Normalize row-level material inputs against upstream records or explicit literature tables.",
            "Add a separate Allen-Dynes/UET engine verifier with calibrated-input labels and held-out materials.",
            "Replace broad pass/fail claims in code docs with artifact-linked model-gate status.",
        ],
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Artifact saved to {output_path}")


if __name__ == "__main__":
    # Save data
    save_data()

    # Test McMillan
    print()
    avg_error, result_rows = test_mcmillan()
    write_artifact(ARTIFACT_PATH, avg_error, result_rows)
