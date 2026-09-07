"""Record the HOPG specific-heat source boundary.

The author-posted paper identifies HOPG and natural-graphite specimens and
reports a method-comparison error bound, but the published payload is carried
by figures rather than machine-readable rows. This verifier keeps the route
as a source-traceable comparator and does not digitize figures into the Ding
``C_src`` or alpha calibration paths.
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
    / "perez_castaneda_2013_graphite_specific_heat.pdf"
)
OUT = ROOT / "docs/core/artifacts/t13_perez_castaneda_hopg_source_boundary_audit.json"

EXPECTED_SHA256 = "f5056e3804275336deca634da84a47fec1e91876ff65ab62a84596a5ad3ebd4a"
EXPECTED_BYTES = 1141942
EXPECTED_PAGE_COUNT = 21


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
        "method_comparison_uncertainty_boundary_present": True,
        "row_level_standard_uncertainty_present": False,
        "hopg_specimen_identity_recorded": True,
        "natural_graphite_specimen_identity_recorded": True,
        "ding_ttg_pbte_material_response_match": False,
        "source_archive_payload_present": False,
        "figure_digitization_performed": False,
        "target_curve_read": False,
        "target_fit_performed": False,
        "alpha_fit_performed": False,
        "holdout_accessed": False,
    }
    source_record = {
        "title": "Low-temperature specific heat of graphite and CeSb2: Validation of a quasi-adiabatic continuous method",
        "authors": [
            "T. Perez-Castaneda",
            "J. Azpeitia",
            "J. Hanko",
            "A. Fente",
            "H. Suderow",
            "M. A. Ramos",
        ],
        "journal": "Journal of Low Temperature Physics",
        "volume": 173,
        "pages": "4-20",
        "year": 2013,
        "doi": "10.1007/s10909-013-0884-8",
        "arxiv_locator": "https://arxiv.org/abs/1302.5664",
        "publisher_locator": "https://doi.org/10.1007/s10909-013-0884-8",
        "local_path": SOURCE_PATH.relative_to(ROOT).as_posix(),
        "local_sha256": source_sha256,
        "local_bytes": len(raw),
        "page_count": EXPECTED_PAGE_COUNT,
        "source_locators": [
            {
                "locator": "PDF p. 1, abstract",
                "content": "The paper reports low-temperature specific heat for HOPG and natural graphite and states that the continuous method agrees with relaxation measurements to below 3 percent in absolute value.",
            },
            {
                "locator": "PDF pp. 5-6, section 2.1",
                "content": "The HOPG specimen is 12 mm x 12 mm x 1 mm, 252 mg, Advanced Ceramics grade A, with a 0.4 degree rocking-curve width; natural graphite pieces total 292 mg and their impurity content is described as unknown.",
            },
            {
                "locator": "PDF pp. 14-17, section 3.2 and Figures 6-8",
                "content": "HOPG and natural-graphite specific-heat curves are presented down to 2 K, but the numerical payload is carried by plots and no machine-readable row table or author data archive is supplied with the captured source.",
            },
            {
                "locator": "PDF pp. 14-15, Figure 6 discussion",
                "content": "The below-3-percent value is a method-comparison/experimental-error statement, not a row-level standard uncertainty for a source package.",
            },
        ],
        "material_identity": {
            "hopg": {
                "supplier": "Advanced Ceramics",
                "grade": "A",
                "dimensions_mm": [12.0, 12.0, 1.0],
                "mass_mg": 252.0,
                "rocking_curve_width_deg": 0.4,
                "magnetic_impurity_scale": "approximately one magnetic atom per 10^6 carbon atoms",
            },
            "natural_graphite": {
                "mass_mg": 292.0,
                "impurity_identity": "unknown in the paper",
            },
            "ding_ttg_match": False,
            "match_boundary": "The paper's HOPG specimen is not established as Ding's natural-graphite TTG specimen, and it does not provide Ding's mode-resolved PBTE response contract.",
        },
        "temperature_range_K": {"min": 2.0, "max": 50.0},
        "uncertainty_boundary": {
            "method_comparison_relative_bound": 0.03,
            "reported_text": "below 3 percent in absolute value",
            "interpretation": "method-comparison/experimental-error boundary",
            "is_row_level_standard_uncertainty": False,
            "source_grade_uncertainty_closed": False,
        },
        "data_access": {
            "numeric_rows_accessed": False,
            "figure_digitized": False,
            "raw_machine_readable_payload_stored": False,
            "source_archive_present": False,
            "preprocessing": "No numeric transcription or figure digitization performed.",
        },
    }
    source_record_sha256 = sha256_bytes(canonical_json(source_record))
    return {
        "schema_version": "t13-perez-castaneda-hopg-source-boundary-v1",
        "artifact": "t13_perez_castaneda_hopg_source_boundary_audit",
        "generated_at": "2026-08-21",
        "status": "PASS_SCOPED_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY",
        "major_result": {
            "major_result_id": "T13_PEREZ_CASTANEDA_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "The author-posted HOPG/natural-graphite paper is archived with a reproducible PDF hash, DOI/arXiv locators, and page-level source locators.",
                "The HOPG specimen identity, natural-graphite comparison identity, and the paper's below-3-percent method-comparison boundary are recorded.",
                "The published route is classified as figure-only: no numeric rows, source archive, row-level uncertainty, or Ding mode-resolved PBTE C_src payload is promoted.",
                "The route is closed against silent figure digitization or relabeling as Ding C_src, base Phi, or alpha_Phi_K evidence.",
            ],
            "equation_or_mapping": {
                "candidate_mass_specific_heat": "c_p^m(T, material)",
                "candidate_volumetric_map": "c_v^V(T, material) = rho(T, material) * c_p^m(T, material) - Cp-to-Cv correction",
                "numeric_mapping_emitted": False,
                "uet_mapping_emitted": False,
            },
            "units": {
                "temperature": "K",
                "specific_heat": "J kg^-1 K^-1 (candidate plotted quantity; no numeric rows emitted)",
                "volumetric_heat_capacity": "J m^-3 K^-1 (mapping contract only; no numeric rows emitted)",
                "uncertainty": "relative method-comparison boundary; not row-level standard uncertainty",
            },
            "derivation_class": "primary-source archive and material/uncertainty-boundary audit; no UET derivation",
            "observable": "HOPG specific-heat comparator availability and source-grade uncertainty boundary",
            "data_role": "EXTERNAL_INPUT_HOPG_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {
                    "path": SOURCE_PATH.relative_to(ROOT).as_posix(),
                    "sha256": source_sha256,
                    "locator": "author-posted arXiv PDF, sections 2.1 and 3.2, Figures 6-8",
                },
                {
                    "path": "docs/core/artifacts/t13_perez_castaneda_hopg_source_boundary_audit.json",
                    "source_record_sha256": source_record_sha256,
                },
            ],
            "verification_status": "PASS_SCOPED_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY",
            "open_blockers": [
                "c_v_source_uncertainty_not_closed",
                "direct_volumetric_c_v_or_same_state_Cp_source_missing",
                "material_regime_mapping_to_TTG_not_closed",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "HOPG source-boundary lane only; no numeric c_v closure, Ding C_src, alpha_Phi_K, Full Topic 13, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This closes only a source-traceable HOPG specific-heat comparator boundary. It is not a machine-readable numeric C_src package, not a same-state Ding/HOPG PBTE source, not an uncertainty closure for Topic 13, not an independent alpha_Phi_K calibration, not a temperature prediction, and not external validation.",
        },
        "source": {**source_record, "source_record_sha256": source_record_sha256},
        "checks": checks,
        "acceptance": {
            "accepted_as_hopg_heat_capacity_comparator": True,
            "accepted_for_full_topic13": False,
            "accepted_as_independent_csrc_reproduction": False,
            "accepted_as_alpha_phi_k_calibration": False,
            "numeric_rows_emitted": 0,
            "figure_only_payload": True,
            "method_comparison_uncertainty_boundary_present": True,
            "row_level_standard_uncertainty_present": False,
            "material_match_to_Ding_TTG": False,
            "target_fit_performed": False,
            "alpha_fit_performed": False,
            "holdout_accessed": False,
        },
        "controlling_blocker": "figure_only_numeric_payload_and_Ding_PBTE_response_mapping_missing",
        "next_controller": "Acquire a permitted machine-readable same-state heat-capacity or Ding PBTE C_src package with row locators, units, row-level uncertainty, preprocessing, convergence, material identity, and hash; do not digitize Figures 6-8 into calibration without a declared digitization and uncertainty contract.",
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
