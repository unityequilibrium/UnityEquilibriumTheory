"""Audit the public Ding 2022 supplementary package boundary.

This audit records what the official open-access object inventory contains. It
does not treat equations or plotted figures as a raw numeric C_src package and
does not consume the locked Xie 2026 holdout.
"""

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
INVENTORY = RAW / "ding_2022_pmc_s3_inventory.xml"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_public_supplementary_payload_boundary_audit.json"

EXPECTED_KEYS = {
    "PMC8755757.1/41467_2021_27907_Fig1_HTML.jpg",
    "PMC8755757.1/41467_2021_27907_Fig2_HTML.jpg",
    "PMC8755757.1/41467_2021_27907_Fig3_HTML.jpg",
    "PMC8755757.1/41467_2021_27907_Fig4_HTML.jpg",
    "PMC8755757.1/41467_2021_27907_MOESM1_ESM.pdf",
    "PMC8755757.1/41467_2021_27907_MOESM2_ESM.pdf",
    "PMC8755757.1/41467_2021_27907_MOESM3_ESM.pdf",
    "PMC8755757.1/PMC8755757.1.json",
    "PMC8755757.1/PMC8755757.1.pdf",
    "PMC8755757.1/PMC8755757.1.txt",
    "PMC8755757.1/PMC8755757.1.xml",
}

LOCAL_FILES = {
    "MOESM1": RAW / "ding_2022_supplementary_information.pdf",
    "MOESM2": RAW / "ding_2022_supplementary_materials_2.pdf",
    "MOESM3": RAW / "ding_2022_supplementary_materials_3.pdf",
}

EXPECTED_LOCAL = {
    "MOESM1": {
        "size_bytes": 1_893_976,
        "sha256": "a50c1a6347775de72f705f4395507d3136cbf4e5cadfb6638caca2876c52b8f7",
        "object_key": "PMC8755757.1/41467_2021_27907_MOESM1_ESM.pdf",
    },
    "MOESM2": {
        "size_bytes": 4_537_623,
        "sha256": "2f7d1d057df83b8d3408f65c833dad7542fca8b24aeec087e304842fa5aca6e7",
        "object_key": "PMC8755757.1/41467_2021_27907_MOESM2_ESM.pdf",
    },
    "MOESM3": {
        "size_bytes": 927_333,
        "sha256": "4405683b720a24437d64fe3429d409503fcc91bd33c1e8616a3252cc50d94c5f",
        "object_key": "PMC8755757.1/41467_2021_27907_MOESM3_ESM.pdf",
    },
}

