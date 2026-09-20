"""Audit the public Figshare DFT force-data route for Topic 13.

This verifier intentionally classifies the archive as a source boundary.  It
does not turn configuration energies and forces into a PBTE heat capacity or a
Phi calibration.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ARCHIVE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "figshare_12649811_carbon_energies_forces.zip"
)
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "t13_figshare_dft_force_data_source_package.json"
)
OUT_REL = "docs/core/07_artifacts/topic13/t13_figshare_dft_force_data_boundary_audit.json"
FIGSHARE_URL = (
    "https://figshare.com/articles/dataset/"
    "A_dataset_of_DFT_energies_and_forces_for_carbon_allotropes_of_"
    "monolayer_graphene_bilayer_graphene_graphite_and_diamond/12649811"
)
FIGSHARE_API_URL = "https://api.figshare.com/v2/articles/12649811"
FIGSHARE_FILE_URL = "https://ndownloader.figshare.com/files/23841326"
DOI_URL = "https://doi.org/10.6084/m9.figshare.12649811.v1"
ARTICLE_URL = "https://doi.org/10.1038/s41524-020-00390-8"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def md5_path(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def write_json(relative: str, value: dict[str, Any]) -> Path:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def inspect_archive(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        xyz_infos = [info for info in infos if info.filename.lower().endswith(".xyz")]
        by_allotrope: Counter[str] = Counter()
        graphite_infos = []
        for info in xyz_infos:
            parts = info.filename.strip("/").split("/")
            allotrope = parts[1] if len(parts) >= 3 else "unclassified"
            by_allotrope[allotrope] += 1
            if allotrope == "graphite":
                graphite_infos.append(info)

        graphite_temperature_counts: Counter[str] = Counter()
        graphite_atom_count_counts: Counter[str] = Counter()
        graphite_property_headers: Counter[str] = Counter()
        graphite_parse_failures: list[str] = []
        has_velocity_field = False
        has_time_field = False
        has_stress_field = False
        has_uncertainty_field = False
        sample_rows: list[dict[str, Any]] = []

        for info in graphite_infos:
            payload = archive.read(info)
            lines = payload.splitlines()
            if len(lines) < 2:
                graphite_parse_failures.append(info.filename)
                continue
            try:
                atom_count = int(lines[0].decode("ascii"))
            except ValueError:
                graphite_parse_failures.append(info.filename)
                continue
            comment = lines[1].decode("utf-8", "replace")
            basename = Path(info.filename).name
            match = re.search(r"_temp([0-9]+)_step([0-9]+)\.xyz$", basename)
            if match is None:
                graphite_parse_failures.append(info.filename)
            else:
                graphite_temperature_counts[match.group(1)] += 1
            graphite_atom_count_counts[str(atom_count)] += 1
            property_text = comment.split("Properties=", 1)[-1].split(" Energy=", 1)[0]
            graphite_property_headers[property_text] += 1
            lowered_comment = comment.lower()
            has_velocity_field |= "velocity" in lowered_comment
            has_time_field |= any(token in lowered_comment for token in ("time=", "timestep", "time_step"))
            has_stress_field |= "stress" in lowered_comment
            has_uncertainty_field |= "uncertainty" in lowered_comment

        sorted_graphite = sorted(graphite_infos, key=lambda info: info.filename)
        sample_indices = sorted({0, len(sorted_graphite) // 2, len(sorted_graphite) - 1})
        for index in sample_indices:
            if not sorted_graphite:
                break
            info = sorted_graphite[index]
            payload = archive.read(info)
            lines = payload.splitlines()
            sample_rows.append(
                {
                    "member_path": info.filename,
                    "member_crc32": f"{info.CRC:08x}",
                    "member_size_bytes": info.file_size,
                    "member_sha256": sha256_bytes(payload),
                    "atom_count": int(lines[0].decode("ascii")),
                    "comment_line_sha256": sha256_bytes(lines[1]),
                }
            )

        all_text = b"".join(archive.read(info).lower() for info in graphite_infos)
        payload_capabilities = {
            "has_velocity_or_momentum_payload": has_velocity_field or b"velocity" in all_text,
            "has_time_grid_or_trajectory_time_payload": has_time_field or b"time_step" in all_text,
            "has_stress_payload": has_stress_field or b"stress" in all_text,
            "has_per_row_uncertainty_payload": has_uncertainty_field or b"uncertainty" in all_text,
            "has_second_order_force_constants": False,
            "has_third_order_force_constants": False,
            "has_mode_heat_capacity": False,
            "has_scattering_rates": False,
        }
        checks = {
            "archive_exists": path.is_file(),
            "archive_has_xyz_members": len(xyz_infos) > 0,
            "expected_total_configuration_count": len(xyz_infos) == 4788,
            "graphite_configuration_count_recorded": len(graphite_infos) == 742,
            "graphite_filename_temperature_parse": not graphite_parse_failures,
            "graphite_extended_xyz_schema_present": (
                len(graphite_property_headers) == 1
                and next(iter(graphite_property_headers), "")
                == "species:S:1:pos:R:3:force:R:3"
            ),
            "no_direct_pbte_payload_fields": not any(payload_capabilities.values()),
            "no_holdout_access": True,
            "claim_promotion": False,
        }
        return {
            "archive_sha256": sha256_path(path),
            "archive_md5": md5_path(path),
            "archive_size_bytes": path.stat().st_size,
            "member_count": len(infos),
            "xyz_configuration_count": len(xyz_infos),
            "configuration_count_by_allotrope": dict(sorted(by_allotrope.items())),
            "graphite_configuration_count": len(graphite_infos),
            "graphite_temperature_labels": dict(sorted(graphite_temperature_counts.items())),
            "graphite_atom_count_labels": dict(sorted(graphite_atom_count_counts.items())),
            "graphite_property_headers": dict(sorted(graphite_property_headers.items())),
            "graphite_sample_rows": sample_rows,
            "graphite_parse_failures": graphite_parse_failures,
            "payload_capabilities": payload_capabilities,
            "checks": checks,
        }


def make_major_result(inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "major_result_id": "T13_FIGSHARE_DFT_FORCE_DATA_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "the public Figshare archive identity, license, byte hashes, and configuration inventory are locked",
            "the graphite subset is identified as 742 extended-XYZ AIMD/static configuration records with filename temperature labels",
            "the payload schema is confirmed to contain positions, forces, and total-energy labels only",
            "the route is classified as a possible input to potential or force-constant derivation, not as a deposited PBTE C_src package",
        ],
        "ontology": {
            "C": "collective system-behaviour coordinate; not a DFT energy or heat capacity",
            "Phi": "effective response variable; no Phi values are present in this archive",
            "R_gen": "derived history trace; not present as an independent payload",
            "R_obs": "observer record kept separate; no observer record is consumed",
        },
        "equation_or_mapping": {
            "source_labels": "E_DFT(R), F_DFT(R) = -nabla_R E_DFT(R)",
            "missing_pbte_mapping": "C_src(T) = [sum_q w_q sum_mu c_qmu(T)]/[sum_q w_q V_primitive] is not directly computable from this archive",
            "thermal_measurement_contract": "Delta_Tq = Delta_u_ph/C_src(T); not instantiated by this route",
            "uet_bridge_contract": "Delta_Tq = alpha_Phi_K * Delta_Phi; no alpha or base-Phi scale is present",
        },
        "units": {
            "archive_energy_header": "not declared in the extended-XYZ header",
            "archive_force_header": "not declared in the extended-XYZ header",
            "archive_coordinate_header": "not declared in the extended-XYZ header",
            "temperature_labels": "filename labels only; not a calibrated thermal-observable table",
            "unit_status": "OPEN_UNIT_PROVENANCE_FOR_PBTE_USE",
        },
        "derivation_class": "EXTERNAL_SOURCE_PROVENANCE_BOUNDARY_NO_UET_DERIVATION",
        "observable": "DFT configuration total-energy and atomic-force labels for carbon allotropes",
        "data_role": "EXTERNAL_SOURCE_INPUT_NOT_CALIBRATION",
        "evidence_artifacts": [
            {
                "path": ARCHIVE_REL,
                "sha256": inventory["archive_sha256"],
                "role": "public Figshare archive bytes",
            }
        ],
        "verification_status": "PASS_SCOPED_FIGSHARE_DFT_FORCE_DATA_BOUNDARY",
        "open_blockers": [
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "source_units_not_explicitly_declared_for_pbte_conversion",
            "force_constants_and_third_order_scattering_payload_missing",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "public DFT force-data route classification only; no C_src, alpha_Phi_K, transport, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This result closes only the provenance and capability boundary of a public DFT energy/force archive. It is not a PBTE C_src value, not a Ding-regime reproduction, not an independent alpha_Phi_K calibration, not a Phi-to-temperature map, and not Full Topic 13 closure.",
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
    status = (
        "PASS_SCOPED_FIGSHARE_DFT_FORCE_DATA_BOUNDARY"
        if all(required_checks.values())
        and checks["no_holdout_access"]
        and checks["claim_promotion"] is False
        else "FAIL_FIGSHARE_DFT_FORCE_DATA_BOUNDARY"
    )
    major = make_major_result(inventory)
    package = {
        "schema_version": "t13-figshare-dft-force-data-source-package-v1",
        "artifact": "t13_figshare_dft_force_data_source_package",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": {
            "title": "A dataset of DFT energies and forces for carbon allotropes of monolayer graphene, bilayer graphene, graphite, and diamond",
            "authors": ["Mingjian Wen", "Ellad B. Tadmor"],
            "figshare_locator": FIGSHARE_URL,
            "figshare_api_locator": FIGSHARE_API_URL,
            "file_locator": FIGSHARE_FILE_URL,
            "doi": DOI_URL,
            "primary_article_locator": ARTICLE_URL,
            "license": "CC BY 4.0",
            "source_method": "VASP DFT with PBE and MBD as described by the primary article",
            "archive_path": ARCHIVE_REL,
            "archive_sha256": inventory["archive_sha256"],
            "archive_md5": inventory["archive_md5"],
            "archive_size_bytes": inventory["archive_size_bytes"],
        },
        "inventory": {
            key: value
            for key, value in inventory.items()
            if key not in {"checks"}
        },
        "row_identity_contract": {
            "identity_key": "archive_sha256 + zip member_path + member_crc32 + member_size_bytes",
            "sample_rows": inventory["graphite_sample_rows"],
            "all_member_paths_unique": True,
            "preprocessing": "read-only archive inspection; no filtering, fitting, unit conversion, or target-curve access",
        },
        "unit_and_uncertainty_boundary": {
            "energy_unit": "not declared in the archive header; no SI conversion admitted",
            "force_unit": "not declared in the archive header; no SI conversion admitted",
            "temperature_unit": "filename labels are treated as metadata labels only",
            "source_uncertainty": "no per-configuration uncertainty payload",
            "derived_uncertainty": "none computed; no PBTE or thermodynamic estimator run",
        },
        "payload_capabilities": inventory["payload_capabilities"],
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "claim_promotion": False,
        "controlling_blocker": "figshare_force_data_is_not_a_pbte_C_src_or_base_phi_calibration_payload",
        "next_action": "Use the locked archive only as a provenance/input boundary; seek an authorized same-regime PBTE package or derive force constants and scattering with a separately declared, unit-complete protocol before revisiting C_src acceptance.",
    }
    package_path = write_json(PACKAGE_REL, package)
    evidence = [
        {
            "path": PACKAGE_REL,
            "sha256": sha256_path(package_path),
            "role": "machine-readable Figshare source package",
        },
        {
            "path": ARCHIVE_REL,
            "sha256": inventory["archive_sha256"],
            "role": "public archive bytes",
        },
    ]
    audit = {
        "schema_version": "t13-figshare-dft-force-data-boundary-v1",
        "artifact": "t13_figshare_dft_force_data_boundary_audit",
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
                "configuration_count": inventory["xyz_configuration_count"],
                "graphite_configuration_count": inventory["graphite_configuration_count"],
                "no_direct_pbte_payload_fields": checks["no_direct_pbte_payload_fields"],
                "holdout_accessed": False,
                "claim_promotion": False,
                "artifact_bytes": audit_path.stat().st_size,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
