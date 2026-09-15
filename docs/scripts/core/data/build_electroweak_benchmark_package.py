"""Build a structured benchmark package for topic 0.6 electroweak work."""

from __future__ import annotations

# BEGIN UET REPO ROOT BOOTSTRAP
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
# END UET REPO ROOT BOOTSTRAP

import json
import sys
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
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


from docs import ROOT_PATH


root_path = ROOT_PATH
topic_dir = root_path / "docs" / "topics" / "0.6_Electroweak_Physics"
reference_package_json = root_path / "docs" / "data" / "external" / "particle_physics" / "pdg" / "electroweak_reference_package.json"
neutron_data_path = topic_dir / "Data" / "03_Research" / "neutron_decay_data.py"
output_json = root_path / "docs" / "data" / "external" / "particle_physics" / "pdg" / "electroweak_benchmark_package.json"


RUNNING_ANGLE_POINTS = [
    {
        "label": "APV_Cs",
        "Q_GeV": 0.0024,
        "sin2_theta_W": 0.23867,
        "uncertainty": 0.00016,
        "provenance_status": "checked_local_compilation",
    },
    {
        "label": "Qweak",
        "Q_GeV": 0.16,
        "sin2_theta_W": 0.2313,
        "uncertainty": 0.001,
        "provenance_status": "checked_local_compilation",
    },
    {
        "label": "DIS",
        "Q_GeV": 30.0,
        "sin2_theta_W": 0.232,
        "uncertainty": 0.001,
        "provenance_status": "checked_local_compilation",
    },
    {
        "label": "Z_pole",
        "Q_GeV": 91.18,
        "sin2_theta_W": 0.23121,
        "uncertainty": 0.00004,
        "provenance_status": "checked_local_compilation",
    },
    {
        "label": "LHC_high_Q",
        "Q_GeV": 8000.0,
        "sin2_theta_W": 0.231,
        "uncertainty": 0.001,
        "provenance_status": "checked_local_compilation",
    },
]


def load_module(path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    reference_package = json.loads(reference_package_json.read_text(encoding="utf-8"))
    neutron_module = load_module(neutron_data_path)

    payload = {
        "source_package": "topic_0.6 electroweak benchmark package",
        "reference_package": str(reference_package_json.relative_to(root_path)),
        "core_observables": reference_package["references"],
        "running_angle_diagnostic": {
            "status": "diagnostic_only",
            "source": "compiled local benchmark points embedded in legacy topic research script",
            "points": RUNNING_ANGLE_POINTS,
        },
        "neutron_decay_benchmark": {
            "status": "checked_local_compilation",
            "best_lifetime_s": neutron_module.BEST_LIFETIME_S,
            "best_lifetime_uncertainty_s": neutron_module.BEST_LIFETIME_UNCERTAINTY_S,
            "fermi_constant_GeV2": neutron_module.FERMI_CONSTANT["value_GeV"],
            "fermi_constant_uncertainty_GeV2": neutron_module.FERMI_CONSTANT["uncertainty_GeV"],
            "v_ud": neutron_module.CKM_VUD["value"],
            "g_A": neutron_module.AXIAL_COUPLING["value"],
            "source_file": str(neutron_data_path.relative_to(root_path)),
        },
    }
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
