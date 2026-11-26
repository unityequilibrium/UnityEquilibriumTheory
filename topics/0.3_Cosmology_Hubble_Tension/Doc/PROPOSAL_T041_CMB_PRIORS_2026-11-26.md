# Proposal T041: the parent action's dark energy with the CMB added

Drafted by Claude on 2026-11-26. Option B of T040. Status: draft for the author's approval.

## Question

T040 found the thawing psi of the parent action fits DESI DR2 BAO and Pantheon+ as well as a free linear w(a)
(dchi2 = 0.03, no CMB). Does that survive once the CMB acoustic scale is added?

## Mainstream context

- DESI DR2 (arXiv:2503.14738) reports that BAO with CMB and supernovae prefers CPL with w0 > -1 and wa < 0 over
  LambdaCDM at about 2.8 to 4.2 sigma depending on the supernova set, and that the CPL best fit crosses w = -1.
- Thawing quintessence cannot cross w = -1; the parent action's minimal-coupling family is of that kind (C1). With
  xi_c > 0 it has phantom phases, but only at z > 1.5 (C1). Extended quintessence is the nearest theory.
- Compressed CMB likelihoods (shift parameter R, acoustic scale l_A, omega_b) are the standard light way to add the
  CMB to a background test; Chen, Huang & Wang (2019) give them for Planck 2018 and validate them for wCDM and CPL.

## Models and numbers already known

- C2 (this repository): at fixed densities the thawing family moves theta* from LambdaCDM by +0.6% to +1.6%; Planck
  measures it to about 0.03%, so the CMB constrains the densities and the dark-energy history jointly.
- T040: dchi2_CPL = 0.03, dchi2_LCDM = 5.1 without the CMB.

## Data

Chen, Huang & Wang (2019), arXiv:1808.05724v1 TeX source (downloaded with the author's permission, kept local because
the arXiv licence does not allow redistribution; sha256 in the data manifest). BAO and SN files as in T040.

## Method

As in the card: LCDM, CPL and the UET grid of T040 fitted to BAO + SN + CMB, with omega_b and omega_m free, the BAO
amplitude and SN offset profiled, and the bounds of today applied to every UET point. Run time about 3 hours.

## Proposed criteria

Same as T040: PASS if dchi2_CPL <= 4, FAIL if dchi2_CPL > 9, INCONCLUSIVE otherwise.

## What is an AI choice

The compression (author's choice: Chen 2019), the use of its base LambdaCDM block, symmetrised errors, free BAO
amplitude, massless neutrinos, the release redshift and the grid. The drafter expects INCONCLUSIVE or FAIL (see the
card's disclosure).
