"""Create a local extracted JSON benchmark for official NuFIT 6.0 parameter tables."""

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
from pathlib import Path


REPO_ROOT = _UET_REPO_ROOT / "docs"
SOURCE_PDF = REPO_ROOT / "docs" / "data" / "external" / "particle_physics" / "nufit" / "official" / "v60.tbl-parameters.pdf"
OUT_JSON = REPO_ROOT / "docs" / "data" / "external" / "particle_physics" / "nufit" / "official" / "nufit_v60_parameters_extracted.json"


def main() -> int:
    payload = {
        "source": "NuFIT 6.0 official parameter-table PDF",
        "source_url": "https://www.nu-fit.org/sites/default/files/v60.tbl-parameters.pdf",
        "source_page_url": "https://www.nu-fit.org/?q=node/294",
        "local_source_file": str(SOURCE_PDF.relative_to(REPO_ROOT)),
        "publication_reference": "JHEP 12 (2024) 216, doi:10.1007/JHEP12(2024)216",
        "transcription_status": "checked transcription",
        "manual_review_required": True,
        "schema_validation_status": "pending external validation script",
        "transcription_note": (
            "Values were manually transcribed from the official NuFIT v6.0 parameter-table PDF into a local JSON "
            "because the workspace does not currently bundle a PDF table parser. Recheck against the PDF if this "
            "table is later machine-parsed."
        ),
        "variants": {
            "ic19_without_sk_atm": {
                "normal_ordering": {
                    "theta12_deg": {"best_fit": 33.68, "1sigma_plus": 0.73, "1sigma_minus": 0.70, "3sigma_min": 31.63, "3sigma_max": 35.95},
                    "theta23_deg": {"best_fit": 48.5, "1sigma_plus": 0.7, "1sigma_minus": 0.9, "3sigma_min": 41.0, "3sigma_max": 50.5},
                    "theta13_deg": {"best_fit": 8.52, "1sigma_plus": 0.11, "1sigma_minus": 0.11, "3sigma_min": 8.18, "3sigma_max": 8.87},
                    "delta_m21_sq_1e5_eV2": {"best_fit": 7.49, "1sigma_plus": 0.19, "1sigma_minus": 0.19, "3sigma_min": 6.92, "3sigma_max": 8.05},
                    "delta_m3l_sq_1e3_eV2": {"best_fit": 2.534, "1sigma_plus": 0.025, "1sigma_minus": 0.023, "3sigma_min": 2.463, "3sigma_max": 2.606},
                }
            },
            "ic24_with_sk_atm": {
                "normal_ordering": {
                    "theta12_deg": {"best_fit": 33.68, "1sigma_plus": 0.73, "1sigma_minus": 0.70, "3sigma_min": 31.63, "3sigma_max": 35.95},
                    "theta23_deg": {"best_fit": 43.3, "1sigma_plus": 1.0, "1sigma_minus": 0.8, "3sigma_min": 41.3, "3sigma_max": 49.9},
                    "theta13_deg": {"best_fit": 8.56, "1sigma_plus": 0.11, "1sigma_minus": 0.11, "3sigma_min": 8.19, "3sigma_max": 8.89},
                    "delta_m21_sq_1e5_eV2": {"best_fit": 7.49, "1sigma_plus": 0.19, "1sigma_minus": 0.19, "3sigma_min": 6.92, "3sigma_max": 8.05},
                    "delta_m3l_sq_1e3_eV2": {"best_fit": 2.513, "1sigma_plus": 0.021, "1sigma_minus": 0.019, "3sigma_min": 2.451, "3sigma_max": 2.578},
                }
            },
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
