# Carrier and observer lane

This lane contains the operational quantum-measurement baseline and the
prediction-invariant QBism/RQM comparison adapters. They separate source
states, channels, instruments, outcomes, and observer records.

Owner: LANE

These modules import standard finite-dimensional quantum mechanics as an
interface. They add no UET quantum dynamics, do not identify `C` with a wave
function density, and do not turn observer metadata into physical feedback.

## Standard comparator sources

- photon_observer_baseline.py is a normalized source → propagation → detector comparator.
- relational_two_body_baseline.py is a Newtonian relational-coordinate and finite-signal observer comparator.
- Both are standard-physics baselines only; neither identifies C with mass nor derives a UET particle/carrier law.
- Their dimensional source packages, uncertainty model, and UET source-to-carrier mapping remain open.
