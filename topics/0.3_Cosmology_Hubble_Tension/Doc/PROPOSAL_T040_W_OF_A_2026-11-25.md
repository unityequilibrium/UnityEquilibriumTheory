# Proposal T040: the parent action's dark-energy w(a) against BAO and supernova distances

Drafted by Claude on 2026-11-25 as T033; renumbered T040 the same day (ID collision). Not approved. No comparison data have been downloaded or opened.
Claim under test: `C_C1_FRW_DARK_ENERGY` (L1, wave C1, `core/03_lanes/scalar_tensor/uet_frw_background.py`).

## Question

Can the w(a) family that the parent action allows reproduce the expansion history measured by baryon acoustic
oscillations (BAO) and type Ia supernovae (SN)? The question is not "is ΛCDM ruled out" (ΛCDM is inside the family).
It is whether the data need an expansion history that the action cannot produce.

## Competing models

| model | free parameters | what it can do (from C1) |
|---|---|---|
| ΛCDM (psi = 0) | Ωm, plus nuisance | w = −1 |
| UET family | Ωm, psi_i, m/H0, xi_c, plus nuisance; xi_c restricted to the region Cassini, LLR and T001 allow today | thawing: w0 ≥ −1 in every allowed run; with xi_c > 0 a phantom phase only in the past, ending at z ≈ 1.5 to 2.2 |
| CPL comparator | Ωm, w0, wa, plus nuisance | any linear w(a), including a crossing of w = −1 at low z |

Nuisance parameters: h·r_d for uncalibrated BAO and the SN absolute magnitude M, both analytically marginalised.
No CMB information in the primary test (see option B).

## Data (needs the author's permission to download)

| data_id (proposed) | content | source | approx. size |
|---|---|---|---|
| DESI_DR2_BAO | DESI DR2 Gaussian BAO means (D_M/r_d, D_H/r_d, D_V/r_d at 7 redshift bins) and covariance | `CobayaSampler/bao_data` on GitHub, folder `desi_bao_dr2` (two text files) | about 2 KB |
| SN compilation, one of: | | | |
| PANTHEON_PLUS | Pantheon+ Hubble diagram (1701 light curves) and STAT+SYS covariance | `PantheonPlusSH0ES/DataRelease` on GitHub | about 0.5 MB + about 30 MB |
| DES_SN5YR | DES 5-year Hubble diagram and covariance | `des-science/DES-SN5YR` on GitHub | about 0.5 MB + about 30 MB |

Which SN compilation to use is the author's choice. The published results differ between them, so the choice must be
made before the run and not changed afterwards.

## Method

1. For each model compute D_M(z), D_H(z) = c/H(z) and the SN distance modulus from H(a). For the UET family, H(a)
   comes from `uet_frw_background.py` (radiation neglected; it is below 1e-3 of H^2 at z < 2.5).
2. χ²_BAO uses the DESI covariance with h·r_d free. χ²_SN uses the compilation covariance with M free.
3. Minimise χ² = χ²_BAO + χ²_SN for each model. The UET minimisation runs over a grid (psi_i, m/H0, xi_c), keeping only
   points allowed by Cassini, LLR and T001 today. Ωm and the nuisance parameters are profiled at each grid point.
4. Report Δχ²_CPL = χ²_min(UET) − χ²_min(CPL), Δχ²_ΛCDM = χ²_min(ΛCDM) − χ²_min(UET), and the UET best-fit (w0, wa).

## Proposed criteria (to be fixed by the author before the data are opened)

- PASS if Δχ²_CPL ≤ 4: the action's family fits as well as a free linear w(a) to within about 2σ for 2 parameters.
- FAIL if Δχ²_CPL > 9: the data need an expansion history the action cannot produce at more than about 3σ.
- INCONCLUSIVE in between.
- Reported, not deciding: Δχ²_ΛCDM, the UET best-fit (w0, wa), and the result with the other SN compilation.

## Option B (needs another download and more code)

Add a compressed CMB prior (for example the Planck 2018 shift parameters R, l_A, ω_b). This needs radiation and r_d
from the model, and the early G_eff = G/F(psi_i). It makes the test sharper, because most of the published preference for
evolving dark energy uses the CMB. It is not part of the primary test unless the author chooses it.

## Disclosure (the test is not blind)

- The drafter knows from the literature that DESI DR2 BAO combined with CMB and SN data was reported to prefer
  w0 > −1 and wa < 0 in the CPL fit at roughly 2.8 to 4.2σ, depending on the SN compilation. It also knows that the
  CPL best fit crosses w = −1 near z ≈ 0.4 to 0.5.
- C1 found that the UET family has w0 ≥ −1 and phantom phases only at z > 1.5. The drafter therefore expects the
  action to be unable to follow a low-z crossing. Without the CMB, the published preference is weaker, so the primary
  test (option A) may be INCONCLUSIVE.
- None of the comparison numbers above were used to build or tune the model. The model's parameters were never fitted
  to these data.
