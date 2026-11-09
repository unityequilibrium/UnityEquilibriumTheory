# Limitations

- The primary verifier checks a source constant against a local CODATA working copy; it does not derive `G`.
- Planck units are standard definitions computed from constants, not an independent validation of UET gravity.
- Weak-field calculations such as `g = GM/r^2`, `r_s = 2GM/c^2`, and `n(r) ~= 1 + 2GM/(rc^2)` are diagnostics unless tied to source-backed artifacts.
- The equivalence-principle script currently asserts `eta = 0`; it does not compare against the MICROSCOPE 2022 reported value and uncertainty.
- Eot-Wash short-range gravity data exists locally, but no primary artifact currently tests UET parameter values against the exclusion curve.
- This topic does not currently validate light bending, perihelion precession, Einstein field equations, singularity avoidance, or quantum-gravity closure.
- Downstream core topics must inherit these limitations before citing `0.19` for broad GR or cosmology claims.
- Topic-level source-evidence and branch-claim gates now make that boundary explicit: accepted evidence stops at the CODATA constant checkpoint and derived Planck-unit branch, not GR closure.
- The artifact-level `gravity_claim_scope_gate` is the export controller: constant PASS
  cannot be cited as first-principles G derivation, GR validation, equivalence-principle
  proof, short-range gravity validation, singularity resolution, or quantum-gravity closure.

## Core GR program dependency boundary

- The core `epsilon_nc = 0` result is an exact response-null of an implemented candidate evaluator, not a solved metric PDE or a derivation of Einstein equations.
- The covariant balance result is local and exchange-completed; it is not a global conservation theorem or proof that the universe is open or closed.
- The causal kernel is restricted to a flat local 1+1 constitutive lane, and the matter-space reduction covers only the response sector.
- The Noether-to-phase-field result closes only a fixed-scale coarse coordinate layer; EOS, covariant coarse graining, susceptibility, transport/KMS, entropy current, and dissipative-Bianchi completion remain blocked.
- Core candidate artifacts do not replace Topic 0.19 light-bending, perihelion, MICROSCOPE, Eot-Wash, metric/EFE, singularity, or quantum-gravity benchmark artifacts.
- The Topic 0.19 CODATA PASS and Planck definitions remain a Claim Class C internal checkpoint with export controller `WARN`.
- Topic status remains `Draft / Tier B`; no physical GR, global-universe, external-validation, or solved-theory claim is promoted.
