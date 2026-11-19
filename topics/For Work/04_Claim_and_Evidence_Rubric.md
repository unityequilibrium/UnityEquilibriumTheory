# Claim and Evidence Rubric

This rubric defines how to classify statements in UET topics.

Its purpose is to stop claim inflation.

Use [profile-specific applicability and evidence types](32_Theory_Development_and_Research_Sequencing_Standard.md#applicability-and-evidence-types).
For FORMAL work cite the proposition, assumptions and proof/counterexample rather
than inventing a script, dataset or threshold. These classes describe evidence
wording; they are not grades, a universal chronological ladder or guarantees of truth.

## Purpose

Provide a shared language for describing what kind of claim exists, what evidence supports
it, and how strong the wording is allowed to be.

## When to use

Use this file when:

- writing topic summaries
- reviewing README wording
- downgrading overclaimed language
- mapping a claim to evidence for audit or paper work

## Workflow summary

```mermaid
flowchart TD
    A["Draft sentence"] --> B["Classify claim"]
    B --> C["Map to evidence, script, data, baseline"]
    C --> D["Check allowed wording"]
    D --> E{"Too strong?"}
    E -->|Yes| F["Downgrade wording"]
    E -->|No| G["Publish as constrained statement"]
```

## Claim matrix

| Class | What it means | Allowed wording | Not allowed |
| :-- | :-- | :-- | :-- |
| A | mechanism proposed | hypothesis, proposal | solved, verified |
| B | model exists | model, formulation, derived relation | theory confirmed |
| C | internal run benchmark | reproduced internally, passes current internal benchmark | proved nature, externally validated |
| D | external rerun succeeded | externally replicated | peer-reviewed unless it is |
| E | reviewed external result | peer-reviewed result | stronger claims than the paper itself supports |

## 1. Claim classes

### Class A: Hypothesis

Use when:

- the mechanism is proposed
- the math is incomplete
- the benchmark is not yet stable

Allowed wording:

- `hypothesis`
- `proposal`
- `possible mechanism`

### Class B: Model statement

Use when:

- a mathematical or computational model exists
- the model can be run or analyzed
- the evidence is still mostly internal

Allowed wording:

- `model`
- `formulation`
- `derived relation`

### Class C: Internal benchmark result

Use when:

- a script runs
- inputs are known
- metrics and thresholds are explicit
- results are internal to the repository workflow

Allowed wording:

- `reproduced internally`
- `passes current internal benchmark`
- `matches selected repository benchmark data`

### Class D: External replication

Compatibility note: the historical class name is retained. An outside rerun using
the same supplied data/code is external computational reproduction; a study with
independently obtained data is a different evidence type under the National Academies
terminology linked in the standards entrypoint. Record which actually happened.
Do not describe a same-package rerun as independent empirical confirmation. Historical
labels/artifacts are not rewritten or promoted by this clarification.

Use when:

- an outside person or team can rerun the method from the provided package
- the rerun reproduces the result within stated bounds

Allowed wording:

- `externally replicated`

### Class E: Peer-reviewed scientific result

Use when:

- the claim exists in a reviewed publication or accepted equivalent external venue

Review status does not establish correctness, replication, predictive performance or
support beyond the publication's actual evidence. A class E statement can retain
open limitations or later be contradicted; classes need not be traversed in order.

Allowed wording:

- `peer-reviewed result`

## 2. Forbidden upgrades

The following transitions are forbidden without explicit evidence:

- `Hypothesis` -> `Solved`
- `Internal benchmark` -> `proved`
- `fit to selected data` -> `predicts nature`
- `repository code runs` -> `theory confirmed`

## 3. Required mapping for every major claim

Every major topic claim should answer:

Fields apply to the claimed evidence type. Mark genuinely inapplicable fields with
a reason and cite existing records; missing required evidence is not non-applicability.

- claim text
- claim class
- evidence source
- script or derivation source
- data source
- baseline
- uncertainty or limitation

## 4. Fast review test

Before publishing any sentence, ask:

1. Is this a hypothesis, model, fit, benchmark, or external result?
2. What exact evidence supports it?
3. What would make the sentence too strong?

If the third answer is unclear, the sentence is probably too strong already.

## Key rules

- every major claim must map to evidence, script, data, and baseline
- every readiness statement must match a concrete class of support
- strong wording must be earned, not inferred from ambition

## Common failure modes

- saying `verified` when only an internal rerun exists
- calling a fitted retrospective match a prediction
- writing percentages without defining the metric and threshold
- omitting the baseline that makes the claim interpretable

## Checklist

- [ ] claim class is named explicitly
- [ ] evidence source and supporting script are identified
- [ ] dataset and baseline are named
- [ ] wording matches the evidence class
- [ ] limitations or uncertainty are stated where needed
