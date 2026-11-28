---
name: uet-wave
description: Run one UET research wave under Research Standard v2 - one question, one new derivation or number, physics tests, a FORMAL contract, a result and an L1 claim, one commit. Use when asked to continue core research, derive something from the parent action, or answer a theory question with mathematics.
---

# One research wave (STANDARD §9)

A wave is one question, at least one new number, derivation or FAILED result, a log entry of 6 lines or fewer, and one commit.
External data is not part of a wave: that is `uet-test-card`.

## Before you start
1. `git status`. Leave changes you did not make alone. Branch `claude/research/<task>` from the branch the work builds on.
2. Read `core/AUTHOR_PROPOSITION.md` if the question touches what UET means. Check `docs/standard/claims.json` for claims that already cover it.
3. Write the question down in one sentence. Name the nearest known theory before deriving (UET is a synthesis theory: reusing known physics is expected, not a weakness). Short form of STANDARD §16: in the module docstring name the field's established model with a source (not just a label), say whether the field already answers the question (then the wave shows that UET reproduces it), and say who chose any mapping from UET variables to a real system (author or AI).

## Do the work
1. **Code**: one module under `core/03_lanes/<lane>/` (or the topic's `Code/`). Its docstring states the question, the derivation steps marked `[AI derivation]`, the nearest known theory, what the action does NOT fix, and "Not UET-distinct" when true.
2. **Physics tests**: `core/05_tests/physics/test_<name>.py` with `pytestmark = pytest.mark.physics`. Only these count (§6):
   - derivation check against the code at 20 or more random points (rel < 1e-10);
   - known limit through the general code path (never an `if param == 0: return reference` branch);
   - convergence order on at least 3 grids;
   - conservation or identity that holds because of physics;
   - independent second route (for example a Lorentz boost against a direct integral).
   Status-string, hash or file-exists assertions are bookkeeping and prove nothing.
3. **FORMAL contract**:
   `.venv/Scripts/python.exe docs/scripts/standard/new_formal_contract.py --contract-id <id>_formal --question "..." --quantity "..." --formula-id <id> --code <module> --test <test> --unit natural --out core/00_governance/calculation_contracts/<id>_formal.json`
   Then check the file is LF (`git diff --check`). Contracts lock sha256 of code: commit code, test and contract together, and regenerate the contract if the code changes.
4. Commit the code first (`research(core): <what was found>`). Its sha is the result's `producer.commit`.
5. **Result** `docs/standard/results/R_<ID>.json`: schema `uet-result-v2`, `level` `L1_CONSISTENT`, `outcome` `PASS`, `numbers` as `{name, value, uncertainty, unit}` where `value` is a number or a string (never a boolean), `producer` {script: the test file, commit}, `note` with scope, approximations and nearest theory.
6. **Claim** in `claims.json`: `{claim_id, statement, level: "L1_CONSISTENT", evidence: [result_id], note}`. Insert next to related claims; keep the file's indentation.
7. Update the counts wherever they appear: `README.md` badge and registry line, `README.th.md`, `core/CORE_MAP.md`. Add the 6-line entry to `core/UPDATE_LOG.md` (or the topic's `UPDATE_LOG.md`).
8. Finish with `uet-ship` (ledger, checks, commit `research(standard): register <claim> at L1`).

## Stop and ask the owner when
- the next step needs data from outside the repo (downloads need permission);
- a choice is the author's: what a symbol means, which interpretation to adopt, approving anything;
- the work would change a hash-locked shared script or create a new audit script or gate.
Do not ask the author for parameter values or physics answers: turn those into the next wave.

## Report
Say in plain words what is now derived, what is not, the nearest known theory, and what is an AI choice.
