"""The generated FORMAL contract must pass the unchanged standard-30 validator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import new_formal_contract  # noqa: E402

REPO_ROOT = HERE.parents[3]
_spec = importlib.util.spec_from_file_location(
    "audit_calculation_completeness", REPO_ROOT / "docs/scripts/audit/audit_calculation_completeness.py")
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


def test_generated_formal_contract_validates(tmp_path: Path) -> None:
    (tmp_path / "docs/meta/schemas").mkdir(parents=True)
    (tmp_path / audit.SCHEMA).write_bytes((REPO_ROOT / audit.SCHEMA).read_bytes())
    code, test = "docs/core/02_equations/demo.py", "docs/core/05_tests/physics/test_demo.py"
    for rel in (code, test):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_bytes(b"x = 1\r\n")  # CRLF on disk must hash like LF
    contract = new_formal_contract.build_contract(
        tmp_path, "DEMO_FORMAL_V1", "Does the demo identity hold?", "identity", ["DEMO"], [code], [test])
    review = audit.validate_contract(contract, tmp_path)
    assert review["errors"] == []
    assert contract["identities"][0]["sha256"] == audit.identity_hash(tmp_path, contract["identities"][0])
