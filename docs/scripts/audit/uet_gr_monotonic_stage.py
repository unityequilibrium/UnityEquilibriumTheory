"""Preserve the newest verified GR-program stage during upstream reruns.

The GR research chain is intentionally rerunnable from its earliest audit.
Earlier generators must therefore recognize later stable artifacts instead of
silently moving the shared program gate backwards.  This helper applies the
sourced comparator stage and, when present, the later fixed-cone feasibility
stage, Noether/phase-field hydrodynamic state-coordinate stage, and the O(2)
finite-density EOS/T=0 superfluid stage together with their audit metadata.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docs.core.core_paths import canonical_artifact_path

COMPARATOR_ARTIFACT = (
    "hyperbolic_phase_field_external_comparator_verification.json"
)
COMPARATOR_EVIDENCE = "PARTIAL_EXTERNAL_COMPARATOR"
LATEST_STAGE = "EXTERNAL_HYPERBOLIC_PHASE_FIELD_COMPARATOR_FORMULA_VERIFIED"
OLD_CONTROLLER = "first_order_hyperbolic_phase_field_uv_closure_missing"
LATEST_CONTROLLER = (
    "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing"
)
FEASIBILITY_ARTIFACT = "hyperbolic_phase_field_causal_feasibility.json"
FEASIBILITY_EVIDENCE = "PARTIAL_ANALYTIC_CAUSAL_BRIDGE"
FEASIBILITY_STAGE = (
    "FIXED_LIGHT_CONE_FEASIBILITY_AND_LOCAL_CURRENT_MAP_VERIFIED"
)
FEASIBILITY_CONTROLLER = "noether_density_to_phase_field_order_parameter_map_missing"
MAPPING_GATE_ARTIFACT = "hyperbolic_phase_field_covariant_mapping_gate.json"
STATE_MAP_ARTIFACT = "noether_phase_field_state_map_verification.json"
STATE_MAP_EVIDENCE = "PARTIAL_HYDRODYNAMIC_STATE_COORDINATE_MAP"
STATE_MAP_STAGE = "NOETHER_PHASE_FIELD_STATE_COORDINATE_MAP_VERIFIED"
STATE_MAP_CONTROLLER = (
    "noether_charge_equation_of_state_and_covariant_transport_matching_missing"
)
STATE_MAP_GATE_ARTIFACT = "noether_phase_field_dependency_gate.json"
O2_EOS_ARTIFACT = "o2_finite_density_eos_verification.json"
O2_TRANSPORT_ARTIFACT = "covariant_superfluid_transport_verification.json"
O2_TRANSPORT_CONTRACT_ARTIFACT = "covariant_superfluid_transport_contract.json"
O2_PROGRAM_ARTIFACT = "uet_gr_research_program_gate.json"
O2_PROGRAM_VERSION = "wave10_v1"
O2_PROGRAM_CONTROLLER = "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing"
PROGRAM_TOPIC = "docs/core UET GR non-closed response"


_ARTIFACT_DOMAINS = {
    COMPARATOR_ARTIFACT: "verification",
    FEASIBILITY_ARTIFACT: "verification",
    MAPPING_GATE_ARTIFACT: "gates",
    STATE_MAP_ARTIFACT: "verification",
    STATE_MAP_GATE_ARTIFACT: "gates",
    O2_EOS_ARTIFACT: "verification",
    O2_TRANSPORT_ARTIFACT: "verification",
    O2_TRANSPORT_CONTRACT_ARTIFACT: "archive",
    O2_PROGRAM_ARTIFACT: "gates",
}


def _artifact_path(out: Path, name: str) -> Path:
    """Resolve a stage artifact through canonical authority with legacy fallback."""

    canonical = canonical_artifact_path(name, _ARTIFACT_DOMAINS.get(name))
    if canonical.exists():
        return canonical
    historical_canonical = canonical_artifact_path(name)
    if historical_canonical.exists():
        return historical_canonical
    legacy = out / name
    if legacy.exists():
        return legacy
    legacy_boundary = canonical.parents[2] / "artifacts" / name
    if legacy_boundary.exists():
        return legacy_boundary
    return canonical


def _artifact_ref(name: str) -> str:
    path = canonical_artifact_path(name, _ARTIFACT_DOMAINS.get(name))
    return "docs/core/" + path.relative_to(path.parents[2]).as_posix()



def _load_comparator(out: Path) -> dict[str, Any] | None:
    path = _artifact_path(out, COMPARATOR_ARTIFACT)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("audit_status") != "PASS":
        return None
    if payload.get("evidence_status") != COMPARATOR_EVIDENCE:
        return None
    return payload


def _load_feasibility(out: Path) -> dict[str, Any] | None:
    path = _artifact_path(out, FEASIBILITY_ARTIFACT)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("audit_status") != "PASS":
        return None
    if payload.get("evidence_status") != FEASIBILITY_EVIDENCE:
        return None
    return payload


def _load_state_map(out: Path) -> dict[str, Any] | None:
    path = _artifact_path(out, STATE_MAP_ARTIFACT)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("audit_status") != "PASS":
        return None
    if payload.get("evidence_status") != STATE_MAP_EVIDENCE:
        return None
    return payload


def _load_o2_superfluid_program(out: Path) -> dict[str, Any] | None:
    """Load Wave 10 only when every interface-producing artifact is stable."""

    names = (
        O2_EOS_ARTIFACT,
        O2_TRANSPORT_ARTIFACT,
        O2_TRANSPORT_CONTRACT_ARTIFACT,
        O2_PROGRAM_ARTIFACT,
    )
    payloads: list[dict[str, Any]] = []
    for name in names:
        path = _artifact_path(out, name)
        if not path.exists():
            return None
        try:
            payloads.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            return None
    eos, transport, contract, program = payloads
    if eos.get("audit_status") != "PASS":
        return None
    if transport.get("audit_status") != "PASS":
        return None
    if contract.get("interface_status") != "PASS":
        return None
    if program.get("version") != O2_PROGRAM_VERSION:
        return None
    if program.get("controlling_blocker") != O2_PROGRAM_CONTROLLER:
        return None
    return program




def _rewrite_controller(value: Any) -> Any:
    if isinstance(value, str):
        return LATEST_CONTROLLER if value == OLD_CONTROLLER else value
    if isinstance(value, list):
        return [_rewrite_controller(item) for item in value]
    if isinstance(value, dict):
        return {key: _rewrite_controller(item) for key, item in value.items()}
    return value


def _update_payload(payload: dict[str, Any], comparator: dict[str, Any]) -> None:
    rewritten = _rewrite_controller(payload)
    payload.clear()
    payload.update(rewritten)
    payload["downstream_hyperbolic_phase_field"] = {
        "artifact": COMPARATOR_ARTIFACT,
        "audit_status": comparator["audit_status"],
        "evidence_status": comparator["evidence_status"],
        "role": "external_fixed_parameter_formula_comparator",
        "uet_derivation": "BLOCKED",
        "uniform_subluminal_limit": "BLOCKED",
    }
    completed = payload.get("completed_formula_gates")
    if isinstance(completed, list):
        marker = "external_hyperbolic_phase_field_comparator_formula"
        if marker not in completed:
            completed.append(marker)
    blocked = payload.get("blocked_gates")
    if isinstance(blocked, dict) and "first_order_hyperbolic_gradient_phase_field" in blocked:
        blocked["uet_native_first_order_hyperbolic_gradient_phase_field"] = blocked.pop(
            "first_order_hyperbolic_gradient_phase_field"
        )
        blocked["uniform_subluminal_cahn_hilliard_limit"] = "BLOCKED"



def _rewrite_feasibility_controller(value: Any) -> Any:
    if isinstance(value, str):
        if value in {OLD_CONTROLLER, LATEST_CONTROLLER}:
            return FEASIBILITY_CONTROLLER
        return value
    if isinstance(value, list):
        return [_rewrite_feasibility_controller(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _rewrite_feasibility_controller(item)
            for key, item in value.items()
        }
    return value


def _update_feasibility_payload(
    payload: dict[str, Any],
    comparator: dict[str, Any],
    feasibility: dict[str, Any],
) -> None:
    rewritten = _rewrite_feasibility_controller(payload)
    payload.clear()
    payload.update(rewritten)
    payload["downstream_hyperbolic_phase_field"] = {
        "artifact": COMPARATOR_ARTIFACT,
        "audit_status": comparator["audit_status"],
        "evidence_status": comparator["evidence_status"],
        "role": "external_fixed_parameter_formula_comparator",
        "causal_feasibility_artifact": FEASIBILITY_ARTIFACT,
        "causal_feasibility_status": feasibility["audit_status"],
        "fixed_light_cone_parameter_domain": "PASS_NORMALIZED_ANALYTIC",
        "uniform_subluminal_limit": "NO_GO_EXACT_PARABOLIC_LIMIT",
        "uet_derivation": "BLOCKED",
    }
    completed = payload.get("completed_formula_gates")
    if isinstance(completed, list):
        for marker in (
            "fixed_light_cone_parameter_inequalities",
            "external_q_to_local_current_law_map",
        ):
            if marker not in completed:
                completed.append(marker)


def _rewrite_state_map_controller(value: Any) -> Any:
    if isinstance(value, str):
        if value in {OLD_CONTROLLER, LATEST_CONTROLLER, FEASIBILITY_CONTROLLER}:
            return STATE_MAP_CONTROLLER
        return value
    if isinstance(value, list):
        return [_rewrite_state_map_controller(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _rewrite_state_map_controller(item)
            for key, item in value.items()
        }
    return value


def _update_state_map_payload(
    payload: dict[str, Any],
    state_map: dict[str, Any],
) -> None:
    rewritten = _rewrite_state_map_controller(payload)
    payload.clear()
    payload.update(rewritten)
    payload["downstream_noether_phase_field_state_map"] = {
        "artifact": STATE_MAP_ARTIFACT,
        "audit_status": state_map["audit_status"],
        "evidence_status": state_map["evidence_status"],
        "role": "hydrodynamic_state_coordinate_map_not_microscopic_derivation",
        "affine_fixed_scale_layer": "PASS",
        "microscopic_reconstruction": "NO_GO_MANY_TO_ONE",
        "equation_of_state_and_transport": "BLOCKED",
    }
    completed = payload.get("completed_formula_gates")
    if isinstance(completed, list):
        for marker in (
            "noether_charge_to_phase_coordinate_affine_map",
            "microscopic_and_coarse_graining_noninvertibility",
        ):
            if marker not in completed:
                completed.append(marker)
    if payload.get("artifact") != "hyperbolic_phase_field_covariant_mapping_gate":
        return
    completed_layers = payload.setdefault("completed_layers", {})
    completed_layers["noether_charge_variable_declaration"] = (
        "PASS_SIGNED_O2_CHARGE"
    )
    completed_layers["coarse_density_to_phase_coordinate"] = (
        "PASS_AFFINE_FIXED_SCALE"
    )
    lane = payload.setdefault("classical_covariant_lane", {})
    lane["noether_density_to_phase_field_order_parameter"] = (
        "PASS_HYDRODYNAMIC_AFFINE_ONLY"
    )
    lane["equation_of_state_from_covariant_O2_action"] = "BLOCKED_CONTROLLING"
    lane["covariant_coarse_graining_kernel"] = "BLOCKED"
    lane["susceptibility_and_transport_matching"] = "BLOCKED"
    payload["required_next_evidence"] = [
        "derive or independently calibrate the signed-charge equation of state",
        "map equilibrium susceptibility and transport coefficients to the covariant matter theory",
        "specify a covariant coarse-graining or hydrodynamic matching prescription",
        "then construct entropy-current and dissipative-Bianchi closure",
    ]


def _replace_program_with_state_map_stage(
    payload: dict[str, Any],
) -> None:
    generated_at = payload.get("generated_at")
    payload.clear()
    payload.update(
        {
            "schema_version": "1.0",
            "artifact": "uet_gr_research_program_gate",
            "generated_at": generated_at,
            "topic": PROGRAM_TOPIC,
            "version": "wave9_v1",
            "benchmark_role": "program_gate",
            "method_label": "monotonic_gr_research_stage_gate",
                "input_identity": {
                "state_map_artifact": (
                    _artifact_ref(STATE_MAP_ARTIFACT)
                ),
                "state_map_dependency_gate": (
                    _artifact_ref(STATE_MAP_GATE_ARTIFACT)
                ),
            },
            "notes": [
                "The hydrodynamic coordinate map is verified while microscopic reconstruction is disproved by counterexample.",
                "The controlling blocker is now equation-of-state and covariant transport matching.",
            ],
            "status": "BLOCKED",
            "program_stage": STATE_MAP_STAGE,
            "current_claim_class": "B",
            "gr_null_model": {
                "parameter": "epsilon_nc",
                "value": 0,
                "verification_status": "PASS",
            },
            "sector_status": {
                "ontology_and_claim_contract": "PASS",
                "legacy_claim_quarantine": "PASS",
                "conservative_tensor_formula": "PASS",
                "exact_gr_closed_limit": "PASS",
                "covariant_exchange_bianchi_balance": "PASS_CONSERVATIVE_PARENT_ONLY",
                "causal_nonclosed_sector": "PASS_CONSTITUTIVE_1P1D",
                "weak_field_reduction": "PARTIAL_RESPONSE_ONLY",
                "covariant_matter_action": "PASS_O2_SCALAR_PILOT",
                "reciprocal_coupling": "PASS_ACTION_LEVEL",
                "signed_O2_noether_current": "PASS_ON_SHELL",
                "diffusive_matter_reduction": "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT",
                "local_convex_matter_causality": "PASS_CONTROL",
                "gradient_phase_field_causality": "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY",
                "fixed_light_cone_parameter_domain": "PASS_NORMALIZED_ANALYTIC",
                "uniform_subluminal_phase_field_limit": "NO_GO_FOR_EXACT_PARABOLIC_LIMIT",
                "local_current_law_mapping": "PASS_ALGEBRAIC_MOBILITY_ONE",
                "hydrodynamic_state_coordinate_map": "PASS_AFFINE_FIXED_SCALE",
                "microscopic_state_reconstruction": "NO_GO_MANY_TO_ONE",
                "external_C_noether_coordinate_map": "PASS_DECLARED_SIGNED_CHARGE_ONLY",
                "equation_of_state_from_matter_action": "BLOCKED",
                "covariant_coarse_graining": "BLOCKED",
                "covariant_transport_matching": "BLOCKED",
                "entropy_current_kms_completion": "BLOCKED",
                "physical_gr_benchmarks": "NOT_STARTED",
            },
            "global_universe_closure": "UNRESOLVED",
            "topic_0_11_status_impact": "NONE",
            "topic_0_19_status_impact": "NONE",
            "controlling_blocker": STATE_MAP_CONTROLLER,
            "claim_promotion": "BLOCKED",
            "reason": (
                "The coarse O2 Noether density/current and normalized C/J now "
                "have an exact fixed-scale coordinate map, while microscopic "
                "inversion is explicitly many-to-one. The charge-density "
                "equation of state, coarse-graining prescription, and covariant "
                "dissipative transport are not derived."
            ),
        }
    )


def _replace_program_with_o2_superfluid_stage(
    payload: dict[str, Any],
    program: dict[str, Any],
) -> None:
    """Preserve the generated Wave 10 gate as the stage source of truth.

    Earlier generators may rerun after Wave 10 is complete.  Reusing the
    existing stage payload, including its timestamp, keeps cross-generator
    reproducibility stable instead of making the stage depend on rerun order.
    """

    payload.clear()
    payload.update(program)



def apply_latest_hyperbolic_phase_field_stage(
    out: Path,
    *payloads: dict[str, Any],
) -> bool:
    """Apply the latest downstream stage to earlier generated payloads."""

    comparator = _load_comparator(out)
    if comparator is None:
        return False
    feasibility = _load_feasibility(out)
    state_map = _load_state_map(out)
    o2_program = _load_o2_superfluid_program(out)
    for payload in payloads:
        _update_payload(payload, comparator)
    if feasibility is not None:
        for payload in payloads:
            _update_feasibility_payload(payload, comparator, feasibility)
    if state_map is not None:
        for payload in payloads:
            _update_state_map_payload(payload, state_map)
    for payload in payloads:
        if payload.get("artifact") != "uet_gr_research_program_gate":
            continue
        if o2_program is not None:
            _replace_program_with_o2_superfluid_stage(payload, o2_program)
            continue
        if state_map is not None:
            _replace_program_with_state_map_stage(payload)
            continue
        if feasibility is not None:
            payload["topic"] = PROGRAM_TOPIC
            payload["version"] = "wave8_v1"
            payload["benchmark_role"] = "program_gate"
            payload["method_label"] = "monotonic_gr_research_stage_gate"
            payload["input_identity"] = {
                "causal_feasibility_artifact": (
                    _artifact_ref(FEASIBILITY_ARTIFACT)
                ),
                "covariant_mapping_gate": (
                    _artifact_ref(MAPPING_GATE_ARTIFACT)
                ),
            }
            payload["notes"] = [
                "The controlling blocker is the physical density/order-parameter state map.",
                "Thermal SK/KMS completion is downstream of the classical covariant lane.",
            ]
            payload["program_stage"] = FEASIBILITY_STAGE
            payload["controlling_blocker"] = FEASIBILITY_CONTROLLER
            sectors = payload.setdefault("sector_status", {})
            sectors["gradient_phase_field_causality"] = (
                "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY"
            )
            sectors["fixed_light_cone_parameter_domain"] = (
                "PASS_NORMALIZED_ANALYTIC"
            )
            sectors["uniform_subluminal_phase_field_limit"] = (
                "NO_GO_FOR_EXACT_PARABOLIC_LIMIT"
            )
            sectors["local_current_law_mapping"] = (
                "PASS_ALGEBRAIC_MOBILITY_ONE"
            )
            sectors["uet_covariant_phase_field_mapping"] = "BLOCKED"
            sectors["entropy_current_kms_completion"] = "BLOCKED"
            payload["reason"] = (
                "Exact normalized fixed-cone inequalities and a local "
                "mobility-one current-law map are verified, but the external "
                "order parameter is not mapped to the UET Noether density."
            )
            payload["status"] = "BLOCKED"
            payload["claim_promotion"] = "BLOCKED"
            payload["global_universe_closure"] = "UNRESOLVED"
            payload["topic_0_11_status_impact"] = "NONE"
            payload["topic_0_19_status_impact"] = "NONE"
            continue
        payload["program_stage"] = LATEST_STAGE
        payload["controlling_blocker"] = LATEST_CONTROLLER
        sectors = payload.setdefault("sector_status", {})
        sectors["gradient_phase_field_causality"] = (
            "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY"
        )
        sectors["uniform_subluminal_phase_field_limit"] = "BLOCKED"
        sectors["uet_covariant_phase_field_mapping"] = "BLOCKED"
        payload["reason"] = (
            "A sourced external first-order hyperbolic phase-field comparator "
            "closes at formula level for fixed parameters, but it is not "
            "UET-derived and its parabolic Cahn-Hilliard scaling is not "
            "uniformly subluminal."
        )
        payload["status"] = "BLOCKED"
        payload["claim_promotion"] = "BLOCKED"
        payload["global_universe_closure"] = "UNRESOLVED"
        payload["topic_0_11_status_impact"] = "NONE"
        payload["topic_0_19_status_impact"] = "NONE"
    return True
