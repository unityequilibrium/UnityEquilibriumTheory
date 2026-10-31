---
name: uet-evidence-setup
description: Set up and use the local read-only UET evidence search plugin in ChatGPT Desktop.
---

# UET Evidence setup and use

This plugin exposes only three local MCP tools: one-time repository configuration, evidence search, and hash-checked source retrieval. It does not ingest files, write the SQLite index, make paid API calls, access the web, or update research statuses.

## First use

1. Call `configure_repository` with the absolute path to the UET repository folder. On this machine the expected folder is `C:\Users\santa\Desktop\uet_harness`.
2. The tool validates `AGENTS.md`, the local indexer, a schema-3 SQLite index, and a compatible Python runtime, then stores the repository path, selected index, and runtime command in the plugin's local data folder. It prefers the standard index and can fall back to the local research-foundation pilot index when the standard one is legacy.
3. If setup reports a missing or legacy index, do not create or migrate it through this plugin. Ask the user to rebuild explicitly using the repository's documented `personal_kb.py` workflow. The pilot fallback is limited to its pinned corpus and may report changed files as stale.

## Research workflow

1. Search with a narrow question. Add a repository-relative `scope` when the relevant topic or standards folder is known.
2. Treat returned snippets as discovery aids. Use `fetch_source` on selected locators before making a source-backed statement.
3. Keep citations as `source_path#Lstart-Lend` and preserve the returned source hash in any durable evidence note.
4. Report stale/unavailable diagnostics. Never cite those rows; rerun search after the source index is refreshed by its owner.
5. Leave lane, topic status, and controlling blocker as unknown unless fetched source text explicitly supports them.
6. Preserve the distinction between a hypothesis, an internal result, independent replication, and publication. Retrieval rank or model confidence cannot promote a scientific claim.

## Privacy and limits

The MCP process reads only text files inside the configured repository and rejects raw/private/secret/config locations. It opens the index read-only and suppresses Python bytecode writes. Tool responses that ChatGPT uses become part of the current ChatGPT conversation, so fetch only the evidence needed for the question. No repository content is sent to Jev, OpenRouter, or a separate server by this plugin.
