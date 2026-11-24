# Topic 0.18 Mathnicry: audit under Research Standard v2 and the next direction

> Drafted by Claude on 2026-11-23 (AI review). Legacy files are not changed by this note; their provenance stays LEGACY_UNREVIEWED.
> Context: in Nov 2026 the Riemann hypothesis was reported proved with AI help and certified in Lean by the Lean/Mathlib community (Scientific American, 2026-11-20/21); quasi-RH (OpenAI, Oct 2026) and several Navier-Stokes blow-up claims (one still unverified) appeared the same season.

## 1. What topic 0.18 contains

488 files: about 30 Python scripts in 5 groups, 12 analysis documents, a reference folder and a few result files.
The shared idea in the legacy work is "every problem is the minimisation of an information potential Omega".

## 2. Branch-by-branch verdict

| Branch | What the code actually does | Value as evidence | Why |
|---|---|---|---|
| Riemann (`Engine_Riemann_Field`, `Research_Riemann_*`, `Proof_Riemann_Siege`) | evaluates abs(zeta) at zeros returned by `mpmath.zetazero(n)`; gradient descent on abs(zeta) from Re = 0.8 | none for RH | the zeros come from the library and already lie on the line; descent on abs(zeta) only finds zeros that exist, so it cannot exclude off-line zeros (circular) |
| BSD (`Engine_Elliptic_Resonance`, `Research_BSD_Elliptic_Unity`) | surrogate rank rule (a+b) mod 2 and a made-up L-function | none | no elliptic curve, no real L-function |
| P vs NP (`Proof_P_vs_NP_*`, Grover scripts) | Grover iteration count pi/4 sqrt(N) on a state vector | none for P vs NP | Grover's square-root speed-up is known (1996) and does not make NP-complete problems polynomial |
| Collatz | bounded iteration with an entropy-weighted potential | none | bounded check; code has unreachable logic after a return |
| Poincare, Hodge (`Proof_Millennium_Grand_Slam`, `Hodge_Lattice_Topography`) | diffusion (Laplacian smoothing) of a 2D grid surface | none | 2D grid smoothing is not Ricci flow on 3-manifolds; Poincare was proved by Perelman |
| Quantum circuits (`Engine_Quantum_Logic`, Bell fidelity) | standard gate matrices, Bell state, entropy | correct, standard | textbook linear algebra; useful as a tested utility, not as UET evidence |
| SHA-256 / "miner" scripts | hash computations and searches | unrelated | no link to any theorem or to the UET equations |
| Grand slam report | prints PASS for seven problems | overclaim | the PASS strings are not tied to any theorem statement |

The topic's own `LIMITATIONS.md` and `FORMULA_AUDIT.md` (2026-11 reviews) already list most of these limits. The public-facing docs (`Doc/ANALYSIS_01_Riemann_Hypothesis.md` "FINAL", `Result/03_Research/grand_slam_report.txt` "Verified") still overclaim.

## 3. Why the old route could not work (AI interpretation)

"A zero of f is a minimum of abs(f)" is true of every function. A principle that is true of everything cannot single out where the zeros lie. A proof needs mathematical lemmas that hold for zeta and fail for functions that break RH; a physical principle gives none of them by itself.

## 4. What is worth keeping

- The instinct to connect UET to mathematics, and to check results by machine.
- The quantum-circuit utilities, as tested code.
- The lesson from 2026: the large AI proofs were syntheses of known ideas checked line by line in Lean. UET is a synthesis theory too; what it lacks is the machine check.

## 5. New direction: 0.18 becomes the formal-proof lane of the UET core

Prove the derived relations of the core in Lean, so that their evidence is a checked proof rather than numerical tests (L1). Candidates, easiest first:

| # | Theorem (core claim) | Mathematics needed |
|---|---|---|
| F1 | Persistence threshold: for continuous strictly increasing uptake mu with mu(0) = 0, a consumer invades the empty chemostat iff S0 > R*, i.e. S > delta R* (`C_L3_SUPPLY_CHEMOSTAT`) | real analysis, intermediate value theorem |
| F2 | Trace feedback: the quadratic for the steady trace, the switch supply S_c and the sign change of the invasion rate at S_c (`C_L3_TRACE_FEEDBACK`) | algebra, inequalities |
| F3 | Isotropic occupation cannot feed phi: the scattering integral telescopes to int_a^(a+w) f(E) dE >= 0 (`C_L3_FROM_ACTION`) | integrals, monotonicity |
| F4 | O(2) charge identity d_mu N^mu = chi1 E2 - chi2 E1 with the portal on (`C_NOETHER_COVERAGE`) | polynomial algebra, derivatives |
| F5 | Lowest R* wins: with linear uptake the only stable steady state keeps the type with the smallest R* (`C_L3_SELECTION_FORMAL`) | linear stability, inequalities |

