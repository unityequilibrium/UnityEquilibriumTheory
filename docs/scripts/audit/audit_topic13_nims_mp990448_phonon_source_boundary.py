"""Audit the public NIMS graphite phonon record as a source boundary.

The record is a useful graphite harmonic-phonon provenance route, but its
public archive must not be promoted to numeric C_src evidence when it exposes
only raw structural inputs and figure outputs.  This audit deliberately does
not digitize the thermal-properties figure, fit a bridge, or emit alpha.
"""

from __future__ import annotations

import hashlib
import json
import lzma
import tarfile
import zipfile
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ARCHIVE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "nims_mdr_mp990448_graphite_phonon_dataset.zip"
)
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "nims_mdr_mp990448_phonon_source_package.json"
)
OUT_REL = "docs/core/artifacts/t13_nims_mp990448_phonon_source_boundary_audit.json"
COLLECTION_URL = "https://mdr.nims.go.jp/collections/d7aab932-8512-4b9a-b93d-b61f6e5e7019?locale=en"
DATASET_URL = "https://mdr.nims.go.jp/datasets/5383108b-180d-4eb0-a34f-b28ff9e430d7"
ZIP_URL = f"{DATASET_URL}.zip"
MATERIALS_PROJECT_URL = "https://www.materialsproject.org/materials/mp-990448/"
EXPECTED_ARCHIVE_SHA256 = "eea6ca7569c9442754ce5492ddb2f545186f97ad8b82b209d95f1a80b0158767"
EXPECTED_ARCHIVE_MD5 = "72f4a4e4410f140ba4f8c1ae4725a1a4"
EXPECTED_ARCHIVE_SIZE_BYTES = 133375
EXPECTED_MEMBERS = (
    "band_structure.png",
    "projected_dos.png",
    "thermal_properties.png",
    "total_dos.png",
    "phonopy_params.yaml.xz",
    "vasp-settings.tar.lzma",
)


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
    empty = {
        "archive_sha256": None,
        "archive_md5": None,
        "archive_size_bytes": None,
        "member_count": 0,
        "members": [],
        "phonopy_params": {},
        "vasp_settings": {},
        "payload_capabilities": {
            "has_force_constants_data": False,
            "has_frequency_mesh": False,
            "has_machine_readable_thermal_rows": False,
            "thermal_properties_figure_only": False,
        },
        "checks": {
            "archive_exists": False,
            "archive_hash_matches_locked_download": False,
            "expected_member_set": False,
            "phonopy_raw_payload_checked": False,
            "vasp_settings_payload_checked": False,
            "no_force_constants_data": True,
            "no_frequency_mesh": True,
            "no_machine_readable_thermal_rows": True,
            "thermal_properties_is_figure_only": False,
            "no_holdout_access": True,
            "claim_promotion": False,
        },
    }
    if not path.is_file():
        return empty

    archive_sha256 = digest_path(path)
    archive_md5 = digest_path(path, "md5")
    members: list[dict[str, Any]] = []
    phonopy_params: dict[str, Any] = {}
    vasp_settings: dict[str, Any] = {}
    with zipfile.ZipFile(path) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        for info in infos:
            payload = archive.read(info)
            members.append(
                {
                    "path": info.filename,
                    "size_bytes": info.file_size,
                    "crc32": f"{info.CRC:08x}",
                    "sha256": digest_bytes(payload),
                    "media_type": (
                        "image/png"
                        if info.filename.lower().endswith(".png")
                        else "application/x-xz"
                    ),
                }
            )
            if info.filename == "phonopy_params.yaml.xz":
                text = lzma.decompress(payload).decode("utf-8", errors="replace")
                top_level_keys = [
                    line.split(":", 1)[0].strip()
                    for line in text.splitlines()
                    if line and not line[0].isspace() and ":" in line
                ]
                phonopy_params = {
                    "compressed_sha256": digest_bytes(payload),
                    "decompressed_size_bytes": len(lzma.decompress(payload)),
                    "top_level_keys": top_level_keys,
                    "has_force_constants_data": "\nforce_constants:" in text,
                    "has_frequency_mesh": any(
                        token in text
                        for token in ("\nphonon:", "\nfrequency:", "\nfrequencies:")
                    ),
                    "has_displacements": "\ndisplacements:" in text,
                    "physical_units_declared": {
                        "length": "angstrom",
                        "force_constants": "eV/angstrom^2",
                    },
                }
            if info.filename == "vasp-settings.tar.lzma":
                decompressed = lzma.decompress(payload)
                with tarfile.open(fileobj=__import__("io").BytesIO(decompressed), mode="r:") as settings:
                    setting_members = [member.name for member in settings.getmembers()]
                vasp_settings = {
                    "compressed_sha256": digest_bytes(payload),
                    "decompressed_size_bytes": len(decompressed),
                    "members": setting_members,
                    "contains_force_output": any(
                        token in member.lower()
                        for member in setting_members
                        for token in ("outcar", "force_constants", "vasprun")
                    ),
                }

    member_names = [member["path"] for member in members]
    lower_names = [name.lower() for name in member_names]
    has_machine_readable_thermal_rows = any(
        name in {"thermal_properties.yaml", "thermal_properties.dat", "thermal_properties.csv"}
        or ("thermal" in name and name.endswith((".csv", ".tsv", ".dat")))
        for name in lower_names
    )
    has_force_constants_data = bool(phonopy_params.get("has_force_constants_data")) or bool(
        vasp_settings.get("contains_force_output")
    )
    has_frequency_mesh = bool(phonopy_params.get("has_frequency_mesh"))
    thermal_properties_figure_only = (
        "thermal_properties.png" in member_names and not has_machine_readable_thermal_rows
    )
    payload_capabilities = {
        "has_force_constants_data": has_force_constants_data,
        "has_frequency_mesh": has_frequency_mesh,
        "has_machine_readable_thermal_rows": has_machine_readable_thermal_rows,
        "thermal_properties_figure_only": thermal_properties_figure_only,
    }
    checks = {
        "archive_exists": True,
        "archive_hash_matches_locked_download": (
            archive_sha256 == EXPECTED_ARCHIVE_SHA256
            and archive_md5 == EXPECTED_ARCHIVE_MD5
            and path.stat().st_size == EXPECTED_ARCHIVE_SIZE_BYTES
        ),
        "expected_member_set": tuple(member_names) == EXPECTED_MEMBERS,
        "phonopy_raw_payload_checked": bool(phonopy_params),
        "vasp_settings_payload_checked": bool(vasp_settings),
        "no_force_constants_data": not has_force_constants_data,
        "no_frequency_mesh": not has_frequency_mesh,
        "no_machine_readable_thermal_rows": not has_machine_readable_thermal_rows,
        "thermal_properties_is_figure_only": thermal_properties_figure_only,
        "no_holdout_access": True,
        "claim_promotion": False,
    }
    return {
        "archive_sha256": archive_sha256,
        "archive_md5": archive_md5,
        "archive_size_bytes": path.stat().st_size,
        "member_count": len(members),
        "members": members,
        "phonopy_params": phonopy_params,
        "vasp_settings": vasp_settings,
        "payload_capabilities": payload_capabilities,
        "checks": checks,
    }


