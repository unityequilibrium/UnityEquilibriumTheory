# Center source variations at their declared state

Date:2026-10-01. Numerical caller wiring repair; no parameter or target change.
After source binding correction, the next process exits1 with RuntimeWarning
invalid value encountered in sqrt during the first chemical-potential derivative.
The reused helper evaluates a function at offsets around zero, but the new caller
passed an absolute-mu function. Thus it probed near-zero, uncondensed mu rather
than mu1.28. No complete scientific state or numerical artifact was produced.
The exact uncentered verifier and observed failure record remain archived.

Wrap energy(mu_central+offset) and thermal pressure(mu_central+offset) or
pressure(T_central+offset) before passing the same five-point helper. This restores
the originally prelocked derivative meaning. Do not change the helper, dispersion,
state, physical fixed K, steps, formulas, tolerances or admissions. Original card,
registry, first contract and both failed source versions remain unchanged.
