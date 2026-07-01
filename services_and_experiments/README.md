# Services and Experiments

This folder keeps prototype service code that supports UET tooling experiments.

It is source-only by default. Do not commit local runtime state, generated build
outputs, compiled binaries, credentials, `.env` files, or machine-specific caches.

## Current areas

| Area | Purpose |
| :-- | :-- |
| `uet_agents/` | prototype agent orchestration and document ingestion helpers |
| `uet_api/` | experimental Rust API service |
| `uet_chain/` | experimental ledger and chain primitives |
| `uet_core/` | reusable Rust core calculation primitives |
| `uet_kb/` | experimental knowledge-base and MCP-facing service code |
| `uet_miner/` | experimental mining and benchmarking code |
| `uet_security/` | experimental signing, hashing, and key-management primitives |
| `uet_under_development/` | unfinished market, governance, oracle, and economic modules |

## Commit discipline

- Keep this directory separate from research topic hardening commits.
- Treat these services as prototypes unless a later document says otherwise.
- Keep generated artifacts out of Git and publish binaries through releases only.
- Store real secrets outside the repository.
