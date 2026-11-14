"""
Wave 10 operator-form requirement gate.

Waves 5-9 exposed a useful but still blocked path: the core engine now has an
opt-in spatial-coupled candidate, but coefficient sweeps, finite-size windows,
and longer relaxation runs have not produced measurable correlation growth or a
universality shift. This script turns that evidence chain into a
machine-readable requirement artifact before any spatial_coupled_v2 proposal is
allowed to carry stronger claims.

This is a design-requirement gate, not a physics-validation verifier.
"""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET docs root not found")


ROOT = _bootstrap()
TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_operator_form_requirement_gate.json"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
ALIGNMENT_AUDIT_PATH = ROOT / "docs" / "core" / "WAVE5_MASTER_EQUATION_ALIGNMENT_AUDIT.md"

PRIOR_ARTIFACTS = {
    "wave5_spatial_coupling": "0_11_spatial_coupling_scaling.json",
    "wave6_coefficient_sensitivity": "0_11_spatial_coupling_sensitivity.json",
    "wave7_correlation_length": "0_11_correlation_length_diagnostics.json",
    "wave8_finite_size": "0_11_finite_size_scaling_diagnostics.json",
    "wave9_critical_window_relaxation": "0_11_critical_window_relaxation_diagnostics.json",
}


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def gate_status(artifact: dict[str, Any], gate_name: str) -> str:
    return artifact.get("gates", {}).get(gate_name, {}).get("status", "MISSING")


def nested_get(data: dict[str, Any], path: list[str], default: Any = None) -> Any:
    cursor: Any = data
    for key in path:
        if not isinstance(cursor, dict) or key not in cursor:
            return default
        cursor = cursor[key]
    return cursor


def artifact_input(path: Path, role: str) -> dict[str, str]:
    return {
        "path": relpath(path),
        "sha256": hash_file(path),
        "role": role,
    }


