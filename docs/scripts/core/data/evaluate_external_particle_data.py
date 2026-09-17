"""Evaluate downloaded external particle-physics source artifacts.

This does not certify UET correctness. It reports which downloaded sources are
machine-readable and whether current topic verification scripts are already linked
to those sources.
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
from pathlib import Path


REPO_ROOT = _UET_REPO_ROOT / "docs"
SOURCE_MANIFEST = (
    REPO_ROOT
    / "docs"
    / "data"
    / "external"
    / "particle_physics"
    / "external_particle_sources_manifest.json"
)
OUT_PATH = REPO_ROOT / "docs" / "meta" / "external_particle_data_evaluation.json"
REPORT_PATH = REPO_ROOT / "docs" / "meta" / "external_particle_data_evaluation.md"


TOPIC_SPECS = {
    "0.5_Nuclear_Binding_Hadrons": {
        "uses_external_sources_now": False,
        "current_command": "python docs/topics/0.5_Nuclear_Binding_Hadrons/Code/03_Research/Research_Nuclear_Binding.py",
        "current_problem": "Primary script still uses an embedded AME subset in code, not the downloaded AME raw table.",
        "next_fix": "Parse AME2020 raw table and replace NUCLEI_DATA with a source-locked extracted benchmark table.",
    },
    "0.6_Electroweak_Physics": {
        "uses_external_sources_now": False,
        "current_command": "python docs/topics/0.6_Electroweak_Physics/Code/03_Research/Research_Alpha_Decay.py",
        "current_problem": "Verification command is alpha-decay oriented and does not use PDG/HEPData electroweak source artifacts.",
        "next_fix": "Add an electroweak verifier that reads PDG SQLite constants and HEPData/CERN measurement tables.",
    },
    "0.7_Neutrino_Physics": {
        "uses_external_sources_now": False,
        "current_command": "python docs/topics/0.7_Neutrino_Physics/Code/03_Research/Research_Ft_Values.py",
        "current_problem": "Primary script checks beta-decay ft values and does not use NuFIT 6.0 source data.",
        "next_fix": "Add a NuFIT parser/table snapshot and run PMNS/mass-splitting residual checks from that source.",
    },
    "0.8_Muon_g2_Anomaly": {
        "uses_external_sources_now": False,
        "current_command": "python docs/topics/0.8_Muon_g2_Anomaly/Code/03_Research/Research_Muon_Anomaly.py",
        "current_problem": "Primary script reads 2023 local JSON, not the source-locked 2025 final-result documents.",
        "next_fix": "Extract the final 2025 numerical result from publication/table source and add a versioned comparison.",
    },
}


def load_manifest() -> dict:
    if not SOURCE_MANIFEST.exists():
        raise FileNotFoundError(f"Run fetch_external_particle_data.py first: {SOURCE_MANIFEST}")
    return json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))


def inspect_sqlite(path: Path) -> dict:
    if not path.exists():
        return {"ok": False, "error": "missing"}
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        tables = [row[0] for row in cur.execute("select name from sqlite_master where type='table'")]
        counts = {}
        for table in tables:
            try:
                counts[table] = cur.execute(f"select count(*) from {table}").fetchone()[0]
            except sqlite3.DatabaseError:
                counts[table] = None
        conn.close()
        return {"ok": True, "tables": tables, "counts": counts}
    except sqlite3.DatabaseError as exc:
        return {"ok": False, "error": str(exc)}


def evaluate_records(records: list[dict]) -> list[dict]:
    evaluated = []
    for record in records:
        local_path = REPO_ROOT / record["local_path"]
        detail = {}
        if record["source_type"] == "sqlite" and record["status"].startswith("downloaded"):
            detail = inspect_sqlite(local_path)
        elif record["status"].startswith("downloaded"):
            detail = {
                "ok": local_path.exists() and local_path.stat().st_size >= record["expected_min_bytes"],
                "requires_parser": not record["benchmark_ready"],
            }
        else:
            detail = {"ok": False, "error": record.get("error")}

        evaluated.append(
            {
                **record,
                "evaluation": detail,
                "data_grade": (
                    "benchmark_machine_readable"
                    if record["benchmark_ready"] and detail.get("ok")
                    else "source_locked_needs_parser"
                    if detail.get("ok")
                    else "not_available"
                ),
            }
        )
    return evaluated


def write_reports(evaluated: list[dict]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "source_manifest": str(SOURCE_MANIFEST.relative_to(REPO_ROOT)),
        "records": evaluated,
        "topic_linkage": TOPIC_SPECS,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# External Particle Data Evaluation",
        "",
        "This report is strict: source-locked files are not counted as theory validation until a topic verifier reads them.",
        "",
        "## Source Artifact Status",
        "",
        "| Dataset | Topic | Status | Data grade | Local path |",
        "| :-- | :-- | :-- | :-- | :-- |",
    ]
    for record in evaluated:
        lines.append(
            f"| `{record['dataset_id']}` | `{record['topic']}` | `{record['status']}` | "
            f"`{record['data_grade']}` | `{record['local_path']}` |"
        )

    lines.extend(
        [
            "",
            "## Topic Verification Linkage",
            "",
            "| Topic | Current state | Problem | Next fix |",
            "| :-- | :-- | :-- | :-- |",
        ]
    )
    for topic, spec in TOPIC_SPECS.items():
        state = "external-linked" if spec["uses_external_sources_now"] else "not external-linked yet"
        lines.append(f"| `{topic}` | `{state}` | {spec['current_problem']} | {spec['next_fix']} |")

    lines.extend(
        [
            "",
            "## Scientific Summary",
            "",
            "- PDG SQLite sources are the strongest immediate upgrade because they are machine-readable.",
            "- AME2020, NuFIT 6.0, and Muon g-2 final-result documents become scientifically useful only after parser/versioned table extraction.",
            "- Current `0.5-0.8` verification commands still mostly test internal snapshots, so theory error on the new source-locked data is not yet established.",
            "- The next remediation step is not more documentation; it is wiring topic verifiers to these source-locked artifacts.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote JSON: {OUT_PATH}")
    print(f"Wrote report: {REPORT_PATH}")


def main() -> int:
    manifest = load_manifest()
    evaluated = evaluate_records(manifest["records"])
    write_reports(evaluated)
    unavailable = [record for record in evaluated if record["data_grade"] == "not_available"]
    return 1 if unavailable else 0


if __name__ == "__main__":
    raise SystemExit(main())
