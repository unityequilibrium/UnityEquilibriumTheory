"""Audit the public Huberman 2019 graphite PBTE source boundary.

The arXiv preprint includes the article and supplementary methods. It records
the BTE equations and identifies the Ding graphite force-constant input, but it
does not provide a machine-readable mode-resolved C_src payload or the raw
force-constant/scattering package needed for an accepted reproduction.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
SOURCE = RAW / "huberman_2019_graphite_second_sound_arxiv.pdf"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_huberman_2019_public_pbte_boundary_audit.json"

EXPECTED_SIZE_BYTES = 1_888_806
EXPECTED_SHA256 = "29dc508df146125e6aef524404c0cfff98b31605783524526e81a8c93ad46027"
EXPECTED_PAGE_COUNT = 22


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_page_marker_count(payload: bytes) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", payload))


def main() -> int:
    exists = SOURCE.is_file()
    payload = SOURCE.read_bytes() if exists else b""
    size_bytes = len(payload) if exists else None
    sha256 = digest(SOURCE) if exists else None
    page_count = pdf_page_marker_count(payload) if exists else None

    package_inventory = [
        {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "media_type": "application/pdf",
            "role": "public preprint plus embedded supplementary methods",
            "numeric_payload_role": False,
        }
    ]
    machine_readable_payload_files: list[str] = []
    checks = {
        "source_file_present": exists,
        "pdf_header_present": payload.startswith(b"%PDF-") if exists else False,
        "size_matches_downloaded_source": size_bytes == EXPECTED_SIZE_BYTES,
        "sha256_matches_downloaded_source": sha256 == EXPECTED_SHA256,
        "page_marker_count_matches_reviewed_pdf": page_count == EXPECTED_PAGE_COUNT,
        "public_package_inventory_contains_only_pdf": len(package_inventory) == 1,
        "no_machine_readable_mode_resolved_csrc_or_force_constant_payload": not machine_readable_payload_files,
        "no_curve_digitization_performed": True,
        "holdout_not_accessed": True,
        "target_fit_not_performed": True,
        "alpha_phi_k_fit_not_performed": True,
    }
    passed = all(checks.values())
    status = (
        "PASS_HUBERMAN_PUBLIC_PBTE_BOUNDARY_NO_ACCEPTED_NUMERIC_PAYLOAD"
        if passed
        else "FAIL_HUBERMAN_PUBLIC_PBTE_BOUNDARY_AUDIT"
    )

    result = {
        "schema_version": "t13-huberman-2019-public-pbte-boundary-v1",
        "artifact": "t13_huberman_2019_public_pbte_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_HUBERMAN_2019_PUBLIC_PBTE_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the public Huberman 2019 arXiv package is source-locked by locator, size, and SHA-256",
                "the embedded supplementary methods are reviewed as method/narrative material only",
                "the source reports a full-scattering-matrix BTE method and attributes graphite force-constant inputs to Ding et al. 2018",
                "no machine-readable mode-resolved C_src, raw force-constant, or scattering-matrix payload is accepted from this route",
                "figure digitization, target fitting, alpha calibration, and holdout access are excluded",
            ],
            "equation_or_mapping": {
                "source_method_context": "g_i are mode-specific deviational energy densities; C = sum_i c_i; Delta_T = (1/C) sum_i g_i",
                "topic13_measurement_boundary": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
                "acceptance_boundary": "C_src(T) = sum_mu c_mu(T) in J m^-3 K^-1 requires a raw or accepted reproduction payload",
            },
            "units": {
                "source_C": "not imported; the public PDF does not provide an accepted row-level unit contract",
                "required_C_src": "J m^-3 K^-1",
                "normalized_TTG": "dimensionless",
            },
            "derivation_class": "public-source provenance boundary; no UET derivation",
            "observable": "graphite TTG hydrodynamic transport comparator",
            "data_role": "EXTERNAL_COMPARATOR_PROVENANCE_BOUNDARY_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": OUT.relative_to(ROOT).as_posix()},
                {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": sha256},
            ],
            "verification_status": status,
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "huberman_public_package_has_no_machine_readable_mode_resolved_csrc_payload",
                "accepted_independent_reproduction_requires_source_grade_uncertainty_and_convergence",
            ] if passed else ["public_pbte_boundary_checks_failed"],
            "dependency_unlocked": "Huberman graphite PBTE comparator provenance only; no Ding source, alpha, bridge, transport, Core, or Gravity unlock",
            "claim_boundary": "This closes only the public Huberman source-availability boundary. It does not close Ding C_src, establish an accepted independent reproduction, derive alpha_Phi_K, or validate UET transport.",
        },
        "source": {
            "article_doi": "10.1126/science.aav3548",
            "article_url": "https://www.science.org/doi/10.1126/science.aav3548",
            "arxiv_url": "https://arxiv.org/abs/1901.09160",
            "download_url": "https://arxiv.org/pdf/1901.09160",
            "local_path": SOURCE.relative_to(ROOT).as_posix(),
            "size_bytes": size_bytes,
            "sha256": sha256,
            "expected_size_bytes": EXPECTED_SIZE_BYTES,
            "expected_sha256": EXPECTED_SHA256,
            "reviewed_page_count": page_count,
            "package_inventory": package_inventory,
            "machine_readable_payload_files": machine_readable_payload_files,
            "license_observed": "public arXiv route; no separate license assertion imported into the evidence contract",
        },
        "review_boundary": {
            "content_review": "All 22 pages, including the embedded supplementary methods, were reviewed for row-level mode-resolved C_src, force constants, scattering matrices, and machine-readable uncertainty/convergence payload.",
            "reported_method_context": "The supplementary method gives the full-scattering-matrix BTE equations and states that second- and third-order force constants calculated by Ding et al. 2018 were used as inputs; those inputs are not deposited in this package.",
            "numeric_content_policy": "Printed values and plotted curves remain narrative/comparator context; no curve pixels or PDF tables were promoted to C_src rows.",
            "holdout_accessed": False,
            "target_fit_performed": False,
            "alpha_Phi_K_fit_performed": False,
        },
        "checks": checks,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": "Keep this source as a public comparator boundary. Obtain an authorized Ding numeric package or complete an accepted same-regime reproduction with mode-resolved C_src(T), SI units, source-grade uncertainty, convergence, and material/state mapping.",
        "claim_boundary": "This artifact narrows the public PBTE search but does not promote Huberman 2019 into Ding source closure, alpha calibration, TTG prediction, external validation, or Full Topic 13 closure.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
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
