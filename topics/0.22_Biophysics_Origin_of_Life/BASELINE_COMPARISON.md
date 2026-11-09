# Baseline Comparison: 0.22 Biophysics & Origin of Life

## Current baseline

The current baseline is the seeded synthetic positive-control matrix defined in VERIFICATION_SPEC.md. It is a mechanics and code-path baseline, not a clinical, EEG, TCGA, or prebiotic benchmark.

## Metrics

- synthetic gene count and sample count;
- variance and stability for expected positive controls;
- fixed seed and threshold;
- input identity and artifact hash;
- future lane-specific metrics only after a separate source-locked gate exists.

## Acceptance boundary

The current artifact may support only an internal benchmark comparison and produces WARN. A future source-backed comparison must record source identity, preprocessing, units, baseline implementation, threshold, timestamp, environment, and hashes before it is considered evidence for a stronger claim.

## Claim boundary

This baseline does not support wording such as solved, exact, clinical, real TCGA validation, external replication, or production grade.

## Protein-folding lane baseline

The protein lane uses a separate finite-model baseline:

| Component | Definition | Role |
| :-- | :-- | :-- |
| Oracle | Exhaustive self-avoiding walks for `HHPPHHPHHPH` with the first step fixed | Exact optimum within the declared 2-D HP model |
| Unbiased comparator | Uniform random valid next move; seeds 22010, 22011, 22012; 1,000 attempts per seed | Baseline search behavior |
| Centroid-biased comparator | Historical H-centroid preference with probability 0.8 and 0.2 random exploration | Repaired legacy heuristic behavior |
| Metrics | Best energy, optimum gap, optimum hit rate, mean energy, histogram, valid/invalid folds | Internal algorithmic comparison |

The fixed acceptance boundary is: exhaustive configuration count must be positive; model contact checks must pass; stochastic optimum gaps must be non-negative relative to the oracle; and a replay with the same input and seeds must match exactly. These thresholds validate the mechanics contract, not biological accuracy.


## Protein-folding dynamics baseline contract

Wave 0 defines the baseline but produces no molecular-dynamics result.

| Component | Contract | Current status |
| :-- | :-- | :-- |
| Source cohort | 12 small single-domain proteins; 8 development and 4 protein-level holdout | Blocked; zero rows frozen |
| Structure source | PDB chain/construct identity; CASP only as future holdout/reference | Source target only |
| Kinetic source | KineticDB, PFD, and PFDB source records with rate, temperature, pH, buffer, denaturant, and method fields | Source target only |
| Standard baseline | OpenMM, AMBER ff14SB, explicit TIP3P, explicit ions | Runtime not available/hashed |
| Analysis | MDTraj; openmmtools only after version gate | Runtime not available/hashed |
| UET comparison | H0 standard MD, H1 readout-only, H2 coupled candidate after formula closure | H1/H2 not run |
| Acceptance | Source hashes, exact split, runtime smoke tests, convergence, endpoint/pathway/kinetic metrics, uncertainty, and ablations | Preflight blocked |

No source row may be replaced by the synthetic HP input. AlphaFold is an
endpoint/reference comparison only and is not a dynamic baseline.