def run_requirement_gate() -> dict[str, Any]:
    loaded: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    malformed: list[str] = []

    for label, filename in PRIOR_ARTIFACTS.items():
        path = ARTIFACT_DIR / filename
        if not path.exists():
            missing.append(filename)
            continue
        try:
            loaded[label] = load_json(path)
        except json.JSONDecodeError:
            malformed.append(filename)

    wave5 = loaded.get("wave5_spatial_coupling", {})
    wave6 = loaded.get("wave6_coefficient_sensitivity", {})
    wave7 = loaded.get("wave7_correlation_length", {})
    wave8 = loaded.get("wave8_finite_size", {})
    wave9 = loaded.get("wave9_critical_window_relaxation", {})

    prior_artifact_chain_gate = {
        "status": "PASS" if not missing and not malformed and len(loaded) == len(PRIOR_ARTIFACTS) else "BLOCKED",
        "required_condition": "Wave 5-9 artifacts must exist and be valid JSON before designing the next operator revision.",
        "loaded_artifacts": sorted(loaded.keys()),
        "missing_artifacts": missing,
        "malformed_artifacts": malformed,
    }

    core_engine_alignment_gate = {
        "status": (
            "PASS"
            if gate_status(wave5, "engine_alignment_gate") == "PASS"
            and gate_status(wave5, "spatial_operator_gate") == "PASS"
            and CORE_ENGINE_PATH.exists()
            else "BLOCKED"
        ),
        "required_condition": "The current candidate must be exposed through core engine helpers before a v2 path is designed.",
        "engine_alignment_gate": gate_status(wave5, "engine_alignment_gate"),
        "spatial_operator_gate": gate_status(wave5, "spatial_operator_gate"),
        "core_engine_path": relpath(CORE_ENGINE_PATH),
    }

    coefficient_only_path_gate = {
        "status": "PASS" if gate_status(wave6, "coefficient_sensitivity_gate") == "PASS" else "BLOCKED",
        "required_condition": "Coefficient-only tuning must produce at least one stable near-Ising case before it remains a plausible repair path.",
        "coefficient_sensitivity_gate": gate_status(wave6, "coefficient_sensitivity_gate"),
        "operator_form_revision_gate": gate_status(wave6, "operator_form_revision_gate"),
        "best_beta": nested_get(wave6, ["metrics", "best_case", "beta"]),
        "near_ising_case_count": nested_get(
            wave6,
            ["gates", "coefficient_sensitivity_gate", "near_ising_case_count"],
        ),
    }

    finite_size_signal_gate = {
        "status": (
            "PASS"
            if gate_status(wave8, "correlation_window_gate") == "PASS"
            and gate_status(wave8, "operator_separation_gate") == "PASS"
            else "BLOCKED"
        ),
        "required_condition": "The current finite-size diagnostics must show adequate xi/L and spatial-vs-baseline separation.",
        "finite_size_coverage_gate": gate_status(wave8, "finite_size_coverage_gate"),
        "binder_crossing_gate": gate_status(wave8, "binder_crossing_gate"),
        "correlation_window_gate": gate_status(wave8, "correlation_window_gate"),
        "operator_separation_gate": gate_status(wave8, "operator_separation_gate"),
        "max_spatial_xi_over_L_near": nested_get(
            wave8,
            ["gates", "correlation_window_gate", "max_spatial_xi_over_L_near"],
        ),
        "max_baseline_xi_over_L_near": nested_get(
            wave8,
            ["gates", "operator_separation_gate", "max_baseline_xi_over_L_near"],
        ),
    }

    critical_window_path_gate = {
        "status": (
            "PASS"
            if gate_status(wave9, "critical_window_extension_gate") == "PASS"
            and gate_status(wave9, "relaxation_sensitivity_gate") == "PASS"
            and gate_status(wave9, "operator_separation_gate") == "PASS"
            else "BLOCKED"
        ),
        "required_condition": "Closer-to-Tc and longer relaxation runs must lift xi/L and separate from baseline before runtime/window extension remains a plausible repair path.",
        "critical_window_extension_gate": gate_status(wave9, "critical_window_extension_gate"),
        "relaxation_sensitivity_gate": gate_status(wave9, "relaxation_sensitivity_gate"),
        "operator_separation_gate": gate_status(wave9, "operator_separation_gate"),
        "max_spatial_xi_over_L": nested_get(
            wave9,
            ["gates", "critical_window_extension_gate", "max_spatial_xi_over_L"],
        ),
        "max_baseline_xi_over_L": nested_get(
            wave9,
            ["gates", "critical_window_extension_gate", "max_baseline_xi_over_L"],
        ),
        "relaxation_gain_near_T": nested_get(
            wave9,
            ["gates", "relaxation_sensitivity_gate", "relaxation_gain_near_T"],
        ),
    }

    blocked_paths = [
        name
        for name, gate in {
            "coefficient_only_path_gate": coefficient_only_path_gate,
            "finite_size_signal_gate": finite_size_signal_gate,
            "critical_window_path_gate": critical_window_path_gate,
        }.items()
        if gate["status"] != "PASS"
    ]

    next_operator_requirements = [
        "keep legacy_local as the default and expose any new candidate as opt-in core-engine operator_mode",
        "include a nonlocal, conserved, or scale-dependent mechanism rather than only local amplitude or coefficient changes",
        "produce connected-correlation growth with xi/L >= 0.20 in the diagnostic window before stronger finite-size claims",
        "separate the candidate lane from baseline TDGL by delta xi/L >= 0.05 before universality-shift claims",
        "keep information/game terms zero or reduced on C=0, I=0, uniform, and no-interface fields unless a derivation says otherwise",
        "update formula audit, parameter defaults, unit/proxy boundary, and unit tests before rerunning scaling claims",
    ]

    operator_form_requirement_gate = {
        "status": "BLOCKED" if blocked_paths else "PASS",
        "required_condition": "No spatial_coupled_v2 claim upgrade is allowed until the blocked repair paths are replaced by an operator that passes correlation and separation gates.",
        "blocked_paths": blocked_paths,
        "next_operator_requirements": next_operator_requirements,
        "claim_boundary": "This gate authorizes design work only; it does not validate a new physics operator.",
    }

    artifact_chain_summary = {
        "wave5": {
            "blocker_label": wave5.get("blocker_label"),
            "engine_alignment_gate": gate_status(wave5, "engine_alignment_gate"),
            "spatial_operator_gate": gate_status(wave5, "spatial_operator_gate"),
            "universality_shift_gate": gate_status(wave5, "universality_shift_gate"),
            "baseline_beta": nested_get(wave5, ["metrics", "beta_estimates", "baseline_tdgl", "beta"]),
            "legacy_beta": nested_get(wave5, ["metrics", "beta_estimates", "legacy_local_uet", "beta"]),
            "spatial_beta": nested_get(wave5, ["metrics", "beta_estimates", "spatial_coupled_v1", "beta"]),
        },
        "wave6": {
            "blocker_label": wave6.get("blocker_label"),
            "coefficient_sensitivity_gate": gate_status(wave6, "coefficient_sensitivity_gate"),
            "best_beta": nested_get(wave6, ["metrics", "best_case", "beta"]),
            "near_ising_case_count": nested_get(
                wave6,
                ["gates", "coefficient_sensitivity_gate", "near_ising_case_count"],
            ),
        },
        "wave7": {
            "blocker_label": wave7.get("blocker_label"),
            "critical_window_gate": gate_status(wave7, "critical_window_gate"),
            "estimator_adequacy_gate": gate_status(wave7, "estimator_adequacy_gate"),
            "operator_separation_gate": gate_status(wave7, "operator_separation_gate"),
            "spatial_nu_proxy": nested_get(
                wave7,
                ["gates", "critical_window_gate", "spatial_nu_proxy"],
            ),
            "spatial_xi_ratio_near_over_far": nested_get(
                wave7,
                ["gates", "critical_window_gate", "spatial_xi_ratio_near_over_far"],
            ),
        },
        "wave8": {
            "blocker_label": wave8.get("blocker_label"),
            "finite_size_coverage_gate": gate_status(wave8, "finite_size_coverage_gate"),
            "binder_crossing_gate": gate_status(wave8, "binder_crossing_gate"),
            "correlation_window_gate": gate_status(wave8, "correlation_window_gate"),
            "operator_separation_gate": gate_status(wave8, "operator_separation_gate"),
        },
        "wave9": {
            "blocker_label": wave9.get("blocker_label"),
            "critical_window_extension_gate": gate_status(wave9, "critical_window_extension_gate"),
            "relaxation_sensitivity_gate": gate_status(wave9, "relaxation_sensitivity_gate"),
            "operator_separation_gate": gate_status(wave9, "operator_separation_gate"),
        },
    }

    inputs = [
        artifact_input(CORE_ENGINE_PATH, "core engine operator implementation"),
        artifact_input(ALIGNMENT_AUDIT_PATH, "committed intake-to-code alignment audit"),
    ]
    for label, filename in PRIOR_ARTIFACTS.items():
        path = ARTIFACT_DIR / filename
        if path.exists():
            inputs.append(artifact_input(path, f"{label} prior machine-readable result"))

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 10 operator-form requirement gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Operator_Form_Requirement_Gate.py",
        "status": "WARN" if operator_form_requirement_gate["status"] == "BLOCKED" else "PASS",
        "blocker_label": "operator_form_revision_required",
        "claim_class": "design_requirement_gate",
        "inputs": inputs,
        "intake_evidence_policy": {
            "source": "docs/core/00_inbox is treated as intake evidence, not canonical proof.",
            "canonical_bridge": relpath(ALIGNMENT_AUDIT_PATH),
            "candidate_family_from_intake": "multiplicative information plus gradient/interface game coupling",
        },
        "metrics": {
            "artifact_chain_summary": artifact_chain_summary,
            "blocked_paths": blocked_paths,
            "next_operator_requirements": next_operator_requirements,
        },
        "gates": {
            "prior_artifact_chain_gate": prior_artifact_chain_gate,
            "core_engine_alignment_gate": core_engine_alignment_gate,
            "coefficient_only_path_gate": coefficient_only_path_gate,
            "finite_size_signal_gate": finite_size_signal_gate,
            "critical_window_path_gate": critical_window_path_gate,
            "operator_form_requirement_gate": operator_form_requirement_gate,
        },
        "limitations": [
            "This gate aggregates prior local artifacts and does not introduce a new physics operator.",
            "A blocked requirement gate does not prove that no better UET operator exists; it blocks claim upgrades from the current operator family.",
            "Any future spatial_coupled_v2 candidate still needs code-level unit tests, formula audit updates, and fresh scaling artifacts.",
        ],
        "claim_boundary": "Do not implement or describe a new spatial-coupled operator as validated physics until it passes correlation-growth, operator-separation, finite-size, and formula-audit gates.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_requirement_gate()
    print(
        json.dumps(
            {
                "status": result["status"],
                "artifact": str(ARTIFACT_PATH),
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "blocked_paths": result["metrics"]["blocked_paths"],
            },
            indent=2,
        )
    )
