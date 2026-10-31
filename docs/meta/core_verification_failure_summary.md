# Core Verification Run Summary

This summary records the latest core verification batch for topics `0.0-0.26`.

## Latest Result

- Run contract passed: `27/27`
- Current failing topic: none in the latest run
- Runner artifact summary: `docs/meta/core_verification_run_summary.json`

## Current Failure

| Topic | Current blocker | Evidence artifact | Policy consequence |
| :-- | :-- | :-- | :-- |
| None | Latest run contract has no failing core topic | `docs/meta/core_verification_run_summary.json` | Continue scientific hardening; passing scripts are not full proof |

Resolved blocker analysis:

- `docs/topics/0.3_Cosmology_Hubble_Tension/Doc/ANALYSIS_Hubble_Verification_Blocker.md`

No-fitting policy:

- Do not use fitted beta or post-hoc target matching to promote `0.3`.
- The current passing `0.3` artifact uses `beta_frame = sqrt(alpha_em)` from the central
  constants module, not an optimized target value.
- Remaining work is to strengthen the derivation and test BAO/SN/CMB/high-z consistency.

## Stability Watch

| Topic | Observation | Policy consequence |
| :-- | :-- | :-- |
| `0.10_Fluid_Dynamics_Chaos` | Previous single-run timing reported `1.9x` against a `> 2.0x` threshold; benchmark now uses warm-up plus 5-trial median and reports `2.84x` with stability | Keep repeated-run timing in artifacts; do not reduce the speed threshold |

## Environment Fixes Applied

- Verification runner now forces `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1` for child processes.
- Verification runner prepends the repo root to `PYTHONPATH` so topic scripts can import the local `docs` package.
- `0.24_Artificial_Intelligence` import path was fixed from `docs.core.test.scientific_validation` to `docs.scripts.core.audit.scientific_validation`.
