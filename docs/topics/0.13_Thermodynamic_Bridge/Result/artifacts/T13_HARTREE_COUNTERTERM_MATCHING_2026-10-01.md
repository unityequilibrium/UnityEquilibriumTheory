# Homogeneous Hartree counterterm and on-gap potential matching

MAJOR_RESULT_CLOSURE: `T13_FIXED_PHI_HARTREE_COUNTERTERM_AND_ON_GAP_POTENTIAL_MATCH`, `CLOSED_FOR_LANE` in the named fixed-Phi finite Hartree candidate. Not a full regulator or material match.

WHAT_IS_ACTUALLY_CLOSED: Two invariant counterterm channels cancel the homogeneous gap coefficients, a distinct field quartic closes the mean-field equation, and the on-gap potential equals the previous finite potential up to a state-independent constant. The prior witnesses match without retuning. The symmetric offdiagonal channel and a conditional vertex subtraction identity are checked.

WHAT_REMAINS_OPEN: Regulator tensor/translation invariance, actual finite-frequency bubble divergence and external vertices, running/action inputs, joint Phi/global phase state, material/observable map, controlled dynamic remainder and transport.

DEPENDENCY_UNLOCKED: Counterterm contract for external-vertex work in this candidate only. No funding, full Topic13 or Core-composition gate change.

STATUS: `PASS_HOMOGENEOUS_HARTREE_COUNTERTERM_MATCH`; [machine-readable evidence](t13_hartree_counterterm_matching.json).

WHAT_CHANGED: Added a coefficient-first verifier and nineteen tests; matched the [finite Hartree background](T13_RENORMALIZED_HARTREE_BACKGROUND_2026-10-01.md), without forcing its internal phase mass to zero.

EQUATION_OR_MAPPING:

## 1. Fixed-Phi divergence and unit contract

Use u=lambda/Z^2, s=v^2, m2=m(Phi)^2/Z and physical squared masses M1=a+mu^2,M2=b+mu^2. H=[[3,1],[1,3]] is a Wick matrix, **not UET C**. C remains a collective coordinate, Phi an effective response and R_gen a derived trace.

The formal tadpole decomposition is T_i=F_i+D2+(M_i-M02)*D. Finite F_i is a tadpole, not a free-energy functional. D,u and countercouplings are dimensionless; D2,M_i,M02,s,F_i have E^2; loop/potential E^4; T,mu have E. No SI/helium calibration is introduced.

D,D2 are independent algebra probes, not cutoffs, a continuum UV limit or measurements. Their decomposition assumes absence of additional superflow-dependent tensor divergences; these probes do not prove that regulator requirement. Counterterms have no T,mu or finite-tadpole inputs. Joint Phi dependence remains open.

## 2. Coefficient derivation

Let K=u*H and K_b=[[A+2B,A],[A,A+2B]]. Finite and bare gaps are

```text
M=m2*1+K*(s*e1+F).
M=mb2*1+K_b*(s*e1+F+D2*1+D*(M-M02*1)).
```

Matching arbitrary F and s coefficients, rather than selected roots, gives

```text
K_b*(I+D*K)=K.
B=u/(1+2uD); A=u/[(1+2uD)*(1+4uD)].
mb2=m2-2(A+B)*[D2+(m2-M02)*D].
u4=A+2B-2u; delta_u4=delta_A+2delta_B.
B_field=M1-mu^2-2u*s.
```

The singlet and traceless eigenvalues of K are 4u and 2u. One common bare coupling would have to equal both u/(1+4uD) and u/(1+2uD). Their difference is nonzero for u>0,D!=0 away from poles: a scoped obstruction to the single-countercoupling ansatz, not UET or all Hartree completions. The field relation follows by subtracting the first bare gap from the bare mean-field bracket.

Projection poles are rejected, not clipped. Signs of bare quartics at formal probes do not establish global stability or nonperturbative UV completion.

