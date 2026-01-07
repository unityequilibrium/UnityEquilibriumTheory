# Cosmologically Coupled Black Holes: Selection Bias, Information Theory, and the k Parameter

Black holes that grow with cosmic expansion remain among the most contested ideas in contemporary astrophysics. The Cosmologically Coupled Black Hole (CCBH) hypothesis—proposing that black hole masses scale as **M_BH ∝ a^k** where a is the cosmological scale factor—faces a critical juncture in late 2025. While Farrah et al. (2023) reported k ≈ 3.11 from supermassive black holes in elliptical galaxies, multiple independent constraints from gravitational wave observations, Gaia astrometric binaries, and JWST high-redshift data now disfavor k = 3 at **2σ–4σ significance**, with one recent analysis claiming >10σ rejection. Yet theoretical developments, particularly Faraoni & Rinaldi's 2024 proof that static horizons cannot exist in expanding spacetime, provide surprising support for some form of cosmological coupling being physically necessary.

---

## Selection bias creates systematic distortions but cannot fully explain observed signals

Malmquist bias—the preferential detection of intrinsically luminous objects in flux-limited surveys—constitutes the primary systematic concern for CCBH measurements. The classical formulation establishes that mean observed absolute magnitude shifts from the true population mean by **ΔM = 1.38σ²**, where σ is the luminosity dispersion. For quasar surveys with typical black hole mass scatter of σ ≈ 0.4–0.5 dex, this translates to systematic overestimation of **0.25–0.4 dex** in log(M_BH).

The SDSS DR7 quasar catalog (Shen et al. 2011), containing **105,783 quasars**, exhibits well-characterized selection effects. The survey becomes significantly incomplete below M_BH < 3×10⁸ M☉ and Eddington ratios L/L_Edd < 0.07. Lauer et al. (2007) demonstrated an additional compounding effect: when comparing high-redshift AGN samples (selected by nuclear luminosity) to local samples (selected by host galaxy properties), scatter in the M_BH-σ and M_BH-L relations creates apparent evolution of factors **3–9×** in black hole mass—purely from statistical selection.

Quantitative modeling suggests selection bias alone could produce apparent coupling with **k ≈ 0.6–1.0** between z = 0 and z = 2. This falls well short of the k ≈ 3 claimed by Farrah et al., suggesting selection effects cannot fully explain the observed signal if it is real. However, resolution-dependent selection in local dynamical samples may partially counteract high-redshift biases, potentially reducing net systematic effects in some sample configurations.

### Physical versus observational selection remains speculative

The question of whether selection bias has a "physical" component—beyond purely instrumental effects—connects to information-theoretic considerations. Objects dissipating more energy (higher luminosity) are necessarily more observable; this is tautological for flux-limited samples but could reflect deeper thermodynamic principles. Landauer's principle establishes that erasing one bit of information requires minimum energy **E_min = k_B T ln(2)**, directly linking observability to thermodynamic irreversibility.

Recent work by Cortês & Liddle (2024) demonstrates that black holes saturate the Landauer limit exactly in Hawking radiation—they erase information at maximum thermodynamic efficiency. However, no rigorous theoretical framework currently connects CCBH interior physics to electromagnetic observability. Standard selection effects are well-explained by purely observational considerations without invoking fundamental physics.

---

## Information storage in spacetime connects entropy to cosmological dynamics

The Bekenstein-Hawking entropy formula **S = A/(4ℓ_P²)** establishes that black hole entropy—and thus information storage capacity—scales with horizon area rather than enclosed volume. For a solar-mass black hole, this yields approximately **10⁷⁷ bits** of information capacity, roughly 10⁶⁶ bits per cm² of horizon area. This counterintuitive area-scaling underlies the holographic principle proposed by 't Hooft (1993) and Susskind, suggesting spacetime itself functions as an information storage medium.

