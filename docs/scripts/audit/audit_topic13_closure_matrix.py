"""Build a compact, machine-readable Topic 13 closure matrix.

The full Topic 13 gate remains the authority for readiness.  This artifact is
only a reporting projection: it makes the major research requirements and
their current closure boundaries readable without counting a lane-level PASS
as Full Topic 13 closure.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
GATE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"
OUT_REL = "docs/core/artifacts/t13_topic13_closure_matrix.json"


REQUIREMENTS: tuple[dict[str, Any], ...] = (
    {
        "requirement_id": "causal_structure",
        "label": "Causal thermal branch",
        "gate_key": "causal_full_candidate_or_formal_no_go_branch",
        "closure_level": "CLOSED_AS_NO_GO",
        "what_is_closed": (
            "The finite-cone compatibility question is closed as a scoped "
            "no-go for the declared local conserved-C gradient class. The "
            "named coupled conserved-flux/Phi branch is retained separately "
            "with its own causal checks."
        ),
        "what_remains_open": (
            "The original conserved-C full-candidate baseline remains blocked; "
            "the named branch does not replace it."
        ),
        "dependency_unlocked": "Named causal branch only; no Full Topic 13 or downstream unlock.",
    },
    {
        "requirement_id": "dimensional_phi_to_thermal_observable_map",
        "label": "Dimensional Phi-to-thermal observable map",
        "gate_key": "dimensional_observable_map",
        "closure_level": "OPEN",
        "what_is_closed": (
            "The normalized measurement operator and the conditional dimensional "
            "operator are explicitly separated."
        ),
        "what_remains_open": (
            "A physical base-Phi-to-energy/temperature map with a declared SI "
            "anchor is not identified."
        ),
        "dependency_unlocked": "None.",
    },
    {
        "requirement_id": "independent_alpha_Phi_K",
        "label": "Independent alpha_Phi_K",
        "gate_key": "alpha_Phi_K",
        "closure_level": "OPEN",
        "what_is_closed": (
            "The candidate search and anti-fitting acceptance contract are closed; "
            "no eligible paired record was found."
        ),
        "what_remains_open": (
            "An independent base-Phi amplitude paired with an SI thermal/energy "
            "response and uncertainty required for alpha_Phi_K is missing."
        ),
        "dependency_unlocked": "None; the Xie 2026 holdout remains locked.",
    },
    {
        "requirement_id": "beta_and_si_correspondence",
        "label": "Beta and SI correspondence",
        "gate_key": "non_circular_bridge",
        "closure_level": "PARTIAL",
        "what_is_closed": (
            "A non-Landauer action-origin natural-unit stiffness slope and a "
            "formal finite-temperature beta contract are recorded."
        ),
        "what_remains_open": (
            "The normalized beta_T13, energy reference, field normalization, and "
            "SI coefficient provenance are not identified."
        ),
        "dependency_unlocked": "Natural-unit/formal beta lanes only; no SI unlock.",
    },
    {
        "requirement_id": "charge_density_eos",
        "label": "Charge-density EOS",
        "gate_key": "collective_response_eos_stability_contract",
        "closure_level": "PARTIAL",
        "what_is_closed": (
            "The candidate normalized EOS, reciprocity, and local stability "
            "contract are machine-checked."
        ),
        "what_remains_open": (
            "A source-backed physical charge-density EOS and finite-temperature "
            "coefficient provenance are not closed."
        ),
        "dependency_unlocked": "Candidate normalized EOS lane only.",
    },
    {
        "requirement_id": "covariant_thermal_transport",
        "label": "Covariant thermal transport",
        "gate_key": "eos_transport_kms_entropy",
        "closure_level": "PARTIAL",
        "what_is_closed": (
            "Finite-cutoff natural-unit heat-current, entropy, and conservation "
            "interfaces are connected."
        ),
        "what_remains_open": (
            "A physical Kubo coefficient, complete finite-temperature normal/two-fluid "
            "sector, and stable continuum promotion are missing."
        ),
        "dependency_unlocked": "Formal/natural transport interface only.",
    },
    {
        "requirement_id": "sk_kms_matching",
        "label": "SK/KMS matching",
        "gate_key": "eos_transport_kms_entropy",
        "closure_level": "PARTIAL",
        "what_is_closed": (
            "The formal local SK/KMS/FDT interface and finite-cutoff action-matched "
            "lane are explicit."
        ),
        "what_remains_open": (
            "Microscopic interacting all-channel matching and physical transport "
            "provenance remain open."
        ),
        "dependency_unlocked": "Formal SK/KMS interface only.",
    },
    {
        "requirement_id": "entropy_current_and_dissipative_balance",
        "label": "Entropy current and dissipative balance",
        "gate_key": "eos_transport_kms_entropy",
        "closure_level": "PARTIAL",
        "what_is_closed": (
            "The formal entropy-current positivity and conserved matter/UET "
            "exchange interface are recorded."
        ),
        "what_remains_open": (
            "Physical coefficient matching, SI normalization, and curved 3+1 "
            "transport closure remain open."
        ),
        "dependency_unlocked": "Formal balance interface only.",
    },
    {
        "requirement_id": "source_and_uncertainty",
        "label": "TTG source package and uncertainty",
        "gate_key": "source_package",
        "closure_level": "OPEN",
        "what_is_closed": (
            "Ding source identity, setup rows, incident fluence, source acceptance "
            "rules, and independent comparator provenance are archived."
        ),
        "what_remains_open": (
            "A permitted Ding numeric C_src payload or accepted same-regime PBTE "
            "reproduction with material/state, convergence, and source-grade "
            "uncertainty is missing."
        ),
        "dependency_unlocked": "Source acceptance policy only.",
    },
)


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_ref(relative: str, summary: dict[str, Any] | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"path": relative, "sha256": sha256(relative)}
    if summary:
        value["summary"] = summary
    return value


def status_evidence(section: dict[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    seen: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            path = value.get("path")
            if isinstance(path, str) and path.endswith(".json"):
                candidate = ROOT / path
                if candidate.is_file() and path not in seen:
                    refs.append(
                        {
                            "path": path,
                            "sha256": sha256(path),
                            "summary": {
                                "role": "gate-linked evidence",
                                "reported_sha256": value.get("sha256"),
                            },
                        }
                    )
                    seen.add(path)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(section)
    return refs[:8]


def build_requirement(gate: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    section = gate.get("verification_status", {}).get(spec["gate_key"], {})
    if not isinstance(section, dict):
        section = {"status": str(section)}
    closure_level = spec["closure_level"]
    if spec["requirement_id"] == "causal_structure":
        closure_level = section.get("structural_question_closure", closure_level)
    return {
        **spec,
        "closure_level": closure_level,
        "gate_status": section.get("status", "OPEN"),
        "gate_controlling_blocker": section.get("controlling_blocker"),
        "gate_lane_status": section.get("lane_status"),
        "gate_lane_closure_level": section.get("lane_closure_level"),
        "evidence_artifacts": status_evidence(section),
    }


def build_matrix() -> dict[str, Any]:
    gate = load_json(GATE_REL)
    summary = gate.get("major_result", {}).get("closure_summary", {})
    requirements = [build_requirement(gate, spec) for spec in REQUIREMENTS]
    open_blockers = list(gate.get("major_result", {}).get("what_remains_open", []))
    evidence = [
        artifact_ref(
            GATE_REL,
            {
                "role": "canonical full Topic 13 readiness gate",
                "status": gate.get("status"),
            },
        )
    ]
    for requirement in requirements:
        for ref in requirement["evidence_artifacts"]:
            if ref["path"] not in {item["path"] for item in evidence}:
                evidence.append(ref)

    major_result = {
        "major_result_id": "T13_TOPIC13_CLOSURE_MATRIX",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "PARTIAL",
        "what_is_closed": [
            "The nine required Topic 13 result areas are reported separately by closure level.",
            "Lane-level formal results are not counted as Full Topic 13 Core-ready closure.",
            "The current full-gate blocker groups and dependency state are projected without changing them.",
            "The normalized measurement operator remains separate from the dimensional thermal operator.",
        ],
        "equation_or_mapping": {
            "standard": gate.get("equation_or_mapping", {}).get("standard"),
            "uet_normalized": gate.get("equation_or_mapping", {}).get("uet_normalized"),
            "dimensional": gate.get("equation_or_mapping", {}).get("dimensional"),
            "formal_action_bridge": "Delta_Tq^nat = Delta_epsilon^nat / C_epsilon_T^nat",
            "formal_entropy_balance": "nabla_mu J_S^mu = q_perp^2/(kappa T^2) + X_A L^(AB) X_B >= 0",
            "source_response": "C_src(T) = sum_mu c_mu(T); Delta_Tq = Delta_u_ph / C_src(T)",
        },
        "units": {
            "y_TTG": "dimensionless",
            "y_TTG_UET": "dimensionless",
            "Delta_Tq": "K only after a physical source/scale map",
            "alpha_Phi_K": "K per normalized Phi; open",
            "C_src": "J m^-3 K^-1 when a qualifying source package exists",
            "formal_transport": "natural-unit or conditional interface; not SI physical transport",
        },
        "derivation_class": "machine-readable status reconstruction from canonical gate and lane evidence; no new physical derivation",
        "observable": "Topic 13 major-result closure state and dependency readiness",
        "data_role": "INTERNAL_CLOSURE_REPORT_NOT_CALIBRATION",
        "evidence_artifacts": evidence,
        "verification_status": "PASS_MACHINE_READABLE_CLOSURE_MATRIX_WITH_FULL_BRIDGE_BLOCKED",
        "open_blockers": open_blockers,
        "dependency_unlocked": "None for Full Topic 13; formal and source-acceptance lanes remain separately available.",
        "claim_boundary": "This matrix reports progress and closure boundaries. It does not promote a lane-level PASS, comparator, no-go, or formal interface to Full Topic 13, Core, external validation, or a global UET claim.",
    }
    matrix = {
        "schema_version": "t13-topic13-closure-matrix-v1",
        "artifact": "t13_topic13_closure_matrix",
        "generated_at": date.today().isoformat(),
        "status": "BLOCKED_OPEN_T13_FULL_BRIDGE",
        "claim_promotion": False,
        "full_core_unlock": False,
        "major_result": major_result,
        "requirements": requirements,
        "closure_summary": {
            "closed_lane_count": summary.get("closed_lane_count"),
            "closed_as_no_go_count": summary.get("closed_as_no_go_count"),
            "open_blocker_count": summary.get("open_blocker_count"),
            "open_blocker_groups": summary.get("open_blocker_groups", {}),
            "downstream_dependency_unlocked": summary.get("downstream_dependency_unlocked", False),
        },
        "canonical_gate": {
            "path": GATE_REL,
            "sha256": sha256(GATE_REL),
            "status": gate.get("status"),
            "controlling_blocker": gate.get("controlling_blocker"),
        },
        "holdout_policy": {
            "xie_2026_accessed": gate.get("verification_status", {})
            .get("holdout_integrity", {})
            .get("holdout_consumed", False),
            "target_fit_performed": False,
            "calibration_path_may_read_holdout": False,
        },
        "report": {
            "MAJOR_RESULT_CLOSURE": "PARTIAL",
            "WHAT_IS_ACTUALLY_CLOSED": major_result["what_is_closed"],
            "WHAT_REMAINS_OPEN": open_blockers,
            "DEPENDENCY_UNLOCKED": major_result["dependency_unlocked"],
            "STATUS": matrix_status(gate),
            "WHAT_CHANGED": "Added a compact projection of the canonical Topic 13 gate into nine major research requirements; no equation, threshold, source role, fit path, or holdout policy changed.",
            "EQUATION_OR_MAPPING": major_result["equation_or_mapping"],
            "VERIFICATION": "Canonical gate hash, blocker groups, lane statuses, evidence references, and holdout metadata were read and projected without consuming numeric holdout data.",
            "CONTROLLING_BLOCKER": gate.get("controlling_blocker"),
            "NEXT_ACTION": gate.get("next_action"),
            "CLAIM_BOUNDARY": major_result["claim_boundary"],
        },
    }
    return matrix


def matrix_status(gate: dict[str, Any]) -> str:
    return f"{gate.get('status', 'OPEN')}; full_core_unlock=False"


def sync_register_and_dependency(matrix: dict[str, Any]) -> None:
    matrix_hash = sha256(OUT_REL)
    register = load_json(REGISTER_REL)
    entry = matrix["major_result"].copy()
    entry["evidence_artifacts"] = [
        artifact_ref(OUT_REL, {"role": "compact Topic 13 closure projection"}),
        artifact_ref(GATE_REL, {"role": "canonical readiness gate"}),
    ]
    entry["closure_summary"] = matrix["closure_summary"]
    entry["claim_promotion"] = False
    entries = register.setdefault("entries", [])
    existing = next((item for item in entries if item.get("major_result_id") == entry["major_result_id"]), None)
    if existing is None:
        entries.append(entry)
    else:
        existing.clear()
        existing.update(entry)
    full_entry = next(item for item in entries if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    full_entry["closure_matrix"] = {
        "path": OUT_REL,
        "sha256": matrix_hash,
        "status": matrix["status"],
        "full_core_unlock": False,
    }
    register["generated_at"] = date.today().isoformat()
    register["claim_promotion"] = False
    register_path = ROOT / REGISTER_REL
    register_path.write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load_json(DEPENDENCY_REL)
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["closure_matrix"] = {
        "path": OUT_REL,
        "sha256": matrix_hash,
        "full_core_unlock": False,
        "status": matrix["status"],
    }
    register_hash = sha256(REGISTER_REL)
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = register_hash
    partial["register_sha256"] = register_hash
    partial["full_core_unlock"] = False
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    matrix = build_matrix()
    (ROOT / OUT_REL).write_text(json.dumps(matrix, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    sync_register_and_dependency(matrix)
    print(
        json.dumps(
            {
                "status": matrix["status"],
                "artifact": OUT_REL,
                "major_result_id": matrix["major_result"]["major_result_id"],
                "requirement_count": len(matrix["requirements"]),
                "open_blocker_count": matrix["closure_summary"]["open_blocker_count"],
                "full_core_unlock": matrix["full_core_unlock"],
                "holdout_accessed": matrix["holdout_policy"]["xie_2026_accessed"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
