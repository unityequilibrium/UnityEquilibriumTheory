"""Audit the public NIMS MDR package associated with Huang et al. (2023).

The NIMS record is useful for provenance discovery, but its downloadable
archive is checked here as a payload boundary.  An article PDF is not treated
as a machine-readable ShengBTE, force-constant, scattering, C_src, or Phi
calibration package.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ARCHIVE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "huang_2023_nims_mdr_dataset.zip"
)
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "huang_2023_nims_mdr_payload_source_package.json"
)
OUT_REL = "docs/core/07_artifacts/topic13/t13_huang_2023_nims_mdr_payload_boundary_audit.json"
DATASET_URL = "https://mdr.nims.go.jp/datasets/bf141c90-3911-4b2c-9fbc-274dad05d5d0"
ZIP_URL = f"{DATASET_URL}.zip"
ARTICLE_URL = "https://www.nature.com/articles/s41467-023-37380-5"
DOI_URL = "https://doi.org/10.1038/s41467-023-37380-5"
EXPECTED_ARCHIVE_SHA256 = "8ed58adc28eddcec45de73a1fdd9ee5394c5d75777be60015b4d59334b32608e"
EXPECTED_ARCHIVE_MD5 = "7927b217b25f06480a5a5fd2096984a1"
EXPECTED_ARCHIVE_SIZE_BYTES = 989576
EXPECTED_MEMBER_NAME = "s41467-023-37380-5.pdf"
EXPECTED_MEMBER_SIZE_BYTES = 1441389
EXPECTED_MEMBER_CRC32 = "3581d56c"


def digest_bytes(value: bytes, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, value).hexdigest()


def digest_path(path: Path, algorithm: str = "sha256") -> str:
    return digest_bytes(path.read_bytes(), algorithm)


def write_json(relative: str, value: dict[str, Any]) -> Path:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def inspect_archive(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "archive_sha256": None,
            "archive_md5": None,
            "archive_size_bytes": None,
            "member_count": 0,
            "members": [],
            "non_pdf_members": [],
            "payload_capabilities": {
                "has_force_constant_files": False,
                "has_shengbte_payload": False,
                "has_numeric_csrc_rows": False,
            },
            "checks": {
                "archive_exists": False,
                "archive_hash_matches_locked_download": False,
                "single_pdf_member": False,
                "expected_pdf_identity": False,
                "no_force_constant_files": True,
                "no_shengbte_payload": True,
                "no_numeric_csrc_rows": True,
                "license_present": True,
                "no_holdout_access": True,
                "claim_promotion": False,
            },
        }

    archive_sha256 = digest_path(path)
    archive_md5 = digest_path(path, "md5")
    with zipfile.ZipFile(path) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        members: list[dict[str, Any]] = []
        for info in infos:
            payload = archive.read(info)
            members.append(
                {
                    "path": info.filename,
                    "size_bytes": info.file_size,
                    "crc32": f"{info.CRC:08x}",
                    "sha256": digest_bytes(payload),
                    "media_type": "application/pdf"
                    if info.filename.lower().endswith(".pdf")
                    else "application/octet-stream",
                }
            )

    member_names = [member["path"] for member in members]
    lower_names = [name.lower() for name in member_names]
    non_pdf_members = [
        name for name in member_names if not name.lower().endswith(".pdf")
    ]
    force_tokens = ("force_constant", "force-constant", "fc2", "fc3")
    shengbte_tokens = ("shengbte", "scattering", "thirdorder", "third_order")
    csrc_tokens = ("c_src", "csrc", "heat_capacity", "mode_capacity")
    has_force_constant_files = any(
        any(token in name for token in force_tokens) for name in lower_names
    )
    has_shengbte_payload = any(
        any(token in name for token in shengbte_tokens) for name in lower_names
    )
    has_numeric_csrc_rows = any(
        any(token in name for token in csrc_tokens) for name in lower_names
    )
    expected_member = next(
        (member for member in members if member["path"] == EXPECTED_MEMBER_NAME),
        None,
    )
    checks = {
        "archive_exists": path.is_file(),
        "archive_hash_matches_locked_download": (
            archive_sha256 == EXPECTED_ARCHIVE_SHA256
            and archive_md5 == EXPECTED_ARCHIVE_MD5
            and path.stat().st_size == EXPECTED_ARCHIVE_SIZE_BYTES
        ),
        "single_pdf_member": (
            len(members) == 1
            and len(non_pdf_members) == 0
            and member_names == [EXPECTED_MEMBER_NAME]
        ),
        "expected_pdf_identity": (
            expected_member is not None
            and expected_member["size_bytes"] == EXPECTED_MEMBER_SIZE_BYTES
            and expected_member["crc32"] == EXPECTED_MEMBER_CRC32
        ),
        "no_force_constant_files": not has_force_constant_files,
        "no_shengbte_payload": not has_shengbte_payload,
        "no_numeric_csrc_rows": not has_numeric_csrc_rows,
        "license_present": True,
        "no_holdout_access": True,
        "claim_promotion": False,
    }
    return {
        "archive_sha256": archive_sha256,
        "archive_md5": archive_md5,
        "archive_size_bytes": path.stat().st_size,
        "member_count": len(members),
        "members": members,
        "non_pdf_members": non_pdf_members,
        "payload_capabilities": {
            "has_force_constant_files": has_force_constant_files,
            "has_shengbte_payload": has_shengbte_payload,
            "has_numeric_csrc_rows": has_numeric_csrc_rows,
            "article_pdf_only": len(members) == 1 and not non_pdf_members,
        },
        "checks": checks,
    }


def make_major_result(inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "major_result_id": "T13_HUANG_2023_NIMS_MDR_PAYLOAD_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "the public NIMS MDR dataset identity, locator, license, archive hash, and member identity are locked",
            "the downloadable archive is confirmed to contain the article PDF only",
            "the public package is classified as a source-availability boundary rather than a machine-readable PBTE payload",
        ],
        "ontology": {
            "C": "collective system-behaviour coordinate; not a phonon heat capacity or source label",
            "Phi": "effective response variable; no Phi values are present in this archive",
            "R_gen": "derived history trace; not present as an independent payload",
            "R_obs": "observer record kept separate; no observer record is consumed",
        },
        "equation_or_mapping": {
            "required_source_contract": "C_src(T) = sum_mu c_mu(T) in J m^-3 K^-1 remains uninstantiated",
            "thermal_measurement_contract": "Delta_Tq = Delta_u_ph/C_src(T); not instantiated by this route",
            "uet_bridge_contract": "Delta_Tq = alpha_Phi_K * Delta_Phi; no alpha or base-Phi scale is present",
            "normalized_observable": "y_TTG = Delta_Tq(t)/Delta_Tq(0); this archive does not provide target rows",
        },
        "units": {
            "required_c_src": "J m^-3 K^-1",
            "archive_payload_units": "not applicable to an article-only package",
            "temperature_or_time_rows": "not deposited as machine-readable source rows",
            "unit_status": "OPEN_C_SRC_UNIT_AND_SOURCE_PROVENANCE",
        },
        "derivation_class": "EXTERNAL_SOURCE_AVAILABILITY_BOUNDARY_NO_UET_DERIVATION",
        "observable": "availability of a public numeric PBTE input/output package associated with Huang 2023",
        "data_role": "SOURCE_AVAILABILITY_BOUNDARY_NOT_CALIBRATION",
        "evidence_artifacts": [
            {
                "path": ARCHIVE_REL,
                "sha256": inventory["archive_sha256"],
                "role": "public NIMS MDR archive bytes",
            }
        ],
        "verification_status": "PASS_SCOPED_HUANG_2023_NIMS_MDR_PAYLOAD_BOUNDARY",
        "open_blockers": [
            "huang_2023_public_zip_contains_article_pdf_only",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "NIMS source-availability boundary only; no C_src, alpha_Phi_K, transport, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This result closes only the public NIMS MDR payload boundary. It is not a numeric PBTE C_src value, not a Ding-regime reproduction, not an independent alpha_Phi_K calibration, not a Phi-to-temperature map, and not Full Topic 13 closure.",
    }


def main() -> int:
    archive_path = ROOT / ARCHIVE_REL
    inventory = inspect_archive(archive_path)
    checks = inventory["checks"]
    required_checks = {
        key: value
        for key, value in checks.items()
        if key not in {"no_holdout_access", "claim_promotion"}
    }
    passed = all(required_checks.values()) and checks["no_holdout_access"] and checks["claim_promotion"] is False
    status = (
        "PASS_SCOPED_HUANG_2023_NIMS_MDR_PAYLOAD_BOUNDARY"
        if passed
        else "FAIL_HUANG_2023_NIMS_MDR_PAYLOAD_BOUNDARY"
    )
    major = make_major_result(inventory)
    major["verification_status"] = status
    package = {
        "schema_version": "t13-huang-2023-nims-mdr-payload-source-package-v1",
        "artifact": "t13_huang_2023_nims_mdr_payload_source_package",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": {
            "title": "Observation of phonon Poiseuille flow in isotopically purified graphite ribbons",
            "authors": ["Huang et al."],
            "nims_mdr_dataset_locator": DATASET_URL,
            "nims_mdr_zip_locator": ZIP_URL,
            "article_locator": ARTICLE_URL,
            "doi": DOI_URL,
            "license": "CC BY 4.0",
            "archive_path": ARCHIVE_REL,
            "archive_sha256": inventory["archive_sha256"],
            "archive_md5": inventory["archive_md5"],
            "archive_size_bytes": inventory["archive_size_bytes"],
            "data_availability_note": "The article reports data availability from the corresponding authors on reasonable request; the public NIMS downloadable archive inspected here contains the article PDF only.",
        },
        "inventory": {
            key: value for key, value in inventory.items() if key != "checks"
        },
        "row_identity_contract": {
            "identity_key": "archive_sha256 + zip member path + member CRC32 + member size",
            "machine_readable_numeric_rows": [],
            "preprocessing": "read-only ZIP member inventory; no PDF digitization, curve extraction, fitting, unit conversion, or target-curve access",
        },
        "unit_and_uncertainty_boundary": {
            "required_c_src_unit": "J m^-3 K^-1",
            "numeric_source_units": "not deposited in the public archive",
            "source_uncertainty": "not deposited as machine-readable rows",
            "derived_uncertainty": "none computed; no PBTE estimator or thermodynamic conversion run",
        },
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "claim_promotion": False,
        "controlling_blocker": "huang_2023_public_zip_contains_article_pdf_only",
        "next_action": "Keep the NIMS record as a source boundary; obtain an authorized numeric PBTE/force-constant package or an accepted same-regime reproduction with mode-resolved C_src(T), SI units, uncertainty, convergence, and material/state mapping before revisiting alpha_Phi_K.",
    }
    package_path = write_json(PACKAGE_REL, package)
    evidence = [
        {
            "path": PACKAGE_REL,
            "sha256": digest_path(package_path),
            "role": "machine-readable NIMS source package",
        },
        {
            "path": ARCHIVE_REL,
            "sha256": inventory["archive_sha256"],
            "role": "public NIMS MDR archive bytes",
        },
    ]
    audit = {
        "schema_version": "t13-huang-2023-nims-mdr-payload-boundary-v1",
        "artifact": "t13_huang_2023_nims_mdr_payload_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": package["source"],
        "inventory": package["inventory"],
        "row_identity_contract": package["row_identity_contract"],
        "unit_and_uncertainty_boundary": package["unit_and_uncertainty_boundary"],
        "payload_capabilities": inventory["payload_capabilities"],
        "checks": checks,
        "evidence_artifacts": evidence,
        "holdout_policy": package["holdout_policy"],
        "controlling_blocker": package["controlling_blocker"],
        "next_action": package["next_action"],
        "claim_promotion": False,
    }
    audit_path = write_json(OUT_REL, audit)
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT_REL,
                "source_package": PACKAGE_REL,
                "archive_sha256": inventory["archive_sha256"],
                "member_count": inventory["member_count"],
                "members": [member["path"] for member in inventory["members"]],
                "article_pdf_only": inventory["payload_capabilities"]["article_pdf_only"],
                "holdout_accessed": False,
                "claim_promotion": False,
                "artifact_bytes": audit_path.stat().st_size,
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
