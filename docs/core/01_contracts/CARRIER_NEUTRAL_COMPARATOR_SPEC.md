# Carrier-Neutral Comparator Contract

## Status

`BLOCKED / CONTRACT_ONLY / NO_UET_PARTICLE_DERIVATION`

This document defines the minimum comparison record for a photon lane, a
neutrino lane, and an electron-positron reaction lane. It does not choose a
universal carrier for UET and does not identify `I_trace`, `R_gen`, or `effect`
with any particle.

## Required lane record

Every lane must record:

- source interaction and source state,
- carrier identity or reaction-participant role,
- rest-mass status,
- energy-momentum ledger,
- charge/current and other relevant conservation laws,
- propagation law and causal speed,
- detector/receiver interaction,
- observable payload and units,
- falsification condition,
- source provenance and evidence status.

## Declared comparator roles

| Lane | Role in this program | Current status |
| --- | --- | --- |
| Photon | primary massless electromagnetic observation/signal-carrier baseline | standard comparator; UET derivation not established |
| Neutrino | weakly interacting carrier candidate with standard mass eigenstates | benchmark compatibility only; UET identity not established |
| Electron-positron | mass-bearing antiparticle reaction participant; annihilation product comparator | standard reaction comparator; not a universal carrier |

The phrase “mass-bearing phase continues in a carrier” is therefore a
candidate transition hypothesis. It can be tested only after a source
interaction, transition mechanism, and conservation ledger are specified. A
large speed or an observer record alone cannot derive a photon or erase rest
mass.

## Gate boundary

The contract remains `BLOCKED` while the matter-space core has a causal-support
failure, while the carrier-specific unit/detector maps are open, or while the
Topic 0.11 phase pilot is only simulation-only. The next valid work is a
source-locked comparator package, not parameter fitting or particle identity
promotion.

## Wave 8 normalized photon comparator

The repository now contains a deliberately standard, normalized photon
comparator in `photon_observer_baseline.py`. It closes the local bookkeeping
relations for one declared source event:

\[
p_\gamma = E_\gamma \hat n,\qquad
t_{\rm arrival}=t_{\rm emit}+L/c,
\]

with explicit source energy and momentum ledgers and a detector record that
can be switched on or off without changing propagation. Its verifier artifact
is `photon_observer_baseline_verification.json`.

This is a standard comparator only. It uses normalized units, has no
instrument response or uncertainty package, does not fit data, and does not
derive a UET source-to-photon transition. The photon lane is therefore locally
verified while the Wave 8 dependency remains blocked by dimensional detector
mapping, external provenance, the neutrino/positron comparator packages, and
the missing UET transition law.