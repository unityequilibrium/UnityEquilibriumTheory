# Homogeneous classical-Phi Hartree stationary candidate

MAJOR_RESULT_CLOSURE: `T13_HOMOGENEOUS_CLASSICAL_PHI_HARTREE_STATIONARITY`, `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The mass-dependent homogeneous normalization has a derived Phi force/curvature counterterm. Two matter/Phi stationary states are solved with the original action trial inputs. Their mixed static Hessian agrees between covariance differentiation, an actual independent source bubble, reoptimized potential differences and the radially relaxed force derivative.

WHAT_REMAINS_OPEN: Joint finite-q retarded response, quantum Phi fluctuations/kinetic counterterms, global phase/stability, controlled Hartree remainder and full regulator/RG matching; independent material/state/source/detector/temperature input, heat/collision/Kubo/SK-KMS/entropy transport. These are not supplied by static positivity.

DEPENDENCY_UNLOCKED: Named homogeneous classical-Phi candidate research only, not a physical/Core unlock or full R1/Goal acceptance. The fixed-Phi branch and the Core owner's separate composition gate are unchanged.

STATUS: `PASS_SCOPED_JOINT_PHI_STATIC` in [machine-readable evidence](t13_hartree_joint_phi_static.json), SHA-256 `e73c0ea5f41fd38053a46db2b61c894a44bba38566d884d1e94b9eab4b3a10ba`.

WHAT_CHANGED: New topic-local diagnostic branch `t13.candidate.classical_phi_hartree_ms_homogeneous_v1`, parent `t13.candidate.fixed_phi_hartree_ms_finite_potential_v1`. Phi is now solved as a classical stationary background, not the fixed .15 input. No Core equation was edited or promoted.

EQUATION_OR_MAPPING:

## Same-action normalization and force

Use canonical O(2) amplitude `v`, with `s=v^2`, not collective UET C or a signed charge. Existing UET Phi is distinct from the O(2) field and any 2PI functional. The natural action lane has Phi, T, mu and gamma in E; s/a/b/m2/D2 in E^2, u/D/epsilon/Z dimensionless, potential in E^4, Phi force in E^3 and joint static curvature in E^2. This is not the normalized TTG lane or SI alpha calibration.

The original trial action gives Z=1, m0^2=1, u=1, gamma=epsilon*h/Z=.04, epsilon=.05, Phi_*=0, m_Phi^2=1 and lambda_Phi=1:

```text
x=Phi-Phi_*
m2(Phi)=m0^2-gamma*x
V_R(Phi)=epsilon*(m_Phi^2*x^2/2+lambda_Phi*x^4/4)
A=u/[(1+2uD)(1+4uD)]
B=u/(1+2uD), A+B=2u/(1+4uD)
delta=m2-m_ref^2, d=D2+delta*D
N=L0+delta*D2+delta^2*D/2-(A+B)*d^2
dm_b^2/dPhi=-gamma/(1+4uD)
N_Phi=-gamma*d/(1+4uD)
N_PhiPhi=gamma^2*D/(1+4uD)
V_b=V_R-N
```

D/D2 are formal algebra probes, not a physical UV regulator. Differentiate with fixed renormalized action inputs and reference scale; no target curve selects a counterterm. The predecessor normalization was constant only at fixed Phi and cannot be dropped when m2 varies.

For arbitrary finite signed tadpoles the predecessor affine map implies:

```text
s+T1+T2=(1+4uD)*(s+I1+I2)+2d
bare_matter_force=-(gamma/(1+4uD))*(s+T1+T2)/2
bare_matter_force=-gamma*(s+I1+I2)/2+N_Phi
V_b'+bare_matter_force=V_R'-gamma*(s+I1+I2)/2
```

Exact rational polynomial differentiation independently checks N_Phi, N_PhiPhi and the bare mass slope. Dropping N leaves a nonzero force difference; the negative control detects it. The identity is homogeneous/on-gap, not a complete quantum or off-gap renormalized action.

## Actual jointly stationary states

Solve the following four equations, with s/a/b positive via log variables and Phi unrestricted. `r=mu^2-m2(Phi)>0` defines the declared condensed chart; no branch or mass repair is used:

```text
-r+u*s+u*(3I_s+I_p)=0
a+r-3u*s-u*(3I_s+I_p)=0
b+r-u*s-u*(I_s+3I_p)=0
V_R'(Phi)-gamma*(s+I_s+I_p)/2=0
```

Numerical root residual scales are E^2 for the matter equations and `epsilon*Q^3` (E^3) for Phi force, with Q=MS_scale=1 E. Changing root seeds is not adjusting action coefficients. At T=.22 E:

| mu (E) | s (E^2) | a (E^2) | b (E^2) | Phi (E) | Minimum amplitude/Phi static eigenvalue (E^2) |
| --- | --- | --- | --- | --- | --- |
| 1.05 | .112290015174 | .224580030348 | .009544230990 | .044179631621 | .049207287079 |
| 1.20 | .450914914828 | .901829829655 | .012467242445 | .175433844597 | .053775951283 |

The old fixed-Phi=.15 states have nonzero joint forces .005367977008 and -.001352772227 E^3. They remain valid fixed-background witnesses, not joint stationary states. Their internal phase gap b stays nonzero; the external static Ward limit is checked independently.

## Independent mixed-source response

Let J2=partial(I_s,I_p)/partial(a,b), H=[[3,1],[1,3]] and K2=uH. Differentiating the covariance gaps gives:

```text
mass_s=(I-K2*J2)^-1*u*(3,1)
mass_m2=(I-K2*J2)^-1*(1,1)
H_vv=2s*[u+u*(3,1)*J2*mass_s]+field_bracket
H_vPhi=-gamma*sqrt(s)*[1+u*(3,1)*J2*mass_m2]
H_PhiV=-gamma*sqrt(s)*[1+(1,1)*J2*mass_s]
H_PhiPhi=V_R''+gamma^2/2*(1,1)*J2*mass_m2
H_Phi_relaxed=H_PhiPhi-H_PhiV*H_vPhi/H_vv
```

Independently compute the actual three-channel source bubble J3 at q=z=0 with the predecessor spectral integration, not a numerical derivative of tadpoles. The new mass-source insertion is `L_Phi=(-sqrt(2)*gamma,0,0)`. With L_joint=(L_radial,L_Phi):

```text
Gamma_joint=[[a,-gamma*sqrt(s)],[-gamma*sqrt(s),V_R'']]
            +L_joint^T*J3*(I-K3*J3)^-1*L_joint/2
