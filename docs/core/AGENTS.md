# Core Equation Research Instructions

These folder-scoped instructions apply to all work under `docs/core/`.

## Required reading order

Before editing an equation, parameter, operator, verifier, or core narrative, read:

1. the repository root `AGENTS.md`
2. `docs/topics/For Work/01_Project_Research_Constitution.md`
3. `docs/topics/For Work/02_Project_Workflow_and_Lifecycle.md`
4. `docs/topics/For Work/17_Formula_Audit_Standard.md`
5. `docs/topics/For Work/18_Research_Hardening_Workflow.md`
6. `docs/topics/For Work/EQUATION_RESEARCH_AND_PHYSICAL_CORRESPONDENCE_STANDARD.md`
7. `docs/core/artifacts/uet_foundation_dependency_gate.json`
8. `docs/core/artifacts/uet_equation_correspondence_registry.json`
9. `docs/core/artifacts/uet_foundation_equation_inventory.json`
10. `docs/core/artifacts/uet_foundation_correspondence_matrix.json`
11. `docs/core/artifacts/uet_code_surface_inventory.json`
12. `docs/core/artifacts/uet_core_equation_family_contract.json`
13. `docs/core/00_governance/uet_research_organization_policy.json`
14. `docs/core/artifacts/uet_research_organization_registry.json`
15. `docs/core/artifacts/uet_core_file_migration_map.json`
16. `docs/core/artifacts/uet_core_organization_audit.json`
17. `docs/core/artifacts/uet_foundation_status_aggregate.json`
18. `docs/core/artifacts/uet_legacy_variational_closure.json`
19. `docs/core/artifacts/matter_space_causal_discretization_diagnostic.json`
20. `docs/core/artifacts/matter_space_causal_reference_verification.json`
21. `docs/core/artifacts/uet_foundation_compatibility_decision.json`
22. `docs/core/artifacts/uet_main_theory_wave0_gate.json`
23. `docs/core/artifacts/uet_main_theory_dependency_graph.json`
24. `docs/core/UET_MAIN_THEORY_AXIOMS_SPEC.md`
25. `docs/core/artifacts/uet_main_theory_ontology_gate.json`
26. `docs/core/artifacts/uet_main_theory_wave2_gate.json`
27. `docs/core/artifacts/uet_main_theory_wave3_gate.json`
28. `docs/core/artifacts/uet_main_theory_wave4_gate.json`
29. `docs/core/artifacts/uet_main_theory_wave5_gate.json`
30. `docs/core/artifacts/uet_main_theory_wave6_gate.json`
31. `docs/core/artifacts/uet_main_theory_wave7_gate.json`
32. `docs/core/artifacts/uet_main_theory_wave8_gate.json`
33. `docs/core/artifacts/uet_main_theory_wave9_gate.json`
34. `docs/core/artifacts/uet_main_theory_wave10_gate.json`
35. `docs/core/artifacts/uet_main_theory_wave11_gate.json`
36. `docs/core/artifacts/uet_main_theory_closure_gate.json`

The foundation gate and registry are the controlling status sources for new core work.
Existing topic prose, old badges, and legacy validators do not override them.
The aggregate status is the cross-family stopping boundary: it may expose conditional
compatibility, but it cannot promote a blocked foundation.

After the organization assignment wave, scientific-link work must also read and run
`docs/core/artifacts/uet_core_scientific_link_audit.json` and
`docs/scripts/audit/audit_uet_core_scientific_links.py`. Its status answers whether an
assigned file is actually linked to a canonical family contract, formula IDs, units,
verifiers, artifacts, and claim metadata. `BLOCKED_OPEN_SCIENTIFIC_LINKS` is a valid
stopping state and must not be converted into a physics pass by ownership assignment.
When a bounded family is added, its module paths may remain in organization review through
an explicit `organization_review_required` contract flag. The family link is complete only
when formula IDs are present in the central correspondence registry and the generated
organization record contains the unit, verifier, artifact, and claim links. A named branch
can be internally verified while the foundation gate and its scientific claim remain blocked.

## Mandatory workflow

Before changing or adding a core equation, regenerate the F0 inventory with `docs/scripts/audit/build_uet_equation_inventory.py`; its `inventory_gate_status` must remain visible in the wave record. For organization-only changes, refresh the core-file manifest and then run `docs/scripts/audit/build_uet_research_organization_registry_v2.py`.

