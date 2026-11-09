# Topic 0.25 Research Code

This directory contains exploratory strategy simulations and the source-locked Book 1 economics
hardening lane. The two are separate evidence classes.

## Book 1 hardening scripts

| Script | Role | Output |
| :-- | :-- | :-- |
| `Research_UET_Economics_External_Source_Transform.py` | download/parse official BEA/EIA files and a provider-supplied EPI chart export | raw-cache hashes and transform manifest |
| `Research_UET_Economics_Source_Package.py` | lock source identity, terms, units, coverage, and hashes | source/formula/parameter/holdout/claim gates |
| `Research_UET_Economics_Panel.py` | annualize FRED, validate coverage, construct indexed proxies, reject imputation | normalized panel and panel-status gate |
| Research_UET_Measurement_Validity_Audit.py | compare declared R/N/K/I proxy families and explicit missingness | measurement-validity artifact |
| Research_UET_Welfare_Source_Package.py | archive declared rent, OER, income, and FHFA/FRED series | welfare source manifest |
| Research_UET_Welfare_Audit.py | construct separate cost-of-living and household-welfare outcomes | welfare artifact |
| Research_UET_Resource_Equation_Audit.py | test the predeclared R/N/K/I diagnostic and rolling-origin candidate rule | resource artifact |
| `Research_Stone_Balloon_Audit.py` | test monetary-resource mismatch and inflation baselines; gate assets | Stone artifact |
| `Research_Energy_Density_Audit.py` | separate throughput history from literal density definition | energy artifact |
| `Research_Wage_Productivity_Audit.py` | reproduce EPI chart construction and report BLS separately | wage artifact |
| `Verify_UET_Economics_Hardening.py` | execute and aggregate all lanes; fail on subcommand errors and missing legacy boundary warnings | aggregate verifier artifact |

## Rerun

```powershell
cd C:\Users\santa\Desktop\uet_harness
.\.venv\Scripts\python.exe docs/topics/0.25_Strategy_Power_Economics/Code/03_Research/Research_UET_Economics_External_Source_Transform.py --vintage 2026-07-12 --epi-csv <provider-export.csv>
.\.venv\Scripts\python.exe docs/topics/0.25_Strategy_Power_Economics/Code/03_Research/Research_UET_Economics_Source_Package.py --vintage 2026-07-12
.\.venv\Scripts\python.exe docs/topics/0.25_Strategy_Power_Economics/Code/03_Research/Verify_UET_Economics_Hardening.py
```

## Evidence boundary

A `PASS` source or panel gate means only that the declared input contract is present. A
`DIAGNOSTIC_COMPLETE` artifact means the predeclared comparison ran. Neither status supports
claims of economic-law confirmation, fiat causality, policy validation, asset superiority, or
strategic superiority. The current aggregate is intentionally `WARN` because the literal
energy-density and architecture WARN gates remain open.

The older engine/proof/research scripts remain exploratory model proposals and are not included
in the Book 1 primary panel.

