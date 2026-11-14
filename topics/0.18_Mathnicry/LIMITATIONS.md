# Limitations

- The root baseline comparison is present, but numeric acceptance boundaries are still provisional until a saved artifact is generated and reviewed.
- Current data posture is "manual or placeholder", which is below a fully normalized archival dataset package.
- Presence of proof scripts does not by itself establish theorem-level correctness, so proof scope must stay explicit.
- Internal script execution does not by itself establish external replication, theorem-level proof, or broad physical closure.
- The current BSD verifier uses a surrogate rank rule `(a+b)%2`, not actual elliptic-curve rank or L-function computation.
- Riemann scripts that evaluate `mpmath.zetazero(n)` check library-provided zeros; they do not search for or exclude off-critical-line zeros.
- Grover/P-vs-NP scaling scripts demonstrate quantum-search behavior and do not imply NP-complete problems are polynomial-time solvable.
- Collatz scripts are bounded/heuristic and include code hygiene issues such as unreachable logic after a `return` in `Engine_Collatz_Field.py`.
- Figure and report names containing `Proof` are not theorem-level evidence unless linked to a formal theorem statement and closed proof.
