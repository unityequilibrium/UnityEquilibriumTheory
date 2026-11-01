# Formula Audit Template

Link the calculation contract (ID, profile, review state and locator) following
[Calculation and Observation Completeness v1](30_Calculation_and_Observation_Completeness_Standard.md).
State modeled/corrected/omitted/inapplicable/unknown components and error-budget evidence.

Use this template to document important formulas in a topic.

## Formula Audit

### Entry 1: `<formula_id>`

**Relation**

```text
<write the formula or calculation path>
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `<x>` | `<meaning>` | `<unit>` |

**Conversion steps**

| Step | Description |
| :-- | :-- |
| `1` | `<unit conversion or normalization>` |

**Constant origins**

| Term | Origin class | Note |
| :-- | :-- | :-- |
| `<constant>` | `<source_locked_physics_constant / heuristic_bridge / ...>` | `<source or caveat>` |

**Status**

| Field | Value |
| :-- | :-- |
| `proof_status` | `<identity / derived / checked local / heuristic bridge / open>` |
| `verification_role` | `<gate / benchmark input / diagnostic-only / exploratory>` |
| `code_path` | `<script or engine path>` |
| `artifact_path` | `<artifact path or N/A>` |

**Failure mode**

- `<what goes wrong if this term or unit path is wrong>`

**Next hardening step**

- `<what should be derived, source-locked, or tested next>`
