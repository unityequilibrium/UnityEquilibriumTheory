"""Extract the official Muon g-2 Theory Initiative 2025 comparator from local HTML."""

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
from pathlib import Path


REPO_ROOT = _UET_REPO_ROOT / "docs"
SOURCE_HTML = REPO_ROOT / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "theory" / "muon_g2_theory_white_paper_2025.html"
OUT_JSON = REPO_ROOT / "docs" / "data" / "external" / "particle_physics" / "muon_g2" / "theory" / "muon_g2_theory_2025_total_sm.json"


def parse_value(raw: str) -> tuple[float, float]:
    match = re.fullmatch(r"([\d ]+)\((\d+)\)", raw.strip())
    if not match:
        raise ValueError(f"Unexpected numeric format: {raw}")
    digits = match.group(1).replace(" ", "")
    err_digits = match.group(2)
    value = float(digits) * 1e-11
    uncertainty = float(err_digits) * 1e-11
    return value, uncertainty


def main() -> int:
    text = SOURCE_HTML.read_text(encoding="utf-8", errors="replace")
    sm_match = re.search(r"Total SM Value</td>.*?<td class=\"noline right\">([\d ]+\(\d+\))</td>", text, re.DOTALL)
    delta_match = re.search(r"Difference: .*?<td class=\"right\">([\d ]+\(\d+\))</td>", text, re.DOTALL)
    if not sm_match or not delta_match:
        raise ValueError("Could not locate Theory Initiative summary-table values in HTML")

    sm_value, sm_unc = parse_value(sm_match.group(1))
    delta_value_raw = delta_match.group(1).replace(" ", "")
    delta_val = float(delta_value_raw.split("(")[0]) * 1e-11
    delta_unc = float(delta_value_raw.split("(")[1].rstrip(")")) * 1e-11

    payload = {
        "source": "Muon g-2 Theory Initiative White Paper 2025",
        "source_file": str(SOURCE_HTML.relative_to(REPO_ROOT)),
        "source_url": "https://muon-gm2-theory.illinois.edu/white-paper-25/",
        "publication_reference": "Physics Reports 1143 (2025) 1-158 / arXiv:2505.21476",
        "data": {
            "a_mu_sm_total": {"value": sm_value, "uncertainty": sm_unc},
            "delta_a_mu_exp_minus_sm": {"value": delta_val, "uncertainty": delta_unc},
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
