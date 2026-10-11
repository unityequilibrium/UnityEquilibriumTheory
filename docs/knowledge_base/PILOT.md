# Research foundation pilot

## Evidence interface

Schema-3 SQLite is derived data. `search`, `status`, `fetch` and `ingest
--dry-run` never initialize or migrate the index. A legacy database fails with
an explicit rebuild instruction. Keep the existing database and build a NEW
path with `--db <new-path> ingest --rebuild <scopes>`.

`search --packet` returns schema-version 1 JSON: `question`, `scope`, `lane`,
`controlling_blocker`, `evidence`, and `diagnostics`. Lane/blocker default to
`unknown`; they are supplied task context, not inferred scientific status.
Each evidence record has `source_path`, `source_hash`, `chunk_hash`,
`heading_path`, `line_start`, `line_end`, `text`, `snippet`, `search_method`.
Line ranges are one-based and inclusive; SHA256 source hashes cover original
bytes, while chunk hashes cover UTF-8 text with LF-separated lines. Full text
preserves the corresponding source lines, including limitations.

`fetch <path> --line-start N --line-end M --expected-hash SHA256` returns that
exact range after checking source identity. Paths must resolve inside the repo;
raw/private/secret/config sources are rejected. Malformed FTS syntax is an
error, not a silent change to LIKE semantics. The fallback backend uses literal
substring search and deterministic path/chunk order. Diagnostics explicitly
identify stale sources excluded from evidence. This is a retrieval layer, not
an evaluator that changes research gates.

## Offline checks and baseline

Run `python -m pytest docs/knowledge_base/tests -q`. For restricted environments,
provide `--basetemp` beneath a writable workspace directory. The 24 KB cases
cover retrieval (8), freshness/scope (8) and citation/boundary (8); additional
tests cover accounting and client behavior. The legacy comparison loads a
frozen pre-edit module using `UET_KB_BASELINE_MODULE`; do not point it at the live
index. Inputs and nine installed skill hashes are recorded in the snapshot.
These fixtures do not constitute an evaluation of all nine skills or all topics.

For a new checkout, obtain the frozen pre-edit module from the Git revision
recorded in `PILOT_RESULTS.json` using `git show <revision>:docs/knowledge_base/personal_kb.py`,
and save it under `tmp/research-foundation-pilot/legacy_personal_kb.py`.
The pilot runner checks corpus hashes and refuses a changed-source rerun.

## Cost accounting and optional live comparison

`chat()` returns text and `embed()` returns vectors. Real calls now require
`preflight(agent_id)`, explicit `experiment_id` and positive `experiment_limit`.
An unknown price or unresolved charge fails closed. Preflight is restricted to
the official OpenRouter endpoint, confirms configured-model availability,
fetches current prices and checks credits. The default client is not an unlimited
spender. Environment keys override file keys; keys/prompts are never logged.

The append-only JSONL ledger records reservation and settlement events keyed
by request ID. Summaries count the latest event once. Actual provider cost,
historical estimates, unknown amounts and held reservations stay distinct.
Daily totals use UTC; experiment totals persist across restarts and day changes.
The exclusive lock spans each request. An interrupted process can leave a
lock; inspect the recorded pending request and provider billing before recovery.
Do not delete a lock or release a reservation simply to resume spending. Once
authoritative cost is obtained, use `log_call` with the SAME request ID,
experiment ID and reservation, plus `provider_cost`, to append a settlement.

The pilot is text-only, sequential, without retries, plugins, tools or model/
provider fallback. It reserves conservative text-byte and output bounds before
each call and admits complete pairs only within the remaining $2 experiment
cap. Additional or unrecognised pricing is rejected. These bounds depend on
provider price metadata; if reported cost exceeds a reservation the experiment
stops. They are not a guarantee against incorrect provider billing.

Run `python -m docs.knowledge_base.foundation_pilot --live --config <actual-config>`.
The model comes exclusively from `agents.local_data`; never substitute the
template model. The corpus is four explicit public standards documents.
There are at most 8 pairs/16 calls with 2,048 output tokens and temperature 0.
Existing experiment ledger entries prevent duplicate runs. Config missing or
unsupported pricing/model information blocks only the paid section.

Keys, SQLite databases, full responses, detailed usage and private run records
remain under ignored `tmp/`. `PILOT_RESULTS.json` contains only safe metrics,
source identities and limitations. Context bytes are not token counts. Paired
answer quality requires source/rubric review; no pass is inferred from a model's
self-assessment, and no claim about ChatGPT subscription usage follows.

## Acceptance and next controller

Mandatory locator correctness, freshness and scope checks must pass. A 20%
token reduction is an efficiency target, never permission to omit evidence.
Do not expand to Jev/MCP until paired quality review and actual usage support
the change. A missing API configuration or absent domain review must remain a
visible blocker in the result report.
