# Conditional thermal variance actuation

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The local Gaussian thermal variance provides a nonzero linear static Phi response to a mass-source, despite zero coherent mean chi. Phi feedback is included and checked against nonlinear equilibrium roots.
WHAT_REMAINS_OPEN: Physical mass-source amplitude and units, bare-coefficient/reference provenance, dynamic response, energy input ledger and material calibration.
DEPENDENCY_UNLOCKED: None.
STATUS: CONDITIONAL_STATIC_SOURCE_RESPONSE_CHECKED.
WHAT_CHANGED: Implicit-equilibrium diagnostic, three tests and artifact; no production action or physical calibration changed.
EQUATION_OR_MAPPING: A*phi-eta*(F_x(T+dT,x+u-eta*phi)-F_x(T,x))=0. A_eff=A+eta^2 F_xx; dphi/du=eta F_xx/A_eff; dphi/dT=eta F_xT/A_eff.
VERIFICATION: Three tests PASS. Three reference temperatures0.4/0.8/1.2 and perturbation steps0.01/0.005/0.0025 show decreasing derivative errors. Smallest-step mass derivative errors are below1.3e-6 relative, thermal below4.3e-5. Positive A_eff in all rows; unstable reference rejected, zero coupling returns zero response.
CONTROLLING_BLOCKER: physical_mass_source_gain_and_reference_coefficient_provenance.
NEXT_ACTION: Identify a physical modulation u with independent calibration in the chosen material lane. Reuse thermal matching rather than adding arbitrary force; include the full source work and dynamic susceptibility before interpreting an experiment.
CLAIM_BOUNDARY: Homogeneous isothermal static normal Gaussian control, not finite-frequency or finite-cone closure. Temperature-driven Phi is not an independent alpha calibration. No source/holdout data or fitted parameters.

## Reference convention and feedback

The conditional local free energy is A*phi^2/2+F_th(T+dT,x+u-eta*phi)+eta*F_x(T,x)*phi. The last term explicitly cancels the reference thermal tadpole, so phi=0 is the declared reference at u=dT=0. This is a declared diagnostic background-support convention, not a derived material counterterm. It is kept fixed while differentiating each response; each reference-temperature row has its own declared background and is not a temperature sweep of one fixed bare action.

The thermal F_xx is negative and softens the response curvature. For fixed x=2.25, eta=.35 and A=.8, the feedback factors A/A_eff are1.0000583/1.0005815/1.0014749. No conclusion about arbitrary temperatures/couplings follows. A large response near A_eff=0 would signal a loss of this approximation's stability margin, not an automatic calibration success.

Units: phi,T,eta energy; x,u,A energy^2; F energy^4. A is a declared bare static curvature, not automatically a measured total stiffness. Do not add eta^2 F_xx to a total measured coefficient twice. The prescribed-source static root does not supply a work ledger or an on-shell driven preparation protocol.

Evidence: artifacts/t13_thermal_mass_actuation_audit.json; thermal integrals reused from uet_matter_strain_susceptibility.py.