```

This matches H and the reoptimized potential Hessian. Reoptimizing matter at Phi+/-h also matches the Schur-complement relaxed curvature; freezing amplitude would miss that term. Positive amplitude/Phi static eigenvalues are local static evidence only, not finite-q dynamical stability or a global minimum. O(2) phase marginality is excluded from this two-variable positivity statement.

VERIFICATION: Fourteen artifact checks. Algebra 1e-10, scaled roots 1e-8, state refinement 1e-5 and Hessian agreement 2e-5 are declared unchanged. Orders/splits 128/20,192/40,256/64; seeds .8/1.2; source-loop orders 96/144/192; difference steps .002/.001/.0005 Q. Maximum final state refinement 9.454e-9, seed difference 9.357e-14, independent source-Hessian disagreement 4.202e-9, reoptimized potential-Hessian disagreement 2.167e-6 and relaxed-force curvature disagreement 1.25e-8. Protected Core/baseline hashes match. The audit reads derived predecessor artifacts and action code, not experimental rows or Xie. Eighteen independent tests cover exact rational algebra, signed tadpoles, decoupling, units, invalid domains, roots/source/potential/Schur checks and read/hash/claim boundaries; regression execution is recorded in UPDATE_LOG, not inferred from this note.

CONTROLLING_BLOCKER: `joint_dynamic_validity_regulator_remainder_material_transport_not_closed`.

NEXT_ACTION: Construct same-action joint retarded response and validity/approximation obligations; build the independent material/source/readout measurement card. Do not reuse old fixed-Phi poles as joint poles. Preserve 7 October science freeze and 11 October portfolio review; the D5 methods-route decision remains planning, not accepted scientific delivery.

CLAIM_BOUNDARY: Homogeneous classical-Phi Hartree trial candidate only. No quantum Phi loops, full covariant counterterms/RG, global proof or controlled Hartree remainder; no SI alpha, physical sound/heat/collision/Kubo/SK-KMS/entropy, material prediction, external validation, novelty certification or Full Topic13/UET closure. No fitting, clipping, filters, mass repair, threshold changes or R_gen/R_obs dynamics. Prior Xie context exposure remains REVIEW_REQUIRED with no new numeric access. Existing Core composition is not overwritten.
