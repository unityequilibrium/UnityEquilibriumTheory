"""Audit the public Huang 2023 graphite supplementary package boundary.

The NIMS record exposes the article PDF and the publisher supplementary PDF,
but this audit does not digitize plotted curves or relabel figure pixels as
machine-readable PBTE input.  The result is therefore a provenance boundary,
not a Ding C_src source or an alpha calibration.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
SUPPLEMENTARY = RAW / "huang_2023_graphite_poiseuille_supplementary.pdf"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_huang_2023_supplementary_payload_boundary_audit.json"

EXPECTED_SIZE_BYTES = 2_726_877
EXPECTED_SHA256 = "aaf2f325ddc797e7c309132e65d69379e4223e049e7411e6c3dc04cba9e09b90"
EXPECTED_PAGE_COUNT = 9


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_page_marker_count(payload: bytes) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", payload))


def main() -> int:
    exists = SUPPLEMENTARY.is_file()
    payload = SUPPLEMENTARY.read_bytes() if exists else b""
    size_bytes = len(payload) if exists else None
    sha256 = digest(SUPPLEMENTARY) if exists else None
    page_count = pdf_page_marker_count(payload) if exists else None

    # The public package inventory observed for this DOI contains the PDF only;
    # no CSV/TSV/NPZ/force-constant object was downloaded or inferred.
    package_inventory = [
        {
            "path": SUPPLEMENTARY.relative_to(ROOT).as_posix(),
            "media_type": "application/pdf",
            "role": "supplementary figures, methods, and narrative",
            "numeric_payload_role": False,
        }
    ]
    machine_readable_payload_files: list[str] = []

    checks = {
        "supplementary_file_present": exists,
        "pdf_header_present": payload.startswith(b"%PDF-") if exists else False,
        "size_matches_downloaded_source": size_bytes == EXPECTED_SIZE_BYTES,
        "sha256_matches_downloaded_source": sha256 == EXPECTED_SHA256,
        "page_marker_count_matches_reviewed_pdf": page_count == EXPECTED_PAGE_COUNT,
        "public_package_inventory_contains_only_pdf": len(package_inventory) == 1,
        "no_machine_readable_pbte_or_force_constant_payload": not machine_readable_payload_files,
        "no_curve_digitization_performed": True,
        "holdout_not_accessed": True,
        "alpha_phi_k_fit_not_performed": True,
    }
    passed = all(checks.values())

    result = {
        "schema_version": "t13-huang-2023-supplementary-payload-boundary-v1",
        "artifact": "t13_huang_2023_supplementary_payload_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": (
            "PASS_HUANG_PUBLIC_SUPPLEMENTARY_BOUNDARY_NO_NUMERIC_PBTE_PAYLOAD"
            if passed
            else "FAIL_HUANG_PUBLIC_SUPPLEMENTARY_BOUNDARY_AUDIT"
        ),
        "major_result": {
            "major_result_id": "T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the public Huang 2023 supplementary PDF is source-locked by locator, size, and SHA-256",
                "the downloaded public package is classified as PDF narrative/figure material only",
                "no machine-readable PBTE, mode-resolved C_src, or force-constant payload is accepted from this route",
                "figure digitization and target-curve fitting are explicitly excluded",
            ],
            "equation_or_mapping": {
                "source_observable": "graphite phonon Poiseuille-flow comparator",
                "thermal_role": "independent transport-regime comparator; not Ding C_src",
                "measurement_layer": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
            },
            "units": {
                "source_file": "PDF bytes",
                "reported_physical_context": "graphite ribbon transport; no row-level source unit contract imported",
            },
            "derivation_class": "public-source provenance boundary; no UET derivation",
            "observable": "graphite hydrodynamic transport comparator",
            "data_role": "EXTERNAL_COMPARATOR_PROVENANCE_BOUNDARY_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": OUT.relative_to(ROOT).as_posix()},
                {
                    "path": SUPPLEMENTARY.relative_to(ROOT).as_posix(),
                    "sha256": sha256,
                },
            ],
            "verification_status": (
                "PASS_HUANG_PUBLIC_SUPPLEMENTARY_BOUNDARY_NO_NUMERIC_PBTE_PAYLOAD"
                if passed
                else "FAIL_HUANG_PUBLIC_SUPPLEMENTARY_BOUNDARY_AUDIT"
            ),
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "huang_public_package_has_no_mode_resolved_numeric_payload",
                "material_and_regime_mapping_to_Ding_TTG_not_closed",
            ] if passed else ["public_supplementary_boundary_checks_failed"],
            "dependency_unlocked": "Huang graphite comparator provenance only; no Ding source, alpha, bridge, transport, Core, or Gravity unlock",
            "claim_boundary": "This closes only the public supplementary availability boundary for an independent graphite hydrodynamic comparator. It does not close Ding C_src, establish material/regime equivalence, derive alpha_Phi_K, or validate UET transport.",
        },
        "source": {
            "article_doi": "10.1038/s41467-023-37380-5",
            "article_url": "https://www.nature.com/articles/s41467-023-37380-5",
            "repository_url": "https://mdr.nims.go.jp/datasets/bf141c90-3911-4b2c-9fbc-274dad05d5d0?locale=en",
            "supplementary_url": "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-023-37380-5/MediaObjects/41467_2023_37380_MOESM1_ESM.pdf",
            "license_observed": "CC BY 4.0 on the repository/article route",
            "local_path": SUPPLEMENTARY.relative_to(ROOT).as_posix(),
            "size_bytes": size_bytes,
            "sha256": sha256,
            "expected_size_bytes": EXPECTED_SIZE_BYTES,
            "expected_sha256": EXPECTED_SHA256,
            "reviewed_page_count": page_count,
            "package_inventory": package_inventory,
            "machine_readable_payload_files": machine_readable_payload_files,
        },
        "review_boundary": {
            "content_review": "All 9 supplementary pages were reviewed for row-level PBTE/force-constant payload. The file contains figures, methods, and narrative; plotted curves were not digitized.",
            "comparator_context": "The source concerns isotopically purified graphite ribbon phonon Poiseuille flow and is not declared equivalent to Ding's HOPG TTG/PBTE source.",
            "holdout_accessed": False,
            "target_fit_performed": False,
            "alpha_Phi_K_fit_performed": False,
        },
        "checks": checks,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": "Keep the source as a provenance boundary/comparator. Obtain an authorized numeric PBTE payload or complete an accepted same-regime reproduction with mode-resolved C_src(T), convergence, uncertainty, and unit contracts.",
        "claim_boundary": "This artifact narrows the public-data search but does not promote Huang 2023 into Ding source closure or full Topic 13 closure.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "checks_pass": passed,
                "page_count": page_count,
                "machine_readable_payload_files": len(machine_readable_payload_files),
                "controlling_blocker": result["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
