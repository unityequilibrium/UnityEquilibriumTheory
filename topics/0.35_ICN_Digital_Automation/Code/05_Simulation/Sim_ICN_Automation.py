import json, sys
from pathlib import Path
from datetime import datetime

def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
topic_path = Path(__file__).resolve().parents[2]

def run_simulation():
    data_file = topic_path / "Data" / "05_Simulation" / "empirical_automation_profile.json"
    if not data_file.exists():
        print(f"CRITICAL: Empirical data missing at {data_file}")
        sys.exit(1)

    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    params = data["parameters"]
    targets = data["targets"]

    passed = True
    for key, target_val in targets.items():
        if key.startswith("min_"):
            param_key = key[4:]
            if params.get(param_key, 0) < target_val:
                passed = False
        elif key.startswith("max_"):
            param_key = key[4:]
            if params.get(param_key, 999999) > target_val:
                passed = False

    result = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "topic": "0.35_ICN_Digital_Automation",
            "status": "PASS" if passed else "FAIL"
        },
        "parameters": params,
        "targets": targets
    }

    artifact_dir = topic_path / "Result" / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_file = artifact_dir / "rd_sim_artifact.json"

    with open(artifact_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print(f"Topic 0.35_ICN_Digital_Automation Sim Status: {result['metadata']['status']}")
    return result

if __name__ == "__main__":
    run_simulation()