Every new equation or operator must complete the F0–F8 sequence in the equation research
standard. A blocked upstream gate blocks physical interpretation and downstream promotion.
Exploratory work may continue only when it is explicitly labelled `DRAFT`, `CANDIDATE`,
`INTERNAL`, or `SIMULATION_ONLY`.

Before describing a standard theory as a special case, or describing two UET lanes as the same physical variable, run docs/scripts/audit/audit_uet_foundation_compatibility.py and read docs/core/UET_FOUNDATION_COMPATIBILITY_AUDIT.md. COMPATIBLE_CONDITIONAL is not a global physics proof; CONTRADICTION, CONFLICT, BLOCKED, and REJECTED_REDUCTION remain controlling blockers.

Do not use topic numbers as a work queue. Follow the dependency graph.

## Core symbol rules

- `C` is a system-state coordinate; it is not universally mass.
- `Phi` is an effective response variable; it is not a metric, ether, particle, or
  information substance.
- `Pi` is `∂t Phi`.
- `R` / `I_trace` is a derived causal/history observable with no feedback in the new mode.
- mass, density, charge, stress-energy, and physical energy require explicit lane mappings.
- UET-PRINCIPLE-001 is a candidate result-based persistence principle, not an
  intentional optimization law; its current path-cost implementation remains a
  normalized constitutive diagnostic.
- legacy `I`, `V`, `J_in`, and `J_out` must not be silently reinterpreted as `Phi`.

## Units and derivation rules

Every formula change must update the registry with its unit lane, variable meanings,
constant origin, derivation class, proof status, and failure mode. Normalized simulation
quantities must not be presented as SI physical quantities.

No constitutive ansatz, calibration relation, or benchmark anchor may be described as a
first-principles derivation.

## Compatibility and legacy work

Do not delete or silently rewrite legacy engines. Preserve compatibility adapters and
mark legacy equations as `LEGACY` or `COMPARATOR` in the registry. The historical
`docs/core/README.md` is not a current claim source until its wording is reconciled with
the foundation gate.

The older `docs/scripts/audit/validate_foundation.py` is a legacy validation runner. It is
not the foundation gate and its output must not be used as evidence that the theory is
stable or physically validated.

## Verification and artifacts

Before closing a wave:

- run the equation-foundation audit
- run the foundation compatibility audit when equation meaning, implementation, units, or limiting-case language changed
- run the relevant scientific verifier only if evidence-producing state changed
- check JSON parsing and dependency integrity
- run the organization registry `--check` when the organization control plane changes
- run `docs/scripts/audit/audit_uet_core_scientific_links.py --check` when owner/family
  disposition or equation-link metadata changes
- sync core docs and update logs to the controlling blocker
- record the wave in `WORK_LEDGER/YYYY/YYYY-MM-DD.md`

Do not hand-edit generated verification output. Do not hide failed gates with clipping,
fallback parameters, or renamed statuses.

## Git scope

Check `git status` before editing. Preserve unrelated user changes. Stage only the files
belonging to the current standards or equation wave. Commit one coherent wave locally;
do not push or open a pull request unless the user explicitly requests it.

## Foundation program extension: impact, effect, carrier, and persistence

The foundation program adds one mandatory distinction to the core workflow:

```text
physical impact -> generated trace R_gen -> declared carrier -> receiver/detector interaction -> effect -> observer record R_obs
```

- `impact` is a physical coupling or state change with a declared field, force, energy-momentum, mass-transfer, stress-energy, or other standard-physics counterpart.
- `carrier` is a lane-specific physical excitation or signal. Photon, neutrino, gravitational-wave perturbation, and matter-antimatter products must not be identified with `I_trace` by name alone.
- `effect` is a derived receiver-side input-output relation. It is not an independent field or substance, and it does not require source-mass transfer.
- `R_gen` is a physical/history trace generated by the dynamics. `R_obs` is a detector/observer record. An observer protocol alone must not alter the physical state.
- Receiver feedback is allowed only through an explicit receiver-dynamics operator with a declared input, units, conservation/ledger rule, and detector interaction. The current matter-space operator has no `R_gen` feedback edge.
- `C` remains a collective system-behaviour coordinate until a lane-specific map to density, charge, order parameter, or another standard quantity is closed. `C = mass` is never a universal identity.
- The hypothesis that a mass-bearing phase can terminate while a carrier or product continues is a candidate transition hypothesis. It requires a transition mechanism and conservation laws; speed alone never implies conversion into a photon.
- A non-closed effective subsystem must not be promoted to a claim that the whole universe is globally open. A closed-limit correspondence to standard mechanics or GR remains a target gate, not an established result.

