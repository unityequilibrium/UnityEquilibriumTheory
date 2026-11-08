# Core Equation Research Instructions

These instructions apply under `docs/core/`. They add to the root [`AGENTS.md`](../../AGENTS.md) and [`docs/STANDARD.md`](../STANDARD.md), which control.

## Before changing an equation or operator

1. Read `docs/core/THEORY_CARD.md` once it exists (W3). It holds the core equations, the nearest known theory class, the redundant parameters and the planned predictions.
2. Change the equation's code under `02_equations/` and the card together. Bump the card `version` whenever a core equation changes.
3. Add or update physics tests under `05_tests/physics/` marked `@pytest.mark.physics`, following §6 of the standard:
   - a **sympy derivation check** that the implemented equations follow from the declared action, at 20 or more random points with relative difference below 1e-10
   - a **dimension table** with a test
   - **known limits through the general code path**. A special-case branch such as `if epsilon_nc == 0: return gr_residual(...)` does not count.
   - a **convergence order** check for numerical solvers
4. Check for parameter redundancy, i.e. whether a field redefinition absorbs the parameter, before giving it a physical meaning.
   Example: ε in the parent action is largely absorbed by rescaling φ.

## Symbol rules (unchanged)

- `C` is a lane-specific system-state coordinate. It is not universally mass.
- `Phi` is an effective response variable. It is not a metric, an ether or a substance.
- `Pi` is `∂t Phi`.
- `R` / `I_trace` is a derived history observable with no feedback in the current mode.
- Mass, density, charge, stress-energy and physical energy need explicit lane mappings. Normalized or natural-unit quantities are not SI.
- A constitutive ansatz, calibration or benchmark anchor is never a first-principles derivation.

## Layout

- `00_governance`: navigation and registries.
- `01_contracts`: specifications.
- `02_equations`: canonical implementations.
- `03_lanes`: lane models.
- `04_proofs` and `05_tests`: proofs and tests. New evidence-grade tests go in `05_tests/physics/`.
- `06_data`: inputs.
- `07_artifacts`: generated outputs.
- `08_history`: logs and notes.
- `99_review`: quarantine.

Use `docs/core/core_paths.py` as the path authority. Keep `__init__.py`, `AGENTS.md`, `README.md` and `CORE_FILE_INDEX.md` at the root.

## Legacy and diagnostics

- Do not delete or rewrite legacy engines, gates or artifacts. Their provenance label is `LEGACY_UNREVIEWED`.
- The foundation gates F0–F8, the main-theory wave gates, the aggregate, reconcile v4, migration and scientific-link audits are **diagnostic tools**. They do not decide a claim's level.
- Re-running them is optional. Never hand-edit generated output. Never hide a failed result through clipping, fallback parameters or renamed statuses.
- The historical `docs/core/README.md` is not a claim source.

## Wave close

Run `pytest -m physics docs/core/05_tests/physics` and the three `docs/scripts/standard/` checks.
Then add a log entry of 6 lines or fewer to `docs/core/UPDATE_LOG.md` (template in §9 of the standard) and a ledger entry, and make one scoped commit.
