# Acoustic tree pole, cubic vertex and modal cuts

MAJOR_RESULT_CLOSURE: `T13_ACOUSTIC_TREE_MODAL_CUT_MATCHING`, `CLOSED_FOR_LANE`. Not Full Topic13, R1-R5 or Goal completion.

WHAT_IS_ACTUALLY_CLOSED: Tree acoustic pole residue with chemical/symplectic normalization, full shifted-parent cubic projection on three acoustic legs and the corresponding vacuum/finite-T pair/Landau cuts. Independent potential derivatives and matrix-pole residues agree, and low-q results recover the earlier phase EFT.

WHAT_REMAINS_OPEN: Off-shell source/contact and local real matching, all-mode quantum/heavy contributions, complete thermal sunset/mixed pressure/source/entropy, finite-T normal/heat/Kubo/SK-KMS/entropy transport, independent material/readout/scale and full approximation/uncertainty control.

DEPENDENCY_UNLOCKED: Off-shell matching and thermal-sunset research only. No physical/Core/Gravity unlock; original action, owner Core and old failed conserved-C unchanged.

STATUS: `PASS_SCOPED_ACOUSTIC_MODAL_CUT`. [Artifact](t13_acoustic_modal_cuts.json) SHA-256 `6f44a1c7e28aaa3c925a9f9f452892529ba12c5378a0e6222aeab6e3662e7840`.

WHAT_CHANGED: Separate [verifier](../../Code/03_Research/Research_T13_Acoustic_Modal_Cuts.py), focused tests and [local registry](../../Data/03_Research/t13_acoustic_modal_cut_registry.json). The [leading-vertex thermal predecessor](T13_THERMAL_CUT_STIFFNESS_2026-10-03.md) remains byte-identical and retains its static-coherence result. This calculation replaces its approximate vertex/residue only in the declared three-acoustic cut, not in the full real operator.

EQUATION_OR_MAPPING:

## 1. Parent and meaning of its coordinates

Let R=sqrt(s) be the background O(2) radial amplitude, x0=Phi0-Phi_ref,
and fluctuations be y=(sigma, pi_phase, phi). These are coordinates of the
existing parent, not collective C, UET Pi or a new R_gen state. Kinetic
k_Phi=epsilon*Z_Phi is dimensionless; the normalized matter field is canonical.
The grand-potential polynomial, at fixed mu and external h, is

```text
r2=(R+sigma)^2+pi_phase^2
V_eff=-(mu^2-m0^2+gamma_action*(x0+phi))*r2/2 + u*r2^2/4
      +epsilon*[mPhi^2*(x0+phi)^2/2+lambdaPhi*(x0+phi)^4/4]
      -h*(Phi0+phi)
```

R/s are not mass or signed charge; h is a nondynamical external source.
This is the already-declared tree-reduced acoustic quantization. A slaved
Phi component in the light-mode polarization does not introduce independent
quantum Phi propagators/loops or quantization of every massive parent mode.

For convention exp(-i omega t), D=V(q)-omega^2 K-i omega G,
K=diag(1,1,k_Phi), G_12=-2mu, G_21=2mu, and

```text
D = [[ell+2us, +2i mu omega, -gamma_action R],
     [-2i mu omega, ell, 0],
     [-gamma_action R, 0, V_curvature+k_Phi ell]]
ell=q^2-omega^2
```

Its Schur complement is the original phase inverse, not a new dispersion.
The same cancellation-free root from the predecessor supplies E(q).

## 2. Derive the residue, do not use a Euclidean vector norm

On the acoustic root define

```text
W=V_curvature+k_Phi ell
den=ell+2us-gamma_action^2 s/W
A=2mu omega/den; B=gamma_action R A/W
N_pi=1+4mu^2/den+A^2+k_Phi B^2
Z_pi=1/N_pi
u_mode=sqrt(Z_pi)*(-iA,1,-iB)
```

N_pi=-partial_(omega^2) Gamma_phase on the pole. Equivalently,
u_mode^dagger[-partial_omega D]u_mode/(2omega)=1. The chemical
mixing contributes 4mu^2/den; using the ordinary squared length would
miss it. The independently inverted matrix gives

```text
-lim_(omega^2 -> E(q)^2) (omega^2-E(q)^2) D^-1_(phase,phase)=Z_pi
```

Symmetric offsets .01/.001/.0001 check this pole residue. The largest
finest discrepancy is 2.164e-12. Z_pi tends to c^2 at low q; hence the
Cartesian phase coordinate tends to c times the canonical EFT phase.
Positive pole norm and the original positive/conserved quadratic ledger
are checked on the full q grid. This does not prove global interacting
stability or a finite-cone statement for the old conserved-C branch.

## 3. Full tree cubic tensor and on-shell projection

The only nonzero symmetric entries of T_ijk=partial_i partial_j partial_k V_eff are

```text
T_sigma,sigma,sigma = 6uR
T_sigma,phase,phase = 2uR
T_phi,sigma,sigma = T_phi,phase,phase = -gamma_action
T_phi,phi,phi = 6epsilon lambdaPhi x0
```

