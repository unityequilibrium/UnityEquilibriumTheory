"""Audit whether funding flows can be joined to industry, labor, and physical resources.

The public macro package can identify aggregate funding channels, but it cannot
claim that a particular dollar paid for a particular labor/resource transformation.
This gate records which source-locked joins are present locally and which remain
missing or blocked.  It performs no imputation and no causal estimation.
"""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

from economic_hardening_common import (
    ARTIFACT_DIR,
    BEA_1997_IO_ARTIFACT,
    BLS_INDUSTRY_HOURS_ARTIFACT,
    BLS_INDUSTRY_HOURS_RAW_DIR,
    USASPENDING_LEDGER_ARTIFACT,
    TREASURY_FUNDING_SOURCE_ARTIFACT,
    AWARD_OUTLAY_RECONCILIATION_ARTIFACT,
    AWARD_LEVEL_OUTLAY_ARTIFACT,
    AWARD_FUNDING_ACCOUNT_ARTIFACT,
    FEDERAL_ACCOUNT_BUDGET_RESOURCE_ARTIFACT,
    SUBAWARD_DOWNSTREAM_ARTIFACT,
    USGS_MATERIAL_QUANTITY_ARTIFACT,
    SEC_PUBLIC_FIRM_PROXY_ARTIFACT,
    SEC_PUBLIC_FIRM_MIX_ARTIFACT,
    SEC_RECIPIENT_FUNDING_CONCORDANCE_ARTIFACT,
    PROJECT_PAYMENT_LEDGER_ARTIFACT,
    BLS_IO_SOURCE_GATE_ARTIFACT,
    FED_Z1_FUNDING_MAPPING_ARTIFACT,
    RAW_ROOT,
    ROOT,
    sha256,
    utc_now,
    write_json,
)


ARTIFACT = ARTIFACT_DIR / "0_25_payer_resource_join_readiness.json"


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _file_record(path: Path, role: str, status_if_present: str = "PASS") -> dict:
    exists = path.is_file()
    return {
        "role": role,
        "path": _relative(path) if exists else None,
        "exists": exists,
        "sha256": sha256(path) if exists else None,
        "status": status_if_present if exists else "MISSING",
    }


def _glob_record(directory: Path, pattern: str, role: str, status_if_present: str = "PASS") -> dict:
    files = sorted(path for path in directory.glob(pattern) if path.is_file()) if directory.exists() else []
    return {
        "role": role,
        "directory": _relative(directory),
        "pattern": pattern,
        "files": [_relative(path) for path in files],
        "hashes": { _relative(path): sha256(path) for path in files },
        "status": status_if_present if files else "MISSING",
    }


def _artifact_status(path: Path) -> dict:
    if not path.exists():
        return {"path": _relative(path), "exists": False, "status": "MISSING"}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": _relative(path),
        "exists": True,
        "sha256": sha256(path),
        "status": payload.get("status", "UNKNOWN"),
        "controller_status": payload.get("controller_status"),
    }


def _bounded_bls_hours(path: Path) -> tuple[dict, bool]:
    """Allow a complete returned-series subset while preserving candidate-set WARN."""
    record = _artifact_status(path)
    if not record.get("exists"):
        return record, False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return record, False
    coverage = payload.get("coverage", {})
    complete_series = int(coverage.get("complete_series_count", 0) or 0)
    rows = int(coverage.get("rows", 0) or 0)
    incomplete = coverage.get("incomplete_series", payload.get("incomplete_series", {}))
    bounded_ready = bool(coverage.get("no_imputation")) and complete_series > 0 and rows > 0 and not incomplete
    record["bounded_coverage"] = {
        "ready": bounded_ready,
        "complete_series_count": complete_series,
        "returned_naics4": coverage.get("returned_naics4"),
        "requested_naics4": coverage.get("requested_bea_naics4"),
        "rows": rows,
        "years": coverage.get("years"),
        "candidate_set_complete": bool(coverage.get("returned_naics4") == coverage.get("requested_bea_naics4")),
        "request_failures": len(payload.get("request_failures", [])),
        "no_imputation": bool(coverage.get("no_imputation")),
    }
    return record, bounded_ready


