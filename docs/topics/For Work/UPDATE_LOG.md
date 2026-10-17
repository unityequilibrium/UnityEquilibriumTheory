# UET Research Standards Update Log

> Scope: shared research standards and the foundation-first equation workflow.

## [2026-10-17] - Scoped calculation and observation contracts v1

- Area: research-standards; pilot linkage: Core matter-space/observer and Topic13, then astronomy coverage.
- Changed: standard/template/schema, stdlib validator and artifact-metadata interface; observer/component/error/correction rules; gradual legacy inventory and changed-path CI checks.
- Verification: standalone contract tests and selected existing matter-space tests; read-only/deterministic checks and scoped diff check recorded in WORK_LEDGER.
- Result: methodological enforcement is implemented; unresolved physical/model/source conditions remain INCOMPLETE. No scientific artifact or physical threshold changed.
- Existing blockers: pre-migration equation-registry references and unrelated topic readiness metadata drift remain visible in the old audits.
- Next controller: review scoped physical state/observable/input gaps from the contract inventory; do not rerun unchanged proofs or treat coverage as scientific closure.

## [2026-07-26] - Foundation-first equation protocol

- Wave type: `workflow-repair pass`
- Added or changed: `EQUATION_RESEARCH_AND_PHYSICAL_CORRESPONDENCE_STANDARD.md`, core-scoped `AGENTS.md`, equation registry, protocol, dependency gate, and foundation audit.
- Verified with: `.venv\Scripts\python.exe docs/scripts/audit/audit_uet_equation_foundation.py --json`; `git diff --check`.
- Result: audit `PASS`; foundation gate `BLOCKED`.
- Blocker narrowed: equation work now has a named F0-F8 controller instead of relying only on scattered formula, lifecycle, and hardening prose.
- Still open: the initial registry is not exhaustive; complete the repository-wide equation inventory and standard-physics correspondence matrix.
- Next controller: `foundation_inventory_and_correspondence_registry_incomplete`.
- Claim impact: no physical claim upgrade; legacy core wording explicitly quarantined.
- Workflow linkage: applies the shared constitution, lifecycle, formula-audit, and hardening rules to `docs/core/`.
