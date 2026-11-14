"""
Wave 15 conserved-order numerics-gap diagnostic.

Wave 13 showed the spectral Cahn-Hilliard topic engine is a promising Model C
mechanism direction. Wave 14 exposed a core opt-in conserved_order_v1 mode, but
its explicit finite-difference path conserved mass while failing the mechanism
response gate.

This diagnostic checks whether the gap is likely numerical/operator-form
related rather than simply a coefficient or mobility issue. It compares the
stiffness implied by the spectral Cahn-Hilliard settings against the explicit
core candidate and writes a machine-readable next-requirement gate.
"""

from __future__ import annotations

import json
import math
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np


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
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_numerics_gap.json"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
ENGINE_PHASE_PATH = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Phase.py"
WAVE13_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_model_c_conserved_order_diagnostic.json"
WAVE14_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_core_candidate.json"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def gate_status(artifact: dict[str, Any], gate_name: str) -> str:
    return artifact.get("gates", {}).get(gate_name, {}).get("status", "MISSING")


def explicit_biharmonic_stiffness(dt: float, kappa: float, dx: float) -> float:
    """Dimensionless explicit stiffness proxy for the kappa * nabla^4 term."""
    if dx <= 0:
        return float("inf")
    k_max = math.pi / dx
    return float(dt * kappa * k_max**4)


