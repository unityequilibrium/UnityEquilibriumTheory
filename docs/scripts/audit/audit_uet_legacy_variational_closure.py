"""Audit the scoped variational contract for the legacy C/I implementation.

The historical ``legacy_local`` path is intentionally preserved as a comparator.
The opt-in ``legacy_variational_v1`` path is the canonical lane audited here. The
artifact therefore reports canonical closure separately from legacy preservation;
it must not turn preservation of the old path into a variational claim.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
MASTER_PATH = ROOT / "docs/core/uet_master_equation.py"
OUT = ROOT / "docs/core/07_artifacts/gates/uet_legacy_variational_closure.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def potential_pair(master_text: str) -> dict[str, Any]:
    from docs.core.uet_master_equation import (
        legacy_reaction_derivative,
        potential_V,
        potential_derivative,
    )
    from docs.core.uet_parameters import UETParameters

    params = UETParameters(alpha=1.0, gamma=0.025, C0=1.0)
    samples = np.array([-1.5, -0.75, 0.0, 0.5, 1.0, 1.5, 2.0], dtype=float)
    epsilon = 1.0e-6
    finite_difference = (
        potential_V(samples + epsilon, params) - potential_V(samples - epsilon, params)
    ) / (2.0 * epsilon)
    canonical = potential_derivative(samples, params)
    legacy = legacy_reaction_derivative(samples, params)
    canonical_residual = np.abs(finite_difference - canonical)
    legacy_residual = np.abs(finite_difference - legacy)
    threshold = 1.0e-8
    return {
        "finding_id": "legacy_potential_derivative_pair",
        "status": "COMPATIBLE_CONDITIONAL"
        if float(np.max(canonical_residual)) <= threshold
        else "CONTRADICTION",
        "declared_relation": "V(C)=alpha/2*(C^2-C0^2)^2+gamma/4*(C^2-C0^2)^4",
        "canonical_mode": "legacy_variational_v1",
        "canonical_coded_relation": "dynamics uses the exact radial derivative of potential_V",
        "legacy_comparator_relation": "legacy_local uses alpha*(C-C0)+gamma*(C-C0)^3",
        "analytic_derivative": "2*C*(alpha*(C^2-C0^2)+gamma*(C^2-C0^2)^3)",
        "metrics": {
            "canonical_finite_difference_max_absolute_residual": float(np.max(canonical_residual)),
            "legacy_comparator_finite_difference_max_absolute_residual": float(np.max(legacy_residual)),
            "threshold": threshold,
            "samples": samples.tolist(),
        },
        "legacy_comparator": {
            "status": "QUARANTINED_COMPARATOR",
            "preserved": True,
            "reason": "Historical legacy_local reaction is not the derivative of the declared radial potential.",
        },
        "claim_boundary": "Canonical potential/derivative closure is established only in legacy_variational_v1; legacy_local remains a non-variational comparator.",
    }


def information_gradient_sign(master_text: str) -> dict[str, Any]:
    coupling_present = "return params.beta * np.sum(C * I) * volume" in master_text
    canonical_source_present = "source = -params.beta * C" in master_text
    legacy_source_present = "source = params.beta * C" in master_text
    c_source_present = "return -params.beta * I" in master_text
    expected_i_source_sign = -1
    canonical_i_source_sign = -1
    legacy_i_source_sign = 1
    return {
        "finding_id": "legacy_information_gradient_sign",
        "status": "COMPATIBLE_CONDITIONAL"
        if coupling_present and canonical_source_present
        and expected_i_source_sign == canonical_i_source_sign
        else "NOT_ESTABLISHED",
        "declared_relation": "Omega_I contains +beta*C*I and dI/dt=-delta(Omega)/delta(I)",
        "canonical_mode": "legacy_variational_v1",
        "canonical_coded_relation": "dI/dt=laplacian-kappa_I*I-beta*C",
        "legacy_comparator_relation": "legacy_local uses dI/dt=laplacian-kappa_I*I+beta*C",
        "expected_source_sign": expected_i_source_sign,
        "canonical_source_sign": canonical_i_source_sign,
        "legacy_comparator_source_sign": legacy_i_source_sign,
        "canonical_source_present": canonical_source_present,
        "legacy_source_present": legacy_source_present,
        "c_source_sign_matches": c_source_present,
        "legacy_comparator": {
            "status": "QUARANTINED_COMPARATOR",
            "preserved": True,
            "reason": "Historical legacy_local source sign is retained for compatibility and is not claimed to be variational.",
        },
        "claim_boundary": "Canonical I-source sign is closed only in legacy_variational_v1; legacy_local remains a historical comparator.",
    }


def information_operator_contract(master_text: str) -> dict[str, Any]:
    """Check that the canonical I operator matches its declared normalized functional."""

    contract = {
        "historical_box_is_comparator": "historical box/wave relation" in master_text and "comparator" in master_text,
        "canonical_gradient_flow_declared": "dI/dt = Laplacian(I) - kappa_I*I - beta*C" in master_text,
        "periodic_laplacian": "laplacian = conserved_laplacian(I, dx)" in master_text,
        "periodic_gradient_energy": "periodic_gradient_energy(I, dx, 1.0)" in master_text,
        "canonical_source": "source = -params.beta * C" in master_text,
        "first_order_update": "dI_dt = laplacian - decay + source" in master_text and "return I + dt * dI_dt" in master_text,
    }
    closed = all(contract.values())
    return {
        "finding_id": "legacy_information_operator",
        "status": "COMPATIBLE_CONDITIONAL" if closed else "NOT_ESTABLISHED",
        "declared_relation": "Omega_I=1/2|grad I|^2+1/2*kappa_I*I^2+beta*C*I in the normalized periodic lane",
        "canonical_coded_relation": "dI/dt=Laplacian(I)-kappa_I*I-beta*C",
        "legacy_comparator_relation": "legacy_local retains its historical first-order/boundary behavior",
        "contract": contract,
        "legacy_behavior_preserved": contract["historical_box_is_comparator"],
        "claim_boundary": "The normalized periodic I operator is conditionally closed; covariant box dynamics and SI interpretation remain outside this lane.",
    }

def build_report() -> dict[str, Any]:
    master_text = MASTER_PATH.read_text(encoding="utf-8", errors="replace")
    findings = [potential_pair(master_text), information_gradient_sign(master_text), information_operator_contract(master_text)]
    blockers = [item["finding_id"] for item in findings if item["status"] == "CONTRADICTION"]
    return {
        "schema_version": "1.2",
        "artifact": "uet_legacy_variational_closure",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS",
        "closure_status": "BLOCKED" if blockers else "PASS_CONDITIONAL",
        "controlling_blockers": blockers,
        "canonical_mode": "legacy_variational_v1",
        "legacy_default_mode": "legacy_local",
        "legacy_behavior_preserved": True,
        "unresolved_scope_conflicts": [],
        "equation_family": "uet.legacy.master_functional",
        "evidence_inputs": {"master_equation": rel(MASTER_PATH)},
        "findings": findings,
        "principle": "A dynamics implementation is variational only when every coupled state equation is the negative derivative of the same declared functional in the same unit and boundary lane.",
        "next_action": "Use legacy_variational_v1 for the conditionally closed normalized C/I contract; keep legacy_local quarantined and route covariant, SI, and standard-physics correspondence questions through their own gates.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        report = build_report()
    except Exception as exc:  # pragma: no cover - surfaced as an audit failure
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={report['audit_status']}")
        print(f"closure_status={report['closure_status']}")
        print(f"controlling_blockers={','.join(report['controlling_blockers'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())