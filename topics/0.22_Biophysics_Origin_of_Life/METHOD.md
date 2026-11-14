# Method: 0.22 Biophysics & Origin of Life

## Method boundary

The topic is an umbrella research workspace. It does not treat living systems, neural signals, omics, proteins, protocells, and clinical simulations as one dataset or one claim. Each lane is listed in RESEARCH_REGISTRY.json and must obtain its own source, formula, baseline, and artifact before its claim ceiling can change.

## Active evidence-producing paths

The primary umbrella verifier is Code/03_Research/Research_Biomarker_Identification.py. The protein_folding lane also has a separate deterministic finite-model verifier at Code/03_Research/Research_Protein_Folding_HP_Benchmark.py. Each path emits its own artifact and claim boundary.

All other historical engines, proof-named scripts, simulations, competitors, and visualizations are catalogued in the registry and stored under the legacy boundary until they have a dedicated gate.

## Lane method map

| Lane | Model/data method | Observable role | Current status |
| :-- | :-- | :-- | :-- |
| Homeostasis | Normalized entropy/information proxy | Diagnostic model score | Exploratory; environment ledger open |
| Origin of life | Random/structured field and protocell proxy simulations | Simulation behavior only | Exploratory; no emergent chemistry |
| EEG/neural | Source-referenced summaries and synthetic mechanics samples | Future neural diagnostic features | No raw-window gate |
| Synthetic biomarker | Seeded positive-control expression matrix | Stability diagnostic | Current class-C benchmark |
| TCGA/omics | Historical mock expression matrix scripts | Metric-shape demonstration | No real matrix |
| Protein folding | Deterministic finite 2-D HP lattice; exhaustive oracle plus seeded random and centroid-biased search | Model energy, optimum gap, hit rate, energy histogram | Class-C internal model benchmark; no biological correspondence |
| Protein-folding dynamics | Wave-0 source/runtime contract for future atomistic, co-translational, and chaperone lanes | Source readiness, runtime readiness, cohort split, and smoke-test status | Class-B design/preflight; no atomistic result |
| Immune/clinical | Virtual-subject normalized scores | Exploratory scenario only | No clinical evidence |

## Protein-folding dynamics method contract

The dynamics lane begins with source and runtime preflight. It targets a
source-locked cohort of 12 small single-domain proteins, split by protein into
8 development and 4 holdout entries. The first atomistic baseline is standard
OpenMM with AMBER ff14SB, explicit TIP3P water, and explicit ions after exact
versions and asset hashes are frozen. MDTraj is the analysis layer and
openmmtools is a declared enhanced-sampling dependency, not an implicit
fallback.

The UET lane is readout-only first. Atomistic coordinates are mapped to
lane-specific contact, secondary-structure, compactness, native-basin,
solvent-exposure, and contact-order coordinates. A coupled UET force is
blocked until the formula audit closes ontology, units, parameter provenance,
standard-physics correspondence, and observable mapping. The sequence is
intrinsic folding -> co-translational folding -> chaperone/non-equilibrium
channels.

The preflight script does not download sources, run MD, create trajectories, or
generate a folding result. A missing runtime or cohort is a named blocker, not
a reason to substitute the synthetic HP input.

## Variable and unit framing

- Omega, stability, coherence, complexity, diversity, and synchrony values are dimensionless or normalized proxies unless a source-specific unit contract says otherwise.
- Proxy normalization is not a conversion to SI energy, entropy, temperature, or clinical risk.
- Sampling rates are in Hz and time windows in seconds only where the source record explicitly declares them.
- Expression units must be declared by assay before any omics metric is interpreted.
- Parameters are topic/model parameters unless an external source, derivation, or calibration artifact is recorded.
- HP coordinates are integer lattice positions; HP energy is dimensionless model units and the -1 contact term is a benchmark anchor, not SI energy or protein free energy.

## Dependencies

Homeostasis and negative-entropy language depends on Topic 0.13_Thermodynamic_Bridge. Until its environment and units boundary is closed, this topic may use only normalized exploratory language.

## Excluded from current method

- a complete origin-of-life mechanism;
- clinical biomarker or treatment effectiveness conclusions;
- EEG seizure prediction from raw clinical windows;
- real TCGA/omics analysis;
- external replication;
- formal proof of life or biological efficacy.
- real protein structure prediction or free-energy inference;
- AlphaFold replication, PDB/CASP performance, or experimental validation.
- Atomistic protein-folding results before the source/runtime gate closes.
- Cellular folding mechanism confirmation from a source-referenced design.

## Reproducibility contract

The umbrella command, its nine context inputs, and the separate protein-folding command, synthetic input, fixed seeds, thresholds, artifact path, and interpretation boundary are defined in VERIFICATION_SPEC.md. Each lane must keep its own specification and artifact rather than extending another lane implicitly.
