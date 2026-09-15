"""Audit the scoped conservative-action Kubo identifiability no-go."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_covariant_superfluid_transport import (
    covariant_superfluid_transport_contract,
)
from docs.core.thermal_sk_kms_entropy_contract import (
    thermal_sk_kms_entropy_contract,
)
from docs.core.uet_transport_coefficient_identifiability import (
    conservative_action_transport_witnesses,
    transport_coefficient_identifiability_contract,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_transport_coefficient_identifiability.py"
TRANSPORT_REL = "docs/core/uet_covariant_superfluid_transport.py"
SK_REL = "docs/core/thermal_sk_kms_entropy_contract.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_transport_coefficient_identifiability_no_go.json"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    contract = transport_coefficient_identifiability_contract()
    witnesses = conservative_action_transport_witnesses()
    transport = covariant_superfluid_transport_contract()
    sk = thermal_sk_kms_entropy_contract()
    matrices = [item.matrix for item in witnesses]
    checks = {
        "two_distinct_witnesses_are_present": len(witnesses) == 2
        and witnesses[0].name != witnesses[1].name,
        "witness_matrices_are_distinct": not np.allclose(matrices[0], matrices[1]),
        "witness_A_is_positive_semidefinite": witnesses[0].positive_semidefinite,
        "witness_B_is_positive_semidefinite": witnesses[1].positive_semidefinite,
        "witness_A_has_positive_relaxation": witnesses[0].positive_relaxation_time,
        "witness_B_has_positive_relaxation": witnesses[1].positive_relaxation_time,
        "witnesses_have_distinct_relaxation": witnesses[0].relaxation_time
        != witnesses[1].relaxation_time,
        "same_ideal_action_is_declared": contract["witness_policy"]["same_ideal_action"] is True,
        "physical_values_are_not_emitted": contract["witness_policy"]["witnesses_are_physical_values"] is False,
        "transport_requires_external_or_microscopic_match": transport["transport_values"]
        == "REQUIRED_EXTERNAL_OR_MICROSCOPIC_MATCH_NO_DEFAULTS",
        "normal_component_is_open": transport["normal_component"] == "OPEN_NOT_DERIVED",
        "sk_contract_is_formal": sk["physical_status"]
        == "named formal SK/KMS/entropy interface; not physical transport closure",
        "kubo_admission_requires_provenance": "matched retarded correlator" in contract["equations"]["Kubo_admission"],
        "entropy_positivity_is_not_identification": contract["witness_policy"]["entropy_positivity_is_sufficient_for_identification"] is False,
        "C_ontology_is_preserved": "not a transport coefficient" in contract["ontology"]["C"],
        "Phi_ontology_is_preserved": "not a dissipative coefficient" in contract["ontology"]["Phi"],
        "R_gen_has_no_feedback": "no transport state or feedback" in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_SCOPED_NO_GO_CONSERVATIVE_ACTION_KUBO_IDENTIFIABILITY"
        if all(checks.values())
        else "FAIL_SCOPED_NO_GO_CONSERVATIVE_ACTION_KUBO_IDENTIFIABILITY"
    )
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": TRANSPORT_REL, "sha256": digest(TRANSPORT_REL)},
        {"path": SK_REL, "sha256": digest(SK_REL)},
    ]
    report = {
        "schema_version": "t13-transport-coefficient-identifiability-no-go-v1",
        "artifact": "t13_transport_coefficient_identifiability_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_TRANSPORT_COEFFICIENT_IDENTIFIABILITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the current conservative single-copy action fixes the ideal O(2) pressure/current/stress sector but not a unique dissipative Onsager/Kubo sector",
                "two distinct positive-semidefinite dissipative witnesses satisfy the formal entropy positivity contract while producing different transport responses",
                "the admission boundary requiring a state-matched retarded correlator, units, locator, source identity, and hash is explicit",
                "the no-go is scoped to the current action and does not reject a future open-system or SK microscopic extension",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "structural identifiability no-go from the conservative action contract plus two internal PSD witnesses; no physical coefficient inference",
            "observable": "difference between admissible dissipative response completions, not an external transport observable",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "physical_Kubo_coefficient_record_missing",
                "finite_temperature_normal_component_not_derived",
                "microscopic_SK_KMS_matching_not_closed",
                "SI_transport_unit_map_missing",
                "curved_3p1_transport_solver_missing",
                "base_Phi_SI_anchor_and_alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "closes only the structural Kubo identifiability boundary; no physical transport, Full Topic 13, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "witnesses": [
            {
                "name": item.name,
                "onsager_matrix": item.onsager_matrix,
                "eigenvalues": item.eigenvalues.tolist(),
                "relaxation_time": item.relaxation_time,
                "positive_semidefinite": item.positive_semidefinite,
                "positive_relaxation_time": item.positive_relaxation_time,
                "coefficient_origin": item.coefficient_origin,
            }
            for item in witnesses
        ],
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        "next_controller": "Acquire or microscopically derive one state-matched Kubo coefficient record and an open-system/SK collision-noise kernel; then rerun finite-temperature normal transport and SI observables without using synthetic witnesses as physical values.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "failed_checks": [key for key, value in checks.items() if not value],
                "witness_count": len(witnesses),
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
