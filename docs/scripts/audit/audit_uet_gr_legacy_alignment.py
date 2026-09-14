"""Audit legacy Lorentz and Noether modules against current claim boundaries.

The audit intentionally does not promote a numerical self-comparison into a
covariance proof. A successful audit means the legacy limitations are detected
and quarantined in machine-readable form.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

LEGACY_LORENTZ_PATH = REPO_ROOT / "docs" / "core" / "uet_lorentz.py"
LEGACY_NOETHER_PATH = REPO_ROOT / "docs" / "core" / "uet_noether.py"
CANONICAL_LORENTZ_PATH = (
    REPO_ROOT
    / "docs"
    / "core"
    / "02_equations"
    / "lorentz_noether"
    / "uet_lorentz.py"
)
CANONICAL_NOETHER_PATH = (
    REPO_ROOT
    / "docs"
    / "core"
    / "02_equations"
    / "lorentz_noether"
    / "uet_noether.py"
)
ARTIFACT_PATH = (
    REPO_ROOT / "docs" / "core" / "artifacts" / "legacy_covariance_alignment_gate.json"
)


def _source_path(legacy: Path, canonical: Path) -> Path:
    """Read the canonical implementation while a legacy path is a shim."""

    return canonical if canonical.exists() else legacy


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _class_method(tree: ast.AST, class_name: str, method_name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == method_name:
                    return child
    raise RuntimeError(f"missing method {class_name}.{method_name}")


def _argument_names(function: ast.FunctionDef) -> list[str]:
    return [argument.arg for argument in function.args.args]


def _name_load_count(node: ast.AST, name: str) -> int:
    return sum(
        1
        for child in ast.walk(node)
        if isinstance(child, ast.Name)
        and child.id == name
        and isinstance(child.ctx, ast.Load)
    )


def _legacy_lorentz_findings(source: str) -> dict[str, Any]:
    tree = ast.parse(source)
    methods = [
        "check_lorentz_invariance",
        "check_lorentz_invariance_complex",
        "check_lorentz_invariance_schwarzschild",
        "check_lorentz_invariance_kerr",
        "check_lorentz_invariance_frw",
        "check_lorentz_invariance_time_dependent",
    ]
    method_nodes = [_class_method(tree, "UETLorentz", name) for name in methods]
    relativistic_omega = _class_method(tree, "UETLorentz", "relativistic_omega")
    lambda_loads = sum(_name_load_count(node, "Lambda") for node in method_nodes)
    metric_calls = sum(
        1
        for node in method_nodes
        for child in ast.walk(node)
        if isinstance(child, ast.Attribute)
        and isinstance(child.value, ast.Attribute)
        and isinstance(child.value.value, ast.Name)
        and child.value.value.id == "self"
        and child.value.attr == "metric"
    )
    return {
        "checked_methods": methods,
        "placeholder_field_assignments": source.count("C_transformed = C_4d"),
        "lorentz_matrix_loads_after_assignment": lambda_loads,
        "curved_metric_calls_in_claim_methods": metric_calls,
        "relativistic_omega_arguments": _argument_names(relativistic_omega),
        "metric_argument_present": "metric" in _argument_names(relativistic_omega),
        "legacy_status_constant_present": (
            'LEGACY_COVARIANCE_EVIDENCE_STATUS = "BLOCKED_FOR_INVARIANCE_CLAIMS"'
            in source
        ),
        "completion_overclaim_present": "LORENTZ INVARIANCE: IMPLEMENTATION COMPLETE" in source,
        "independent_information_field_present": "I_4d" in source,
    }


def _legacy_noether_findings(source: str) -> dict[str, Any]:
    tree = ast.parse(source)
    lagrangian = _class_method(tree, "UETNoether", "lagrangian_density")
    return {
        "lagrangian_arguments": _argument_names(lagrangian),
        "time_derivative_argument_present": any(
            name in _argument_names(lagrangian)
            for name in ("dC_dt", "time_derivative", "spacetime_gradient")
        ),
        "gradient_flow_update_present": "C = C - dt * grad_C" in source,
        "real_field_u1_proxy_present": "charge_density = self.params.beta * C * I" in source,
        "legacy_status_constant_present": (
            'LEGACY_NOETHER_EVIDENCE_STATUS = "BLOCKED_FOR_CONSERVATION_PROOF_CLAIMS"'
            in source
        ),
        "completion_overclaim_present": "NOETHER'S THEOREM: IMPLEMENTATION COMPLETE" in source,
        "metric_argument_present": "metric" in _argument_names(lagrangian),
    }


def build_gate() -> dict[str, Any]:
    lorentz_path = _source_path(LEGACY_LORENTZ_PATH, CANONICAL_LORENTZ_PATH)
    noether_path = _source_path(LEGACY_NOETHER_PATH, CANONICAL_NOETHER_PATH)
    lorentz_source = lorentz_path.read_text(encoding="utf-8")
    noether_source = noether_path.read_text(encoding="utf-8")
    lorentz = _legacy_lorentz_findings(lorentz_source)
    noether = _legacy_noether_findings(noether_source)

    quarantine_pass = (
        lorentz["legacy_status_constant_present"]
        and noether["legacy_status_constant_present"]
        and not lorentz["completion_overclaim_present"]
        and not noether["completion_overclaim_present"]
    )
    return {
        "schema_version": "1.0",
        "artifact": "legacy_covariance_alignment_gate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audit_status": "PASS" if quarantine_pass else "FAIL",
        "evidence_status": "BLOCKED",
        "claim_class": "LEGACY_EXPLORATORY_DIAGNOSTIC",
        "controlling_blocker": "legacy_covariance_not_implemented",
        "source_files": {
            "docs/core/uet_lorentz.py": _sha256(lorentz_path),
            "docs/core/uet_noether.py": _sha256(noether_path),
        },
        "source_paths_used": {
            "lorentz": str(lorentz_path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "noether": str(noether_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        },
        "findings": {
            "lorentz": lorentz,
            "noether": noether,
        },
        "gates": {
            "actual_lorentz_transform_application": {
                "status": "FAIL",
                "reason": "The generated Lambda matrix is not loaded after assignment and C_transformed aliases C_4d.",
            },
            "curved_metric_wiring": {
                "status": "FAIL",
                "reason": "Schwarzschild, Kerr, and FRW claim methods do not pass a metric into relativistic_omega.",
            },
            "covariant_noether_action": {
                "status": "FAIL",
                "reason": "The legacy density has no spacetime derivative or metric argument.",
            },
            "dynamics_consistent_conservation": {
                "status": "FAIL",
                "reason": "The claimed conservation checks evolve C with an ad hoc spatial-gradient update.",
            },
            "legacy_claim_quarantine": {
                "status": "PASS" if quarantine_pass else "FAIL",
                "reason": "Legacy modules carry explicit blocked evidence status and no completion banner.",
            },
        },
        "allowed_use": [
            "legacy formula inventory",
            "diagnostic code archaeology",
            "negative alignment tests",
        ],
        "blocked_use": [
            "Lorentz-invariance proof",
            "curved-spacetime covariance evidence",
            "Noether conservation proof",
            "Einstein-equation derivation",
        ],
        "next_controller": "covariant_parent_action_missing",
        "claim_impact": "legacy proof exports blocked; no topic readiness change",
    }


def write_gate(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    gate = build_gate()
    write_gate(gate)
    if args.print_summary:
        print(
            json.dumps(
                {
                    "audit_status": gate["audit_status"],
                    "evidence_status": gate["evidence_status"],
                    "controlling_blocker": gate["controlling_blocker"],
                    "next_controller": gate["next_controller"],
                },
                indent=2,
            )
        )
    return 2 if args.strict and gate["audit_status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
