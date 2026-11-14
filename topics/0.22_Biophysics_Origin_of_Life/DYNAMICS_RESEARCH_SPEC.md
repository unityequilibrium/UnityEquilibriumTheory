# Protein Folding Dynamics Research Spec: 0.22

## Research question

This lane asks how a protein moves from an incompletely structured chain to a
functional conformational basin, and how that path changes when the chain is
translated in a cell or interacts with chaperones.

The lane is not an AlphaFold replacement. AlphaFold is an endpoint/reference
for structure comparison only; it is not treated as a folding trajectory,
cellular mechanism, or dynamic law.

Current lane status: `source_ready_design_blocked / Claim ceiling B / WARN`.
The umbrella topic remains `Draft / Tier B / WARN`.

## Scope order

1. Intrinsic folding of small single-domain proteins.
2. Co-translational folding with nascent-chain and ribosome constraints.
3. Chaperone-assisted folding and non-equilibrium exchange.
4. Pathways, intermediates, kinetic traps, folding rates, and failure modes.

The historical 2-D HP lane remains a reduced exact control. It is not a
substitute for an atomistic model and has no biological structure mapping.

## State and observation contract

```text
X_micro = coordinates, velocities, solvent, ions,
          nascent-chain state, and chaperone state

X_micro -- lane-specific coarse graining --> C_l

C_l     = contact, secondary-structure, compactness, and native-basin
          coordinates; C_l is not universal mass, charge, or entropy

Phi/Pi  = candidate environmental or memory response and its time derivative
J_*     = explicitly declared translation, ATP/chaperone, solvent, or boundary
          exchange channels
R_gen   = derived trajectory/readout after evolution; no feedback by default
```

The existing UET objects are reused only through a protein-specific lane
adapter. No core axiom is changed by this spec.

| UET object | Protein lane interpretation | Boundary |
| :-- | :-- | :-- |
| `C_l` | collective conformational coordinate | not a universal order parameter |
| `Phi` | candidate environment/history response | not an information substance |
| `Pi` | `dPhi/dt` | derivative only until mapped to an observable |
| `Omega` | candidate effective landscape/readout | not SI free energy without closure |
| `J_in/J_out` | translation, ATP, solvent, and chaperone exchange | physical units and provenance required |
| `K_R` | candidate solvent/chaperone memory kernel | constitutive bridge, not microscopic derivation |
| `P_C` | conformational path-cost proxy | not measured power |
| `R_gen` | derived trajectory/record | no feedback into the state by default |

## Candidate dynamics

The first kinetic representation is a state-transition model:

