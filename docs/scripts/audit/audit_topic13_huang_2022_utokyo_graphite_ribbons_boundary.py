"""Audit the public UTokyo Huang thesis as a Topic 13 source boundary.

The thesis is useful evidence about natural and isotope-purified graphite
ribbon transport, but it is not silently promoted to Ding C_src or a Phi
calibration.  This audit locks the PDF identity and records the reviewed
content boundary: the thesis contains model/measurement context and figures,
not a deposited mode-resolved PBTE payload.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
PDF = RAW / "huang_2022_utokyo_graphite_ribbons_thesis.pdf"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "huang_2022_utokyo_graphite_ribbons_source_package.json"
)
OUT = ROOT / "docs/core/artifacts/t13_huang_2022_utokyo_graphite_ribbons_boundary_audit.json"

EXPECTED_SIZE_BYTES = 25_529_971
EXPECTED_SHA256 = "812ca326070b8036179a0f5fd40addacb88c9bfdf73c2f4c16f0873175a04e6a"
EXPECTED_PAGE_COUNT = 110


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_page_marker_count(payload: bytes) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", payload))


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def make_major_result(raw_sha256: str, passed: bool) -> dict[str, Any]:
    status = (
        "PASS_HUANG_2022_UTOKYO_GRAPHITE_RIBBONS_BOUNDARY"
        if passed
        else "FAIL_HUANG_2022_UTOKYO_GRAPHITE_RIBBONS_BOUNDARY"
    )
    return {
        "major_result_id": "T13_HUANG_2022_UTOKYO_GRAPHITE_RIBBONS_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
        "what_is_closed": [
            "the open UTokyo repository record, DOI, PDF identity, byte hash, and 110-page archive are locked",
            "the thesis reports natural graphite at 1.1% 13C and an isotope-purified comparator at 0.02% 13C with explicit ribbon dimensions",
            "the reviewed content boundary is fixed: graphite transport measurements, Callaway/BTE modelling, and figures are present, but no deposited mode-resolved PBTE payload is present",
            "the route is classified as a provenance/comparator boundary and is not promoted to Ding C_src or Phi calibration",
        ],
        "ontology": {
            "C": "collective system-behaviour coordinate; not graphite heat capacity or a source label",
            "Phi": "effective response variable; no Phi amplitude is present in the thesis",
            "R_gen": "derived history trace; no independent R_gen payload is consumed",
            "R_obs": "observer record remains separate; thesis measurements are external comparator evidence",
        },
        "equation_or_mapping": {
            "required_source_contract": "C_src(T) = sum_mu c_mu(T) in J m^-3 K^-1 remains uninstantiated",
            "source_thermal_model": "C_v(T-T0) = sum_p integral[hbar*omega*(f-f_R_eq) dk/(2*pi)^3] is reported as a model equation, not a deposited C_src row package",
            "thermal_measurement_contract": "Delta_Tq = Delta_u_ph/C_src(T); not instantiated by this route",
            "uet_bridge_contract": "Delta_Tq = alpha_Phi_K * Delta_Phi; no base-Phi amplitude or alpha is present",
            "normalized_observable": "y_TTG = Delta_Tq(t)/Delta_Tq(0); this thesis is not a TTG source-row package",
        },
        "units": {
            "required_c_src": "J m^-3 K^-1",
            "source_model_Cv": "volumetric heat capacity symbol in the model; no numeric row-level unit package",
            "transport_context": "thermal conductivity and thermal decay context; not imported as UET transport",
            "unit_status": "OPEN_C_SRC_UNIT_AND_SOURCE_PROVENANCE",
        },
        "derivation_class": "EXTERNAL_SOURCE_CONTENT_BOUNDARY_NO_UET_DERIVATION",
        "observable": "natural/isotope-purified graphite ribbon thermal-transport comparator",
        "data_role": "EXTERNAL_COMPARATOR_PROVENANCE_BOUNDARY_NOT_CALIBRATION",
        "evidence_artifacts": [
            {"path": relative(PDF), "sha256": raw_sha256, "role": "archived public thesis PDF"},
        ],
        "verification_status": status,
        "open_blockers": [
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "c_v_source_uncertainty_not_closed",
            "material_regime_mapping_to_TTG_not_closed",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "UTokyo graphite comparator provenance only; no Ding C_src, alpha_Phi_K, bridge, transport, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This result closes only the public UTokyo thesis source boundary. It is not numeric Ding C_src, not an accepted same-regime PBTE reproduction, not an independent alpha_Phi_K calibration, not a Phi-to-temperature map, and not Full Topic 13 closure.",
    }


def main() -> int:
    exists = PDF.is_file()
    payload = PDF.read_bytes() if exists else b""
    actual_size = len(payload) if exists else None
    actual_sha256 = digest(PDF) if exists else None
    page_count = pdf_page_marker_count(payload) if exists else None

    # These are content-review declarations with page locators.  No figure
    # digitization, target fitting, or holdout access is part of this audit.
    review_boundary = {
        "page_locators": [
            {"pages": "30-31", "finding": "QE/THIRDORDER/ShengBTE workflow is described, but force-constant and scattering files are not deposited in the thesis archive"},
            {"pages": "32", "finding": "a symbolic volumetric C_v model equation is given without numeric C_src rows or uncertainty table"},
            {"pages": "40-41", "finding": "sample identity records natural graphite at 1.1% 13C and isotope-purified graphite at 0.02% 13C"},
            {"pages": "52-53", "finding": "thermal measurements use decay fits and a reported benchmark heat-capacity input; no machine-readable source table is deposited"},
            {"pages": "62-66", "finding": "raw probe-signal and thermal-conductivity figures are reported; plotted curves are not digitized"},
        ],
        "material_state": {
            "natural_isotope_fraction_13C": 0.011,
            "purified_isotope_fraction_13C": 0.0002,
            "ribbon_length_um": 30,
            "ribbon_thickness_nm": 65,
            "width_range_um": [0.5, 5.0],
            "temperature_range_K": [10, 200],
            "Ding_TTG_material_equivalence": False,
            "Ding_equivalence_reason": "grain morphology, defect state, TTG geometry, and source-response contract are not established as identical",
        },
        "payload_capabilities": {
            "has_machine_readable_numeric_files": False,
            "has_force_constant_files": False,
            "has_shengbte_input_files": False,
            "has_mode_resolved_csrc_rows": False,
            "has_source_grade_csrc_uncertainty": False,
            "has_base_phi_amplitude": False,
            "has_alpha_phi_k_record": False,
            "contains_transport_figures_or_model_context": True,
        },
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "preprocessing": "byte hash and PDF page-marker inventory only; page-level content review recorded above; no curve digitization, unit conversion, PBTE rerun, fitting, or target/holdout access",
    }
    checks = {
        "source_pdf_present": exists,
        "pdf_header_present": payload.startswith(b"%PDF-") if exists else False,
        "size_matches_locked_download": actual_size == EXPECTED_SIZE_BYTES,
        "sha256_matches_locked_download": actual_sha256 == EXPECTED_SHA256,
        "page_marker_count_matches_reviewed_pdf": page_count == EXPECTED_PAGE_COUNT,
        "content_review_has_page_locators": bool(review_boundary["page_locators"]),
        "no_mode_resolved_csrc_rows_in_reviewed_boundary": review_boundary["payload_capabilities"]["has_mode_resolved_csrc_rows"] is False,
        "no_base_phi_or_alpha_record_in_reviewed_boundary": (
            review_boundary["payload_capabilities"]["has_base_phi_amplitude"] is False
            and review_boundary["payload_capabilities"]["has_alpha_phi_k_record"] is False
        ),
        "ding_material_equivalence_not_claimed": review_boundary["material_state"]["Ding_TTG_material_equivalence"] is False,
        "no_holdout_access": review_boundary["holdout_policy"]["xie_2026_accessed"] is False,
        "claim_promotion": False,
    }
    passed = all(
        value for key, value in checks.items() if key != "claim_promotion"
    ) and checks["claim_promotion"] is False
    status = (
        "PASS_HUANG_2022_UTOKYO_GRAPHITE_RIBBONS_BOUNDARY"
        if passed
        else "FAIL_HUANG_2022_UTOKYO_GRAPHITE_RIBBONS_BOUNDARY"
    )
    major = make_major_result(actual_sha256 or "", passed)
    major["verification_status"] = status

    source = {
        "title": "Investigation of hydrodynamic thermal transport in submicroscale graphite ribbons",
        "author": "Xin Huang",
        "repository_record_url": "https://repository.dl.itc.u-tokyo.ac.jp/records/2011088",
        "pdf_url": "https://repository.dl.itc.u-tokyo.ac.jp/record/2011088/files/A39915.pdf",
        "doi": "https://doi.org/10.15083/0002011088",
        "repository_publication_date": "2025-03-27",
        "degree_award_date": "2022-10-13",
        "access_right": "open access repository record",
        "license_observed": "no explicit reuse license stated on the repository landing page",
        "local_path": relative(PDF),
        "size_bytes": actual_size,
        "sha256": actual_sha256,
        "expected_size_bytes": EXPECTED_SIZE_BYTES,
        "expected_sha256": EXPECTED_SHA256,
        "reviewed_page_count": page_count,
    }
    package = {
        "schema_version": "t13-huang-2022-utokyo-graphite-ribbons-source-package-v1",
        "artifact": "t13_huang_2022_utokyo_graphite_ribbons_source_package",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": source,
        "review_boundary": review_boundary,
        "checks": checks,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_action": "Keep this route as a source boundary; obtain an authorized numeric PBTE payload or accepted same-regime reproduction with mode-resolved C_src(T), SI units, uncertainty, convergence, and material/state mapping.",
        "claim_promotion": False,
    }
    write_json(PACKAGE, package)

    evidence = [
        {"path": relative(PACKAGE), "sha256": digest(PACKAGE), "role": "machine-readable UTokyo source package"},
        {"path": relative(PDF), "sha256": actual_sha256, "role": "archived public thesis PDF"},
    ]
    audit = {
        "schema_version": "t13-huang-2022-utokyo-graphite-ribbons-boundary-v1",
        "artifact": "t13_huang_2022_utokyo_graphite_ribbons_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": source,
        "review_boundary": review_boundary,
        "checks": checks,
        "evidence_artifacts": evidence,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": "Pursue an authorized Ding numeric package or accepted same-regime PBTE reproduction; do not relabel the thesis model equation or figures as C_src, and do not infer alpha_Phi_K from this comparator.",
        "claim_promotion": False,
    }
    write_json(OUT, audit)
    print(json.dumps({
        "status": status,
        "artifact": relative(OUT),
        "source_package": relative(PACKAGE),
        "raw_sha256": actual_sha256,
        "page_count": page_count,
        "mode_resolved_csrc_rows": False,
        "base_phi_or_alpha_record": False,
        "holdout_accessed": False,
        "claim_promotion": False,
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
