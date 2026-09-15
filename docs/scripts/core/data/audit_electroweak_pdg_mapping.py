"""Audit whether topic 0.6 electroweak observables can be mapped directly from PDG SQLite."""

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
import sqlite3
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
pdg_db = root_path / "docs" / "data" / "external" / "particle_physics" / "pdg" / "pdg-2025-v0.2.2.sqlite"
output_json = root_path / "docs" / "data" / "external" / "particle_physics" / "pdg" / "electroweak_mapping_audit.json"


SEARCH_QUERIES = {
    "pdgid_description": """
        select pdgid, description
        from pdgid
        where lower(description) like '%weinberg%'
           or lower(description) like '%weak mixing%'
           or lower(description) like '%theta_w%'
           or lower(description) like '%sin2%'
        limit 50
    """,
    "pdgitem_name": """
        select id, name
        from pdgitem
        where lower(name) like '%weinberg%'
           or lower(name) like '%weak mixing%'
           or lower(name) like '%theta%'
        limit 50
    """,
    "pdgdata_comment": """
        select pdgid, comment, display_value_text
        from pdgdata
        where lower(coalesce(comment, '')) like '%weinberg%'
           or lower(coalesce(comment, '')) like '%weak mixing%'
           or lower(coalesce(comment, '')) like '%theta%'
        limit 50
    """,
}


def main() -> int:
    con = sqlite3.connect(pdg_db)
    cur = con.cursor()
    findings = {key: cur.execute(sql).fetchall() for key, sql in SEARCH_QUERIES.items()}
    con.close()

    meaningful_matches = bool(findings["pdgid_description"] or findings["pdgdata_comment"])

    payload = {
        "source": str(pdg_db.relative_to(root_path)),
        "observable": "effective weak-mixing angle / sin^2(theta_W)",
        "direct_mapping_found": meaningful_matches,
        "queries": findings,
        "conclusion": (
            "No direct weak-mixing-angle mapping was located in the current PDG SQLite workflow."
            if not meaningful_matches
            else "Potential upstream mappings were found and require manual review."
        ),
    }
    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
