# UET Cosmological Open-System and Causal-Trace Specification

## Status

`CANDIDATE_COSMOLOGICAL_INTERPRETATION / GLOBAL_CLOSURE_BLOCKED`

This specification records the current cosmological interpretation of UET after
the matter-behaviour, observation-delay, persistence, and two-layer trace
discussion. It is an ontology and correspondence contract. It is not a proof
that the universe is globally open, a replacement for general relativity, or a
derivation of information as a new substance.

## The central distinction

UET does not need to claim that the universe contains an additional material
thing called information. The intended distinction is between:

1. physical matter, fields, and their interactions;
2. the collective behaviour produced by those interactions;
3. physical traces carried by fields or signals after an event;
4. the record calculated by a particular observer.

The word `information` refers to the last two items as a relation or observable,
not to an extra cosmic fluid.

The proposed causal chain is

```text
matter and fields
  -> interaction and energy exchange
  -> collective system behaviour B_sys
  -> C
  -> effective space/system response Phi, Pi
  -> generated physical trace R_gen
  -> signal propagation
  -> observer record Y_O
```

## Vacuum, space, and the open-system claim

The phrase “space is not an empty vacuum” must be made precise. In this
workstream it means that `Phi = 0` is an ordered-space reference state, not the
absence of space, fields, causal structure, or possible response. It does not
mean that `R`, `Y_O`, or information is a new matter component.

The current UET proposal is weaker and more precise than “the entire universe is
100% open”:

- a chosen effective cosmic or spacetime subsystem may require an exchange or
  response channel that is absent from a closed reduction;
- the full universe may therefore be **not adequately represented by the
  closed-system reduction**;
- a global statement that the universe is open requires a boundary, exterior,
  or covariant non-closed closure that is not yet present;
- the closed-system limit recovering an Einstein/GR-like description is a
  required correspondence target, not an established result of the current
  code.

Use `effective non-closed cosmic system` or `open-system constitutive ansatz`
until the global boundary and stress-energy map are derived.

## Behaviour, time, energy, and persistence

The thought experiment uses the following operational idea:

```text
behaviour = physical change or interaction
time       = duration/order required for that process
energy     = exchange or redistribution that enables the process
```

For a declared lane, the resource ledger can be written as

\[
\frac{dE_{\mathrm{available}}}{dt}
= J_{\mathrm{in}}
- P_{\mathrm{behaviour}}
- P_{\mathrm{maintenance}}
- P_{\mathrm{loss}}.
\]

The persistence time of a collective behaviour is therefore a lifetime
functional,

\[
\tau_{\mathrm{persist}}
= \inf\{t\ge 0:E_{\mathrm{available}}(t)\le E_{\min}\},
\]

not a new universal time coordinate. Relativistic proper/coordinate time and
the UET persistence time must remain separate.

There is also a necessary standard-physics qualification: a freely moving body
in ideal vacuum does not continuously consume fuel merely to maintain inertial
motion. Energy is exchanged when the body is accelerated, steered, scattered,
heated, radiates, or otherwise changes state. The UET hypothesis concerns the
energy cost and viability of physical behaviour in a declared system; it must
not redefine all inertial propagation as continuous fuel consumption.

## Light as a causal carrier

Light is a valid example of a signal carrier:

```text
source interaction/transition
  -> emission of a field excitation with energy-momentum
  -> propagation through the causal structure
  -> detector interaction
  -> observer record
```

Zero rest mass does not mean zero energy. A photon can carry energy and
momentum, and a source can transfer energy into radiation. That does not imply
that the photon must spend fuel while propagating freely. The source event and
the carrier's propagation are different behaviours and must be represented by
different terms in an energy ledger.

The observation relation is therefore

\[
t_{\mathrm{arrival}}
=t_{\mathrm{emission}}
 +\Delta t_{\mathrm{propagation}},
\]

and

\[
Y_O
=\mathcal M_O[R_{\mathrm{gen}};
\gamma_O,D_O,\text{sampling}],
\]

where the observer record is a processed record of a source event, not direct
access to the source's complete present state.

## Two layers of `R`

`R` must not be used for both physical generation and observer interpretation.
The canonical notation is

\[
R_{\mathrm{gen}}
=\mathcal G\left[
\text{interaction history},
\text{energy exchange},
\text{dissipation}
\right],
\]

followed by

\[
R_{\mathrm{obs}}^{(O)}
\equiv Y_O
=\mathcal M_O[R_{\mathrm{gen}};\gamma_O,D_O].
\]

`R_gen` is the physical/history layer. `R_obs` is the observer-dependent
measurement layer. Neither is an independent material reservoir in the current
UET mode. The existing implementation name `I_trace` is closest to
`R_gen`; it does not yet implement the observer map.

The observer can change the record through worldline, detector response,
sampling, and coordinate reconstruction. This changes the measurement map, not
the source event arbitrarily.

## Orbital order as collective dynamical balance

The solar-system example is best formalized as a collective-dynamics question,
not as a claim that planets have intention. Let

\[
X_{\mathrm{orb}}
=\{x_i,p_i\}_{i=1}^{N}
\]

be the matter state and let

\[
B_{\mathrm{sys}}
=\mathcal A(\{b_i\},\mathcal I)
\]

be the collective result of individual motion and interaction. A bounded orbit,
resonance, or long-lived configuration can then be represented by a candidate
collective coordinate `C_orb` and a persistence functional. The standard
baseline remains Newtonian/relativistic dynamics: gravity, inertia, initial
conditions, perturbations, and conservation laws determine whether a
configuration is stable.

The UET extension is the hypothesis that long-lived configurations are the
surviving solutions of a coupled balance between interaction, available energy,
and structural compatibility. “Natural selection” is used here only as a
selection analogy: unstable configurations are disrupted and stable ones remain
observable. It is not a teleological force and is not yet a derived orbital law.

## Required equation-level mapping

The current research mapping is

\[
\begin{aligned}
&\text{individual matter behaviour and interaction}
\rightarrow B_{\mathrm{sys}}\rightarrow C\\
&\rightarrow \Phi,\Pi
\rightarrow \text{physical response and energy ledger}
\rightarrow R_{\mathrm{gen}}\\
&\rightarrow \text{signal propagation}
\rightarrow R_{\mathrm{obs}}^{(O)}.
\end{aligned}
\]

This does not identify `C` with mass, `Phi` with information, or `R` with a
substance. Each physical lane still needs its own standard counterpart, units,
derivation, and measurement operator.

## Current claim boundary

Allowed:

- `C` as a candidate collective system-behaviour coordinate;
- `Phi` as a candidate effective response variable;
- `R_gen` as a derived causal/history trace;
- `R_obs` as an observer-dependent measurement record;
- effective non-closed/open-system behaviour as a constitutive hypothesis;
- orbital persistence as a diagnostic question about collective dynamical balance.

Not established:

- that the whole universe is globally open;
- that vacuum information is a new physical substance;
- that light continuously consumes energy while freely propagating;
- that UET has derived Einstein/GR as an exact closed limit;
- that the orbital structure of the Solar System has been derived from `C`;
- that `R_gen` or `Phi` is mass, dark energy, a metric tensor, or a new particle.

## Next gates

1. Complete the source-to-`C` coarse-graining map for one physical lane.
2. Define a dimensional energy-exchange and persistence observable.
3. Define the signal/observer measurement operator separately from `R_gen`.
4. Audit the closed-limit correspondence against the standard Einstein/GR
   baseline without promoting the target to a result.
5. Test one orbital or thermal system only after the preceding gates are closed.

