"""Topic 0.9 verification: CHSH/Bell benchmark audit."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path


def bootstrap_repo() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("Repository root with docs/core was not found.")


ROOT = bootstrap_repo()
TOPIC = ROOT / "docs" / "topics" / "0.9_Quantum_Nonlocality"
DATA = TOPIC / "Data" / "03_Research"
ARTIFACT = TOPIC / "Result" / "artifacts" / "0_9_quantum_nonlocality_verification.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    hensen_path = DATA / "bell_test_2015.json"
    summary_path = DATA / "bell_inequality_data.json"
    hensen = load_json(hensen_path)
    summary = load_json(summary_path)

    s_value = float(hensen["data"]["S_value"]["value"])
    s_error = float(hensen["data"]["S_value"]["error"])
    classical_bound = float(hensen["data"]["local_hidden_var_bound"])
    qm_max = float(hensen["data"]["qm_max"])
    p_value = float(hensen["data"]["p_value"])
    tsirelson_exact = 2.0 * math.sqrt(2.0)

    margin_over_local = s_value - classical_bound
    lower_1sigma = s_value - s_error
    tsirelson_gap = abs(qm_max - tsirelson_exact)

    thresholds = {
        "s_value_must_exceed_local_bound": classical_bound,
        "lower_1sigma_must_exceed_local_bound": classical_bound,
        "p_value_max": 0.05,
        "tsirelson_rounding_error_max": 0.001,
    }

    checks = {
        "s_value_exceeds_local_bound": s_value > classical_bound,
        "lower_1sigma_exceeds_local_bound": lower_1sigma > classical_bound,
        "p_value_ok": p_value < thresholds["p_value_max"],
        "tsirelson_reference_ok": tsirelson_gap <= thresholds["tsirelson_rounding_error_max"],
        "source_has_doi": bool(hensen.get("doi")),
    }

    blockers = []
    if not checks["lower_1sigma_exceeds_local_bound"]:
        blockers.append("The lower 1-sigma CHSH value does not clear the local-realist bound.")
    if not checks["p_value_ok"]:
        blockers.append("The recorded p-value does not clear the provisional p<0.05 gate.")
    if not checks["tsirelson_reference_ok"]:
        blockers.append("The stored qm_max value is not sufficiently close to 2*sqrt(2).")
    if not checks["source_has_doi"]:
        blockers.append("Primary Bell-test working copy does not record a DOI.")

    status = "PASS" if all(checks.values()) else "WARN"

    artifact = {
        "schema_version": "1.1",
        "topic": "0.9_Quantum_Nonlocality",
        "status": status,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "command": "python docs/topics/0.9_Quantum_Nonlocality/Code/03_Research/Research_CHSH_Verification.py",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "claim_class": "C - source-referenced internal CHSH benchmark",
        "formula_ids": [
            "QN09-CHSH-PARAMETER",
            "QN09-LOCAL-REALIST-BOUND",
            "QN09-TSIRELSON-BOUND",
            "QN09-PVALUE-GATE",
        ],
        "inputs": [
            {
                "name": "bell_test_2015",
                "path": str(hensen_path.relative_to(ROOT)).replace("\\", "/"),
                "source": hensen.get("source"),
                "doi": hensen.get("doi"),
                "sha256": sha256(hensen_path),
            },
            {
                "name": "bell_inequality_data",
                "path": str(summary_path.relative_to(ROOT)).replace("\\", "/"),
                "source": summary.get("source"),
                "sha256": sha256(summary_path),
            },
        ],
        "threshold": thresholds,
        "checks": checks,
        "blockers": blockers,
        "metrics": {
            "S_value": s_value,
            "S_error": s_error,
            "local_realist_bound": classical_bound,
            "margin_over_local_bound": margin_over_local,
            "lower_1sigma": lower_1sigma,
            "p_value": p_value,
            "qm_max_recorded": qm_max,
            "tsirelson_exact": tsirelson_exact,
            "tsirelson_rounding_gap": tsirelson_gap,
        },
        "limitations": [
            "This artifact verifies a source-referenced CHSH benchmark and Tsirelson-bound consistency.",
            "It does not derive the UET topological-filament explanation from first principles.",
            "It does not reproduce raw event-count analysis from the Hensen et al. experiment.",
            "Double-slit, tunneling, qubit T1, and LC-unity scripts are outside this primary verifier.",
        ],
    }

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    print("UET 0.9 CHSH verification")
    print(f"  status: {status}")
    print(f"  S = {s_value:.3f} +/- {s_error:.3f}")
    print(f"  local bound = {classical_bound:.3f}")
    print(f"  p-value = {p_value:.3f}")
    print(f"  Tsirelson recorded/exact = {qm_max:.6f} / {tsirelson_exact:.6f}")
    print(f"  artifact: {ARTIFACT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