Edward Witten's December 2024 review (arXiv:2412.16795) provides comprehensive coverage of black hole thermodynamics, emphasizing the **Ryu-Takayanagi formula** S_A = Area(γ_A)/(4G_N) which generalizes Bekenstein-Hawking entropy to arbitrary boundary regions in holographic contexts. The review discusses how Euclidean path integrals with imaginary time periodicity determine Hawking temperature T_H = ℏc³/(8πGMk_B), establishing the deep connection between spacetime geometry and thermodynamics.

The black hole information paradox—whether information is destroyed during evaporation—has seen substantial progress through the "island formula" developed in 2019–2024:

**S(R) = min[ext(Area(∂I)/(4G) + S_matter(R ∪ I))]**

This formalism shows that gravitational entropy calculations are consistent with unitary evolution, recovering the expected Page curve where radiation entropy increases to a maximum at the "Page time" then decreases as the black hole evaporates. Extensions to Kerr (rotating) and Reissner-Nordström (charged) black holes were completed in 2024, demonstrating the framework's generality.

### Vacuum energy and holographic dark energy models face observational constraints

The cosmological constant problem—a **50–120 order of magnitude** discrepancy between observed vacuum energy (ρ_vac ≈ 5.96 × 10⁻²⁷ kg/m³) and QFT predictions—motivates holographic dark energy models where ρ_DE ~ M_P²/L² with L an infrared cutoff. The Cohen-Kaplan-Nelson bound provides UV-IR connection that yields estimates compatible with observations. However, most generalized entropy models (Barrow, Tsallis, Kaniadakis modifications) remain statistically disfavored compared to ΛCDM when tested against Pantheon supernovae, BAO, and cosmic chronometer data.

---

## Practical methods for correcting selection bias offer multiple complementary approaches

The **V/Vmax method** (Schmidt 1968) provides an unbiased luminosity function estimator by weighting each object by the inverse of the maximum observable volume:

**Φ(M)ΔM = Σ[1/V_max,i]**

For each object with absolute magnitude M_i at redshift z_i, one computes z_max—the maximum redshift where the object remains above the survey flux limit. The key relation is:

**z_max = z where: M_i + DM(z_max) + K(z_max) = m_lim**

A complete sample yields ⟨V/V_max⟩ = 0.5; deviations indicate incompleteness or cosmic evolution. Implementation for CCBH analysis requires computing V_max for each quasar based on SDSS flux limits, then applying volume-weighted least-squares fitting to M_BH/M_* ratios across redshift bins.

### SDSS stellar mass catalogs enable M_BH/M_galaxy approaches

The **MPA-JHU DR7 catalog** (available at wwwmpa.mpa-garching.mpg.de/SDSS/DR7/) provides stellar masses for 927,552 galaxy spectra using Bayesian fits to ugriz photometry with Bruzual & Charlot 2003 models. The catalog includes both fiber and total stellar masses, with systematic uncertainties of ~0.1–0.2 dex. The Mendel et al. (2014) bulge+disk decomposition catalog offers separate bulge and disk stellar mass estimates, showing ~0.02 dex offset from MPA-JHU masses.

Farrah et al. (2023) specifically avoided selection bias by restricting analysis to **quiescent elliptical galaxies**—systems with minimal ongoing star formation where SMBHs cannot grow via accretion. This controls for:

- Accretion-driven growth (gas-poor environments)
- Merger-driven growth (stable elliptical morphology)
- Selection effects related to AGN activity (no nuclear luminosity selection)

Their Bayesian analysis found stellar mass offsets consistent with measurement bias (small) but SMBH mass offsets of factors **7–20** (too large for bias alone), yielding k = 3.11 ± 1.19 and excluding k = 0 at 99.98% confidence.

---

## Theoretical derivation establishes k = 3 for vacuum energy interiors

The fundamental relationship between k and the interior equation of state w emerges from energy conservation:

**k = −3w**

