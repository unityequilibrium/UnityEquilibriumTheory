# Impact–Effect Ontology Update Log

## 2026-08-02 - Deterministic legacy-wording disposition

- Scope: Wave 1 wording audit and foundation controller synchronization.
- Wave type: claim-boundary pass and workflow-repair pass.
- Added or changed: `audit_impact_effect_legacy_wording.py` now emits a disposition and basis for every occurrence without rewriting source text.
- Verified with: wording audit plus schema assertions; 664 occurrences were classified as 127 `LEGACY_ARCHIVE_QUARANTINED`, 283 `CODE_OR_TEST_LITERAL`, 12 `CANONICAL_CONTRACT_LITERAL`, and 242 `ACTIVE_PROSE_MANUAL_REVIEW`.
- Result: artifact status `SCOPED_DISPOSITIONS_WITH_ACTIVE_PROSE_OPEN`; foundation remains `BLOCKED`.
- Blocker narrowed: archive/code/core-contract occurrences are routed deterministically; only active prose remains the manual wording controller, while F2 correspondence rows remain independently open.
- Still open: manually review the 242 active-prose occurrences and close the exhaustive F2 lane correspondence/measurement-operator manifest.
- Next controller: active-prose review plus F2 open-row closure; no wording promotion is implied.
- Claim impact: no change; `C`, `R_gen`, mass, vacuum, photon, neutrino, and positron identities remain lane-specific or blocked.


## 2026-07-29 - Separate physical impact from informational effect

- Scope: distinction between mass/energy-bearing interaction and receiver-side
  information effect; phase-change interpretation; carrier-neutral mapping.
- Added: `IMPACT_EFFECT_AND_INFORMATION_FLOW_SPEC.md`, machine-readable contract,
  and equation-registry addendum.
- Clarified: an impact is a physical coupling; an effect is the input-output
  influence extracted by a receiver. An effect does not require source-mass
  transfer, but a physical receiver change still requires a carrier and a
  detector interaction.
- Clarified: photons, neutrinos, and positrons have different roles. No one of
  them is promoted to the universal information carrier.
- Clarified: “death” is represented as termination of a mass-bearing organized
  phase, while energy-momentum and causal traces may continue in new products.
- Claim boundary: no automatic massive-to-photon conversion, no universal
  `I_trace` particle identity, and no independently derived orbital law.
- Next controller: build a carrier-neutral photon/neutrino/matter-antimatter
  comparison with units, conservation, detector maps, and falsification gates.


## 2026-07-29 - Foundation-first registry and legacy boundary synchronization

- Scope: Wave 0 synchronization for the foundation-first matter/impact/effect/carrier program.
- Added: central registry merge script, F0 inventory refresh, dependency graph, and legacy-wording audit.
- Audited: 27 topic formula-audit files and 263 formula rows; registry now contains 15 entries including the impact/effect and cosmological addenda.
- Found: 650 legacy/ambiguous wording occurrences in the scoped docs/code inventory; no wording was rewritten automatically.
- Claim boundary: foundation remains `BLOCKED`; impact/effect remains `CANDIDATE`; no particle identity, global-open-universe claim, or mass mapping was promoted.
- Next controller: implement the explicit carrier-neutral receiver relation, then verify it without feeding observer records back into the physical core.
## 2026-07-29 - Add carrier-neutral relation and explicit receiver feedback

- Scope: Wave 1 implementation of the impact/effect/carrier boundary.
- Added: `uet_impact_effect.py`, public dataclasses for impact/carrier/effect/receiver dynamics, targeted tests, and generated verification/dependency artifacts.
- Verified: 6 focused impact/effect tests plus 13 matter-space alignment regressions passed; local verifier status `PASS`.
- Semantics: an effect can exist with zero source-mass transfer; receiver state changes only in explicit `coupled_receiver_v1`; observer protocol changes `R_obs` without changing `R_gen` or core state.
- Claim boundary: normalized carrier-neutral relation only; carrier identity, dimensional closure, detector maps, and transition physics remain open; dependency gate remains `BLOCKED`.
- Next controller: extend matter-space core verification and add the isolated phase diagnostic without modifying the current 0.11 structure-factor controller.
## 2026-07-30 - Carrier-neutral photon/neutrino/reaction comparator contract

- Scope: Wave 4 contract-only comparator after the phase pilot; no particle dynamics were added.
- Added: `CARRIER_NEUTRAL_COMPARATOR_SPEC.md`, a generated three-lane contract artifact, verifier, and regression tests.
- Verified: contract checks `PASS`, two boundary tests passed, dependency remains `BLOCKED`.
- Clarified: photon is the massless signal-carrier baseline; neutrino is a standard massive weak-carrier benchmark candidate; positron is a mass-bearing reaction participant. None is identified with `I_trace`.
- Claim boundary: no UET carrier identity, massless transition, detector map, or dimensional external validation is established.
- Next controller: source-lock one carrier lane and close its units/conservation/detector map only after upstream phase/core gates.