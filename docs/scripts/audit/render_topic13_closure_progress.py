"""Render the canonical Topic 13 major-result and subresult status.

This is a reporting pass only. It reads the existing closure matrix, full gate,
and input-package audit; it never creates a calibration value or changes a gate.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MATRIX_REL = "docs/core/artifacts/t13_topic13_closure_matrix.json"
GATE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
INPUT_REL = "docs/core/artifacts/t13_closure_input_package_audit.json"
OUT_JSON_REL = "docs/core/artifacts/t13_full_closure_progress.json"
OUT_MD_REL = "docs/topics/0.13_Thermodynamic_Bridge/TOPIC13_FULL_CLOSURE_STATUS.md"


PACKAGE_BY_SUBRESULT = {
    "base_phi_si_anchor": "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
    "independent_alpha_record": "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
    "normalized_beta_si_map": "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
    "physical_source_backed_eos": "T13_INPUT_DING_TTG_SOURCE + T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
    "physical_uet_kubo_record": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
    "physical_sk_transport_match": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
    "physical_entropy_production_mapping": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
    "accepted_numeric_csrc": "T13_INPUT_DING_TTG_SOURCE",
    "material_and_uncertainty_closure": "T13_INPUT_DING_TTG_SOURCE",
    "physical_heat_flux_entropy_map": (
        "T13_INPUT_DING_TTG_SOURCE + T13_INPUT_BASE_PHI_SI_ALPHA_BETA + "
        "T13_INPUT_PHYSICAL_TRANSPORT_MATCH"
    ),
}

PACKAGE_IDS = (
    "T13_INPUT_DING_TTG_SOURCE",
    "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
    "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
)


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def subresult_record(major: dict[str, Any], subresult: dict[str, Any]) -> dict[str, Any]:
    subresult_id = subresult.get("subresult_id")
    package_label = PACKAGE_BY_SUBRESULT.get(subresult_id)
    package_ids = (
        [item.strip() for item in package_label.split("+")]
        if package_label
        else []
    )
    return {
        "major_result_id": major.get("major_result_id"),
        "label": subresult.get("label"),
        "subresult_id": subresult_id,
        "status": subresult.get("status", "OPEN"),
        "required_closure_level": subresult.get("required_closure_level"),
        "acceptance": subresult.get("acceptance"),
        "evidence_result_ids": subresult.get("evidence_result_ids", []),
        "controlling_input_package": package_label,
        "controlling_input_packages": package_ids,
    }


def build_payload() -> dict[str, Any]:
    matrix = load(MATRIX_REL)
    gate = load(GATE_REL)
    input_audit = load(INPUT_REL)

    major_results: list[dict[str, Any]] = []
    subresults: list[dict[str, Any]] = []
    for major in matrix.get("requirements", []):
        children = [subresult_record(major, item) for item in major.get("required_subresults", [])]
        counts = dict(Counter(item["status"] for item in children))
        major_results.append(
            {
                "major_result_id": major.get("major_result_id"),
                "label": major.get("label"),
                "closure_level": major.get("closure_level"),
                "gate_status": major.get("gate_status"),
                "required_subresult_count": len(children),
                "subresult_status_counts": counts,
                "open_subresults": [item["subresult_id"] for item in children if item["status"] == "OPEN"],
                "dependency_unlocked": major.get("dependency_unlocked"),
                "claim_boundary": major.get("claim_boundary"),
            }
        )
        subresults.extend(children)

    input_packages = []
    for package in input_audit.get("packages", []):
        package_id = package.get("package_id")
        open_for_package = [
            item["subresult_id"]
            for item in subresults
            if item["status"] == "OPEN"
            and package_id in item.get("controlling_input_packages", [])
        ]
        input_packages.append(
            {
                "package_id": package_id,
                "status": package.get("status"),
                "accepted_for_core": package.get("accepted_for_core", False),
                "missing_acceptance_fields": package.get("missing_acceptance_fields", []),
                "unlocks_subresults": package.get("unlocks_subresults", []),
                "open_subresults": open_for_package,
            }
        )

    source_hashes = {
        relative: digest(relative)
        for relative in (MATRIX_REL, GATE_REL, INPUT_REL)
    }
    counts = dict(Counter(item["status"] for item in subresults))
    open_subresults = [item for item in subresults if item["status"] == "OPEN"]
    closure_arithmetic = {
        "required_subresults": len(subresults),
        "closed_for_lane": counts.get("CLOSED_FOR_LANE", 0),
        "closed_as_no_go": counts.get("CLOSED_AS_NO_GO", 0),
        "closed_for_core": counts.get("CLOSED_FOR_CORE", 0),
        "open": counts.get("OPEN", 0),
        "root_input_packages": len(PACKAGE_IDS),
        "full_topic_core_ready_rule": (
            "all required subresults must be CLOSED_FOR_CORE or an explicitly "
            "accepted closure level in the canonical full gate; no OPEN "
            "subresult and all required input packages accepted"
        ),
    }
    return {
        "schema_version": "t13-full-closure-progress-v1",
        "artifact": "t13_full_closure_progress",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canonical_status": {
            "full_topic_status": gate.get("status"),
            "full_topic_closure_level": gate.get("major_result", {}).get("closure_level"),
            "claim_promotion": gate.get("claim_promotion", False),
            "full_core_unlock": matrix.get("full_core_unlock", False),
            "controlling_blocker": gate.get("controlling_blocker"),
        },
        "closure_counts": counts,
        "closure_arithmetic": closure_arithmetic,
        "required_major_result_count": len(major_results),
        "required_subresult_count": len(subresults),
        "major_results": major_results,
        "subresults": subresults,
        "open_subresults": open_subresults,
        "input_packages": input_packages,
        "dependency_unlock": {
            "causal_named_branch": "CLOSED_FOR_CORE as a bounded normalized branch",
            "full_topic_13": "LOCKED until all required subresults are closed at their declared level",
            "downstream_core_gravity_transport": "LOCKED",
        },
        "rerun_policy": {
            "rerun_existing_numeric_gates_without_new_input": False,
            "rerun_when_any_input_hash_changes": True,
            "required_external_state_change": [
                "authorized Ding-compatible C_src payload or accepted same-regime reproduction",
                "independent base-Phi SI anchor or dimensionful action anchor with alpha record",
                "state-matched physical Kubo coefficient and SK/KMS/entropy linkage",
            ],
        },
        "holdout_policy": input_audit.get("holdout_policy", {}),
        "source_hashes": source_hashes,
    }


def md_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def render_markdown(payload: dict[str, Any]) -> str:
    counts = payload["closure_counts"]
    arithmetic = payload["closure_arithmetic"]
    status = payload["canonical_status"]
    open_rows = payload["open_subresults"]
    lines = [
        "# Topic 13 Full Closure Status",
        "",
        "This file is generated from the canonical closure matrix and full gate. It is a status handoff, not a new scientific result.",
        "",
        "MAJOR_RESULT_CLOSURE:",
        f"- Full Topic 13: `{status['full_topic_closure_level']}`.",
        f"- Required subresults: `{payload['required_subresult_count']}`; `CLOSED_FOR_LANE={counts.get('CLOSED_FOR_LANE', 0)}`, `CLOSED_AS_NO_GO={counts.get('CLOSED_AS_NO_GO', 0)}`, `CLOSED_FOR_CORE={counts.get('CLOSED_FOR_CORE', 0)}`, `OPEN={counts.get('OPEN', 0)}`.",
        "",
        "WHAT_IS_ACTUALLY_CLOSED:",
        "- The named causal flux-Phi branch is `CLOSED_FOR_CORE` only as a bounded normalized branch; the original conserved-C baseline remains blocked/no-go.",
        "- Formal natural-unit bridge, EOS, SK/KMS, entropy, heat-current, source-boundary, and comparator lanes remain separated and machine-audited.",
        "- No input package is accepted for Full Topic 13 Core closure.",
        "",
        "WHAT_REMAINS_OPEN:",
        "| Major result | Open subresult | Required evidence |",
        "| --- | --- | --- |",
    ]
    for row in open_rows:
        lines.append(
            f"| `{md_cell(row['major_result_id'])}` | `{md_cell(row['subresult_id'])}` | {md_cell(row['acceptance'])} |"
        )
    lines.extend(
        [
            "",
            "CLOSURE_ARITHMETIC:",
            f"- Core-ready requires all `{arithmetic['required_subresults']}` required subresults to leave `OPEN`; current counts are `CLOSED_FOR_LANE={arithmetic['closed_for_lane']}`, `CLOSED_AS_NO_GO={arithmetic['closed_as_no_go']}`, `CLOSED_FOR_CORE={arithmetic['closed_for_core']}`, `OPEN={arithmetic['open']}`.",
            f"- The `{arithmetic['open']}` open subresults are controlled by `{arithmetic['root_input_packages']}` root input packages, so the next work is evidence acquisition/derivation, not indefinite reruns.",
            "",
            "ROOT_INPUT_PACKAGES:",
            "| Package | Status | Open subresults | Missing acceptance fields |",
            "| --- | --- | --- | --- |",
        ]
    )
    for package in payload["input_packages"]:
        lines.append(
            f"| `{md_cell(package['package_id'])}` | `{md_cell(package['status'])}` | {md_cell(', '.join(package['open_subresults']))} | {md_cell(', '.join(package['missing_acceptance_fields']))} |"
        )
    lines.extend(
        [
            "",
            "DEPENDENCY_UNLOCKED:",
            "- Causal named branch only. Full Topic 13, curved 3+1, Gravity, and constitutive transport remain locked.",
            "",
            "STATUS:",
            f"- `{status['full_topic_status']}`; `claim_promotion={str(status['claim_promotion']).lower()}`; `full_core_unlock={str(status['full_core_unlock']).lower()}`.",
            "",
            "WHAT_CHANGED:",
            "- Added package-level closure arithmetic and blocker ownership to the generated dashboard; no equation, threshold, source role, or claim status was changed.",
            "",
            "EQUATION_OR_MAPPING:",
            "- `y_TTG = Delta_Tq(t) / Delta_Tq(0)`",
            "- `y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)`",
            "- `Delta_Tq = alpha_Phi_K * Delta_Phi`",
            "- `alpha_Phi_K = (e0 / c_v) * s_material` only after an independent base-Phi map and SI anchor are accepted.",
            "",
            "VERIFICATION:",
            f"- Holdout policy: `{payload['holdout_policy']}`.",
            "- No numeric alpha, physical UET Kubo coefficient, or accepted Ding C_src payload is emitted by this report.",
            f"- Source hashes are recorded in `{OUT_JSON_REL}` for the matrix, gate, and input audit.",
            "",
            "CONTROLLING_BLOCKER:",
            f"- `{status['controlling_blocker']}`.",
            "- The three root input packages are still blocked: Ding-compatible source/material uncertainty, base-Phi/SI/alpha/beta, and physical transport matching.",
            "",
            "NEXT_ACTION:",
            "- Obtain one authorized Ding-compatible numeric package or accepted same-regime reproduction.",
            "- Obtain one independent base-Phi/SI response record or a dimensionful action anchor that fixes the normalization.",
            "- Obtain one state-matched physical Kubo record with SK/KMS/FDT, entropy, units, and uncertainty linkage.",
            "- Only after an input hash changes: run the record validators, input-package audit, full gate, and registry/dependency synchronization.",
            "",
            "CLAIM_BOUNDARY:",
            "- This dashboard reports closure progress only. It does not close Full Topic 13, establish an SI temperature prediction, consume Xie 2026, or unlock downstream Core/Gravity claims.",
            "",
            "RERUN_POLICY:",
            "- Do not rerun the same numeric gates as a substitute for missing evidence. Rerun when an accepted source, calibration record, physical transport record, or its hash changes.",
            "",
            f"Generated UTC: `{payload['generated_at']}`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_payload()
    json_path = ROOT / OUT_JSON_REL
    md_path = ROOT / OUT_MD_REL
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "PASS_T13_CLOSURE_PROGRESS_RENDERED",
                "json": OUT_JSON_REL,
                "markdown": OUT_MD_REL,
                "required_subresults": payload["required_subresult_count"],
                "open_subresults": len(payload["open_subresults"]),
                "closure_counts": payload["closure_counts"],
                "full_core_unlock": payload["canonical_status"]["full_core_unlock"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
