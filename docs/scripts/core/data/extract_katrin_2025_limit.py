"""
Extract the official KATRIN 2025 direct neutrino-mass limit from the local
source-locked KATRIN results page.
"""

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
import re
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
source_html = (
    root_path
    / "docs"
    / "data"
    / "external"
    / "particle_physics"
    / "katrin"
    / "katrin_latest_results_2025.html"
)
out_json = (
    root_path
    / "docs"
    / "data"
    / "external"
    / "particle_physics"
    / "katrin"
    / "katrin_latest_results_2025.json"
)


def main() -> int:
    text = source_html.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"0\.45 eV/c", text)
    if not match:
        raise RuntimeError("Could not locate 0.45 eV/c^2 limit in KATRIN source HTML")

    payload = {
        "source": "KATRIN official latest-results page",
        "source_url": "https://www.katrin.kit.edu/1271.php",
        "local_source_file": str(source_html.relative_to(root_path)),
        "publication_reference": "Science, published 10 April 2025",
        "data": {
            "mass_limit_eV_c2": 0.45,
            "mass_limit_kg": 8e-37,
            "year": 2025,
            "confidence_note": "Upper limit reported on the official KATRIN results page.",
        },
        "extraction_note": "Value extracted from the local source-locked KATRIN HTML page.",
    }
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
