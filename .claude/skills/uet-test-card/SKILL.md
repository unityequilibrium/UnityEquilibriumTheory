---
name: uet-test-card
description: Take a UET claim to external data under Research Standard v2 - data intake and manifest, a preregistered Test Card, author approval before the run, the run, and the PASS / FAIL / INCONCLUSIVE record. Use for any comparison with published or measured data, including "test this on real data" and "draft a card".
---

# Test Card workflow (STANDARD §4, §5, §7)

The order is enforced by `check_preregistration.py`. Each numbered step is its own commit.

1. **Proposal** (optional but usual): `topics/<topic>/Doc/PROPOSAL_<TEST>_<date>.md` with the question, the competing models with their numbers, the data needed, the method and the proposed criteria. Disclose what you already know about the data (it is rarely blind).
2. **Data intake** (ask before any download; state file, source and size):
   - Save raw files under `docs/data/external/<field>/<set>/`. CSVs there are git-ignored: use `git add -f`.
   - Register each file in `docs/standard/data_manifest.json`: `data_id, description, source, doi_or_url, retrieved, path, sha256, license, visibility, note`. Hash only raw external data.
   - Never reuse data that fitted or calibrated a claim to validate the same claim.
3. **Claim at L0** in `claims.json` (the card needs its claim to exist).
4. **Draft card** `docs/standard/tests/T0NN.json` (schema `uet-test-card-v2`), `status: "DRAFT"`, `drafted_by: "claude"`:
   - `test_kind`: only `CONSTRAINT` (known data; never call it a prediction) or `BLIND_PREDICTION` (holdout with `exposure: UNSEEN`).
   - `theory_card`: `{card_id: "UET_PARENT", version}` from `core/theory_card.json`; `hypothesis`; `observable` {quantity, unit, domain}.
   - `data_sources`: `{data_id, role, exposure}` with role `COMPARISON`, `HOLDOUT` or `CALIBRATION` and exposure `UNSEEN`, `SEEN_SUMMARY` or `SEEN_FULL`; every `data_id` must already be in the manifest, even for a draft.
   - `prediction_method` {script, description}; `free_parameters`; `fixed_parameters` (mark AI choices).
   - `pass_criterion` and `fail_criterion` as numbers or computable expressions. Not allowed: "script runs", "hash matches", "N/N checks pass".
   - The script must refuse to run before approval (say so in its docstring) and must check the data sha256.
5. **Author approval**: only when the author says so in chat. Add `"approval": {"approved_by": "santxkoz", "date": "...", "role": "AUTHOR"}`, set `status: "APPROVED"`, and commit before any result exists. Never approve your own card. Criteria are frozen from here.
6. **Run** once. Commit the script output path and numbers (`research(core): T0NN run is <outcome> ...`).
7. **Result** `R_<ID>.json` with `test_card_id`, `outcome` (`PASS`, `FAIL`, `INCONCLUSIVE`) and `numbers`.
   - The claim stays at L1 or L0 until the author approves L2. Ask; record the approval block on the result.
   - A failed confrontation is `outcome: "FAIL"` with `level: "FAILED"` (the schema pairs them). Record it plainly. Do not rename it, split the scope, or add a branch to escape the comparator.
8. Update README counts and the results table, CORE_MAP and UPDATE_LOG, then `uet-ship`.

## Schema traps seen before
- `test_kind` values other than CONSTRAINT / BLIND_PREDICTION fail the schema.
- Booleans in `numbers.value` fail; write "yes"/"no".
- Every file a record points to must be tracked by git.
- The contract for a data comparison follows `core/00_governance/calculation_contracts/t001_binary_pulsar_def_constraint.json`; its `evidence` may list only identities (code, data), never the Test Card or Result.
