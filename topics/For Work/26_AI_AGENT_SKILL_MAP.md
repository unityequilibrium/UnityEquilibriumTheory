# AI Agent Skill Map

This file defines the UET skill layer for AI collaborators.

It does not replace the standards in this folder. The skill layer is an adapter
that routes an agent to the right source files, reconstruction order, and output
discipline before it edits, audits, or summarizes topic work.

## Purpose

Use this map when:

- creating or updating a UET-focused Codex skill
- deciding which skill should handle a repo task
- checking that AI workflow support still points back to canonical standards
- preventing repeated hardening work from becoming custom one-off behavior

## Source-of-truth rule

`docs/topics/For Work/` remains the canonical operating manual.

Skills may:

- route an agent to the right standard
- enforce reading order and checklist discipline
- produce draft audits, summaries, templates, and next-wave plans
- identify drift between docs, metadata, gates, artifacts, and logs

Skills may not:

- override a `For Work` standard
- promote readiness or claim status without human review
- treat prose memory as stronger than artifacts, manifests, gates, or metadata
- replace artifacts, manifests, or update logs as evidence records

## Global required reads

Every UET skill must start from these repo-local sources when they exist:

1. `AGENTS.md`
2. `docs/topics/For Work/00_README.md`
3. `docs/topics/For Work/01_Project_Research_Constitution.md`
4. `docs/topics/For Work/03_AI_Usage_and_Governance.md`

Then read the task-specific standards listed below.

## Skill catalog

| Skill | Use when | Required task-specific reads | Primary output |
| :-- | :-- | :-- | :-- |
| `uet-status-reconstructor` | reconstructing a topic's current state | `02_Project_Workflow_and_Lifecycle.md`, `18_Research_Hardening_Workflow.md`, topic docs, latest artifact/gate/log | status tuple and controlling blocker |
| `uet-repo-wide-progress-snapshot` | summarizing many topics | `02_Project_Workflow_and_Lifecycle.md`, `18_Research_Hardening_Workflow.md`, `docs/topics/README.md`, `docs/meta/` | compact topic table |
| `uet-claim-auditor` | reviewing claim wording or status language | `04_Claim_and_Evidence_Rubric.md`, style guide if available | claim/evidence map and flagged wording |
| `uet-hardening-wave` | planning or executing one blocker-narrowing pass | `18_Research_Hardening_Workflow.md`, `24_TEMPLATE_UPDATE_LOG.md` | one scoped wave packet |
| `uet-update-log-writer` | recording repeated hardening work | `24_TEMPLATE_UPDATE_LOG.md`, `18_Research_Hardening_Workflow.md` | concise update-log entry |
| `uet-formula-audit` | reviewing formulas, units, constants, or derivation status | `17_Formula_Audit_Standard.md`, topic `FORMULA_AUDIT.md` | formula audit findings |
| `uet-data-provenance-audit` | checking data source and local input traceability | `12_Data_Standard.md`, topic `DATA_MANIFEST.md` | provenance findings |
| `uet-result-artifact-reviewer` | reviewing result files or verifier artifacts | `14_Result_Standard.md`, topic `VERIFICATION_SPEC.md` | artifact quality findings |
| `uet-standards-drift-detector` | checking disagreement across docs, metadata, artifacts, gates, and logs | `02_Project_Workflow_and_Lifecycle.md`, `18_Research_Hardening_Workflow.md` | drift report and controlling state |

## Skill specifications

### `uet-status-reconstructor`

- Purpose: rebuild a topic's current state from local evidence.
- Trigger: user asks for status, current blocker, readiness, what changed, or whether a topic can be promoted.
- Required reads: global required reads, `02_Project_Workflow_and_Lifecycle.md`, `18_Research_Hardening_Workflow.md`, `docs/topics/README.md`, relevant `docs/meta/`, topic `README.md`, `LIMITATIONS.md`, `VERIFICATION_SPEC.md`, latest artifact/gate, and `UPDATE_LOG.md` when present.
- Workflow: read canonical status sources first, read topic docs, read artifacts/gates, read log last for wave history, then report explicit facts separately from inference.
- Output: readiness label, controlling blocker, latest verifier result, last completed wave, publication boundary, and drift notes.
- Stop condition: if no artifact/gate/log can support a status claim, report that status-hardening is needed instead of guessing.

### `uet-repo-wide-progress-snapshot`

- Purpose: produce a compact multi-topic progress view.
- Trigger: user asks for overall progress, what changed lately, stalled topics, or active topic state.
- Required reads: global required reads, `docs/topics/README.md`, relevant `docs/meta/`, and the local package for each topic included.
- Workflow: summarize each topic with the same tuple so missing evidence is visible.
- Output: topic, readiness, controlling blocker, latest verifier result, last wave, publication boundary.
- Stop condition: if a topic cannot be summarized from local evidence, mark it as needing status-hardening.

