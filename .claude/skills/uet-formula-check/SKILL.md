---
name: uet-formula-check
description: Review a UET equation or code path - units and mass dimensions, where each constant comes from, the nearest known theory, redundant parameters, and whether its tests are real physics tests. Use to audit a formula, to read the Theory Card against code, or to decide whether a legacy result can be promoted to a claim.
---

# Formula and derivation check (STANDARD §3, §6, §8; For Work 17 for the audit table format)

## Checks
1. **Source**: is it derived from the parent action (`core/THEORY_CARD.md`, `theory_card.json`) or posited? Posited terms are L0 until derived or tested.
2. **Units**: a mass-dimension table for every new symbol, and a test that checks dimensional consistency. Natural units must say so; SI needs explicit conversions.
3. **Constants**: each number traced to a cited source, a fit (then it cannot validate the same claim) or an AI choice (label it).
4. **Nearest known theory** with the map of variables, and the list of real differences. "None yet" is an allowed answer.
5. **Redundancy**: can a field redefinition or unit change absorb the parameter (as with ε in the parent action)? Then do not give it physical meaning.
6. **Well-posedness** for PDEs used to compute anything.
7. **Tests**: are the tests on this path `@pytest.mark.physics` and of a kind STANDARD §6 counts? Known limits must go through the general code path. A test that compares a function with itself, or a limit reached by an `if` branch, is a tautology.

## Legacy results (§8)
Old artifacts, gates and contracts are `LEGACY_UNREVIEWED` and must not be edited. A legacy result becomes a claim only by meeting the level's conditions now (usually: write a physics test for it). Changing a hash-locked shared script makes many contracts STALE; that is a separate wave the owner approves.

## Output
Findings per item with file:line, a verdict (used correctly / needs correction / conflicts / domain-limited), and a proposed next wave. Edit nothing unless asked.
