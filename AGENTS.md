# UET Agent Operating Guide

This file is the entrypoint for every AI agent and collaborator working in this repository.
No agent is the lead. Any agent must be able to pick up the work from the records in this repository alone,
without trusting what another agent says about it. It is deliberately short.

**The controlling research standard is [`docs/STANDARD.md`](docs/STANDARD.md)** (Research Standard v2, approved by the author on 2026-11-08).
When this guide and the standard disagree, the standard wins. The exceptions are the boundary, privacy and publication rules below, which stay in force.
`topics/For Work/` must not be edited (the owner moved it there from `docs/topics/For Work/` on 2026-11-19; file contents are unchanged). Its operational standards (topic structure, code READMEs, data, references,
results, formula audit, papers, visualization, templates and calculation contracts) are still in force under §15 of the standard.
Its old status vocabularies and workflow ladders are replaced.

## 1. What the repository is

- `core/` holds the UET core equations, tests and artifacts.
  Core-specific rules are in [`core/AGENTS.md`](core/AGENTS.md).
- `topics/` holds the numbered research topics.
- `topics/For Work/` holds the operational standards. Only one tracked file remains under `docs/topics/`:
  `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_fig1.png` (see `docs/meta/TOPIC13_LEFTOVER_RAW_FIGURE_2026-11-19.md`).
- In frozen records, `docs/core/<path>` means `core/<path>` and `docs/topics/<topic>/` means `topics/<topic>/`.
  Do not rewrite old paths, hashes or contracts just to update the path text.
- `docs/standard/` holds the machine-checked records: claims, Test Cards, results and the data manifest.
- `WORK_LEDGER/` is the repository-wide daily work history. Topic `UPDATE_LOG.md` files record research waves.
- Generated JSON under `07_artifacts/`, `Result/` and `_Logs/` is output. It is not where narrative decisions get made.
- Claude's research skills live in `.claude/skills/` (index: `.claude/skills/README.md`). They follow `docs/STANDARD.md` and replace the older Codex `uet-*` skills.
- The local interpreter is `.venv/Scripts/python.exe`. Dependencies are pinned in `.github/requirements-research.txt`.

## 2. Harness and Superapp boundary (always in force)

- On 2026-11-03 the owner moved `uet_history` (history and book work) into the separate Superapp project. `thailand_proposals` moved to its own repository.
  References to those paths are historical. Do not recreate them.
- Work done in `uet_harness` stays inside Harness. Do not inspect, edit, run commands in, change settings for, commit to, or push the separate `uet-superapp` project.
- Superapp may read Harness as a downstream client. That does not make it a source of truth for Harness, and it does not authorize syncing into it.
- Keep raw and private material local: ignored `raw/` paths and `1_raw/`-style sources. Downstream access is not permission to publish private material.

## 3. How to do research (summary of docs/STANDARD.md)

0. **Author intent first:** read [`core/AUTHOR_PROPOSITION.md`](core/AUTHOR_PROPOSITION.md) before you interpret UET.
   It replaces earlier AI reconstructions of the author's meaning (for example "open universe" and "learning").
   Label your own interpretations as AI interpretations.
1. **Evidence levels** (§1): `L0_SPECULATIVE`, `L1_CONSISTENT`, `L2_CONFRONTED`, `L3_REPLICATED`, `FAILED`.
   Do not invent any other status value in new records.
2. **Zones** (§2): sandbox work is free. Claims must be registered in `docs/standard/claims.json`.
3. **Theory Card** (§3): name the nearest known theory class, list what differs from it, and record redundant parameters.
4. **Test Card** (§4): commit the numeric pass and fail criteria and get author approval *before* running any external comparison.
   An agent must never approve its own card or promote a claim to L2 or higher.
5. **Physics tests** (§6): mark them `@pytest.mark.physics`. Only derivation checks, known limits that go through the general code path, convergence tests, physical identities and external comparisons count.
   Assertions on status strings or hashes are bookkeeping only.
6. **Data** (§7): hash-lock only raw external data, in `docs/standard/data_manifest.json`.
   Never validate a claim with data that was used to fit or calibrate it.
7. **Negative results are results.** Record `FAILED` plainly. Do not rename a failure as a pass, split the scope after seeing the outcome, or add a branch to escape a comparator.
8. **Wave format** (§9): each wave is one question, at least one new number or derivation, a log entry of 6 lines or fewer, and one commit.
   Governance work should stay at roughly 20% of effort or less. New gates or audit scripts need author approval.
9. **Author intent versus AI proposals:** say clearly which examples or materials the AI chose. They are not requirements of the theory.
10. **Research design** (§16, approved 2026-11-27, trial on the next 3 cards): map the field's established models first, write a one-page question brief before every Test Card (who chose the mapping, the field's rival model, a discrimination forecast, data shape, what each outcome would mean), and state the cause of each FAIL or INCONCLUSIVE in the Result note. No new status or gate.

## 4. Claim wording

- Use conservative words: `hypothesis`, `model`, `derived relation`, `internally consistent (L1)`, `confronted with data (L2)`, `externally replicated (L3)`.
- `solved`, `proved`, `verified`, `exact`, `predicts` and `production grade` are restricted.
  "Predicts" is allowed only for a `BLIND_PREDICTION` Test Card.
- Do not upgrade a fit into a prediction, an internal rerun into external validation, a normalized quantity into SI, or a lane mapping into a universal identity (for example, C is not universally mass).
- Mark inferences as inferences. Answer from local evidence and cite the controlling file.

