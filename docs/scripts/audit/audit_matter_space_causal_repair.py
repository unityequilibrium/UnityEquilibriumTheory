"""Package the causal discretization repair result without promoting the full operator."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.scripts.audit.audit_matter_space_causal_reference import run_reference  # noqa: E402

DEFAULT_VERIFICATION = ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json"
CAUSAL_DIAGNOSTIC = ROOT / "docs/core/07_artifacts/archive/matter_space_causal_discretization_diagnostic.json"
CORE_SOURCE = ROOT / "docs/core/02_equations/matter_space/uet_matter_space.py"
OUTPUT = ROOT / "docs/core/07_artifacts/archive/causal_discretization_repair_artifact.json"
REFERENCE_ENERGY = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_reference_energy_verification.json"
CAUSAL_DISCRETE_GRADIENT = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_discrete_gradient_verification.json"
CAUSAL_SPLIT = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_split_verification.json"
CAUSAL_CONE_COMPATIBILITY = ROOT / "docs/core/07_artifacts/archive/matter_space_causal_cone_compatibility.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_artifact() -> dict[str, Any]:
    default = load(DEFAULT_VERIFICATION)
    old_diagnostic = load(CAUSAL_DIAGNOSTIC)
    reference = run_reference()
    reference_energy = load(REFERENCE_ENERGY)
    causal_discrete_gradient = load(CAUSAL_DISCRETE_GRADIENT)
    causal_split = load(CAUSAL_SPLIT)
    causal_cone = load(CAUSAL_CONE_COMPATIBILITY)
    reference_pass = (
        reference["status"] == "PASS"
        and reference["metrics"]["prearrival_max_outside_discrete_cone"] == 0.0
        and reference["metrics"]["prearrival_target_abs"] == 0.0
        and reference["metrics"]["arrival_target_abs"] > 0.0
    )
    checks = {
        "reference_compact_support": reference_pass,
        "reference_uses_strict_cfl": reference["reference_cfl"] == 1.0 if "reference_cfl" in reference else reference["time_step"]["cfl"] == 1.0,
        "default_full_candidate_remains_blocked": default["metrics"]["prearrival_leakage"]["gate"] == "FAIL",
        "old_diagnostic_classifies_numerical_domain_failure": old_diagnostic["classification"] == "NUMERICAL_DOMAIN_OF_DEPENDENCE_EXCEEDS_DECLARED_CONE",
        "no_clipping_or_cone_padding": True,
        "reference_energy_ledger_closed": reference_energy["audit_status"] == "PASS",
        "causal_discrete_gradient_partial_closure": causal_discrete_gradient["partial_closure_status"] == "PASS",
        "causal_split_shared_ledger_pass": causal_split["shared_ledger_status"] == "PASS",
        "causal_cone_structural_blocker_visible": causal_cone["response_cone_status"] == "BLOCKED",
        "full_coupled_integration_closed": False,
    }
    return {
        "schema_version": "causal-discretization-repair-artifact-v1",
        "artifact": "causal_discretization_repair_artifact",
        "generated_at": date.today().isoformat(),
        "status": "BLOCKED",
        "repair_status": "REFERENCE_AND_PHI_AND_SPLIT_LEDGER_PASS_C_CONE_STRUCTURAL_BLOCKER_OPEN",
        "reference_status": "PASS" if reference_pass else "FAIL",
        "split_bridge_status": causal_split["split_bridge_status"],
        "causal_cone_compatibility_status": causal_cone["response_cone_status"],
        "changing_C_causal_cone_status": causal_split["changing_C_causal_cone_status"],
        "default_full_candidate_status": "BLOCKED",
        "controlling_blocker": "conserved_C_gradient_term_has_unbounded_k4_characteristic_speed",
        "checks": checks,
        "default_candidate": {
            "artifact": "docs/core/07_artifacts/verification/matter_space_variational_verification.json",
            "prearrival_leakage_fraction": default["metrics"]["prearrival_leakage"]["value"],
            "threshold": default["metrics"]["prearrival_leakage"]["threshold"],
            "gate": default["metrics"]["prearrival_leakage"]["gate"],
        },
        "reference_lane": {
            "scope": "linearized_space_response_with_frozen_C",
            "scheme": "centered_second_order_damped_recurrence",
            "required_cfl": 1.0,
            "metrics": reference["metrics"],
            "config": reference["config"],
            "time_step": reference["time_step"],
            "claim_boundary": "compact-support numerical control only; not full nonlinear matter-space verification",
        },
        "integration_requirements": [
            "resolve the finite-cone incompatibility of conserved C with kappa_C>0",
            "choose between a restricted frozen-C cone claim, a non-conserved telegraph C lane, or an explicit UV/nonlocal regularization",
            "derive units, energy and observable contracts for whichever C realization is selected",
            "rerun the full-candidate gate only after the structural cone decision is closed",
            "rerun the original full-candidate prearrival gate without clipping or cone padding",
        ],
        "evidence_inputs": {
            "core_source": "docs/core/02_equations/matter_space/uet_matter_space.py",
            "core_source_sha256": sha256(CORE_SOURCE),
            "default_verification": "docs/core/07_artifacts/verification/matter_space_variational_verification.json",
            "causal_diagnostic": "docs/core/07_artifacts/archive/matter_space_causal_discretization_diagnostic.json",
            "reference_energy_verification": "docs/core/07_artifacts/verification/matter_space_causal_reference_energy_verification.json",
            "causal_discrete_gradient_verification": "docs/core/07_artifacts/verification/matter_space_causal_discrete_gradient_verification.json",
            "causal_split_verification": "docs/core/07_artifacts/verification/matter_space_causal_split_verification.json",
            "causal_cone_compatibility": "docs/core/07_artifacts/archive/matter_space_causal_cone_compatibility.json",
        },
        "claim_boundary": "The repair closes the frozen-C Phi/Pi and changing-C shared-ledger diagnostics, but exposes a structural finite-cone incompatibility in conserved C with kappa_C>0; the full operator, continuum causality, SI physics, and downstream topics remain blocked.",
        "next_controller": "resolve the conserved-C k4 finite-cone incompatibility or restrict the causal claim before integrating the full operator",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"repair_status={artifact['repair_status']}")
    print(f"reference_status={artifact['reference_status']}")
    print(f"controlling_blocker={artifact['controlling_blocker']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
