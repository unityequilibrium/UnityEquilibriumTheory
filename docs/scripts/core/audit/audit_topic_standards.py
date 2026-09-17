"""
Audit topic-standard coverage and readiness metadata consistency.

This still does not certify scientific correctness, but it does enforce that the repository's
topic inventory, readiness metadata, and structured-topic requirements remain aligned.
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
from pathlib import Path


DOCS_ROOT = _UET_REPO_ROOT / "docs"
TOPICS_ROOT = DOCS_ROOT / "topics"
READINESS_FILE = DOCS_ROOT / "meta" / "topic_readiness.json"
FLAGSHIP_REQUIRED = [
    "METHOD.md",
    "DATA_MANIFEST.md",
    "VERIFICATION_SPEC.md",
    "BASELINE_COMPARISON.md",
    "LIMITATIONS.md",
]
CORE_REQUIRED = FLAGSHIP_REQUIRED
AUDIT_TIERS = {"A", "B", "C", "D"}
SCOPE_CLASSES = {"core_research", "future_concept", "support_workspace"}
DATA_REALITY_STATUSES = {
    "no data path",
    "embedded local only",
    "manual or placeholder",
    "real source referenced",
    "manifested real dataset",
}
SCORE_FIELDS = [
    "structure_score",
    "data_reality_score",
    "verification_score",
    "mathematical_rigor_score",
    "physical_rigor_score",
    "claim_integrity_score",
]


def load_readiness():
    data = json.loads(READINESS_FILE.read_text(encoding="utf-8"))
    return data, {entry["name"]: entry for entry in data["topics"]}


def main() -> int:
    readiness_data, readiness = load_readiness()
    failures = []
    topic_dirs = sorted(path for path in TOPICS_ROOT.iterdir() if path.is_dir())
    numbered = [path for path in topic_dirs if path.name.startswith("0.")]
    support = [path for path in topic_dirs if not path.name.startswith("0.")]

    if readiness_data.get("scope", {}).get("numbered_topics") != len(numbered):
        failures.append(
            f"Mismatch numbered topic count: metadata={readiness_data.get('scope', {}).get('numbered_topics')} actual={len(numbered)}"
        )

    if readiness_data.get("scope", {}).get("support_workspaces") != len(support):
        failures.append(
            f"Mismatch support workspace count: metadata={readiness_data.get('scope', {}).get('support_workspaces')} actual={len(support)}"
        )

    metadata_core = sum(
        1 for entry in readiness.values() if entry.get("scope_class") == "core_research"
    )
    metadata_future = sum(
        1 for entry in readiness.values() if entry.get("scope_class") == "future_concept"
    )

    if readiness_data.get("scope", {}).get("core_research_topics") != metadata_core:
        failures.append(
            f"Mismatch core research count: metadata={readiness_data.get('scope', {}).get('core_research_topics')} actual={metadata_core}"
        )

    if readiness_data.get("scope", {}).get("future_concept_topics") != metadata_future:
        failures.append(
            f"Mismatch future concept count: metadata={readiness_data.get('scope', {}).get('future_concept_topics')} actual={metadata_future}"
        )

    for topic_dir in topic_dirs:
        entry = readiness.get(topic_dir.name)
        if entry is None:
            failures.append(f"Missing readiness entry: {topic_dir.name}")
            continue

        scope_class = entry.get("scope_class")
        if scope_class not in SCOPE_CLASSES:
            failures.append(f"Invalid scope_class: {topic_dir.name} -> {scope_class}")

        if entry.get("kind") == "support_workspace":
            continue

        readme = topic_dir / "README.md"
        if not readme.exists():
            failures.append(f"Missing README: {topic_dir.name}")

        tier = entry.get("audit_tier")
        if tier not in AUDIT_TIERS:
            failures.append(f"Invalid audit tier: {topic_dir.name} -> {tier}")

        data_status = entry.get("data_reality_status")
        if data_status not in DATA_REALITY_STATUSES:
            failures.append(f"Invalid data reality status: {topic_dir.name} -> {data_status}")

        for field in SCORE_FIELDS:
            value = entry.get(field)
            if value not in {0, 1, 2, 3}:
                failures.append(f"Invalid {field}: {topic_dir.name} -> {value}")

        if not entry.get("recommended_next_action"):
            failures.append(f"Missing recommended_next_action: {topic_dir.name}")

        status = entry.get("status")
        if status == "Structured":
            for filename in FLAGSHIP_REQUIRED:
                if not (topic_dir / filename).exists():
                    failures.append(f"Missing {filename}: {topic_dir.name}")

        if scope_class == "core_research":
            for filename in CORE_REQUIRED:
                if not (topic_dir / filename).exists():
                    failures.append(f"Core topic missing {filename}: {topic_dir.name}")

        if tier == "A":
            for filename in FLAGSHIP_REQUIRED:
                if not (topic_dir / filename).exists():
                    failures.append(f"Tier A topic missing {filename}: {topic_dir.name}")

        if scope_class == "future_concept" and tier != "D":
            failures.append(f"Future concept must remain Tier D in this phase: {topic_dir.name}")

        if scope_class == "future_concept" and status not in {"Draft", "Archived"}:
            failures.append(f"Future concept should not advertise mature status in this phase: {topic_dir.name}")

    if failures:
        print("Topic standards audit failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Topic standards audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
