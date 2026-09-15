"""Classify the failed matter-space causal gate at the discretization level.

This diagnostic does not weaken the causal gate and does not claim that the
continuous candidate is valid. It records the numerical domain-of-dependence
implied by the current two-stage Heun/RK2 update so a leakage failure is not
mistaken for a direct contradiction of the continuum equation.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CORE_PATH = ROOT / "docs/core/uet_matter_space.py"
VERIFICATION_PATH = ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json"
OUT = ROOT / "docs/core/07_artifacts/archive/matter_space_causal_discretization_diagnostic.json"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def build_report() -> dict[str, Any]:
    verification = load(VERIFICATION_PATH)
    source = CORE_PATH.read_text(encoding="utf-8", errors="replace")
    causal = verification["raw_diagnostics"]["causal_pulse"]
    dx = float(causal["dx"])
    dt = float(causal["dt"])
    declared_speed = float(causal["declared_speed"])
    stencil_radius = 2
    numerical_speed = stencil_radius * dx / dt
    leakage = float(causal["prearrival_leakage_fraction"])
    threshold = float(verification["thresholds"]["prearrival_leakage_fraction_max"])
    implementation_contract = {
        "integrator_is_heun_rk2": "Advance one Heun/RK2 step" in source,
        "predictor_stage_present": "predictor = MatterSpaceState" in source,
        "second_rhs_stage_present": "k2_C, k2_Phi, k2_Pi" in source,
        "nearest_neighbor_laplacian": "laplacian_1d" in source,
        "stencil_radius_assumption_cells_per_full_step": stencil_radius,
    }
    return {
        "schema_version": "1.0",
        "artifact": "matter_space_causal_discretization_diagnostic",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS",
        "causal_gate_status": verification["metrics"]["prearrival_leakage"]["gate"],
        "interpretation_status": "BLOCKED_NUMERICAL_SUPPORT",
        "continuum_formula_status": "NOT_TESTED_BY_THIS_GATE",
        "classification": "NUMERICAL_DOMAIN_OF_DEPENDENCE_EXCEEDS_DECLARED_CONE",
        "metrics": {
            "dx": dx,
            "dt": dt,
            "declared_physical_speed": declared_speed,
            "stencil_radius_cells_per_full_step": stencil_radius,
            "numerical_domain_speed_upper_bound": numerical_speed,
            "numerical_to_declared_speed_ratio": numerical_speed / declared_speed,
            "prearrival_leakage_fraction": leakage,
            "prearrival_threshold": threshold,
            "leakage_gate_failed": leakage > threshold,
        },
        "implementation_contract": implementation_contract,
        "inference_boundary": "The support-speed estimate is an implementation-level diagnostic, not a proof that every Heun/RK2 trajectory reaches the bound. It explains why the current leakage result cannot by itself distinguish a continuum-law contradiction from a numerical-cone failure.",
        "required_repair": "Use a causality-preserving characteristic/staggered scheme or a separately proven discrete cone, then rerun the original prearrival gate without cone padding or clipping.",
        "evidence_inputs": {
            "core_source": rel(CORE_PATH),
            "verification_artifact": rel(VERIFICATION_PATH),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        report = build_report()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={report['audit_status']}")
        print(f"causal_gate_status={report['causal_gate_status']}")
        print(f"interpretation_status={report['interpretation_status']}")
        print(f"numerical_domain_speed_upper_bound={report['metrics']['numerical_domain_speed_upper_bound']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
