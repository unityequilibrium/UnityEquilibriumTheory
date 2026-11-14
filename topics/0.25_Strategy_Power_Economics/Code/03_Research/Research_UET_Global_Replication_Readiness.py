"""Machine-readable readiness gate for the post-U.S. global replication wave.

This script deliberately emits a blocker until country-level source vintages,
PPP/exchange-rate conventions, and common coverage are frozen. It never
constructs a global result from the U.S. panel or silently fills missing data.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "Result" / "artifacts" / "0_25_global_replication_readiness.json"
REQUIRED = {
    "World Bank WDI": "GDP, population, energy, poverty, macro indicators",
    "OECD": "productivity, income, compensation, investment, household accounts",
    "ILOSTAT": "productivity, earnings, hours, labor income",
    "IMF": "CPI, exchange rates, monetary/financial statistics",
    "BIS": "credit, debt, financial conditions",
    "WID": "income/wealth distribution and distributional national accounts",
}

def main() -> int:
    wdi_manifest = Path("docs/data/external/economics/global/wdi/2026-07-16/source_manifest.json")
    wdi_panel = Path("docs/topics/0.25_Strategy_Power_Economics/Result/artifacts/0_25_global_wdi_panel.json")
    wdi_ready = wdi_manifest.exists() and wdi_panel.exists() and json.loads(wdi_panel.read_text()).get("status") == "PASS"
    blockers = [
        "OECD, ILOSTAT, IMF, BIS, and WID source manifests with release/vintage/hash records are absent.",
        "PPP and exchange-rate versions are not yet pooled through a measurement-invariance protocol.",
        "No leave-one-region-out artifact or resource-exporter classification is locked.",
        "Independent global replication remains absent.",
    ]
    payload = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "PARTIAL_PASS" if wdi_ready else "BLOCKED",
        "completed_sublanes": {"world_bank_wdi": "PASS" if wdi_ready else "BLOCKED"},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "required_providers": REQUIRED,
        "design": {
            "minimum_economies": 30,
            "minimum_common_years_per_economy": 20,
            "strata": ["high_income", "middle_income", "low_income", "resource_exporter"],
            "robustness": ["leave_one_country_out", "leave_one_region_out", "PPP_vs_exchange_rate"],
        },
        "blockers": blockers,
        "claim_boundary": "No global sign, causal, or universality claim is permitted until this gate is PASS and an independent replication artifact exists.",
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Global replication readiness:", payload["status"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
