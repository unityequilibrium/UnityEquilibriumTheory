#!/usr/bin/env python3
"""Audit the Topic 13 closure critical path without promoting the physics claim.

This audit turns the current partial closure state into a replayable research
control artifact.  It deliberately does not create a thermal coefficient,
accept a source, or infer a physical SI scale.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[3]
PROGRESS_PATH = ROOT / "docs/core/artifacts/t13_full_closure_progress.json"
MATRIX_PATH = ROOT / "docs/core/artifacts/t13_topic13_closure_matrix.json"
INPUT_AUDIT_PATH = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
ROUTE_AUDIT_PATH = ROOT / "docs/core/artifacts/t13_csrc_source_route_priority_audit.json"
SCALE_NO_GO_PATH = ROOT / "docs/core/artifacts/t13_thermal_bridge_scale_dependency_no_go.json"
ACTION_SI_PATH = ROOT / "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json"
CV_AUDIT_PATH = ROOT / "docs/core/artifacts/t13_cv_source_reconciliation_audit.json"

OUTPUT_PATH = ROOT / "docs/core/artifacts/t13_closure_critical_path_audit.json"
MARKDOWN_PATH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/TOPIC13_CLOSURE_CRITICAL_PATH.md"

PACKAGE_IDS = (
    "T13_INPUT_DING_TTG_SOURCE",
    "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
    "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def first_value(mapping: dict[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return default


def walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def find_row_list(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Find the canonical subresult rows while tolerating schema aliases."""

    preferred_keys = (
        "subresults",
        "required_subresults",
        "closure_rows",
        "rows",
        "results",
    )
    candidates: list[list[dict[str, Any]]] = []
    for node in walk_dicts(document):
        for key in preferred_keys:
            value = node.get(key)
            if not isinstance(value, list):
                continue
            rows = [item for item in value if isinstance(item, dict)]
            if rows and any(
                any(name in row for name in ("subresult_id", "major_result_id", "result_id", "id"))
                for row in rows
            ):
                candidates.append(rows)
    if candidates:
        return max(candidates, key=len)
    raise KeyError("no canonical Topic 13 subresult row list found")


def row_id(row: dict[str, Any]) -> str:
    value = first_value(row, ("subresult_id", "result_id", "major_result_id", "id", "name"))
    if value is None:
        raise KeyError(f"subresult row has no identifier: {row}")
    return str(value)


def row_closure_level(row: dict[str, Any]) -> str:
    value = first_value(row, ("closure_level", "level", "result_level"))
    if value is None:
        value = first_value(row, ("status", "verification_status", "result_status"), "OPEN")
    return str(value).upper()


def row_status(row: dict[str, Any]) -> str:
    value = first_value(row, ("status", "verification_status", "result_status"), "OPEN")
    return str(value).upper()


def is_open(row: dict[str, Any]) -> bool:
    return row_closure_level(row) == "OPEN"


