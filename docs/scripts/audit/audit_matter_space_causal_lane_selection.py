"""Build the causal-lane decision artifact without promoting the default lane."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from docs.core.uet_master_equation import UETMasterEquation, UETParameters
from docs.core.uet_matter_space_finite_cone import FiniteConeCConfig


def load(name: str) -> dict:
    return json.loads((ROOT / "core" / "artifacts" / name).read_text(encoding="utf-8"))


def check_master_equation_adapter() -> dict:
    """Smoke-test the selected lane through the public master-equation API."""
    try:
        field = np.zeros(41, dtype=float)
        field[20] = 1.0
        engine = UETMasterEquation(
            UETParameters(operator_mode="matter_space_characteristic_cone_v1")
        )
        result = engine.step(
            C=field,
            dt=0.05,
            dx=0.05,
            operator_mode="matter_space_characteristic_cone_v1",
            characteristic_cone_config=FiniteConeCConfig(),
        )
        diagnostics = getattr(result, "diagnostics", {})
        return {
            "passed": (
                result.__class__.__name__ == "UETStepResult"
                and diagnostics.get("operator_mode")
                == "matter_space_characteristic_cone_v1"
                and isinstance(getattr(result, "energy_ledger", None), dict)
            ),
            "result_type": result.__class__.__name__,
            "operator_mode": diagnostics.get("operator_mode"),
            "has_energy_ledger": isinstance(getattr(result, "energy_ledger", None), dict),
            "has_diagnostics": isinstance(diagnostics, dict),
        }
    except Exception as exc:  # pragma: no cover - artifact should expose failures
        return {
            "passed": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def build_artifact() -> dict:
    characteristic = load("matter_space_characteristic_cone_verification.json")
    conserved = load("matter_space_causal_cone_compatibility.json")
    default = load("matter_space_variational_verification.json")
    adapter = check_master_equation_adapter()
    characteristic_pass = characteristic["audit_status"] == "PASS"
    checks = {
        "selected_characteristic_lane_passes": characteristic_pass,
        "selected_lane_compact_support": characteristic["gates"]["compact_support_no_prearrival_leakage"],
        "selected_lane_energy_ledger": characteristic["gates"]["ledger_relative_residual_le_1e-4"],
        "selected_lane_no_clipping_or_padding": (
            characteristic["gates"]["no_clipping"]
            and characteristic["gates"]["no_cone_padding"]
        ),
        "master_equation_adapter": adapter["passed"],
        "conserved_C_changing_response_remains_blocked": (
            conserved["response_cone_status"] == "BLOCKED"
            and conserved["structural_blocker"]
            == "conserved_C_gradient_term_has_unbounded_k4_characteristic_speed"
        ),
        "default_full_candidate_remains_blocked": (
            default["metrics"]["prearrival_leakage"]["gate"] == "FAIL"
        ),
    }
    return {
        "schema_version": "1.1",
        "artifact": "matter_space_causal_lane_selection",
        "audit_status": "PASS_WITH_DEFERRED_CONSERVED_BRANCH" if all(checks.values()) else "FAIL",
        "selected_lane": {
            "operator_mode": characteristic["operator_mode"],
            "status": "CANDIDATE_NORMALIZED_FINITE_CONE",
            "claim_status": "SIMULATION_ONLY",
            "artifact": "docs/core/07_artifacts/verification/matter_space_characteristic_cone_verification.json",
        },
        "conserved_C_lane": {
            "status": "BLOCKED_FOR_CHANGING_C_FINITE_CONE",
            "artifact": "docs/core/07_artifacts/archive/matter_space_causal_cone_compatibility.json",
            "allowed_role": "parabolic conserved phase comparator",
        },
        "default_full_candidate": {
            "status": "BLOCKED",
            "artifact": "docs/core/07_artifacts/verification/matter_space_variational_verification.json",
        },
        "adapter_contract": adapter,
        "checks": checks,
        "claim_boundary": (
            "The selected non-conserved characteristic lane has a verified "
            "normalized compact-support numerical contract and is reachable "
            "through the explicit master-equation adapter. This does not close "
            "the conserved-C causal claim, the default full operator, SI units, "
            "covariant physics, or downstream empirical claims."
        ),
        "next_controller": (
            "rerun full coupled verification and add an explicit observable "
            "mapping; keep the conserved-C changing-response branch and the "
            "default full candidate blocked"
        ),
    }


def main() -> int:
    artifact = build_artifact()
    output = ROOT / "core" / "artifacts" / "matter_space_causal_lane_selection.json"
    output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))
    return 0 if artifact["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())