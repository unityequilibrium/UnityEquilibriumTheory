"""Record the public-data boundary for a firm/project payment ledger.

This gate does not pretend that public macro accounts or SEC annual filings
are invoice records.  It records the official Census access boundary for the
closest firm/establishment microdata and keeps the payer-level claim blocked
until approved restricted-use access or an independently licensed ledger is
actually supplied.
"""

from __future__ import annotations

from economic_hardening_common import ARTIFACT_DIR, ROOT, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_project_payment_ledger_gate.json"


def main() -> int:
    payload = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "BLOCKED",
        "controller_status": "PROJECT_PAYMENT_LEDGER_NOT_PUBLIC",
        "generated_at_utc": utc_now(),
        "public_sources_checked": [
            {
                "provider": "U.S. Census Bureau",
                "url": "https://www.census.gov/topics/research/guidance/restricted-use-microdata/economic-data.html",
                "role": "firm/establishment/transaction microdata availability",
                "observation": "Business Register, LBD, ACES, QFR, CFS, and related economic microdata are listed as restricted-use assets requiring approved secure access; they are not a public invoice-level ledger.",
                "status": "RESTRICTED_USE",
            },
            {
                "provider": "U.S. Census Bureau",
                "url": "https://www.census.gov/programs-surveys/ces/data/restricted-use-data/longitudinal-business-database.html",
                "role": "firm/establishment longitudinal linkage",
                "observation": "The LBD is available only to qualified researchers for approved projects in secure Federal Statistical Research Data Centers.",
                "status": "RESTRICTED_USE",
            },
            {
                "provider": "U.S. Securities and Exchange Commission",
                "url": "https://www.sec.gov/edgar/sec-api-documentation",
                "role": "public-firm accounting proxy",
                "observation": "SEC XBRL facts provide annual accounting channels but no supplier invoice, payment counterparty, or project resource ledger.",
                "status": "PUBLIC_PROXY_ONLY",
            },
        ],
        "local_archives": [],
        "required_fields": [
            "payer identity",
            "payee/supplier identity",
            "transaction date and amount",
            "industry/commodity concordance",
            "project or asset identity",
            "profit/debt/equity funding provenance",
        ],
        "next_allowed_path": "Obtain approved restricted-use access or a licensed, source-locked transaction ledger; archive terms, vintage, and hash before any join.",
        "claim_boundary": "No payment-level payer, profit-vs-debt attribution, project-resource transformation, or innovation-causality claim is allowed from the current public package.",
        "limitations": [
            "Aggregate financial accounts and public-firm filings cannot trace a particular payment to a physical resource.",
            "Restricted-use access would require a human-approved research project and secure output review; it is not an automatic source acquisition.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("Project payment ledger gate: BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
