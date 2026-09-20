"""Dependency-only alignment between the core GR program and Topic 0.19.

The verifier does not rerun the Topic 0.19 CODATA checkpoint and does not solve
any metric PDE.  It records which core mathematical candidate layers exist,
which Topic 0.19 physical tests remain absent, and why the exact epsilon_nc=0
response-null is not a statement about global universe closure.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET repository root not found")


ROOT = _bootstrap()
TOPIC = "0.19_Gravity_GR"
TOPIC_DIR = ROOT / "docs" / "topics" / TOPIC
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"

CORE_PROGRAM = ROOT / "docs/core/07_artifacts/gates/uet_gr_research_program_gate.json"
CORE_CLOSED_LIMIT = ROOT / "docs/core/07_artifacts/verification/gr_closed_limit_verification.json"
CORE_BALANCE = ROOT / "docs/core/07_artifacts/verification/covariant_bianchi_exchange_verification.json"
CORE_CAUSAL = ROOT / "docs/core/07_artifacts/verification/causal_nonclosed_kernel_verification.json"
CORE_REDUCTION = ROOT / "docs/core/07_artifacts/verification/covariant_matter_space_reduction_verification.json"
CORE_STATE_MAP = ROOT / "docs/core/07_artifacts/gates/noether_phase_field_dependency_gate.json"
TOPIC_PRIMARY = ARTIFACT_DIR / "0_19_gravity_gr_verification.json"
TOPIC_BRANCH_GATE = TOPIC_DIR / "Data/03_Research/branch_claim_gate.json"
READINESS_METADATA = ROOT / "docs/meta/topic_readiness.json"

ARTIFACT_PATH = ARTIFACT_DIR / "0_19_core_gr_program_dependency_gate.json"
CONTROLLING_BLOCKER = "topic_0_19_classical_gr_tests_and_covariant_completion_missing"
VOLATILE_JSON_KEYS = frozenset(
    {"generated_at", "generated_at_utc", "timestamp_utc", "environment"}
)


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _strip_volatile(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_volatile(item)
            for key, item in sorted(value.items())
            if key not in VOLATILE_JSON_KEYS
        }
    if isinstance(value, list):
        return [_strip_volatile(item) for item in value]
    return value


def scientific_payload_sha256(path: Path) -> str:
    payload = _strip_volatile(load_json(path))
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def gate(status: str, required_condition: str, **details: Any) -> dict[str, Any]:
    return {"status": status, "required_condition": required_condition, **details}


def _readiness_topic(metadata: dict[str, Any]) -> dict[str, Any]:
    for topic in metadata.get("topics", []):
        if topic.get("name") == TOPIC:
            return topic
    raise RuntimeError(f"Canonical readiness entry not found for {TOPIC}")


def _input_record(path: Path, role: str) -> dict[str, Any]:
    return {
        "path": relpath(path),
        "role": role,
        "exists": path.exists(),
        "scientific_payload_sha256": scientific_payload_sha256(path),
        "hash_scope": (
            "canonical_json_without_generated_at_generated_at_utc_"
            "timestamp_utc_or_environment"
        ),
    }


def build_artifact() -> dict[str, Any]:
    program = load_json(CORE_PROGRAM)
    closed_limit = load_json(CORE_CLOSED_LIMIT)
    balance = load_json(CORE_BALANCE)
    causal = load_json(CORE_CAUSAL)
    reduction = load_json(CORE_REDUCTION)
    state_map = load_json(CORE_STATE_MAP)
    topic_primary = load_json(TOPIC_PRIMARY)
    topic_branch = load_json(TOPIC_BRANCH_GATE)
    readiness = _readiness_topic(load_json(READINESS_METADATA))

    sectors = program.get("sector_status", {})
    topic_scope = topic_primary.get("gravity_claim_scope_gate", {})

    program_checks = {
        "program_is_still_blocked": program.get("status") == "BLOCKED",
        "stage_is_current": program.get("program_stage")
        == "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED",
        "claim_class_is_candidate_B": program.get("current_claim_class") == "B",
        "claim_promotion_blocked": program.get("claim_promotion") == "BLOCKED",
        "physical_benchmarks_not_started": sectors.get("physical_gr_benchmarks")
        == "NOT_STARTED",
    }

    closed_checks = {
        "closed_limit_artifact_pass": closed_limit.get("status") == "PASS",
        "epsilon_zero_program_null": program.get("gr_null_model")
        == {"parameter": "epsilon_nc", "value": 0, "verification_status": "PASS"},
        "metric_residual_zero": closed_limit.get("numeric", {}).get(
            "closed_limit_max_abs_residual"
        )
        == 0.0,
        "scalar_residual_zero": closed_limit.get("numeric", {}).get(
            "scalar_closed_limit_residual"
        )
        == 0.0,
        "metric_pde_not_solved": closed_limit.get("run_contract", {}).get(
            "metric_pde_solved"
        )
        is False,
        "trace_disconnected": closed_limit.get("gates", {}).get(
            "derived_trace_disconnected"
        )
        == "PASS",
    }

    balance_checks = {
        "balance_artifact_pass": balance.get("status") == "PASS",
        "local_identity_exact": balance.get("symbolic", {}).get("identity_exact")
        is True,
        "exchange_closure_exact": balance.get("symbolic", {}).get(
            "exchange_closure_exact"
        )
        is True,
        "global_energy_theorem_not_claimed": balance.get("run_contract", {}).get(
            "global_energy_theorem"
        )
        is False,
        "curved_derivative_solver_absent": balance.get("run_contract", {}).get(
            "curved_derivative_solver"
        )
        is False,
    }

    causal_checks = {
        "causal_artifact_pass": causal.get("status") == "PASS",
        "outside_cone_zero": causal.get("numeric", {}).get("outside_cone_max_abs")
        == 0.0,
        "arrival_error_zero": causal.get("numeric", {}).get(
            "arrival_speed_relative_error_max"
        )
        == 0.0,
        "one_spatial_dimension": causal.get("run_contract", {}).get(
            "spatial_dimension"
        )
        == 1,
        "flat_local_slice_only": causal.get("run_contract", {}).get(
            "flat_local_slice"
        )
        is True,
        "curved_green_solver_absent": causal.get("run_contract", {}).get(
            "curved_green_solver"
        )
        is False,
    }

    reduction_checks = {
        "reduction_audit_pass": reduction.get("audit_status") == "PASS",
        "evidence_is_partial": reduction.get("evidence_status") == "PARTIAL",
        "response_sector_only": reduction.get("run_contract", {}).get(
            "response_sector_only"
        )
        is True,
        "full_matter_equation_not_derived": reduction.get("run_contract", {}).get(
            "full_matter_equation_derived"
        )
        is False,
        "full_coupled_reduction_blocked": reduction.get("blocked_gates", {}).get(
            "full_coupled_matter_space_reduction"
        )
        == "BLOCKED",
    }

    state_map_checks = {
        "state_map_dependency_blocked": state_map.get("status") == "BLOCKED",
        "affine_layer_pass": state_map.get("completed_layers", {}).get(
            "coarse_density_to_phase_coordinate"
        )
        == "PASS_AFFINE_FIXED_SCALE",
        "microscopic_inverse_rejected": state_map.get("completed_layers", {}).get(
            "microscopic_inverse_requirement"
        )
        == "REJECTED_AS_CATEGORY_ERROR",
        "equation_of_state_blocked": state_map.get("blocked_layers", {}).get(
            "equation_of_state_from_covariant_O2_action"
        )
        == "BLOCKED_CONTROLLING",
        "transport_blocked": state_map.get("blocked_layers", {}).get(
            "susceptibility_and_transport_coefficient_matching"
        )
        == "BLOCKED",
        "trace_feedback_forbidden": "do_not_import_trace_as_state_or_feedback"
        in state_map.get("forbidden_shortcuts", []),
    }

    checkpoint_checks = {
        "topic_primary_pass": topic_primary.get("status") == "PASS",
        "topic_claim_class_is_checkpoint": topic_primary.get("claim_class")
        == "C - source-constant internal checkpoint only",
        "topic_export_controller_warn": topic_scope.get("controller_status") == "WARN",
        "branch_gate_two_accepted": topic_branch.get("summary", {}).get("accepted_now")
        == 2,
        "branch_gate_four_blocked": topic_branch.get("summary", {}).get(
            "blocked_for_strong_claims"
        )
        == 4,
    }

    canonical_status_pass = readiness.get("status") == "Draft" and readiness.get(
        "audit_tier"
    ) == "B"
    topic_blockers = topic_scope.get("machine_readable_next_blockers", [])

    gates = {
        "core_program_stage_gate": gate(
            "PASS" if all(program_checks.values()) else "BLOCKED",
            "The current core stage must remain a blocked class-B candidate program rather than a promoted GR result.",
            checks=program_checks,
            program_controller=program.get("controlling_blocker"),
        ),
        "exact_gr_response_null_gate": gate(
            "PASS" if all(closed_checks.values()) else "BLOCKED",
            "epsilon_nc=0 must remove the implemented response corrections exactly without being described as a full metric-PDE derivation.",
            checks=closed_checks,
        ),
        "local_covariant_balance_gate": gate(
            "PASS" if all(balance_checks.values()) else "BLOCKED",
            "The local exchange-completed identity may pass only with global and curved-solver claims explicitly absent.",
            checks=balance_checks,
        ),
        "causal_constitutive_scope_gate": gate(
            "PASS" if all(causal_checks.values()) else "BLOCKED",
            "Causal support is accepted only for the declared flat local 1+1 constitutive kernel.",
            checks=causal_checks,
        ),
        "partial_response_reduction_gate": gate(
            "PASS" if all(reduction_checks.values()) else "BLOCKED",
            "Only the response-sector coefficient map may be inherited; the full coupled matter equation remains underived.",
            checks=reduction_checks,
        ),
        "noether_state_map_scope_gate": gate(
            "PASS" if all(state_map_checks.values()) else "BLOCKED",
            "The coarse coordinate result must preserve the many-to-one microscopic boundary and open EOS/transport blockers.",
            checks=state_map_checks,
        ),
        "topic_constant_checkpoint_preservation_gate": gate(
            "PASS" if all(checkpoint_checks.values()) else "BLOCKED",
            "The existing Topic 0.19 CODATA/Planck checkpoint remains its independent primary artifact and claim ceiling.",
            checks=checkpoint_checks,
        ),
        "physical_gr_benchmark_gate": gate(
            "BLOCKED",
            "Topic promotion requires dedicated light-bending, perihelion, MICROSCOPE, Eot-Wash, metric/EFE, and uncertainty artifacts.",
            unchanged_topic_blockers=topic_blockers,
        ),
        "covariant_completion_gate": gate(
            "BLOCKED",
            "Promotion requires equation-of-state, covariant coarse-graining, transport/KMS, entropy-current, dissipative-Bianchi, and curved 3+1 closure.",
            blocked_core_sectors={
                key: value
                for key, value in sectors.items()
                if value in {"BLOCKED", "NOT_STARTED"}
            },
        ),
        "global_universe_closure_gate": gate(
            "PASS" if program.get("global_universe_closure") == "UNRESOLVED" else "BLOCKED",
            "The complete universe must remain unresolved; epsilon_nc is a nesting coupling, not an openness percentage.",
            global_universe_closure=program.get("global_universe_closure"),
        ),
        "canonical_topic_status_gate": gate(
            "PASS" if canonical_status_pass else "BLOCKED",
            "Canonical Topic 0.19 status must remain unchanged by this dependency packet.",
            status_before=readiness.get("status"),
            status_after=readiness.get("status"),
            tier_before=readiness.get("audit_tier"),
            tier_after=readiness.get("audit_tier"),
        ),
        "topic_promotion_gate": gate(
            "BLOCKED",
            "Core candidate mathematics cannot replace Topic 0.19 physical benchmarks or promote the topic claim.",
        ),
    }

    input_paths = [
        (CORE_PROGRAM, "Current core GR research-program gate"),
        (CORE_CLOSED_LIMIT, "Exact implemented GR response-null verification"),
        (CORE_BALANCE, "Local covariant exchange-balance verification"),
        (CORE_CAUSAL, "Flat local 1+1 causal constitutive kernel"),
        (CORE_REDUCTION, "Partial response-sector reduction verification"),
        (CORE_STATE_MAP, "Noether/phase-field dependency boundary"),
        (TOPIC_PRIMARY, "Topic 0.19 CODATA/Planck primary checkpoint"),
        (TOPIC_BRANCH_GATE, "Topic 0.19 branch claim gate"),
        (READINESS_METADATA, "Canonical topic readiness metadata"),
    ]

    return {
        "schema_version": "1.0",
        "artifact": "0_19_core_gr_program_dependency_gate",
        "topic": TOPIC,
        "version": "core_wave9_topic_dependency_v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "command": "python docs/topics/0.19_Gravity_GR/Code/03_Research/Research_Core_GR_Program_Dependency_Gate.py",
        "benchmark_role": "DEPENDENCY_ONLY_NO_PHYSICAL_GR_RERUN",
        "status": "BLOCKED",
        "evidence_status": "CORE_CANDIDATE_GR_PARENT_AVAILABLE_TOPIC_PHYSICAL_VALIDATION_OPEN",
        "claim_class": "internal_dependency_boundary",
        "controlling_blocker": CONTROLLING_BLOCKER,
        "core_program_stage": program.get("program_stage"),
        "core_program_controller": program.get("controlling_blocker"),
        "topic_primary_status_unchanged": topic_primary.get("status"),
        "topic_claim_scope_controller_unchanged": topic_scope.get(
            "controller_status"
        ),
        "topic_controlling_blockers_unchanged": topic_blockers,
        "topic_status_impact": "NONE",
        "canonical_topic_status": readiness.get("status"),
        "canonical_topic_tier": readiness.get("audit_tier"),
        "global_universe_closure": program.get("global_universe_closure"),
        "scientific_inputs": [_input_record(path, role) for path, role in input_paths],
        "gates": gates,
        "completed_scope": [
            "exact implemented epsilon_nc=0 response-null of the candidate tensor evaluator",
            "local exchange-completed covariant identity for the conservative candidate parent",
            "exact-support flat local 1+1 constitutive kernel",
            "partial response-sector reduction under declared scaling",
            "fixed-scale coarse Noether-charge coordinate layer with microscopic no-go boundary",
        ],
        "blocked_scope": [
            "Einstein equations derived from UET",
            "full curved 3+1 well-posed evolution",
            "classical GR light-bending and perihelion validation",
            "MICROSCOPE equivalence-principle and Eot-Wash short-range validation",
            "equation-of-state, covariant coarse-graining, transport/KMS, and entropy-current completion",
            "global universe open/closed proof",
            "singularity or quantum-gravity closure",
        ],
        "required_next_evidence": [
            "dedicated source-backed light-bending and perihelion artifacts with uncertainties and baselines",
            "MICROSCOPE eta and Eot-Wash exclusion-curve comparison artifacts",
            "curved 3+1 metric/response solver with well-posedness and convergence gates",
            "charge-density EOS, covariant coarse graining, transport/KMS, entropy-current, and dissipative-Bianchi completion",
            "independent holdout comparison of epsilon_nc != 0 against the epsilon_nc=0 GR null model",
        ],
        "allowed_language": [
            "candidate conservative covariant parent",
            "exact implemented GR response-null contract",
            "local covariant exchange-balance identity",
            "flat local 1+1 causal constitutive kernel",
            "partial response-sector reduction",
        ],
        "blocked_language": [
            "UET derives Einstein equations",
            "UET validates general relativity",
            "the universe is proved open or closed",
            "epsilon_nc is the percentage openness of the universe",
            "core candidate artifacts replace classical GR tests",
            "Topic 0.19 is externally validated or solved",
        ],
        "limitations": [
            "No Topic 0.19 simulation, physical-data comparison, metric PDE, or parameter fit is run.",
            "The causal kernel is restricted to a flat local 1+1 constitutive lane.",
            "The response reduction is partial and does not derive the full matter equation.",
            "The existing Topic 0.19 PASS remains only a source-constant checkpoint.",
        ],
        "claim_boundary": (
            "The core program supplies candidate mathematical GR-response infrastructure and an exact implemented "
            "epsilon_nc=0 response-null, but Topic 0.19 remains a Draft/Tier-B CODATA checkpoint with physical GR "
            "benchmarks and covariant completion blocked. No global-universe or validation claim is promoted."
        ),
        "environment": {
            # Keep this provenance field portable: the artifact is compared in
            # local and CI runtimes, while scientific inputs are hashed separately.
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "platform": "portable-research-runtime",
        },
    }


def main() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact = build_artifact()
    ARTIFACT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact


if __name__ == "__main__":
    result = main()
    print(
        json.dumps(
            {
                "status": result["status"],
                "evidence_status": result["evidence_status"],
                "controlling_blocker": result["controlling_blocker"],
                "core_program_stage": result["core_program_stage"],
                "gates": {
                    name: value["status"]
                    for name, value in result["gates"].items()
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
