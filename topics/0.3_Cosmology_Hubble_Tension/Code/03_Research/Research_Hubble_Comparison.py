"""
UET Cosmology and Hubble Tension Comparison
===========================================
Internal comparison using published H0 reference values and the repository cosmology engine.
"""

import sys
import json
from pathlib import Path

def _bootstrap_root() -> Path:
    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        if (parent / "docs" / "__init__.py").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("Could not locate repository root containing docs package.")


_bootstrap_root()

from docs import ROOT_PATH
from docs.core.reproducibility import generate_artifact, hash_dataset, hash_file, save_artifact


root_path = ROOT_PATH
topic_path = root_path / "docs" / "topics" / "0.3_Cosmology_Hubble_Tension"
engine_path = topic_path / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

try:
    from Engine_Cosmology import UETCosmologyEngine
except ImportError as exc:
    print(f"CRITICAL SETUP ERROR: {exc}")
    sys.exit(1)


H0_PLANCK = 67.4
H0_PLANCK_UNCERTAINTY = 0.5
H0_SHOES = 73.04
H0_SHOES_UNCERTAINTY = 1.04
TENSION_SIGMA = 4.8
SOURCE_LOCK_PATH = topic_path / "Data" / "03_Research" / "source_lock_manifest.json"


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
        path = root_path / record_path
        hashes.append(
            {
                "path": record_path,
                "sha256": hash_file(path) if path.exists() else None,
                "status": "present" if path.exists() else "missing",
            }
        )
    return hashes


def run_test():
    """Run the repository Hubble-comparison benchmark."""
    print("=" * 70)
    print("UET COSMOLOGY - HUBBLE TENSION TEST")
    print("Data: Planck 2018 + SH0ES 2022")
    print("=" * 70)

    engine = UETCosmologyEngine()
    res = engine.solve_hubble_tension(H0_PLANCK, H0_SHOES)
    h0_early_uet = float(res["H0_early_uet"])
    h0_late_uet = float(res["H0_late_uet"])
    delta_h0_uet = float(res["Delta_H0"])
    beta = float(res["beta"])
    beta_source = str(res.get("beta_source", "unspecified"))
    solver_beta = float(res.get("solver_beta", beta))

    observed_delta = H0_SHOES - H0_PLANCK
    observed_delta_uncertainty = (H0_PLANCK_UNCERTAINTY**2 + H0_SHOES_UNCERTAINTY**2) ** 0.5
    error = abs(delta_h0_uet - observed_delta) / observed_delta * 100
    passed = error < 20
    source_lock = load_source_lock()

    print(f"Planck 2018 (CMB): {H0_PLANCK} km/s/Mpc")
    print(f"SH0ES 2022 (local): {H0_SHOES} km/s/Mpc")
    print(f"Observed Delta H0: {observed_delta:.2f} km/s/Mpc")
    print(f"UET early value: {h0_early_uet:.2f} km/s/Mpc")
    print(f"UET late value: {h0_late_uet:.2f} km/s/Mpc")
    print(f"UET Delta H0: {delta_h0_uet:.2f} km/s/Mpc")
    print(f"Hubble frame beta: {beta:.4f} ({beta_source})")
    print(f"Generic solver beta: {solver_beta:.4e}")
    print(f"Relative error: {error:.1f}%")
    print(f"Status: {'PASS' if passed else 'FAIL'}")

    try:
        import matplotlib.pyplot as plt

        fig_dir = topic_path / "Result" / "artifacts"
        fig_dir.mkdir(parents=True, exist_ok=True)
        output_path = fig_dir / "hubble_tension_resolution.png"

        labels = ["Planck 2018", "SH0ES 2022", "UET late"]
        values = [H0_PLANCK, H0_SHOES, h0_late_uet]

        plt.figure(figsize=(10, 6))
        plt.bar(labels, values, color=["#1f77b4", "#d62728", "#2ca02c"])
        plt.ylabel("Hubble Constant (km/s/Mpc)")
        plt.title("Repository Hubble Comparison")
        plt.ylim(60, 80)
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Plot saved to {output_path}")
    except Exception as exc:
        print(f"Visualization skipped: {exc}")

    artifact = generate_artifact(
        topic="0.3_Cosmology_Hubble_Tension",
        dataset_hash=hash_dataset(
            {
                "H0_PLANCK": H0_PLANCK,
                "H0_PLANCK_UNCERTAINTY": H0_PLANCK_UNCERTAINTY,
                "H0_SHOES": H0_SHOES,
                "H0_SHOES_UNCERTAINTY": H0_SHOES_UNCERTAINTY,
                "TENSION_SIGMA": TENSION_SIGMA,
                "source_lock_sha256": hash_file(SOURCE_LOCK_PATH) if SOURCE_LOCK_PATH.exists() else None,
            }
        ),
        results={
            "H0_early_uet": h0_early_uet,
            "H0_late_uet": h0_late_uet,
            "H0_planck_reference": H0_PLANCK,
            "H0_planck_uncertainty": H0_PLANCK_UNCERTAINTY,
            "H0_shoes_reference": H0_SHOES,
            "H0_shoes_uncertainty": H0_SHOES_UNCERTAINTY,
            "observed_delta_h0": observed_delta,
            "observed_delta_h0_uncertainty": observed_delta_uncertainty,
            "delta_h0_uet": delta_h0_uet,
            "delta_residual": delta_h0_uet - observed_delta,
            "hubble_frame_beta": beta,
            "hubble_frame_beta_source": beta_source,
            "generic_solver_beta": solver_beta,
            "status": "PASS" if passed else "FAIL",
        },
        config={
            "relative_error_threshold_percent": 20.0,
            "no_fitting_rule": "hubble_frame_beta is sqrt(ALPHA_EM), not optimized against H0 data",
            "source_lock_path": str(SOURCE_LOCK_PATH.relative_to(root_path)),
        },
        metrics={"relative_error_percent": float(error)},
        thresholds={"max_relative_error_percent": 20.0},
        notes="Internal scalar H0-gap comparison artifact using published H0 reference values and source-lock records.",
    )
    artifact["input_hashes"] = {
        "source_lock_manifest": hash_file(SOURCE_LOCK_PATH) if SOURCE_LOCK_PATH.exists() else None,
        "source_records": source_record_hashes(source_lock),
    }
    artifact["source_lock"] = {
        "path": str(SOURCE_LOCK_PATH.relative_to(root_path)),
        "derived_inputs": source_lock.get("derived_inputs", []),
    }
    artifact["claim_boundary"] = (
        "PASS means the scalar z=0 H0-gap benchmark is inside the fixed 20 percent gate; "
        "it is not a full Planck/SH0ES likelihood replication or a universal cosmology resolution."
    )
    artifact_path = topic_path / "Result" / "artifacts" / "hubble_comparison_validation.json"
    save_artifact(artifact, artifact_path)
    print(f"Artifact saved to {artifact_path}")

    return passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
