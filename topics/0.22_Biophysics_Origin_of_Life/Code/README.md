# Code: 0.22 Biophysics & Origin of Life

## Active code

The primary umbrella evidence-producing script is `03_Research/Research_Biomarker_Identification.py`. The protein-folding lane has a separate evidence-producing verifier, `03_Research/Research_Protein_Folding_HP_Benchmark.py`, which emits a finite 2-D HP artifact.

Run the protein lane with:

    .venv\Scripts\python.exe docs\topics\0.22_Biophysics_Origin_of_Life\Code\03_Research\Research_Protein_Folding_HP_Benchmark.py

The protein artifact is `claim_class=C` and `data_class=synthetic` for an internal algorithmic benchmark only.

Run the dynamics preflight with:

    .venv\Scripts\python.exe docs\topics\0.22_Biophysics_Origin_of_Life\Code\03_Research\Research_Protein_Folding_Dynamics_Gate.py

It writes a BLOCKED or PASS source/runtime gate artifact and never downloads data or runs molecular dynamics. The preflight must remain aligned with `VERIFICATION_SPEC.md`, `RESEARCH_REGISTRY.json`, `FORMULA_AUDIT.md`, and the lane input manifest.

## Legacy code boundary

Historical engines, proof-named scripts, neural/cancer/clinical/protocell/protein experiments, competitor code, visualization code, and stale output are preserved under Code/Legacy/. They are not current evidence and are not included in the topic status decision.

Any script returning PASS from synthetic or virtual data must remain bounded to its declared model or diagnostic role. A passing HP artifact does not establish real protein folding, protein free energy, AlphaFold replication, or external validation.

## Path policy

- Use repository-relative paths derived from Path(__file__) or the shared path manager.
- Do not use workstation-specific absolute paths.
- Do not write a convenience pattern into a file whose name implies an upstream dataset.
- New evidence-producing scripts must write a machine-readable artifact under Result/artifacts/.
