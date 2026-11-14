# Formula Audit: 0.18_Mathnicry

Review status: first reviewed proof-boundary registry.

This topic is a collection of mathematical proof attempts and symbolic/numerical experiments. The registry below intentionally groups related scripts into audit surfaces rather than pretending that every script establishes a theorem. A script in `Code/02_Proof` is treated as proof-oriented code, not proof-level evidence, unless its assumptions, theorem statement, and validity domain are explicitly closed.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T18-BSD-001` | Surrogate elliptic potential: `L_surrogate(s) = (s-1)^rank * exp(-(s-1)^2)` and `Omega = |L_surrogate(s)|^2`; local `rank = 1 if (a+b)%2 == 0 else 0`. | `Code/01_Engine/Engine_Elliptic_Resonance.py`, `Code/03_Research/Research_BSD_Elliptic_Unity.py` | `a`, `b`: integer curve coefficients in `y^2=x^3+ax+b`; `s`: complex dimensionless variable; `rank`: local surrogate flag; `Omega`: dimensionless. | `rank` rule is a heuristic bridge; not sourced from elliptic-curve arithmetic or actual L-function data. | Heuristic surrogate/open. | Current primary verifier branch; supports only internal demonstration/run-contract status. | Can label a curve as rank 0 in narration while local parity rule produces rank 1; does not compute BSD rank or leading L-series term. | Replace parity rank with source-backed curve data or a math library computation, then write rank/order-of-vanishing artifact. |
| `T18-RIEMANN-002` | Zeta potential: `Omega(s)=|zeta(s)|` or fallback eta approximation; Riemann siege checks `Omega(0.5 + i*t_n) < 1e-7` for known zeros `t_n = imag(mpmath.zetazero(n))`. | `Code/01_Engine/Engine_Riemann_Field.py`, `Code/02_Proof/Proof_Riemann_Siege.py` | `s`: complex dimensionless input; `t_n`: imaginary coordinate from mpmath; `Omega`: dimensionless magnitude. | `mpmath.zetazero` supplies known zero coordinates; threshold `1e-7` is local numeric tolerance. | Numerical consistency check, not theorem proof. | Diagnostic-only; not current primary verifier. | Checking points already returned as zeta zeros cannot prove no off-line zeros exist. | Add explicit theorem target, define search domain, record zero source/version, and remove proof-level wording. |
| `T18-PNP-003` | Grover-style iteration count: `iterations = int(pi/4 * sqrt(N))`, `N=2^k`; target fidelity is `abs(state[target])^2`. | `Code/01_Engine/Engine_Quantum_Logic.py`, `Code/02_Proof/Proof_P_vs_NP_Scaling.py`, `Code/03_Research/Research_Grover_Search_UET.py` | `k`: qubits; `N`: state count; `iterations`: count; `state`: complex amplitude vector; `fidelity`: probability. | Grover scaling is standard quantum-search behavior; use of it as P-vs-NP argument is heuristic/open. | Known algorithm demonstration plus unsupported complexity-theory bridge. | Diagnostic-only. | Demonstrating `O(sqrt(N))` unstructured search does not imply NP-complete problems are polynomial-time solvable. | Rename branch to quantum-search scaling unless a formal reduction and complexity proof are supplied. |
| `T18-QUANTUM-004` | Gate simulation: Hadamard `H=(1/sqrt(2))*[[1,1],[1,-1]]`, Pauli-X, CNOT tensor flip; entropy `S=-sum(lambda_i^2 log2(lambda_i^2))`. | `Code/01_Engine/Engine_Quantum_Logic.py`, `Code/02_Proof/Proof_Bell_State_Fidelity.py`, `Code/03_Research/Verify_Quantum_Logic.py` | `state`: normalized complex vector; probabilities dimensionless; entropy in bits. | Standard quantum circuit formulas; implementation is local. | Model implementation/internal check. | Diagnostic branch for quantum-engine integrity. | Does not establish new theorem claims; state-vector simulation scale is bounded by memory. | Add deterministic unit tests for gates, norm preservation, Bell fidelity, and entropy against known expected states. |
| `T18-COLLATZ-005` | Collatz transform: if even `n -> n/2`, if odd `n -> 3n+1`; potential `Omega(n)=log2(n)*(1+binary_entropy(n))`; gradient compares next potential to current. | `Code/01_Engine/Engine_Collatz_Field.py`, `Code/02_Proof/Proof_Collatz_Convergence.py`, `Code/03_Research/Research_Collatz_Unity.py`, `Code/03_Research/Research_Lyapunov_Collatz.py` | `n`: positive integer; entropy and Omega dimensionless; step count integer. | Collatz rule is standard; Omega function is local heuristic bridge. | Bounded numerical/heuristic analysis, not proof. | Diagnostic-only. | Potential can increase on some steps; bounded trajectories do not prove convergence for all integers. There is also dead code after a `return` in `get_binary_entropy`. | Fix dead code, define bounded search range, artifact failure cases, and distinguish empirical convergence from proof. |
| `T18-SHA-006` | Native SHA-256 and mining/resonance scripts transform byte/string states and search predicates. | `Code/01_Engine/Engine_SHA256_Native.py`, `Code/03_Research/UET_Grover_Miner_Alpha.py`, `Code/03_Research/Research_UET_Resonance_Miner.py` | Bytes, hashes, nonce/search counts; mostly dimensionless/discrete. | SHA-256 algorithm standard if implemented faithfully; UET mining bridge is local heuristic. | Implementation/exploratory. | Diagnostic-only. | Performance or search success does not imply cryptographic weakness without a formal attack model. | Add known SHA-256 test vectors and separate cryptographic claims from visualization/search demos. |
| `T18-HODGE-007` | Lattice/topography and Hodge-style scripts compute field surfaces, potentials, or visual indicators over grids. | `Code/03_Research/Hodge_Lattice_Topography.py`, visualization scripts, related docs. | Grid coordinates and potentials are dimensionless unless otherwise declared. | Local visualization/model parameters. | Exploratory visualization. | Showcase/diagnostic only. | Figure names such as "proof" can overstate visual demonstrations. | Add explicit theorem target or rename outputs as diagrams/diagnostics. |
| `T18-GRANDSLAM-008` | Aggregator script reports broad Millennium-problem style claims from separate branches. | `Code/02_Proof/Proof_Millennium_Grand_Slam.py`, `Result/03_Research/grand_slam_report.txt` | Mixed symbolic/numeric branch outputs; no shared unit system. | Aggregates local heuristics and diagnostics. | Open/proof-boundary placeholder. | Not a verifier for theorem closure. | Aggregation can convert many weak diagnostics into a false proof impression. | Restrict to dashboard/status map; require each branch to cite artifact, theorem target, assumptions, and blocker. |

## Current Verifier Boundary

- Primary verifier: `Code/03_Research/Research_BSD_Elliptic_Unity.py`.
- Current artifact target: `Result/artifacts/0_18_mathnicry_verification.json`.
- Supported claim class: internal run-contract/surrogate BSD demonstration.
- Unsupported by current artifact: proof of BSD, Riemann Hypothesis, P vs NP, Collatz, Hodge, Navier-Stokes, Yang-Mills, or any Millennium Problem.

## Unit and Data Discipline

- Most quantities are dimensionless mathematical or algorithmic states.
- The current data posture is manual/placeholder; `Data/Download_Quantum_Data.py` is a helper, not a dataset that validates the theorem branches.
- Any future theorem-branch artifact must record the exact domain searched, precision, library versions, tolerances, and known counterexample policy.

## Required Follow-Up

- Convert `Proof_*` naming in docs into proof-boundary labels: theorem target, assumptions, domain, result class, blocker.
- Make each branch write its own artifact with PASS/WARN/FAIL and failure reasons.
- Replace "solved/proof" wording in user-facing docs and figure captions unless theorem-level evidence exists.
- For Riemann/BSD branches, use actual mathematical library/source-backed data rather than surrogate fields before making theorem-adjacent claims.

## Audit Link

- Core audit report: `docs/meta/core_research_hardening_audit.md`