def _xlsx_record(path: Path, role: str) -> dict:
    exists = path.is_file()
    sheets: list[str] = []
    valid = False
    if exists:
        try:
            with zipfile.ZipFile(path) as archive:
                workbook = archive.read("xl/workbook.xml").decode("utf-8", errors="replace")
                sheets = re.findall(r'<sheet[^>]+name="([^"]+)"', workbook)
                valid = bool(sheets)
        except (OSError, KeyError, zipfile.BadZipFile):
            valid = False
    digest = sha256(path) if exists else None
    manifest_path = path.parent / "source_manifest.json"
    manifest_exists = manifest_path.is_file()
    manifest_hash_matches = False
    if manifest_exists and digest:
        try:
            manifest_hash_matches = json.loads(manifest_path.read_text(encoding="utf-8")).get("sha256") == digest
        except (OSError, json.JSONDecodeError):
            manifest_hash_matches = False
    status = "PASS_WITH_BOUNDARY" if valid and manifest_hash_matches else ("WARN" if exists else "MISSING")
    return {
        "role": role,
        "path": _relative(path) if exists else None,
        "exists": exists,
        "sha256": digest,
        "sheet_names": sheets,
        "source_manifest": {
            "path": _relative(manifest_path) if manifest_exists else None,
            "exists": manifest_exists,
            "sha256": sha256(manifest_path) if manifest_exists else None,
            "hash_matches_data": manifest_hash_matches,
        },
        "status": status,
    }