def make_major_result(inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "major_result_id": "T13_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "the public NIMS MDR graphite phonon dataset identity, license, archive hash, and member identity are locked",
            "the raw archive is confirmed to expose structural/displacement inputs and figure outputs but no force-constant data, frequency mesh, or machine-readable thermal-property rows",
            "the route is classified as a source payload boundary and not promoted to numeric C_src evidence",
        ],
        "ontology": {
            "C": "collective system-behaviour coordinate; not elemental carbon, a phonon source label, or heat capacity",
            "Phi": "effective response variable; no Phi values are present in this archive",
            "R_gen": "derived history trace; not present as an independent payload",
            "R_obs": "observer record kept separate; no observer record is consumed",
        },
        "equation_or_mapping": {
            "required_source_contract": "C_src(T) = sum_mu c_mu(T) in J m^-3 K^-1",
            "thermal_measurement_contract": "Delta_Tq = Delta_u_ph/C_src(T); not instantiated because frequency/thermal rows are not deposited",
            "uet_bridge_contract": "Delta_Tq = alpha_Phi_K * Delta_Phi; no alpha or base-Phi scale is present",
            "route_decision": "figure-only thermal properties and incomplete raw phonon inputs -> no numeric C_src admission",
        },
        "units": {
            "required_C_src": "J m^-3 K^-1",
            "declared_raw_units": {
                "length": "angstrom",
                "atomic_mass": "AMU",
                "force_constants": "eV/angstrom^2",
            },
            "numeric_C_src_units": "not emitted",
            "unit_status": "OPEN_C_SRC_NUMERIC_SOURCE_AND_UNCERTAINTY",
        },
        "derivation_class": "EXTERNAL_SOURCE_PAYLOAD_BOUNDARY_NO_UET_DERIVATION",
        "observable": "availability of a graphite harmonic phonon payload sufficient for reproducible numeric C_src(T)",
        "data_role": "SOURCE_PAYLOAD_BOUNDARY_NOT_CALIBRATION",
        "evidence_artifacts": [
            {
                "path": ARCHIVE_REL,
                "sha256": inventory["archive_sha256"],
                "role": "public NIMS MDR archive bytes",
            }
        ],
        "verification_status": "PASS_SCOPED_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY",
        "open_blockers": [
            "nims_mp990448_archive_lacks_machine_readable_force_constants_or_frequency_mesh",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "source_grade_C_src_uncertainty_missing",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "NIMS graphite phonon payload boundary only; no C_src, alpha_Phi_K, transport, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This result closes only the NIMS MP-990448 payload boundary. It is not a numeric C_src value, not a Ding-regime reproduction, not an independent alpha_Phi_K calibration, not a Phi-to-temperature map, and not Full Topic 13 closure.",
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
    passed = (
        all(required_checks.values())
        and checks["no_holdout_access"]
        and checks["claim_promotion"] is False
    )
    status = (
        "PASS_SCOPED_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY"
        if passed
        else "FAIL_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY"
    )
    major = make_major_result(inventory)
    major["verification_status"] = status
    source = {
        "title": "Ab-initio phonon calculation for C / P6/mmm (191) / materials id 990448",
        "creator": "Atsushi Togo",
        "publisher": "National Institute for Materials Science",
        "collection_locator": COLLECTION_URL,
        "collection_doi": "https://doi.org/10.48505/nims.4197",
        "dataset_locator": DATASET_URL,
        "zip_locator": ZIP_URL,
        "materials_project_locator": MATERIALS_PROJECT_URL,
        "license": "CC BY 4.0",
        "archive_path": ARCHIVE_REL,
        "archive_sha256": inventory["archive_sha256"],
        "archive_md5": inventory["archive_md5"],
        "archive_size_bytes": inventory["archive_size_bytes"],
        "material_identity": "C / P6/mmm (191), MP-990448; treated as an external harmonic comparator, not UET C",
        "calculation_description": "phonon band structure, phonon DOS, constant-volume thermal-properties figure, and phonon raw data are presented",
    }
    package = {
        "schema_version": "t13-nims-mp990448-phonon-source-package-v1",
        "artifact": "t13_nims_mp990448_phonon_source_package",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": source,
        "inventory": {key: value for key, value in inventory.items() if key != "checks"},
        "row_identity_contract": {
            "identity_key": "archive_sha256 + zip member path + member CRC32 + member size",
            "machine_readable_numeric_rows": [],
            "preprocessing": "read-only ZIP inventory plus decompression of phonopy/settings members; no figure digitization, curve extraction, fitting, unit conversion, or target-curve access",
        },
        "unit_and_uncertainty_boundary": {
            "required_C_src_unit": "J m^-3 K^-1",
            "declared_input_units": "angstrom, AMU, and eV/angstrom^2",
            "numeric_source_units": "not emitted",
            "source_uncertainty": "not deposited",
            "derived_uncertainty": "none computed; no frequency mesh or thermal-property rows are present",
        },
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "claim_promotion": False,
        "controlling_blocker": "nims_mp990448_archive_lacks_machine_readable_force_constants_or_frequency_mesh",
        "next_action": "Obtain a permitted raw force-constant/frequency-mesh package or Ding-compatible numeric C_src source with uncertainty and state mapping; do not digitize the figure or use this route for alpha_Phi_K.",
    }
    package_path = write_json(PACKAGE_REL, package)
    major["evidence_artifacts"].append(
        {
            "path": PACKAGE_REL,
            "sha256": digest_path(package_path),
            "role": "machine-readable NIMS source package",
        }
    )
    audit = {
        "schema_version": "t13-nims-mp990448-phonon-source-boundary-v1",
        "artifact": "t13_nims_mp990448_phonon_source_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": source,
        "inventory": package["inventory"],
        "row_identity_contract": package["row_identity_contract"],
        "unit_and_uncertainty_boundary": package["unit_and_uncertainty_boundary"],
        "payload_capabilities": inventory["payload_capabilities"],
        "checks": checks,
        "evidence_artifacts": [
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
        ],
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
                "has_force_constants_data": inventory["payload_capabilities"]["has_force_constants_data"],
                "has_frequency_mesh": inventory["payload_capabilities"]["has_frequency_mesh"],
                "thermal_properties_figure_only": inventory["payload_capabilities"]["thermal_properties_figure_only"],
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
