# Numeric Source Archive And Omitted-Term Measurement Boundary

MAJOR_RESULT_CLOSURE: Aggregate PARTIAL/FAIL_SCOPED_LOW_Q_SOURCE_BOUNDARY. Two subresults CLOSED_FOR_LANE: T13_GODFRIN_V1_NUMERIC_SOURCE_ARCHIVE and T13_Q4_ALIAS_AND_FOUR_NODE_SEPARATION. The original float64 control still fails; physical response/measurement/Goal acceptance is not established.

WHAT_IS_ACTUALLY_CLOSED: Versioned author numeric files are archived with byte hashes, units, source line/pressure row identities, missing values and ancestry. Exact algebra gives the omitted-q4 alias, its scaling, a constructive three-observation ambiguity and four-node separation within the declared four-term class, checked independently at80digits.

WHAT_REMAINS_OPEN: Same-state material/current/action normalization, full joint q/energy covariance, bounded non-tree remainder, source ancestry/version parity and practical measurement feasibility. For this response branch, thermal alpha/gain/heat/entropy/Kubo/KMS and nonlinear parent remain open. Core-owner's separate1.7K O(2)/He4 calibration is neither removed nor transferred here.

DEPENDENCY_UNLOCKED: Source-backed model-discrepancy and independent-scale research only. No physical/Core/Gravity/full-design/G2-G4/R1-R5/Goal or owner-composition promotion.

STATUS: [Artifact](t13_low_q_source_boundary.json), SHA256 `2c254806eb21b23dc282cbe30f052bf9af2376e427bc5c9b0de229d63f06945e`. Seven of eight original checks pass; independent_scaled_float_control fails. Two declared extension checks pass. [First failure](t13_low_q_source_boundary_first_failure.json) stays byte-identical, SHA256 `ba1acb4929d07a222476f4c0b0b0ca0684e9da17a86f3a6ea8438ac31a42982d`.

WHAT_CHANGED: Downloaded author ancillary files and supplement from arXiv2012.09067v1; new parser/estimator/protocol/tests preserve raw bytes and original failures. No target-curve calibration, source-window tuning, curve digitization, missing-cell replacement or UET action change.

## Attribution And Source Boundary

