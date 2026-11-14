---
layout: article
title: "UET Topic 0.18: Mathnicry"
description: "Evidence-bounded overview for mathematical proof-attempt and symbolic experiment branches in the UET repository."
---

# 0.18 Mathnicry

Topic status: core research, draft.

This topic groups UET-inspired mathematical and mathematical-physics experiments related to Riemann-style stability, BSD-style elliptic-curve surrogates, quantum-search scaling, Collatz dynamics, SHA-256/search demos, and proof-boundary dashboards.

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
