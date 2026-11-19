# UET Repository Context

This glossary is the compact shared vocabulary for repository architecture work.
It does not replace `AGENTS.md`, `topics/For Work/`, or topic standards.

## Canonical terms

- **Research source**: a reviewed or working file under `docs/`, `uet_history/`,
  or `thailand_proposals/` that is edited as the primary content.
- **Artifact**: a generated or recorded output such as a verifier result, report,
  figure, manifest, or gate. An artifact can support a claim but does not replace
  the source or the governing standard.
- **Canonical state**: the state determined by repository sources, metadata,
  manifests, gates, verifier artifacts, and update logs according to the relevant
  standard.
- **Derived index**: a searchable copy built from canonical sources. It may be
  stale and must never promote a claim or status on its own.
- **Research workflow**: the evidence-producing work in topics, theory/history,
  books, and policy proposals.
- **Platform**: optional tooling around the research corpus, including agents,
  knowledge retrieval, APIs, MCP, and future GraphQL surfaces.
- **Service**: code in `services_and_experiments/`. A service is not a source of
  truth and must not be required for ordinary research work unless explicitly
  activated by a documented decision.
- **Future platform**: a retained design or prototype that is not part of the
  current research execution path.
- **Work section**: one coherent unit of work that can be recorded in the repo
  ledger and closed with verification and a Git checkpoint.

## Boundary rule

Research, books, and policy consume canonical sources and evidence artifacts.
Optional services may index or expose those sources, but they must not decide
research status, claim strength, publication readiness, or provenance.

## Decision record rule

Use `docs/adr/` only for a decision that is hard to reverse, surprising without
context, or involves a real trade-off. Routine edits belong in the relevant
README, update log, or work ledger.