## 5. Legacy work

- Earlier gates, artifacts, calculation contracts and update logs are preserved unchanged. Their provenance label is `LEGACY_UNREVIEWED`.
- Old status vocabularies map to the v2 levels as set out in §13 of the standard.
- Old audit scripts (inventory, compatibility, aggregate, reconcile, migration, scientific links) may still be run as diagnostics. They do not control status.
- `docs/scripts/audit/audit_calculation_completeness.py --check` is still part of CI for calculation contracts.

## 6. Git workflow

- Run `git status` before editing. Preserve unrelated user changes and stage only the files that belong to the current wave.
- Use one short-lived branch per coherent unit: `<agent>/<area>/<task>` (for example `claude/repo/...` or `codex/research/...`), where area is `research`, `repo`, `services`, `book`, `history` or `policy` (enforced by `pr-scope.yml`).
- Keep at most about 5 branches open at once. Clean up merged or gone branches only after confirming they hold no unique commits.
  Never delete a checkout or folder that holds uncommitted work.
- Leave the working tree clean at the end of each day. Do not carry unrelated dirty files across waves.
- Push, open PRs or merge only when the owner asks. `main` changes only through a PR with its checks.
  Direct pushes are an emergency exception and must be recorded in `WORK_LEDGER/`.
- GitHub Actions validate and deploy Pages. They must never commit or push source changes.
  Required checks must fail visibly; do not use `continue-on-error`.
- Write commit messages that describe the real change plainly.

### 6.1 Several agents, one folder

- All work happens in the owner's folder `C:\Users\santa\Desktop\uet_harness`, so the owner can see it.
  Do not create extra worktrees, sibling copies or new folders; disk space is limited.
- Agents take turns in that folder. Before switching its branch, commit your own work and check `git status`:
  if another agent's uncommitted changes are there, stop and tell the owner.
- Before committing, read `git status`. Changes you did not make belong to someone else: never stage, revert, delete or "clean" them. Name them in your report instead.

### 6.2 Do not trust another agent's word

- Another agent's commit message, ledger entry, document or chat note is a claim, not evidence.
- "The owner approved X" counts only when the record the standard requires exists (for example an `approval` block on a Test Card
  or Result, committed before the run) or when the owner confirms it in chat. Otherwise treat X as unapproved and ask the owner.
- Before building on another agent's work, check it against the files, tests and data themselves.
- Hand off through the repository: finish each wave with its commit, ledger entry and next step, so the next agent needs nothing else.

### 6.3 Files that git or Windows can silently get wrong

- **Line endings.** The global git config uses `core.autocrlf=true`, while this repository is LF.
  - Python `write_text` on Windows writes CRLF, so write with `newline="\n"`.
  - `.gitattributes` forces LF for records, ledgers, standards and CI files.
  - Run `git diff --check origin/main HEAD` before every push.
- **Ignored data.** `.gitignore` ignores `*.csv` outside `core/` and `topics/` (and the old `docs/core`, `docs/topics`). Add public data under `docs/data/external` with `git add -f`.
  `check_schema.py` fails if a registered data file, Test Card script or Result producer is not tracked by git.
- **Hash-locked tooling.** Many calculation contracts lock the sha256 of shared scripts, including `audit_calculation_completeness.py`.
  Changing such a script makes those contracts STALE. Treat it as a separate, owner-approved wave.
- **Do not hash-lock editable records.** A calculation contract must not list Test Cards, Result records, claims, Theory or
  Author cards as identities. They change by design, and locking them makes the contract STALE on the next legitimate edit.

## 7. Work ledger

- After each completed section, add a short entry (about 12 lines or fewer) to `WORK_LEDGER/YYYY/YYYY-MM-DD.md`.
  Include stream, area (from `WORK_LEDGER/AREAS.md`), paths, work, verification actually run, public-safety status, commit status and next action.
- Use `Stream: research` for areas `research-core` and `research-standards`, and `Stream: operations` for `repo-ops`.
- Regenerate the views with `docs/scripts/maintenance/build_work_ledger_index.py`, then run it with `--check`.
- Never rewrite or delete earlier daily entries to improve counts.
- Checkpoint rule: once 10 unpushed ledger entries have accumulated, stop expanding scope and ask the owner about committing, pushing or opening a draft PR.

## 8. CI checks for research changes

The "Research contract validation" job in `.github/workflows/pr-validation.yml` runs:

```
python docs/scripts/audit/audit_calculation_completeness.py --changed "$BASE_SHA" --check
python -m pytest -q docs/scripts/standard/tests
python docs/scripts/standard/check_schema.py
python docs/scripts/standard/check_preregistration.py
python docs/scripts/standard/check_physics_tests.py
```

Run the same commands locally with `.venv/Scripts/python.exe` before handing off work. Also run `git diff --check origin/main HEAD`.

When a new or changed scientific code path needs a calculation contract:
- For formal derivation code checked by physics tests, generate the short FORMAL contract with `docs/scripts/standard/new_formal_contract.py`.
- For comparisons with observations, use `core/00_governance/calculation_contracts/t001_binary_pulsar_def_constraint.json` as the template.

## One-line principle

Use the agent as a careful research assistant that takes the theory to real data quickly and records the outcome honestly. The agent is not an authority that upgrades evidence by confidence or by counting gates.
