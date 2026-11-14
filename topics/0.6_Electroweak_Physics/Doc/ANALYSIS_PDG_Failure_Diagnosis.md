# Electroweak PDG Transition Diagnosis

## Scope

This note records how topic `0.6_Electroweak_Physics` moved from an initial PDG-linked failure to a current PDG-linked pass, and what still remains outside the scope of that pass.

Primary verifier:

- `docs/topics/0.6_Electroweak_Physics/Code/03_Research/Research_Electroweak_PDG_Comparison.py`

Supporting diagnosis:

- `docs/topics/0.6_Electroweak_Physics/Code/03_Research/Research_Electroweak_Higgs_Diagnosis.py`

Artifacts:

- `docs/topics/0.6_Electroweak_Physics/Result/artifacts/electroweak_pdg_validation.json`
- `docs/topics/0.6_Electroweak_Physics/Result/artifacts/electroweak_higgs_diagnosis.json`

## Current real-data result

Observed PDG-linked residuals after the electroweak consistency fixes:

| Observable | UET | PDG/reference | Relative error |
| :-- | --: | --: | --: |
| `sin2(theta_W)` | `0.231236` | `0.23153` | `0.127%` |
| `m_W` | `79.953 GeV` | `80.377 GeV` | `0.528%` |
| `m_H` | `125.263 GeV` | `125.200 GeV` | `0.051%` |
| `G_F` | `1.166375e-5 GeV^-2` | `1.166379e-5 GeV^-2` | `0.00028%` |

Verifier status: `PASS`

## What changed

### 1. The first failure was an implementation problem

The earlier PDG-linked run failed badly because the electroweak engine was effectively counting the Landauer beta twice inside the mixing-angle correction.

Before that fix:

| Observable | Relative error |
| :-- | --: |
| `sin2(theta_W)` | `49.98%` |
| `m_W` | `6.68%` |
| `m_H` | `4.03%` |

After removing the beta double-counting:

| Observable | Relative error |
| :-- | --: |
| `sin2(theta_W)` | `0.127%` |
| `m_W` | `0.528%` |
| `m_H` | `4.03%` |

So the first correction was an implementation cleanup, not a parameter retune.

### 2. The remaining mismatch was a branch-consistency problem

The Higgs branch had still been using the raw symmetry-limit seed:

- `lambda_higgs = kappa * 0.25`

while the successful electroweak angle and W-mass branch was already using the corrected running angle:

- `sin2_theta_W_running ~= 0.231236`

That meant the Higgs mass was being computed from a less physical branch than the one already validated by the electroweak observables.

### 3. Unifying the branch closed the Higgs mismatch

The engine now uses:

- `lambda_higgs = kappa * sin2_theta_W_running`

under the same runtime `kappa`, rather than the legacy raw-angle seed.

Under that comparison:

| Higgs branch | Higgs mass | Relative error |
| :-- | --: | --: |
| Legacy raw-angle branch | `130.246 GeV` | `4.031%` |
| Current running-angle branch | `125.263 GeV` | `0.051%` |

This closes the PDG Higgs mismatch without changing the runtime `kappa`.

## Scientific interpretation

- The current pass is stronger than the earlier topic-local claims because it is tied to source-locked PDG data.
- The improvement did not come from fitting `kappa`; it came from using a Higgs branch that is internally consistent with the already-validated electroweak-running branch.
- This is still a selective observable package, not a full proof of the electroweak sector.

## Remaining limitations

1. The effective weak-mixing-angle reference is still carried through a topic-local snapshot note rather than a direct PDG table mapping.
2. The current pass covers four observables only: `sin2(theta_W)`, `m_W`, `m_H`, and `G_F`.
3. Internal consistency is now better, but a fuller derivation is still needed if the running-angle Higgs branch is to be defended in a manuscript-level argument.

## Next checks

1. Replace the weak-mixing-angle snapshot reference with a direct PDG table mapping.
2. Extend the electroweak benchmark package beyond the current four observables.
3. Keep proof scripts and runtime verifiers on the same parameter regime for all future electroweak work.
