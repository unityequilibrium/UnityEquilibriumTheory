"""Audit whether the official Ding 2022 PMC OA package exposes PBTE inputs."""

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[3]
TOPIC_DATA = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
PACKAGE = TOPIC_DATA / "ding_2022_pbte_numeric_input_availability_package.json"
OA_RECORD = TOPIC_DATA / "raw/ding_2022_pmc_oa_record.xml"
INVENTORY = TOPIC_DATA / "raw/ding_2022_pmc_s3_inventory.xml"
METADATA = TOPIC_DATA / "raw/ding_2022_pmc_object_metadata.json"
FULL_TEXT = TOPIC_DATA / "raw/ding_2022_pmc_full_text.txt"
SUPPLEMENT = TOPIC_DATA / "raw/ding_2022_supplementary_information.pdf"
SUPPLEMENTARY_FILES = {
    "SUPPLEMENTARY_INFORMATION": SUPPLEMENT,
    "SUPPLEMENTARY_MATERIALS_2": TOPIC_DATA
    / "raw/ding_2022_supplementary_materials_2.pdf",
    "SUPPLEMENTARY_MATERIALS_3": TOPIC_DATA
    / "raw/ding_2022_supplementary_materials_3.pdf",
}
OUT = ROOT / "docs/core/artifacts/t13_ding_pbte_numeric_input_availability_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalize(text: str) -> str:
    return text.replace("\u2009", " ").replace("\u00a0", " ")