This follows from the continuity equation for a fluid with p = wρ, giving ρ ∝ a^(−3(1+w)). For black holes with number density n ∝ a⁻³ and mass M ∝ a^k, the physical mass density becomes ρ_BH = nM ∝ a^(k−3) = a^(−3(1+w_eff)), yielding k = −3w_eff.

|Interior Equation of State|k Value|Physical Interpretation|
|---|---|---|
|w = 0|k = 0|Standard Kerr BH (no coupling)|
|w = −1/3|k = 1|Comoving scenario|
|**w = −1**|**k = 3**|**Vacuum energy interior**|
|w < −1|k > 3|Phantom energy (causally forbidden)|

For **k = 3**, the black hole mass density ρ_BH = nM ∝ a⁻³ × a³ = constant—exactly mimicking a cosmological constant Λ. The physical mechanism proposed by Croker & Weiner (2019) involves black holes containing vacuum energy (de Sitter-like) interiors rather than singularities, with boundary conditions matched to FLRW (not Minkowski) spacetime at infinity.

### DESI 2024 results hint at evolving dark energy with implications for k

DESI DR1 (April 2024) found hints that dark energy may not be a pure cosmological constant. Using the CPL parameterization w(a) = w₀ + w_a(1−a):

- DESI + CMB + DES-SN5YR: **3.9σ preference** for evolving dark energy over ΛCDM
- Best-fit values suggest w₀ > −1 and w_a < 0

If w evolves with time, k would also evolve: **k(a) = −3[w₀ + w_a(1−a)]**. For w₀ ≈ −0.8 to −0.9 (as suggested by DESI), present-day k ≈ 2.4–2.7, below the canonical k = 3. DESI DR2 (December 2024/March 2025) strengthened evidence for dynamical dark energy.

Croker et al. (2024, JCAP 10, 094) showed that the CCBH model naturally recovers DESI's evolving dark energy signature, producing H₀ = 69.94 ± 0.81 km/s/Mpc and reducing Hubble tension with SH0ES to 2.7σ.

---

## Multiple independent observations now challenge k = 3

### Gravitational wave constraints

Amendola et al. (2024, MNRAS 528, 2377) tested CCBH using LIGO-Virgo-KAGRA binary black hole mergers, finding:

- k = 3 produces **3.7σ tension** with standard delay time distributions
- Constraint: k < 2.1 at 2σ (standard delay model)
- Constraint: k < 1.1 at 2σ (CCBH-corrected delay model)
- O4 run data (250 events) projected to reject k = 3 at >5σ if tension persists

### Stellar-mass black hole constraints

Rodriguez (2023, ApJL 947, L12) analyzed NGC 3201 globular cluster black holes, finding k = 3 would require formation masses below the Tolman-Oppenheimer-Volkoff limit—disfavoring k = 3 at **3.8σ**. Andrae & El-Badry (2023) used Gaia BH1 and BH2 astrometric binaries to constrain k, finding 77% probability that Gaia BH2 would have formed below the TOV limit if k = 3.

### JWST high-redshift observations

Lei et al. (2025, arXiv:2506.19589) claim JWST very high-redshift AGN data rejects black holes as a dark energy source at **>10σ confidence**. The argument centers on "Little Red Dots" (compact high-z AGN) naturally evolving into elliptical galaxy SMBHs at z ~ 0.7–2.5 without requiring cosmological coupling—alternative explanations including heavy seeds and super-Eddington accretion can explain JWST observations.

### Accretion budget constraint

Lacy et al. (2024, ApJL 961, L33) compared z = 0 SMBH mass density to total accreted mass since z = 6, constraining k ≲ 2 under standard accretion efficiency assumptions. However, if higher SMBH mass density from pulsar timing arrays (~7.4 × 10⁶ M☉ Mpc⁻³) is adopted, k = 3 becomes marginally viable.

---

## Theoretical criticisms remain partially unresolved

