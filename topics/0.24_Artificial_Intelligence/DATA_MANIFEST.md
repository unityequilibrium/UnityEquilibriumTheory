# Data Manifest

Current data reality status: `real source referenced`

The topic has usable local benchmark inputs, but not yet a fully archival upstream
provenance package. Claims must therefore remain below paper-ready status until
source URLs/DOIs, retrieval dates, preprocessing notes, and hashes are normalized.

## Primary Inputs

| Dataset | Local path | Source | Unit convention | Benchmark role | Provenance status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Scaling-law constants | `Data/03_Research/scaling_laws.json` | Kaplan et al., "Scaling Laws for Neural Language Models" working copy | dimensionless exponents; parameters, tokens, PF-days | primary scaling-law reference | source named; upstream URL/DOI and extraction notes still needed |
| GPT-3 scaling table | `Data/GPT3_Scaling_Laws.csv` | topic-local GPT-style scaling table | parameters, test loss, FLOPs | independent log-log fit diagnostic | working copy; table provenance not archival |
| Model architecture metadata | `Data/03_Research/deepseek_moe_data.json` | topic-local model metadata package | total/active parameters, context window, tokens | sparse-vs-dense active-fraction diagnostic | mixed: some entries are public-model metadata, some estimated/proprietary |

## Secondary Inputs

| Dataset | Local path | Role | Limitation |
| :-- | :-- | :-- | :-- |
| Foundation notes | `Data/00_Foundation/foundation_basics.txt` | background notes for foundation-model concepts | not a numeric verifier input |
| Tiny Shakespeare | `Data/03_Research/tiny_shakespeare.txt` | possible toy language-model input | not used by the primary verifier |

## Hash Policy

The primary verifier records SHA-256 hashes for all primary inputs in
`Result/artifacts/0_24_artificial_intelligence_verification.json`.

## Next Provenance Work

- Add upstream URLs/DOIs/arXiv IDs and retrieval dates for the scaling-law source.
- Split public, estimated, and proprietary model metadata into separate tables.
- Move any raw external downloads to `docs/data/external/...`; keep derived
  topic-specific tables under `docs/topics/0.24_Artificial_Intelligence/Data/...`.
