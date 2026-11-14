# Limitations

- The current primary verifier supports only a sphere-plate Casimir force benchmark, not a general vacuum-energy theory.
- The dataset is a topic-local working copy with a real source label; upstream URL/DOI capture and transcription audit are still incomplete.
- The engine's `calculate_casimir_force` method implements the ideal parallel-plate pressure law but names it as force. This must not be used as a geometry-general force claim.
- The primary verifier uses `R=200 um` while the working dataset declares `R=196 um`; this is acceptable only as a tracked benchmark assumption until a sensitivity artifact is added.
- The finite-conductivity correction is clipped to `[0.8, 1.0]`, which may hide short-distance model failure.
- `calculate_cosmological_constant` currently returns an observed-like dark-energy density anchor. It is not derived from the Casimir dataset and must not be described as solving the cosmological-constant problem.
- Algebraic outputs such as `w=-1` and `Omega_total=1` are diagnostics unless a cosmological dataset and baseline comparison are added.
- Downstream topics must inherit these limitations when using `0.12` as part of the core theory map.
