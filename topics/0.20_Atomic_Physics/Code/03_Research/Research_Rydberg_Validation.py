"""
UET Rydberg Formula Validation
==============================
Topic 0.20 diagnostic verifier.

This verifier checks a standard Rydberg-series relation against the topic-local
NIST hydrogen spectrum working copy and CODATA R_H value. It supports an internal
hydrogen-spectrum benchmark only; it does not derive the Rydberg formula from UET
first principles or validate many-electron atomic physics.
"""

import json
import platform
import re
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import numpy as np


def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None


ROOT = _bootstrap()
if ROOT is None:
    print("CRITICAL: UET docs root not found")
    sys.exit(1)

TOPIC_DIR = ROOT / "docs" / "topics" / "0.20_Atomic_Physics"
SPECTRUM_PATH = TOPIC_DIR / "Data" / "03_Research" / "nist_hydrogen_spectrum.json"
CODATA_PATH = TOPIC_DIR / "Data" / "03_Research" / "codata_2018_atomic.json"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_20_atomic_physics_verification.json"


def file_sha256(path):
    digest = sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_transition(text):
    values = [int(token) for token in re.findall(r"\d+", text)]
    if len(values) != 2:
        raise ValueError(f"Cannot parse transition: {text}")
    return values[0], values[1]


def collect_lines(spectrum):
    rows = []
    for series_name in ("balmer_series", "lyman_series"):
        for line in spectrum[series_name]["lines"]:
            n_upper, n_lower = parse_transition(line["transition"])
            rows.append(
                {
                    "series": series_name.replace("_series", ""),
                    "name": line["name"],
                    "n_upper": n_upper,
                    "n_lower": n_lower,
                    "wavelength_vacuum_nm": line["wavelength_vacuum_nm"],
                }
            )
    return rows


def write_artifact(artifact):
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")


def run_rydberg_analysis():
    print("=" * 60)
    print("UET ATOMIC PHYSICS: RYDBERG VALIDATION")
    print("Data: NIST hydrogen spectrum + CODATA R_H")
    print("=" * 60)

    spectrum = load_json(SPECTRUM_PATH)
    codata = load_json(CODATA_PATH)
    r_h = codata["constants"]["R_H"]["value"]
    r_infinity = codata["constants"]["R_infinity"]["value"]

    results = []
    x_vals = []
    y_vals = []
    for row in collect_lines(spectrum):
        term = (1.0 / row["n_lower"] ** 2) - (1.0 / row["n_upper"] ** 2)
        predicted_nm = 1e9 / (r_h * term)
        observed_nm = row["wavelength_vacuum_nm"]
        error_ppm = abs(predicted_nm - observed_nm) / observed_nm * 1e6
        inv_lam = 1.0 / (observed_nm * 1e-9)
        x_vals.append(term)
        y_vals.append(inv_lam)
        results.append(
            {
                **row,
                "geometric_term": term,
                "predicted_wavelength_nm": predicted_nm,
                "wavelength_error_ppm": error_ppm,
            }
        )
        print(
            f"  {row['name']}: observed={observed_nm:.4f} nm, "
            f"R_H prediction={predicted_nm:.4f} nm, error={error_ppm:.2f} ppm"
        )

    x_arr = np.array(x_vals)
    y_arr = np.array(y_vals)
    slope_origin = float(np.dot(x_arr, y_arr) / np.dot(x_arr, x_arr))
    slope_error_ppm = abs(slope_origin - r_h) / r_h * 1e6
    avg_error_ppm = float(np.mean([row["wavelength_error_ppm"] for row in results]))
    max_error_ppm = float(np.max([row["wavelength_error_ppm"] for row in results]))
    threshold = {
        "average_wavelength_error_ppm_max": 100.0,
        "max_wavelength_error_ppm_max": 250.0,
        "slope_error_ppm_max": 250.0,
    }
    status = (
        "PASS"
        if avg_error_ppm <= threshold["average_wavelength_error_ppm_max"]
        and max_error_ppm <= threshold["max_wavelength_error_ppm_max"]
        and slope_error_ppm <= threshold["slope_error_ppm_max"]
        else "FAIL"
    )

    artifact = {
        "schema_version": "1.1",
        "topic": "0.20_Atomic_Physics",
        "status": status,
        "claim_class": "C - source-backed internal hydrogen spectrum benchmark",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.20_Atomic_Physics/Code/03_Research/Research_Rydberg_Validation.py",
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "inputs": [
            {
                "path": str(SPECTRUM_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": file_sha256(SPECTRUM_PATH),
                "source": spectrum.get("source"),
                "doi": spectrum.get("publication", {}).get("doi"),
                "url": spectrum.get("publication", {}).get("url"),
            },
            {
                "path": str(CODATA_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": file_sha256(CODATA_PATH),
                "source": codata.get("source"),
                "doi": codata.get("publication", {}).get("doi"),
            },
        ],
        "formula_ids": [
            "AT20-RYDBERG-WAVELENGTH",
            "AT20-RH-CODATA-CHECKPOINT",
            "AT20-SPECTRUM-RESIDUAL",
        ],
        "threshold": threshold,
        "metrics": {
            "R_H_codata_m_inverse": r_h,
            "R_infinity_codata_m_inverse": r_infinity,
            "fitted_slope_through_origin_m_inverse": slope_origin,
            "slope_error_ppm": slope_error_ppm,
            "average_wavelength_error_ppm": avg_error_ppm,
            "max_wavelength_error_ppm": max_error_ppm,
            "line_count": len(results),
        },
        "results": results,
        "limitations": [
            "This validates the standard Rydberg relation against the topic-local hydrogen spectrum working copy.",
            "It does not derive the Rydberg relation from UET first principles.",
            "It does not validate fine structure, Lamb shift, helium, or many-electron atoms.",
        ],
    }
    write_artifact(artifact)
    print(f"Average wavelength error: {avg_error_ppm:.2f} ppm")
    print(f"Max wavelength error: {max_error_ppm:.2f} ppm")
    print(f"Slope error: {slope_error_ppm:.2f} ppm")
    print(f"Artifact status: {status}")
    print(f"Artifact written: {ARTIFACT_PATH}")
    return status == "PASS"


if __name__ == "__main__":
    success = run_rydberg_analysis()
    sys.exit(0 if success else 1)
