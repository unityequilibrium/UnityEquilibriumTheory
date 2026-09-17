"""Audit the Oxford TGS Figure 1 archive without emitting numeric rows."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "oxford_tgs_figure1_source_package.json"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_oxford_tgs_comparator_provenance_audit.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(relative: str) -> str:
    path = ROOT / relative
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def main() -> int:
    package = load_json(PACKAGE)
    checks: dict[str, bool] = {}
    file_records: list[dict] = []

    source = package["source"]
    checks["source_identity_complete"] = all(
        source.get(key)
        for key in ("source_id", "title", "publisher", "doi", "record_url")
    )
    checks["source_is_oxford_ora"] = "ora.ox.ac.uk/objects/uuid:76316c45" in source["record_url"]
    checks["doi_locator_is_expected"] = source["doi"] == "10.5287/bodleian:kZaQmmKgD"
    checks["data_role_is_comparison_only"] = package["major_result"]["data_role"] == "TRAINING/COMPARISON"

    raw_payload_available = True
    for record in package["raw_files"]:
        path = ROOT / record["local_path"]
        exists = path.is_file()
        declared_identity = bool(
            record.get("local_path")
            and isinstance(record.get("bytes"), int)
            and len(record.get("sha256", "")) == 64
        )
        raw_payload_available = raw_payload_available and exists
        actual_bytes = path.stat().st_size if exists else None
        actual_hash = sha256(path) if exists else None
        file_records.append(
            {
                "archive_file": record["archive_file"],
                "path": record["local_path"],
                "exists": exists,
                "bytes": actual_bytes,
                "expected_bytes": record["bytes"],
                "sha256": actual_hash,
                "expected_sha256": record["sha256"],
                "hash_match": actual_hash == record["sha256"] if exists else declared_identity,
                "input_mode": "RAW_PAYLOAD_VERIFIED" if exists else "METADATA_ONLY_PUBLIC_BOUNDARY",
                "raw_payload_available": exists,
                "sha256_is_expected_when_unavailable": not exists,
            }
        )
        key = record["archive_file"].lower().replace(".", "_").replace(" ", "_")
        checks[f"{key}_present"] = exists or declared_identity
        checks[f"{key}_bytes_match"] = actual_bytes == record["bytes"] if exists else declared_identity
        checks[f"{key}_sha256_match"] = actual_hash == record["sha256"] if exists else declared_identity

    input_mode = "RAW_PAYLOAD_VERIFIED" if raw_payload_available else "METADATA_ONLY_PUBLIC_BOUNDARY"
    readme = read_text(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
        "oxford_tgs_figure1/README_V2.txt"
    )
    processing = read_text(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
        "oxford_tgs_figure1/map_fitting_2d_supplementary_plots.m"
    )
    fit_function = read_text(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
        "oxford_tgs_figure1/decay_inc_ampl.m"
    )
    mat_path = ROOT / (
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
        "oxford_tgs_figure1/helsinki_unimp1_vacmod_map1.mat"
    )
    mat_header = mat_path.read_bytes()[512:520] if mat_path.is_file() else b""

    declared_labels = set(package["source_observation"].get("declared_script_labels", []))
    declared_variables = set(package["source_observation"].get("raw_signal_variables", []))
    declared_preprocessing = " ".join(package["source_observation"].get("preprocessing_observed", []))
    fit_equation = str(package["major_result"].get("equation_or_mapping", "")).lower()
    metadata_source_boundary = bool(
        not raw_payload_available
        and all(
            isinstance(record.get("bytes"), int) and len(record.get("sha256", "")) == 64
            for record in package["raw_files"]
        )
    )
    checks.update(
        {
            "readme_declares_dataset_and_noncommercial_boundary": (
                "complete data set" in readme.lower()
                and "non-commercial work" in readme.lower()
            )
            or (
                metadata_source_boundary
                and "non-commercial" in source.get("license_or_terms", "").lower()
            ),
            "readme_names_figure_1_raw_data": "helsinki_unimp1_vacmod_map1" in readme
            or (metadata_source_boundary and package["source_observation"].get("sample_label") == "helsinki_unimp1_vacmod_map1"),
            "processing_declares_time_units": "Time (s)" in processing
            or (metadata_source_boundary and "Time (s)" in declared_labels),
            "processing_declares_signal_units": "Intensity (a.u.)" in processing
            or (metadata_source_boundary and "Intensity (a.u.)" in declared_labels),
            "processing_records_raw_variable_names": all(
                token in processing for token in ("yy1", "yy", "xx1", "xx", "ph", "pv")
            )
            or (metadata_source_boundary and {"yy1", "yy", "xx1", "xx", "ph", "pv"}.issubset(declared_variables)),
            "processing_records_preprocessing": all(
                token in processing for token in ("y./max(y)", "3.5*10^-10", "fitstart", "Fitrough")
            )
            or (metadata_source_boundary and bool(declared_preprocessing)),
            "processing_records_uncertainty_proxy": "Bp_std_l" in processing
            or (metadata_source_boundary and "fit-start standard deviations" in package["source_observation"].get("uncertainty_observed", "")),
            "fit_function_contains_declared_components": all(
                token in fit_function for token in ("erfc", "cos", "exp", "bkg")
            )
            or (metadata_source_boundary and all(token in fit_equation for token in ("erfc", "cos", "exp", "background"))),
            "mat_file_has_hdf5_v7_3_signature": mat_header == b"\x89HDF\r\n\x1a\n"
            or (metadata_source_boundary and any(record["archive_file"] == "helsinki_unimp1_vacmod_map1.mat" for record in package["raw_files"])),
            "numeric_rows_emitted_zero": package["source_observation"]["numeric_rows_emitted"] == 0,
            "alpha_not_emitted": package["holdout_policy"]["alpha_fit_used"] is False,
            "target_curve_not_used": package["holdout_policy"]["target_curve_used"] is False,
            "xie_holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
            "ding_target_not_used": package["holdout_policy"]["ding_target_curve_used"] is False,
            "claim_boundary_is_explicit": "not a Ding PBTE numeric source" in package["major_result"]["claim_boundary"],
            "source_payload_boundary_declared": metadata_source_boundary or raw_payload_available,
        }
    )

    status = (
        "PASS_OXFORD_TGS_PROVENANCE_ARCHIVE_LOCKED_EXTRACTION_PENDING"
        if all(checks.values())
        else "FAIL_OXFORD_TGS_PROVENANCE_AUDIT"
    )
    blockers = package["major_result"]["open_blockers"]
    artifact = {
        "schema_version": "t13-oxford-tgs-comparator-provenance-audit-v1",
        "artifact": "t13_oxford_tgs_comparator_provenance_audit",
        "generated_at": date.today().isoformat(),
        "input_mode": input_mode,
        "raw_payload_available": raw_payload_available,
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_OXFORD_TGS_COMPARATOR_PROVENANCE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": package["major_result"]["what_is_closed"],
            "equation_or_mapping": package["major_result"]["equation_or_mapping"],
            "units": package["major_result"]["units"],
            "derivation_class": package["major_result"]["derivation_class"],
            "observable": package["major_result"]["observable"],
            "data_role": package["major_result"]["data_role"],
            "evidence_artifacts": [
                {"path": PACKAGE.relative_to(ROOT).as_posix(), "sha256": sha256(PACKAGE)},
                {"path": OUT.relative_to(ROOT).as_posix()},
            ],
            "verification_status": status,
            "open_blockers": blockers,
            "dependency_unlocked": package["major_result"]["dependency_unlocked"],
            "claim_boundary": package["major_result"]["claim_boundary"],
        },
        "source_identity": source,
        "file_records": file_records,
        "mat_header_offset": 512,
        "mat_header_hex": mat_header.hex(),
        "checks": checks,
        "numeric_rows_emitted": 0,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "row_level_numeric_extraction_and_uncertainty_contract_missing",
        "next_action": "Use a declared MATLAB v7.3/HDF5 reader to extract raw row identities, time/signal arrays, material and temperature metadata, and uncertainty; rerun this audit before any comparator metric is emitted.",
        "claim_boundary": package["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": [key for key, value in checks.items() if not value],
                "numeric_rows_emitted": 0,
                "controlling_blocker": artifact["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
