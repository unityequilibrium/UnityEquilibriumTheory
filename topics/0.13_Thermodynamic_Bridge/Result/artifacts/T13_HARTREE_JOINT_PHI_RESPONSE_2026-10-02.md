# Same-action classical-Phi joint retarded response

MAJOR_RESULT_CLOSURE: `T13_CLASSICAL_PHI_HARTREE_JOINT_RETARDED_RESPONSE`, `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: A joint source-responsive matter/classical-Phi Hessian with the original kinetic term, its quadratic counterterm cancellation, six newly computed local phase poles and static charge susceptibility after reoptimizing both matter and Phi. The clamped-Phi answer is not substituted.

WHAT_REMAINS_OPEN: Full-frequency/global spectrum and causal domain, regulator/RG and controlled Hartree approximation, quantum Phi if required by a later lane, independent material/state/source/detector/temperature mapping, and physical heat/collision/Kubo/SK-KMS/entropy transport. Full R1, Full Topic13 and the active scientific Goal remain unaccepted.

DEPENDENCY_UNLOCKED: Named classical-Phi candidate validity and independent-input research only. No physical/Core unlock or overwrite of the Core owner's separate composition gate.

STATUS: `PASS_SCOPED_JOINT_PHI_RESPONSE`; [artifact](t13_hartree_joint_phi_response.json) SHA-256 `a50b95ce5b326e41220187322f7c0f015b7b45489b57b49d0f9c720850c7dd42`.

WHAT_CHANGED: Separate topic-local response verifier and 21 independent tests. The branch remains `t13.candidate.classical_phi_hartree_ms_homogeneous_v1`, using the unchanged joint stationary states and action trial inputs. The previous static artifact retains `joint_finite_q_complex_pole_computed=false`; old fixed-Phi poles remain a separate predecessor.

EQUATION_OR_MAPPING:

## Declared classical kinetic term and joint source

The flat, rest-frame limit of the original conservative response action is
`L_Phi=-epsilon*Z_Phi*(partial Phi)^2/2-V_R(Phi)` with metric signature
(-,+,+,+). The original trial input Z_Phi=1 is not a measured transport
coefficient. Independent finite differences of the parent Lagrangian check
the temporal/spatial signs and potential curvature. No damping is inserted.

Order fields as (canonical O(2) radial v, canonical O(2) phase p, existing
UET response Phi). Neither O(2) field is relabelled collective C. The source
A is nondynamical, while R_gen and R_obs do not enter the state or dynamics.
Phi is not the 2PI functional or a newly introduced particle.

```text
L = (K*W, L_Phi), L_Phi=(-sqrt(2)*gamma,0,0)^T
K=diag(4u,2u,2u)
Gamma_tree = [[q^2+a-z^2, 2i*mu*z, -gamma*sqrt(s)],
              [-2i*mu*z, q^2+b-z^2, 0],
              [-gamma*sqrt(s), 0, epsilon*Z_Phi*(q^2-z^2)+V_R'']]
Gamma_joint=Gamma_tree+L^T*J*(I-KJ)^-1*L/2
```

J is the actual subtracted three-channel matter bubble at the joint states,
not a tadpole derivative used in place of a frequency loop. Phi is a
classical dynamical response coupled to that covariance; no quantum Phi
propagator is inserted into the Hartree matter gap equations.

All three field coordinates and A carry E. Gamma, current Hessians and
charge susceptibility carry E^2; J/K/D/epsilon/Z_Phi/u are dimensionless.
Velocity z/q is dimensionless and det(I-KJ)*det(Gamma_joint)/q^2 carries
E^4. The MS scale is 1 E. This is not an SI temperature or heat-flux map.

## Counterterm identity beyond the static point

Write `S=I+D*K`, `K_b=S^-1*K`, `J_b=J+D*I` and `L_b=S^-1*L`.
The bare mass-source slope is gamma_b=gamma/(1+4uD), not gamma. With all
inverses nonsingular, even when K and the complex J do not commute:

```text
L_b^T*J_b*(I-K_b*J_b)^-1*L_b
 = L^T*J*(I-KJ)^-1*L + D*L^T*S^-1*L
