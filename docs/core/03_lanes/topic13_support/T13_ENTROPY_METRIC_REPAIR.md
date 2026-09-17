# Susceptibility entropy metric repair

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE; entropy normalization repaired in the declared finite-cutoff natural heat-only interface.
WHAT_IS_ACTUALLY_CLOSED: Both current divergence and collision dissipation use the same inverse-temperature factor. Heat flux, response matrix, collision operator and calibration are unchanged by this repair.
WHAT_REMAINS_OPEN: Frame/charge-diffusion mapping, action configuration agreement, physical Kubo/SK and material correspondence.
DEPENDENCY_UNLOCKED: No new physical unlock; historical composition remains awaiting review.
STATUS: INTERNAL_NORMALIZATION_REPAIRED.
WHAT_CHANGED: Corrected entropy_production and kinetic_entropy_production together, documented weighted coordinates in the existing contract, added independent Hessian/streaming tests and separate repair artifact. Frozen counterexample and original reference artifacts preserved.
EQUATION_OR_MAPPING: See derivation below; no new substance/state or material fit.
VERIFICATION: F0 inventory369/no duplicate IDs. Thirteen tests pass: Bose entropy Hessian, fixed-pressure streaming for both charges, four-temperature entropy-current divergence, preserved historical counterexample, and legacy matrix/conservation/covariance tests. Repaired reference sigma=1169.8766682851042; kinetic/current residual5.18689e-8 meets unchanged1e-7 gate. Kappa=257.3728670227229; difference from historical kappa is the preceding EOS revision, not this normalization repair.
CONTROLLING_BLOCKER: action_configuration_correspondence and hydrodynamic_frame_and_charge_diffusion_map.
NEXT_ACTION: Evaluate the corrected entropy interface with the SAME action configuration used for alpha/beta. Default entropy parameters have response_coupling=0 and epsilon_nc=0; alpha/beta use0.8 and0.05. Do not interpret equal coordinates as equal actions or change parameters to improve a fit.
CLAIM_BOUNDARY: Internal normalization closure, not full He4 closure, physical entropy-production measurement, microscopic collision validation or SI transport. Old artifact hashes intentionally remain historical; no full-gate rerun or blanket promotion.

## Derivation

The upstream basis constructs w_i=m_i f_i(1+f_i)/T, where m_i is a quadrature measure, not particle mass. Define the energy-like perturbation psi by delta f_i=f_i(1+f_i) psi_i/T and the weighted solver coordinate z_i=sqrt(w_i) psi_i. This makes the second-order negative Bose entropy increment

    sum_i m_i (delta f_i)^2/[2 f_i(1+f_i)] = z^T z/(2T).

For a fixed local background and dz/dt=-Lz, the corresponding quadratic collision entropy production is z^T Lz/T. The stored solver vector is z, not the literal occupation perturbation delta f. This agrees with the upstream continuum operator's already-declared formal entropy witness, which divides its quadratic form by T.

At constant local pressure and fixed Phi, Gibbs-Duhem gives grad(mu)=-(h-mu)grad(T)/T. Differentiating Bose equilibrium then gives the heat driving term proportional to [f(1+f)/T](E-h*q_species) v X, with X=-grad(T)/T. Thus no change of the existing heat source or flux is required for this normalization correction. In weighted coordinates, Lz=bX, j_Q=b^Tz, and sigma=z^TLz/T=X*j_Q/T. The heat-only rest-frame entropy-current divergence gives the same expression independently.

The projection and finite collocation are still model approximations. This local calculation does not prove full relativistic frame equivalence or a complete interacting collision entropy theorem. In particular, a physical Landau-frame current needs its charge-diffusion contribution explicitly mapped.

Correspondence: [Schianchi and Abalos, Lemma4 equations73-74](https://arxiv.org/pdf/2602.20254v3). No new literature or holdout data was consumed in this repair.