Credit H. Godfrin, K. Beauvois, A. Sultan, E. Krotscheck, J. Dawidowski, B. Fak and J. Ollivier, [author version](https://arxiv.org/abs/2012.09067v1), related DOI [10.1103/PhysRevB.103.104516](https://doi.org/10.1103/PhysRevB.103.104516). The arXiv record declares [CC BY4.0](https://creativecommons.org/licenses/by/4.0/); this archive does not redistribute the APS final paper. Source files are unchanged. Parsing/identifiers and the estimator diagnostic are repository derivatives, not author endorsement.

The [supplement](../../Data/03_Research/godfrin_2021_v1/Supplemental-v2.tex), lines570-589, identifies the files and units. AllPressures is a neutron table; P0 is ultrasound below.15 inverse angstrom, hybrid through.3, then neutron. P0 is not independent of AllPressures. Manuscript SectionsVI/VII.1 discuss correlated calibration and low-q systematics; equations2-4 include dispersion terms beyond the odd tree polynomial. Joint covariance and final-version parity are not supplied by these archived tables. Missing errors are not zero or assumed standard deviations. [Protocol/provenance](../../Data/03_Research/t13_low_q_source_protocol.json) records exact file URLs, hashes, roles and locators; no raw event data or numeric Xie acquisition.

EQUATION_OR_MAPPING: Introduce a measurement-discrepancy comparator, not a new UET state/action:

```text
E(q)=c*q+eta*q^3+b4*q^4+zeta*q^5
f(q)=E/q=c+eta*q^2+b4*q^3+zeta*q^4
```

For the predecessor's three-node weights W on powers(0,2,4), omitting b4 produces exactly delta_beta_k=b4*sum_i W_ki*q_i^3. At q=(a,a/2,a/4):

```text
delta_c    = -b4*a^3/90
delta_eta  =  7*b4*a/18
delta_zeta = 28*b4/(45*a)
```

Changing b4 by d and changing (c,eta,zeta) by minus these aliases leaves all three observations unchanged. This is a constructive one-dimensional ambiguity in this expanded measurement class. It does not contradict the predecessor's rank statement in the fixed odd-tree class. Lowering q makes the quintic contamination larger, not smaller, unless b4 is independently bounded or separately estimated. The old rational tree bound controls that tree, not an unknown b4.

For four distinct positive momenta, use V_ik=q_i^p_k with p=(0,2,3,4). The exact determinant is:

```text
detV = product_(i<j)(q_j-q_i) * e3(q)
e3(q) = sum_(i<j<k) q_i*q_j*q_k > 0
beta_hat=(c,eta,b4,zeta)=V^-1*(E_i/q_i)
```

Proof: the monic polynomial with the four q_i as roots gives q_i^4=e1*q_i^3-e2*q_i^2+e3*q_i-e4. In the determinant with columns(1,q^2,q^3,q^4), terms already spanned by the first three columns vanish; only e3*q remains. Reordering(1,q^2,q^3,q) into(1,q,q^2,q^3) has positive sign, yielding e3 times the usual Vandermonde. This proves rank4 for this class without fitting any physical coefficient. It is not an all-order or globally minimal experimental-design theorem.

Native b4:E^-3; physical source coefficients have units meV*angstrom^(1,3,4,5). Natural Phi:E, phase variable, collective C and thermal Kelvin maps remain distinct. Source interpolants are exposed coefficient estimates, not native I, physical asymptotic coefficients or predictions. Other possible terms, including an energy q2 contribution, are not proved absent; the four-term class is an explicit conditional example, not a complete physical expansion.

VERIFICATION: Three frozen control q maxima.02/.01/.005, beta=(1,2,3,-1) and four node ratios1/half/third/quarter. Exact Gaussian-elimination inverse/rank/alias identities pass. Scaled float64 inversion errors3.378e-8/5.627e-7/4.809e-5 fail the original1e-8 gate. An80-digit LU alternative, declared after that preserved failure and before its first run, has error<=9.675e-71 against1e-45. It does not repair binary64 or instrument precision. Source parser archives7350 pressure-row cells including232 missing pairs and1727 P0 energies with1693 missing errors; these views overlap, not9077 independent observations. Separators are counted, row line encodings/hashes retained. All selected physical windows, missing rows and hybrid/low-q ancestry remain; no source interpolation or physical I inversion. Tests cover scope/negative inputs/source hashes/runtime Path-read allowlist. Final linked test count belongs in UPDATE_LOG. Original causal1e-6 unchanged/not rerun.

CONTROLLING_BLOCKER: native_material_map_joint_covariance_and_non_tree_remainder_not_admitted. Float64 method FAIL remains a separate implementation boundary, not a physical inconsistency.

NEXT_ACTION: Bound/derive the non-tree dispersion terms and construct a same-state independent scale/current input packet before treating either q5 or independent-scale/q3 as material inference. Use the acquired numeric files for source-quality and exposed comparison work only. Do not transfer the old four certified tree budgets to this broader model or promote source acquisition to G4. Preserve7 October scientific freeze/11 October review and later R1-R5 dates.

CLAIM_BOUNDARY: Two bounded source/algebra subresults, aggregate PARTIAL with original FAIL retained. No detection of a physical q4 term by this audit, native calibration/alpha, intrinsic width, Kubo/KMS/heat/complete thermal bridge, necessary lab precision or global no-go. Higher remainders and covariance remain unknown. C is not charge/mass; R_gen/R_obs do not enter state. No physical/Core-owner gate, threshold, ontology or holdout-policy change; Xie exposure REVIEW_REQUIRED. Model trialNOT_RUN/settings unchanged; no new Goal/automation/contact/purchase/submission or publishing authorization.