Mistele (2023, arXiv:2304.09817) raised a fundamental objection: the Croker & Weiner derivation allegedly confuses the principle of least action by restricting variations to homogeneous perturbations before deriving equations of motion. No direct published rebuttal addresses this specific criticism.

Wang & Wang (2023, arXiv:2304.01059) argued that junction conditions in GR prevent gravitationally bound systems from "feeling" cosmological expansion. However, Faraoni & Rinaldi (2024, PRD 110, 063553) directly contradicted this, proving that an exactly static, spherically symmetric black hole event horizon **cannot be embedded in time-dependent geometry** without creating naked null singularities. Since the universe is expanding, some form of cosmological coupling appears theoretically necessary.

Cadoni et al. (2023–2024) showed that if black holes are singularity-free objects within GR, they necessarily couple to cosmological dynamics—but the leading contribution yields k = 1, not k = 3. This suggests standard nonsingular GR black holes are "unlikely to be the source of dark energy."

---

## Cross-cutting synthesis reveals deeper connections

### Information theory and selection bias show limited connection

The search for a "physical" component to selection bias—rooted in thermodynamic energy dissipation and information preservation—remains speculative. While Landauer's principle establishes fundamental connections between information erasure and energy dissipation, and black holes appear to saturate this limit exactly, no rigorous framework connects CCBH interior physics to electromagnetic observability. Standard Malmquist-type biases are well-explained by purely observational considerations.

### Thermodynamic principles underlie both k derivation and information storage

The k = −3w relationship emerges directly from energy conservation and the first law of thermodynamics applied to expanding spacetime. Similarly, Bekenstein-Hawking entropy as information storage follows from thermodynamic considerations (horizon area theorem). Both frameworks suggest deep connections between gravity, thermodynamics, and information—consistent with Wheeler's "it from bit" paradigm—but the specific mechanism connecting vacuum energy coupling to black hole mass growth remains theoretically contested.

### Current scientific consensus

The CCBH hypothesis remains **highly controversial** with significant observational challenges:

- **Arguments for CCBH:** Faraoni & Rinaldi (2024) theoretical support; DESI evolving dark energy naturally explained; original Farrah et al. observation not definitively ruled out; physical mechanism (k = −3w) well-grounded in thermodynamics
- **Arguments against CCBH:** NGC 3201 constraints (3.8σ); GW observations (3.7σ); Gaia BH constraints; JWST claims (>10σ); unresolved action principle criticism; alternative explanations for high-z overmassive black holes (heavy seeds, super-Eddington accretion)

The 2024–2025 observational landscape has substantially weakened the case for k = 3 specifically, while theoretical developments paradoxically strengthen arguments that _some_ form of cosmological coupling should exist. The emerging picture suggests k may be closer to 1 than 3—sufficient to require cosmological coupling but insufficient for black holes to constitute dark energy.

## Conclusion

Cosmologically Coupled Black Holes represent a fascinating intersection of general relativity, thermodynamics, and observational cosmology. The theoretical derivation of k = 3 from vacuum energy interiors is mathematically sound, resting on the fundamental relation k = −3w. However, multiple independent observational constraints—from gravitational waves, stellar-mass black holes, and high-redshift JWST data—now disfavor k = 3 at 2–4σ or greater significance.

The practical tools for testing CCBH are mature: V/Vmax corrections, MPA-JHU stellar mass catalogs, and Farrah-style elliptical galaxy samples offer rigorous approaches to controlling selection bias. The key question has shifted from "Is there cosmological coupling?" to "What is the actual value of k?" Faraoni & Rinaldi's 2024 result suggests some coupling may be theoretically necessary, but the dark-energy-producing k = 3 scenario faces mounting challenges. DESI's evolving dark energy hints provide intriguing circumstantial support, yet the weight of stellar-mass black hole constraints points toward k ≲ 2—a coupling too weak to explain cosmic acceleration but potentially sufficient to resolve other cosmological anomalies.