Gamma_tree_b=Gamma_tree-D*L^T*S^-1*L/2
Gamma_b=Gamma_joint
```

The tree subtraction is not assigned after seeing a response. Its matter
block is `-W^T*(K-K_b)*W/2`, its radial/Phi contact follows the original
bare mass slope, and its Phi curvature is `V_b''=V_R''-N_PhiPhi`, where
`N_PhiPhi=gamma^2*D/(1+4uD)` was independently derived in the static wave.
These three separately derived terms reproduce the matrix contact above.
Mixed gauge vertices and current contacts satisfy the same affine identity.
Freezing Phi counterterms fails the negative control. Formal D probes are
not a Lorentz-invariant regulator or a proof of full RG/truncation control.

The external-action versus internal-gap distinction follows the method
context of [van Hees and Knoll](https://arxiv.org/abs/hep-ph/0203008).
[Fejos](https://arxiv.org/abs/1410.1337) treats invariant regularization in
Hartree superflow; that requirement is not closed by our algebraic replay.
Neither paper supplies this UET Phi coupling or material calibration.

## Actual joint phase poles and gauge source

Let E=(radial,Phi). Eliminate both neutral amplitude directions, retaining
their determinant/singular values and the uneliminated joint determinant:

```text
Gamma_phase=Gamma_pp-Gamma_pE*Gamma_EE^-1*Gamma_Ep
Pi_AA_relaxed=Gamma_AA-Gamma_AE*Gamma_EE^-1*Gamma_EA
Gamma_phase=Q_E^T*Pi_AA_relaxed*Q_E/s, Q_E=(-i*z,q,0,0)
Gamma_phase(q,z_pole)=0
```

Continue the matter loops using the newly evaluated local cut at the joint
a/b states: B_retarded=B_principal_lower-2*pi*i*D(q,z/q). The local strip is
Re(z/q)=.19 to .45, Im(z/q)=-.015 to 0, q<=.04, below the admitted pair
threshold. Fixed nodes precede each search; seeds .2-.01i and .4-.005i are
numerical controls, not old fitted solutions or assigned widths.

At T=.22 E, the finest-grid z_pole/q values are:

| mu (E) | Phi (E) | q (E) | Re(z_pole/q) | Im(z_pole/q) |
| --- | --- | --- | --- | --- |
| 1.05 | .044179631621 | .04 | .213579960426 | -.006887703060 |
| 1.05 | .044179631621 | .02 | .213008301483 | -.006920957922 |
| 1.05 | .044179631621 | .01 | .212864921936 | -.006929326038 |
| 1.20 | .175433844597 | .04 | .372449371161 | -.003388647455 |
| 1.20 | .175433844597 | .02 | .372267532640 | -.003394765360 |
| 1.20 | .175433844597 | .01 | .372221889161 | -.003396296255 |

The clamped-Phi inverse at these joint poles remains approximately .0154
and .0126, not zero. This is a same-background comparison and is distinct
from changing the old fixed-Phi background. It establishes that freezing
Phi is not an equivalent response calculation, not a material sound speed.

## Independent equilibrium charge-envelope check

At q=z=0 exclude the phase zero direction and compute
`chi_joint=Gamma_A0A0-Gamma_A0E*Gamma_EE^-1*Gamma_EA0`.
Independently reoptimize all four stationary equations at mu+/-h, including
Phi, at fixed T and action inputs; compare with `-d^2 Omega_joint/dmu^2`.

| mu (E) | chi_joint (E^2) | chi_clamped_Phi (E^2) | Final envelope relative disagreement |
| --- | --- | --- | --- |
| 1.05 | 2.408515019051 | 2.370852116211 | 5.054e-9 |
| 1.20 | 3.269206612503 | 3.228182917800 | 8.957e-9 |

This checks source/thermodynamic consistency of the same candidate, not a
physical He-II compressibility measurement. Constant T here is a declared
equilibrium protocol, not a closed thermal energy-exchange calculation.

VERIFICATION: Fourteen artifact checks and 21 focused tests passed. Orders 64/24,96/32,128/40; three q values and two seeds, alternate fixed grids/tail paths, direct absolute upper bubble, full determinants, Ward/source and static potential checks. Maximum final pole refinement 3.098e-7, alternate-grid difference 1.343e-8, independent upper bubble difference 1.472e-8, joint field difference 2.529e-8 and finest phase-current Ward disagreement 1.289e-6. Root <=1e-8, numerical/reference agreement <=2e-5, Ward <=1e-3 and counterterm algebra <=1e-10 remain declared controls; causal leakage threshold remains 1e-6 but that original gate is not repaired or rerun. Listed source/protected hashes match; the new audit reads only the derived joint-state artifact, not old pole answers or measured/holdout rows. Linked regression execution is recorded in UPDATE_LOG.

CONTROLLING_BLOCKER: `joint_global_validity_Hartree_remainder_material_thermal_transport_not_closed`.

NEXT_ACTION: Test the same candidate's low-temperature EOS/external-mode consistency and validity/approximation obligations without a Goldstone mass repair or an added phonon free energy by hand; independently specify material/source/readout/thermal input. This is a new physics question, not another unchanged local-root run. Keep 7 October scientific freeze, 11 October portfolio review and the original scientific completion rule.

CLAIM_BOUNDARY: Classical-Phi response in one named Hartree prescription on two states and six local q points. Not quantum Phi, all-frequency/global/causal stability, controlled Hartree remainder/RG, SI alpha, material sound/heat/collision/Kubo/SK-KMS/entropy, external validation, novelty certification or Full Topic13/UET. No target fit, assigned damping, clipping/filter/padding, mass repair, threshold change or Core-owner edit. Original conserved-C failure stays blocked. Prior Xie context exposure remains REVIEW_REQUIRED with no new numeric access.
