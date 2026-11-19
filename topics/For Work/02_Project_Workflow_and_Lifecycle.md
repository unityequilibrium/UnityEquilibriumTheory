# Project Workflow and Topic Lifecycle

Theory design follows [Theory Development and Research Sequencing v1](32_Theory_Development_and_Research_Sequencing_Standard.md):
proposition -> minimal model -> consistency -> comparator -> physical realization ->
locked test -> generalization. These are decision stages, not readiness labels or
new physics gates. Reuse the existing evidence before selecting the next dependency.
Explicit FORMAL/normalized exploration may continue with physical correspondence
open under the existing F2 exception; it cannot satisfy a physical acceptance claim.

Calculation paths also follow [Calculation and Observation Completeness v1](30_Calculation_and_Observation_Completeness_Standard.md).
Declare a scoped contract before using new/changed calculations for physical claims;
unknown contributions permit bounded diagnostic work but not physical acceptance.

This document defines how a UET topic should move from idea to structured research work.

## Purpose

Provide the standard lifecycle for turning an idea into a topic that is organized,
auditable, and honest about its readiness.

## When to use

Use this file when:

- creating a new topic
- deciding a topic's readiness label
- promoting or demoting a topic
- planning missing artifacts and next steps

## Workflow summary

```mermaid
flowchart LR
    A["Hypothesis note"] --> B["Draft topic"]
    B --> C["Structured topic"]
    C --> D["Reproducible internally"]
    D --> E["Academic-ready"]
    E --> F["Paper preparation"]
    C -. missing evidence .-> B
    D -. broken provenance or unstable runs .-> C
```

## Readiness matrix

| State | Minimum docs | Evidence expectation | Typical blocker |
| :-- | :-- | :-- | :-- |
| `Hypothesis note` | note or sketch | idea only | no stable benchmark |
| `Draft` | README and assumptions | partial structure | missing manifests, baselines, or formula registry |
| `Structured` | root standards set | auditable internal package | scripts, artifacts, or formula provenance still weak |
| `Reproducible internally` | docs plus stable artifacts | rerunnable internal benchmark | external scrutiny not ready |
| `Academic-ready` | mature methods package | bounded claims and explicit limits | paper framing still needed |

## Lifecycle states

### 1. Hypothesis note

Use when:

- the core idea exists
- the mechanism is still speculative
- there is no stable benchmark yet

Minimum output:

- a note or draft
- no public certainty wording

### 2. Draft topic

Use when:

- folder structure exists
- initial code or derivation exists
- data and baselines are still incomplete

Minimum output:

- topic README
- high-level assumptions
- open questions list

### 3. Structured topic

Use when:

- README exists in standard format
- method, data manifest, verification spec, baseline comparison, and limitations exist
- status wording is under control

Minimum output:

- `README.md`
- `METHOD.md`
- `DATA_MANIFEST.md`
- `VERIFICATION_SPEC.md`
- `BASELINE_COMPARISON.md`
- `LIMITATIONS.md`
- `FORMULA_AUDIT.md` or equivalent dedicated registry
- unit and variable definition section or equivalent

### 4. Reproducible internally

Use when:

- verification commands are stable
- artifacts are produced consistently
- inputs and thresholds are explicit

Minimum output:

- standard docs from the `Structured` stage
- generated artifact examples
- deterministic or documented runtime assumptions

### 5. Academic-ready

Use when:

- methods are clear enough for external scrutiny
- evidence and limitations are mature
- manuscript material can be drafted without inventing missing steps

Minimum output:

- structured topic package
- publication-oriented analysis
- clear statement of what is and is not being claimed

## Standard workflow

1. Start with problem definition.
2. Declare assumptions before writing triumph language.
3. For equation work, complete F0-F4 in EQUATION_RESEARCH_AND_PHYSICAL_CORRESPONDENCE_STANDARD.md before implementation.
4. Declare formulas, units, variable meanings, and standard-physics correspondence before writing high-confidence prose.
5. Collect references and dataset provenance.
6. Build or refactor code.
7. Complete formal and numerical verification before observable mapping.
8. Define the measurement operator, metric, threshold, uncertainty, baseline, and holdout policy before comparing against data.
9. Write limitations before writing summaries.
10. Only then update public-facing wording.

## Promotion rules

A topic may move up one readiness level only if its required artifacts are present.

It may move down if:

- evidence was overstated
- provenance is unclear
- a key script no longer runs
- a baseline claim cannot be audited

## Required review questions before publishing a topic

- Is this a derivation, a fit, or a prediction?
- Is the dataset local and documented?
- Is the baseline explicit?
- Are the variables and units explicit?
- Which constants come from source-locked physics, and which are bridges or heuristics?
- Does the README say more than the verification spec supports?
- Would a skeptical reviewer know what to attack first?

If the answer to the last question is "no", the topic is probably still too vague.

## Key rules

- promotion happens one level at a time
- missing artifacts block readiness upgrades
- demotion is allowed when evidence weakens or drift is discovered
- limitations must be written before public summary language is upgraded

## Common failure modes

- skipping from idea to strong README wording
- marking a topic reproducible without stable commands and artifacts
- treating folder creation alone as scientific progress
- hiding demotion when a script no longer runs or provenance breaks
- calling a topic structured even though formulas still have no origin or unit table
- promoting dictated equations into methods without a formula-audit pass

## Checklist

- [ ] current readiness label matches actual artifacts
- [ ] required root files exist for the stage claimed
- [ ] formulas, units, and variable meanings are explicit enough for review
- [ ] metric, threshold, and baseline are explicit before promotion
- [ ] public wording was updated only after evidence review
- [ ] next blocker for promotion is named clearly
