"""Record the official BLS input-output source gate without bypassing access controls."""

from __future__ import annotations

import zipfile
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, ROOT, sha256, utc_now, write_json


PAGE_URL = "https://www.bls.gov/emp/data/input-output-matrix.htm"
DOWNLOAD_URL = "https://www.bls.gov/emp/input-output/input-output.zip"
ARCHIVE = ROOT / "docs" / "data" / "external" / "economics" / "us_historical" / "bls_io" / "2026-07-16" / "input-output.zip"
ARTIFACT = ARTIFACT_DIR / "0_25_bls_io_source_gate.json"


def main() -> int:
    archived = ARCHIVE.exists()
    payload = {
        "schema_version": "1.0",
        "status": "WARN" if archived else "BLOCKED",
        "controller_status": "BLS_IO_QUALITY_AND_ACCESS_GATE",
        "generated_at_utc": utc_now(),
        "source": {
            "provider": "U.S. Bureau of Labor Statistics Employment Projections",
            "official_page": PAGE_URL,
            "download_url": DOWNLOAD_URL,
            "coverage_claimed_by_provider": [1997, 2024],
            "data_role": "commodity flows from production through intermediate industry use to final users; labor/resource concordance candidate",
            "upstream_note": "BLS states the matrices are developed from input-output data initially developed by BEA.",
        },
        "archive": {
            "path": str(ARCHIVE).replace("\\", "/"),
            "exists": archived,
            "sha256": sha256(ARCHIVE) if archived else None,
            "bytes": ARCHIVE.stat().st_size if archived else None,
            "member_count": len(zipfile.ZipFile(ARCHIVE).namelist()) if archived else None,
        },
        "provider_quality_notice": {
            "notice_date": "2026-02-06",
            "text": "BLS page says the three public matrix files were removed because they included incorrect values for the percentage of total industry output that is value added; updated tables are pending.",
            "effect": "No matrix result may be used until the replacement or researcher ZIP is independently checked against the notice and archived with a hash.",
        },
        "access_observation": {
            "automated_retrieval_status": "ACCESS_DENIED" if not archived else "ARCHIVE_PRESENT",
            "observation": "The official download endpoint returned an Access Denied response to the repository retrieval attempt; no user-agent spoofing, anti-bot bypass, or mirror substitution was used.",
            "next_allowed_action": "Obtain the provider file through an approved manual or official access path, record terms/release/hash, then rerun this gate.",
        },
        "claim_boundary": "This gate establishes source identity and a quality/access blocker only. It does not provide payment-level flows, causal evidence, or a payer-resource result.",
        "blockers": [
            "The BLS researcher ZIP is not archived in the frozen package." if not archived else "The archived BLS ZIP is subject to the provider's 2026-02-06 value-added quality notice and requires validation before analysis.",
            "No firm/project payer-payee identities or invoice-level payment records are supplied by an aggregate input-output matrix.",
            "Physical natural-resource quantities still require a concordant EIA/USGS/FAOSTAT or environmental satellite-account join.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("BLS I-O source gate:", payload["status"], payload["access_observation"]["automated_retrieval_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
