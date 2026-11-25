---
layout: article
title: "UET Topic 0.18: Mathnicry"
description: "Evidence-bounded overview for mathematical proof-attempt and symbolic experiment branches in the UET repository."
---

# 0.18 Mathnicry

Topic status: core research, draft.

This topic groups UET-inspired mathematical and mathematical-physics experiments related to Riemann-style stability, BSD-style elliptic-curve surrogates, quantum-search scaling, Collatz dynamics, SHA-256/search demos, and proof-boundary dashboards.

## Legacy status (labelled 2026-11-25 with the owner's approval)

The legacy branches of this topic are `LEGACY_UNREVIEWED`. None of them proves a theorem. The review is in
[`Doc/AUDIT_2026-11-23_STANDARD_V2.md`](Doc/AUDIT_2026-11-23_STANDARD_V2.md). Files are kept as they were; nothing was
deleted or renamed. Overclaims to read with that in mind:

- `Result/03_Research/grand_slam_report.txt` (and its copies under `Result/03_show_Result/`), written by
  `Code/02_Proof/Proof_Millennium_Grand_Slam.py`: the PASS lines for seven Millennium problems are printed strings, not
  tied to any theorem statement.
- Riemann branch (`Doc/ANALYSIS_01_Riemann_Hypothesis.md` "FINAL", `Engine_Riemann_Field`, `Research_Riemann_*`,
  `Proof_Riemann_Siege`): the zeros come from `mpmath.zetazero`, which already returns zeros on the critical line, so the
  checks are circular and cannot exclude off-line zeros.
- BSD branch (`Research_BSD_Elliptic_Unity`, `Engine_Elliptic_Resonance`): surrogate rank rule and a made-up L-function.
- P vs NP (`Proof_P_vs_NP_*`, Grover scripts): Grover's square-root speed-up, which does not make NP-complete problems
  polynomial.
- Collatz, Poincare and Hodge scripts: bounded checks and 2D grid smoothing, not proofs.

Each legacy analysis document now opens with a one-line "not a proof" banner. The current formal work of this topic is
the Lean lane [`Code/06_Lean/uet_formal/`](Code/06_Lean/uet_formal/README.md): machine-checked proofs (F1 to F9) of
derived relations of the UET core, which make those statements exact under their assumptions but do not show that the
model describes nature.

## Current Claim Class

- Claim class: internal run-contract support for a surrogate BSD demonstration.
- Current artifact: `Result/artifacts/0_18_mathnicry_verification.json`.
- Current verifier: `Code/03_Research/Research_BSD_Elliptic_Unity.py`.
- Data posture: manual/placeholder; no theorem branch is source-backed enough for proof-level claims.

## Evidence Boundary

The repository can currently support conservative statements such as:

- The primary BSD script runs and writes a machine-readable artifact.
- Several branches implement symbolic or numerical diagnostics for theorem-inspired questions.
- The formula registry identifies which branches are heuristic, diagnostic, or open.

The current evidence package does not establish the Riemann Hypothesis, BSD conjecture, P vs NP, Collatz conjecture, Hodge conjecture, Navier-Stokes regularity, Yang-Mills mass gap, or any other Millennium-problem closure.

## Core Files

- `FORMULA_AUDIT.md`: proof-boundary registry for BSD, Riemann, P-vs-NP/Grover, quantum logic, Collatz, SHA-256/search, Hodge/topography, and grand-slam aggregation.
- `DATA_MANIFEST.md`: current manual/placeholder data posture.
- `VERIFICATION_SPEC.md`: primary verifier command and artifact contract.
- `METHOD.md`: branch method boundary and excluded cases.
- `LIMITATIONS.md`: theorem-boundary limitations.
- `Code/03_Research/Research_BSD_Elliptic_Unity.py`: current primary verifier.

## Verification

Primary command:

```powershell
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8='1'; .\.venv\Scripts\python.exe docs\topics\0.18_Mathnicry\Code\03_Research\Research_BSD_Elliptic_Unity.py
```

A pass means the current BSD surrogate demonstration ran and wrote an artifact. It does not mean BSD, Riemann, P vs NP, Collatz, or any other theorem has been proved.

## Next Hardening Tasks

1. For every `Proof_*` script, add a proof-boundary record: theorem target, assumptions, domain searched, result class, blocker, and artifact path.
2. Replace surrogate BSD rank logic with actual elliptic-curve/L-function data or rename the branch as visualization only.
3. Reframe Grover/P-vs-NP scripts as quantum-search scaling unless a formal reduction and complexity proof exists.
4. Add deterministic tests for the quantum engine: norm preservation, Hadamard, CNOT, Bell state, entropy, and known expected outputs.
5. Fix Collatz dead code and add bounded-search artifacts with explicit search limits and counterexample handling.