def run_numerics_gap_diagnostic() -> dict[str, Any]:
    wave13 = load_json(WAVE13_ARTIFACT_PATH) if WAVE13_ARTIFACT_PATH.exists() else {}
    wave14 = load_json(WAVE14_ARTIFACT_PATH) if WAVE14_ARTIFACT_PATH.exists() else {}

    wave13_params = wave13.get("parameters", {})
    wave14_params = wave14.get("parameters", {})
    wave14_candidate = wave14_params.get("candidate_params", {})

    wave13_dx = float(wave13_params.get("dx", float("nan")))
    wave13_dt = float(wave13_params.get("dt", float("nan")))
    wave13_kappa = float(wave13_params.get("kappa", float("nan")))
    wave14_dx = float(wave14_params.get("dx", float("nan")))
    wave14_dt = float(wave14_params.get("dt", float("nan")))
    wave14_kappa = float(wave14_candidate.get("kappa", float("nan")))

    wave13_stiffness = explicit_biharmonic_stiffness(wave13_dt, wave13_kappa, wave13_dx)
    wave14_stiffness = explicit_biharmonic_stiffness(wave14_dt, wave14_kappa, wave14_dx)
    stiffness_ratio = float(wave13_stiffness / wave14_stiffness) if wave14_stiffness > 0 else float("inf")

    wave13_model_c = wave13.get("metrics", {}).get("by_lane", {}).get("model_c_cahn_hilliard", {})
    wave14_core = wave14.get("metrics", {}).get("by_lane", {}).get("core_conserved_order_v1", {})
    wave14_legacy = wave14.get("metrics", {}).get("by_lane", {}).get("legacy_nonconserved_core", {})

    artifact_chain_gate = {
        "status": "PASS" if wave13 and wave14 else "BLOCKED",
        "required_condition": "Wave 13 and Wave 14 artifacts must be present and parseable.",
        "wave13_present": bool(wave13),
        "wave14_present": bool(wave14),
    }
    mechanism_gap_gate = {
        "status": (
            "PASS"
            if gate_status(wave13, "domain_growth_gate") == "PASS"
            and gate_status(wave14, "core_mechanism_response_gate") == "BLOCKED"
            else "BLOCKED"
        ),
        "required_condition": "Wave 13 mechanism must pass while the Wave 14 explicit core mechanism gate remains blocked.",
        "wave13_domain_growth_gate": gate_status(wave13, "domain_growth_gate"),
        "wave13_operator_distinction_gate": gate_status(wave13, "operator_distinction_gate"),
        "wave14_core_mechanism_response_gate": gate_status(wave14, "core_mechanism_response_gate"),
        "wave13_model_c_median_xi_growth_ratio": wave13_model_c.get("median_xi_growth_ratio"),
        "wave14_core_median_xi_growth_ratio": wave14_core.get("median_xi_growth_ratio"),
        "wave14_legacy_median_xi_growth_ratio": wave14_legacy.get("median_xi_growth_ratio"),
    }
    explicit_core_viability_gate = {
        "status": "PASS" if wave13_stiffness <= 1.0 else "BLOCKED",
        "required_condition": "The explicit core conserved-order path should have dt*kappa*(pi/dx)^4 <= 1 under Wave 13-like settings before it is treated as a viable direct replacement.",
        "wave13_explicit_stiffness_proxy": wave13_stiffness,
        "wave14_explicit_stiffness_proxy": wave14_stiffness,
        "wave13_to_wave14_stiffness_ratio": stiffness_ratio,
        "wave13_settings": {
            "dx": wave13_dx,
            "dt": wave13_dt,
            "kappa": wave13_kappa,
        },
        "wave14_settings": {
            "dx": wave14_dx,
            "dt": wave14_dt,
            "kappa": wave14_kappa,
        },
    }
    spectral_core_requirement_gate = {
        "status": "BLOCKED" if explicit_core_viability_gate["status"] == "BLOCKED" else "WARN",
        "required_condition": "If explicit stiffness is blocked, the next core candidate should use a spectral or semi-implicit conserved-order update rather than coefficient-only tuning.",
        "next_required_candidate": "spectral_or_semi_implicit_conserved_order_core",
        "blocked_repair_paths": [
            "mobility_only_tuning",
            "recombining_spatial_coupled_v2_components",
            "treating explicit finite-difference conserved_order_v1 as mechanism-complete",
        ],
    }

    inputs = []
    for path, role in [
        (CORE_ENGINE_PATH, "core explicit conserved-order candidate"),
        (ENGINE_PHASE_PATH, "topic spectral Cahn-Hilliard reference engine"),
        (WAVE13_ARTIFACT_PATH, "Wave 13 spectral Model C mechanism result"),
        (WAVE14_ARTIFACT_PATH, "Wave 14 core conserved-order result"),
    ]:
        if path.exists():
            inputs.append({"path": relpath(path), "sha256": hash_file(path), "role": role})

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 15 conserved-order numerics-gap diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Numerics_Gap.py",
        "status": "WARN",
        "blocker_label": "explicit_core_ch_scheme_stiffness_blocks_model_c_response",
        "claim_class": "diagnostic_numerics_gap_only",
        "inputs": inputs,
        "metrics": {
            "wave13_explicit_stiffness_proxy": wave13_stiffness,
            "wave14_explicit_stiffness_proxy": wave14_stiffness,
            "wave13_to_wave14_stiffness_ratio": stiffness_ratio,
            "wave13_model_c_median_xi_growth_ratio": wave13_model_c.get("median_xi_growth_ratio"),
            "wave14_core_median_xi_growth_ratio": wave14_core.get("median_xi_growth_ratio"),
            "wave14_legacy_median_xi_growth_ratio": wave14_legacy.get("median_xi_growth_ratio"),
        },
        "gates": {
            "artifact_chain_gate": artifact_chain_gate,
            "mechanism_gap_gate": mechanism_gap_gate,
            "explicit_core_viability_gate": explicit_core_viability_gate,
            "spectral_core_requirement_gate": spectral_core_requirement_gate,
        },
        "limitations": [
            "This diagnostic uses a stiffness proxy and prior artifacts; it does not implement the spectral core candidate.",
            "A blocked explicit-viability gate does not prove a spectral core candidate will pass scaling gates.",
            "The result should guide operator implementation, not promote a physics claim.",
        ],
        "claim_boundary": "Use this artifact only to justify the next core implementation requirement: a spectral or semi-implicit conserved-order candidate.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy_version": np.__version__,
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_numerics_gap_diagnostic()
    print(
        json.dumps(
            {
                "status": result["status"],
                "artifact": str(ARTIFACT_PATH),
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "blocker_label": result["blocker_label"],
            },
            indent=2,
        )
    )
