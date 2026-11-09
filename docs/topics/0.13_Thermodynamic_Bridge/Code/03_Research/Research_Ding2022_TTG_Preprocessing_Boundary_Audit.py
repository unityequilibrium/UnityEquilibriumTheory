"""Record Ding 2022 TTG preprocessing and uncertainty limits from archived SI."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

import pdfplumber


ROOT = Path(__file__).resolve().parents[5]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
DATA = TOPIC / "Data/03_Research"
REVIEW_PACKAGE = DATA / "ding_2022_supplementary_content_review_package.json"
OUTPUT = TOPIC / "Result/artifacts/ding_2022_ttg_preprocessing_boundary_audit.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _pdf_text(path: Path) -> tuple[int, list[str]]:
    with pdfplumber.open(path) as pdf:
        return len(pdf.pages), [page.extract_text() or "" for page in pdf.pages]


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def build_audit() -> dict[str, Any]:
    review = json.loads(REVIEW_PACKAGE.read_text(encoding="utf-8-sig"))
    pdf_records = review["source_files"]
    texts: dict[str, str] = {}
    page_counts: dict[str, int] = {}
    hashes: dict[str, str] = {}
    hash_matches: dict[str, bool] = {}

    for record in pdf_records:
        source_id = record["source_id"]
        path = ROOT / record["local_path"]
        page_count, page_texts = _pdf_text(path)
        texts[source_id] = _normalise("\n".join(page_texts))
        page_counts[source_id] = page_count
        hashes[source_id] = sha256(path)
        hash_matches[source_id] = hashes[source_id] == record["sha256"]

    m1_page2_path = ROOT / pdf_records[0]["local_path"]
    _, m1_pages = _pdf_text(m1_page2_path)
    methods_page = _normalise(m1_pages[1])
    all_text = " ".join(texts.values())

    method_evidence = {
        "phase_and_amplitude_grating_distinguished": "phase grating" in methods_page
        and "amplitude grating" in methods_page,
        "savitzky_golay_filter_named": "savitzky-golay" in methods_page,
        "filter_used_to_suppress_acoustic_oscillation": "filter out this unwanted oscillation" in methods_page,
        "noise_estimated_from_negative_time_delay": "standard deviation" in methods_page
        and "negative-time-delay" in methods_page,
        "author_reports_typical_error_about_0_01": bool(re.search(r"around 0\.01", methods_page)),
    }
    parameter_search = {
        "window_length_or_size_found": bool(
            re.search(r"(?:window\s+(?:length|size)|(?:length|size)\s+of\s+(?:the\s+)?window)", all_text)
        ),
        "polynomial_order_or_degree_found": bool(
            re.search(r"(?:polynomial\s+(?:order|degree)|(?:order|degree)\s+of\s+(?:the\s+)?polynomial)", all_text)
        ),
    }
    numeric_absence = all(
        not record.get("numeric_payload_present", True)
        and not record.get("machine_readable_rows_present", True)
        for record in pdf_records
    )
    checks = {
        "all_archived_supplement_hashes_match_review_package": all(hash_matches.values()),
        "methods_and_noise_evidence_present": all(method_evidence.values()),
        "filter_parameter_search_reproduces_absence": not any(parameter_search.values()),
        "review_package_reports_no_numeric_payload_or_rows": numeric_absence,
        "holdout_policy_remains_locked": review["holdout_policy"]["xie_2026_accessed"] is False
        and review["holdout_policy"]["calibration_path_may_read_holdout"] is False,
    }
    status = "PASS_SUPPLEMENTARY_METHOD_BOUNDARY" if all(checks.values()) else "FAIL_SOURCE_BOUNDARY_AUDIT"

    return {
        "schema_version": "t13-ding-ttg-preprocessing-boundary-v1",
        "artifact": "ding_2022_ttg_preprocessing_boundary_audit",
        "generated_on": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_DING_TTG_PREPROCESSING_UNCERTAINTY_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "the archived Supplementary Information documents phase/amplitude grating separation and Savitzky-Golay smoothing to suppress acoustic oscillation",
                "the authors estimate waveform error from negative-time-delay baseline variation and report a typical magnitude around 0.01",
                "the reviewed supplementary package contains no machine-readable response rows, mode-resolved C_src payload, or pointwise uncertainty series",
            ],
            "equation_or_mapping": {
                "author_error_method": "sigma_signal estimated from standard deviation of negative-time-delay waveform samples",
                "reported_scale": "typical error around 0.01 in the reported waveform; units/covariance are not specified in the cited methods text",
                "normalized_measurement": "y_TTG=Delta_Tq(t)/Delta_Tq(0)",
                "uet_shape_operator": "y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)",
            },
            "units": {
                "reported_waveform_error": "about 0.01; signal-unit and pointwise covariance contract not supplied",
                "digitization_error": "separate pixel-derived extraction bound; not combined with the reported waveform error",
            },
            "derivation_class": "archived-source methods and uncertainty-boundary audit",
            "observable": "Ding 2022 phase-grating TTG waveform processing and reported baseline noise",
            "data_role": "SUPPLEMENTARY_METHODS_CONTEXT_NOT_NUMERIC_TRAINING_OR_CALIBRATION",
            "evidence_artifacts": [
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_supplementary_content_review_package.json",
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_information.pdf",
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_materials_2.pdf",
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_materials_3.pdf",
            ],
            "verification_status": status,
            "open_blockers": [
                "the reviewed PDFs do not supply a numerical waveform, row-level error/covariance, or enough detail to reproduce the Savitzky-Golay filter window/order",
                "measured markers and simulated curves remain mixed in the Fig. 1d digitization",
                "independent alpha_Phi_K, physical Phi scale, Ding-compatible C_src, and physical transport remain open",
            ],
            "dependency_unlocked": "A source-grounded preprocessing and uncertainty contract for future figure-level comparison only; no numeric-source acceptance, calibration, prediction, or Core unlock",
            "claim_boundary": "This closes the documentary methods boundary only. The approximate error is not a pointwise uncertainty series and is not combined with pixel uncertainty.",
        },
        "verification": {
            "checks": checks,
            "supplementary_source_hashes": hashes,
            "page_counts": page_counts,
            "method_evidence": method_evidence,
            "filter_parameter_search": parameter_search,
            "numeric_rows_or_csrc_admitted": False,
            "reported_error_used_for_calibration": False,
            "pixel_and_waveform_uncertainty_combined": False,
            "holdout_accessed": False,
            "source_data_modified": False,
            "claim_promotion": False,
        },
    }


def main() -> int:
    artifact = build_audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "checks": artifact["verification"]["checks"], "output": str(OUTPUT)}, indent=2))
    return 0 if artifact["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
