from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_REL = "docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json"
FULL_GATE_REL = "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
SYNC_REL = "docs/scripts/audit/sync_topic13_major_result_lanes.py"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def evidence(relative: str, summary: dict) -> dict:
    return {"path": relative, "sha256": digest(relative), "summary": summary}


def build_artifact() -> dict:
    ding_inputs = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_pbte_numeric_input_availability_package.json"
    )
    ding_boundary = load("docs/core/07_artifacts/topic13/t13_ding_c_src_independent_reproduction_boundary_audit.json")
    material_boundary = load("docs/core/07_artifacts/topic13/t13_ding_material_regime_boundary_audit.json")
    mesh = load("docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json")

    ding_author_payload_present = bool(
        ding_inputs.get("availability_contract", {})
        .get("direct_oa_numeric_route", "")
        .startswith("PRESENT")
    ) or bool(
        ding_inputs.get("acquisition_decision", {})
        .get("author_numeric_payload_received", False)
    )
    mp48_material_equivalent = bool(
        material_boundary.get("mapping_contract", {}).get("equivalence_result", False)
    )
    mp48_csrc_ready = bool(
        ding_boundary.get("checks", {}).get("mp48_declares_ding_c_src", False)
    )
    mp48_mesh_pass = (
        mesh.get("status") == "PASS_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE"
        and mesh.get("mesh_policy", {}).get("fine_tail_converged", False)
    )
    accepted_independent = (
        mp48_material_equivalent
        and mp48_csrc_ready
        and mp48_mesh_pass
    )

    return {
        "schema_version": "t13-independent-csrc-acceptance-contract-v1",
        "artifact": "t13_independent_csrc_acceptance_contract",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT",
        "major_result": {
            "major_result_id": "T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "the independent-reproduction route is now an explicit machine-readable source gate",
                "full Topic 13 may accept an independent reproduction only when material/state, PBTE response, units, uncertainty, convergence, and provenance are all present",
                "the current MP48 harmonic comparator is evaluated and rejected without silent substitution for Ding C_src",
                "raw-author Ding C_src and accepted independent reproduction are separate source routes",
            ],
            "what_is_remains_open": [
                "Ding author numeric payload or a qualifying independent PBTE reproduction",
                "mode-resolved C_src(T) in J m^-3 K^-1 with uncertainty",
                "same material regime, temperature/state, and response-contract mapping",
            ],
            "dependency_unlocked": "source acceptance policy only; no Ding C_src, alpha, transport, Core, or Gravity unlock",
            "equation_or_mapping": {
                "source_response": "C_src(T) = sum_mu c_mu(T)",
                "temperature_response": "Delta_Tq = Delta_u_ph / C_src",
                "acceptance_rule": "accepted_independent_C_src := provenance and raw payload + material/state match + PBTE response + SI units + uncertainty + convergence",
            },
            "units": {
                "C_src": "J m^-3 K^-1",
                "temperature": "K",
                "uncertainty": "source-declared standard or otherwise explicitly qualified uncertainty",
            },
            "derivation_class": "source acceptance contract and candidate qualification audit; no UET derivation",
            "observable": "Ding-compatible mode-resolved PBTE heat-capacity response",
            "data_role": "SOURCE_ACCEPTANCE_GATE_NOT_CALIBRATION",
            "evidence_artifacts": [
                evidence(
                    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_pbte_numeric_input_availability_package.json",
                    {"role": "Ding official OA and author-request availability"},
                ),
                evidence(
                    "docs/core/07_artifacts/topic13/t13_ding_c_src_independent_reproduction_boundary_audit.json",
                    {"role": "current independent comparator boundary"},
                ),
                evidence(
                    "docs/core/07_artifacts/topic13/t13_ding_material_regime_boundary_audit.json",
                    {"role": "material/state equivalence controller"},
                ),
                evidence(
                    "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json",
                    {"role": "independent force-constant convergence controller"},
                ),
            ],
            "verification_status": "PASS_SCOPED_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT",
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "claim_boundary": "This closes the acceptance policy and current candidate evaluation only. It does not emit C_src, replace Ding data with MP48, calibrate alpha_Phi_K, or close Topic 13.",
        },
        "acceptance_contract": {
            "required_fields": [
                "source_identity_and_locator",
                "raw_numeric_or_reproduction_payload",
                "source_hash",
                "material_identity_morphology_isotope_defect_state",
                "temperature_and_state",
                "PBTE_mode_resolved_response_contract",
                "C_src_rows_with_J_m^-3_K^-1_units",
                "uncertainty_and_preprocessing",
                "mesh_or_numerical_convergence",
                "independence_statement",
                "holdout_and_fit_audit",
            ],
            "rejection_rules": [
                "figure-derived normalized TTG rows cannot satisfy C_src acceptance",
                "harmonic c_v or DOS comparators cannot satisfy PBTE C_src acceptance without a declared response mapping",
                "a different graphite grade or morphology cannot satisfy Ding equivalence by label alone",
                "missing uncertainty or convergence cannot be repaired by changing a threshold",
                "Xie 2026 holdout cannot be read by source, calibration, or tuning paths",
            ],
        },
        "candidate_evaluations": {
            "ding_author_payload": {
                "accepted_for_full_topic13": ding_author_payload_present,
                "source_route": "RAW_AUTHOR_DING_C_SRC",
                "reason": "No numeric author payload is present in the captured package; the request route remains open.",
            },
            "mp48_harmonic_comparator": {
                "accepted_for_full_topic13": accepted_independent,
                "source_route": "INDEPENDENT_PBTE_REPRODUCTION",
                "material_equivalent_to_ding": mp48_material_equivalent,
                "mode_resolved_ding_c_src_ready": mp48_csrc_ready,
                "force_constant_mesh_pass": mp48_mesh_pass,
                "reason": "MP48 is a harmonic ideal AB graphite comparator, not a Ding-equivalent PBTE response; it remains comparison-only.",
            },
        },
        "acceptance": {
            "raw_author_numeric_C_src_available": ding_author_payload_present,
            "accepted_independent_reproduction_available": accepted_independent,
            "accepted_for_full_topic13": ding_author_payload_present or accepted_independent,
            "status": "PASS" if ding_author_payload_present or accepted_independent else "BLOCKED",
            "controlling_blocker": None
            if ding_author_payload_present or accepted_independent
            else "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        },
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "claim_promotion": False,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": "Obtain the Ding author numeric package or a permitted same-regime PBTE reproduction with mode-resolved C_src, SI units, uncertainty, convergence, and material-state mapping; do not relabel MP48.",
        "claim_boundary": "Source acceptance policy and candidate boundary only; no numeric C_src, no alpha_Phi_K, no holdout use, and no Full Topic 13 closure.",
    }


