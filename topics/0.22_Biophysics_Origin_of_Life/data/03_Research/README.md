# Data: 0.22 Biophysics & Origin of Life

This directory contains source-referenced context and explicitly labeled local placeholders. It is not an archival release of EEG, omics, clinical, protein, or prebiotic measurements.

## Active data roles

- 03_Research/source_lock_manifest.json: source and role manifest.
- 03_Research/protein_folding_hp_benchmark.json: synthetic topic-local HP model definition used by the deterministic protein lane; no external protein data.
- 03_Research/chb_mit_reference.json: source-labeled CHB-MIT reference metadata.
- 03_Research/chb01_summary.txt: local summary, not raw EDF.
- 03_Research/seizure_phase_data.json: derived discussion summary, not raw windows.
- Bonn_EEG/Z.txt and Bonn_EEG/S.txt: synthetic mechanics-test placeholders, not authenticated Bonn files.
- protein_folding_hp_benchmark.json is dimensionless model input; its -1 contact term is a benchmark anchor, not SI energy or protein free energy.

The protein-folding dynamics source/runtime package is declared at the topic root in DYNAMICS_DATA_MANIFEST.json and DYNAMICS_RUNTIME_MANIFEST.json. It currently contains source targets only; no PDB, KineticDB, PFD, PFDB, or CASP raw package is present.

Downloaders and duplicate paths are under data/legacy/ and are excluded from current evidence.