The verifier also embeds the preregistered research register, variable dictionary, causal DAG,
claim matrix, and 12-gate WARN registry from Data/03_Research. These contracts define the
ten-wave path from Package Tier A to the Evidence Grade A target; they do not change the
current Claim Class C boundary.
| Research_UET_IMF_WDI_Normalization.py | normalize IMF CPI ISO3 to WDI ISO2 with coverage/no-imputation checks | IMF-WDI normalization artifact |
| Research_UET_Global_WDI_Region_Leave_One_Out.py | run official-region leave-one-out robustness with aggregate exclusion | regional robustness artifact |
| Research_UET_Funding_Source_Proxy_Panel.py | construct no-imputation annual sectoral proxies for profits, investment, business credit, and dividends | funding proxy panel |
| Research_UET_Funding_Source_Association_Audit.py | calculate descriptive profit/credit/dividend associations with investment growth | funding association artifact |
| Research_UET_Funding_Source_Lag_Association.py | report predeclared 0-2 year funding-source lag associations | funding lag artifact |
| Research_UET_Fed_Z1_Source_Probe.py | archive and count official Fed Z.1 release tables | Fed Z.1 source probe |
| Research_UET_Fed_Z1_Funding_Mapping_Probe.py | map sectoral wages, taxes, interest, dividends, saving, capital formation, debt, and equity flows; check the rounded accounting bridge | Fed Z.1 funding mapping artifact |
| Research_UET_BLS_IO_Source_Gate.py | record the official BLS I-O source identity, coverage, access observation, and provider quality notice without bypassing controls | BLS I-O source gate |
| Research_UET_Fed_Z1_Funding_Mix_Audit.py | compute signed 0-2-year net-flow associations and payment-flow scale; reject gross earmarked-share interpretation | funding mix audit artifact |
| Research_UET_Payer_Resource_Join_Readiness.py | check source/hash readiness for funding -> industry use -> labor hours -> physical resources -> project/output joins | payer-resource join readiness artifact |
| Research_UET_BEA_1997_IO_Benchmark_Audit.py | validate the official 1997 BEA make/use and requirements benchmark without treating it as a time series | BEA benchmark structural artifact |
| Research_UET_BLS_Industry_Hours_Source_Package.py | query the official BLS API for predeclared NAICS4 annual hours, archive responses, hash inputs, and report missing codes | BLS industry-hours source package |
| Research_UET_USGS_Material_Quantity_Audit.py | parse source-locked USGS mineral workbooks into national physical-quantity rows without industry allocation | USGS material quantity artifact |
| Research_UET_USASpending_Award_Level_Outlay_Audit.py | retrieve ten fixed USAspending award details, compare account obligation/outlay fields, and enforce the nonrepresentative/non-settlement boundary | award-level outlay artifact |
| Research_UET_USASpending_Award_Funding_Account_Audit.py | retrieve the same ten `/awards/funding/` responses, extract FY2024 federal-account/agency/object-class rows, preserve missing awards, and enforce the no-financing/no-settlement boundary | award funding-account artifact |
| Research_UET_USASpending_Federal_Account_Budget_Resource_Audit.py | resolve every observed federal account to its profile, FY2024 internal-ID budget snapshot, TAS tree, and paginated program activities; check budget-authority identity and preserve the no-financing/no-settlement boundary | federal-account budget-resource artifact |
| Research_UET_USASpending_Subaward_Downstream_Recipient_Audit.py | retrieve all ten subaward counts and every positive-count page for the fixed awards, reconcile reported versus retrieved rows, and normalize downstream recipients/descriptions without calling them settlements | downstream subaward-recipient artifact |
| Research_UET_Federal_Award_Outlay_Reconciliation.py | compare fixed DOE FY2024 grouped USAspending award obligations with Treasury DOE net outlays and enforce the NOT_ONE_TO_ONE boundary | award/outlay reconciliation artifact |
| Research_UET_Treasury_Funding_Source_Package.py | archive fixed Treasury MTS/debt FY2024 endpoints and normalize aggregate receipts, outlays, financing, and debt | Treasury funding-source artifact |
| Research_UET_USASpending_Federal_Award_Ledger.py | archive a fixed USAspending.gov DOE FY2024 five-page award-transaction sample, hash raw responses, and normalize obligations | public federal-award ledger artifact |
| Research_UET_SEC_Public_Firm_Funding_Proxy.py | archive SEC Company Facts for the predeclared nonfinancial-firm sample and extract annual profit/cash/capex/debt/dividend facts | SEC public-firm funding proxy |
| Research_UET_SEC_Public_Firm_Funding_Mix_Audit.py | calculate descriptive firm-level funding-scale ratios while keeping gross funding shares unidentified | SEC funding-mix artifact |
| Research_UET_SEC_Recipient_Funding_Concordance.py | exact-match prime/subaward recipient names to SEC issuers, archive Company Facts, and report annual profit/cash/capex/debt channels without assigning award-dollar funding shares | SEC recipient funding concordance artifact |
| Research_UET_Project_Payment_Ledger_Gate.py | record the public-data boundary and restricted-use route for invoice/project payer identity | project payment ledger gate |
