# Formula Audit

## Purpose

Track which electroweak relations are source-locked, derived, checked local, or still open.

## Audit matrix

| Formula ID | Relation | Units | Constant origin | Proof status | Verification role | Current note |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `EW-01` | `sin2_running = 0.25 - (bridge_factor * alpha_em_mz * rho_info) / (2*pi)` | dimensionless | `alpha_em_mz` is source-locked/check-local; `bridge_factor = 1.18` is heuristic bridge | heuristic bridge | benchmark gate | passes current benchmark but is not a full gauge derivation |
| `EW-02` | `m_W = m_Z * sqrt(1 - sin2_running)` | GeV | `m_Z` is source-locked PDG mass input | identity plus benchmark input | benchmark gate | clean unit path; quality depends on `EW-01` |
| `EW-03` | `lambda_h = kappa * sin2_running`, `m_H = sqrt(2*lambda_h) * v_ew` | dimensionless, GeV | `kappa` is topic runtime parameter; `v_ew = 246.22 GeV` is benchmark anchor | derived but incomplete | benchmark gate | internally consistent with current running branch, not full Higgs-sector proof |
| `EW-04` | `G_F = 1 / (sqrt(2) * v_ew^2)` | GeV^-2 | `v_ew = 246.22 GeV` benchmark anchor | identity using anchored input | benchmark gate | mathematically clean; provenance depends on anchored `v_ew` |
| `EW-05` | `tau_n = 879.4 / (G_F / G_F_exp)^2` | seconds | `879.4` is benchmark anchor; `G_F_exp` is source-locked/check-local reference | benchmark anchor | expanded benchmark gate | useful internal gate, not first-principles neutron-decay closure |

## Entry details

### EW-01: Running weak-mixing-angle path

**Relation**

```text
sin2_theta_0 = 0.25
rho_info = beta / kappa
correction = (bridge_factor * alpha_em_mz * rho_info) / (2*pi)
sin2_running = sin2_theta_0 - correction
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `sin2_theta_0` | symmetry-limit seed angle | dimensionless |
| `beta` | topic runtime coupling from `get_params("0.6")` | dimensionless |
| `kappa` | topic runtime scaling parameter | dimensionless |
| `rho_info` | effective information-density ratio | dimensionless |
| `alpha_em_mz` | electromagnetic coupling at electroweak scale | dimensionless |
| `bridge_factor` | SU(2)xU(1) manifold bridge term | dimensionless |

**Constant origins**

| Term | Origin class | Note |
| :-- | :-- | :-- |
| `sin2_theta_0 = 0.25` | topic_derived_relation | symmetry-limit seed used by current engine |
| `alpha_em_mz` | checked_local_reference | used as electroweak reference constant in current workflow |
| `bridge_factor = 1.18` | heuristic_bridge | still needs first-principles derivation |

**Current limitation**

- This is the main scientific soft spot of the topic.
- The relation is structured and benchmarked, but not closed as a first-principles gauge-theory derivation.

**Next hardening step**

- Replace the checked-local weak-mixing-angle layer with a direct upstream mapping if possible.
- Derive or better justify `bridge_factor = 1.18`.

### EW-02: W-mass relation

**Relation**

```text
m_W = m_Z * sqrt(1 - sin2_running)
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `m_Z` | Z-boson mass | GeV |
| `m_W` | W-boson mass | GeV |
| `sin2_running` | running weak-mixing-angle output from `EW-01` | dimensionless |

**Conversion steps**

- No unit conversion inside the formula.
- All masses are held in GeV.

**Current limitation**

- The algebra is clean, but scientific confidence still inherits the weakness of `EW-01`.

### EW-03: Higgs branch

**Relation**

```text
lambda_h = kappa * sin2_running
m_H = sqrt(2 * lambda_h) * v_ew
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `lambda_h` | Higgs self-coupling surrogate in current engine | dimensionless |
| `kappa` | topic runtime scaling parameter | dimensionless |
| `sin2_running` | running weak-mixing-angle output | dimensionless |
| `v_ew` | electroweak vacuum expectation value anchor | GeV |
| `m_H` | Higgs mass prediction | GeV |

**Current limitation**

- This branch is now internally consistent with the successful electroweak-running path.
- It remains a derived internal closure, not a full Standard Model Higgs-sector derivation.

### EW-04: Fermi constant

**Relation**

```text
G_F = 1 / (sqrt(2) * v_ew^2)
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `G_F` | Fermi constant | GeV^-2 |
| `v_ew` | electroweak vacuum expectation value anchor | GeV |

**Current limitation**

- The math and units are clean.
- The open question is not the algebra but why the topic should take `v_ew` from the anchored electroweak scale in this exact way.

### EW-05: Neutron-lifetime gate

**Relation**

```text
ratio_sq = (G_F / G_F_exp)^2
tau_n = 879.4 / ratio_sq
```

**Variables**

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `G_F` | topic-derived Fermi constant | GeV^-2 |
| `G_F_exp` | reference Fermi constant | GeV^-2 |
| `tau_n` | neutron lifetime estimate | s |

**Current limitation**

- This is an audit-grade benchmark gate, not a full neutron-decay derivation.
- The `879.4` baseline must remain labeled as a benchmark anchor.

## Highest-priority open gaps

1. `EW-01` still depends on a heuristic bridge and a checked-local weak-angle reference layer.
2. `EW-03` is internally consistent but not yet a field-theory-level Higgs derivation.
3. `EW-05` should not be promoted beyond benchmark-gate status.
