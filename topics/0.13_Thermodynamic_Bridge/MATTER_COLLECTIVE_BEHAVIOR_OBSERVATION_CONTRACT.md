# Matter, Collective Behavior, Observation, and Persistence Contract

## Purpose

This contract records the clarified UET interpretation without adding a new
substance called “information”. It separates:

1. the physical behavior of matter and interacting components;
2. the collective behavior of the system, represented by \(C\);
3. the physical response candidate represented by \(\Phi\);
4. the record constructed by an observer from received signals;
5. the duration for which a collective system behavior can be maintained.

The contract is conceptual and normalized. It is not yet a dimensional theory
of matter, temperature, or spacetime geometry.

## Two ontological layers, not two substances

Let \(X\) denote the physical state of matter, fields, interactions, and their
current activity. Let \(O\) denote an observer with a worldline, detector, and
measurement protocol. The observation record is

\[
Y_O=\mathcal M_O[X;\gamma_O,D_O],
\]

where \(\gamma_O\) is the observer worldline and \(D_O\) is the detector/
processing rule.

\(Y_O\) is not a new material layer added to the universe. It is the result of
an interaction between the physical state and the observer's measurement
process. A distant observation is therefore a record of a signal that has
already propagated, not direct access to the complete current state of the
source.

The observer can change the record by changing motion, clock synchronization,
detector response, or sampling protocol. That does not mean the observer
arbitrarily creates the source event.

## Individual behavior and system behavior

For interacting matter components \(i=1,\ldots,N\), define a conceptual
individual behavior variable

\[
b_i(t)=\mathcal B_i[m_i,\,\text{local state},\,\text{interactions}].
\]

The collective system behavior is a coarse-grained result of all components
and their relations:

\[
B_{\mathrm{sys}}(t)=
\mathcal A\bigl(\{b_i(t)\},\,\mathcal I(t)\bigr).
\]

The UET coordinate \(C\) is assigned to this system-level result:

\[
C=\mathcal C[B_{\mathrm{sys}}].
\]

Thus \(C\) is not the behavior of one particle, one country, or one piece of
matter. It is a state coordinate describing the collective outcome of
interaction. It may represent coordination, compatibility, or effective
interaction capacity in a declared lane; it is not universally mass, energy,
information, or charge.

The conflict example is an intuition for the direction of the mapping:

\[
\text{stronger opposition}
\rightarrow
\text{higher coordination cost}
\rightarrow
\text{lower collective persistence efficiency}
\rightarrow
\text{lower }C
\]

This example motivates a constitutive mapping. It is not itself a numerical
definition of \(C\).

## Space/system response

If the ordered-space interpretation is retained, \(\Phi\) is the candidate
response of the effective space/system layer to the collective matter state:

\[
\Phi=\mathcal R_{\mathrm{space}}
\bigl(C,\,\partial_t C,\,E_{\mathrm{available}},\,J_E\bigr).
\]

This is different from the observer record. In the current opt-in matter-space
operator, \(\Phi\) and \(\Pi=\partial_t\Phi\) are physical state variables of
the candidate dynamics, while \(R=I_{\mathrm{trace}}\) is a derived history
observable.

The contract therefore keeps the following distinction:

```text
Phi: candidate physical response that may participate in dynamics
R:   derived trace/record of completed dissipation history
Y_O: observer-dependent measurement record
```

\(\Phi\) must not be renamed \(I\) merely because both are described using
words such as response, information, or memory.

## Persistence is not coordinate time

Relativistic coordinate/proper time describes the ordering and measurement of
events along worldlines. UET's additional question is different:

> Given a collective system behavior, how long can that behavior be maintained
> before the available energy/resource capacity no longer supports it?

Introduce a conceptual reserve variable \(E_{\mathrm{res}}\) and behavior power
costs:

\[
\frac{dE_{\mathrm{res}}}{dt}
=
J_E-
P_{\mathrm{behavior}}(B_{\mathrm{sys}},C)-
P_{\mathrm{maintenance}}(C)-
P_{\mathrm{loss}}.
\]

The persistence time of a declared system behavior is then a stopping-time
functional:

\[
\tau_{\mathrm{persist}}
=
\inf\{t\geq0:E_{\mathrm{res}}(t)\leq E_{\mathrm{min}}\}.
\]

This is not a second time coordinate and does not replace relativistic time.
It is a system-level lifetime/viability observable conditional on an energy
budget and a constitutive power-cost mapping.

The current core equation does not yet contain
\(P_{\mathrm{behavior}}\), \(P_{\mathrm{maintenance}}\), or a physical
\(E_{\mathrm{res}}\) scale. The persistence equations are therefore a
candidate accounting layer, not a completed UET law.

## Corrected causal architecture

The clarified research architecture is:

\[
\begin{aligned}
&\text{matter behavior }\{b_i\}
\rightarrow \text{interactions }\mathcal I
\rightarrow B_{\mathrm{sys}}
\rightarrow C\\
&\qquad\rightarrow \Phi,\Pi
\rightarrow \text{effective energy/dissipation}
\rightarrow R\\
&\text{physical state }X
\xrightarrow{\mathcal M_O[\cdot;\gamma_O,D_O]}
Y_O
\rightarrow \text{reported observable}.
\end{aligned}
\]

The observer branch is a measurement map. It is not a feedback arrow into
physical dynamics unless a separate measurement-interaction model explicitly
defines such feedback.

## What this resolves

This contract resolves four previous ambiguities:

- data/information is not treated as an additional cosmic substance;
- \(C\) is explicitly collective/system-level rather than particle-level;
- \(\Phi\) is separated from the derived trace and the observer record;
- persistence/lifetime is separated from relativistic coordinate time.

## What remains open

The next mathematical closures are now specific:

1. define the coarse-graining/observable map \(\mathcal C\) from interacting
   matter behavior to \(C\);
2. define the collective power-cost functional
   \(P_{\mathrm{behavior}}\);
3. determine whether \(\Phi\) responds directly to \(C\), to its rate, or to
   available energy/reserve;
4. define \(\mathcal M_O\) for a concrete measurement lane;
5. only then derive temperature or TTG observables from the physical state.

Current status: `ONTOLOGY_LOCK_CANDIDATE / DIMENSIONAL_AND_MICROPHYSICAL_MAPPING_OPEN`.

