# Correcting CCBH Selection Bias with Galaxy Stellar Mass Ratios

Your k = -1.5 result from raw M_BH data is a textbook case of **Malmquist bias**—luminosity-selected samples preferentially detect more massive black holes at higher redshift, creating artificial anti-correlation. The solution is the M_BH/M_galaxy ratio method used by Farrah et al. (2023), which cancels distance-dependent selection effects and recovered **k = 3.11 ± 1.19** for elliptical galaxies. However, critical implementation details require attention: most Shen 2011 quasars are classified as "QSO" not "GALAXY" in SDSS, meaning they won't appear in MPA-JHU, and recent JWST data at z > 4.5 increasingly disfavors k ≈ 3.

## MPA-JHU DR7 stellar mass catalog access and specifications

The MPA-JHU DR7 catalog remains the standard reference for SDSS galaxy stellar masses, covering **927,552 galaxy spectra** with Bayesian SED-derived masses using Bruzual & Charlot (2003) models and Kroupa IMF.

**Primary download URLs (no registration required):**

- Main page: https://wwwmpa.mpa-garching.mpg.de/SDSS/DR7/
- Stellar masses: `totlgm_dr7_v5_2.fit.gz` (**16 MB**, recommended: use improved version at https://home.strw.leidenuniv.nl/~jarle/SDSS/DR7/totlgm_dr7_v5_2b.fit for z > 0.3)
- Galaxy info (RA, Dec, z): `gal_info_dr7_v5_2.fits` (**72 MB**)

**Critical columns:** Use `lgm_tot_p50` for median log stellar mass (log M_☉), with uncertainties from `lgm_tot_p84 - lgm_tot_p16` (2σ range, typically **~0.15-0.2 dex statistical**). Systematic uncertainties from IMF choice add ~0.2 dex; Kroupa-to-Chabrier conversion multiplies mass by 0.943.

**Alternative access:** SDSS CasJobs tables `galSpecInfo` and `galSpecExtra` contain identical data with SQL query capability. For z > 0.3 objects, the Leiden-hosted improved file corrects failures from poor u/z photometry.

## The quasar-galaxy matching problem requires specialized catalogs

Here is the critical issue: **most Shen 2011 quasars will NOT have MPA-JHU matches**. The MPA-JHU catalog contains objects classified as "GALAXY" by the SDSS pipeline, while quasars are classified as "QSO." Only low-z (z < 0.3), low-luminosity AGN where host galaxy light dominates might appear in MPA-JHU—expect **<1% match rate** for typical Type 1 quasars.

**Solutions for quasar host stellar masses:**

- **Mendel et al. (2014):** Provides separate bulge masses from 2D decomposition for ~660,000 DR7 galaxies (VizieR: J/ApJS/210/3). Bulge mass serves as proxy for the spheroidal component hosting the SMBH
- **Simard et al. (2011):** PSF-convolved bulge+disk decompositions with Sérsic indices for 1.12M galaxies (VizieR: J/ApJS/196/11)
- **Image/spectral decomposition:** For resolved quasar hosts, separate AGN and galaxy components using point-source + Sérsic fitting

**Recommended matching approach:** Use **1 arcsec** matching radius for SDSS-to-SDSS catalogs via `astropy.coordinates.match_coordinates_sky()`. For 100k × 900k catalog matching, astropy's KD-tree implementation handles this in under 30 seconds. Match on PLATEID-MJD-FIBERID for spectroscopic data or RA/Dec with 2-3" tolerance for photometric catalogs.

```python
from astropy.coordinates import SkyCoord, match_coordinates_sky
from astropy import units as u

quasar_coords = SkyCoord(ra=quasar_ra*u.deg, dec=quasar_dec*u.deg)
galaxy_coords = SkyCoord(ra=galaxy_ra*u.deg, dec=galaxy_dec*u.deg)
idx, d2d, _ = match_coordinates_sky(quasar_coords, galaxy_coords)
matches = d2d < 1.0*u.arcsec  # Expect very few matches for QSOs
```

## How the M_BH/M_galaxy ratio cancels selection bias

The mathematical elegance of the ratio method lies in how Malmquist bias affects both quantities proportionally. For luminosity-limited samples, observed masses scale with a distance-dependent selection function S(z):

**Observed:** M_BH,obs ∝ S(z) × M_BH,intrinsic; M__,obs ∝ S(z) × M__,intrinsic

Taking the ratio cancels S(z), leaving only intrinsic evolution. If cosmological coupling follows M_BH ∝ a^k (where a = 1/(1+z) is the scale factor) and stellar mass in passive ellipticals is essentially constant (k_star ≈ 0), then:

**log(M_BH/M_*) = k × log(1+z) + constant**

Fitting this relation to data at different redshifts directly yields k, free from distance-dependent selection effects. Farrah et al. found that SMBHs in elliptical galaxies grew by factors of **7-20×** between z ~ 1-2.5 and z ~ 0, while stellar masses remained constant—inconsistent with accretion but consistent with k ≈ 3 cosmological coupling.

**Error propagation:** σ²[log(M_BH/M__)] = σ²[log M_BH] + σ²[log M__] - 2×cov, though the covariance term is typically negligible for independent measurements.

## Elliptical galaxy selection requires multi-parameter cuts

Farrah et al. specifically selected **quiescent red-sequence elliptical galaxies** because SMBHs in these systems cannot grow via accretion or mergers, making any mass evolution a signature of non-standard physics. Implement this selection through layered criteria:

|Parameter|Threshold|Source|
|---|---|---|
|Concentration (C = R90/R50)|C > 2.6|SDSS petroR90_r/petroR50_r|
|Sérsic index|n > 2.5|Simard et al. 2011|
|Bulge fraction (B/T)|B/T > 0.5|Mendel et al. 2014|
|Galaxy Zoo vote|P_EL > 0.8|https://data.galaxyzoo.org/|
|Specific SFR|log(sSFR) < -11 yr⁻¹|MPA-JHU SPECSFR_TOT|
|Color|g-r > 0.7 or u-r > 2.6|Red sequence|

Galaxy Zoo 1 covers ~893,212 DR7 objects with debiased elliptical/spiral classifications. The MPA-JHU catalog provides BPT classifications where LINER (class 5) or unclassifiable (class -1) typically indicates quiescent systems. Combine morphological and star-formation criteria for robust quiescent elliptical selection.

## Published k values show tension between methods and redshifts

The landscape of k measurements reveals significant disagreement:

|Study|k Value|Sample|Key Constraint|
|---|---|---|---|
|**Farrah et al. 2023**|3.11 ± 1.19|Elliptical SMBHs, z ≲ 2.5|k=0 excluded at 99.98%|
|Croker et al. 2021|~0.5|LIGO-Virgo mergers|Stellar-mass BHs|
|Rodriguez 2023|k > 2 disfavored|NGC 3201 cluster BHs|~1/2000 probability|
|Andrae & El-Badry 2023|k=3 disfavored|Gaia BH1, BH2|93% confidence against|
|**Lei et al. 2024**|-0.03 ± 1.33|JWST AGN, z ~ 4.5-7|2σ against k=3|
|Amendola et al. 2024|k < 2.1|LVK gravitational waves|2σ upper limit|

**Critical discrepancy:** JWST observations at z > 4 find "overmassive" black holes—the opposite of CCBH predictions. If M_BH ∝ a^k with k = 3, high-z BHs should have **lower** M_BH/M_* ratios than local ones, but JWST finds ratios **~55× higher** at z ~ 5 (Pacucci & Loeb 2024). This tension is reinforced by a June 2025 analysis rejecting k = 3 at ~11σ using JWST little red dot descendants.

## Practical implementation pathway for 1-3 day timeline

**Day 1: Data acquisition and sample selection**

1. Download MPA-JHU files and Shen 2011 catalog (VizieR: J/ApJS/194/45)
2. Download Mendel et al. 2014 for bulge masses
3. Cross-match catalogs—identify the small subset with both QSO classifications AND resolved host photometry
4. Apply elliptical/quiescent selection cuts (concentration, Sérsic n, sSFR, color)

**Day 2: Analysis implementation**

1. Compute log(M_BH/M_*) for each matched object
2. Bin by redshift or use continuous fitting
3. Fit: log(M_BH/M_*) = k × log(1+z) + c using least squares or Bayesian framework (emcee/dynesty)
4. Bootstrap or MCMC for uncertainty estimation

**Day 3: Validation and systematics**

1. Compare to local M_BH-M_* relation (Kormendy & Ho 2013)
2. Check for systematic offsets in morphological subsamples
3. Validate that selection criteria match across redshift bins

**Common failure modes to avoid:**

- Using raw M_BH without M_* normalization (causes your k = -1.5)
- Including actively accreting AGN or star-forming hosts
- Not matching host galaxy properties across redshift bins
- Ignoring the classification mismatch between QSO and GALAXY catalogs

## Expected outcomes after proper correction

If your sample genuinely traces CCBH physics and you've correctly selected quiescent elliptical hosts, the M_BH/M_* method should shift k from -1.5 to **positive values**. Whether you recover k ≈ 3 (Farrah et al.) or k < 2 (gravitational wave/JWST constraints) depends on your sample properties and redshift range.

For z < 2.5 elliptical galaxies following Farrah methodology, expect k ~ 2-4. However, be aware that the CCBH interpretation remains contested: theoretical objections question whether cosmological coupling can occur within gravitationally bound systems (Avelino 2023, Wang & Wang 2023), and stellar-mass BH observations systematically prefer lower k values.

**Key references:** Farrah et al. 2023 ApJ 943, 133 (methodology) and ApJL 944, L31 (k measurement); Mendel et al. 2014 ApJS 210, 3 (bulge masses); Lei et al. 2024 Sci. China Phys. Mech. Astron. 67, 229811 (JWST constraints).

## Conclusion

The path from k = -1.5 to an unbiased measurement requires three essential corrections: (1) switching from raw M_BH to the M_BH/M_* ratio, (2) restricting to quiescent elliptical hosts where stellar mass is stable, and (3) ensuring consistent sample selection across redshift. The MPA-JHU catalog provides stellar masses, but for quasar hosts specifically, you'll need Mendel et al. bulge decompositions or dedicated AGN-host separation—most QSOs aren't in galaxy catalogs. While Farrah et al. found k = 3.11 supporting the dark energy connection, accumulating evidence from stellar-mass BHs and high-z JWST data increasingly favors k < 2, suggesting your final result may depend critically on sample properties and redshift range examined.