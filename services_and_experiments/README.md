# Services and Experiments

This folder keeps source-only prototype services and repository-local tools/plugins for a future UET platform.

The current UET execution path is research-first: work in docs/,
uet_history/, and thailand_proposals/ must remain useful with these
services stopped or unavailable. Read [SERVICE_STATUS.md](./SERVICE_STATUS.md)
before changing or activating a component.

It is source-only by default. Do not commit local runtime state, generated build
outputs, compiled binaries, credentials, `.env` files, or machine-specific caches.

## Current areas

| Area | Purpose |
| :-- | :-- |
| `plugins/` | repository-local plugins and MCP tools, including read-only UET evidence search |
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
- Do not make research topics depend on a service for status, claims, gates, or
  provenance.
- Keep service status changes separate from topic hardening unless the same
  scoped decision requires both.
