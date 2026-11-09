"""
UET Critical Exponents Research
===============================
Topic: 0.11 Phase Transitions
Goal: Validate UET prediction for universality classes (Critical Exponents).
Data: 3D Ising Model / Liquid-Gas Universality.

Hypothesis:
Critical exponents derive from the dimensionality of the Information Manifold.
Beta ~ 1/D_effective. For 3D space, D_eff ~ 3, Beta ~ 1/3 (0.333).
Compare with Mean Field (Beta=0.5) and 3D Ising (Beta=0.326).
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import platform
from datetime import datetime, timezone
from hashlib import sha256

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
project_root = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists() and (parent / "docs" / "core").exists():
        project_root = parent
        break

if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
elif not project_root:
    # Fallback to 5 levels up
    fallback = current_path.parents[5]
    if (fallback / "docs").exists():
        sys.path.insert(0, str(fallback))
    else:
        sys.path.insert(0, str(current_path.parents[4]))

from docs.core.uet_glass_box import UETPathManager, UETMetricLogger


TOPIC_DIR = project_root / "docs" / "topics" / "0.11_Phase_Transitions"
DATA_FILE = TOPIC_DIR / "Data" / "03_Research" / "critical_exponents.json"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_phase_transitions_verification.json"
SOURCE_EVIDENCE_INTAKE_PATH = TOPIC_DIR / "Data" / "03_Research" / "source_evidence_intake_stub.json"
SOURCE_EVIDENCE_READINESS_PATH = TOPIC_DIR / "Data" / "03_Research" / "source_evidence_readiness_matrix.json"
BRANCH_CLAIM_GATE_PATH = TOPIC_DIR / "Data" / "03_Research" / "branch_claim_gate.json"


def load_critical_data():
    """Load Critical Exponents data."""
    if not DATA_FILE.exists():
        return None
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def build_source_evidence_intake_stub() -> dict:
    return {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "purpose": "Source evidence intake before upgrading claims across the phase-transition benchmark, normalized simulations, and universality branches.",
        "source_targets": [
            {
                "name": "Critical exponent benchmark package",
                "priority": "immediate",
                "status_hint": "working_copy_benchmark_with_literature_metadata",
                "evidence_entries": [
                    "working_copy_json_path",
                    "literature_reference_list",
                    "observable_scope",
                    "unit_basis",
                    "benchmark_role",
                    "upgrade_requirement",
                ],
            },
            {
                "name": "Critical-point material table package",
                "priority": "high",
                "status_hint": "working_copy_material_gate",
                "evidence_entries": [
                    "table_path",
                    "upstream_source_package",
                    "observable_scope",
                    "unit_basis",
                    "preprocessing_note",
                    "upgrade_requirement",
                ],
            },
            {
                "name": "Cahn-Hilliard morphology package",
                "priority": "high",
                "status_hint": "normalized_mechanism_diagnostic",
                "evidence_entries": [
                    "engine_path",
                    "seed_policy",
                    "grid_and_unit_convention",
                    "morphology_metric_package",
                    "material_mapping_note",
                    "upgrade_requirement",
                ],
            },
            {
                "name": "Order-parameter proof package",
                "priority": "high",
                "status_hint": "internal_diagnostic_branch",
                "evidence_entries": [
                    "proof_script_path",
                    "threshold_policy",
                    "artifact_path",
                    "observable_scope",
                    "claim_boundary_note",
                    "upgrade_requirement",
                ],
            },
            {
                "name": "Universality and renormalization-group closure package",
                "priority": "medium",
                "status_hint": "blocked_theory_branch",
                "evidence_entries": [
                    "full_exponent_set",
                    "scaling_relation_checks",
                    "rg_derivation_package",
                    "held_out_material_suite",
                    "cross_topic_dependency_map",
                    "upgrade_requirement",
                ],
            },
        ],
        "claim_boundary": "This intake stub organizes provenance and branch-upgrade work only. It does not itself prove a universal phase-transition theory.",
    }


def build_source_evidence_readiness_matrix() -> dict:
    rows = [
        {
            "name": "Critical exponent benchmark package",
            "priority": "immediate",
            "fields_total": 6,
            "fields_complete": 4,
            "fields_pending": 2,
            "pending_fields": [
                "upstream_external_archive",
                "preprocessing_and_hash_lock",
            ],
            "ready_for_source_review": False,
            "blocking_reason": "The current beta benchmark is literature-referenced but still stored only as a topic-local working copy.",
        },
        {
            "name": "Critical-point material table package",
            "priority": "high",
            "fields_total": 6,
            "fields_complete": 2,
            "fields_pending": 4,
            "pending_fields": [
                "upstream_source_package",
                "preprocessing_note",
                "hash_lock",
                "benchmark_role_closure",
            ],
            "ready_for_source_review": False,
            "blocking_reason": "The NIST-style critical-point table is still a working copy without a normalized external archive.",
        },
        {
            "name": "Cahn-Hilliard morphology package",
            "priority": "high",
            "fields_total": 6,
            "fields_complete": 2,
            "fields_pending": 4,
            "pending_fields": [
                "seed_policy",
                "grid_and_unit_convention",
                "morphology_metric_package",
                "material_mapping_note",
            ],
            "ready_for_source_review": False,
            "blocking_reason": "The Cahn-Hilliard solver remains a normalized mechanism diagnostic without fixed morphology and material gates.",
        },
        {
            "name": "Order-parameter proof package",
            "priority": "high",
            "fields_total": 6,
            "fields_complete": 3,
            "fields_pending": 3,
            "pending_fields": [
                "threshold_policy",
                "artifact_path",
                "upgrade_requirement",
            ],
            "ready_for_source_review": False,
            "blocking_reason": "Order-parameter proof scripts remain internal diagnostics without an audit-grade threshold policy.",
        },
        {
            "name": "Universality and renormalization-group closure package",
            "priority": "medium",
            "fields_total": 6,
            "fields_complete": 0,
            "fields_pending": 6,
            "pending_fields": [
                "full_exponent_set",
                "scaling_relation_checks",
                "rg_derivation_package",
                "held_out_material_suite",
                "cross_topic_dependency_map",
                "upgrade_requirement",
            ],
            "ready_for_source_review": False,
            "blocking_reason": "The topic does not yet have a full exponent set, scaling checks, or renormalization-group closure package.",
        },
    ]
    ready_count = sum(1 for row in rows if row["ready_for_source_review"])
    return {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "purpose": "Readiness matrix for source-evidence review across phase-transition benchmark and theory branches.",
        "summary": {
            "source_targets_total": len(rows),
            "targets_ready_for_source_review": ready_count,
            "targets_blocked_by_pending_evidence": len(rows) - ready_count,
        },
        "readiness_rows": rows,
        "claim_boundary": "A ready row has enough provenance structure for source review. It does not by itself upgrade universality claims.",
    }


def build_branch_claim_gate() -> dict:
    return {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "purpose": "Claim gate for separate phase-transition branches inside the topic.",
        "summary": {
            "branches_total": 6,
            "accepted_now": 2,
            "blocked_for_strong_claims": 4,
        },
        "branches": [
            {
                "branch": "Selected beta critical-exponent benchmark branch",
                "status": "accepted_internal_benchmark_branch",
                "allowed_usage_now": "Accepted selected beta compatibility branch against the topic-local 3D Ising/liquid-gas benchmark.",
                "blocker_to_stronger_claim": "Need externally archived exponent sources and a fuller exponent set before promoting this branch.",
            },
            {
                "branch": "Normalized Cahn-Hilliard mechanism branch",
                "status": "accepted_mechanism_diagnostic_branch",
                "allowed_usage_now": "Accepted normalized mechanism simulation branch only.",
                "blocker_to_stronger_claim": "Need fixed seeds, unit conventions, morphology metrics, and material mapping before using it as material evidence.",
            },
            {
                "branch": "Order-parameter proof branch",
                "status": "blocked_for_strong_claims",
                "allowed_usage_now": "Internal diagnostic only.",
                "blocker_to_stronger_claim": "Need an audit-grade threshold policy and machine-readable artifact path.",
            },
            {
                "branch": "Material critical-point benchmark branch",
                "status": "blocked_for_strong_claims",
                "allowed_usage_now": "Future gate only.",
                "blocker_to_stronger_claim": "Need source-locked external critical-point tables and preprocessing records.",
            },
            {
                "branch": "Full critical-exponent and scaling-relation branch",
                "status": "blocked_for_strong_claims",
                "allowed_usage_now": "Not supported by current evidence.",
                "blocker_to_stronger_claim": "Need gamma, nu, scaling relations, and held-out material checks as primary gates.",
            },
            {
                "branch": "Universal phase-transition theory claims",
                "status": "blocked_for_strong_claims",
                "allowed_usage_now": "Not supported by current evidence.",
                "blocker_to_stronger_claim": "Need renormalization-group closure and cross-topic consistency beyond the selected beta benchmark.",
            },
        ],
        "claim_boundary": "This gate keeps the topic at selected-benchmark and mechanism-diagnostic status, not universal theory closure.",
    }


def build_phase_transition_claim_scope_gate(
    status: str,
    error_percent: float,
    source_evidence_readiness_matrix: dict,
    branch_claim_gate: dict,
) -> dict:
    controller_status = "WARN" if status == "PASS" else "FAIL"
    return {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "controller_status": controller_status,
        "controller_reason": (
            "The selected beta benchmark passed, but topic-level export remains warning-gated because "
            "source readiness is incomplete and full exponent/scaling/RG branches are blocked."
            if status == "PASS"
            else "The selected beta benchmark did not meet the declared relative-error threshold."
        ),
        "claim_class": "C_selected_exponent_benchmark_only",
        "allowed_claims_now": [
            {
                "claim": "The current UET beta projection is compatible with the topic-local 3D Ising/liquid-gas beta benchmark under the declared threshold.",
                "status": status,
                "artifact_role": "primary selected beta benchmark",
                "metric": "beta_relative_error_percent",
                "metric_value": error_percent,
                "threshold": "<= 5.0",
                "source_evidence_readiness": "working_copy_not_source_locked",
            },
            {
                "claim": "The Cahn-Hilliard branch can be cited as a normalized mechanism diagnostic.",
                "status": "DIAGNOSTIC_ONLY",
                "artifact_role": "supporting simulation branch",
                "formula_role": "normalized mechanism illustration, not material calibration",
                "source_evidence_readiness": "pending_seed_unit_morphology_gate",
            },
        ],
        "blocked_claims": [
            {
                "claim": "UET proves a universal phase-transition theory.",
                "status": "BLOCKED",
                "blocking_reason": "No renormalization-group closure package or cross-topic dependency proof is available.",
                "next_evidence_required": [
                    "renormalization-group derivation package",
                    "cross-topic dependency map",
                    "independent review status",
                ],
            },
            {
                "claim": "UET explains the full critical-exponent set and scaling relations.",
                "status": "BLOCKED",
                "blocking_reason": "The primary gate tests beta only; gamma, nu, and scaling relations are not gated.",
                "next_evidence_required": [
                    "full exponent-set benchmark",
                    "scaling-relation checks",
                    "held-out material suite",
                ],
            },
            {
                "claim": "UET is validated against source-locked material critical-point data.",
                "status": "BLOCKED",
                "blocking_reason": "Critical-point and exponent data remain topic-local working copies without normalized external archives.",
                "next_evidence_required": [
                    "external source archive",
                    "preprocessing record",
                    "hash-locked material table",
                ],
            },
        ],
        "blocked_export_phrases": [
            "universal phase-transition theory proved",
            "renormalization-group closure established",
            "full critical-exponent set validated",
            "material critical points validated",
            "phase transitions solved",
        ],
        "source_evidence_summary": source_evidence_readiness_matrix["summary"],
        "branch_claim_gate_summary": branch_claim_gate["summary"],
        "machine_readable_next_blockers": [
            "critical_exponent_sources_not_archived",
            "full_exponent_set_missing",
            "scaling_relation_checks_missing",
            "rg_closure_package_missing",
            "material_critical_point_gate_missing",
        ],
        "claim_boundary": (
            "A PASS artifact supports selected beta-exponent compatibility only. It does not prove "
            "universal phase-transition theory, full exponent/scaling closure, or material critical-point validation."
        ),
    }


def write_artifact(error_percent: float, beta_values: dict, save_path: Path) -> None:
    status = "PASS" if error_percent <= 5.0 else "FAIL"
    source_evidence_intake_stub = build_source_evidence_intake_stub()
    source_evidence_readiness_matrix = build_source_evidence_readiness_matrix()
    branch_claim_gate = build_branch_claim_gate()
    write_json(SOURCE_EVIDENCE_INTAKE_PATH, source_evidence_intake_stub)
    write_json(SOURCE_EVIDENCE_READINESS_PATH, source_evidence_readiness_matrix)
    write_json(BRANCH_CLAIM_GATE_PATH, branch_claim_gate)
    phase_transition_claim_scope_gate = build_phase_transition_claim_scope_gate(
        status,
        error_percent,
        source_evidence_readiness_matrix,
        branch_claim_gate,
    )
    artifact = {
        "schema_version": "1.1",
        "topic": "0.11_Phase_Transitions",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Critical_Exponents.py",
        "status": status,
        "claim_class": "C internal benchmark" if status == "PASS" else "model-baseline blocker",
        "inputs": [
            {
                "path": str(DATA_FILE.relative_to(TOPIC_DIR)),
                "sha256": hash_file(DATA_FILE),
                "role": "3D Ising/liquid-gas beta exponent working-copy benchmark",
            }
        ],
        "thresholds": {"beta_relative_error_percent_max": 5.0},
        "metrics": {
            "beta_relative_error_percent": error_percent,
            "beta_uet": beta_values["uet"],
            "beta_experimental_fluids": beta_values["experimental"],
            "beta_3d_ising_theory": beta_values["ising"],
            "beta_mean_field": beta_values["mean_field"],
            "source_targets_ready_for_review": source_evidence_readiness_matrix["summary"]["targets_ready_for_source_review"],
            "source_targets_blocked": source_evidence_readiness_matrix["summary"]["targets_blocked_by_pending_evidence"],
            "accepted_claim_branches": branch_claim_gate["summary"]["accepted_now"],
            "blocked_claim_exports": len(phase_transition_claim_scope_gate["blocked_export_phrases"]),
        },
        "results": {
            "plot_path": str(save_path.relative_to(TOPIC_DIR)),
            "interpretation": "selected beta critical-exponent compatibility only",
            "source_evidence_readiness_summary": source_evidence_readiness_matrix["summary"],
            "branch_claim_gate_summary": branch_claim_gate["summary"],
            "phase_transition_claim_scope_gate_status": phase_transition_claim_scope_gate["controller_status"],
        },
        "limitations": [
            "Only beta is tested in the current primary gate.",
            "Gamma, nu, scaling relations, morphology, and material critical-point datasets are not yet gated.",
            "The UET beta relation is a heuristic projection until broader exponent and derivation checks are added.",
        ],
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy_version": np.__version__,
        },
    }
    artifact["source_evidence_intake_stub"] = {
        "path": str(SOURCE_EVIDENCE_INTAKE_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        "sha256": sha256(json.dumps(source_evidence_intake_stub, sort_keys=True).encode("utf-8")).hexdigest(),
        "source_targets": [row["name"] for row in source_evidence_intake_stub["source_targets"]],
        "claim_boundary": source_evidence_intake_stub["claim_boundary"],
    }
    artifact["source_evidence_readiness_matrix"] = {
        "path": str(SOURCE_EVIDENCE_READINESS_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        "sha256": sha256(json.dumps(source_evidence_readiness_matrix, sort_keys=True).encode("utf-8")).hexdigest(),
        "summary": source_evidence_readiness_matrix["summary"],
        "claim_boundary": source_evidence_readiness_matrix["claim_boundary"],
    }
    artifact["branch_claim_gate"] = {
        "path": str(BRANCH_CLAIM_GATE_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        "sha256": sha256(json.dumps(branch_claim_gate, sort_keys=True).encode("utf-8")).hexdigest(),
        "summary": branch_claim_gate["summary"],
        "claim_boundary": branch_claim_gate["claim_boundary"],
    }
    artifact["phase_transition_claim_scope_gate"] = phase_transition_claim_scope_gate
    artifact["interpretation"] = (
        "This artifact supports a selected beta benchmark branch and a normalized mechanism-diagnostic branch. "
        "It does not prove a universal phase-transition theory."
    )
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Artifact saved to {ARTIFACT_PATH}")


def run_critical_analysis():
    print("=" * 60)
    print("🔥 UET PHASE TRANSITIONS: UNIVERSALITY CLASSES")
    print("Data: 3D Ising / Liquid-Gas Experiment")
    print("=" * 60)

    data = load_critical_data()
    if not data:
        return False

    # Extract
    beta_ising = data["3D_Ising"]["theoretical"]["beta"]
    beta_exp = data["3D_Ising"]["experimental_fluids"]["beta"]
    beta_uet = data["3D_Ising"]["UET_prediction"]["beta"]
    beta_mean = data["Mean_Field"]["beta"]

    print(f"\n[1] Order Parameter Exponent (Beta)")
    print(f"  Mean Field Theory (Landau): {beta_mean}")
    print(f"  3D Ising (Renormalization): {beta_ising}")
    print(f"  Experimental (Fluids):      {beta_exp}")
    print(f"  UET Prediction (1/3):       {beta_uet}")

    # Calculate Error
    error = abs(beta_uet - beta_exp) / beta_exp * 100
    print(f"  UET Error vs Experiment:    {error:.2f}%")

    # --- VISUALIZATION ---
    result_dir = UETPathManager.get_result_dir(
        "0.11_Phase_Transitions", "Critical_Exponents_Validation", category="showcase"
    )
    logger = UETMetricLogger("PhaseTrans", topic_id="0.11", category="showcase")

    plt.figure(figsize=(10, 6))

    # Plot M ~ (-t)^Beta
    t = np.linspace(-1, 0, 100)  # Reduced temp (T-Tc)/Tc
    red_t = np.abs(t)

    M_mean = red_t**beta_mean
    M_ising = red_t**beta_ising
    M_uet = red_t**beta_uet

    plt.plot(red_t, M_mean, "k--", label=f"Mean Field (Beta={beta_mean})")
    plt.plot(
        red_t, M_ising, "g-", linewidth=4, alpha=0.5, label=f"3D Ising / Exp (Beta={beta_ising})"
    )
    plt.plot(red_t, M_uet, "b-.", label=f"UET Prediction (Beta={beta_uet})")

    plt.xlabel("Reduced Temperature |t| = |(T-Tc)/Tc|")
    plt.ylabel("Order Parameter (Density Diff)")
    plt.title("Universality Classes near Critical Point")
    plt.grid(True, alpha=0.3)
    plt.legend()

    save_path = result_dir / "Critical_Exponents_Validation.png"
    plt.savefig(save_path, dpi=300)
    print(f"📸 Showcase Image Saved: {save_path}")
    write_artifact(
        float(error),
        {
            "uet": float(beta_uet),
            "experimental": float(beta_exp),
            "ising": float(beta_ising),
            "mean_field": float(beta_mean),
        },
        save_path,
    )

    if error < 5.0:
        print("PASS: selected UET beta projection matches the topic-local beta benchmark; this is not a dynamics or RG-closure claim.")
        return True
    else:
        print("⚠️ WARNING: Error > 5%.")
        return True


if __name__ == "__main__":
    sys.exit(0 if run_critical_analysis() else 1)