Mixed central third differences of the full shifted potential check every
independent tensor entry, including zeros, normalized by the largest tensor
component. The largest discrepancy across states/steps is 7.599e-11.
No couplings are inferred from a damping curve.

For signed incoming frequencies (E_k,-E_p,-E_r) in pair and
(E_k,E_p,-E_r) in Landau, the amplitude is T_ijk u_i u_j u_k.
The sign on a frequency conjugates the corresponding real-field mode.
An overall imaginary phase is a convention, not a rate difference.
The tensor is symmetric and negative-frequency conjugation is verified.

At very small q the sum of linear A terms cancels on shell. The stable
formula uses the exact sum omega_i=0 before evaluating the small remainder:

```text
a0=2sU; den=a0+ell H
H=1+gamma_action^2 s k_Phi/[V_curvature W]
Delta(1/den)=-ell H/(a0 den)
Delta(1/(den W))=-ell(a0 k_Phi+H V_curvature+ell H k_Phi)
                      /(a0 V_curvature den W)
sum A_i=2mu sum omega_i Delta(1/den_i)
sum B_i=2mu gamma_action R sum omega_i Delta(1/(den_i W_i))
```

Insert these in the same tensor contraction; do not evaluate the cancelling
large terms directly. Off-shell/unbalanced energies and unsupported momentum
triangles are rejected. This is an analytic on-shell identity, not changing
energy roots or fitting parameters. At independently resolvable q the
stable and raw tensor contractions agree within 3.190e-12.

## 4. Replace the leading cut vertex with the matched acoustic amplitude

Use identical energy roots, group velocity, Bose weights and phase-space
normalization as the predecessor, replacing its LO |M|^2 with the full
tree-projected three-acoustic |M_aaa|^2. All three external-leg residues
are already in M_aaa; do not multiply them again.

```text
gamma_pair = integral dp p r |M_aaa|^2 (1+n_p+n_r)
                        /(E_p E_r v_r) / (64pi E_k k)
gamma_L = integral dp p r |M_aaa|^2 (n_p-n_r)
                        /(E_p E_r v_r) / (32pi E_k k)
Gamma_occupation=2 gamma_pole
```

The tree residue/projection closes the missing finite-q ingredients for
this three-acoustic channel, not for all channels or an off-shell operator.
Pair T=0 recovers the old q^5 coefficient, and soft Landau recovers the
independent 3pi^3(g_t+g_s/c^2)^2/(10c^2) Bose coefficient as T/q refine.

| mu E | vertex/LO relative error at q=.005 E | vacuum q5 error at q=.005 E | modal/LO Landau at finest thermal point |
| --- | --- | --- | --- |
| 1.05 | 7.874738e-6 | .000114834791 | .999981960392 |
| 1.20 | 5.031473e-6 | .0000353791514 | .999950904124 |

The last column changes the leading-vertex rate by -0.001804%/-0.004910%
at these specific points. It quantifies this tree modal correction only;
it does not bound missing quantum/local/source/thermal-pressure physics.
Natural E units do not identify a material's temperature or detector.

VERIFICATION: Nine artifact checks and focused tests; mu=1.05/1.2, q=.04/.02/.01/.005, potential steps.01/.005/.0025, symmetric residue offsets.01/.001/.0001 and predecessor thermal/order grids with tails32/40 declared before audit. Independent potential derivatives and inverted matrix pole, symplectic norm and kernel, raw/stable tensor, low-q EFT/vacuum/soft Bose limits, order/tail/support/energy/Bose and ledger, permutation/reality/coordinate/decoupled/invalid-energy controls, evidence/protected hashes and runtime read allowlist. Counts in UPDATE_LOG; no full repo/external validation implied.

CONTROLLING_BLOCKER: `off_shell_source_real_matching_and_complete_thermal_sunset_open`.

NEXT_ACTION: Derive the off-shell source/contact and real matching interface of the same tree-reduced theory, then complete thermal sunset/mixed pressure/source/entropy. Independent material/readout/scale remains separate. Preserve 7 October freeze, 11 October review and all R1-R5/Goal acceptance requirements.

CLAIM_BOUNDARY: Acoustic tree residue/cubic/cut matching only. Not all-mode quantum Phi/heavy loops, full off-shell/source/local real response, complete interacting pressure/transport/KMS/entropy/uncertainty, Kelvin calibration, material prediction or Full Topic13/Core. No fit, assigned width, clipping/filter/padding, threshold/ontology/Core-owner change or numeric Xie access; prior exposure REVIEW_REQUIRED, old conserved-C blocked at1e-6 and physical/global flags false.

Primary method context: [Derezinski, Li and Napiorkowski](https://www.fuw.edu.pl/~derezins/damping_publ.pdf) construct quasiparticle interaction matrix elements and distinguish pole damping from occupation decay. Their nonrelativistic coefficients are not matching inputs here; the local relativistic-X parent supplies the tensor and residue.