A machine-checked proof makes each statement exact for the stated assumptions; it does not make the model true of nature (that still needs Test Cards).

## 6. Millennium problems and UET (for the record)

- Riemann: no UET equation involves primes or zeta; reported proved in Nov 2026.
- Navier-Stokes: the Clay problem is about the exact NS equations; adding UET terms changes the equation. NS with extra damping is a known, separately studied class.
- Yang-Mills mass gap: the UET action has no non-abelian gauge field.
- P vs NP, Hodge, BSD: no shared structure.
UET should not target these problems; it should prove its own statements and publish them in a checkable form.

## 7. Clean-up to do with the owner's approval

- Mark `grand_slam_report.txt` and the Riemann analysis as LEGACY_UNREVIEWED overclaims in the topic README (do not delete; do not rewrite history).
- Rename nothing; add a boundary line to each public doc that says "not a proof".

## 8. Progress on the formal-proof lane (2026-11-23)

All five candidates F1 to F5 are proved in Lean 4 (v4.36.0) with Mathlib, in `Code/06_Lean/uet_formal/`.
`lake build` succeeds, no file contains `sorry`, and `#print axioms` reports only the three standard axioms
(propext, Classical.choice, Quot.sound) for every main theorem. Lean also showed that several hypotheses were
not needed (d2 > 0 in F2; three positivity conditions in F5's invasion criterion), so those theorems hold more
generally than the numerical tests assumed. F4 is proved in flat 1+1 dimensions; the curved-metric
(diffeomorphism) identity remains a numerical check.

F6 (added the same day, `UetFormal/EnergyMomentum.lean`): the flat-space energy and momentum identities
d_t H + d_x S = sum_A d_t chi_A E_A and d_t P + d_x Pi = sum_A d_x chi_A E_A, off shell, for any number of fields
with their own kinetic coefficients and speeds and any differentiable potential, the portal included. It assumes
equal mixed partials (C^2 fields). Angular momentum in 2+1 and the curved-metric Bianchi identity remain numerical
checks.

F7 (`UetFormal/Boost.lean`): the boost identity d_t K^t + d_x K^x = x sum d_t chi E + c t sum d_x chi E
+ sum_A Z_A (c - c_A) d_t chi_A d_x chi_A, off shell. On shell the boost charge is conserved when every field has
speed c, and for one field with c_A /= c it is not conserved wherever Z, d_t chi and d_x chi are nonzero. This
proves the numerical finding that the boost charge needs one light cone.

F8 (2026-11-24, `UetFormal/Rotation.lean`): the rotation (angular momentum) identity in flat 2+1,
d_t J^t + d_x J^x + d_y J^y = x sum d_y chi E - y sum d_x chi E + sum_A Z_A (b_A - a_A) d_x chi_A d_y chi_A, off shell,
where a_A and b_A are the squared speeds of field A along x and y. On shell the rotation charge is conserved when
every field is isotropic in space (a_A = b_A); unlike the boost (F7), different fields may have different speeds.
One anisotropic field breaks it wherever Z d_x chi d_y chi is nonzero. The curved-metric Bianchi identity remains
a numerical check.

F9 (2026-11-24, `UetFormal/Reparam.lean`): the homogeneous case of Noether's second theorem. For any minisuperspace
Lagrangian L = Q(q, qdot)/N - N U(q) + beta W(q), with Q quadratic in the velocities through a symmetric G(q),
N d/dt E_N = sum_k E_k qdot_k - beta dW/dt holds off shell. With beta = 0 (reparametrization invariant) the energy
constraint E_N = 0 is preserved once the other equations hold; with beta /= 0 it is not (the negative control of
the numerical test). Writing the Bianchi I parent action in this form needs an integration by parts of the curvature
term; that step is an AI derivation checked by the sympy test, not by Lean. The full curved-metric identity
nabla^mu E_mu_nu = -kappa (E_phi d_nu phi + sum_A E_A d_nu chi_A) remains a numerical check.
