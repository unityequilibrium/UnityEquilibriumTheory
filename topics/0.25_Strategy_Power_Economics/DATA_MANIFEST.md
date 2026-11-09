# Data Manifest — Topic 0.25

## Data architecture

| Level | Main sources | Current use | Boundary |
| --- | --- | --- | --- |
| `L0` | FRED/H.6, BEA, BLS, EIA, FHFA | U.S. macro and welfare diagnostics | revised aggregate association |
| `L1` | Fed Z.1, BEA–BLS KLEMS, BEA I-O, USEEIO, USGS | sector accounting and modelled footprints | no individual payment lineage |
| `L2` | DCPC, CE, SEC XBRL, USAspending, CFS public files | bounded payment/firm/award/shipment evidence | incomplete joins and coverage |
| `L3` | FSRDC and matched lender–borrower candidates | planned | access/ethics/identification required |
| `L4` | tagged bank/processor/invoice/ERP/inventory records | absent | required for observed payer-resource lineage |

## Canonical U.S. package

The frozen U.S. annual macro panel remains 1959–2024 with source identities and hashes in `Data/03_Research/uet_us_economics_source_manifest.json`. It is retained for reproducibility of legacy diagnostics; it is not the final KLEMS research panel.

No silent imputation is permitted. Provider units, annualization, per-capita/per-worker transformations, index bases, and hashes are stored in the source and transformation manifests.

## Global package — blocked

The frozen WDI raw package declares:

- real GDP per capita;
- PPP real GDP per capita;
- population;
- energy use per capita.

The repaired builder requires all four fields, excludes World Bank aggregate codes, requires consecutive common coverage, and reconciles source hashes. Current complete-case rows: `0`. Therefore:

- `0_25_global_wdi_panel.json` is `BLOCKED / INVALID_SUPERSEDED`;
- legacy leave-one-country, leave-one-region, PPP, strata, income, and IMF/WDI join artifacts are `INVALID_SUPERSEDED`;
- no current global result contributes to Evidence Grade A.

## Asset and convenience-file quarantine

Yahoo price-only gold, S&P, and Bitcoin files and `Global_Economy_2024.json` remain legacy diagnostics. They are not primary Book 1 evidence and cannot substitute for licensed total-return or source-locked asset data.

## Lineage labels

Every payer/resource output must declare one of `OBSERVED`, `ACCOUNTING_INFERRED`, `MODEL_ALLOCATED`, or `UNOBSERVED` and its evidence level `L0–L4`.
