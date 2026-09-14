# Linear heat-charge frame map

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE; the projected heat moment and the corresponding linear charged-fluid entropy-current transformation are identified.
WHAT_IS_ACTUALLY_CLOSED: The energy-current source is momentum times sqrt(w), hence lies in the projected invariant space. Direct energy flux Q is numerically zero while charge current V is not. The computed heat moment is Q-hV=-hV in this Landau energy frame. It must not be identified with Q itself.
WHAT_REMAINS_OPEN: Propagating frame labels and current outputs into the core interface/composition, finite-cutoff convergence, material-charge/protocol matching and full two-fluid transport.
DEPENDENCY_UNLOCKED: Internal linear frame correspondence only; no physical Core promotion.
STATUS: LINEAR_FRAME_MAP_RESOLVED.
WHAT_CHANGED: Added direct moment/frame audit, tests, generated artifact and unmerged registry addendum; existing production frame outputs and historical artifacts not changed.
EQUATION_OR_MAPPING: u_E=u_L+V/n+O(V^2); q_E=-hV to first order. S_L=s*u_L-mu*V/T and S_E=s*u_E+q_E/T agree after transforming velocity because h=mu+Ts/n. The old heat/T term alone is not the spatial Landau entropy current.
VERIFICATION: Three tests pass, including rejection of zero-charge mapping and detection of wrong enthalpy. Three fixed small driving amplitudes use the same existing action/operator. Energy/heat ratio2.53e-16, heat=-hV relative residual4.53e-16, entropy frame residual9.16e-16. K_heat=h^2 K_charge matrix residual2.22e-16. Charge-diffusion entropy and corrected kinetic entropy agree relatively1.78e-15. These are linear algebra identities, not precision estimates for a material or independent physical measurements. F0 inventory369/no duplicate IDs.
CONTROLLING_BLOCKER: physical_material_charge_and_protocol_map; production frame label/current propagation is still required.
NEXT_ACTION: Make the production interface distinguish invariant heat combination, Landau energy flux, charge diffusion and frame-specific entropy current. Preserve heat response as a formal moment coefficient; use material evidence before identifying signed O(2) charge with particle or mass flow.
CLAIM_BOUNDARY: Linear, local, fixed-Phi charged normal branch only. Not an exact finite-velocity transformation, microscopic SK match, SI heat conductivity or full He4 bridge validation. Three amplitudes check linearity, not temporal/spatial convergence.

## Derivation and interpretation

With weighted coordinate z, raw moment sources are b_E=E*v*sqrt(w)=p*sqrt(w) and b_N=q_species*v*sqrt(w). Conservation projection P removes b_E. Therefore P*b_heat=P*(b_E-h*b_N)=-h*P*b_N. The response matrices satisfy K_heat=h^2*K_charge before any material mapping.

At fixed pressure and fixed Phi, Gibbs-Duhem yields grad(mu/T)=h*X/T for X=-grad(T)/T. Thus sigma=-V.grad(mu/T)=X.q_heat/T, consistent with the repaired kinetic entropy metric. The entropy-conjugate charge-force coefficient is T*K_charge, not K_heat. This is a formal conversion within the chosen natural-unit conventions, not a determination of a physical conductivity.

The projected energy frame has V nonzero. Calling its raw entropy current s*u_L+q_heat/T would omit the charge/frame bookkeeping. In the Eckart particle frame, the convective shift s*V/n precisely supplies the missing term at first order. n must be nonzero; no Eckart construction is claimed at charge neutrality. The frame velocities used here are linear expansions, not separately normalized finite-velocity solutions.

The canonical entropy decomposition is consistent with [Schianchi and Abalos, equation73 and Lemma4](https://arxiv.org/pdf/2602.20254v3). No new source/holdout data or fit was used.
