# Verification Spec: 0.22 Biophysics & Origin of Life

- Primary command:
  - `.venv\Scripts\python.exe docs\topics\0.22_Biophysics_Origin_of_Life\Code\03_Research\Research_Biomarker_Identification.py`
- Inputs:
  - `data/03_Research/chb_mit_reference.json`
  - `data/03_Research/source_lock_manifest.json`
  - `data/03_Research/chb01_summary.txt`
  - `data/03_Research/seizure_phase_data.json`
  - `data/Bonn_EEG/Z.txt`
  - `data/Bonn_EEG/S.txt`
  - `docs/data/external/biophysics/eeg/chb_mit/source_record.json`
  - `docs/data/external/biophysics/eeg/bonn/source_record.json`
  - `docs/data/external/biophysics/omics/tcga/source_record.json`
- Baseline:
  - Seeded synthetic positive-control matrix, not a clinical or external benchmark.
- Reported metrics:
  - synthetic gene/sample count, threshold, seed, candidates, input hashes, and resolution status.
- Fixed threshold:
  - stability below 0.5 flags a synthetic candidate.
  - expected positive controls are GENE_007 and GENE_023.
  - successful execution remains WARN because the matrix is synthetic.
- Artifact target:
  - `Result/artifacts/0_22_biophysics_origin_of_life_verification.json`
- Interpretation:
  - Code-path diagnostic only; no clinical, real omics, EEG, origin-of-life, or external replication claim.

Evidence class: C internal benchmark.
Data class: synthetic.
No claim class above C is allowed from this artifact.

## Protein-folding lane command

- Command:
  - `.venv\Scripts\python.exe docs\topics\0.22_Biophysics_Origin_of_Life\Code\03_Research\Research_Protein_Folding_HP_Benchmark.py`
- Input:
  - `data/03_Research/protein_folding_hp_benchmark.json`
- Input class:
  - `synthetic`
- Formula:
  - `T22-010`, finite 2-D HP contact energy in dimensionless model units.
- Search contract:
  - sequence `HHPPHHPHHPH`;
  - square integer lattice;
  - residue 0 fixed at `[0,0]`, residue 1 fixed at `[1,0]`;
  - seeds `22010`, `22011`, `22012`;
  - 1,000 attempts per seed;
  - unbiased random and centroid-biased methods;
  - centroid bias probability `0.8`.
- Exact reference:
  - exhaustive canonical self-avoiding walks;
  - positive configuration count;
  - minimum model energy and one optimal coordinate set;
  - non-bonded H-H contacts only; covalent neighbors excluded.


## Protein-folding dynamics Wave-0 preflight

- Command:
  - .venv\Scripts\python.exe docs\topics\0.22_Biophysics_Origin_of_Life\Code\03_Research\Research_Protein_Folding_Dynamics_Gate.py
- Inputs:
  - DYNAMICS_RESEARCH_SPEC.md
  - DYNAMICS_DATA_MANIFEST.json
  - DYNAMICS_RUNTIME_MANIFEST.json
- Artifact:
  - Result/artifacts/0_22_protein_folding_dynamics_gate.json
- Role:
  - source and runtime preflight only; it does not download sources, run MD,
    create trajectories, or generate a folding result.
- Required source gate:
  - 12 source-locked small single-domain proteins, split by protein into 8
    development and 4 holdout entries.
- Required runtime gate:
  - pinned OpenMM, MDTraj, and openmmtools availability;
  - hashed AMBER ff14SB/TIP3P/ion/topology assets;
  - passing CPU one-step and trajectory round-trip smoke tests.
- Current result:
  - BLOCKED for the dynamics lane because the source cohort and runtime
    assets are not present in the repository.
  - umbrella status remains Draft / Tier B / WARN.
- Claim boundary:
  - no real protein folding, biological free-energy, PDB/CASP validation,
    AlphaFold replication, cellular mechanism confirmation, or external
    replication is allowed from this gate.
