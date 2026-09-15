"""Build a structured muon g-2 baseline package for topic 0.8."""

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

import importlib.util
import json
import math
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
topic_dir = root_path / "docs" / "topics" / "0.8_Muon_g2_Anomaly"
legacy_2023_json = topic_dir / "Data" / "03_Research" / "fermilab_g2_2023.json"
local_muon_module_path = topic_dir / "Data" / "03_Research" / "muon_g2_data.py"
exp_2025_json = root_path / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "fermilab_muon_g2_2025_experiment.json"
theory_2025_json = root_path / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "theory" / "muon_g2_theory_2025_total_sm.json"
output_json = root_path / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "theory" / "muon_g2_baseline_package.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_local_muon_module():
    spec = importlib.util.spec_from_file_location("muon_g2_data_local", local_muon_module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def baseline_entry(label: str, a_exp: float, exp_unc: float, a_sm: float, sm_unc: float, provenance: str, source: str) -> dict:
    delta = a_exp - a_sm
    combined = math.sqrt(exp_unc**2 + sm_unc**2)
    return {
        "label": label,
        "a_mu_exp": a_exp,
        "experimental_uncertainty": exp_unc,
        "a_mu_sm": a_sm,
        "sm_uncertainty": sm_unc,
        "delta_a_mu": delta,
        "combined_uncertainty": combined,
        "provenance_status": provenance,
        "source": source,
    }


def main() -> int:
    legacy_2023 = load_json(legacy_2023_json)
    exp_2025 = load_json(exp_2025_json)
    theory_2025 = load_json(theory_2025_json)
    local_module = load_local_muon_module()

    exp_2025_value = exp_2025["data"]["a_mu_exp"]
    exp_2025_unc = exp_2025["data"]["combined_error"]
    theory_2025_value = theory_2025["data"]["a_mu_sm_total"]["value"]
    theory_2025_unc = theory_2025["data"]["a_mu_sm_total"]["uncertainty"]
    published_2025_delta = theory_2025["data"]["delta_a_mu_exp_minus_sm"]["value"]
    published_2025_unc = theory_2025["data"]["delta_a_mu_exp_minus_sm"]["uncertainty"]

    baselines = [
        {
            "label": "source_locked_2025_derived",
            "a_mu_exp": exp_2025_value,
            "experimental_uncertainty": exp_2025_unc,
            "a_mu_sm": theory_2025_value,
            "sm_uncertainty": theory_2025_unc,
            "delta_a_mu": exp_2025_value - theory_2025_value,
            "combined_uncertainty": math.sqrt(exp_2025_unc**2 + theory_2025_unc**2),
            "provenance_status": "source_locked",
            "source": str(theory_2025_json.relative_to(root_path)),
        },
        {
            "label": "source_locked_2025_published",
            "delta_a_mu": published_2025_delta,
            "combined_uncertainty": published_2025_unc,
            "provenance_status": "source_locked",
            "source": str(theory_2025_json.relative_to(root_path)),
        },
        baseline_entry(
            "local_2023_data_driven",
            legacy_2023["data"]["a_mu_exp"]["value"],
            legacy_2023["data"]["a_mu_exp"]["error"],
            legacy_2023["data"]["a_mu_sm"]["value"],
            legacy_2023["data"]["a_mu_sm"]["error"],
            "historical_local_reference",
            str(legacy_2023_json.relative_to(root_path)),
        ),
        baseline_entry(
            "local_2021_lattice_qcd",
            local_module.A_MU_EXPERIMENT,
            local_module.A_MU_UNCERTAINTY,
            local_module.SM_PREDICTIONS["2021_lattice_qcd"]["value"],
            local_module.SM_PREDICTIONS["2021_lattice_qcd"]["uncertainty"],
            "historical_local_reference",
            str(local_muon_module_path.relative_to(root_path)),
        ),
        baseline_entry(
            "local_2025_theory_initiative_snapshot",
            local_module.A_MU_EXPERIMENT,
            local_module.A_MU_UNCERTAINTY,
            local_module.SM_PREDICTIONS["2025_theory_initiative"]["value"],
            local_module.SM_PREDICTIONS["2025_theory_initiative"]["uncertainty"],
            "historical_local_reference",
            str(local_muon_module_path.relative_to(root_path)),
        ),
    ]

    payload = {
        "source_package": "topic_0.8 muon g-2 baseline package",
        "canonical_verification_baseline": "source_locked_2025_derived",
        "baselines": baselines,
    }
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
