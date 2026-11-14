# Formula Audit — Topic 0.25

> **Registry:** `Data/03_Research/uet_us_economics_formula_gate.json`
> **Book version:** `book1-economics-v2-research-reset`

| Formula ID | Relation | Class | Unit closure | Current status |
| --- | --- | --- | --- | --- |
| `BOOK-HEURISTIC-001` | `R=N+K+I` | narrative mnemonic | `FAIL` | `RETIRED_AS_IDENTITY` |
| `EC25-PRODUCTION-KLEMS` | `dlnQ = Σs_x dlnX_x + dlnA` | standard benchmark | closed in log changes | benchmark |
| `EC25-INNOVATION-CONSTRAINT` | innovation as a function of constraint, knowledge, R&D, capital, finance, institutions | hypothesis family | model specific | open; no sign restriction on constraint |
| `EC25-MONEY-PURCHASING-POWER` | `PP=P0/Pt` | measurement definition | dimensionless | basket/group/base required |
| `EC25-MONEY-IDENTITY` | `MV=PY` | accounting identity | closed for matching scope/time | not causal by itself |
| `EC25-RESOURCE-COVERAGE-DIAGNOSTIC` | `dlnM-dlnY_or_capacity` | Book-inspired diagnostic | closed after log change | not observed money value |
| `EC25-IO-FOOTPRINT` | `x=(I-A)^-1f`, `q=B(I-A)^-1f` | accounting/modelled network | closed with declared matrices | not individual lineage |
| `EC25-FIRM-SOURCES-USES` | financing sources = uses + residual | accounting bridge | currency per period | no tagged-dollar inference |
| `EC25-INFRASTRUCTURE-CAPITAL` | `Kp[t+1]=(1-delta)Kp[t]+I[t]` | benchmark | real capital stock | separate from debt |
| `EC25-INFRASTRUCTURE-SOCIAL-NPV` | discounted benefits minus costs | project benchmark | present-value currency | fiscal NPV/debt service separate |
| `EC25-EXERGY-DESTRUCTION` | `B_destroyed=T0*S_generated` | physical benchmark | J if K × J/K | requires boundary/reference environment |
| `EC25-WAGE-PRODUCTIVITY-GAP` | `ln(productivity)-ln(compensation)` | construction-specific diagnostic | dimensionless | universe/deflator/vintage must match |

## Retired formulas

The earlier infrastructure integral subtracted a physical-flow integral from a currency debt stock and omitted depreciation, O&M, discounting, maturity, and residual value. It is not used.

The earlier `ΔE_usable=-ΣΔS_nested` mixed joules with joules per kelvin. It is replaced by a standard exergy relation only where the physical system is defined.

## Claim boundary

Formula readiness authorizes calculation under declared assumptions. It does not authorize `law`, `proved`, `fiat caused`, `validated peg`, or policy-success wording.