The central registry and dependency graph are controlling. New impact/effect or carrier work must remain `CANDIDATE`, `INTERNAL`, `SIMULATION_ONLY`, or `BLOCKED` until F0-F8 are complete.
## Additional lane rules recorded 2026-08-01

- resource_selection_dynamic_game_v1 is a non-agentic interaction-selection
  comparator: interaction/payoff and cost vectors are constitutive inputs, not
  intent or a universal optimizer.
- matter_space_characteristic_cone_v1 is a selected normalized finite-cone
  candidate only. Its compact-support result does not promote the conserved-C
  changing-response branch or the default full operator.

## Physical organization v3

The canonical physical tree is the source-of-truth layout for new work:

- 00_governance/ owns navigation, registries, migration maps, and room routing.
- 01_contracts/ owns ontology, correspondence, units, derivation, and claim contracts.
- 02_equations/ owns canonical equation-family implementations.
- 03_lanes/ owns lane-specific models, comparators, and observable bridges.
- 04_proofs/ and 05_tests/ own proofs, verification, numerical, artifact, and regression tests.
- 06_data/ owns source packages, manifests, and derived inputs.
- 07_artifacts/ is the only canonical destination for generated outputs.
- 08_history/ owns update logs, research notes, and legacy research records.
- 99_review/ is the quarantine boundary for unassigned or ambiguous surfaces.
- Core tooling belongs under docs/scripts/core/, not under 06_data/.

Use docs/core/core_paths.py as the path authority and docs/core/core_compat.py for
compatibility loading. Numeric folders are documentation namespaces; do not invent a second
import scheme. Keep docs/core/__init__.py, AGENTS.md, README.md, and
CORE_FILE_INDEX.md as permanent root entrypoints.

For every new file, classify it, assign one owner and one canonical path, connect its
formula/source/verifier/artifact metadata, run the physical migration/path audit, update the
appropriate log and work ledger, then make a scoped commit. A file may be
MIGRATED_WITH_SHIM while its old import or link remains usable.

Organization state (MIGRATED, QUARANTINED, or BLOCKED) is independent of scientific
evidence state. Moving, renaming, indexing, or repairing links must never change an equation's
physics status, unlock a foundation gate, or promote a claim. Dirty user files are held back
until their owning change is explicitly included.

## Physical migration enforcement controls

The structural migration control plane has four executable checks:

- `docs/scripts/audit/audit_uet_core_paths.py` — canonical target, ownership, disposition and protected-entrypoint invariants.
- `docs/scripts/audit/audit_uet_core_imports.py` — public root-module and `docs.core` import smoke tests.
- `docs/scripts/audit/audit_uet_core_links.py` — active-core local Markdown link resolution; historical and quarantine areas are intentionally excluded.
- `docs/scripts/audit/audit_uet_core_migration.py` — runs the three checks and writes the combined enforcement artifact/report.

These checks are organization controls only. A PASS cannot promote a formula, evidence class or foundation claim.
## Bounded generated-artifact migration

Generated output migration is a separate organization wave. Use
`docs/scripts/audit/migrate_uet_core_artifact_family_v3.py` for one explicitly
resolved family at a time. The runner requires a switched generator, checks
actual legacy-path consumers, compares semantic payloads, preserves hashes, and
records the move in `00_governance/uet_core_artifact_migration_history.json`.

A generated-index reference is not an active reader once the generator is
refreshed, but unresolved active consumers block the move. If generator output
differs from the legacy artifact, stop; do not overwrite legacy work. A source
provenance refresh may be proposed only through an explicit review step, and
must never hide changes beyond declared metadata. The canonical output belongs
The machine-readable generator review queue is `07_artifacts/gates/uet_core_artifact_generator_review_queue.json`; it separates unresolved generator identity, active-consumer rewrites, generator-path switches, and already migrated records. Its `PASS_WITH_REVIEW_REQUIRED` state is an organization blocker, not a physics result.
under `07_artifacts/`; the old artifacts directory is an index/compatibility
boundary only. A migrated artifact remains `INTERNAL` or its existing evidence
class; organization migration never promotes physics claims.