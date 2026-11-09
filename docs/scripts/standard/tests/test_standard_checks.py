"""Regression tests for the Research Standard v2 CI checks.

These are bookkeeping tests (not physics evidence): they prove the checks accept
a valid record set and reject each forbidden pattern in docs/STANDARD.md.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import check_preregistration  # noqa: E402
from check_schema import SchemaChecker  # noqa: E402

REPO_ROOT = HERE.parents[3]
SCHEMA = REPO_ROOT / "docs" / "standard" / "schema.json"

APPROVAL = {"approved_by": "author", "date": "2026-11-09", "role": "AUTHOR"}
DATA_BYTES = b"gamma_minus_one_bound,2.3e-5\n"

THEORY = {
    "schema": "uet-theory-card-v2", "card_id": "UET_PARENT", "version": 1, "status": "APPROVED",
    "core_equations": [{"formula_id": "F1", "expression": "S=...", "code_path": "x.py"}],
    "unit_system": "natural", "sign_convention": "(-,+,+,+)",
    "fields_parameters": [{"symbol": "phi", "meaning": "response scalar", "mass_dimension": 1}],
    "nearest_known_class": {"name": "scalar-tensor", "references": ["ref"], "variable_map": "phi->phi"},
    "differences_from_known_class": [], "redundant_parameters": [], "predictions": [],
    "lane_mappings": [], "approval": APPROVAL,
}
CARD = {
    "schema": "uet-test-card-v2", "test_id": "T001", "status": "APPROVED", "claim_id": "C_PPN",
    "theory_card": {"card_id": "UET_PARENT", "version": 1}, "hypothesis": "h",
    "observable": {"quantity": "gamma-1", "unit": "1", "domain": "solar system"},
    "test_kind": "CONSTRAINT",
    "data_sources": [{"data_id": "CASSINI", "role": "COMPARISON", "exposure": "SEEN_SUMMARY"}],
    "prediction_method": {"script": "p.py", "description": "d"},
    "free_parameters": ["xi"], "fixed_parameters": ["kappa"],
    "pass_criterion": "|gamma-1| < 2.3e-5", "fail_criterion": "otherwise",
    "drafted_by": "claude", "approval": APPROVAL,
}
RESULT = {
    "schema": "uet-result-v2", "result_id": "R001", "claim_id": "C_PPN", "level": "L2_CONFRONTED",
    "test_card_id": "T001", "outcome": "PASS",
    "numbers": [{"name": "gamma-1", "value": 0.0, "unit": "1"}],
    "producer": {"script": "p.py", "commit": "abc1234"}, "artifacts": [], "date": "2026-11-09",
    "approval": APPROVAL,
}
CLAIMS = {"schema": "uet-claims-v2", "claims": [
    {"claim_id": "C_PPN", "statement": "s", "level": "L2_CONFRONTED", "evidence": ["R001"]}]}


def write(root: Path, rel: str, payload) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, bytes):
        path.write_bytes(payload)
    else:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def manifest() -> dict:
    return {"schema": "uet-data-manifest-v2", "entries": [{
        "data_id": "CASSINI", "description": "d", "source": "Bertotti 2003", "retrieved": "2026-11-09",
        "path": "data/cassini.csv", "sha256": hashlib.sha256(DATA_BYTES).hexdigest(),
        "license": "fact", "visibility": "PUBLIC"}]}


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "standard").mkdir(parents=True)
    shutil.copy(SCHEMA, root / "docs" / "standard" / "schema.json")
    return root


def full_set(root: Path) -> None:
    write(root, "docs/core/theory_card.json", THEORY)
    write(root, "docs/standard/data_manifest.json", manifest())
    write(root, "data/cassini.csv", DATA_BYTES)
    write(root, "docs/standard/claims.json", CLAIMS)
    write(root, "docs/standard/tests/T001.json", CARD)
    write(root, "docs/standard/results/R001.json", RESULT)
    write(root, "p.py", b"print(1)\n")


def schema_errors(root: Path) -> list[str]:
    return SchemaChecker(root).run()


def test_empty_repo_is_clean(repo: Path) -> None:
    assert schema_errors(repo) == []


def test_full_valid_set_is_clean(repo: Path) -> None:
    full_set(repo)
    assert schema_errors(repo) == []


def test_status_outside_enum_is_rejected(repo: Path) -> None:
    full_set(repo)
    claims = copy.deepcopy(CLAIMS)
    claims["claims"][0]["level"] = "PASS_SCOPED_SOMETHING"
    write(repo, "docs/standard/claims.json", claims)
    assert any("PASS_SCOPED_SOMETHING" in e for e in schema_errors(repo))


def test_claim_level_must_be_backed_by_result(repo: Path) -> None:
    full_set(repo)
    claims = copy.deepcopy(CLAIMS)
    claims["claims"][0]["level"] = "L3_REPLICATED"
    write(repo, "docs/standard/claims.json", claims)
    assert any("not backed" in e for e in schema_errors(repo))


def test_raw_data_hash_lock(repo: Path) -> None:
    full_set(repo)
    write(repo, "data/cassini.csv", DATA_BYTES + b"tampered\n")
    assert any("sha256 mismatch" in e for e in schema_errors(repo))


def test_drafter_cannot_approve_own_card(repo: Path) -> None:
    full_set(repo)
    card = copy.deepcopy(CARD)
    card["approval"] = dict(APPROVAL, approved_by="Claude")
    write(repo, "docs/standard/tests/T001.json", card)
    assert any("approved by its drafter" in e for e in schema_errors(repo))


def test_fail_outcome_must_be_failed_level(repo: Path) -> None:
    full_set(repo)
    write(repo, "docs/standard/results/R001.json", dict(RESULT, outcome="FAIL"))
    assert any("FAILED" in e for e in schema_errors(repo))


# --- preregistration (git history) -------------------------------------------------


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def init_git(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.email", "t@example.invalid")
    git(root, "config", "user.name", "t")
    git(root, "config", "commit.gpgsign", "false")


def commit_all(root: Path, message: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


def prereg_errors(root: Path) -> list[str]:
    return check_preregistration.run(root)


def test_result_after_approval_is_clean(repo: Path) -> None:
    init_git(repo)
    write(repo, "docs/standard/tests/T001.json", CARD)
    commit_all(repo, "approve card")
    write(repo, "docs/standard/results/R001.json", RESULT)
    commit_all(repo, "add result")
    assert prereg_errors(repo) == []


def test_result_in_same_commit_as_approval_is_rejected(repo: Path) -> None:
    init_git(repo)
    write(repo, "docs/standard/tests/T001.json", CARD)
    write(repo, "docs/standard/results/R001.json", RESULT)
    commit_all(repo, "card and result together")
    assert any("does not come after" in e for e in prereg_errors(repo))


def test_result_before_approval_is_rejected(repo: Path) -> None:
    init_git(repo)
    write(repo, "docs/standard/tests/T001.json", dict(CARD, status="DRAFT"))
    write(repo, "docs/standard/results/R001.json", RESULT)
    commit_all(repo, "draft card and early result")
    write(repo, "docs/standard/tests/T001.json", CARD)
    commit_all(repo, "approve later")
    assert any("does not come after" in e for e in prereg_errors(repo))


def test_frozen_criterion_change_is_rejected(repo: Path) -> None:
    init_git(repo)
    write(repo, "docs/standard/tests/T001.json", CARD)
    commit_all(repo, "approve card")
    write(repo, "docs/standard/tests/T001.json", dict(CARD, pass_criterion="|gamma-1| < 1e-3"))
    commit_all(repo, "loosen criterion")
    assert any("frozen fields changed" in e for e in prereg_errors(repo))


def test_uncommitted_approval_blocks_result(repo: Path) -> None:
    init_git(repo)
    write(repo, "docs/standard/tests/T001.json", dict(CARD, status="DRAFT"))
    commit_all(repo, "draft card")
    write(repo, "docs/standard/tests/T001.json", CARD)
    write(repo, "docs/standard/results/R001.json", RESULT)
    assert any("not committed yet" in e for e in prereg_errors(repo))


def test_data_hidden_by_gitignore_is_rejected(repo: Path) -> None:
    full_set(repo)
    init_git(repo)
    (repo / ".gitignore").write_text("*.csv\n", encoding="utf-8")
    commit_all(repo, "csv silently ignored")
    errors = schema_errors(repo)
    assert any("not tracked by git" in e and "cassini.csv" in e for e in errors)


def test_force_added_data_is_accepted(repo: Path) -> None:
    full_set(repo)
    init_git(repo)
    (repo / ".gitignore").write_text("*.csv\n", encoding="utf-8")
    git(repo, "add", "-f", "data/cassini.csv")
    commit_all(repo, "csv force-added")
    assert schema_errors(repo) == []


def test_missing_producer_script_is_rejected(repo: Path) -> None:
    full_set(repo)
    (repo / "p.py").unlink()
    assert any("p.py missing" in e for e in schema_errors(repo))
