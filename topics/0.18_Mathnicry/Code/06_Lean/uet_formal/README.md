# uet_formal: machine-checked proofs of UET core relations (topic 0.18)

Lean 4 (toolchain in `lean-toolchain`) with Mathlib. Each file proves derived relations of the UET core
so that their evidence is a checked proof, not only numerical tests. A proof makes the statement exact
under its stated assumptions; it does not show the model describes nature (that needs Test Cards).

| File | Core claim | Status |
|---|---|---|
| `UetFormal/Threshold.lean` | `C_L3_SUPPLY_CHEMOSTAT`: persistence threshold S > delta R* for any strictly increasing uptake; Tilman's Monod R* | proved (2026-11-23), axioms: propext, Classical.choice, Quot.sound |
| `UetFormal/TraceFeedback.lean` | `C_L3_TRACE_FEEDBACK`: type 2 beats type 1 iff E > E_c; invasion rate = a20 r1 beta2 (w/kappa)(S - S_c), so the winner switches exactly at S_c = delta r1 + kappa (r20/r1 - 1)/(w beta2), which lies above delta r1 | proved (2026-11-23), same three axioms |
| `UetFormal/Isotropic.lean` | `C_L3_FROM_ACTION` point 2: the scattering integral over (a, oo) of f(x) - f(x+w) telescopes to the integral of f over [a, a+w], so any non-negative isotropic occupation gives rho >= 0 (an isotropic pool can only damp phi) | proved (2026-11-23), same three axioms |
| `UetFormal/NoetherO2.lean` | `C_NOETHER_COVERAGE` (O(2) part): in flat 1+1, Z (d_t N^t + d_x N^x) = chi1 E2 - chi2 E1 off shell for any differentiable O(2)-invariant potential U(chi1^2 + chi2^2), which includes the portal; on shell the charge is conserved | proved (2026-11-23), same three axioms |
| `UetFormal/Selection.lean` | `C_L3_SELECTION_FORMAL`: resident steady state and its positivity iff S > delta R*; local stability (trace < 0, det > 0); a rare type invades iff its R* is lower; the strictly cheapest type invades all others and resists all; no two types with different R* coexist at rest | proved (2026-11-23), same three axioms |
| `UetFormal/EnergyMomentum.lean` | `C_NOETHER_COVERAGE` (translation part): in flat 1+1, for any number of fields with their own Z_A and speeds c_A and any differentiable potential V (so phi, chi1, chi2 and the portal), d_t H + d_x S = sum_A d_t chi_A E_A and d_t P + d_x Pi = sum_A d_x chi_A E_A off shell; on shell energy and momentum are conserved. Assumes equal mixed partials (C^2 fields). Boost charge not covered | proved (2026-11-23), same three axioms |

Build: `lake exe cache get` (downloads Mathlib's compiled files, about 7 GB in `.lake/`, ignored by git), then `lake build`.
Check axioms: `#print axioms UetFormal.invades_iff_monod`.
