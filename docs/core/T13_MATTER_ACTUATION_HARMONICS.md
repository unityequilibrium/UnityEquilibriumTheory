# Existing matter-source actuation boundary

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The existing response residual gives a quadratic coherent matter source. Around zero classical chi, no first-order source at the drive frequency exists; DC and twice-frequency terms remain.
WHAT_REMAINS_OPEN: Physical preparation/measurement of chi, thermal variance susceptibility, coupled on-shell response and source energy accounting, material SI matching.
DEPENDENCY_UNLOCKED: None.
STATUS: EXISTING_ACTION_SOURCE_HARMONICS_CHECKED.
WHAT_CHANGED: Production-residual harmonic diagnostic, three tests and artifact. No new force added to the action.
EQUATION_OR_MAPPING: J=epsilon*h*(chi1^2+chi2^2)/2. With chi1=chi0+A*cos(omega*t), chi2=0, subtracting the background gives DeltaJ=epsilon*h*chi0*A*cos(omega*t)+epsilon*h*A^2*(1+cos(2omega*t))/4.
VERIFICATION: Three tests PASS. Seven artifact cases include zero/nonzero backgrounds, three amplitudes and epsilon=0. Harmonics agree within4e-18 absolute in the declared natural-unit examples. Halving amplitude quarters the zero-background source; at nonzero background it halves the fundamental component. No division by epsilon at the GR null.
CONTROLLING_BLOCKER: physical_preparation_and_measurement_of_matter_amplitude_or_variance.
NEXT_ACTION: For a normal thermal branch inspect response of the matter variance, not coherent mean chi alone. Reuse existing mass-source thermal matching and require an independently known physical modulation of that mass source before claiming an actuation gain.
CLAIM_BOUNDARY: This measures source harmonics, not Phi/temperature harmonics or an on-shell driven experiment. Prescribed chi is a mathematical probe. No physical calibration, coherent condensate preparation, source energy ledger or Full Topic13 closure is asserted.

## Choice of input matters

The previous linear control D Phi=b U remains only a conditional design. Taking U=chi on a zero classical background makes its first-order b zero. Taking U=chi^2 gives a source coefficient epsilon*h/2 in the existing residual, but does not make chi^2 an independently measured material observable. The drive gain in an evolution equation also depends on kinetic normalization and response propagation, not just this residual coefficient.

For thermal matter, mean chi=0 does not imply mean chi^2=0. A modulation of occupation or mass can change the variance at first order. The existing `uet_matter_strain_susceptibility.py` computes conditional thermal mass derivatives and companion entropy/stiffness terms; it must not be replaced by the coherent-field result above. Its external deformation input still needs physical matching.

Therefore neither adding an arbitrary linear source nor insisting on a nonzero coherent background is justified as a shortcut. First specify whether the experiment modulates a coherent amplitude, a mass source or a thermal population, and retain the corresponding operator and energy ledger.

Units: chi0 and A energy, h energy, J energy^3, epsilon dimensionless. C, Phi and R_gen meanings unchanged. Evidence: artifacts/t13_matter_actuation_harmonics_audit.json.
