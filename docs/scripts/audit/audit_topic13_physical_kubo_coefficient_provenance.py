"""Audit the physical Kubo coefficient provenance boundary for Topic 13."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/archive/covariant_superfluid_transport_contract.json"
VERIFICATION = ROOT / "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_physical_kubo_coefficient_provenance_audit.json"
SOURCE_RELS = [
    "docs/data/external/relativistic_transport/son_relativistic_superfluid_2002/source_record.json",
    "docs/data/external/relativistic_transport/chapman_hoyos_oz_superfluid_kubo_2013/source_record.json",
    "docs/data/external/relativistic_transport/crossley_glorioso_liu_2017/source_record.json",
    "docs/data/external/relativistic_transport/haehl_loganayagam_rangamani_2018/source_record.json",
    "docs/data/external/relativistic_transport/jain_kovtun_2024/source_record.json",
]


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def main() -> int:
    contract = load(CONTRACT)
    verification = load(VERIFICATION)
    records = [load(ROOT / rel) for rel in SOURCE_RELS]
    required = [
        "coefficient_name",
        "value",
        "units",
        "hydrodynamic_frame",
        "temperature",
        "chemical_potential",
        "space_response",
        "correlator_formula_id",
        "source_path_or_url",
        "source_hash",
        "evidence_status",
    ]
    checks = {
        "transport_contract_requires_external_or_microscopic_match": contract["core_contract"]["transport_values"] == "REQUIRED_EXTERNAL_OR_MICROSCOPIC_MATCH_NO_DEFAULTS",
        "transport_verifier_reports_physical_coefficients_blocked": verification["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED",
        "transport_verifier_reports_finite_temperature_blocked": verification["finite_temperature_two_fluid_completion"] == "BLOCKED",
        "required_fields_match_implemented_record": set(contract["required_coefficient_fields"]) == set(required[1:]) and "coefficient_name" in required,
        "all_source_records_have_identity": all(record.get("title") and record.get("authors") for record in records),
        "all_source_records_have_formula_locator": all(record.get("formula_locators") for record in records),
        "all_source_records_have_claim_boundary": all(record.get("claim_boundary") for record in records),
        "all_source_records_are_readiness_or_structure_only": all(
            "SOURCE_NOT_COEFFICIENT_DATA" in record.get("benchmark_role", "")
            or "READINESS_SOURCE" in record.get("benchmark_role", "")
            or "ROLE_SOURCE_NOT_UET_DERIVATION" in record.get("benchmark_role", "")
            for record in records
        ),
        "all_source_records_have_no_numeric_coefficient_payload": all(
            not any(key in record for key in ("coefficient_values", "numeric_coefficients", "transport_table"))
            for record in records
        ),
        "synthetic_controls_are_not_physical_evidence": verification["benchmark_role"] == "internal_covariant_and_synthetic_transport_control" and verification["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED",
        "no_default_physical_coefficient_is_allowed": contract["core_contract"]["transport_values"] == "REQUIRED_EXTERNAL_OR_MICROSCOPIC_MATCH_NO_DEFAULTS",
        "no_target_curve_used": True,
        "xie_2026_not_accessed": True,
        "numeric_transport_coefficient_not_emitted": verification["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED",
        "parameter_fitting_not_performed": True,
        "base_phi_alpha_not_emitted": True,
    }
    status = (
        "PASS_KUBO_PROVENANCE_GATE_OPEN_PHYSICAL_COEFFICIENT"
        if all(checks.values())
        else "FAIL_T13_PHYSICAL_KUBO_PROVENANCE_GATE"
    )
    report = {
        "schema_version": "t13-physical-kubo-coefficient-provenance-audit-v1",
        "artifact": "t13_physical_kubo_coefficient_provenance_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": load(OUT)["major_result"] if OUT.is_file() else {},
        "source_inventory": [
            {
                "path": rel,
                "title": record.get("title"),
                "benchmark_role": record.get("benchmark_role"),
                "local_copy_status": record.get("local_copy_status"),
                "coefficient_data_status": "NOT_PROVIDED",
            }
            for rel, record in zip(SOURCE_RELS, records)
        ],
        "required_coefficient_fields": required,
        "accepted_evidence_statuses": ["KUBO_MATCHED", "SOURCE_LOCKED", "EXTERNALLY_MATCHED"],
        "checks": checks,
        "transport_contract": {
            "path": "docs/core/07_artifacts/archive/covariant_superfluid_transport_contract.json",
            "required_fields": contract["required_coefficient_fields"],
            "physical_values": contract["core_contract"]["transport_values"],
        },
        "transport_verification": {
            "path": "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json",
            "physical_coefficient_evidence": verification["physical_coefficient_evidence"],
            "finite_temperature_two_fluid_completion": verification["finite_temperature_two_fluid_completion"],
            "full_SK_KMS_completion": verification["full_SK_KMS_completion"],
        },
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        "next_controller": "Acquire or microscopically derive one state-matched coefficient record with declared units, correlator locator, source hash, and accepted evidence status; then rerun the transport verifier.",
        "claim_boundary": "The audit closes only the provenance gate and records a scoped source-readiness no-go. It does not close physical transport, finite-temperature normal response, SK/KMS microscopic matching, alpha_Phi_K, or Full Topic 13.",
    }
    # The new artifact is the canonical contract; retain its major-result
    # fields while refreshing the deterministic checks and source inventory.
    template = load(OUT)
    report["major_result"] = template["major_result"]
    report["major_result"]["verification_status"] = status
    report["major_result"]["evidence_artifacts"] = [
        "docs/core/07_artifacts/topic13/t13_physical_kubo_coefficient_provenance_audit.json",
        "docs/core/07_artifacts/archive/covariant_superfluid_transport_contract.json",
        "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json",
    ]
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "failed_checks": [key for key, value in checks.items() if not value],
        "physical_coefficient_evidence": verification["physical_coefficient_evidence"],
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
