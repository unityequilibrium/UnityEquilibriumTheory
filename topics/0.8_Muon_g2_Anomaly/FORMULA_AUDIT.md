# Formula Audit

## Purpose

Track which parts of the muon g-2 workflow are source-locked inputs, engine relations, or
open bridge terms.

## Audit matrix

| Formula ID | Relation | Units | Constant origin | Proof status | Verification role | Current note |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `MG2-01` | `mass_ratio = m_mu / m_W` | dimensionless | `m_mu` and `m_W` are benchmark inputs | source-locked constant plus benchmark input | benchmark gate input | algebra is clean; source path must stay explicit |
| `MG2-02` | `loop_factor = alpha_em^2 * mass_ratio^2 * (4*pi)` | dimensionless | `alpha_em` source-locked constant | derived | benchmark gate path | structured relation, not a full QED loop derivation |
| `MG2-03` | `spin_factor = (3.0 - 1.5)^2` | dimensionless | topic bridge term | heuristic bridge | benchmark gate path | still needs first-principles justification |
| `MG2-04` | `delta_a_uet = beta * spin_factor * loop_factor` | dimensionless | `beta` from runtime topic parameters | heuristic bridge | canonical benchmark gate | current engine path used by 2025 verifier |
| `MG2-05` | `z_score = abs(delta_a_uet - delta_a_ref) / sigma_ref` | sigma | benchmark package inputs | identity with benchmark inputs | verification metric | source-locked 2025 path is canonical; historical baselines are diagnostic |

## Entry details

### MG2-01: Mass-ratio path

**Relation**

```text
mass_ratio = m_mu / m_W
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `m_mu` | muon mass | MeV |
| `m_W` | W-boson mass expressed in MeV inside engine | MeV |
| `mass_ratio` | electroweak mass ratio | dimensionless |

**Conversion steps**

- The engine uses `m_W = 80379.0` in MeV.
- `m_mu` is also in MeV.
- No hidden unit conversion should be inserted between these terms.

**Current limitation**

- The ratio is dimensionally clean, but `m_W` currently enters as a benchmark-fed value rather than being pulled live from topic `0.6`.

### MG2-02: Loop-factor path

**Relation**

```text
loop_factor = alpha_em^2 * mass_ratio^2 * (4*pi)
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `alpha_em` | electromagnetic fine-structure constant | dimensionless |
| `mass_ratio` | muon-to-W mass ratio | dimensionless |
| `loop_factor` | compact anomaly scale factor | dimensionless |

**Current limitation**

- The formula is mathematically straightforward.
- What remains open is the physical uniqueness of this compact path relative to full Standard Model loop structure.

### MG2-03: Spin bridge

**Relation**

```text
spin_factor = (3.0 - 1.5)^2
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `3.0` | current manifold dimension placeholder in engine logic | dimensionless |
| `1.5` | symmetry offset used by current engine logic | dimensionless |
| `spin_factor` | geometric spin bridge factor | dimensionless |

**Current limitation**

- This is the softest term in the engine.
- It is structured and explicit, but still heuristic rather than first-principles closed.

### MG2-04: UET anomaly correction

**Relation**

```text
delta_a_uet = beta * spin_factor * loop_factor
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `beta` | topic runtime coupling from `get_params("0.8")` | dimensionless |
| `spin_factor` | geometric bridge term from `MG2-03` | dimensionless |
| `loop_factor` | anomaly scale path from `MG2-02` | dimensionless |
| `delta_a_uet` | UET anomaly correction | dimensionless |

**Current limitation**

- This is the canonical engine output used by the 2025 verifier.
- It is benchmark-compatible on the current canonical package, but not a closed proof that the muon anomaly is solved.

### MG2-05: Benchmark comparison metric

**Relation**

```text
z_score = abs(delta_a_uet - delta_a_ref) / sigma_ref
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `delta_a_uet` | engine anomaly output | dimensionless |
| `delta_a_ref` | benchmark experiment-theory gap | dimensionless |
| `sigma_ref` | benchmark uncertainty | dimensionless |
| `z_score` | standardized residual | sigma |

**Current limitation**

- The metric is clean.
- Scientific interpretation still depends on which theory comparator package is chosen, which is why the sensitivity layer must stay part of the topic package.

## Highest-priority open gaps

1. `MG2-03` is still a heuristic bridge rather than a derivation.
2. `MG2-04` still uses a benchmark-fed `m_W` instead of a live dependency on topic `0.6`.
3. `MG2-05` is robust only when the comparator package is declared explicitly.
