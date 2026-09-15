"""Regression tests for shared verification input path resolution."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path


ROOT = repo_root()
SCRIPT = ROOT / "docs/scripts/audit/run_core_verifications.py"


def _module():
    spec = importlib.util.spec_from_file_location("run_core_verifications", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_topic_relative_input_is_preferred(tmp_path: Path) -> None:
    module = _module()
    repo_root = tmp_path / "repo"
    topic_dir = repo_root / "docs" / "topics" / "topic"
    topic_dir.mkdir(parents=True)
    target = topic_dir / "data" / "sample.txt"
    target.parent.mkdir(parents=True)
    target.write_text("topic", encoding="utf-8")

    record = module.resolve_input_path(topic_dir, "data/sample.txt", repo_root)

    assert record["status"] == "present"
    assert record["resolution_base"] == "topic_dir"
    assert record["resolved_path"] == "docs/topics/topic/data/sample.txt"


def test_repository_relative_input_is_resolved_when_topic_candidate_is_absent(
    tmp_path: Path,
) -> None:
    module = _module()
    repo_root = tmp_path / "repo"
    topic_dir = repo_root / "docs" / "topics" / "topic"
    topic_dir.mkdir(parents=True)
    target = repo_root / "docs" / "data" / "external" / "source.json"
    target.parent.mkdir(parents=True)
    target.write_text("repo", encoding="utf-8")

    record = module.resolve_input_path(
        topic_dir, "docs/data/external/source.json", repo_root
    )

    assert record["status"] == "present"
    assert record["resolution_base"] == "repo_root"
    assert record["resolved_path"] == "docs/data/external/source.json"


def test_missing_input_is_explicitly_recorded(tmp_path: Path) -> None:
    module = _module()
    repo_root = tmp_path / "repo"
    topic_dir = repo_root / "docs" / "topics" / "topic"
    topic_dir.mkdir(parents=True)

    record = module.resolve_input_path(topic_dir, "data/missing.txt", repo_root)

    assert record["status"] == "missing"
    assert record["resolution_status"] == "missing"
    assert len(record["candidates"]) == 2


def test_conflicting_topic_and_repository_candidates_are_ambiguous(
    tmp_path: Path,
) -> None:
    module = _module()
    repo_root = tmp_path / "repo"
    topic_dir = repo_root / "docs" / "topics" / "topic"
    topic_dir.mkdir(parents=True)
    topic_target = topic_dir / "shared.txt"
    repo_target = repo_root / "shared.txt"
    topic_target.write_text("topic", encoding="utf-8")
    repo_target.write_text("repo", encoding="utf-8")

    record = module.resolve_input_path(topic_dir, "shared.txt", repo_root)

    assert record["status"] == "ambiguous"
    assert record["resolution_status"] == "ambiguous"
    assert {item["resolution_base"] for item in record["candidates"]} == {
        "topic_dir",
        "repo_root",
    }
