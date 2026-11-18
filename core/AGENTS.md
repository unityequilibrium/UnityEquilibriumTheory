# Core Equation Research Instructions

These instructions apply under `core/`. They add to the root [`AGENTS.md`](../AGENTS.md) and [`docs/STANDARD.md`](../docs/STANDARD.md), which control.

## Before changing an equation or operator

0. Read [`CORE_MAP.md`](CORE_MAP.md) first. It says which files are the live equations for each layer, which are legacy, and what is still open.
   Check the file's label in [`CORE_ALIGNMENT_REGISTER.tsv`](CORE_ALIGNMENT_REGISTER.tsv): A use, B develop, C keep as history, D structure.
   Do not build new work on a C file.
1. Read [`THEORY_CARD.md`](THEORY_CARD.md). It holds the layer 1 equations, the nearest known theory class, the redundant parameters and the planned predictions.
2. Change the equation's code and the card together. Bump the card `version` whenever a core equation changes.
3. Add or update physics tests under `05_tests/physics/` marked `@pytest.mark.physics`, following §6 of the standard:
   - a **sympy derivation check** that the implemented equations follow from the declared action, at 20 or more random points with relative difference below 1e-10
   - a **dimension table** with a test
   - **known limits through the general code path**. A special-case branch such as `if epsilon_nc == 0: return gr_residual(...)` does not count.
   - a **convergence order** check for numerical solvers
   - no `pytest.skip` inside a physics test: the CI runner treats a skipped physics test as incomplete. Choose inputs deterministically instead.
4. Check for parameter redundancy, i.e. whether a field redefinition absorbs the parameter, before giving it a physical meaning.
   Example: ε in the parent action is largely absorbed by rescaling φ.
5. New code that a Test Card or claim uses needs a calculation contract under `00_governance/calculation_contracts/` (root AGENTS.md §8).
   Add the new file to `CORE_ALIGNMENT_REGISTER.tsv` with its label.

## Symbol rules

- `C` is a lane-specific system-state coordinate of the legacy equation set. It is not universally mass. The layer 1 action uses φ and χ instead.
- `Phi` (φ) is an effective response variable. It is not a metric, an ether or a substance.
- `Pi` is `∂t Phi`.
- `R` / `I_trace` is a derived history observable with no feedback in the current mode.
- Mass, density, charge, stress-energy and physical energy need explicit lane mappings. Normalized or natural-unit quantities are not SI.
- A constitutive ansatz, calibration or benchmark anchor is never a first-principles derivation.

## Layout

See [`README.md`](README.md) for what each folder holds.
Use `core/core_paths.py` as the path authority. Keep `__init__.py`, `AGENTS.md`, `README.md` and `CORE_FILE_INDEX.md` at the root.
`CORE_FILE_INDEX.md` is generated legacy output; the per-file index is now `CORE_ALIGNMENT_REGISTER.tsv`.

## Legacy and diagnostics

- Do not delete or rewrite legacy engines, gates or artifacts. Their provenance label is `LEGACY_UNREVIEWED`.
- Archived failing tests live in `08_history/archived_tests/` (core) and in each topic's `Archive/tests/`. They are not evidence and are not run.
- The foundation gates F0–F8, the main-theory wave gates, the aggregate, reconcile v4, migration and scientific-link audits are **diagnostic tools**. They do not decide a claim's level.
- Re-running them is optional. Never hand-edit generated output. Never hide a failed result through clipping, fallback parameters or renamed statuses.
- The old core README is kept at `08_history/README_LEGACY_2026-11-14.md`. It is not a claim source.

## Wave close

Run `pytest -m physics core/05_tests/physics` and the three `docs/scripts/standard/` checks.
Then add a log entry of 6 lines or fewer to `core/UPDATE_LOG.md` (template in §9 of the standard) and a ledger entry, and make one scoped commit.
