"""
Test: Gravitational Constant G
==============================
Topic 0.19 diagnostic verifier.

This script checks that the gravity engine's constant package matches the
topic-local CODATA 2018 working copy. It is a source-constant checkpoint, not a
derivation of G, Einstein equations, light bending, or singularity avoidance.
"""

import importlib.util
import json
import platform
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

TOPIC_DIR = ROOT / "docs" / "topics" / "0.19_Gravity_GR"
DATA_PATH = TOPIC_DIR / "Data" / "03_Research" / "codata_2018_gravity.json"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_19_gravity_gr_verification.json"


def file_sha256(path):
    digest = sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_engine():
    engine_file = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Gravity_GR.py"
    spec = importlib.util.spec_from_file_location("Engine_Gravity_GR", str(engine_file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.UETGravityEngine


def load_codata():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_artifact(artifact):
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")


def test_gravitational_constant():
    print("=" * 60)
    print("Test: Gravitational Constant G")
    print("=" * 60)

    codata = load_codata()
    constants = codata["constants"]
    engine = load_engine()()
    planck = engine.get_planck_units()

    g_codata = constants["G"]["value"]
    g_engine = planck["G"]
    rel_uncertainty_percent = constants["G"]["relative_uncertainty"] * 100
    threshold_percent = max(rel_uncertainty_percent, 0.0001)

    if np.isnan(g_engine) or g_engine == 0:
        error_percent = None
        status = "FAIL"
        failure_reason = "Engine returned NaN or zero for G."
    else:
        error_percent = abs(g_engine - g_codata) / g_codata * 100
        status = "PASS" if error_percent <= threshold_percent else "FAIL"
        failure_reason = None if status == "PASS" else "Engine G differs from CODATA checkpoint beyond threshold."

    print(f"CODATA 2018: G = {g_codata:.5e}")
    print(f"Engine value: G = {g_engine:.5e}")
    print(f"Error: {error_percent:.8f}%")
    print(f"Artifact status: {status}")

    artifact = {
        "schema_version": "1.1",
        "topic": "0.19_Gravity_GR",
        "status": status,
        "claim_class": "C - source-constant internal checkpoint only",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.19_Gravity_GR/Code/03_Research/Research_G_Constant.py",
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "inputs": [
            {
                "path": str(DATA_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": file_sha256(DATA_PATH),
                "source": codata.get("source"),
                "doi": codata.get("publication", {}).get("doi"),
            }
        ],
        "formula_ids": [
            "GR19-CONSTANT-PACKAGE",
            "GR19-PLANCK-UNITS",
            "GR19-G-CHECKPOINT",
        ],
        "threshold": {
            "max_relative_error_percent": threshold_percent,
            "codata_relative_uncertainty_percent": rel_uncertainty_percent,
        },
        "metrics": {
            "G_codata": g_codata,
            "G_engine": g_engine,
            "relative_error_percent": error_percent,
            "planck_length_m": planck["length"],
            "planck_time_s": planck["time"],
            "planck_mass_kg": planck["mass"],
        },
        "failure_reason": failure_reason,
        "limitations": [
            "This verifies that the engine constant package matches the CODATA working copy.",
            "It does not derive G from UET first principles.",
            "It does not validate Einstein field equations, light bending, perihelion precession, or singularity avoidance.",
        ],
    }
    write_artifact(artifact)
    print(f"Artifact written: {ARTIFACT_PATH}")
    return status == "PASS"


if __name__ == "__main__":
    success = test_gravitational_constant()
    sys.exit(0 if success else 1)