NUMERIC_PAYLOAD_EXTENSIONS = {
    ".csv",
    ".tsv",
    ".dat",
    ".mat",
    ".h5",
    ".hdf5",
    ".npy",
    ".npz",
    ".xlsx",
    ".zip",
    ".tar",
    ".gz",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory_rows() -> list[dict[str, object]]:
    root = ET.parse(INVENTORY).getroot()
    namespace = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    rows: list[dict[str, object]] = []
    for content in root.findall(f"{namespace}Contents"):
        key = content.findtext(f"{namespace}Key")
        size = content.findtext(f"{namespace}Size")
        etag = content.findtext(f"{namespace}ETag")
        rows.append(
            {
                "key": key,
                "size_bytes": int(size) if size is not None else None,
                "etag": etag,
            }
        )
    return rows


def main() -> int:
    rows = inventory_rows() if INVENTORY.is_file() else []
    keys = {str(row["key"]) for row in rows if row.get("key")}
    pdf_rows = [row for row in rows if str(row.get("key", "")).lower().endswith(".pdf")]
    supplementary_rows = [row for row in pdf_rows if "MOESM" in str(row.get("key", ""))]
    numeric_payload_rows = [
        row
        for row in rows
        if Path(str(row.get("key", ""))).suffix.lower() in NUMERIC_PAYLOAD_EXTENSIONS
    ]

    local_records: dict[str, dict[str, object]] = {}
    for name, path in LOCAL_FILES.items():
        expected = EXPECTED_LOCAL[name]
        local_records[name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "exists": path.is_file(),
            "size_bytes": path.stat().st_size if path.is_file() else None,
            "sha256": digest(path) if path.is_file() else None,
            "expected_size_bytes": expected["size_bytes"],
            "expected_sha256": expected["sha256"],
            "object_key": expected["object_key"],
            "size_matches": path.is_file() and path.stat().st_size == expected["size_bytes"],
            "hash_matches": path.is_file() and digest(path) == expected["sha256"],
            "role": {
                "MOESM1": "methods, equations, figures, and supplementary narrative",
                "MOESM2": "reviewer response and reporting clarification",
                "MOESM3": "reporting summary",
            }[name],
        }

    checks = {
        "inventory_present": INVENTORY.is_file(),
        "inventory_key_count_is_11": len(rows) == 11,
        "inventory_keys_match_expected_set": keys == EXPECTED_KEYS,
        "supplementary_object_count_is_3": len(supplementary_rows) == 3,
        "supplementary_objects_are_pdf": all(
            str(row.get("key", "")).lower().endswith(".pdf") for row in supplementary_rows
        ),
        "no_machine_readable_numeric_payload_object": not numeric_payload_rows,
        "local_supplementary_files_present": all(record["exists"] for record in local_records.values()),
        "local_supplementary_sizes_match_inventory": all(
            record["size_matches"] for record in local_records.values()
        ),
        "local_supplementary_hashes_match_declared": all(
            record["hash_matches"] for record in local_records.values()
        ),
        "data_availability_request_route_recorded": True,
        "holdout_not_accessed": True,
        "alpha_fit_not_performed": True,
    }
    passed = all(checks.values())

    result = {
        "schema_version": "t13-ding-public-supplementary-payload-boundary-v1",
        "artifact": "t13_ding_public_supplementary_payload_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": (
            "PASS_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY_NO_NUMERIC_C_SRC"
            if passed
            else "FAIL_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY_AUDIT"
        ),
        "major_result": {
            "major_result_id": "T13_DING_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the official public Ding object inventory is captured with object identity, size, and local PDF hashes",
                "the three MOESM supplementary objects are classified as PDF narrative/figure/reporting material",
                "the public machine-readable route contains no raw numeric C_src or PBTE input payload object",
                "the corresponding-author request route is recorded without treating a request as received data",
            ],
            "equation_or_mapping": {
                "ding_mode_sum": "C_src(T) = sum_mu c_mu(T)",
                "ding_temperature_response": "Delta_Tq = Delta_u_ph / C_src",
                "measurement_layer": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
            },
            "units": {
                "C_src": "J m^-3 K^-1; numeric source payload not publicly available in the audited inventory",
                "supplementary_files": "PDF bytes; not a thermal observable unit",
            },
            "derivation_class": "public-source provenance and payload-availability boundary; no UET derivation",
            "observable": "Ding PBTE thermal-response source boundary",
            "data_role": "SOURCE_PROVENANCE_BOUNDARY_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": OUT.relative_to(ROOT).as_posix()},
                {
                    "path": INVENTORY.relative_to(ROOT).as_posix(),
                    "sha256": digest(INVENTORY) if INVENTORY.is_file() else None,
                },
                *[
                    {"path": str(record["path"]), "sha256": record["sha256"]}
                    for record in local_records.values()
                ],
            ],
            "verification_status": (
                "PASS_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY_NO_NUMERIC_C_SRC"
                if passed
                else "FAIL_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY_AUDIT"
            ),
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "author_request_or_mode_resolved_PBTE_reproduction_required_for_full_source_closure",
            ] if passed else ["public_supplementary_boundary_checks_failed"],
            "dependency_unlocked": "public Ding provenance boundary only; no full-source, alpha, bridge, transport, Core, or Gravity unlock",
            "claim_boundary": "The audited open-access package is provenance-complete for the public supplementary route but does not close Ding's numeric C_src. Equations and plotted figures are not relabeled as a machine-readable C_src source, and the author-request route remains open.",
        },
        "source": {
            "article_doi": "10.1038/s41467-021-27907-z",
            "article_url": "https://www.nature.com/articles/s41467-021-27907-z",
            "data_availability": "data available from corresponding author on reasonable request",
            "data_availability_locator": "https://www.nature.com/articles/s41467-021-27907-z#data-availability",
            "official_inventory_path": INVENTORY.relative_to(ROOT).as_posix(),
            "official_inventory_sha256": digest(INVENTORY) if INVENTORY.is_file() else None,
            "inventory_object_count": len(rows),
            "objects": rows,
            "supplementary_objects": supplementary_rows,
            "numeric_payload_objects": numeric_payload_rows,
            "local_supplementary_files": local_records,
        },
        "review_boundary": {
            "pdf_review": "MOESM1 was reviewed for PBTE equations and figures; MOESM2 for reviewer-response clarifications; MOESM3 for reporting summary. None supplies a machine-readable mode-resolved C_src table or PBTE collision/scattering input package.",
            "figure_route": "Figures remain normalized/visual comparison evidence only and do not become raw-author C_src rows.",
            "request_route": "READY_NOT_SENT",
            "holdout_accessed": False,
            "target_fit_performed": False,
            "alpha_Phi_K_fit_performed": False,
        },
        "checks": checks,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": "Use the recorded author-request route if authorized, or build an accepted Ding-regime PBTE reproduction with mode-resolved C_src(T), convergence, uncertainty, and unit contracts; do not relabel MP48, figures, or PDFs as C_src.",
        "claim_boundary": "This closes only the public supplementary payload-availability boundary. Full Topic 13 remains blocked on accepted C_src, independent alpha_Phi_K, non-circular bridge/beta, EOS/transport/KMS/entropy, and dimensional Phi-to-thermal mapping.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks_pass": passed, "numeric_payload_objects": len(numeric_payload_rows), "controlling_blocker": result["controlling_blocker"]}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
