"""Audit the fail-closed input-record contract for Topic 13."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.topic13_closure_record_contract import topic13_closure_record_schema


OUT = ROOT / "docs/core/artifacts/t13_closure_record_contract_audit.json"


def main() -> int:
    schema = topic13_closure_record_schema()
    packages = schema["packages"]
    checks = {
        "schema_version_is_declared": bool(schema.get("schema_version")),
        "all_three_packages_are_present": set(packages) == {
            "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
            "T13_INPUT_DING_TTG_SOURCE",
            "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
        },
        "all_packages_have_validator": all(
            isinstance(value.get("validator"), str) and value["validator"]
            for value in packages.values()
        ),
        "all_packages_have_required_fields": all(
            isinstance(value.get("required_closure_fields"), list)
            and bool(value["required_closure_fields"])
            for value in packages.values()
        ),
        "forbidden_shortcuts_are_declared": len(schema.get("forbidden_shortcuts", [])) >= 5,
        "schema_has_no_scientific_values": schema.get("status") == "SCHEMA_ONLY_NO_EVIDENCE",
    }
    status = (
        "PASS_T13_CLOSURE_RECORD_CONTRACT_OPEN"
        if all(checks.values())
        else "FAIL_T13_CLOSURE_RECORD_CONTRACT"
    )
    report = {
        "schema_version": "t13-closure-record-contract-audit-v1",
        "artifact": "t13_closure_record_contract_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_CLOSURE_RECORD_CONTRACT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "PARTIAL",
            "what_is_closed": [
                "The three non-derivable Core input packages have explicit fail-closed record schemas.",
                "The schemas require provenance, units, uncertainty, state identity, and anti-holdout fields.",
                "The schema layer does not emit any physical value or promote a package.",
            ],
            "what_remains_open": [
                "No Ding numeric C_src payload has been received or accepted.",
                "No independent base-Phi/SI alpha record has been received or accepted.",
                "No physical state-matched Kubo/KMS/entropy record has been received or accepted.",
            ],
            "dependency_unlocked": "None; schema readiness only.",
            "equation_or_mapping": {
                "TTG": "C_src(T)=sum_mu c_mu(T); Delta_Tq=Delta_u_ph/C_src(T)",
                "Phi": "Delta_Tq=alpha_Phi_K*Delta_Phi",
                "transport": "KuboCoefficientRecord -> physical coefficient only after matched provenance",
            },
            "units": {
                "C_src": "J m^-3 K^-1",
                "alpha_Phi_K": "K per normalized base Phi",
                "transport": "SI units declared per coefficient",
            },
            "derivation_class": "machine-readable acceptance schema; no physical derivation",
            "observable": "Topic 13 closure-input readiness",
            "data_role": "INTERNAL_CONTRACT_NOT_CALIBRATION",
            "evidence_artifacts": [
                "docs/core/topic13_closure_record_contract.py",
                "docs/core/artifacts/t13_closure_record_contract_audit.json",
            ],
            "verification_status": status,
            "controlling_blocker": "three_core_input_packages_not_accepted",
            "claim_boundary": "This closes record-format ambiguity only; it does not close Full Topic 13 or emit alpha, C_src, or transport values.",
        },
        "schema": schema,
        "checks": checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_fit_performed": False,
            "calibration_path_may_read_holdout": False,
        },
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"), "failed_checks": [key for key, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
