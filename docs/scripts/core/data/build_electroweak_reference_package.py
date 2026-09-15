"""Build a structured electroweak reference package for topic 0.6.

This consolidates what is directly source-locked from PDG SQLite and what still
comes from a checked local electroweak reference file.
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
legacy_json = root_path / "docs" / "topics" / "0.6_Electroweak_Physics" / "Data" / "03_Research" / "pdg_electroweak_2024.json"
output_json = root_path / "docs" / "data" / "external" / "particle_physics" / "pdg" / "electroweak_reference_package.json"
mapping_audit_json = root_path / "docs" / "data" / "external" / "particle_physics" / "pdg" / "electroweak_mapping_audit.json"


def pdg_quantity(cur: sqlite3.Cursor, particle_name: str, suffix: str) -> dict:
    particle = cur.execute(
        "select pdgid, name from pdgparticle where name=? limit 1",
        (particle_name,),
    ).fetchone()
    if not particle:
        raise KeyError(f"PDG particle not found: {particle_name}")
    pdgid, _ = particle
    row = cur.execute(
        """
        select value, error_positive, error_negative, unit_text, display_value_text
        from pdgdata
        where pdgid=? and edition='2025' and in_summary_table=1
        order by sort
        limit 1
        """,
        (pdgid + suffix,),
    ).fetchone()
    if not row:
        raise KeyError(f"PDG quantity not found: {particle_name}{suffix}")
    value, err_pos, err_neg, unit, display = row
    return {
        "value": float(value),
        "error_positive": float(err_pos or 0.0),
        "error_negative": float(err_neg or 0.0),
        "unit": unit,
        "display": display,
        "provenance_status": "source_locked_pdg_sqlite",
    }


def main() -> int:
    legacy = json.loads(legacy_json.read_text(encoding="utf-8"))
    mapping_audit = json.loads(mapping_audit_json.read_text(encoding="utf-8")) if mapping_audit_json.exists() else None
    con = sqlite3.connect(pdg_db)
    cur = con.cursor()

    payload = {
        "source_package": "topic_0.6 electroweak reference package",
        "pdg_sqlite_source": str(pdg_db.relative_to(root_path)),
        "checked_local_reference_source": str(legacy_json.relative_to(root_path)),
        "mapping_audit_source": str(mapping_audit_json.relative_to(root_path)) if mapping_audit_json.exists() else None,
        "weak_mixing_angle_direct_mapping_found": mapping_audit["direct_mapping_found"] if mapping_audit else False,
        "references": {
            "m_W": pdg_quantity(cur, "W+", "M"),
            "m_Z": pdg_quantity(cur, "Z0", "M"),
            "m_H": pdg_quantity(cur, "H", "M"),
            "sin2_theta_W_effective": {
                "value": legacy["data"]["sin2_theta_W"]["value"],
                "error_positive": legacy["data"]["sin2_theta_W"]["error"],
                "error_negative": legacy["data"]["sin2_theta_W"]["error"],
                "unit": "dimensionless",
                "display": f"{legacy['data']['sin2_theta_W']['value']}+-{legacy['data']['sin2_theta_W']['error']}",
                "provenance_status": "checked_local_reference",
                "source_note": "Direct weak-mixing-angle observable was not located in the current PDG SQLite workflow; this remains a checked local electroweak reference until a direct upstream mapping is added.",
            },
            "fermi_constant": {
                "value": legacy["data"]["G_fermi_GeV2"]["value"],
                "error_positive": legacy["data"]["G_fermi_GeV2"]["error"],
                "error_negative": legacy["data"]["G_fermi_GeV2"]["error"],
                "unit": "GeV^-2",
                "display": str(legacy["data"]["G_fermi_GeV2"]["value"]),
                "provenance_status": "checked_local_reference",
            },
        },
    }
    con.close()
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
