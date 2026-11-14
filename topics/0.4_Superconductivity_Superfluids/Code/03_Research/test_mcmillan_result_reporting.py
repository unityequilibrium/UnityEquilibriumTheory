"""Software regression only: preserve the existing McMillan decision contract.

No producer import, benchmark rerun, physical-data admission or UET validation.
The decision helper is extracted from its owner; no copied evolution/fit law.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path


TOPIC = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name("Experiment_Superconductor_Data.py")
RESULT = TOPIC / "Result/artifacts/0_4_superconductivity_superfluids_verification.json"


def decision_helper():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8-sig"))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "analyze_failures"]
    assert len(functions) == 1
    assert not functions[0].decorator_list
    assert all(isinstance(n.func, ast.Name) and n.func.id in {"sorted", "len"}
               for n in ast.walk(functions[0]) if isinstance(n, ast.Call))
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal))
                   for n in ast.walk(functions[0]))
    namespace = {}
    # Only this pure decision helper executes; top-level imports, data writes,
    # the scientific benchmark and main remain unexecuted.
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace["analyze_failures"]


def test_saved_model_failure_is_not_execution_failure_or_physics_acceptance():
    record = json.loads(RESULT.read_text(encoding="utf-8-sig"))
    decision = decision_helper()(record["metrics"]["average_relative_error_percent"], record["results"])
    assert record["run_status"] == "PASS"
    assert record["model_gate_status"] == record["status"] == decision["model_gate_status"] == "FAIL"
    assert decision["failed_material_count"] == record["failure_analysis"]["failed_material_count"]


def test_original_average_and_per_material_requirements_are_both_enforced():
    decide = decision_helper()
    def row(error, within):
        return {"name": "synthetic decision fixture", "relative_error_percent": error,
                "within_20_percent": within, "type": "fixture", "source": "not measured data"}
    assert decide(19, [row(19, True)])["model_gate_status"] == "PASS"
    assert decide(20, [row(19, True)])["model_gate_status"] == "PASS"
    assert decide(21, [row(21, False)])["model_gate_status"] == "FAIL"
    assert decide(19, [row(20, False)])["model_gate_status"] == "FAIL"
