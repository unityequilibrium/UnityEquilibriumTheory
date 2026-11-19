---
name: uet-ship
description: Finish UET work so the next agent can pick it up from the repository alone - WORK_LEDGER entry and index, the same checks CI runs, line-ending and ignored-file traps, commit, and (only when the owner asks) push and PR. Use at the end of every wave, Test Card step or repo change.
---

# Ship a unit of work (AGENTS.md §6–§8)

## 1. Ledger
- Append to `WORK_LEDGER/YYYY/YYYY-MM-DD.md` (12 lines or fewer): heading, Stream (`research` for research-core / research-standards, `operations` for repo-ops), Area, Paths, Work, Verification actually run, Public-safety, Commit status, Next.
- Rebuild and check: `.venv/Scripts/python.exe docs/scripts/maintenance/build_work_ledger_index.py` then the same with `--check`.
- Never rewrite earlier entries. At 10 unpushed entries, stop and ask the owner about pushing.

## 2. Checks (what "Research contract validation" runs)
```
.venv/Scripts/python.exe docs/scripts/audit/audit_calculation_completeness.py --check
.venv/Scripts/python.exe -m pytest -q docs/scripts/standard/tests
.venv/Scripts/python.exe docs/scripts/standard/check_schema.py
.venv/Scripts/python.exe docs/scripts/standard/check_preregistration.py
.venv/Scripts/python.exe docs/scripts/standard/check_physics_tests.py
.venv/Scripts/python.exe topics/run_all_tests.py --changed origin/main   # long; run in the background
git diff --check origin/main HEAD
```
`check_preregistration.py` reads git history: commit before trusting its result.

## 3. Traps
- Windows writes CRLF. Write with `newline="\n"`; after a generator, `git diff --check` and strip with `sed -i 's/\r$//' <file>` if needed. Contract hashes are of LF text.
- `.gitignore` drops `*.csv` outside `core/` and `topics/`: `git add -f` registered data.
- A contract's `evidence` may list only its identities; never hash-lock Test Cards, Results, claims or cards.
- `git pull` overwrites `FETCH_HEAD`: fetch again right before `git merge FETCH_HEAD`.

## 4. Commit
- `git status` first. Stage only your files by path. Name other people's changes in the report; never stage, revert or delete them.
- Message: what changed, plainly (`research(core): ...`, `research(standard): ...`, `repo(...): ...`). No `Co-Authored-By: Claude` trailer.

## 5. Push and PR (only when the owner asks)
- Branch `claude/<area>/<task>`, area one of research, repo, services, book, history, policy.
- PRs target `main` (CI runs only there). If stacked on another PR, say so in the body.
- Body follows `.github/pull_request_template.md`. Then bind the PR and offer Auto-fix; never merge unless the owner says so.
