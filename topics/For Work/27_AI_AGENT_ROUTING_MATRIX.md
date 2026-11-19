# AI Agent Routing Matrix

This file routes common UET work requests to the minimum useful skill set and
the canonical standards that must be read first.

Use the task type, not the agent's preference, to choose a skill.

## Routing table

| User request shape | Primary skill | Companion skill | Must read before acting |
| :-- | :-- | :-- | :-- |
| "What is the current status?" | `uet-status-reconstructor` | `uet-standards-drift-detector` | `02_Project_Workflow_and_Lifecycle.md`, `18_Research_Hardening_Workflow.md` |
| "Give me overall progress" | `uet-repo-wide-progress-snapshot` | `uet-status-reconstructor` | `docs/topics/README.md`, relevant `docs/meta/` |
| "Continue hardening this topic" | `uet-hardening-wave` | `uet-update-log-writer` | `18_Research_Hardening_Workflow.md`, `24_TEMPLATE_UPDATE_LOG.md` |
| "This wording sounds too strong" | `uet-claim-auditor` | none | `04_Claim_and_Evidence_Rubric.md` |
| "Can this be promoted?" | `uet-status-reconstructor` | `uet-claim-auditor` | `01_Project_Research_Constitution.md`, `02_Project_Workflow_and_Lifecycle.md`, `04_Claim_and_Evidence_Rubric.md` |
| "Audit formulas or units" | `uet-formula-audit` | `uet-claim-auditor` | `17_Formula_Audit_Standard.md` |
| "Check data provenance" | `uet-data-provenance-audit` | `uet-result-artifact-reviewer` | `12_Data_Standard.md` |
| "Review result artifacts" | `uet-result-artifact-reviewer` | `uet-status-reconstructor` | `14_Result_Standard.md`, topic `VERIFICATION_SPEC.md` |
| "Docs and artifacts disagree" | `uet-standards-drift-detector` | `uet-status-reconstructor` | `02_Project_Workflow_and_Lifecycle.md`, `18_Research_Hardening_Workflow.md` |
| "Write/update an update log" | `uet-update-log-writer` | `uet-hardening-wave` | `24_TEMPLATE_UPDATE_LOG.md` |
| "Create or repair a topic structure" | `uet-hardening-wave` | `uet-data-provenance-audit` | `10_Topic_Architecture_5x4.md`, `02_Project_Workflow_and_Lifecycle.md` |

## Default reconstruction order

When a task asks for status, promotion, progress, or blockers, use this order:

1. `docs/topics/README.md` and relevant `docs/meta/`
2. local topic `README.md`, `LIMITATIONS.md`, and `VERIFICATION_SPEC.md`
3. latest verifier artifact and machine-readable blocker gates
4. manifests such as `DATA_MANIFEST.md` and `FORMULA_AUDIT.md`
5. `UPDATE_LOG.md` for wave history and next-controller context

If these disagree, treat the latest stable artifact and gate as the controlling
state for the current pass, then repair documentation drift.

## Decision rules

- Use the narrowest skill that covers the task.
- Add a companion skill only when it protects a real boundary, such as claim
  wording during status work or update-log discipline during hardening.
- Do not use a skill to skip reading the relevant standard.
- If the same blocker appears across several topics, route first to workflow
  repair in `For Work`, then pilot one topic before broad rollout.
- If a topic lacks machine-readable blocker state, route to status-hardening
  before promotion or publication work.

## Examples

| Prompt | Route |
| :-- | :-- |
| "Why is 0.11 still blocked?" | `uet-status-reconstructor` then `uet-standards-drift-detector` if docs disagree |
| "Make this README less overclaimed" | `uet-claim-auditor` |
| "Run another cleanup wave" | `uet-hardening-wave` and `uet-update-log-writer` |
| "Does this result JSON prove the topic?" | `uet-result-artifact-reviewer` and `uet-claim-auditor` |
| "Find missing formula provenance" | `uet-formula-audit` |
| "Summarize all active topics" | `uet-repo-wide-progress-snapshot` |
