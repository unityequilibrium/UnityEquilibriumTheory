"""Render a human-readable Topic 13 subresult closure map."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
INPUT_REL = "docs/core/artifacts/t13_full_closure_progress.json"
OUT_REL = "docs/topics/0.13_Thermodynamic_Bridge/TOPIC13_SUBRESULT_CLOSURE_MAP.md"


def cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def main() -> int:
    payload = json.loads((ROOT / INPUT_REL).read_text(encoding="utf-8-sig"))
    status = payload["canonical_status"]
    counts = payload["closure_counts"]
    lines = [
        "# Topic 13 Subresult Closure Map",
        "",
        "This file is generated from the canonical Topic 13 closure progress artifact. It exposes result-level closure without treating a passing verifier as Full Topic 13 closure.",
        "",
        "MAJOR_RESULT_CLOSURE:",
        f"- Full Topic 13: {status['full_topic_closure_level']}; status {status['full_topic_status']}.",
        f"- Required subresults: {payload['required_subresult_count']}; CLOSED_FOR_LANE={counts.get('CLOSED_FOR_LANE', 0)}, CLOSED_AS_NO_GO={counts.get('CLOSED_AS_NO_GO', 0)}, CLOSED_FOR_CORE={counts.get('CLOSED_FOR_CORE', 0)}, OPEN={counts.get('OPEN', 0)}.",
        "",
        "WHAT_IS_ACTUALLY_CLOSED:",
        "- The causal conserved-C question has a scoped no-go, and the named finite-cone Phi branch is a bounded Core handoff only.",
        "- Formal normalized/action, EOS, SK/KMS, entropy, heat-current, source-boundary, and comparator lanes have explicit evidence boundaries.",
        "- The open rows below are the remaining acceptance requirements for the full thermal bridge; they are not missing merely because a script has not been rerun.",
        "",
        "WHAT_REMAINS_OPEN:",
        "| Subresult | Major result | Status | Required level | Controlling package | Evidence IDs | Acceptance requirement |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["subresults"]:
        evidence = ", ".join(row.get("evidence_result_ids", [])) or "none"
        lines.append(
            f"| {cell(row.get('subresult_id'))} | {cell(row.get('major_result_id'))} | {cell(row.get('status'))} | {cell(row.get('required_closure_level'))} | {cell(row.get('controlling_input_package'))} | {cell(evidence)} | {cell(row.get('acceptance'))} |"
        )
    lines.extend([
        "",
        "MAJOR_RESULT_BREAKDOWN:",
        "| Major result | Level | Lane | No-go | Core | Open | Dependency unlocked | Claim boundary |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ])
    for major in payload["major_results"]:
        major_counts = major["subresult_status_counts"]
        lines.append(
            f"| {cell(major.get('major_result_id'))} | {cell(major.get('closure_level'))} | {major_counts.get('CLOSED_FOR_LANE', 0)} | {major_counts.get('CLOSED_AS_NO_GO', 0)} | {major_counts.get('CLOSED_FOR_CORE', 0)} | {major_counts.get('OPEN', 0)} | {cell(major.get('dependency_unlocked'))} | {cell(major.get('claim_boundary'))} |"
        )
    lines.extend([
        "",
        "ROOT_INPUT_PACKAGES:",
        "| Package | Status | Accepted for Core | Open subresults | Missing acceptance fields |",
        "| --- | --- | --- | --- | --- |",
    ])
    for package in payload["input_packages"]:
        lines.append(
            f"| {cell(package.get('package_id'))} | {cell(package.get('status'))} | {str(package.get('accepted_for_core', False)).lower()} | {cell(', '.join(package.get('open_subresults', [])))} | {cell(', '.join(package.get('missing_acceptance_fields', [])))} |"
        )
    lines.extend([
        "",
        "DEPENDENCY_UNLOCKED:",
        "- Only the bounded causal branch and explicitly scoped comparator/formal lanes are available as inputs.",
        "- Full Topic 13 Core closure, curved 3+1, Gravity, and full constitutive transport remain locked.",
        "",
        "STATUS:",
        f"- claim_promotion={str(status['claim_promotion']).lower()}; full_core_unlock={str(status['full_core_unlock']).lower()}.",
        "",
        "WHAT_CHANGED:",
        "- Added a complete result-level register so progress can be read as closed lanes, no-go results, Core handoffs, and open acceptance rows rather than as undifferentiated PASS/FAIL counts.",
        "",
        "EQUATION_OR_MAPPING:",
        "- y_TTG = Delta_Tq(t) / Delta_Tq(0); y_TTG^UET = Delta_Phi(t) / Delta_Phi(0); Delta_Tq = alpha_Phi_K * Delta_Phi.",
        "- C_src(T) = sum_mu c_mu(T) remains source/state/uncertainty controlled.",
        "",
        "VERIFICATION:",
        "- This report is generated from the closure matrix, full gate, input-package audit, and minimal-input contract; it creates no scientific value.",
        f"- Source hashes remain in {INPUT_REL}; holdout access remains {payload['holdout_policy']}.",
        "",
        "CONTROLLING_BLOCKER:",
        f"- {status['controlling_blocker']}; grouped input blockers: Ding-compatible source, independent base-Phi/SI/alpha/beta, and physical transport matching.",
        "",
        "NEXT_ACTION:",
        "- Acquire an accepted external input or independently derived SI normalization for an open row; do not rerun unchanged numeric gates as a substitute.",
        "- Keep Xie 2026 metadata-only until the separate holdout preregistration and access gate authorize a final comparison.",
        "",
        "CLAIM_BOUNDARY:",
        "- This map reports research closure boundaries only. It does not claim Full Topic 13 closure, an SI temperature prediction, external validation, or global UET closure.",
        "",
        f"Generated from {INPUT_REL}.",
    ])
    (ROOT / OUT_REL).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_T13_SUBRESULT_CLOSURE_MAP_RENDERED", "path": OUT_REL, "rows": len(payload["subresults"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
