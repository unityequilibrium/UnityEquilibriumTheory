"""Close the Landauer controllers' Core dependency role without closing their datasets."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_landauer_core_disposition_audit.json"

CONTROLLERS = {
    "berut": (
        "docs/core/artifacts/t13_berut_source_package_availability_boundary.json",
        "PASS_SCOPED_BERUT_SOURCE_PACKAGE_BOUNDARY",
        "CLOSED_FOR_LANE",
        "CONSTRAINT_COMPARISON_ONLY_EXTERNAL_ROWS_OPEN",
    ),
    "jun": (
        "docs/core/artifacts/t13_jun_final_source_package_boundary.json",
        "PASS_SCOPED_JUN_FINAL_SOURCE_BOUNDARY",
        "CLOSED_FOR_LANE",
        "SOURCE_IDENTITY_ONLY_EXTERNAL_ROWS_OPEN",
    ),
    "hong": (
        "docs/core/artifacts/t13_hong_final_source_package_boundary.json",
        "PASS_SCOPED_HONG_FINAL_SOURCE_BOUNDARY",
        "CLOSED_FOR_LANE",
        "SOURCE_IDENTITY_ONLY_LEGACY_ROW_REJECTED",
    ),
    "peterson": (
        "docs/core/artifacts/t13_peterson_source_identity_no_go.json",
        "PASS_SCOPED_PETERSON_SOURCE_IDENTITY_NO_GO",
        "CLOSED_FOR_LANE",
        "CLOSED_AS_SOURCE_IDENTITY_NO_GO",
    ),
}

ALPHA = ROOT / "docs/core/artifacts/t13_he4_o2_response_calibration_audit.json"
BETA = ROOT / "docs/core/artifacts/t13_he4_o2_si_beta_mapping_audit.json"
TRANSPORT = ROOT / "docs/core/artifacts/t13_he4_normal_viscosity_kubo_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    records = {}
    controller_checks = {}
    evidence = []
    for name, (path_text, expected_status, expected_level, disposition) in CONTROLLERS.items():
        path = ROOT / path_text
        item = load(path)
        verification = item.get("verification_status", {})
        checks = {
            "expected_status": item.get("status") == expected_status,
            "lane_boundary_closed": item.get("major_result", {}).get("closure_level") == expected_level,
            "no_alpha_emitted": item.get("numeric_alpha_Phi_K_emitted", False) is False,
            "no_parameter_fit": item.get("parameter_fitting_performed", False) is False,
            "holdout_unread": item.get("xie_2026_accessed", False) is False,
            "not_calibration_eligible": (
                verification.get("calibration_not_eligible", True) is True
            ),
        }
        controller_checks[name] = checks
        records[name] = {
            "core_disposition": disposition,
            "core_dependency_required": False,
            "external_numeric_dataset_closed": len(item.get("open_blockers", [])) == 0,
            "external_open_blockers": item.get("open_blockers", []),
            "source_status": item.get("status"),
            "checks": checks,
            "claim_boundary": item.get("claim_boundary"),
        }
        evidence.append({"path": rel(path), "sha256": sha256(path)})

    alpha = load(ALPHA)
    beta = load(BETA)
    transport = load(TRANSPORT)
    physical_bridge_checks = {
        "alpha_is_independent_he4_calibration": (
            alpha.get("status") == "PASS_HE4_LOCAL_ALPHA_AND_FIELD_NORMALIZATION"
            and alpha.get("record", {}).get("data_role") == "CALIBRATION"
            and alpha.get("record", {}).get("holdout_policy", {}).get("target_curve_used") is False
        ),
        "beta_does_not_use_landauer": (
            beta.get("status") == "PASS_HE4_SI_SCALE_AND_NORMALIZED_BETA"
            and beta.get("record", {}).get("holdout_policy", {}).get("landauer_identity_used") is False
        ),
        "transport_is_independent_external_input": (
            transport.get("status") == "PASS_HE4_PHYSICAL_SHEAR_KUBO_TRANSPORT"
            and transport.get("record", {}).get("data_role") == "EXTERNAL_INPUT_NOT_UET_PREDICTION"
            and transport.get("record", {}).get("holdout_policy", {}).get("fit_or_tuning_used") is False
        ),
    }
    for path in (ALPHA, BETA, TRANSPORT):
        evidence.append({"path": rel(path), "sha256": sha256(path)})

    checks = {
        "all_source_controllers_have_closed_core_dispositions": all(
            all(values.values()) for values in controller_checks.values()
        ),
        "landauer_not_used_to_derive_alpha_beta_or_transport": all(physical_bridge_checks.values()),
        "external_dataset_gaps_remain_visible": all(
            records[name]["external_open_blockers"] for name in CONTROLLERS
        ),
        "no_controller_unlocks_external_validation": all(
            not records[name]["external_numeric_dataset_closed"] for name in CONTROLLERS
        ),
    }
    passed = all(checks.values())
    status = "PASS_LANDAUER_CORE_ROLE_DISPOSITION" if passed else "FAIL_LANDAUER_CORE_ROLE_DISPOSITION"
    report = {
        "schema_version": "t13-landauer-core-disposition-v1",
        "artifact": "t13_landauer_core_disposition_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_LANDAUER_CONSTRAINT_SOURCE_DISPOSITION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_CORE" if passed else "OPEN",
            "what_is_closed": "The Core dependency role of Berut, Jun, Hong, and Peterson is dispositioned as imported Landauer constraint/source-boundary evidence only; none supplies alpha, beta, EOS, or transport.",
            "equation_or_mapping": "E_min = k_B T ln(2) remains an imported constraint and is not an inverse map to Phi or a coefficient-identification equation.",
            "units": {"landauer_energy": "J when evaluated", "alpha_Phi_K": "not emitted by these controllers"},
            "derivation_class": "SOURCE_ROLE_AND_DEPENDENCY_DISPOSITION",
            "observable": "Landauer erasure-work/heat comparison only",
            "data_role": "IMPORTED_CONSTRAINT_AND_EXTERNAL_COMPARISON",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [] if passed else ["landauer_core_role_disposition_failed"],
            "dependency_unlocked": "Landauer source rows no longer block the O(2)/He-4 Core bridge; external Landauer validation remains open.",
            "claim_boundary": "This closes only the controllers' Core dependency role. It does not claim raw numeric closure for Berut, Jun, or Hong, does not rehabilitate the Peterson legacy label, and does not validate Landauer experiments externally.",
        },
        "controllers": records,
        "controller_checks": controller_checks,
        "physical_bridge_checks": physical_bridge_checks,
        "checks": checks,
        "controlling_blocker": None if passed else "landauer_core_role_disposition_failed",
        "next_action": "Keep numeric row acquisition and parity work in the external Landauer comparison track; do not feed those rows into alpha, beta, EOS, or transport calibration.",
        "claim_boundary": "Core-role closure is not dataset closure or external validation.",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": rel(OUT), "checks": checks}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
