"""Run and aggregate the bounded Book 1 economics hardening lane for Topic 0.25."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from economic_hardening_common import (
    ARTIFACT_DIR,
    CAUSAL_DAG,
    CLAIM_MATRIX,
    CLAIM_GATE,
    FORMULA_GATE,
    HOLDOUT_POLICY,
    MEASUREMENT_ARTIFACT,
    PARAMETER_POLICY,
    PANEL_STATUS,
    RESEARCH_DATA,
    RESEARCH_REGISTER,
    ROOT,
    SOURCE_MANIFEST,
    SOURCE_READINESS,
    VARIABLE_DICTIONARY,
    WARN_GATE_REGISTRY,
    WELFARE_ARTIFACT,
    MONEY_CREDIT_ARTIFACT,
    GLOBAL_REPLICATION_ARTIFACT,
    GLOBAL_WDI_PANEL_ARTIFACT,
    GLOBAL_WDI_LOO_ARTIFACT,
    GLOBAL_WDI_PPP_ARTIFACT,
    GLOBAL_WDI_STRATA_ARTIFACT,
    GLOBAL_WDI_REGION_LOO_ARTIFACT,
    IMF_WDI_NORMALIZATION_ARTIFACT,
    FUNDING_FLOW_GATE_ARTIFACT,
    FUNDING_PROXY_PANEL_ARTIFACT,
    FUNDING_ASSOCIATION_ARTIFACT,
    FUNDING_LAG_ARTIFACT,
    FED_Z1_PROBE_ARTIFACT,
    FED_Z1_FUNDING_MAPPING_ARTIFACT,
    BLS_IO_SOURCE_GATE_ARTIFACT,
    FED_Z1_FUNDING_MIX_ARTIFACT,
    PAYER_RESOURCE_JOIN_ARTIFACT,
    BEA_1997_IO_ARTIFACT,
    BLS_INDUSTRY_HOURS_ARTIFACT,
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
    CAUSAL_GATE_ARTIFACT,
    REPLICATION_GATE_ARTIFACT,
    PUBLICATION_GATE_ARTIFACT,
    WELFARE_SOURCE_MANIFEST,
    load_json,
    relative,
    runtime_environment,
    sha256,
    utc_now,
    write_json,
)


ARTIFACT = ARTIFACT_DIR / "0_25_uet_economics_verification.json"
BOOK_ALIGNMENT_ARTIFACT = ARTIFACT_DIR / "0_25_book_topic_alignment_gate.json"
GLOBAL_PANEL_INTEGRITY_ARTIFACT = ARTIFACT_DIR / "0_25_global_panel_integrity_gate.json"
BOOK_BLUEPRINT = ROOT / "uet_history/3_publish/books/economics_ai_energy/01_economics/book_1_blueprint.md"
BOOK_RESEARCH_SPEC = ROOT / "uet_history/3_publish/books/economics_ai_energy/01_economics/RESEARCH_SPECIFICATION.md"
BOOK_BLUEPRINT_VERSION = "book1-economics-v2-research-reset"
HERE = Path(__file__).resolve().parent
SUB_ARTIFACTS = {
    "book_topic_alignment": BOOK_ALIGNMENT_ARTIFACT,
    "global_panel_integrity": GLOBAL_PANEL_INTEGRITY_ARTIFACT,
    "measurement_validity": MEASUREMENT_ARTIFACT,
    "welfare": WELFARE_ARTIFACT,
    "money_credit_inflation": MONEY_CREDIT_ARTIFACT,
    "global_replication_readiness": GLOBAL_REPLICATION_ARTIFACT,
    "global_wdi_panel": GLOBAL_WDI_PANEL_ARTIFACT,
    "global_wdi_leave_one_out": GLOBAL_WDI_LOO_ARTIFACT,
    "global_wdi_ppp_comparison": GLOBAL_WDI_PPP_ARTIFACT,
    "global_wdi_strata": GLOBAL_WDI_STRATA_ARTIFACT,
    "global_wdi_region_leave_one_out": GLOBAL_WDI_REGION_LOO_ARTIFACT,
    "imf_wdi_normalization": IMF_WDI_NORMALIZATION_ARTIFACT,
    "funding_source_flow": FUNDING_FLOW_GATE_ARTIFACT,
    "funding_source_proxy_panel": FUNDING_PROXY_PANEL_ARTIFACT,
    "funding_source_association": FUNDING_ASSOCIATION_ARTIFACT,
    "funding_source_lag_association": FUNDING_LAG_ARTIFACT,
    "fed_z1_source_probe": FED_Z1_PROBE_ARTIFACT,
    "fed_z1_funding_mapping": FED_Z1_FUNDING_MAPPING_ARTIFACT,
    "bls_io_source_gate": BLS_IO_SOURCE_GATE_ARTIFACT,
    "fed_z1_funding_mix": FED_Z1_FUNDING_MIX_ARTIFACT,
    "payer_resource_join": PAYER_RESOURCE_JOIN_ARTIFACT,
    "bea_1997_io_benchmark": BEA_1997_IO_ARTIFACT,
    "bls_industry_hours": BLS_INDUSTRY_HOURS_ARTIFACT,
    "usaspending_federal_award_ledger": USASPENDING_LEDGER_ARTIFACT,
    "treasury_funding_source": TREASURY_FUNDING_SOURCE_ARTIFACT,
    "award_outlay_reconciliation": AWARD_OUTLAY_RECONCILIATION_ARTIFACT,
    "award_level_outlay": AWARD_LEVEL_OUTLAY_ARTIFACT,
    "award_funding_account": AWARD_FUNDING_ACCOUNT_ARTIFACT,
    "federal_account_budget_resource": FEDERAL_ACCOUNT_BUDGET_RESOURCE_ARTIFACT,
    "subaward_downstream_recipient": SUBAWARD_DOWNSTREAM_ARTIFACT,
    "usgs_material_quantities": USGS_MATERIAL_QUANTITY_ARTIFACT,
    "sec_public_firm_funding_proxy": SEC_PUBLIC_FIRM_PROXY_ARTIFACT,
    "sec_public_firm_funding_mix": SEC_PUBLIC_FIRM_MIX_ARTIFACT,
    "sec_recipient_funding_concordance": SEC_RECIPIENT_FUNDING_CONCORDANCE_ARTIFACT,
    "project_payment_ledger": PROJECT_PAYMENT_LEDGER_ARTIFACT,
    "causal_identification": CAUSAL_GATE_ARTIFACT,
    "independent_replication": REPLICATION_GATE_ARTIFACT,
    "publication_hardening": PUBLICATION_GATE_ARTIFACT,
    "resource_equation": ARTIFACT_DIR / "0_25_uet_resource_equation_audit.json",
    "stone_balloon": ARTIFACT_DIR / "0_25_stone_balloon_audit.json",
    "energy_density": ARTIFACT_DIR / "0_25_energy_density_audit.json",
    "wage_productivity": ARTIFACT_DIR / "0_25_wage_productivity_audit.json",
}
LEGACY_DOC_ROOT = ROOT / "docs/topics/0.25_Strategy_Power_Economics/Doc"


def legacy_claim_quarantine() -> dict:
    docs = sorted(LEGACY_DOC_ROOT.rglob("*.md")) if LEGACY_DOC_ROOT.exists() else []
    missing_warning = []
    for path in docs:
        content = path.read_text(encoding="utf-8", errors="replace")
        if "Legacy claim boundary" not in content:
            missing_warning.append(relative(path))
    return {
        "status": "PASS" if docs and not missing_warning else "WARN",
        "files_scanned": len(docs),
        "missing_boundary_warning_files": missing_warning,
        "required_boundary_phrase": "Legacy claim boundary",
        "claim_effect": "Legacy notes remain quarantined from topic status and primary Book 1 evidence.",
    }


def run(script: str, arguments: list[str] | None = None) -> dict:
    command = [sys.executable, str(HERE / script)] + (arguments or [])
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "script": relative(HERE / script),
        "command": command,
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-1200:],
        "stderr_tail": completed.stderr[-1200:],
    }


def artifact_reference(path: Path) -> dict:
    if not path.exists():
        return {"path": relative(path), "exists": False, "sha256": None, "status": "MISSING", "controller_status": None, "blockers": []}
    payload = load_json(path)
    return {
        "path": relative(path),
        "exists": True,
        "sha256": sha256(path),
        "status": payload.get("status", "PRESENT"),
        "controller_status": payload.get("controller_status"),
        "blockers": payload.get("blockers", []),
    }


def file_reference(path: Path) -> dict:
    return {
        "path": relative(path),
        "exists": path.exists(),
        "sha256": sha256(path) if path.exists() else None,
        "status": "PRESENT" if path.exists() else "MISSING",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-sources", action="store_true", help="Download public FRED source files before running the non-network diagnostics.")
    args = parser.parse_args()
    commands = []
    commands.append(run("Research_UET_Book_Topic_Alignment_Gate.py"))
    if args.refresh_sources:
        commands.append(run("Research_UET_Economics_Source_Package.py", ["--refresh"]))
    elif not SOURCE_MANIFEST.exists():
        commands.append(run("Research_UET_Economics_Source_Package.py"))
    commands.extend(
        [
            run("Research_UET_Economics_Panel.py"),
            run("Research_UET_Measurement_Validity_Audit.py"),
            run("Research_UET_Welfare_Audit.py"),
            run("Research_UET_Money_Credit_Inflation_Audit.py"),
            run("Research_UET_Global_WDI_Panel.py"),
        ]
    )
    global_panel = load_json(GLOBAL_WDI_PANEL_ARTIFACT)
    if global_panel.get("status") == "PASS":
        commands.extend(
            [
                run("Research_UET_Global_WDI_Leave_One_Out.py"),
                run("Research_UET_Global_WDI_Region_Leave_One_Out.py"),
                run("Research_UET_IMF_WDI_Normalization.py"),
                run("Research_UET_Global_WDI_PPP_Comparison.py"),
            ]
        )
    commands.extend(
        [
            run("Research_UET_Funding_Source_Proxy_Panel.py"),
            run("Research_UET_Funding_Source_Association_Audit.py"),
            run("Research_UET_Funding_Source_Lag_Association.py"),
            run("Research_UET_Fed_Z1_Source_Probe.py"),
            run("Research_UET_Fed_Z1_Funding_Mapping_Probe.py"),
            run("Research_UET_BLS_IO_Source_Gate.py"),
            run("Research_UET_Fed_Z1_Funding_Mix_Audit.py"),
            run("Research_UET_BEA_1997_IO_Benchmark_Audit.py"),
            run("Research_UET_BLS_Industry_Hours_Source_Package.py"),
            run("Research_UET_USASpending_Federal_Award_Ledger.py"),
            run("Research_UET_Treasury_Funding_Source_Package.py"),
            run("Research_UET_Federal_Award_Outlay_Reconciliation.py"),
            run("Research_UET_USASpending_Award_Level_Outlay_Audit.py"),
            run("Research_UET_USASpending_Subaward_Downstream_Recipient_Audit.py"),
            run("Research_UET_USASpending_Award_Funding_Account_Audit.py"),
            run("Research_UET_USASpending_Federal_Account_Budget_Resource_Audit.py"),
            run("Research_UET_USGS_Material_Quantity_Audit.py"),
            run("Research_UET_SEC_Public_Firm_Funding_Proxy.py"),
            run("Research_UET_SEC_Public_Firm_Funding_Mix_Audit.py"),
            run("Research_UET_SEC_Recipient_Funding_Concordance.py"),
            run("Research_UET_Payer_Resource_Join_Readiness.py"),
            run("Research_UET_Project_Payment_Ledger_Gate.py"),
            run("Research_UET_Funding_Source_Flow_Gate.py"),
            run("Research_UET_Causal_Identification_Gate.py"),
            run("Research_UET_Independent_Replication_Gate.py"),
            run("Research_UET_Publication_Hardening_Gate.py"),
            run("Research_UET_Global_Replication_Readiness.py"),
            run("Research_UET_Resource_Equation_Audit.py"),
            run("Research_Stone_Balloon_Audit.py"),
            run("Research_Energy_Density_Audit.py"),
            run("Research_Wage_Productivity_Audit.py"),
        ]
    )
    readiness = load_json(SOURCE_READINESS)
    source_manifest_payload = load_json(SOURCE_MANIFEST)
    welfare_source_manifest_payload = load_json(WELFARE_SOURCE_MANIFEST)
    transform_manifest_payload = load_json(RESEARCH_DATA / "uet_us_economics_transform_manifest.json")
    panel_payload = load_json(PANEL_STATUS)
    formula_payload = load_json(FORMULA_GATE)
    parameter_payload = load_json(PARAMETER_POLICY)
    holdout_payload = load_json(HOLDOUT_POLICY)
    research_register_payload = load_json(RESEARCH_REGISTER)
    variable_dictionary_payload = load_json(VARIABLE_DICTIONARY)
    causal_dag_payload = load_json(CAUSAL_DAG)
    claim_matrix_payload = load_json(CLAIM_MATRIX)
    warn_gate_registry_payload = load_json(WARN_GATE_REGISTRY)
    architecture_files = {
        "research_register": RESEARCH_REGISTER,
        "variable_dictionary": VARIABLE_DICTIONARY,
        "causal_dag": CAUSAL_DAG,
        "claim_matrix": CLAIM_MATRIX,
        "warn_gate_registry": WARN_GATE_REGISTRY,
    }
    architecture_missing = [name for name, path in architecture_files.items() if not path.exists()]
    architecture_gate_rows = warn_gate_registry_payload.get("gates", [])
    architecture_blockers = [
        f"{row.get('gate_id')}: {row.get('status')}"
        for row in architecture_gate_rows
        if row.get("controlling") and row.get("status") not in {"PASS", "PASS_WITH_BOUNDARY"}
    ]
    if architecture_missing:
        architecture_blockers.extend(f"architecture_file_missing: {name}" for name in architecture_missing)
    sub_artifacts = {name: artifact_reference(path) for name, path in SUB_ARTIFACTS.items()}
    sub_artifact_payloads = {name: load_json(path) for name, path in SUB_ARTIFACTS.items()}
    legacy_quarantine = legacy_claim_quarantine()
    source_ready = readiness.get("status") == "PASS"
    command_failures = [f"{item['script']}: exit_code={item['exit_code']}" for item in commands if item.get("exit_code") != 0]
    non_pass_statuses = {"MISSING", "WARN", "BLOCKED", "INVALID_SUPERSEDED", "FAIL", "ERROR"}
    sub_complete = (
        not command_failures
        and legacy_quarantine["status"] == "PASS"
        and all(item["status"] not in non_pass_statuses for item in sub_artifacts.values())
    )
    alignment_payload = load_json(BOOK_ALIGNMENT_ARTIFACT)
    controller_status = alignment_payload.get("controlling_blocker", "HYPOTHESIS_ONTOLOGY_AND_VERSION_NOT_LOCKED")
    status = "DIAGNOSTIC_COMPLETE" if source_ready and sub_complete and not architecture_blockers else "WARN"
    next_blockers = list(readiness.get("blockers", []))
    next_blockers.extend(command_failures)
    if legacy_quarantine["status"] != "PASS":
        next_blockers.append("legacy_claim_quarantine: WARN")
        next_blockers.extend(legacy_quarantine["missing_boundary_warning_files"])
    if not source_ready and not next_blockers:
        next_blockers.append("Source-readiness gate is absent or not PASS.")
    for name, item in sub_artifacts.items():
        if item["status"] in non_pass_statuses:
            next_blockers.append(f"{name}: {item['status']}")
            next_blockers.extend(item.get("blockers", []))
    next_blockers.extend(architecture_blockers)
    claim_gate = {
        "schema_version": "3.0",
        "topic": "0.25_Strategy_Power_Economics",
        "book_blueprint_version": BOOK_BLUEPRINT_VERSION,
        "gate": "uet_book1_economics_claim_gate",
        "controller_status": controller_status,
        "allowed_claims_now": [
            "The topic contains a version-locked, source-gated internal economics architecture.",
            "A completed lane may report its predeclared descriptive comparison and negative results with its evidence level.",
            "Purchasing power, exchange value, payment use, and store-of-value results are reported separately.",
        ],
        "blocked_claims": [
            "R=N+K+I is a derived or confirmed economic law; it is retired as an identity.",
            "R/M is an observed or universal value of money.",
            "A model-allocated supply-chain footprint is observed payment lineage.",
            "Fiat money causally created inflation, wage divergence, or wealth transfer.",
            "Gold or equities are validated scaling pegs or superior assets.",
            "A policy, strategy, social-stabilization, or Nash-equilibrium claim is validated.",
        ],
        "machine_readable_next_blockers": sorted(set(next_blockers)),
        "claim_boundary": "All current results remain Claim Class C unless a lane independently passes its measurement, identification, external-replication, and publication gates.",
        "strategy_social_quarantine": "Strategy, power, Nash, and social-stabilization notes remain exploratory and excluded from core economics evidence.",
    }
    write_json(CLAIM_GATE, claim_gate)
    artifact = {
        "schema_version": "2.0",
        "topic": "0.25_Strategy_Power_Economics",
        "book_blueprint_version": BOOK_BLUEPRINT_VERSION,
        "book_blueprint": file_reference(BOOK_BLUEPRINT),
        "book_research_specification": file_reference(BOOK_RESEARCH_SPEC),
        "status": status,
        "generated_at_utc": utc_now(),
        "command": "python docs/topics/0.25_Strategy_Power_Economics/Code/03_Research/Verify_UET_Economics_Hardening.py",
        "environment": runtime_environment(),
        "claim_class": "C - internal economic data integrity and historical diagnostic benchmark",
        "formula_ids": ["BOOK-HEURISTIC-001", "EC25-PRODUCTION-KLEMS", "EC25-MONEY-PURCHASING-POWER", "EC25-MONEY-IDENTITY", "EC25-RESOURCE-COVERAGE-DIAGNOSTIC", "EC25-WAGE-PRODUCTIVITY-GAP"],
        "source_manifest": artifact_reference(SOURCE_MANIFEST),
        "welfare_source_manifest": artifact_reference(WELFARE_SOURCE_MANIFEST),
        "source_readiness": readiness,
        "source_transformation_manifest": artifact_reference(RESEARCH_DATA / "uet_us_economics_transform_manifest.json"),
        "panel_status": artifact_reference(PANEL_STATUS),
        "execution_gate": {"all_commands_exit_zero": not command_failures, "command_failures": command_failures},
        "legacy_claim_quarantine": legacy_quarantine,
        "formula_gate": artifact_reference(FORMULA_GATE),
        "parameter_policy": artifact_reference(PARAMETER_POLICY),
        "holdout_policy": artifact_reference(HOLDOUT_POLICY),
        "research_architecture": {
            "current_package_tier": research_register_payload.get("current_package_tier", "Package Tier A"),
            "target_evidence_grade": research_register_payload.get("target_evidence_grade", "Evidence Grade A"),
            "current_claim_class": research_register_payload.get("current_claim_class", "C"),
            "active_waves": [row for row in research_register_payload.get("waves", []) if row.get("status") == "IN_PROGRESS"],
            "quarantined_lanes": research_register_payload.get("quarantined_lanes", []),
            "evidence_levels": research_register_payload.get("evidence_levels", {}),
            "architecture_status": "PASS" if not architecture_blockers else "WARN",
            "controlling_gate_blockers": sorted(set(architecture_blockers)),
            "file_references": {name: artifact_reference(path) for name, path in architecture_files.items()},
            "warn_gate_registry": warn_gate_registry_payload,
        },
        "sub_artifacts": sub_artifacts,
        "evidence_bundle": {
            "retrieval_vintage": source_manifest_payload.get("retrieval_vintage"),
            "source_records_with_hashes": source_manifest_payload.get("sources", []),
            "welfare_source_records_with_hashes": welfare_source_manifest_payload.get("sources", []),
            "source_transformation_manifest": transform_manifest_payload,
            "panel_status_payload": panel_payload,
            "formula_gate_payload": formula_payload,
            "parameter_policy_payload": parameter_payload,
            "holdout_policy_payload": holdout_payload,
            "research_register_payload": research_register_payload,
            "variable_dictionary_payload": variable_dictionary_payload,
            "causal_dag_payload": causal_dag_payload,
            "claim_matrix_payload": claim_matrix_payload,
            "warn_gate_registry_payload": warn_gate_registry_payload,
            "sub_artifact_payloads": sub_artifact_payloads,
        },
        "commands": commands,
        "economics_claim_scope_gate": claim_gate,
        "limitations": [
            "BOOK-HEURISTIC-001 is retired as an identity; legacy R/N/K/I results are bounded proxy sensitivities only.",
            "Money value is not represented by one scalar; purchasing power, exchange value, payment use, real returns, and resource coverage remain separate.",
            "The 1971 regime summaries are non-causal and exclude 1971-1973 from pre/post descriptive comparisons.",
            "An internal candidate signal cannot upgrade Claim Class C or support policy, asset-superiority, or strategic-superiority claims.",
        ],
    }
    write_json(ARTIFACT, artifact)
    print(f"UET Book 1 economics hardening: {status}")
    print(f"  controller: {controller_status}")
    print(f"  artifact: {ARTIFACT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