def main() -> int:
    fed_z1_dir = RAW_ROOT / "fed_z1" / "2026-07-16"
    bls_io_dir = RAW_ROOT / "bls_io" / "2026-07-16"
    bea_dir = RAW_ROOT / "bea" / "2026-07-12"
    eia_dir = RAW_ROOT / "eia" / "2026-07-12"
    concordance_path = RAW_ROOT / "bea_io" / "2026-07-16" / "BEA-Industry-and-Commodity-Codes-and-NAICS-Concordance.xlsx"
    bea_benchmark = _artifact_status(BEA_1997_IO_ARTIFACT)
    benchmark_ready = bea_benchmark.get("status") == "PASS_WITH_BOUNDARY"
    bls_hours, bls_hours_ready = _bounded_bls_hours(BLS_INDUSTRY_HOURS_ARTIFACT)
    usgs_materials = _artifact_status(USGS_MATERIAL_QUANTITY_ARTIFACT)
    usgs_materials_ready = usgs_materials.get("status") == "PASS_WITH_BOUNDARY"
    sec_funding_proxy = _artifact_status(SEC_PUBLIC_FIRM_PROXY_ARTIFACT)
    sec_funding_mix = _artifact_status(SEC_PUBLIC_FIRM_MIX_ARTIFACT)
    recipient_funding_concordance = _artifact_status(SEC_RECIPIENT_FUNDING_CONCORDANCE_ARTIFACT)
    recipient_funding_ready = recipient_funding_concordance.get("status") == "PASS_WITH_BOUNDARY"
    recipient_funding_payload = {}
    if recipient_funding_concordance.get("exists"):
        try:
            recipient_funding_payload = json.loads(SEC_RECIPIENT_FUNDING_CONCORDANCE_ARTIFACT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            recipient_funding_payload = {}
    project_ledger_gate = _artifact_status(PROJECT_PAYMENT_LEDGER_ARTIFACT)
    usaspending_ledger = _artifact_status(USASPENDING_LEDGER_ARTIFACT)
    usaspending_ready = usaspending_ledger.get("status") == "PASS_WITH_BOUNDARY"
    treasury_funding = _artifact_status(TREASURY_FUNDING_SOURCE_ARTIFACT)
    treasury_funding_ready = treasury_funding.get("status") == "PASS_WITH_BOUNDARY"
    award_outlay_reconciliation = _artifact_status(AWARD_OUTLAY_RECONCILIATION_ARTIFACT)
    award_outlay_ready = award_outlay_reconciliation.get("status") == "PASS_WITH_BOUNDARY"
    award_level_outlay = _artifact_status(AWARD_LEVEL_OUTLAY_ARTIFACT)
    award_level_ready = award_level_outlay.get("status") == "PASS_WITH_BOUNDARY"
    award_funding_account = _artifact_status(AWARD_FUNDING_ACCOUNT_ARTIFACT)
    award_funding_payload = {}
    if award_funding_account.get("exists"):
        try:
            award_funding_payload = json.loads(AWARD_FUNDING_ACCOUNT_ARTIFACT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            award_funding_payload = {}
    award_funding_bounded = bool(award_funding_payload.get("bounded_coverage", {}).get("ready"))
    federal_account_budget_resource = _artifact_status(FEDERAL_ACCOUNT_BUDGET_RESOURCE_ARTIFACT)
    federal_account_budget_payload = {}
    if federal_account_budget_resource.get("exists"):
        try:
            federal_account_budget_payload = json.loads(FEDERAL_ACCOUNT_BUDGET_RESOURCE_ARTIFACT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            federal_account_budget_payload = {}
    federal_account_budget_ready = federal_account_budget_resource.get("status") == "PASS_WITH_BOUNDARY"
    subaward_downstream = _artifact_status(SUBAWARD_DOWNSTREAM_ARTIFACT)
    subaward_downstream_ready = subaward_downstream.get("status") == "PASS_WITH_BOUNDARY"
    subaward_downstream_payload = {}
    if subaward_downstream.get("exists"):
        try:
            subaward_downstream_payload = json.loads(SUBAWARD_DOWNSTREAM_ARTIFACT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            subaward_downstream_payload = {}

    evidence = {
        "funding_flows": {
            "status": "PASS_WITH_BOUNDARY",
            "artifact": _artifact_status(FED_Z1_FUNDING_MAPPING_ARTIFACT),
            "source": _file_record(fed_z1_dir / "z1_csv_files.zip", "Fed Z.1 sectoral transactions"),
            "boundary": "Aggregate sectoral channels and an accounting bridge are present; no payer-payee or project earmark is observed.",
        },
        "industry_input_output": {
            "status": "PASS_WITH_BOUNDARY" if benchmark_ready else "BLOCKED",
            "artifact": {
                "benchmark": bea_benchmark,
                "annual_bls_source_gate": _artifact_status(BLS_IO_SOURCE_GATE_ARTIFACT),
            },
            "source": _glob_record(bls_io_dir, "*", "BLS/BEA industry and commodity flows"),
            "boundary": "The 1997 BEA benchmark structure is source-locked and validated; the annual BLS/BEA flow lane remains unavailable and cannot be treated as a 1997-2024 panel.",
        },
        "bea_industry_accounts": {
            "status": "PASS_WITH_BOUNDARY" if benchmark_ready else "BLOCKED",
            "artifact": bea_benchmark,
            "source": _glob_record(bea_dir, "*input*output*", "BEA annual supply-use/input-output accounts"),
            "provider_access": {
                "official_page": "https://www.bea.gov/itable/input-output",
                "api_registration": "https://apps.bea.gov/api/signup/",
                "interactive_application": "https://apps.bea.gov/iTable/?Categories=Core&isURI=1&reqid=1602&step=2",
                "interactive_application_id": 52,
                "direct_backend_probe": {
                    "url": "https://apps.bea.gov/iTablecore/data/app/52",
                    "status_code": 500,
                    "table_rows_archived": False,
                    "anti_bot_bypass": False,
                },
                "status": "REGISTRATION_OR_INTERACTIVE_EXPORT_REQUIRED",
            },
            "boundary": "A source-locked 1997 benchmark is archived for structural validation; annual supply-use/input-output flow export still requires the BEA API or interactive application.",
        },
        "labor_industry_hours": {
            "status": "PASS_WITH_BOUNDARY" if bls_hours_ready else "BLOCKED",
            "artifact": bls_hours,
            "source": _glob_record(BLS_INDUSTRY_HOURS_RAW_DIR, "*.json", "BLS industry hours API responses"),
            "boundary": "The BLS source artifact remains WARN for the 202-code candidate set, but the returned 11 four-digit NAICS series are complete for 1987-2024 with no imputation. This bounded subset is not payment-level occupation or payer provenance.",
        },
        "energy_throughput": {
            "status": "PASS_WITH_BOUNDARY",
            "source": _glob_record(eia_dir, "*.csv", "EIA energy throughput"),
            "boundary": "Energy throughput is available; it is not a complete material-extraction or project-level resource ledger.",
        },
        "material_quantities": {
            "status": "PASS_WITH_BOUNDARY" if usgs_materials_ready else "BLOCKED",
            "artifact": usgs_materials,
            "source": _glob_record(RAW_ROOT / "usgs_materials" / "2026-07-16", "*.xlsx", "USGS physical material quantity workbooks"),
            "boundary": "USGS national commodity quantity series are source-locked for selected materials; no material-to-industry or project allocation is observed.",
        },
        "public_firm_funding_proxy": {
            "status": "PASS_WITH_BOUNDARY" if sec_funding_proxy.get("status") == "PASS_WITH_BOUNDARY" and sec_funding_mix.get("status") == "PASS_WITH_BOUNDARY" else "BLOCKED",
            "artifact": {"source_package": sec_funding_proxy, "funding_mix": sec_funding_mix},
            "boundary": "Predeclared public-firm annual accounting channels can be compared descriptively; funding shares and invoice provenance remain unidentified.",
        },
        "recipient_public_firm_funding_channels": {
            "status": "PASS_WITH_BOUNDARY" if recipient_funding_ready else "BLOCKED",
            "artifact": recipient_funding_concordance,
            "coverage": recipient_funding_payload.get("coverage"),
            "source": _glob_record(RAW_ROOT / "sec_xbrl" / "2026-08-01", "CIK*_recipient_companyfacts.json", "SEC company-facts annual recipient accounting responses"),
            "boundary": "Exact unique recipient-name matches to SEC reporting issuers provide annual net-income, operating-cash-flow, capex, debt, dividends, and cash channels. They do not identify which award dollar was paid from profit, borrowing, or cash, and no fuzzy matching or share attribution is used.",
        },
        "award_federal_account_linkage": {
            "status": "PASS_WITH_BOUNDARY" if award_funding_bounded else "BLOCKED",
            "artifact": award_funding_account,
            "bounded_coverage": award_funding_payload.get("bounded_coverage"),
            "source": _glob_record(RAW_ROOT / "usaspending" / "2026-08-01", "award_funding_*.json", "USAspending award funding-account responses"),
            "boundary": "USAspending links a bounded returned subset to federal accounts, account titles, funding agencies, object classes, and reported gross outlays. The source artifact remains WARN because several predeclared awards have no FY2024 funding rows; no ultimate financing instrument or bank settlement is observed.",
        },
        "award_level_account_outlay": {
            "status": "PASS_WITH_BOUNDARY" if award_level_ready else "BLOCKED",
            "artifact": award_level_outlay,
            "source": _glob_record(RAW_ROOT / "usaspending" / "2026-08-01", "award_detail_*.json", "USAspending award-detail account obligation/outlay responses"),
            "boundary": "A fixed nonrepresentative ten-award sample has complete account-level obligation and outlay fields. These are award accounting totals, not bank settlement, supplier invoices, or financing-source evidence.",
        },
        "federal_account_budgetary_resources": {
            "status": "PASS_WITH_BOUNDARY" if federal_account_budget_ready else "BLOCKED",
            "artifact": federal_account_budget_resource,
            "coverage": federal_account_budget_payload.get("coverage"),
            "accounting_identity_check": federal_account_budget_payload.get("accounting_identity_check"),
            "source": _glob_record(RAW_ROOT / "usaspending" / "2026-08-01", "federal_account_*.json", "USAspending federal-account budget-resource responses"),
            "boundary": "FY2024 budget authority, appropriations, obligations, outlays, and unobligated balances are federal account-reporting quantities. They establish account budget context, not tax/debt/money-creation attribution, bank settlement, supplier invoices, or physical-resource conversion.",
        },
        "subaward_downstream_recipient": {
            "status": "PASS_WITH_BOUNDARY" if subaward_downstream_ready else "BLOCKED",
            "artifact": subaward_downstream,
            "coverage": subaward_downstream_payload.get("coverage"),
            "source": _glob_record(RAW_ROOT / "usaspending" / "2026-08-01", "subaward_*.json", "USAspending subaward count and downstream-recipient responses"),
            "boundary": "The fixed ten-award sample has complete reported subaward-page coverage; downstream recipient, amount, action date, and description fields are award-reporting observations, not bank settlement, invoice, payroll, or ultimate financing-source records.",
        },
        "award_outlay_reconciliation": {
            "status": "PASS_WITH_BOUNDARY" if award_outlay_ready else "BLOCKED",
            "artifact": award_outlay_reconciliation,
            "source": _glob_record(RAW_ROOT / "usaspending" / "2026-08-01", "federal_award_outlay_reconciliation_*.json", "USAspending grouped award and Treasury outlay reconciliation inputs"),
            "boundary": "The fixed DOE FY2024 comparison measures grouped award obligations against Treasury program net outlays. It is a scale diagnostic with a NOT_ONE_TO_ONE result, not proof of payment settlement or financing-source attribution.",
        },
        "treasury_aggregate_funding_source": {
            "status": "PASS_WITH_BOUNDARY" if treasury_funding_ready else "BLOCKED",
            "artifact": treasury_funding,
            "source": _glob_record(RAW_ROOT / "treasury_fiscal_data" / "2026-08-01", "*.json", "Treasury Fiscal Data MTS and debt API responses"),
            "boundary": "Treasury records aggregate receipts, outlays, deficit financing, and public debt for FY2024. It does not assign a tax, borrowing, or cash-balance source to an individual USAspending award, invoice, bank settlement, or physical transformation.",
        },
        "public_federal_award_ledger": {
            "status": "PASS_WITH_BOUNDARY" if usaspending_ready else "BLOCKED",
            "artifact": usaspending_ledger,
            "source": _glob_record(RAW_ROOT / "usaspending" / "2026-08-01", "*.json", "USAspending.gov DOE FY2024 award transaction pages"),
            "boundary": "The bounded USAspending sample links federal awarding/funding agency, recipient, award ID, obligation amount, action date, and NAICS/PSC metadata. It is not final cash settlement, a private invoice/payroll ledger, or transaction-level identification of tax, debt, or money-creation funding.",
        },
        "firm_project_payment_ledger": {
            "status": "BLOCKED",
            "artifact": {"public_firm_funding_proxy": sec_funding_proxy, "public_firm_funding_mix": sec_funding_mix, "ledger_gate": project_ledger_gate},
            "source": {
                "required_providers": ["Census business microdata", "administrative ACH/card/invoice records"],
                "local_archives": [],
                "status": "MISSING",
            },
            "boundary": "SEC public-firm annual accounting provides profit/debt/capex channel proxies, but no invoice-level payer, supplier, project, or physical-resource ledger is public in this package.",
        },
        "industry_concordance": {
            "status": "PASS_WITH_BOUNDARY" if concordance_path.is_file() else "BLOCKED",
            "source": _xlsx_record(concordance_path, "BEA industry and commodity codes / NAICS concordance"),
            "boundary": "The BEA code concordance is archived and hashed, but it does not itself provide payer, labor-hours, or physical-resource observations.",
        },
    }
    blocking = [name for name, item in evidence.items() if item["status"] in {"BLOCKED", "MISSING"}]
    payload = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "BLOCKED" if blocking else "PASS_WITH_BOUNDARY",
        "controller_status": "PAYER_RESOURCE_JOIN_NOT_IDENTIFIED" if blocking else "PAYER_RESOURCE_JOIN_SOURCE_READY",
        "generated_at_utc": utc_now(),
        "coverage": {
            "requested": "sectoral funding -> industry use -> labor hours -> physical resources -> output/innovation",
            "no_imputation": True,
            "bounded_labor_subset_ready": bool(bls_hours_ready),
            "public_federal_award_ledger_ready": bool(usaspending_ready),
            "treasury_aggregate_funding_source_ready": bool(treasury_funding_ready),
            "award_outlay_reconciliation_ready": bool(award_outlay_ready),
            "award_level_account_outlay_ready": bool(award_level_ready),
            "award_federal_account_linkage_ready": bool(award_funding_bounded),
            "federal_account_budget_resource_ready": bool(federal_account_budget_ready),
            "subaward_downstream_recipient_ready": bool(subaward_downstream_ready),
            "recipient_public_firm_funding_channels_ready": bool(recipient_funding_ready),
            "bounded_labor_subset": evidence["labor_industry_hours"].get("artifact", {}).get("bounded_coverage"),
        },
        "evidence": evidence,
        "blocking_components": blocking,
        "required_join": [
            "transaction or firm/project funding records",
            "industry/commodity input-output table",
            "industry labor hours and occupations",
            "source-level physical resource quantities",
            "versioned industry/commodity/labor/resource concordance",
        ],
        "claim_boundary": "This gate reports source/join readiness only. It does not infer payment-level provenance, funding shares, resource causality, or innovation causality.",
        "limitations": [
            "Operating surplus and net saving are accounting aggregates, not earmarked cash sources.",
            "Debt and equity liability transactions can include refinancing, redemptions, and repurchases.",
            "A complete public dataset linking every payment to a physical resource transformation is not present in the frozen package.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("Payer-resource join readiness:", payload["status"], "blocking components", len(blocking))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
