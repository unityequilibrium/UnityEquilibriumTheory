# Binary-pulsar pilot: source packet (W5 → W6)

> Status: research notes for drafting Test Card `T001` (docs/STANDARD.md §4).
> This is not a result and does not change any claim's level.
> Every number below must be re-verified against the published version
> before T001 is approved.

## What is being mapped

- UET parent → DEF: `β₀ = −2 ξ_c` and `α₀ = 0` when ψ₀ = 0.
  Implementation: `02_equations/covariant/uet_scalar_tensor_mapping.py`.
  Physics tests: `05_tests/physics/test_def_mapping.py`.
- Spontaneous scalarization (DEF) needs β₀ around −4 or lower, i.e. **ξ_c of roughly 2 or more**.
- **Assumption required for the test:** ordinary matter (neutron stars and white dwarfs) couples minimally to the Jordan metric g.

## Sources consulted (2026-11-08, via the research index)

| ID | Source | What it says (paraphrased) | Use in T001 |
|---|---|---|---|
| ZFKSW22 | J. Zhao, P. C. C. Freire, M. Kramer, L. Shao, N. Wex, "Closing a spontaneous-scalarization window with binary pulsars", arXiv:2201.03771 (v2, 2022) | Combines 7 binary pulsars (J0348+0432, J0737−3039A, J1012+5307, J1738+0333, J1909−3744, J1913+1102, J2222−0137) with 13 EOSs (max mass > 2 M☉). Over the prior β₀ ∈ [−4.8, −4.0] it finds \|α_A\| ≲ 6×10⁻³ (90% CL) for neutron stars of every observed mass, which excludes spontaneous scalarization. The α₀ prior is log₁₀\|α₀\| ∈ [−5.3, −2.5]. | Main comparison. **Check the journal version.** |
| SSBKW17 | L. Shao, N. Sennett, A. Buonanno, M. Kramer, N. Wex, arXiv:1704.07561 (2017) | Earlier DEF bounds from 5 NS–WD systems and 11 EOSs; leaves "scalarization windows" open. | Context and cross-check. |
| DEF96 | T. Damour, G. Esposito-Farèse, Phys. Rev. D 54, 1474 (1996), arXiv:gr-qc/9602056 | Defines the T1(α₀, β₀) framework and the spontaneous scalarization phenomenon. | Defines the mapped parameters. |
| RP16 | F. M. Ramazanoğlu, F. Pretorius, arXiv:1601.07475 (2016) | A scalar mass term avoids the binary-pulsar bounds when the Compton wavelength is small compared with the binary separation. | Sets the validity domain: the bounds apply only when m_ψ is light enough. |

## Open questions for drafting T001 (author decisions)

1. **Mass domain:** the test applies only when 1/m_ψ ≫ the orbital separation of the binary pulsars (roughly 10⁹ m, so about m_ψ ≲ 10⁻¹⁶ eV). The exact threshold must be taken from RP16 or from the binary separations.
   If m_ψ is heavier than that, the test **does not apply**. Report that plainly; it is not a pass.
2. **What counts as "fail" or "pass":** this test is a `CONSTRAINT`, not a `BLIND_PREDICTION`.
   - The most likely outcome is that the region ξ_c ≳ 2 is excluded in the light-scalar domain.
   - This does not decide whether UET is right or wrong overall, because ξ_c is a free parameter.
   - The claim becomes `FAILED` only if the author fixes ξ_c in advance (for example from cosmology or another lane) and that value falls inside the excluded region.
3. **Data to record in `data_manifest.json`:** a small CSV of the published bounds (β₀ range, α_A limit, CL, EOS set, DOI) with its sha256.
   Do not redistribute the papers' figures or tables beyond what the citation needs.
