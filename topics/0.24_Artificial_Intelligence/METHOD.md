# Method

## Problem Target

This topic tests whether selected AI scaling and architecture-efficiency
quantities can be represented in a UET-style information framework. The current
hardening pass targets measurable scaling and sparsity diagnostics first.

## Evidence Lanes

| Lane | Files | Current role |
| :-- | :-- | :-- |
| Scaling-law benchmark | `scaling_laws.json`, `GPT3_Scaling_Laws.csv`, `Research_AI_Scaling_Audit.py` | primary verifier lane |
| Sparse architecture diagnostic | `deepseek_moe_data.json`, `UET_AI_Core.py`, `Research_AI_Scaling_Audit.py` | primary verifier lane |
| Entropy-learning engine | `UET_AI_Core.py` | implemented but not benchmark-validated |
| AI detective/cross-topic reasoning | `Research_AI_Detective_V2.py` | excluded from primary claim; depends on 0.1 galaxy data |
| Alignment/ethics simulation | `Research_Alignment_Equilibrium.py` | future exploratory lane |
| Consciousness/developmental AI | `Research_Consciousness.py`, `Code/05_Developmental_AI/` | future exploratory lane |

## Variables

| Symbol / field | Meaning | Unit |
| :-- | :-- | :-- |
| `L` | test-loss proxy | dimensionless |
| `N` | parameter count | count |
| `D` | training tokens | count |
| `C` | compute | PF-days or FLOP-derived proxy |
| `alpha_N`, `alpha_D`, `alpha_C` | scaling exponents | dimensionless |
| `kappa_macro` | current UET macro proxy used for comparison | dimensionless |
| `active_fraction` | active parameters divided by total parameters | dimensionless |

## Procedure

1. Load topic-local scaling-law constants and model metadata.
2. Fit a simple log-log exponent from `GPT3_Scaling_Laws.csv`.
3. Compare the fitted exponent with stored `alpha_N`.
4. Compare MoE active fractions with dense active fractions.
5. Check whether the current `kappa_macro=0.1` proxy is close enough to `alpha_N`
   to support a constant-identification claim.
6. Write a machine-readable artifact with hashes, metrics, thresholds, blockers,
   and limitations.

## Domain of Validity

The current method applies only to the topic-local scaling/sparsity benchmark
package. It is not a proof of AI alignment, ethics, consciousness, or a general
physical law of intelligence.

## Dependency Policy

`Research_AI_Detective_V2.py` depends on topic `0.1` galaxy data and must not be
used as the primary evidence for topic `0.24` until it is explicitly modeled as a
cross-topic dependency artifact.