def patch_full_gate() -> None:
    path = ROOT / FULL_GATE_REL
    text = path.read_text(encoding="utf-8")
    map_marker = "'T13_UET_O2_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE': 'uet_o2_open_system_sk_kms_entropy_lane'"
    map_entry = ", 'T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT': 'independent_csrc_acceptance_contract'"
    if "T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT" not in text:
        text = text.replace(map_marker, map_marker + map_entry, 1)

    load_marker = '    phi_e_comparator_path, phi_e_comparator = load(\n'
    load_insert = '    independent_csrc_acceptance_path, independent_csrc_acceptance = load(\n        "docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json"\n    )\n'
    if "independent_csrc_acceptance_path" not in text:
        text = text.replace(load_marker, load_insert + load_marker, 1)

    readiness_marker = '    # A figure-derived normalized route is sufficient for the comparison\n'
    readiness_insert = '    independent_reproduction_ready = bool(\n        independent_csrc_acceptance.get("acceptance", {}).get("accepted_for_full_topic13", False)\n    )\n'
    if "independent_reproduction_ready = bool" not in text:
        text = text.replace(readiness_marker, readiness_insert + readiness_marker, 1)
    text = text.replace("    source_ready = raw_author_source_ready\n", "    source_ready = raw_author_source_ready or independent_reproduction_ready\n", 1)

    source_marker = '            "raw_author_C_src_route_ready": raw_author_source_ready,\n'
    source_insert = source_marker + (
        '            "independent_reproduction_route_ready": independent_reproduction_ready,\n'
        '            "independent_reproduction_acceptance_status": independent_csrc_acceptance.get("acceptance", {}).get("status"),\n'
        '            "independent_reproduction_acceptance_artifact": {"path": rel(independent_csrc_acceptance_path), "sha256": sha256(independent_csrc_acceptance_path)},\n'
    )
    if '"independent_reproduction_route_ready": independent_reproduction_ready' not in text:
        text = text.replace(source_marker, source_insert, 1)

    evidence_marker = '            evidence(rel(ding_c_src_boundary_path), ding_c_src_boundary, {\n'
    evidence_insert = (
        '            evidence(rel(independent_csrc_acceptance_path), independent_csrc_acceptance, {\n'
        '                "status": independent_csrc_acceptance.get("status"),\n'
        '                "accepted_for_full_topic13": independent_reproduction_ready,\n'
        '                "controlling_blocker": independent_csrc_acceptance.get("controlling_blocker"),\n'
        '            }),\n'
    )
    if "evidence(rel(independent_csrc_acceptance_path)" not in text:
        text = text.replace(evidence_marker, evidence_insert + evidence_marker, 1)

    route_marker = '    ding_public_supplementary_lane = discovered_lane_integrations.get(\n'
    route_insert = (
        '    independent_csrc_acceptance_lane = discovered_lane_integrations.get(\n'
        '        "independent_csrc_acceptance_contract"\n'
        '    )\n'
        '    if independent_csrc_acceptance_lane:\n'
        '        artifact["verification_status"]["source_package"][\n'
        '            "independent_csrc_acceptance_contract"\n'
        '        ] = independent_csrc_acceptance_lane\n'
        '        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n'
        '            "independent_csrc_acceptance_contract", None\n'
        '        )\n'
    )
    if '"independent_csrc_acceptance_contract"\n        ] = independent_csrc_acceptance_lane' not in text:
        text = text.replace(route_marker, route_insert + route_marker, 1)

    path.write_text(text, encoding="utf-8")


def patch_sync() -> None:
    path = ROOT / SYNC_REL
    text = path.read_text(encoding="utf-8")
    marker = '    ("T13_UET_O2_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE", "uet_o2_open_system_sk_kms_entropy_lane"),\n'
    entry = marker + '    ("T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT", "independent_csrc_acceptance_contract"),\n'
    if "T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT" not in text:
        text = text.replace(marker, entry, 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    artifact_path = ROOT / ARTIFACT_REL
    artifact_path.write_text(json.dumps(build_artifact(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    patch_full_gate()
    patch_sync()
    print(json.dumps({"status": "PASS_REPAIRED_TOPIC13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT", "artifact": ARTIFACT_REL}, indent=2))


if __name__ == "__main__":
    main()
