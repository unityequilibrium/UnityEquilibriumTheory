"""
UET Research: Bullet Cluster Offset
===================================
Topic 0.15 diagnostic verifier.

This script checks whether the topic-local toy collision model reproduces only the
qualitative sign of the Bullet Cluster lensing/X-ray separation. It does not
calibrate the separation in kpc and must not be used as a dark-matter replacement
proof.
"""

import json
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256
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
    print("CRITICAL: UET docs root not found")
    sys.exit(1)


TOPIC_DIR = ROOT / "docs" / "topics" / "0.15_Cluster_Dynamics"
DATA_PATH = TOPIC_DIR / "Data" / "Bullet_Cluster_Coordinates.json"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_15_cluster_dynamics_verification.json"


def file_sha256(path):
    digest = sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_bullet_coordinates():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def simulate_collision():
    dt = 0.1
    steps = 300
    x_gas = -10.0
    x_halo = -10.0
    v_gas = 1.0
    v_halo = 1.0
    drag_gas = 0.05
    drag_halo = 0.0
    center = 0.0

    for _ in range(steps):
        if abs(x_gas - center) < 2.0:
            v_gas *= 1.0 - drag_gas
        if abs(x_halo - center) < 2.0:
            v_halo *= 1.0 - drag_halo
        x_gas += v_gas * dt
        x_halo += v_halo * dt

    return {
        "dt": dt,
        "steps": steps,
        "drag_gas": drag_gas,
        "drag_halo": drag_halo,
        "x_gas_final_model_units": x_gas,
        "x_halo_final_model_units": x_halo,
        "offset_model_units": x_halo - x_gas,
    }


def build_observation_summary(data):
    components = data["components"]
    rows = []
    for key, component in components.items():
        rows.append(
            {
                "component": key,
                "offset_kpc": component["offset_kpc"],
                "lensing_peak_label": component["lensing_peak"]["label"],
                "xray_peak_label": component["xray_peak"]["label"],
                "observed_separation_positive": component["offset_kpc"] > 0,
            }
        )
    return rows


def main():
    print("=" * 60)
    print("UET RESEARCH: BULLET CLUSTER OFFSET DIAGNOSTIC")
    print("=" * 60)

    data = load_bullet_coordinates()
    observations = build_observation_summary(data)
    model = simulate_collision()
    model_positive = model["offset_model_units"] > 0
    observed_positive = all(row["observed_separation_positive"] for row in observations)

    status = "WARN" if model_positive and observed_positive else "FAIL"
    failure_reason = None
    if status == "WARN":
        failure_reason = (
            "Qualitative separation sign matches, but the toy model is not "
            "dimensionally calibrated to kpc offsets."
        )
    else:
        failure_reason = "Toy model failed even the qualitative separation-sign gate."

    print(f"System: {data['system']}")
    print(f"Reference: {data['reference']}")
    for row in observations:
        print(f"Observed {row['component']} offset: {row['offset_kpc']} kpc")
    print(f"Model offset: {model['offset_model_units']:.2f} model units")
    print(f"Artifact status: {status}")

    artifact = {
        "schema_version": "1.1",
        "topic": "0.15_Cluster_Dynamics",
        "status": status,
        "claim_class": "D - qualitative diagnostic only",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.15_Cluster_Dynamics/Code/03_Research/Research_BulletCluster_Offset.py",
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "inputs": [
            {
                "path": str(DATA_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": file_sha256(DATA_PATH),
                "source": data["reference"],
                "system": data["system"],
                "unit_system": data["scale"],
            }
        ],
        "formula_ids": [
            "CL15-DRAG-TOY",
            "CL15-OFFSET-SIGN-GATE",
        ],
        "threshold": {
            "qualitative_offset_sign_match_required": True,
            "dimensional_kpc_calibration_required_for_PASS": True,
        },
        "metrics": {
            "observed_offsets_kpc": {
                row["component"]: row["offset_kpc"] for row in observations
            },
            "model_offset_model_units": model["offset_model_units"],
            "offset_sign_match": model_positive and observed_positive,
            "dimensional_calibration_present": False,
        },
        "model": model,
        "observations": observations,
        "failure_reason": failure_reason,
        "limitations": [
            "The current collision model is one-dimensional and dimensionless.",
            "The artifact supports only a qualitative separation-sign diagnostic.",
            "It does not predict the observed 480 kpc or 120 kpc offsets.",
            "It does not establish a dark-matter-free cluster theory.",
        ],
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Artifact written: {ARTIFACT_PATH}")
    return 0 if status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    sys.exit(main())
