# Operational calibration route, not a request for an undefined Phi measurement

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: A conditional input-output ambiguity is explicit: measuring an absolute temperature transfer function does not by itself separate the source-to-Phi gain from alpha. More frequencies do not remove this gain symmetry.
WHAT_REMAINS_OPEN: An operational base-Phi preparation/readout or independently matched source gain, material operator and same-state source provenance.
DEPENDENCY_UNLOCKED: None.
STATUS: OPERATIONAL_ANCHOR_REQUIRED_BEFORE_PAIRED_DATA_REQUEST.
WHAT_CHANGED: Two-test input-output diagnostic and artifact; clarified how the composite-alpha design can become an actual experiment. No core equation or calibration gate changed.
EQUATION_OR_MAPPING: Conditional control D Phi=b U, DeltaT=alpha Phi gives H=alpha*b/D. Under b->s*b and alpha->alpha/s the full complex response is unchanged. This control is not a new UET branch.
VERIFICATION: Two tests PASS;101-frequency invariance test and rank test. Five-frequency artifact preserves response to2.3e-16 across scales0.1/2/10. Gain design rank1 becomes2 only when an independent actuation-gain constraint is supplied.
CONTROLLING_BLOCKER: operational_input_to_base_Phi_operator_and_gain.
NEXT_ACTION: Identify the physical input U and derive its registered coupling to base Phi in the chosen material lane. Specify what independently anchors b or Phi amplitude before requesting paired measurements. Keep ordinary thermal data as material/comparator evidence until that interface exists.
CLAIM_BOUNDARY: Conditional linear identifiability result, not a universal no-go for nonlinear experiments. No source received, no alpha value, no holdout data, and no Full Topic13 closure.

## Practical measurement requirements

The existing paired-record protocol asks for base-Phi amplitude but does not describe an apparatus or operator that measures it. It is an acceptance requirement, not yet a realizable experiment. A physical source monitor measures U; it does not automatically measure b. An independent thermometer supplies DeltaT; it does not by itself measure Phi. Calling DeltaT/alpha a Phi measurement is circular.

The full-numerator route from T13_COMPOSITE_ALPHA_DESIGN.md remains valid only if its numerator is independently tied to the fixed base-Phi coordinate. If its measurement is another unanchored input-output gain, the ambiguity above survives. The next useful design must say which independent observable or dimensionful action matching breaks that symmetry; setting b=1 by coordinate convention is not a new physical measurement or a derived material coefficient.

## Source inspection

The existing local source-availability and calibration-candidate artifacts already document no eligible paired base-Phi record in their historical inventories. Those inventories were read, not freshly regenerated; no claim is made about all current public datasets.

A targeted literature search inspected the abstract of Johnson et al., *Phase-controlled, heterodyne laser-induced transient grating measurements of thermal transport properties in opaque material*, https://arxiv.org/abs/1109.6685 (2011 preprint). It describes separating optical amplitude and phase contributions, with surface displacement affecting the phase channel, and extracting diffusivity. This is relevant detector-method context, not a base-Phi calibration source. No numeric payload was imported and no full-text or rights review was claimed. The search did not return Xie2026; this does not erase the separately documented earlier holdout-context exposure.

Research priority: physical actuation/readout mapping first, then independent amplitude calibration. Do not spend another source-search wave looking for a published UET-specific latent variable without an operational definition.