\[
\frac{dP(z,t)}{dt} = \sum_{z'}
\left[k(z'\rightarrow z)P(z',t)-k(z\rightarrow z')P(z,t)\right].
\]

A later coarse-grained candidate may use:

\[
\tau_C\ddot C+\Gamma_C\dot C =
-M\frac{\delta\Omega}{\delta C}
+J_{translation}+J_{chaperone}+J_{environment}+\xi(t).
\]

Both are open candidates. Every parameter must declare ontology, unit,
origin, derivation class, observable mapping, uncertainty, and failure mode.
The atomistic baseline uses the declared standard force field before any UET
term is allowed to modify a trajectory.

## Planned hypotheses and baselines

| Label | Definition | Allowed interpretation |
| :-- | :-- | :-- |
| `H0` | standard atomistic MD with the frozen force-field contract | physics baseline |
| `H1` | UET readout computed from `H0` trajectories | explanatory mapping candidate |
| `H2` | UET effective coupling added only after unit and force mapping closure | future coupled candidate |
| `HP-control` | finite dynamic HP state graph with exact short-sequence oracle | reduced algorithmic control |

`H1` is readout-only. It must not be described as changing protein dynamics.
`H2` is blocked until the formula audit and physical correspondence gate pass.

## Wave gates

### Wave 0: source and runtime gate

- Freeze the source identity and selection policy in
  `DYNAMICS_DATA_MANIFEST.json`.
- Freeze engine, package, force-field, solvent, ion, platform, and seed policy
  in `DYNAMICS_RUNTIME_MANIFEST.json`.
- Require a source-backed cohort of 12 small single-domain proteins: 8
  development and 4 protein-level holdout entries.
- Require PDB chain/construct identity and measured folding kinetics where
  available; do not fill missing rows with synthetic data.
- Require a CPU smoke test and trajectory read/write test before any atomistic
  result is generated.

### Wave 1: intrinsic atomistic dynamics

- Start from native and explicitly documented unfolded ensembles.
- Use at least 16 independent replicas per starting ensemble.
- Record trajectories, hashes, energies, temperature/pressure, contacts,
  secondary structure, folded-basin occupancy, transition paths, MFPT,
  survival/hazard curves, and convergence diagnostics.
- Use conventional MD as the baseline and an explicitly declared enhanced
  sampling branch only after the runtime gate supports it.

### Wave 2: dynamic HP control

- Use a fixed local move set and a declared Metropolis, Glauber, or
  continuous-time transition rule.
- Check detailed balance in the equilibrium branch.
- Compare unbiased random, energy-biased, and centroid-biased search against
  exact short-sequence enumeration.
- Keep the result at `Claim Class C / data_class=synthetic`.

### Wave 3: UET dynamic mapping

Map atomistic trajectories to contact, secondary-structure, compactness,
native-basin, solvent-exposure, and contact-order coordinates. Test ablations
in this order: `C`, `C+Omega`, `C+Phi/Pi`, `C+exchange`, and
`C+persistence ledger`.

Pre-register the endpoint, kinetic, pathway, uncertainty, and baseline metrics
before reading the holdout rows. A result that does not outperform `H0` may
still be reported as an explanatory pathway analysis, but not as predictive
superiority.

### Wave 4: co-translational folding

Extend the state with nascent-chain length, translation rate, ribosome exit
constraint, chain emergence order, pause/stall events, and experimentally
observed intermediates. A source-referenced observation without a frozen raw
trace is not external validation.

### Wave 5: chaperone and non-equilibrium channels

Add `b = {unbound, bound, release, refold, aggregation-risk}` and explicit
ATP binding/hydrolysis, chaperone binding/unbinding, translation input, and
failure output channels. Do not impose global detailed balance on a system
with translation and ATP consumption.

### Wave 6: integration and falsification

Compare `H0`, `H1`, `H2` when eligible, HP control, intrinsic,
co-translational, and chaperone conditions. Remove gradient, memory,
exchange, persistence, ribosome, and chaperone terms one at a time. Keep
IDPs, multi-domain, membrane, ligand-dependent, disulfide-rich,
aggregation-prone, and under-sampled proteins as explicit failure boundaries.

## Initial source contract

The first source package targets PDB structures, KineticDB folding kinetics,
PFD experimental conditions, PFDB standardized kinetic records, and CASP
holdout/reference structures. The source URLs, terms, local-path state, hash
state, units, and benchmark roles are recorded in
`DYNAMICS_DATA_MANIFEST.json`.

At this wave no external files are downloaded and no source-backed cohort is
claimed to be present.

## Initial runtime contract

- Engine: OpenMM, exact version to be frozen at installation gate.
- Analysis: MDTraj.
- Enhanced sampling: openmmtools when the package and version are frozen.
- Force field: AMBER ff14SB.
- Solvent: explicit TIP3P water with explicit ions.
- Reproducibility: fixed seed list, immutable input hashes, ensemble-level
  reproducibility across hardware; bitwise trajectory identity is not required.
- Output: machine-readable run contract, input hashes, trajectory hashes,
  metrics, uncertainty, baseline, and limitations.

## Claim boundary

Allowed now:

- protein-folding dynamics research design;
- candidate lane-specific UET mapping;
- source-target and runtime-preflight status;
- finite 2-D HP internal benchmark as a reduced control.

Not allowed now:

- real protein folding result;
- biological free-energy or SI-energy claim from the HP model;
- AlphaFold replication or superiority claim;
- PDB/CASP validation;
- cellular mechanism confirmation;
- external replication or Claim Class D.

The controlling blocker is `source_locked_cohort_and_atomistic_runtime_missing`.