### `uet-claim-auditor`

- Purpose: prevent claim inflation in topic docs and summaries.
- Trigger: user asks whether wording is too strong, requests a README rewrite, asks for publication language, or uses restricted phrases such as `proved`, `verified`, `solved`, `exact`, or `production grade`.
- Required reads: global required reads and `04_Claim_and_Evidence_Rubric.md`.
- Workflow: classify each major claim, map it to evidence/script/data/baseline, flag forbidden upgrades, and propose conservative replacements.
- Output: claim class, supporting evidence, allowed wording, flagged wording, and replacement language.
- Stop condition: if evidence cannot be located, keep the claim at hypothesis/model wording.

### `uet-hardening-wave`

- Purpose: run or plan one coherent blocker-narrowing wave.
- Trigger: user asks to harden, unblock, repair, or continue a repeated topic pass.
- Required reads: global required reads, `18_Research_Hardening_Workflow.md`, `24_TEMPLATE_UPDATE_LOG.md`, and the local topic package.
- Workflow: reconstruct state, choose one controlling blocker, decide wave type, tighten the smallest artifact/gate/manifest/doc boundary, rerun only relevant verifiers, sync docs, write log, and keep commit scope coherent.
- Output: wave packet with blocker, files, verifier decision, doc sync, log entry, and commit scope.
- Stop condition: if the blocker is not visible in a machine-readable artifact, gate, or manifest, make that visibility the next wave goal.

### `uet-update-log-writer`

- Purpose: make multi-wave work reconstructable without git archaeology.
- Trigger: user asks to record a hardening pass, update a topic log, or summarize a completed wave.
- Required reads: global required reads, `24_TEMPLATE_UPDATE_LOG.md`, and relevant artifact/gate/verifier output.
- Workflow: confirm real work happened, use artifact/gate wording for blockers, record verifier commands only if run, and keep the entry concise.
- Output: one update-log entry with scope, wave type, changed item, verification, result, narrowed blocker, next controller, claim impact, and workflow linkage.
- Stop condition: do not write a promise-only entry as if it were completed work.

### `uet-formula-audit`

- Purpose: audit formula provenance, units, constants, proof status, and code linkage.
- Trigger: user asks about equations, units, derivations, formula readiness, hidden constants, or physics/math credibility.
- Required reads: global required reads, `17_Formula_Audit_Standard.md`, topic `FORMULA_AUDIT.md`, `METHOD.md`, verifier code, and artifacts where relevant.
- Workflow: list important formulas, map variables and units, classify constant origins, assign proof status, identify failure modes, and compare README wording to formula status.
- Output: formula findings with required field gaps and next hardening step.
- Stop condition: if unit closure or origin is missing, keep wording at open/heuristic/checked-local status.

### `uet-data-provenance-audit`

- Purpose: ensure important datasets are traceable and honestly labeled.
- Trigger: user asks about data provenance, source readiness, manifests, dataset hashes, or reproducibility inputs.
- Required reads: global required reads, `12_Data_Standard.md`, topic `DATA_MANIFEST.md`, data files, scripts, and artifacts.
- Workflow: identify source, DOI/URL, license/terms, original filename, local path, preprocessing, unit convention, benchmark role, and artifact linkage.
- Output: missing provenance fields, mislabeled local copies, unit risks, and required manifest updates.
- Stop condition: if upstream identity or local path is unclear, block stronger reproducibility claims.

### `uet-result-artifact-reviewer`

- Purpose: review whether outputs are evidence products rather than storage clutter.
- Trigger: user asks about results, verifier JSON, figures, logs, artifacts, thresholds, or pass/fail records.
- Required reads: global required reads, `14_Result_Standard.md`, topic `VERIFICATION_SPEC.md`, result artifacts, verifier scripts, and inputs where practical.
- Workflow: classify outputs, confirm correct folder role, inspect artifact metadata, check metrics/thresholds/config/input identity, and separate logs from evidence.
- Output: artifact quality report and required metadata fixes.
- Stop condition: if evidence exists only in logs/screenshots, do not treat it as benchmark-grade.

### `uet-standards-drift-detector`

- Purpose: find disagreements between repo-wide status, local docs, artifacts, gates, and logs.
- Trigger: user asks why status is confusing, whether docs are stale, or whether a topic's narrative matches its evidence.
- Required reads: global required reads, `02_Project_Workflow_and_Lifecycle.md`, `18_Research_Hardening_Workflow.md`, repo-wide metadata, local topic docs, latest artifact/gate, and `UPDATE_LOG.md`.
- Workflow: compare sources in controlling order, identify the latest stable artifact/gate, list docs that outrun or understate it, and propose a sync-only repair.
- Output: drift table, controlling state, and repair order.
- Stop condition: if sources disagree, do not average them; name the controlling artifact/gate and mark the rest as drift.
