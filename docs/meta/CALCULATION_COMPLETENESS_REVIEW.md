# Calculation and observation adoption review

## Public integration note (PR #37)

The publish worktree was sparse; missing on-disk paths were not all missing from
main. After expanding the existing checkout, only 28 direct Topic13 dependencies
needed their exact committed sources packaged. Five astronomy source identities
are now pinned to equal-hash public main `829c71502`, and the previous Core
contract is a hash-checked portable baseline instead of a local-only Git lookup.
Two offline admission contracts gained relational partitions; physical UNKNOWNs
and INCOMPLETE scope remain. The current generated inventory retains ten missing
or relocated historical baseline paths and does not certify full legacy coverage.
Changed Python tests: 205 pass; whole-diff contract check: 0 errors. Hosted CI is
the final integration gate, independent of scientific acceptance.

This is a methodological handoff, not a scientific gate. The generated
[inventory](calculation_completeness_inventory.json) is the source for current
coverage counts and the unreviewed queue. The
[baseline](calculation_completeness_baseline.json) preserves commit/branch lineage.

## Source boundaries

The editable checkout started on `codex/services/research-foundation-pilot` at
`35a01e65b6baf8a6ff34fae4a8744ccc3e3adf1d` with 452 pre-existing changes.
That initial capture continued on `codex/research/calculation-observation-standard`.
This is historical lineage, not the current branch. The subsequent W0-W9 sequence,
current checkout identities and open scope are recorded in the existing
[standards log](../topics/For%20Work/UPDATE_LOG.md#standards-restructure-w0-w9);
no additional checkout or unrelated dirty work is incorporated by adoption.
The origin/main value in the baseline is a cached ref, not a new remote fetch.

Topic13 October 15-17 evidence belongs to the distinct owner commit
`0f17012ffd6ad456c150b10e048efd868ce95588`. Those proofs/artifacts are referenced,
not copied, merged, regenerated or relabeled as this checkout's implementation.
LOCAL_ONLY evidence remains INCOMPLETE and may be unavailable in a fresh clone;
that is a visible evidence gap and never grounds physical acceptance.

## Pilot dispositions

| Path | Review consequence | Scientific consequence |
| --- | --- | --- |
| Matter-space / observer | Existing normalized dynamics, nonnegative dissipation and read-only trace behavior are distinguished from receiver dynamics. Physical detector completion remains open. | No physical entropy identity, complete-information trace or SI detector claim. |
| He-4 | Frozen normal-state calibration does not supply a condensed He-II response operator. State/current matching, protocol and source/readout admission remain open. | Existing physical BLOCKED state retained; not a universal no-go or proof of nonidentifiability. |
| Nonlinear invariants | Reuse original L,p,B algebra rather than requiring an absolute field coordinate for every observable. | Formal scope retained; ordinary material poles remain alternatives. |
| Nonlinear physical application | Independent mechanical-kernel/source/readout package is not admitted. | No scoring, new data access, fitting or alpha/SI promotion. |
| Published H0 comparison | Published Planck/SH0ES scalars are not raw HST exposures. Upstream corrections remain unaudited here. | No raw-data replication, spacecraft correction applied to H0 or universal Hubble-tension resolution. |
| Galaxy catalog | SPARC/LITTLE THINGS working copies need source/product/frame/calibration lineage review. | Catalog coverage alone is not an independent mass/dynamics validation. |
| Dynamic frame | Galaxy, spacecraft and heuristic-fit inputs remain separate sub-observables. | No transfer of a fitted drag hypothesis into a general cosmology result. |

## Checks and remaining pre-existing drift

### W6 adoption review, 2026-10-19

Core uses a nonadditive relational aggregate; He4 and nonlinear physical contracts
now declare provisional admission topology without promoting UNKNOWN physical state,
source, readout or feedback. Formal invariant and coherent-shear preparation remain
FORMAL, without fake equipment/data. See [Topic13 design section 11](../topics/0.13_Thermodynamic_Bridge/RESEARCH_DESIGN_OBSERVABLE_DISCRIMINATION_2026-10-17.md#11-standards-adoption-w6-separate-topic13-routes-and-prerequisites)
for exact route-specific evidence, prerequisite, stop and owner boundaries.

In particular the old O2/He4 Core composition gate is not the later frozen-bundle
second-sound operator, graphite coherent shear is not thermal TTG, and an absolute
Phi scale is not an unconditional prerequisite for the invariant-only test. Full
TTG contract migration remains a visible W7 coverage gap. No physics status changes.

The standalone contract suite checks schema/identity enforcement and synthetic
observer controls. Selected existing matter-space tests check physical-state
dependence, trace/history isolation and nonnegative dissipation. No scientific
artifact producer or physical threshold was changed.

The existing topic standards audit also detects unrelated readiness-count/status
drift and `For_Work`/`__pycache__` discovery problems in this checkout. The existing
equation-foundation audit fails on registry/protocol references to pre-migration
root paths. These failures remain visible; the new checker does not repair or
whitelist them, and no foundation gate is promoted.

## Next work

### W7 route triage, 2026-10-19

The generated inventory now extends the historical seed with current equation
registry entries, all discovered numbered-topic packages (including missing specs),
scoped contracts and grouped unassigned research surfaces. Core formal contract,
lane, proof and research-note documents are included as candidates. File/route
counts are not experiment counts. The inventory records generator/schema/source
identities; read its `inventory_scope` before interpreting coverage.

Explicit migration aliases reconnect old paths with canonical implementations;
ambiguities fail visibly. Package/family links remain RELATED_ONLY_NOT_PACKAGE_COVERAGE,
with missing/uncovered paths and an evidence-matched adoption action. A complete
scoped contract may be reusable without certifying its topic; UNKNOWN prerequisites
wait; unreviewed or stale sources need targeted inspection, not a blind rerun.

Discovery is not a scientific review of every claim or every historical idea. No
directory is declared inactive by its name and no claim is automatically reduced,
promoted or made history-only. Those decisions require local substantive evidence.
The live directory count may disagree with old readiness/index prose; that drift
is reported, not silently "fixed" by changing a scientific status or unrelated file.

Next: W8 adopt the same method on the existing H0, galaxy and dynamic-frame
contracts, enforce changed-path coverage and preserve actual data-product scope.
W9's locked research-return decision need not wait for every queued archival review.

### W8 astronomy and changed-input enforcement, 2026-10-19

The three existing astronomy contracts now distinguish offline product input and
analysis configuration from raw physical source/instrument states. Source-code
evidence is pinned to `f7ba82307ae4afc698cccc9533d1056782004b9c`; unrelated dirty
scientific producer work is not integrated or certified. Selected unchanged local
input products have explicit identities; hashes do not establish upstream validity.

| Study | Current product/method boundary | Required next review |
| --- | --- | --- |
| 0.3 | Published Planck/SH0ES H0 scalars, embedded in the verifier, plus source-lock/CODATA policy; not HST exposures | Scalar/source-record parity, covariance/likelihood assumptions and physical beta-law justification. No new velocity correction to an already derived scalar |
| 0.1 | SPARC working-copy primary input; LITTLE THINGS is not automatically used by that primary verifier | Row/extraction, units, inclination/distance and mass-model/error provenance; no raw-data replication claim |
| 0.26 | Laniakea landmark visualization/provenance; Cosmicflows/Pioneer files have separate non-acceptance roles | Source/frame/preprocessing and actual residual/competitor gates. Producer class D is not supported as external replication by this visualization; processing gap remains until owner repair |

No upstream correction was silently marked applied; all physical contracts remain
INCOMPLETE. Offline read-only processing is not a claim of universal physical
isolation. Topic10/23 are not opened merely because of their numbers; no necessary
dependency from this adoption wave was established.

CI now distinguishes source JSON/tabular/binary data from result JSON: new/changed
inputs need classification/identity, not fabricated result fields. Result payloads
still require exact contract lineage. Workflow-only/shared-input changes trigger
the research check, explicit fail-fast preserves failures, and nightly checkout
fetches pinned ancestry. YAML parsing and local commands are verified; hosted job
execution and remote required-check configuration are not claimed or changed.

## W0-W9 completion audit — 2026-10-19

This audits the actual adoption-plan deliverables, not the validity of UET or the
completion of every scientific item in the queue. W7 explicitly requires a reasoned
discovery/triage disposition, not retroactive certification of all old results;
W9 explicitly permits a precise prerequisite outcome. No narrower success criterion
is substituted for a scientific result: those result claims remain open.

| Requirement | Current authoritative evidence inspected | Completion and retained limits |
| --- | --- | --- |
| W0 current lineage and baseline without extra checkout/copies | Standards log W0-W1, daily ledger, branch/HEAD/worktree/status outputs | Current versus historical and cross-worktree evidence separated; 452 unrelated paths preserved, no copied raw/scientific payload |
| W1 separate academic practice, operations, UET propositions and studies; assign owners | 00 entrypoint ownership/source map; source-level conflicts in standards log; final root/routing/Core conformance commit 6c259e611 | Major requirements have owners; stale architecture links and universal-chain wording repaired, compatibility history retained |
| W2 applicable method profiles and evidence types | Standards 01/04/14/18/20/25/32 and profile tests | Formal proof needs no invented apparatus/data; fit/prediction, reproduction/independent data, peer-review/truth, review competence and negative/equivalent/inconclusive outcomes distinguished; existing F gates preserved |
| W3 one proposition's authorship and translation | Topic13 design section 9, source/comparator identities and marked local log | Author boundary intent distinguished from AI schema and constitutive ansatz; unapproved physical interpretations remain unapproved |
| W4 relationship-dependent roles, nested ownership, old-record compatibility | Schema/checker, standard 30/template 31, regression cases, pinned old-contract mapping | Duplicate declared state ownership, invalid containment/path/backaction scope and unbound baseline changes rejected; semantic energy/physics adequacy still needs review |
| W5 actual Core pilot and comparator decision | Core matter-space contract/initializer, Core log and Topic13 design section 10 | Source state/functions unchanged; aggregate adds no state/energy; ordinary-comparator limitation and UNKNOWN physical receiver preserved |
| W6 He4/O2, TTG, coherent-shear and nonlinear distinctions | Topic13 design section 11; pinned 0f17012ff evidence and two migrated physical contracts | Each route names evidence/prerequisite/stop; old bounded Core composition does not admit the later physical operator; formal invariants do not require a universal absolute Phi scale |
| W7 all discovered routes have reasoned dispositions, not file-count science | Existing generated inventory: source identities, inventory_scope, 120 route/package/contract/surface units and adoption fields | No missing action/reason/next step; partial links do not certify a family; unknown history/private prose limits explicit. 40 current numbered folders versus old 41-topic prose is not a readiness promotion |
| W8 astronomy and changed-path CI | Three existing astronomy contracts/initializer/local logs; input/result tests; PR/nightly workflow YAML and local commands | Offline products distinguished from raw instruments; inputs identified without output-field pollution; result lineage preserved; pinned code/history and visible failures wired. Physical gaps, dirty-source separation and dynamic-frame claim-label repair remain open |
| W9 finite research-return decision | Topic13 design section 12 and marked local log; existing graphite contract payload 7a1e0986... validates | Frozen feasibility rule reaches no physical scoring for this declared packet; same-state joint observation/preparation/state/error packet is the exact reopening prerequisite. No new derivation, numerical forecast or global data-absence claim |
| Verification, compatibility and unchanged scientific evidence | 58 relevant tests PASS, current/changed-path checks, read-only inventory byte/freshness checks, YAML parse, scoped links/whitespace; foundation audit FAIL/BLOCKED remains visible | Local methodology/control implementation verified in scope. No full old scientific rerun, physics threshold relaxation, hidden claim promotion, hosted-CI success, remote ruleset change, email or push claimed |

The full generated inventory was compared against a fresh read-only build after
the conformance changes and matches current source/discovery identities. Scientific
producers/equations/data/results were not rewritten by these waves; identified
dirty code and historical outputs remain with their owners. Local contract/structural
checks report zero errors, but scientific incompleteness is not an error to hide:
all physical promotion restrictions and the foundation's 224 stale-reference errors
remain explicit. The broad scientific queue is future work, not silently discarded.

Final handoff: the operating/adoption plan is implemented with an auditable W9
prerequisite finish. Do not restart unchanged blocked research automatically. Reopen
the named scientific route on its declared evidence change; independent bounded
formal/normalized work may continue without pretending those physical gaps are closed.

Review queue order is Core/Topic13 first, then the three astronomy packages, then
other topics by dependency and claim importance. Every discovered legacy path is
unreviewed until it has a reviewed contract or an explicit support disposition.
Resolve owner lineage before promoting imported Topic13 evidence. For any future
scientific wave, name the missing physical input or operator before starting a
new search, derivation or run. Existing negatives and unchanged evidence are reused.
