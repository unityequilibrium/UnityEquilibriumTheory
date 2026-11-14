# Formula Audit: 0.1_Galaxy_Rotation_Problem

Bootstrap status: generated scaffold from current code surfaces.

This file is the first-pass formula registry for the topic. It does not claim that
the listed relations are derived or correct. Each row identifies a calculation path
that must be reviewed for variables, units, constants, proof status, verifier role,
failure modes, and next hardening steps.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T01-001` | calculation path in `Data_Loader_SPARC.py` | `Code/01_Engine/Data_Loader_SPARC.py` | benchmark constants; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |
| `T01-002` | engine calculation path in `Engine_Galaxy_V3.py` | `Code/01_Engine/Engine_Galaxy_V3.py` | trigonometry, mass/energy scale, field/density, matrix/vector; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |
| `T01-003` | proof-oriented calculation path in `Proof_Unity_Density_Law.py` | `Code/02_Proof/Proof_Unity_Density_Law.py` | field/density; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |
| `T01-004` | research/benchmark comparison path in `Research_Alpha_Learning.py` | `Code/03_Research/Research_Alpha_Learning.py` | trigonometry, field/density; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |
| `T01-005` | research/benchmark comparison path in `Research_Dwarf_Galaxies.py` | `Code/03_Research/Research_Dwarf_Galaxies.py` | field/density; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |
| `T01-006` | research/benchmark comparison path in `Research_Galaxy_Curve_Social.py` | `Code/03_Research/Research_Galaxy_Curve_Social.py` | trigonometry, mass/energy scale, field/density; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |
| `T01-007` | research/benchmark comparison path in `Research_Galaxy_Rotation.py` | `Code/03_Research/Research_Galaxy_Rotation.py` | benchmark constants, matrix/vector; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |
| `T01-008` | research/benchmark comparison path in `Research_Residual_Analysis.py` | `Code/03_Research/Research_Residual_Analysis.py` | mass/energy scale, field/density; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |
| `T01-009` | calculation path in `Verify_Galaxy_Rotation.py` | `Code/03_Research/Verify_Galaxy_Rotation.py` | matrix/vector; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |
| `T01-010` | baseline/comparator path in `Competitor_NFW.py` | `Code/04_Competitor/Competitor_NFW.py` | trigonometry, mass/energy scale; unit audit required | `open_placeholder` | `open` | exploratory until linked to `VERIFICATION_SPEC.md` | Hidden unit mismatch, untracked benchmark anchor, or unsupported claim. | Review formulas/constants in this file and replace this scaffold row with explicit entries. |

## Required Follow-Up

- Replace each scaffold row with explicit formulas or pseudo-formulas.
- Define every variable and dimensional unit used by the calculation.
- Label constants as source-locked, benchmark anchors, topic-derived, heuristic bridges, or open placeholders.
- Link each important formula to `METHOD.md`, `VERIFICATION_SPEC.md`, and the verifier artifact.
- Keep README claims conservative until open rows are reviewed.

## Audit Link

- Core audit report: `docs/meta/core_research_hardening_audit.md`
