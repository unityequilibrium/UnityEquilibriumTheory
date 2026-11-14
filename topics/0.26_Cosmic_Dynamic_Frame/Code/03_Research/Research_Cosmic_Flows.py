"""
UET Cosmic Flow Research
========================
Topic: 0.26 Cosmic Dynamic Frame

Primary verifier: load the topic-local Laniakea landmark working copy, render a
3D flow-map artifact, and write a machine-readable provenance/status artifact.
This is a visualization/provenance gate, not a cosmological model proof.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
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
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)

from docs.core.uet_glass_box import UETPathManager


TOPIC_DIR = ROOT / "docs" / "topics" / "0.26_Cosmic_Dynamic_Frame"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_26_cosmic_dynamic_frame_verification.json"
DATA_INPUTS = [
    TOPIC_DIR / "Data" / "03_Research" / "Laniakea_Flows.json",
    TOPIC_DIR / "Data" / "03_Research" / "source_lock_manifest.json",
    TOPIC_DIR / "Data" / "Cosmicflows_3_Subset.csv",
    TOPIC_DIR / "Data" / "Download_Cosmic_Data.py",
    TOPIC_DIR / "Data" / "Pioneer_Anomaly_Data.csv",
    ROOT / "docs" / "data" / "external" / "cosmology" / "laniakea" / "tully_2014" / "source_record.json",
    ROOT / "docs" / "data" / "external" / "cosmology" / "cosmicflows" / "cosmicflows3" / "source_record.json",
    ROOT / "docs" / "data" / "external" / "spacecraft" / "pioneer_anomaly" / "anderson_2002" / "source_record.json",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _input_identity():
    items = []
    for path in DATA_INPUTS:
        rel = path.relative_to(ROOT).as_posix()
        if path.exists():
            items.append({"path": rel, "sha256": _sha256(path), "size_bytes": path.stat().st_size})
        else:
            items.append({"path": rel, "missing": True})
    return items


def load_flows():
    path = TOPIC_DIR / "Data" / "03_Research" / "Laniakea_Flows.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing Data: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_artifact(metrics, figure_path):
    inputs = _input_identity()
    missing = [item["path"] for item in inputs if item.get("missing")]
    status = "WARN" if figure_path and not missing else "FAIL"
    artifact = {
        "schema_version": "1.1",
        "topic": "0.26_Cosmic_Dynamic_Frame",
        "command": ".venv\\Scripts\\python.exe docs\\topics\\0.26_Cosmic_Dynamic_Frame\\Code\\03_Research\\Research_Cosmic_Flows.py",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "claim_class": "D",
        "inputs": inputs,
        "metrics": metrics,
        "figure_artifact": str(figure_path.relative_to(TOPIC_DIR)) if figure_path else None,
        "warnings": [
            "Laniakea/Cosmicflows/Pioneer source records are pinned, but raw tables, frame metadata, and preprocessing are not archived.",
            "This verifier checks data loading and flow-map generation, not a cosmological model fit.",
            "Cosmicflows/Pioneer files are hashed for provenance but are not used by this primary visualization gate.",
        ],
        "interpretation": (
            "The artifact supports an exploratory dynamic-frame visualization. It does not establish "
            "dark-matter replacement, toroidal cosmology, or Pioneer-drag physics."
        ),
    }
    if missing:
        artifact["warnings"].append(f"Missing declared inputs: {missing}")
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"\n[Artifact] Verification artifact written: {ARTIFACT_PATH}")
    print(f"[Artifact] Status: {status}")
    return artifact


def run_viz():
    print("=" * 60)
    print("UET COSMIC FLOW VISUALIZATION")
    print("Data: Laniakea topic-local working copy")
    print("=" * 60)

    output_dir = UETPathManager.get_result_dir(
        topic_id="0.26", experiment_name="Laniakea_Flow", category="showcase"
    )

    data = load_flows()
    landmarks = data["landmarks"]
    names = [item["name"] for item in landmarks]
    coords = np.array([item["coords"] for item in landmarks])
    types = [item["type"] for item in landmarks]

    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection="3d")
    colors = {
        "Observer": "blue",
        "Attractor": "red",
        "Major Attractor": "darkred",
        "Repeller (Void)": "cyan",
        "Filament": "green",
        "Local Hub": "orange",
    }

    used_labels = set()
    for name, coord, kind in zip(names, coords, types):
        label = kind if kind not in used_labels else ""
        used_labels.add(kind)
        ax.scatter(coord[0], coord[1], coord[2], c=colors.get(kind, "gray"), s=160, label=label)
        ax.text(coord[0], coord[1], coord[2] + 5, name, fontsize=9)

    flow_names = ["Dipole Repeller", "Milky Way (Local Group)", "Great Attractor (Norma)", "Shapley Concentration"]
    has_flow_path = all(name in names for name in flow_names)
    if has_flow_path:
        path_coords = coords[[names.index(name) for name in flow_names]]
        ax.plot(path_coords[:, 0], path_coords[:, 1], path_coords[:, 2], "k--", linewidth=1, alpha=0.5)

    ax.set_xlabel("SGX (Mpc)")
    ax.set_ylabel("SGY (Mpc)")
    ax.set_zlabel("SGZ (Mpc)")
    ax.set_title("Laniakea Supercluster: Topic-Local Cosmic Flow Map")
    ax.legend()

    save_path = output_dir / "Laniakea_Flow_Map.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Showcase image saved: {save_path}")

    metrics = {
        "landmark_count": int(len(landmarks)),
        "coordinate_frame": "supergalactic Mpc",
        "landmark_types": sorted(set(types)),
        "velocity_magnitudes_km_s": [item["velocity_mag"] for item in landmarks if "velocity_mag" in item],
        "has_flow_path": bool(has_flow_path),
    }
    artifact = _write_artifact(metrics, save_path if save_path.exists() else None)
    print("Result: flow-field map generated as exploratory visualization.")
    return artifact["status"] != "FAIL"


if __name__ == "__main__":
    raise SystemExit(0 if run_viz() else 1)
