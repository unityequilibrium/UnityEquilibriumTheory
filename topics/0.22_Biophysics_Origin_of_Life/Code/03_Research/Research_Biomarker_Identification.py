"""
UET Biophysics: Synthetic Biomarker Diagnostic
==============================================
This is an internal class-C diagnostic only. It is not clinical, TCGA, EEG,
or origin-of-life validation.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


TOPIC_DIR = Path(__file__).resolve().parents[2]
ROOT = TOPIC_DIR.parents[2]
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_22_biophysics_origin_of_life_verification.json"
DATA_INPUTS = [
    TOPIC_DIR / "data" / "03_Research" / "source_lock_manifest.json",
    TOPIC_DIR / "data" / "03_Research" / "chb_mit_reference.json",
    TOPIC_DIR / "data" / "03_Research" / "chb01_summary.txt",
    TOPIC_DIR / "data" / "03_Research" / "seizure_phase_data.json",
    TOPIC_DIR / "data" / "Bonn_EEG" / "Z.txt",
    TOPIC_DIR / "data" / "Bonn_EEG" / "S.txt",
    ROOT / "docs" / "data" / "external" / "biophysics" / "eeg" / "chb_mit" / "source_record.json",
    ROOT / "docs" / "data" / "external" / "biophysics" / "eeg" / "bonn" / "source_record.json",
    ROOT / "docs" / "data" / "external" / "biophysics" / "omics" / "tcga" / "source_record.json",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _input_identity() -> list[dict[str, object]]:
    records = []
    for path in DATA_INPUTS:
        relative = path.relative_to(ROOT).as_posix()
        if path.exists():
            records.append(
                {
                    "path": relative,
                    "sha256": _sha256(path),
                    "size_bytes": path.stat().st_size,
                    "data_role": "source_referenced_context_or_synthetic_placeholder",
                }
            )
        else:
            records.append({"path": relative, "missing": True})
    return records


def _write_artifact(results: list[dict[str, object]], threshold: float, seed: int) -> dict:
    inputs = _input_identity()
    missing = [item["path"] for item in inputs if item.get("missing")]
    status = "WARN" if results and not missing else "FAIL"
    artifact = {
        "schema_version": "1.2",
        "topic": "0.22_Biophysics_Origin_of_Life",
        "command": ".venv\\Scripts\\python.exe docs\\topics\\0.22_Biophysics_Origin_of_Life\\Code\\03_Research\\Research_Biomarker_Identification.py",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "claim_class": "C",
        "data_class": "synthetic",
        "evidence_class": "internal_benchmark",
        "claim_ceiling": "C",
        "topic_status_impact": "NONE",
        "inputs": inputs,
        "metrics": {
            "synthetic_gene_count": 50,
            "synthetic_sample_count": 100,
            "stability_threshold": threshold,
            "random_seed": seed,
            "identified_biomarkers": results,
        },
        "thresholds": {
            "stability_below_threshold_flags_candidate": threshold,
            "expected_synthetic_positive_controls": ["GENE_007", "GENE_023"],
        },
        "warnings": [
            "Biomarker data in this verifier is synthetic; it is not a clinical or TCGA validation.",
            "EEG/TCGA records are hashed for provenance context but are not used as measurements.",
            "This is an internal class-C diagnostic; no external replication is claimed.",
            "Other topic lanes require separate verifier gates.",
        ],
        "interpretation": (
            "This artifact validates the synthetic biomarker diagnostic path only. "
            "It supports code-path hardening and formula auditing, not biomedical efficacy "
            "or origin-of-life evidence."
        ),
    }
    if missing:
        artifact["warnings"].append(f"Missing declared provenance inputs: {missing}")
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"[Artifact] Status: {status}")
    return artifact


def identify_biomarkers() -> bool:
    seed = 22022
    np.random.seed(seed)
    gene_names = [f"GENE_{index:03d}" for index in range(50)]
    data = np.random.normal(5, 0.5, (50, 100))
    data[7] = np.random.normal(5, 2.5, 100)
    data[23] = np.random.normal(5, 3.0, 100)

    results = []
    threshold = 0.5
    for index, gene in enumerate(gene_names):
        variance = float(np.var(data[index]))
        stability = 1.0 / (1.0 + variance)
        if stability < threshold:
            results.append(
                {
                    "gene": gene,
                    "stability": float(stability),
                    "variance": variance,
                    "status": "synthetic_positive_control_candidate",
                }
            )
    if results:
        print(pd.DataFrame(results).to_string(index=False))
    artifact = _write_artifact(results, threshold, seed)
    return artifact["status"] != "FAIL"


if __name__ == "__main__":
    raise SystemExit(0 if identify_biomarkers() else 1)