def main() -> int:
    package = load(PACKAGE)
    metadata = load(METADATA)
    full_text = normalize(FULL_TEXT.read_text(encoding="utf-8-sig"))
    inventory_root = ET.parse(INVENTORY).getroot()
    object_keys = [
        item.findtext("{*}Key", default="")
        for item in inventory_root.findall("{*}Contents")
    ]
    oa_record = ET.parse(OA_RECORD).getroot().find(".//record")
    if oa_record is None:
        raise RuntimeError("PMC OA record element is missing")
    media_urls = metadata.get("media_urls", [])
    media_paths = [urlparse(url).path for url in media_urls]
    media_suffixes = sorted({Path(path).suffix.lower() for path in media_paths})
    reproduction_markers = (
        "force_constants",
        "force_sets",
        "poscar",
        "control",
        "shengbte",
        "phonopy",
        "scattering",
        "heat_capacity",
        "c_mu",
    )
    reproduction_extensions = {
        ".csv",
        ".tsv",
        ".dat",
        ".hdf5",
        ".h5",
        ".yaml",
        ".yml",
        ".npz",
        ".npy",
        ".zip",
        ".tar",
        ".gz",
    }
    candidate_payloads = [
        key
        for key in object_keys
        if any(marker in key.lower() for marker in reproduction_markers)
        or Path(key).suffix.lower() in reproduction_extensions
    ]
    archived = {item["role"]: item for item in package["archived_records"]}
    paths = {
        "PMC_OA_API_RECORD": OA_RECORD,
        "PMC_S3_PREFIX_INVENTORY": INVENTORY,
        "PMC_OBJECT_METADATA": METADATA,
        "PMC_FULL_TEXT": FULL_TEXT,
        **SUPPLEMENTARY_FILES,
    }
    hashes_match = all(
        path.stat().st_size == archived[role]["bytes"]
        and sha256(path) == archived[role]["sha256"]
        for role, path in paths.items()
    )
    checks = {
        "all_archived_records_match_hash_and_size": hashes_match,
        "oa_record_identity_matches": oa_record.attrib.get("id") == "PMC8755757",
        "oa_record_license_is_cc_by": oa_record.attrib.get("license") == "CC BY",
        "oa_record_not_retracted": oa_record.attrib.get("retracted") == "no",
        "publisher_source_identity_is_locked": (
            package["source_identity"]["doi"] == "10.1038/s41467-021-27907-z"
            and package["source_identity"]["publisher_url"]
            == "https://www.nature.com/articles/s41467-021-27907-z"
        ),
        "publisher_data_availability_statement_is_locked": (
            package["source_identity"]["publisher_data_availability_locator"]
            == "Nature Communications article, Data availability section"
            and package["source_identity"]["publisher_data_availability_statement"]
            == "The data that support the findings of this study are available from the corresponding author on reasonable request."
        ),
        "s3_prefix_is_complete_not_truncated": inventory_root.findtext(
            "{*}IsTruncated"
        )
        == "false",
        "s3_object_count_is_11": len(object_keys)
        == package["official_object_inventory"]["object_count"]
        == 11,
        "s3_object_names_match_package": object_keys
        == package["official_object_inventory"]["objects"],
        "media_payload_count_is_7": len(media_urls)
        == package["official_object_inventory"]["media_payload_count"]
        == 7,
        "all_three_supplementary_pdfs_are_archived": all(
            path.exists()
            and path.stat().st_size == archived[role]["bytes"]
            and sha256(path) == archived[role]["sha256"]
            for role, path in SUPPLEMENTARY_FILES.items()
        ),
        "media_payloads_are_figures_or_pdfs_only": media_suffixes == [".jpg", ".pdf"],
        "no_reproduction_payload_candidate_in_oa_prefix": candidate_payloads == [],
        "data_availability_is_author_request": (
            "available from the corresponding author on reasonable request"
            in full_text
        ),
        "published_spec_names_vasp_and_optb88": "Vienna Ab Initio Package"
        in full_text
        and "optB88" in full_text,
        "published_spec_names_supercells_and_mesh": all(
            token in full_text
            for token in (
                "24 × 24 × 10",
                "5 × 5 × 2",
                "4 × 4 × 2",
                "16 × 16 × 8",
            )
        ),
        "published_spec_names_phonopy_and_shengbte": "Phonopy" in full_text
        and "ShengBTE" in full_text,
        "missing_input_list_is_explicit": len(package["missing_reproduction_inputs"])
        >= 10,
        "author_request_not_claimed_executed": package["availability_contract"][
            "author_request_route"
        ]
        == "OPEN_NOT_EXECUTED",
        "xie_holdout_not_accessed": package["holdout_policy"][
            "xie_2026_accessed"
        ]
        is False,
        "xie_holdout_not_consumed": package["holdout_policy"][
            "xie_2026_source_data_consumed"
        ]
        is False,
    }
    status = (
        "PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO"
        if all(checks.values())
        else "FAIL_OA_NUMERIC_INPUT_AVAILABILITY_AUDIT"
    )
    open_blockers = [
        "ding_pbte_author_data_or_independent_reproduction_package_missing",
        "ding_pbte_numeric_C_src_T_not_packaged",
        "ding_pbte_C_src_uncertainty_or_convergence_contract_missing",
        "base_Phi_to_Delta_u_ph_mapping_not_derived",
        "e0_energy_density_scale_not_source_locked",
    ]
    report = {
        "schema_version": "t13-ding-pbte-numeric-input-availability-audit-v1",
        "artifact": "t13_ding_pbte_numeric_input_availability_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_DING_PBTE_OA_NUMERIC_INPUT_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "The captured official PMC OA prefix contains no mode heat-capacity, force-constant, scattering-matrix, or Phonopy/ShengBTE reproduction payload.",
                "The publication gives a partial computational specification but routes supporting data to a corresponding-author request.",
                "Further anonymous searching inside the same PMC OA package is closed as a non-productive source route.",
                "All three supplementary PDF objects in the official OA inventory are archived locally with role-specific byte and SHA-256 checks.",
            ],
            "equation_or_mapping": "C_src(T)=sum_mu(c_mu(T)); the numeric c_mu or equivalent reproducible phonon payload is absent from the captured official OA distribution",
            "units": "required C_src: J m^-3 K^-1; no numeric value emitted",
            "derivation_class": "official-source object-inventory audit and scoped availability no-go",
            "observable": "availability of reproducible inputs for the Ding PBTE temperature-response map",
            "data_role": "SOURCE_PROVENANCE_AND_ACQUISITION_DECISION_ONLY; no calibration consumed",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(PACKAGE), "sha256": sha256(PACKAGE)},
                *[
                    {
                        "path": rel(path),
                        "sha256": sha256(path),
                        "bytes": path.stat().st_size,
                    }
                    for path in paths.values()
                ],
            ],
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "Select either a documented corresponding-author request or an independently sourced graphite phonon reproduction package; no Core dependency is unlocked.",
            "claim_boundary": "The no-go applies only to the captured official PMC OA distribution and the publisher's stated author-request route. It does not prove that author-held or third-party data are unavailable and does not close numeric C_src or Topic 13.",
        },
        "inventory_witness": {
            "object_count": len(object_keys),
            "object_keys": object_keys,
            "media_payload_count": len(media_urls),
            "media_suffixes": media_suffixes,
            "reproduction_payload_candidates": candidate_payloads,
            "data_availability_route": "corresponding author on reasonable request",
            "supplementary_files": [
                {
                    "role": role,
                    "path": rel(path),
                    "bytes": path.stat().st_size if path.exists() else None,
                    "sha256": sha256(path) if path.exists() else None,
                }
                for role, path in SUPPLEMENTARY_FILES.items()
            ],
        },
        "published_specification_present": package[
            "published_computational_specification"
        ],
        "missing_reproduction_inputs": package["missing_reproduction_inputs"],
        "checks": checks,
        "what_changed": "The Ding numeric-input source search now records the primary Nature Communications locator and publisher-level data-availability statement, then verifies the complete official OA inventory and all three locally archived supplementary PDFs with role-specific hashes before applying the scoped no-go.",
        "verification": "The publisher identity and data-availability statement, PMC OA API identity, complete S3 prefix, object metadata, full-text availability statement, published computational details, archived hashes, and holdout non-access are checked.",
        "controlling_blocker": "ding_pbte_author_data_or_independent_reproduction_package_missing",
        "next_action": "Prepare a source-specific author request for relaxed structure, force constants, ShengBTE inputs/outputs, and c_mu(T), or source-lock an independent open graphite phonon package and label it independent reproduction; do not infer C_src from normalized TTG data.",
        "claim_boundary": "This is a scoped source-availability no-go, not a physics no-go, numeric calibration, or Topic 13 closure.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": status,
                "artifact": rel(OUT),
                "object_count": len(object_keys),
                "reproduction_payload_candidates": candidate_payloads,
                "controlling_blocker": report["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if status == "PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
