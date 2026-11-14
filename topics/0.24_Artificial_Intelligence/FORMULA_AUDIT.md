# Formula Audit: 0.24_Artificial_Intelligence

Review status: reviewed first-pass registry for the scaling-law and sparsity
benchmark lane. Alignment, ethics, consciousness, and developmental-AI claims
remain open until they have separate source-backed verifier artifacts.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `AI24-SCALING-POWER-LAW` | `L_N = (N_c / N)^alpha_N`; `L_D = (D_c / D)^alpha_D`; `L_C = (C_c / C)^alpha_C` | `Data/03_Research/scaling_laws.json`; `Research_AI_Scaling_Audit.py` | `L_*` dimensionless loss proxy; `N` parameters; `D` tokens; `C` PF-days; `alpha_*` dimensionless exponents | Kaplan et al. scaling-law working copy; upstream bibliographic source still needs DOI/URL lock | source-backed benchmark relation, not UET derivation | primary scaling-law reference in artifact | Loss offset/irreducible loss omitted; local constants may be rounded; no fresh upstream download | Normalize upstream paper/source metadata and record exact table/exponent provenance. |
| `AI24-CSV-ALPHA-FIT` | fit `log(L) = a - alpha_fit log(N)` | `Data/GPT3_Scaling_Laws.csv`; `Research_AI_Scaling_Audit.py` | `L` dimensionless loss; `N` parameters; `alpha_fit` dimensionless | topic-local GPT-3 scaling-law working table | diagnostic fit | checks whether local CSV broadly agrees with stored `alpha_N` | Tiny local table, no uncertainty model, no irreducible loss term | Replace with a source-locked scaling-law table and full baseline model. |
| `AI24-UET-KAPPA-ALPHA-CHECK` | `Delta = |alpha_N - kappa_macro| / alpha_N` | `Research_AI_Scaling.py`; `Research_AI_Scaling_Audit.py` | `alpha_N`, `kappa_macro`, `Delta` dimensionless | `alpha_N` from scaling-law working copy; `kappa_macro = 0.1` current heuristic proxy | heuristic/open bridge | artifact blocker check for UET constant-identification claim | Numeric closeness is weak and currently outside the provisional warning gate | Derive or fit an information-domain `kappa` from data instead of reusing a macro proxy. |
| `AI24-MOE-SPARSITY` | `active_fraction = active_params / total_params`; `capacity_to_active_ratio = total_params / active_params` | `UET_AI_Core.py`; `Research_AI_Scaling_Audit.py` | total/active parameters are counts; ratios are dimensionless | topic-local model metadata; several rows are working-copy/estimated | source-backed diagnostic where metadata is source-locked, otherwise provisional | checks sparse MoE active fraction vs dense baseline | Model metadata may be estimated, proprietary, or version-dependent | Add upstream source URL/DOI/date for each model row and split estimated rows from verified rows. |
| `AI24-ACTIVATION-ENTROPY` | `H = -sum(p_i log2 p_i)`, `p_i = |a_i| / sum(|a_i|)` | `Code/01_Engine/UET_AI_Core.py` | `a_i` neural activations; `p_i` dimensionless probabilities; `H` bits | Shannon entropy standard formula; activation preprocessing is topic-derived | implemented engine metric, not benchmark-validated | secondary engine diagnostic only | Sensitive to architecture, normalization, and random initialization | Add deterministic seed, dataset, baseline optimizer, and artifact threshold. |
| `AI24-ENTROPY-LR` | `lr = beta * kappa / (1 + H)` | `Code/01_Engine/UET_AI_Core.py` | `lr`, `beta`, `kappa`, `H` dimensionless in current implementation | UET parameter registry plus topic heuristic | heuristic/open | not accepted by primary verifier | No units, no optimizer baseline, no convergence proof | Compare against SGD/Adam on a locked task with repeated seeds. |
| `AI24-DETECTIVE-ENTROPY` | `thought_entropy = log(std(error) + 1)` and tree/correlation reduction | `Code/03_Research/Research_AI_Detective_V2.py` | galaxy velocity-error proxy; entropy is dimensionless heuristic | imports 0.1 galaxy data and engine | cross-topic exploratory diagnostic | excluded from primary 0.24 claim | Uses galaxy residuals, not AI benchmark data; can print "SOLVED" without proving AI theory | Keep out of primary verifier or rewrite as a cross-topic dependency artifact. |
| `AI24-ALIGNMENT-GAME` | cooperation/defection stability simulation terms | `Code/03_Research/Research_Alignment_Equilibrium.py` | utility/stability proxies, dimensionless | topic heuristic | open | future ethics/alignment lane only | Does not establish ethics as a physical law | Define game, payoff table, baseline, and falsifiable threshold before claims. |

## Claim Boundary

- Current accepted evidence supports only a Claim Class C internal benchmark:
  scaling-law metadata and architecture sparsity diagnostics can be checked and
  reproduced from topic-local files.
- It does not support claims that ethics, alignment, consciousness, or AI safety
  are physically proven.
- UET-specific bridges (`kappa` to scaling exponents, entropy learning-rate,
  alignment equilibrium) remain open until they have source-backed verifiers.

## Audit Link

- Core audit report: `docs/meta/core_research_hardening_audit.md`
