"""Record the official NIST SRM 3600 heat-capacity comparator boundary.

This verifier preserves the source as a comparator only. The paper reports
figure-based heat-capacity measurements and an approximate uncertainty
boundary, but it does not provide machine-readable rows for Ding's PBTE
``C_src`` or an independent UET calibration.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SOURCE_PATH = (
    ROOT
    / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    / "nist_srm_3600_glassy_carbon_heat_capacity.pdf"
)
OUT = ROOT / "docs/core/artifacts/t13_nist_srm_3600_heat_capacity_boundary_audit.json"

EXPECTED_SHA256 = "5bbbd0e3949a1e38cbb7ec00bbfc1a75a9d4708f6a0656e5e49c8d44d32ba5da"
EXPECTED_BYTES = 758635
EXPECTED_PAGE_COUNT = 6


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def build_artifact() -> dict[str, Any]:
    if not SOURCE_PATH.is_file():
        raise FileNotFoundError(SOURCE_PATH)
    raw = SOURCE_PATH.read_bytes()
    source_sha256 = sha256_bytes(raw)
    checks = {
        "source_file_exists": True,
        "pdf_signature_present": raw.startswith(b"%PDF-"),
        "source_byte_count_matches": len(raw) == EXPECTED_BYTES,
        "source_sha256_matches": source_sha256 == EXPECTED_SHA256,
        "declared_page_count": EXPECTED_PAGE_COUNT,
        "machine_readable_numeric_rows_emitted": 0,
        "figure_only_payload": True,
        "source_reported_uncertainty_boundary_present": True,
        "row_level_standard_uncertainty_present": False,
        "material_identity_recorded": True,
        "ding_hopg_pbte_material_match": False,
        "target_curve_read": False,
        "target_fit_performed": False,
        "alpha_fit_performed": False,
        "holdout_accessed": False,
    }
    source_record = {
        "publisher": "National Institute of Standards and Technology (NIST)",
        "title": "Glassy carbon, NIST Standard Reference Material (SRM 3600): hydrogen content, neutron vibrational density of states and heat capacity",
        "authors": [
            "Ronald L. Cappelletti",
            "Terrence J. Udovic",
            "Hui Li",
            "Rick L. Paul",
        ],
        "journal": "Journal of Applied Crystallography",
        "year": 2018,
        "doi": "10.1107/S1600576718010828",
        "official_locator": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=921229",
        "nist_publication_locator": "https://www.nist.gov/publications/glassy-carbon-nist-standard-reference-material-srm-3600-hydrogen-content-neutron",
        "local_path": SOURCE_PATH.relative_to(ROOT).as_posix(),
        "local_sha256": source_sha256,
        "local_bytes": len(raw),
        "page_count": EXPECTED_PAGE_COUNT,
        "source_locators": [
            {
                "locator": "PDF p. 1323, abstract and section 2",
                "content": "The source distinguishes low-hydrogen glassy carbon from graphite and describes the SRM 3600 plate material as commercial Type-2 glassy carbon.",
            },
            {
                "locator": "PDF p. 1326, section 4.1 and Figure 3",
                "content": "Heat-capacity measurements are shown in Figure 3 for 20 K to 295 K; the plotted result is not supplied as machine-readable rows in this archive.",
            },
            {
                "locator": "PDF p. 1326, section 4.1",
                "content": "The paper reports accumulated errors of approximately plus or minus 2 percent at each temperature with a 90 percent confidence interval and discusses a separate systematic discrepancy.",
            },
            {
                "locator": "PDF p. 1327, summary",
                "content": "The work reports heat capacity of low-hydrogen glassy carbon and graphite powder for comparison, not Ding's mode-resolved PBTE C_src.",
            },
        ],
        "material_identity": {
            "primary_sample": "low-hydrogen-content glassy carbon, NIST SRM 3600 / Type-2 material",
            "comparison_sample": "spectroscopic-grade graphite powder, SP-1",
            "ding_ttg_hopg_match": False,
            "match_boundary": "Graphite-like spectral similarity is not accepted as identity with Ding's HOPG TTG PBTE state.",
        },
        "temperature_range_K": {"min": 20.0, "max": 295.0},
        "uncertainty_boundary": {
            "reported_relative_magnitude": 0.02,
            "reported_relative_magnitude_text": "approximately +/-2 percent at each temperature",
            "confidence_level": 0.90,
            "confidence_text": "90 percent confidence interval",
            "is_row_level_standard_uncertainty": False,
            "systematic_discrepancy_discussed": True,
        },
        "data_access": {
            "numeric_rows_accessed": False,
            "figure_digitized": False,
            "raw_machine_readable_payload_stored": False,
            "preprocessing": "No numeric transcription or digitization performed.",
        },
    }
    source_record_sha256 = sha256_bytes(canonical_json(source_record))
    return {
        "schema_version": "t13-nist-srm-3600-heat-capacity-boundary-v1",
        "artifact": "t13_nist_srm_3600_heat_capacity_boundary_audit",
        "generated_at": "2026-08-21",
        "status": "PASS_SCOPED_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY",
        "major_result": {
            "major_result_id": "T13_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "The official NIST SRM 3600 paper is archived with a reproducible PDF hash and source locators.",
                "The source-reported 20 K to 295 K heat-capacity comparison range is recorded.",
                "The source-reported approximately +/-2 percent, 90 percent confidence uncertainty boundary and separate systematic-discrepancy warning are preserved without relabeling them as row-level standard uncertainty.",
                "The material boundary between glassy carbon/graphite-powder comparison data and Ding's HOPG PBTE C_src is explicit.",
            ],
            "equation_or_mapping": {
                "candidate_mass_specific_heat": "c_v^m(T, material)",
                "candidate_volumetric_map": "c_v^V(T, material) = rho(T, material) * c_v^m(T, material)",
                "numeric_mapping_emitted": False,
                "uet_mapping_emitted": False,
            },
            "units": {
                "temperature": "K",
                "specific_heat": "J kg^-1 K^-1 (candidate source quantity; no numeric rows emitted)",
                "volumetric_heat_capacity": "J m^-3 K^-1 (mapping contract only; no numeric rows emitted)",
                "uncertainty": "relative fraction with stated 90 percent confidence boundary",
            },
            "derivation_class": "official source archive and uncertainty/material-boundary audit; no UET derivation",
            "observable": "NIST SRM 3600 heat-capacity comparator availability and uncertainty boundary",
            "data_role": "EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {
                    "path": SOURCE_PATH.relative_to(ROOT).as_posix(),
                    "sha256": source_sha256,
                    "locator": "official NIST PDF, Figure 3 and section 4.1",
                },
                {
                    "path": "docs/core/artifacts/t13_nist_srm_3600_heat_capacity_boundary_audit.json",
                    "source_record_sha256": source_record_sha256,
                },
            ],
            "verification_status": "PASS_SCOPED_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY",
            "open_blockers": [
                "c_v_source_uncertainty_not_closed",
                "direct_volumetric_c_v_or_same_state_Cp_source_missing",
                "material_regime_mapping_to_TTG_not_closed",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "NIST SRM 3600 comparator boundary only; no c_v source closure, Ding C_src, alpha_Phi_K, Full Topic 13, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This closes only a source-traceable heat-capacity comparator boundary. It is not a machine-readable numeric C_src package, not a same-state Ding/HOPG source, not an uncertainty closure for Topic 13, not an independent alpha_Phi_K calibration, not a temperature prediction, and not external validation.",
        },
        "source": {
            **source_record,
            "source_record_sha256": source_record_sha256,
        },
        "checks": checks,
        "acceptance": {
            "accepted_as_heat_capacity_comparator": True,
            "accepted_for_full_topic13": False,
            "accepted_as_independent_csrc_reproduction": False,
            "accepted_as_alpha_phi_k_calibration": False,
            "numeric_rows_emitted": 0,
            "figure_only_payload": True,
            "source_reported_uncertainty_boundary_present": True,
            "row_level_standard_uncertainty_present": False,
            "material_match_to_Ding_TTG": False,
            "target_fit_performed": False,
            "alpha_fit_performed": False,
            "holdout_accessed": False,
        },
        "controlling_blocker": "figure_only_numeric_payload_and_Ding_material_mapping_missing",
        "next_controller": "Acquire a permitted machine-readable same-state heat-capacity or Ding PBTE C_src package with row locators, units, row-level uncertainty, preprocessing, convergence, material identity, and hash; do not digitize Figure 3 into calibration without a declared digitization and uncertainty contract.",
        "claim_boundary": "Comparator source boundary only; no numeric C_src, no UET temperature prediction, no alpha_Phi_K calibration, no holdout use, and no Full Topic 13 closure.",
    }


def main() -> int:
    artifact = build_artifact()
    OUT.write_text(json.dumps(artifact, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "artifact": str(OUT),
                "source_sha256": artifact["source"]["local_sha256"],
                "source_record_sha256": artifact["source"]["source_record_sha256"],
                "numeric_rows_emitted": artifact["acceptance"]["numeric_rows_emitted"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
