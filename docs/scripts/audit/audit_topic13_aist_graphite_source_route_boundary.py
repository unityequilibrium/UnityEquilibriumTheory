"""Record the AIST TPDS graphite route boundary without consuming numeric data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_aist_graphite_source_route_boundary_audit.json"


SOURCE_RECORD: dict[str, Any] = {
    "publisher": "National Institute of Advanced Industrial Science and Technology (AIST)",
    "database": "Thermophysical Property Data System, TPDS-web",
    "search_locator": "https://tpds.db.aist.go.jp/tpds-web/index.aspx?Search=graphite",
    "terms_locator": "https://tpds.db.aist.go.jp/tpds-web/index.aspx?Search=graphite",
    "material_records_observed": [
        "Graphite sheet",
        "POCO AXM-5Q1(High temperature)",
        "Graphite 3474D_Bu,Lt1,Specimen1",
        "Graphite 7087_Bulk,Lt1,Specimen1",
    ],
    "property_catalog_observed": [
        "Density",
        "Specific heat capacity at constant pressure",
        "Specific heat capacity at constant volume",
        "Volumetric heat capacity",
        "Volumetric thermal expansion coefficient",
    ],
    "accessed_at": "2026-08-21",
    "material_detail_opened": False,
    "material_state_verified": False,
    "numeric_payload_accessed": False,
    "numeric_payload_stored": False,
    "source_grade_uncertainty_present": False,
    "holdout_accessed": False,
    "target_fit_performed": False,
    "alpha_fit_performed": False,
    "terms": {
        "agreement_present": True,
        "internal_research_use_described": True,
        "public_numeric_redistribution_permitted": False,
        "public_numeric_payload_embedded": False,
        "terms_interpretation": "The displayed English terms restrict publishing or providing the contents to a third party. This audit records metadata only and does not accept the agreement or copy numeric payloads.",
    },
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def build_artifact() -> dict[str, Any]:
    source_record_sha256 = sha256_bytes(canonical_json(SOURCE_RECORD))
    return {
        "schema_version": "t13-aist-graphite-source-route-boundary-v1",
        "artifact": "t13_aist_graphite_source_route_boundary_audit",
        "generated_at": "2026-08-21",
        "status": "PASS_SCOPED_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY",
        "major_result": {
            "major_result_id": "T13_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": "The public AIST TPDS graphite search route is documented as a source-provenance boundary. The route exposes graphite material names and thermophysical-property categories relevant to c_v, density, volumetric heat capacity, and volumetric thermal expansion, but the accessible route does not provide a redistributable numeric payload for this repository under the displayed terms. No material detail, numeric row, or uncertainty record was consumed.",
            "equation_or_mapping": {
                "candidate_specific_heat_input": "c_v(T, material)",
                "candidate_volumetric_map": "c_v^V(T, material) = rho(T, material) * c_v(T, material)",
                "numeric_mapping_emitted": False,
            },
            "units": {
                "c_v": "J kg^-1 K^-1",
                "rho": "kg m^-3",
                "c_v_volumetric": "J m^-3 K^-1",
                "temperature": "K",
            },
            "derivation_class": "public source access and license-boundary audit; no UET derivation",
            "observable": "availability of a redistributable graphite c_v or volumetric-heat-capacity source row with uncertainty",
            "data_role": "SOURCE_PROVENANCE_BOUNDARY_NOT_CALIBRATION",
            "evidence_artifacts": [
                {
                    "role": "aist_tpds_public_search_and_terms_metadata",
                    "locator": SOURCE_RECORD["search_locator"],
                    "source_record_sha256": source_record_sha256,
                }
            ],
            "verification_status": "PASS_SCOPED_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY",
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "c_v_source_uncertainty_not_closed",
                "density_uncertainty_not_source_locked",
                "material_regime_mapping_to_TTG_not_closed",
            ],
            "dependency_unlocked": "AIST public-route boundary only; no c_v source closure, Ding C_src, alpha_Phi_K, Full Topic 13, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This closes only the public-reproducibility boundary of the screened AIST route. It is not a numeric c_v or C_src source package, not an uncertainty closure, not an independent alpha_Phi_K calibration, not a TTG prediction, and not external validation.",
        },
        "source": {
            **SOURCE_RECORD,
            "source_record_sha256": source_record_sha256,
        },
        "acceptance": {
            "accepted_for_full_topic13": False,
            "accepted_as_independent_csrc_reproduction": False,
            "accepted_as_alpha_phi_k_calibration": False,
            "route_closed_as_public_reproducibility_boundary": True,
            "numeric_payload_consumed": False,
            "source_grade_uncertainty_present": False,
            "material_state_verified": False,
            "target_fit_performed": False,
            "alpha_fit_performed": False,
            "holdout_accessed": False,
        },
        "controlling_blocker": "aist_numeric_payload_not_publicly_redistributable",
        "next_controller": "Acquire a permitted redistributable numeric graphite c_v or volumetric-heat-capacity source with material identity, units, row-level uncertainty, preprocessing, and hash; otherwise obtain a permissioned private source package without treating it as publicly reproducible.",
        "claim_boundary": "Source-route boundary only; no numeric c_v, no C_src, no temperature prediction, no alpha_Phi_K calibration, no holdout use, and no Full Topic 13 closure.",
    }


def main() -> int:
    artifact = build_artifact()
    OUT.write_text(json.dumps(artifact, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": str(OUT), "source_record_sha256": artifact["source"]["source_record_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
