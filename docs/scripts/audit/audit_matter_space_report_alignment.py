"""Build the post-Wave-9 alignment gate for the matter-space report.

The integrated report dated 2026-07-21 remains a historical snapshot of the
normalized one-dimensional matter-space program.  This audit does not rewrite
that report.  It verifies a separate addendum against the later GR, Noether,
and downstream dependency artifacts so the two evidence scopes cannot be
silently conflated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from docs.core.core_paths import canonical_existing_path


OUTPUT_PATH = (
    REPO_ROOT
    / "docs/core/07_artifacts/gates/matter_space_report_alignment_gate.json"
)
BASE_REPORT_PATH = canonical_existing_path(
    REPO_ROOT / "docs/core/08_history/research_notes/MATTER_SPACE_RESEARCH_REPORT.md"
)
ADDENDUM_PATH = canonical_existing_path(
    REPO_ROOT / "docs/core/08_history/research_notes/MATTER_SPACE_RESEARCH_REPORT_ADDENDUM_2026-07-23.md"
)
TOPIC_READINESS_PATH = REPO_ROOT / "docs/meta/topic_readiness.json"

INPUT_PATHS = {
    "matter_space_program": REPO_ROOT
    / "docs/core/07_artifacts/gates/matter_space_research_program_gate.json",
    "gr_program": REPO_ROOT / "docs/core/07_artifacts/gates/uet_gr_research_program_gate.json",
    "noether_dependency": REPO_ROOT
    / "docs/core/07_artifacts/gates/noether_phase_field_dependency_gate.json",
    "topic_0_11_dependency": REPO_ROOT
    / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_noether_phase_field_dependency_gate.json",
    "topic_0_19_dependency": REPO_ROOT
    / "docs/topics/0.19_Gravity_GR/Result/artifacts/0_19_core_gr_program_dependency_gate.json",
    "topic_0_13_constraint": REPO_ROOT
    / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/0_13_core_thermodynamic_constraint_gate.json",
}

BASE_MATTER_CONTROLLER = "core_prearrival_leakage"
GR_CONTROLLER = (
    "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing"
 )
NOETHER_CONTROLLER = (
    "noether_charge_equation_of_state_and_covariant_transport_matching_missing"
)

ADDENDUM_REQUIRED_MARKERS = (
    "Base matter-space controller: `core_prearrival_leakage`",
    "Extended GR controller: `physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing`",
    "Global-universe closure: `UNRESOLVED`",
    "Topic 0.11: `Structured / Tier B`",
    "Topic 0.19: `Draft / Tier B`",
    "Topic 0.13: `Draft / Tier B`",
    "Trace `R` remains derived and has no backreaction.",
    "This does not prove that the complete universe is open or closed.",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def _generated_at(inputs: Iterable[dict[str, Any]]) -> str:
    values = [
        value
        for payload in inputs
        for value in (payload.get("generated_at"), payload.get("audit_date"))
        if isinstance(value, str) and value
    ]
    return max(values) if values else "SOURCE_TIMESTAMP_UNAVAILABLE"


def _json_record(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": _relative(path),
        "sha256": _sha256(path),
        "status": payload.get("status", "UNSPECIFIED"),
    }
    for key in (
        "evidence_status",
        "program_stage",
        "controlling_blocker",
        "topic_status_impact",
    ):
        if payload.get(key) is not None:
            record[key] = payload[key]
    return record


def _document_record(path: Path) -> dict[str, Any]:
    return {
        "path": _relative(path),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
    }


def _topic_record(metadata: dict[str, Any], name: str) -> dict[str, str]:
    for item in metadata["topics"]:
        if item.get("name") == name:
            return {
                "name": item["name"],
                "status": item["status"],
                "tier": item["audit_tier"],
            }
    raise KeyError(f"Missing canonical topic metadata: {name}")


def _report_snapshot_date(text: str) -> str:
    match = re.search(r"Evidence snapshot:\*\*\s*(\d{4}-\d{2}-\d{2})", text)
    return match.group(1) if match else "UNAVAILABLE"


def _normalized(text: str) -> str:
    return " ".join(text.split())


def build_alignment_gate(*, generated_at: str | None = None) -> dict[str, Any]:
    inputs = {name: _read_json(path) for name, path in INPUT_PATHS.items()}
    metadata = _read_json(TOPIC_READINESS_PATH)
    report_text = _read_text(BASE_REPORT_PATH)
    addendum_text = _read_text(ADDENDUM_PATH)
    report_normalized = _normalized(report_text)
    addendum_normalized = _normalized(addendum_text)

    matter = inputs["matter_space_program"]
    gr = inputs["gr_program"]
    noether = inputs["noether_dependency"]
    topic_0_11 = inputs["topic_0_11_dependency"]
    topic_0_19 = inputs["topic_0_19_dependency"]
    topic_0_13 = inputs["topic_0_13_constraint"]

    canonical = {
        "0.11": _topic_record(metadata, "0.11_Phase_Transitions"),
        "0.13": _topic_record(metadata, "0.13_Thermodynamic_Bridge"),
        "0.19": _topic_record(metadata, "0.19_Gravity_GR"),
    }

    report_snapshot = _report_snapshot_date(report_text)
    base_scope_pass = all(
        (
            report_snapshot == "2026-07-21",
            matter["status"] == "BLOCKED",
            matter["controlling_blocker"] == BASE_MATTER_CONTROLLER,
            BASE_MATTER_CONTROLLER in report_text,
            "candidate normalized effective model" in report_text,
        )
    )
    historical_topic_status = "Topic 0.11 remains Draft/Tier B" in report_normalized
    current_topic_status = (
        canonical["0.11"]["status"] == "Structured"
        and canonical["0.11"]["tier"] == "B"
        and topic_0_11["canonical_topic_status"] == "Structured"
        and topic_0_11["canonical_topic_tier"] == "B"
    )
    topic_status_drift = historical_topic_status and current_topic_status

    gr_scope_pass = all(
        (
            gr["status"] == "BLOCKED",
            gr["program_stage"] == "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED",
            gr["current_claim_class"] == "B",
            gr["gr_null_model"]["parameter"] == "epsilon_nc",
            gr["gr_null_model"]["value"] == 0,
            gr["gr_null_model"]["verification_status"] == "PASS",
            gr["global_universe_closure"] == "UNRESOLVED",
            gr["controlling_blocker"] == GR_CONTROLLER,
            noether["status"] == "BLOCKED",
            noether["controlling_blocker"] == NOETHER_CONTROLLER,
        )
    )

    downstream_pass = all(
        (
            topic_0_11["status"] == "BLOCKED",
            topic_0_11["topic_status_impact"] == "NONE",
            topic_0_19["status"] == "BLOCKED",
            topic_0_19["topic_status_impact"] == "NONE",
            topic_0_19["canonical_topic_status"] == "Draft",
            topic_0_19["canonical_topic_tier"] == "B",
            topic_0_13["status"] == "BLOCKED",
            topic_0_13["topic_status_impact"] == "NONE",
            topic_0_13["canonical_topic_status"] == "Draft",
            topic_0_13["canonical_topic_tier"] == "B",
        )
    )

    marker_checks = {
        marker: marker in addendum_normalized for marker in ADDENDUM_REQUIRED_MARKERS
    }
    linked_paths = (
        "../../07_artifacts/gates/matter_space_report_alignment_gate.json",
        "../../07_artifacts/gates/matter_space_research_program_gate.json",
        "../../07_artifacts/gates/uet_gr_research_program_gate.json",
        "../../07_artifacts/gates/noether_phase_field_dependency_gate.json",
        "../../../topics/0.11_Phase_Transitions/Result/artifacts/0_11_noether_phase_field_dependency_gate.json",
        "../../../topics/0.19_Gravity_GR/Result/artifacts/0_19_core_gr_program_dependency_gate.json",
        "../../../topics/0.13_Thermodynamic_Bridge/Result/artifacts/0_13_core_thermodynamic_constraint_gate.json",
    )
    link_checks = {path: path in addendum_text for path in linked_paths}
    addendum_pass = all(marker_checks.values()) and all(link_checks.values())

    ontology_pass = all(
        (
            "Trace `R` remains derived and has no backreaction."
            in addendum_normalized,
            "`Phi` is not promoted to a metric tensor" in addendum_normalized,
            "signed O(2) charge" in addendum_normalized,
            "equation of state" in addendum_normalized,
        )
    )
    global_boundary_pass = all(
        (
            gr["global_universe_closure"] == "UNRESOLVED",
            topic_0_19["global_universe_closure"] == "UNRESOLVED",
            "This does not prove that the complete universe is open or closed."
            in addendum_normalized,
        )
    )

    hard_fail = not all(
        (
            base_scope_pass,
            gr_scope_pass,
            downstream_pass,
            addendum_pass,
            ontology_pass,
            global_boundary_pass,
        )
    )
    status = "BLOCKED" if hard_fail else "WARN"
    alignment_status = (
        "BLOCKED_ADDENDUM_OR_INPUT_ALIGNMENT_FAILED"
        if hard_fail
        else "PASS_WITH_HISTORICAL_BASE_REPORT_WARN"
    )

    return {
        "schema_version": "1.0",
        "artifact": "matter_space_report_alignment_gate",
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "source_snapshot_at": _generated_at(inputs.values()),
        "status": status,
        "alignment_status": alignment_status,
        "evidence_status": "POST_WAVE10_ADDENDUM_ALIGNED_BASE_SNAPSHOT_RETAINED",
        "claim_class": "B_MODEL_AND_INTERNAL_DEPENDENCY_SUMMARY",
        "controlling_blocker": GR_CONTROLLER,
        "base_matter_space_controller": BASE_MATTER_CONTROLLER,
        "global_universe_closure": gr["global_universe_closure"],
        "report_status_impact": "NONE",
        "input_artifacts": {
            name: _json_record(INPUT_PATHS[name], payload)
            for name, payload in inputs.items()
        },
        "input_documents": {
            "base_report": _document_record(BASE_REPORT_PATH),
            "addendum": _document_record(ADDENDUM_PATH),
            "topic_readiness": _document_record(TOPIC_READINESS_PATH),
        },
        "canonical_topics": canonical,
        "gates": {
            "base_report_scope_gate": {
                "status": "PASS" if base_scope_pass else "FAIL",
                "snapshot": report_snapshot,
                "scope": "normalized one-dimensional matter-space program",
                "controller": matter["controlling_blocker"],
            },
            "post_wave10_addendum_gate": {
                "status": "PASS" if addendum_pass else "FAIL",
                "required_markers": marker_checks,
                "required_links": link_checks,
            },
            "gr_null_vs_global_closure_gate": {
                "status": "PASS" if global_boundary_pass and gr_scope_pass else "FAIL",
                "gr_null_model": gr["gr_null_model"],
                "global_universe_closure": gr["global_universe_closure"],
                "interpretation": "A passing epsilon_nc=0 response-null is a nested model limit, not a theorem about global universe closure.",
            },
            "controller_separation_gate": {
                "status": "PASS"
                if matter["controlling_blocker"] == BASE_MATTER_CONTROLLER
                and gr["controlling_blocker"] == GR_CONTROLLER
                and BASE_MATTER_CONTROLLER != GR_CONTROLLER
                else "FAIL",
                "matter_space_controller": matter["controlling_blocker"],
                "extended_gr_controller": gr["controlling_blocker"],
            },
            "topic_0_11_historical_status_gate": {
                "status": "WARN" if topic_status_drift else "FAIL",
                "drift_detected": topic_status_drift,
                "historical_report_status": "Draft",
                "canonical_status": canonical["0.11"]["status"],
                "canonical_tier": canonical["0.11"]["tier"],
                "repair": "The addendum controls post-Wave-9 status; the base report is retained as a dated snapshot.",
            },
            "downstream_dependency_gate": {
                "status": "PASS" if downstream_pass else "FAIL",
                "topic_0_11": {
                    "status": topic_0_11["status"],
                    "evidence_status": topic_0_11["evidence_status"],
                    "topic_status_impact": topic_0_11["topic_status_impact"],
                },
                "topic_0_19": {
                    "status": topic_0_19["status"],
                    "evidence_status": topic_0_19["evidence_status"],
                    "topic_status_impact": topic_0_19["topic_status_impact"],
                },
                "topic_0_13": {
                    "status": topic_0_13["status"],
                    "evidence_status": topic_0_13["evidence_status"],
                    "topic_status_impact": topic_0_13["topic_status_impact"],
                },
            },
            "ontology_separation_gate": {
                "status": "PASS" if ontology_pass else "FAIL",
                "trace_backreaction": False,
                "phi_metric_identity": False,
                "coarse_variable": "normalized signed O(2) charge coordinate",
                "equation_of_state_derived": False,
            },
            "claim_boundary_gate": {
                "status": "PASS" if addendum_pass and global_boundary_pass else "FAIL",
                "allowed": [
                    "historical matter-space report for its declared normalized 1D scope",
                    "candidate covariant GR parent and exact response-null model limit",
                    "partial fixed-scale Noether-charge coordinate map",
                    "dependency-only Topic 0.11, 0.19, and 0.13 summaries",
                ],
                "blocked": [
                    "the complete universe is proved open or closed",
                    "Einstein equations are derived from or validated by UET",
                    "the Noether coordinate map derives an equation of state or microscopic inverse",
                    "Phi is established spacetime geometry, a metric tensor, antimatter, or a particle",
                    "R is an independent field, substance, or feedback source",
                    "downstream topic promotion or external validation",
                ],
            },
        },
        "drift_table": [
            {
                "source": _relative(BASE_REPORT_PATH),
                "statement": "Topic 0.11 remains Draft/Tier B.",
                "conflict": "Canonical metadata and the 0.11 dependency gate now report Structured/Tier B.",
                "controlling_state": "Structured / Tier B",
                "repair_order": 1,
                "repair": "Use the dated addendum for current status; retain the base report as historical evidence.",
            },
            {
                "source": _relative(BASE_REPORT_PATH),
                "statement": "A geometry or Lorentz-covariant derivation is absent.",
                "conflict": "A class-B candidate covariant parent, exact response-null branch, restricted causal sector, partial response reduction, and Noether coordinate map now exist.",
                "controlling_state": gr["program_stage"],
                "repair_order": 2,
                "repair": "Replace the all-or-nothing absence statement with candidate-parent-present / physical-completion-blocked wording in the addendum.",
            },
            {
                "source": _relative(BASE_REPORT_PATH),
                "statement": "Topic 0.13 is represented only by the earlier thermal pilot.",
                "conflict": "A later constraint gate permits class-C thermodynamic constraints while keeping UET bridge closure blocked.",
                "controlling_state": topic_0_13["evidence_status"],
                "repair_order": 3,
                "repair": "Add the constraint-only dependency boundary without modifying the historical thermal result.",
            },
        ],
        "required_next_evidence": [
            "derive the signed-charge equation of state from the declared covariant matter theory or reject that identification",
            "specify covariant coarse-graining, susceptibility, and transport matching",
            "close entropy-current and dissipative-Bianchi accounting",
            "build a curved 3+1 well-posed solver and physical GR benchmark suite",
            "retain the independent matter-space pre-arrival leakage blocker for the normalized 1D physical-response lane",
        ],
        "next_controller": GR_CONTROLLER,
        "notes": [
            "The addendum repairs report usability without rewriting the user-owned historical report.",
            "The matter-space and extended-GR controllers are simultaneous scope-specific blockers, not competing global truth labels.",
            "No topic readiness status is promoted by this alignment artifact.",
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return nonzero only when report/addendum alignment is blocked",
    )
    args = parser.parse_args()
    artifact = build_alignment_gate()
    write_json(OUTPUT_PATH, artifact)
    if args.print_summary:
        print(
            json.dumps(
                {
                    "status": artifact["status"],
                    "alignment_status": artifact["alignment_status"],
                    "base_matter_space_controller": artifact[
                        "base_matter_space_controller"
                    ],
                    "extended_gr_controller": artifact["controlling_blocker"],
                    "global_universe_closure": artifact[
                        "global_universe_closure"
                    ],
                    "gates": {
                        name: gate["status"]
                        for name, gate in artifact["gates"].items()
                    },
                },
                indent=2,
            )
        )
    return 2 if args.strict and artifact["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
