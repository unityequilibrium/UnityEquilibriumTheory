# Verification Spec

- Primary command:
  - `python docs/topics/0.1_Galaxy_Rotation_Problem/Code/03_Research/Research_Galaxy_Rotation.py`
- Inputs:
  - `Data/03_Research/sparc_data.json`
- Fixed threshold:
  - Internal pass threshold is `< 15%` error in the current script
- Reported metrics:
  - Mean absolute percentage error
  - Internal pass rate over processed entries
- Artifact target:
  - `Result/artifacts/galaxy_rotation_validation.json`
- Interpretation:
  - Treat output as an internal benchmark artifact, not external confirmation