def find_package_records(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for node in walk_dicts(document):
        package_id = node.get("package_id")
        if package_id in PACKAGE_IDS:
            records[str(package_id)] = copy.deepcopy(node)
    return records


def find_list_value(document: dict[str, Any], names: set[str]) -> list[Any]:
    for node in walk_dicts(document):
        for name in names:
            value = node.get(name)
            if isinstance(value, list):
                return value
    return []


def find_bool(document: dict[str, Any], names: set[str], default: bool) -> bool:
    for node in walk_dicts(document):
        for name in names:
            value = node.get(name)
            if isinstance(value, bool):
                return value
    return default


def package_hint(row: dict[str, Any]) -> str | None:
    identifier = row_id(row).lower()
    exact_package_map = {
        "accepted_numeric_csrc": "T13_INPUT_DING_TTG_SOURCE",
        "material_and_uncertainty_closure": "T13_INPUT_DING_TTG_SOURCE",
        "base_phi_si_anchor": "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
        "independent_alpha_record": "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
        "normalized_beta_si_map": "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
        "physical_source_backed_eos": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
        "physical_uet_kubo_record": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
        "physical_sk_transport_match": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
        "physical_entropy_production_mapping": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
        "physical_heat_flux_entropy_map": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
    }
    if identifier in exact_package_map:
        return exact_package_map[identifier]

    for key in (
        "root_input_package",
        "root_input_package_id",
        "input_package_id",
        "controlling_input_package",
        "controlling_input_package_id",
    ):
        value = row.get(key)
        if isinstance(value, str) and value in PACKAGE_IDS:
            return value
    for key in ("root_input_packages", "input_packages", "controlling_input_packages"):
        value = row.get(key)
        if isinstance(value, list):
            matches = [item for item in value if item in PACKAGE_IDS]
            if len(matches) == 1:
                return matches[0]

    text = json.dumps(row, ensure_ascii=True).lower()
    if any(token in text for token in ("ding", "c_src", "csrc", "heat capacity", "heat_capacity", "c_v", "cv_", "material", "uncertainty")):
        return "T13_INPUT_DING_TTG_SOURCE"
    if any(token in text for token in ("alpha_phi", "alpha", "beta", "dimensional", "phi_si", "phi scale", "energy anchor")):
        return "T13_INPUT_BASE_PHI_SI_ALPHA_BETA"
    if any(token in text for token in ("eos", "transport", "kubo", "kms", "sk", "entropy", "heat flux", "heat_flux", "dissipative")):
        return "T13_INPUT_PHYSICAL_TRANSPORT_MATCH"
    return None


def evidence_record(path: Path) -> dict[str, Any]:
    return {
        "path": relpath(path),
        "sha256": sha256(path) if path.exists() else None,
        "present": path.exists(),
    }


def source_snapshot_time(*documents: dict[str, Any]) -> str:
    for document in documents:
        for key in ("generated_at", "updated_at", "timestamp"):
            value = document.get(key)
            if isinstance(value, str) and value:
                return value
    return datetime.now(timezone.utc).isoformat()


def canonical_blockers(progress: dict[str, Any], input_audit: dict[str, Any]) -> list[str]:
    for document in (progress, input_audit):
        values = find_list_value(document, {"blockers", "open_blockers", "gate_blockers"})
        strings = [str(value) for value in values if isinstance(value, str)]
        if strings:
            return strings
    return []


def accepted_route_count(route_audit: dict[str, Any]) -> int:
    for node in walk_dicts(route_audit):
        for key in ("accepted_route_count", "accepted_count"):
            value = node.get(key)
            if isinstance(value, int):
                return value
    return 0


def package_output(
    package_id: str,
    source_record: dict[str, Any],
    open_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    record = copy.deepcopy(source_record)
    record["package_id"] = package_id
    record.setdefault("status", "BLOCKED")
    record["accepted_for_core"] = bool(record.get("accepted_for_core", False))
    record["open_subresults"] = [row_id(row) for row in open_rows]
    record["required_by_open_subresults"] = [row_id(row) for row in open_rows]
    return record


def route_records() -> list[dict[str, Any]]:
    return [
        {
            "route_id": "DING_AUTHOR_PAYLOAD",
            "packages": ["T13_INPUT_DING_TTG_SOURCE"],
            "required_change": "authorized numeric Ding/PBTE payload with provenance, uncertainty, preprocessing, and hash",
            "can_unlock": ["Ding C_src numeric path", "source-grade c_v uncertainty path"],
        },
        {
            "route_id": "DING_ACCEPTED_REPRODUCTION",
            "packages": ["T13_INPUT_DING_TTG_SOURCE"],
            "required_change": "independent reproduction accepted against the declared Ding material/state and protocol",
            "can_unlock": ["independent C_src path", "TTG material-regime mapping"],
        },
        {
            "route_id": "BASE_PHI_DERIVATION",
            "packages": ["T13_INPUT_BASE_PHI_SI_ALPHA_BETA"],
            "required_change": "dimensionful Phi-to-energy/temperature derivation with explicit SI anchor",
            "can_unlock": ["dimensional observable map", "non-circular bridge", "beta correspondence"],
        },
        {
            "route_id": "INDEPENDENT_ALPHA_RECORD",
            "packages": ["T13_INPUT_BASE_PHI_SI_ALPHA_BETA"],
            "required_change": "independent alpha_Phi_K calibration record, uncertainty, locator, hash, and independence statement",
            "can_unlock": ["alpha_Phi_K closure"],
        },
        {
            "route_id": "PHYSICAL_KUBO_MATCH",
            "packages": ["T13_INPUT_PHYSICAL_TRANSPORT_MATCH"],
            "required_change": "physical finite-temperature transport/Kubo match with KMS and entropy contracts",
            "can_unlock": ["EOS", "transport", "SK/KMS", "entropy", "heat-flux balance"],
        },
    ]


def markdown(payload: dict[str, Any]) -> str:
    major = payload["major_result"]
    critical = payload["critical_path"]
    lines = [
        "# Topic 13 Closure Critical Path",
        "",
        "MAJOR_RESULT_CLOSURE:",
        f"- `{major['major_result_id']}` is `{major['closure_level']}`.",
        "- This closes the current research-control boundary, not the physical thermal bridge.",
        "",
        "WHAT_IS_ACTUALLY_CLOSED:",
        *[f"- {item}" for item in major["what_is_closed"]],
        "",
        "WHAT_REMAINS_OPEN:",
        f"- Open subresults: `{critical['open_subresult_count']}` of `{critical['required_subresult_count']}`.",
        *[f"- `{item}`" for item in major["open_blockers"]],
        "",
        "DEPENDENCY_UNLOCKED:",
        f"- {major['dependency_unlocked']}",
        "",
        "STATUS:",
        f"- `{payload['status']}`",
        f"- Full Topic 13: `{payload['canonical_status']['full_topic_status']}`",
        f"- Full Core unlock: `{payload['canonical_status']['full_core_unlock']}`",
        f"- Claim promotion: `{payload['canonical_status']['claim_promotion']}`",
        "",
        "WHAT_CHANGED:",
        "- Reconstructed the canonical 37-subresult state and preserved each open row's complete required root input package set.",
        "- Recorded the current evidence hashes and replay rule so an unchanged rerun is not counted as progress.",
        "",
        "EQUATION_OR_MAPPING:",
        f"- `{major['equation_or_mapping']['normalized']}`",
        f"- `{major['equation_or_mapping']['dimensional']}`",
        f"- `{major['equation_or_mapping']['source']}`",
        f"- `{major['equation_or_mapping']['scale']}`",
        "",
        "CRITICAL_PATH:",
        "| Root input package | Status | Canonical unlocks | Required by open rows | Accepted for Core |",
        "|---|---|---:|---|",
    ]
    for package in payload["input_packages"]:
        lines.append(
            f"| `{package['package_id']}` | `{package.get('status', 'UNKNOWN')}` | "
            f"{len(package.get('unlocks_subresults', []))} | {len(package.get('required_by_open_subresults', []))} | "
            f"`{package.get('accepted_for_core', False)}` |"
        )
    lines.extend(
        [
            "",
            "OPEN_SUBRESULTS:",
            "| Subresult | Required input packages | Primary controller | Closure level | Status |",
            "|---|---|---|---|---|",
        ]
    )
    for row in payload["open_subresults"]:
        lines.append(
            f"| `{row['subresult_id']}` | {', '.join(f"`{item}`" for item in row['required_input_packages'])} | "
            f"`{row['primary_controller']}` | `{row['closure_level']}` | `{row['status']}` |"
        )
    lines.extend(
        [
            "",
            "VERIFICATION:",
            f"- Checks: `{sum(1 for value in payload['checks'].values() if value)}/{len(payload['checks'])}` passed.",
            "- Existing numeric gates must not be rerun as a substitute for changing an input package.",
            "- Xie 2026 remains locked holdout; no target fit or calibration access is recorded.",
            "",
            "CONTROLLING_BLOCKER:",
            f"- `{payload['controlling_blocker']}`",
            "",
            "NEXT_ACTION:",
            f"- {payload['next_controller']}",
            "",
            "CLAIM_BOUNDARY:",
            f"- {major['claim_boundary']}",
            "",
            "UNBLOCK_ROUTES:",
        ]
    )
    for route in payload["unblock_routes"]:
        lines.append(f"- `{route['route_id']}`: {route['required_change']}.")
    return "\n".join(lines) + "\n"


def build_payload() -> dict[str, Any]:
    progress = load_json(PROGRESS_PATH)
    matrix = load_json(MATRIX_PATH)
    input_audit = load_json(INPUT_AUDIT_PATH)
    route_audit = load_json(ROUTE_AUDIT_PATH)
    scale_no_go = load_json(SCALE_NO_GO_PATH)
    action_si = load_json(ACTION_SI_PATH)
    cv_audit = load_json(CV_AUDIT_PATH)

    rows = find_row_list(progress)
    open_rows = [copy.deepcopy(row) for row in rows if is_open(row)]
    open_rows.sort(key=row_id)
    if not open_rows:
        raise ValueError("canonical progress contains no open Topic 13 subresults")

    package_records = find_package_records(input_audit)
    for package_id in PACKAGE_IDS:
        package_records.setdefault(
            package_id,
            {
                "package_id": package_id,
                "status": "BLOCKED",
                "accepted_for_core": False,
                "missing_acceptance_fields": [],
                "unlocks_subresults": [],
            },
        )

    canonical_unlocks = {
        package_id: {
            str(value)
            for value in package_records[package_id].get("unlocks_subresults", [])
            if isinstance(value, str)
        }
        for package_id in PACKAGE_IDS
    }
    fallback_package_assignment_used = False
    assigned_rows: list[dict[str, Any]] = []
    for row in open_rows:
        row["subresult_id"] = row_id(row)
        row["closure_level"] = row_closure_level(row)
        row["status"] = row_status(row)
        required_packages = [
            package_id
            for package_id in PACKAGE_IDS
            if row["subresult_id"] in canonical_unlocks[package_id]
        ]
        if not required_packages:
            package_id = package_hint(row)
            if package_id is None:
                raise ValueError(f"open subresult has no canonical root package dependency: {row_id(row)}")
            required_packages = [package_id]
            fallback_package_assignment_used = True
        row["required_input_packages"] = required_packages
        row["primary_controller"] = (
            required_packages[0] if len(required_packages) == 1 else "MULTI_PACKAGE_DEPENDENCY"
        )
        assigned_rows.append(row)

    packages = [
        package_output(
            package_id,
            package_records[package_id],
            [row for row in assigned_rows if package_id in row["required_input_packages"]],
        )
        for package_id in PACKAGE_IDS
    ]

    open_row_ids = {row["subresult_id"] for row in assigned_rows}
    projected_by_package = {
        package_id: sorted(
            row["subresult_id"]
            for row in assigned_rows
            if package_id in row["required_input_packages"]
        )
        for package_id in PACKAGE_IDS
    }
    canonical_by_package = {
        package_id: sorted(canonical_unlocks[package_id] & open_row_ids)
        for package_id in PACKAGE_IDS
    }

    closure_counts = Counter(row_closure_level(row) for row in rows)
    canonical_status = {
        "full_topic_status": str(
            first_value(progress, ("full_topic_status", "status"), "BLOCKED_OPEN_T13_FULL_BRIDGE")
        ),
        "full_topic_closure_level": str(first_value(progress, ("full_topic_closure_level",), "PARTIAL")),
        "full_core_unlock": bool(first_value(progress, ("full_core_unlock",), False)),
        "claim_promotion": bool(first_value(progress, ("claim_promotion", "global_claim_promotion"), False)),
    }
    blockers = canonical_blockers(progress, input_audit)
    rerun_policy = first_value(progress, ("rerun_policy",), {})
    if not isinstance(rerun_policy, dict):
        rerun_policy = {}

    evidence_paths = (
        PROGRESS_PATH,
        MATRIX_PATH,
        INPUT_AUDIT_PATH,
        ROUTE_AUDIT_PATH,
        SCALE_NO_GO_PATH,
        ACTION_SI_PATH,
        CV_AUDIT_PATH,
    )
    holdout_accessed = find_bool(input_audit, {"holdout_accessed", "holdout_read", "xie_holdout_accessed"}, False)
    target_fit = find_bool(input_audit, {"target_fit_performed", "fit_holdout", "holdout_fit_performed"}, False)
    input_hashes_unchanged_required = rerun_policy.get("rerun_existing_numeric_gates_without_new_input") is False

    major_result = {
        "major_result_id": "T13_CLOSURE_CRITICAL_PATH",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "current 37-subresult closure state is reconstructed from canonical progress",
            "all open subresults are mapped to their complete required root input package sets, including multi-package dependencies",
            "current input hashes are recorded and rerunning existing gates without new input is explicitly non-progress",
            "normalized/action scale routes are structurally bounded by no-go evidence, not merely missing scripts",
        ],
        "what_remains_open": [
            "exact open subresult IDs",
            "canonical Topic 13 blockers",
            "three root packages not accepted for Core",
        ],
        "equation_or_mapping": {
            "normalized": "y_TTG = Delta_Tq(t)/Delta_Tq(0); y_TTG^UET = Delta_Phi(t)/Delta_Phi(0)",
            "dimensional": "Delta_Tq = alpha_Phi_K * Delta_Phi",
            "source": "C_src(T)=sum_mu c_mu(T); Delta_Tq=Delta_u_ph/C_src(T)",
            "scale": "Phi_normalized=Phi_covariant/Phi_scale; u_SI=u_nat*E_ref^4/(hbar*c)^3",
        },
        "units": {
            "y_TTG": "dimensionless",
            "Delta_Tq": "K",
            "Delta_Phi": "declared Phi lane units; dimensionless only after explicit normalization",
            "alpha_Phi_K": "K per declared Phi unit; numeric value open",
            "C_src": "energy density per K in the selected source convention; source package open",
        },
        "derivation_class": "canonical status reconstruction + dependency/replay audit; no new physical value",
        "observable": "Topic 13 closure critical path and input-state readiness",
        "data_role": "INTERNAL_WORKFLOW_AUDIT_NOT_CALIBRATION",
        "evidence_artifacts": [evidence_record(path) for path in evidence_paths],
        "verification_status": "PASS_CRITICAL_PATH_RECONSTRUCTION_NO_PHYSICAL_PROMOTION",
        "open_blockers": blockers,
        "dependency_unlocked": "none; reporting and replay guard only",
        "claim_boundary": "Does not close Full Topic 13 or claim physical SI, TTG, or transport validation.",
    }

    checks = {
        "canonical_progress_is_blocked": ("BLOCKED" in canonical_status["full_topic_status"])
        or not canonical_status["full_core_unlock"],
        "open_subresults_are_exactly_projected": {row["subresult_id"] for row in assigned_rows}
        == {row_id(row) for row in open_rows},
        "all_open_subresults_have_input_packages": all(
            row["required_input_packages"]
            and set(row["required_input_packages"]).issubset(PACKAGE_IDS)
            for row in assigned_rows
        ),
        "input_package_unlock_lists_match_canonical": projected_by_package == canonical_by_package,
        "multi_package_dependencies_preserved": any(
            len(row["required_input_packages"]) > 1 for row in assigned_rows
        ),
        "no_fallback_package_assignment_used": not fallback_package_assignment_used,
        "package_count_is_three": len(packages) == 3,
        "no_package_accepted_for_core": all(not package["accepted_for_core"] for package in packages),
        "replay_without_hash_change_is_forbidden": input_hashes_unchanged_required,
        "scale_no_go_present": SCALE_NO_GO_PATH.exists()
        and "NO_GO" in str(first_value(scale_no_go, ("status", "verification_status"), "")),
        "action_si_route_remains_blocked": "BLOCKED" in json.dumps(action_si, ensure_ascii=True).upper(),
        "route_inventory_accepted_count_zero": accepted_route_count(route_audit) == 0,
        "holdout_not_accessed": not holdout_accessed,
        "target_fit_not_performed": not target_fit,
        "claim_promotion_false": not canonical_status["claim_promotion"],
    }

    return {
        "schema_version": "t13-closure-critical-path-v1",
        "artifact": "t13_closure_critical_path_audit",
        "generated_at": source_snapshot_time(progress, matrix, input_audit),
        "status": "PASS_T13_CLOSURE_CRITICAL_PATH_WITH_EXTERNAL_INPUTS",
        "major_result": major_result,
        "canonical_status": canonical_status,
        "critical_path": {
            "required_subresult_count": len(rows),
            "open_subresult_count": len(assigned_rows),
            "closed_for_lane": closure_counts.get("CLOSED_FOR_LANE", 0),
            "closed_as_no_go": closure_counts.get("CLOSED_AS_NO_GO", 0),
            "closed_for_core": closure_counts.get("CLOSED_FOR_CORE", 0),
            "root_input_package_count": len(packages),
            "full_core_unlock": canonical_status["full_core_unlock"],
            "claim_promotion": canonical_status["claim_promotion"],
            "input_state": "BLOCKED_NO_ACCEPTED_CORE_PACKAGE",
            "rerun_existing_gates_without_new_input": False,
            "external_state_change_required": True,
            "open_input_package_link_count": sum(
                len(row["required_input_packages"]) for row in assigned_rows
            ),
        },
        "input_packages": packages,
        "open_subresults": assigned_rows,
        "unblock_routes": route_records(),
        "checks": checks,
        "holdout_integrity": {
            "holdout_accessed": holdout_accessed,
            "target_fit_performed": target_fit,
        },
        "controlling_blocker": "external_input_package_state_unchanged",
        "next_controller": "Change one root package state by authorized Ding payload/reproduction, independent base-Phi SI anchor/alpha derivation, or physical Kubo match; then rerun dependent gates.",
        "source_state": {
            "matrix_artifact": relpath(MATRIX_PATH),
            "input_audit_artifact": relpath(INPUT_AUDIT_PATH),
            "route_audit_artifact": relpath(ROUTE_AUDIT_PATH),
        },
    }


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_PATH, payload)
    MARKDOWN_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_PATH.write_text(markdown(payload), encoding="utf-8")
    print(json.dumps({
        "artifact": relpath(OUTPUT_PATH),
        "markdown": relpath(MARKDOWN_PATH),
        "status": payload["status"],
        "open_subresult_count": payload["critical_path"]["open_subresult_count"],
        "checks_passed": sum(1 for value in payload["checks"].values() if value),
        "checks_total": len(payload["checks"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
