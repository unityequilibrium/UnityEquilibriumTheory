# UET Evidence local plugin

Read-only local MCP tools for the UET repository's schema-3 evidence index.

## What it does

- `search_evidence`: runs BM25/FTS5 or deterministic literal fallback search and returns short snippets, hashes, line locators, and stale-source diagnostics.
- `fetch_source`: reads a bounded range from the original repository file after checking its source hash; an optional chunk hash can verify the exact full chunk.
- `configure_repository`: validates the repository and index, then stores the repository path in plugin-local data.

The server never writes the repository or index, ingests files, calls a model/API, invokes a shell, accesses the network, or changes UET topic/status data. Search output leaves claim lane and controlling blocker as `unknown`; use original lines to support conclusions. Content returned into ChatGPT may be included in that conversation.

## Requirements

- ChatGPT Desktop with local/repository plugin support enabled for the current account/workspace.
- Node.js 18 or newer available as `node` on the app's process path.
- Python 3.10 or newer with SQLite support; Python's SQLite build must include FTS5 when the configured index uses the FTS5 backend.
- A prebuilt schema-3 index at the standard or local research-foundation pilot path below.

Setup prefers that standard index when it is schema 3. If it is legacy, setup can use the local pilot index at `tmp/research-foundation-pilot/after-corpus.sqlite3`. That pilot index covers only its pinned corpus; changed source files are excluded as stale, so it is not a full or current repository index.

If the client does not support the plugin's local `stdio` MCP transport, do not publish the repository or open an unauthenticated public tunnel. Use a supported local-MCP connection method approved for the current ChatGPT Desktop surface.

## Local installation

1. Restart ChatGPT Desktop after adding this local repository marketplace.
2. Open Plugins, choose the `UET Research Tools` local source, and install `UET Evidence`.
3. Start a new desktop chat and invoke the plugin's setup skill or `configure_repository` tool once with the absolute repository root.
4. Search for a narrow question and fetch the cited source lines before relying on a claim.

The plugin is stored under the repository's local `plugins/` folder and is not published by these files. ChatGPT installs a local copy in its plugin cache; after code changes, refresh/reinstall the local plugin and start a new conversation.

## Tests

From the repository root, run:

```powershell
node --test plugins/uet-evidence/test/server.test.js
```

Tests use temporary fixture repositories and never access the live local index or a paid provider.
