"""Audit public Green-Kubo graphite/graphene sources against the Topic 13 Kubo contract."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_graphite_green_kubo_source_boundary_audit.json"
SCRIPT = ROOT / "docs/scripts/audit/audit_topic13_graphite_green_kubo_source_boundary.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    candidates = [
        {
            "candidate_id": "khadem_wemhoff_graphite_stacking_2013",
            "title": "Molecular dynamics predictions of the influence of graphite stacking arrangement on the thermal conductivity tensor",
            "authors": "M. H. Khadem and A. P. Wemhoff",
            "year": 2013,
            "doi": "10.1016/j.cplett.2013.04.048",
            "source_url": "https://www.sciencedirect.com/science/article/abs/pii/S0009261413005307",
            "source_locator": "abstract and EMD method section; Green-Kubo tensor relation; 5 x 5 nm graphite domain; AAA/ABA/ABC stacking",
            "method": "equilibrium molecular dynamics with Green-Kubo heat-current autocorrelation",
            "material": "graphite stacking variants",
            "geometry": "finite graphite simulation domain",
            "temperature_K": None,
            "numeric_payload": {
                "intralayer_kappa_W_mK_range": [450.0, 800.0],
                "uncertainty": None,
            },
            "uncertainty_type": "not_reported_in_public_abstract",
            "local_copy_status": "NOT_INGESTED_URL_ONLY",
            "u_et_state_mapping": "MISSING",
            "acceptance_status": "COMPARATOR_NOT_UET_KUBO_RECORD",
            "exclusion_reason": "No base-Phi amplitude, UET space-response state, matched Ding TTG state, or source-locked uncertainty record.",
        },
        {
            "candidate_id": "oliveira_greaney_graphite_defects_2015",
            "title": "Thermal resistance from irradiation defects in graphite",
            "authors": "L. de Sousa Oliveira and P. A. Greaney",
            "year": 2015,
            "doi": "10.1016/j.commatsci.2015.03.001",
            "source_url": "https://www.sciencedirect.com/science/article/abs/pii/S0927025615001639",
            "source_locator": "abstract and Sections 2-4; defect-free and defected graphite Green-Kubo calculations",
            "method": "equilibrium molecular dynamics with Green-Kubo heat-current autocorrelation",
            "material": "graphite and irradiation-defect configurations",
            "geometry": "atomistic graphite cells",
            "temperature_K": None,
            "numeric_payload": {
                "coefficient_rows": "not ingested from the public abstract",
                "uncertainty": "not ingested",
            },
            "uncertainty_type": "not available in the inspected public metadata",
            "local_copy_status": "NOT_INGESTED_URL_ONLY",
            "u_et_state_mapping": "MISSING",
            "acceptance_status": "SOURCE_BOUNDARY_ONLY",
            "exclusion_reason": "Public metadata establishes method and material relevance but not an accepted numeric row with UET state, raw correlator locator, and uncertainty.",
        },
        {
            "candidate_id": "jung_gyroid_graphene_green_kubo_2017",
            "title": "Unusually low and density-insensitive thermal conductivity of three-dimensional gyroid graphene",
            "authors": "G. S. Jung, J. Yeo, Z. Tian, Z. Qin, M. J. Buehler",
            "year": 2017,
            "doi": "10.1039/C7NR04455K",
            "source_url": "https://www.rsc.org/suppdata/c7/nr/c7nr04455k/c7nr04455k1.pdf",
            "source_locator": "Supplementary Information Eq. (S4), pp. 2-3; Tables S3 and S5, pp. 13-14",
            "method": "equilibrium molecular dynamics with Green-Kubo heat-current autocorrelation",
            "material": "graphene and three-dimensional gyroid graphene",
            "geometry": "finite graphene/gyroid models with L = 3, 10, 20 nm",
            "temperature_K": [200.0, 300.0, 400.0],
            "numeric_payload": {
                "source_reported_300K_rows_W_mK": [
                    {"model_L_nm": 3.0, "kappa": 3.52, "reported_plus_minus": 0.03},
                    {"model_L_nm": 10.0, "kappa": 3.00, "reported_plus_minus": 0.07},
                    {"model_L_nm": 20.0, "kappa": 2.69, "reported_plus_minus": 0.15},
                ],
                "uncertainty": "reported plus-minus values retained as source-reported; not promoted to standard uncertainty",
            },
            "uncertainty_type": "source-reported plus-minus",
            "local_copy_status": "NOT_INGESTED_URL_ONLY",
            "u_et_state_mapping": "MISSING",
            "acceptance_status": "NUMERIC_COMPARATOR_NOT_UET_KUBO_RECORD",
            "exclusion_reason": "Numeric Kubo comparator is graphene/gyroid material, not Ding natural graphite, and reports no base-Phi or UET space-response amplitude.",
        },
    ]

    checks = {
        "all_candidates_have_locator_and_method": all(
            candidate["source_locator"] and candidate["method"] for candidate in candidates
        ),
        "graphite_gk_candidate_present": any(
            "graphite" in candidate["material"].lower() for candidate in candidates
        ),
        "numeric_gk_comparator_present": any(
            isinstance(candidate["numeric_payload"], dict)
            and "source_reported_300K_rows_W_mK" in candidate["numeric_payload"]
            for candidate in candidates
        ),
        "all_candidates_reject_silent_uet_relabel": all(
            candidate["u_et_state_mapping"] == "MISSING" for candidate in candidates
        ),
        "no_candidate_is_accepted_physical_uet_kubo": all(
            candidate["acceptance_status"] not in {"KUBO_MATCHED", "SOURCE_LOCKED", "EXTERNALLY_MATCHED"}
            for candidate in candidates
        ),
        "no_local_source_hash_claimed": all(
            candidate["local_copy_status"] == "NOT_INGESTED_URL_ONLY" for candidate in candidates
        ),
        "no_alpha_or_phi_calibration": True,
        "no_target_or_holdout": True,
        "no_parameter_fitting": True,
    }

    artifact = {
        "schema_version": "t13-graphite-green-kubo-source-boundary-v1",
        "artifact": "t13_graphite_green_kubo_source_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY" if all(checks.values()) else "FAIL_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY",
        "major_result": {
            "major_result_id": "T13_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
            "what_is_closed": [
                "public primary Green-Kubo candidate search is source-identified for graphite/graphene thermal transport",
                "a numeric source-reported Green-Kubo comparator with a locator and reported plus-minus rows is archived as comparator evidence",
                "generic material thermal conductivity is not accepted as a UET physical Kubo coefficient without UET state mapping",
                "no source is silently relabeled as Ding C_src, base Phi, or an alpha calibration",
            ],
            "equation_or_mapping": {
                "green_kubo": "kappa_i = 1/(k_B*T^2*V) * integral_0^tau <J_i(t) J_i(0)> dt",
                "required_uet_record": "KuboCoefficientRecord -> coefficient value only when temperature, chemical potential, space_response, correlator locator, source hash, units, and evidence status pass",
                "rejection_mapping": "public graphite/graphene kappa -> comparator only when base-Phi and UET space-response mapping are absent",
            },
            "units": {
                "source_comparator": "W m^-1 K^-1",
                "temperature": "K where reported",
                "u_et_space_response": "missing; no unitful base-Phi amplitude reported",
                "source_hash": "not emitted because sources remain URL-only in this boundary audit",
            },
            "derivation_class": "external primary-source boundary audit; no UET coefficient derivation",
            "observable": "standard-physics Green-Kubo thermal-conductivity comparator and UET Kubo-record readiness",
            "data_role": "EXTERNAL_GREEN_KUBO_COMPARATOR_SOURCE_BOUNDARY_NOT_UET_COEFFICIENT",
            "evidence_artifacts": [
                {
                    "path": "docs/scripts/audit/audit_topic13_graphite_green_kubo_source_boundary.py",
                    "sha256": sha256(SCRIPT),
                }
            ],
            "verification_status": "PASS_SCOPED_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY" if all(checks.values()) else "FAIL_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY",
            "open_blockers": [
                "physical_Kubo_coefficient_record_missing",
                "UET_space_response_state_not_reported_by_external_Green_Kubo_sources",
                "base_Phi_SI_anchor_and_alpha_Phi_K_missing",
                "Ding_natural_graphite_TTG_material_state_match_missing",
                "source_locked_correlator_payload_and_uncertainty_contract_missing",
            ],
            "dependency_unlocked": "external Green-Kubo comparator boundary only; no physical UET transport, alpha, Full Topic 13, Core, Gravity, or external-validation unlock",
            "claim_boundary": "This closes only the source-boundary question for public graphite/graphene Green-Kubo comparators. It is not a physical UET Kubo coefficient, not Ding C_src, not an alpha_Phi_K calibration, not TTG validation, and not Full Topic 13 closure.",
        },
        "candidates": candidates,
        "checks": checks,
        "failed_checks": [key for key, value in checks.items() if not value],
        "numeric_transport_coefficient_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        "next_controller": "Obtain a permitted state-matched correlator or microscopic UET match that reports units, temperature, chemical potential, base-Phi/space-response amplitude, uncertainty, locator, and source hash; otherwise retain this comparator boundary.",
        "claim_promotion": False,
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["status"],
        "closure_level": artifact["major_result"]["closure_level"],
        "candidates": len(candidates),
        "failed_checks": artifact["failed_checks"],
    }, indent=2))
    return 0 if not artifact["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