## 3. Potential cancellation

With the predecessor's finite trace-log Omega_F and reference L0:

```text
Omega_b=Omega_F+L0+(M1+M2-2M02)*D2/2
        +[(M1-M02)^2+(M2-M02)^2]*D/4.
V_b_on_gap=(mb2-mu^2)*s/2+u4*s^2/4+Omega_b
           -(A+B)*(T1+T2)^2/4-B*(T1-T2)^2/4.
V_F_on_gap=(m2-mu^2)*s/2+u*s^2/4+Omega_F
           -u*(3F1^2+2F1F2+3F2^2)/4.
V_b_on_gap=V_F_on_gap+N.
N=L0+(m2-M02)*D2+(m2-M02)^2*D/2
  -(A+B)*[D2+(m2-M02)*D]^2.
```

Expansion after the gap substitution cancels all remaining s and finite-tadpole coefficients. N is independent of s,mu,T and finite tadpoles at fixed action inputs. The predecessor's variational insertion equals minus twice its double-bubble term on its gaps, reproducing this V_F. Both witnesses match potential and shifted masses without retuning.

This is an on-gap identity, not every off-gap/source-dependent 2PI functional. N may depend on m(Phi); it cannot be discarded as Phi-independent when deriving joint Phi dynamics.

## 4. Symmetric tensor and conditional vertex interface

The invariant contraction is Sigma(X)=A*tr(X)*I+2B*X. In orthonormal trace, diagonal-traceless and offdiagonal channels, K=diag(4u,2u,2u). K_b eigenvalues are 4u/(1+4uD),2u/(1+2uD),2u/(1+2uD).

**If** a future bubble obeys J_b(Q)=J_F(Q)+D*I in this convention, then

```text
K_b^-1-D*I=K^-1.
[K_b^-1-J_b(Q)]^-1=[K^-1-J_F(Q)]^-1.
```

No commutation with J_F is needed. Noncommuting complex algebra probes check this identity; they are not computed thermal frequency bubbles. Their decomposition, continuation and physical source vertices remain to be derived. The internal Hartree gap is not the external physical Goldstone response.

VERIFICATION: Nineteen tests cover tensor/matrix inversion, eigenchannels, signed finite tadpoles, exact-rational polynomial cancellation, normalization, negative controls, units, predecessor identity/failure rejection, pole refusal, read allowlist and no-promotion. First run exposed exact float equality at u=0.7; that replay test now checks roundoff at 1e-14, without changing the 1e-10 artifact gate or physical thresholds. Formal residual 1.78e-15; predecessor cancellation 4.44e-16. Neither is a physical uncertainty or truncation bound.

[Fejos](https://arxiv.org/abs/1410.1337), II-IV, supplies established Hartree counterterm/regulator method context. The coefficient and polynomial identities are reconstructed explicitly. This standard-method implementation is not a UET novelty claim. Audit reads declared predecessor/code/protected artifacts only, not Data or numeric holdout. Prior Xie context exposure remains review-required.

Artifact SHA-256: `8daacda13e1e740a9821ea171a7d93fefcbf3392cac5bc28ce75c129f55b4d11`.
Predecessor SHA-256: `c88b6bbb4b8b99667d9562dcfe10930f5c5405053126e5fa729f9016a2652669`.

CONTROLLING_BLOCKER: `external_vertex_and_regulator_RG_material_matching_not_closed`.

NEXT_ACTION: Derive actual finite-q/frequency bubbles/external source equations, their vacuum tensor/translation subtraction and running-input contract, then joint Phi/material admission. Preserve original failed branches.

CLAIM_BOUNDARY: Homogeneous fixed-Phi counterterm and on-gap potential matching, with a conditional vertex interface. Not full regulator/RG closure, finite-frequency observable, physical internal gap, Kubo coefficient, material/graphite validation or global UET closure. Physical/Core gates unchanged.
