from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def pick(obj: dict, *keys: str):
    return {key: obj.get(key) for key in keys if key in obj}


def main() -> None:
    artifact_paths = [
        ROOT / "docs/core/07_artifacts/topic13/t13_base_phi_independent_calibration_requirement.json",
        ROOT / "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json",
        ROOT / "docs/core/07_artifacts/topic13/t13_alpha_phi_k_identifiability_audit.json",
    ]
    for path in artifact_paths:
        obj = load(path)
        print(path.name)
        print(json.dumps(pick(obj, "status", "major_result", "open_calibration_record", "source_anchor", "open_inputs", "checks", "controlling_blocker", "next_controller"), ensure_ascii=True, indent=2, default=str))

    data_dir = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
    names = sorted(
        path.name
        for path in data_dir.glob("*.json")
        if any(token in path.name.lower() for token in ("graphite", "phi", "thermal", "energy", "calib", "source", "ding", "landauer"))
    )
    print("candidate_packages")
    print(json.dumps(names, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
