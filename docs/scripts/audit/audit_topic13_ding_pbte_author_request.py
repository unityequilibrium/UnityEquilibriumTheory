"""Audit the bounded Ding PBTE author-request package without sending it."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_author_request_manifest.json"
)
OA_PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_numeric_input_availability_package.json"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_pbte_author_request_audit.json"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def main() -> int:
    manifest = load(MANIFEST)
    oa_package = load(OA_PACKAGE)
    request_scope = manifest["request_scope"]
    required = manifest["required_record_fields"]
    tests = manifest["acceptance_tests"]
    checks = {
        "manifest_not_sent": manifest["status"] == "REQUEST_PACKAGE_READY_NOT_SENT",
        "major_result_lane_closed": manifest["major_result"]["closure_level"] == "CLOSED_FOR_LANE",
        "source_identity_matches_ding": manifest["source_identity"]["doi"] == oa_package["source_identity"]["doi"],
        "oa_route_is_scoped_no_go": oa_package["availability_contract"]["direct_oa_numeric_route"] == "ABSENT_FROM_CAPTURED_OFFICIAL_PMC_OA_PREFIX",
        "author_route_is_open_not_executed": oa_package["availability_contract"]["author_request_route"] == "OPEN_NOT_EXECUTED",
        "mode_outputs_requested": any("mode-resolved" in value for value in request_scope["numeric_mode_outputs"]),
        "c_src_requested": any("C_src(T)" in value for value in request_scope["numeric_mode_outputs"]),
        "force_constants_requested": any("force constants" in value.lower() for value in request_scope["first_principles_inputs"]),
        "shengbte_requested": any("ShengBTE" in value for value in request_scope["first_principles_inputs"]),
        "units_required": "units" in required,
        "row_identity_required": "mode_index_or_row_identity" in required,
        "uncertainty_required": "uncertainty_or_convergence" in required,
        "hash_required": "source_hash" in required,
        "permission_required": "permission_or_terms" in required,
        "holdout_statement_required": "holdout_non_access_statement" in required,
        "acceptance_tests_present": len(tests) >= 8,
        "no_target_curve": manifest["holdout_policy"]["target_curve_used"] is False,
        "no_alpha_fit": manifest["holdout_policy"]["alpha_fit_used"] is False,
        "no_xie_access": manifest["holdout_policy"]["xie_2026_accessed"] is False,
        "no_numeric_alpha_claim": "no independent base-Phi amplitude" in manifest["claim_boundary"],
    }
    status = (
        "PASS_REQUEST_SCHEMA_OPEN_EXTERNAL_RESPONSE"
        if all(checks.values())
        else "FAIL_DING_PBTE_AUTHOR_REQUEST_SCHEMA"
    )
    report = {
        "schema_version": "t13-ding-pbte-author-request-audit-v1",
        "artifact": "t13_ding_pbte_author_request_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": manifest["major_result"],
        "request_state": manifest["status"],
        "source_identity": manifest["source_identity"],
        "requested_payload_groups": {
            key: len(value) for key, value in request_scope.items() if isinstance(value, list)
        },
        "required_record_fields": required,
        "acceptance_tests": tests,
        "checks": checks,
        "controlling_blocker": "author_data_or_independent_reproduction_payload_not_received",
        "next_controller": "Send the bounded request only after project authorization; on response, hash and audit each payload before changing the response state.",
        "claim_boundary": manifest["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "failed_checks": [key for key, value in checks.items() if not value],
        "request_state": manifest["status"],
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
