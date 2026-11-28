# Unity Equilibrium Theory (UET) v0.9.1

> ## 🇹🇭 [อ่านฉบับภาษาไทย คลิกที่นี่ → README.th.md](README.th.md)
>
> The Thai and English files have the same content. Edit both together.

![Evidence](https://img.shields.io/badge/claims-59_L1_·_25_L2_·_6_FAILED-blue)
![Topics](https://img.shields.io/badge/research_topics-40-blue)
![License](https://img.shields.io/badge/License-MIT-green)

UET is a research program that turns one idea into a calculation procedure:
a system lasts only as long as it manages the resources it uses, and the same accounting should work for any system.
That covers nested systems (a cell inside an organism inside an ecosystem), resources that several systems share, and time as one of the resources.

UET is **not a claim of new physics**. It is a **synthesis**: it takes established, citable results from thermodynamics, gravity,
open-system physics and ecology, joins them into one chain of reasoning, and checks two things at every step:
whether each borrowed result is used within the conditions of its original source, and whether the joined pieces still agree with each other.
Every claim is then compared with real, published data, and the outcome is recorded whether it passes or fails.

## Contents

1. [The core equations](#1-the-core-equations)
2. [The author's reasoning](#2-the-authors-reasoning)
3. [How UET is built from existing theory](#3-how-uet-is-built-from-existing-theory)
4. [Evidence so far](#4-evidence-so-far)
5. [Research topics](#5-research-topics)
6. [How the research is done](#6-how-the-research-is-done)
7. [Repository map](#7-repository-map)
8. [Reproduce the checks](#8-reproduce-the-checks)
9. [What changed in v0.9.1](#what-changed-in-v091)

---

## 1. The core equations

UET started from one balance, written in the v0.9.0 README as

$$\Omega = C \cdot I$$

where Ω is the balance a system seeks, C its connection or interaction, and I the cost of being separate.
That picture is kept, unchanged, in [`docs/history/LEGACY_CLAIMS.md`](docs/history/LEGACY_CLAIMS.md).
The current equations make it calculable in three layers. Full definitions, code locations and tests are in
[`core/THEORY_CARD.md`](core/THEORY_CARD.md) and [`core/AUTHOR_PROPOSITION.md`](core/AUTHOR_PROPOSITION.md).

### Layer 1: matter exchanges energy with the structure of space

The parent action (natural units, signature −+++; δ = φ − φ\*, |χ|² = χ₁² + χ₂²):

$$S = \int d^4x \sqrt{-g}\Big[\tfrac{F(\varphi)}{2\kappa}(R - 2\Lambda) - \varepsilon\big(\tfrac{1}{2}k(\nabla\varphi)^2 + U(\varphi)\big) - \tfrac{1}{2}Z(\nabla\chi_A)^2 - W(|\chi|^2) + \tfrac{1}{2}\varepsilon h\,\delta\,|\chi|^2\Big]$$

$$F(\varphi) = 1 + \varepsilon\xi\delta^2,\qquad U = \rho_* + \tfrac{1}{2}\mu^2\delta^2 + \tfrac{1}{4}\lambda_\varphi\delta^4,\qquad W = \tfrac{1}{2}m^2|\chi|^2 + \tfrac{1}{4}\lambda_\chi|\chi|^4$$

| Symbol | Meaning |
|---|---|
| χ | Matter, an O(2) field |
| φ | The response field of space, coupled to curvature R through F(φ) |
| h | The portal: the only term through which matter and the response field exchange energy |
| ξ, μ, λ | Shape of the response field's coupling and potential |

The metric, response and matter equations follow from this action by derivation (checked symbolically, claim `C_PARENT_EOM_DERIVED`, L1).
Its symmetries give the conserved quantities Noether's theorems require: the matter charge (O(2)) survives the exchange with space,
total energy of matter, response field and geometry is conserved while matter energy alone is not, momentum, angular momentum and the boost charge are conserved, the boost charge because both fields share one light cone (claim `C_NOETHER_COVERAGE`, L1).
Matter alone does not conserve energy; matter plus the response field does.

### Layer 2: an open system burns free energy and leaves a trace

$$dS_{\text{sys}} = d_eS + d_iS,\quad d_iS \ge 0 \qquad P = T\,\dot S_{\text{prod}} \qquad \Sigma = I + D$$

A system inside an environment loses free energy F at burn power P. The entropy it produces, Σ, splits into a readable record I
and a potential difference D (claim `C_R3_TRACE_RECORD_PLUS_POTENTIAL`, L1).
Friction, noise and the second law come out of a closed system without being added by hand (claim `C_LAYER2_OPEN_FROM_CLOSED`, L1).
Taking the matter field χ of layer 1 as a thermal bath, the layer 1 action itself gives the response field φ friction and noise that obey
the fluctuation-dissipation (KMS) relation, so the friction is fixed by the portal coupling rather than chosen (claim `C_L2_FROM_ACTION`, L1).

### Layer 3: selection by how resources are managed

$$\tau = \int \frac{dF}{P(F)} \qquad N = b\,\tau \qquad \frac{dx_i}{dt} = x_i\,(f_i - \bar f)$$

A system's lifetime τ comes from its stock F and how its burn power P depends on that stock.
The number observed, N, is the birth rate b times the lifetime. Among systems that reproduce and share resources,
the one that can live on the lowest resource level R\* wins; with two resources a stable mixed equilibrium appears
(claims `C_L3_SELECTION_FORMAL` and `C_L3_BURN_LAW_SELECTION`, L1).
From the layer 1 action, the death rate 1/τ is the layer 2 damping rate and the capture rate comes from the same one-loop spectral function:
an isotropic pool of any distribution can only damp a mode, while a flowing stream feeds exactly the modes slower than the flow (the Cherenkov condition),
and the lowest R\* wins as before (claim `C_L3_FROM_ACTION`, L1).
The pool's loss rate also follows from the action (χ self-coupling), but its supply does not: with only the action's fields nothing persists,
and a structure stays alive only if its boundary supplies more than S\* = δR\*ₘᵢₙ (claim `C_L3_SUPPLY`, L1).

**What the equations do not yet do:** layer 2 is derived from the layer 1 action for one channel only, and layer 3 only for its capture and death rates, so the three layers are not yet one action,
and the layers do not yet give a number that the established theories do not (section 3).

## 2. The author's reasoning

The author's own statement is in [`core/AUTHOR_PROPOSITION.md`](core/AUTHOR_PROPOSITION.md). In short:

1. A structure that has to burn energy to keep its shape (a dissipative structure) cannot stay closed, or the second law erodes it.
2. "Open" means matter exchanges energy with the structure of space it sits in, not with something outside the universe.
3. Nothing is ever at rest, so every system is always using energy.
4. Using energy is behavior. A system that burns fast lives short; one that manages its stock lives long.
5. Systems that manage resources badly run out and disappear, so what we observe is what was selected by persistence.
   This is selection, not learning.
6. Using energy leaves a trace in the environment that can be read later.
7. The working tool is equilibrium between interacting systems, in the sense of Nash equilibrium in a dynamic game.

The application goal (author, 2026-11-17): if the equations show what lets a system persist,
use them to improve how real systems use their resources, and test that on real data, topic by topic.

## 3. How UET is built from existing theory

The equations are not derived from pure mathematics. Each step of the reasoning above borrows a published result,
and the research checks whether it was borrowed correctly.
The full audit, with every source and verdict, is [`core/SYNTHESIS_AUDIT.md`](core/SYNTHESIS_AUDIT.md).

| Step | Borrowed result (source) | Condition in the source | How UET uses it | Verdict |
|---|---|---|---|---|
| 1 | Second law; open-system entropy balance dS = dₑS + dᵢS (Prigogine) | Isolated system / system in contact with surroundings | Structures that must burn energy have to be open | Correct after the author narrowed it to dissipative structures |
| 2 | Subsystem coupled to an environment (Caldeira & Leggett, *Physica A* 121, 587, 1983) | Large environment in equilibrium at temperature T | Matter alone is an open system; matter plus environment is closed | Correct (friction, noise and the second law appear without being added) |
| 2, 6 | Gravity responds to matter, G = κT (Einstein 1915); scalar-tensor gravity (Damour & Esposito-Farèse, *PRL* 70, 2220, 1993) | Conservative field theory | Matter writes its history into the curvature of space | Correct (derived; checked on the Sun, T006) |
| 6 | Landauer's principle (Landauer 1961) | Erasing information in contact with a bath | "Using energy writes information" | Needs correction: bits = Σ/ln2, split into record and potential difference (Esposito et al., *NJP* 12, 013013, 2010) |
| 5 | Little's law, N = λW (Little 1961) | Steady state | Number observed = birth rate × lifetime | Correct (tested on stars and isotopes) |
| 4 | Lifetime = energy stock ÷ burn rate | Constant burn rate | τ = F/P for any system | Limited: passive systems need τ = ∫dF/P(F) |
| 5 | Lowest R\* wins the resource (Tilman 1982; MacArthur 1970) | Self-reproducing systems sharing a resource | What manages resources best remains | Limited to self-reproducing systems (life, lasers), not stars |
| 7 | Nash equilibrium / evolutionarily stable strategy (Maynard Smith & Price 1973) | Payoff depends on what others choose | Equilibrium between systems | Limited: needs at least two resources for a real mixed equilibrium |
| 3 | Nothing is at rest (third law, zero-point motion) | No motionless state | Λ_eff > 0, so there is no static solution | Correct in the sense the author chose |

Joining the pieces exposed one real conflict: gravitating systems have negative heat capacity, so a closed system with gravity
builds structure while its entropy rises (Lynden-Bell & Wood 1968). The author accepted the narrower wording in step 1 as a result.
A second junction is still open: Caldeira–Leggett needs an environment with a temperature, and general relativity gives space none
except at horizons. The current reading is that space keeps the record and radiation and matter absorb the heat.

### Nearest known theory for each layer

Each layer reduces to a theory that already exists
(result [`R_B4_DISTINCTNESS_AUDIT`](docs/standard/results/R_B4_DISTINCTNESS_AUDIT.json)):

| Layer | Nearest established theory |
|---|---|
| 1. Exchange | Damour–Esposito-Farèse scalar-tensor gravity with a Yukawa portal |
| 2. Open system | Caldeira–Leggett open-system mechanics, Prigogine entropy production |
| 3. Selection | Tilman resource competition; multimode laser rate equations (term for term) |

At the level of the action there is **no difference yet** from the established class.
**UET has no prediction of its own yet**: the one cross-layer effect without a standard counterpart depends on three free parameters.
What UET can add is a tested map of where one set of rules holds across fields, and where it fails.

## 4. Evidence so far

Levels follow [`docs/STANDARD.md`](docs/STANDARD.md): `L1` internally consistent, `L2` confronted with external data, `L3` externally replicated.
The registry is [`docs/standard/claims.json`](docs/standard/claims.json) (90 claims: 59 at L1, 25 at L2, 6 FAILED; none at L3).
Test criteria were committed and approved before each comparison. None of these comparisons was blind.

**Failed** (kept as results, not hidden):

| Test | What was tested | Outcome |
|---|---|---|
| T015 | Superfluid He II as the condensed phase of the parent action's matter field, at tree level (the lane Topic 13 assumed) | FAILED: sound speed 848 m/s calculated vs 233.1 m/s measured, 3.6 times too high |
| T018 | Animal lifespan = one reserve per gram ÷ metabolic rate, the same in every species (author's scope, 2026-11-17) | FAILED: birds use about 2.5 times more energy per gram over their lifespan than mammals of the same mass |
| T024 | Intervals between lighting innovations shrink with world population as N^-0.27 (urban scaling, Bettencourt et al. 2007) | FAILED: slope -1.43 (95%: -2.14 to -0.72), consistent with Kremer's (1993) -1; the synthesis borrows Kremer for innovation against world population |

**Confronted with data (L2):**

| Test | System (field) | Outcome |
|---|---|---|
| T001 | Binary pulsars (gravity) | L2 PASS: excludes the coupling range that maps to DEF scalarization; other values stay allowed |
| T002 | Globular-cluster star ratio (astronomy) | L2 INCONCLUSIVE: 1.467 ± 0.023 calculated vs 1.39 ± 0.03 observed, 2.05σ |
| T005 | Fifth-force searches (gravity) | L2 PASS: bounds the portal coupling, g_c < 5.1×10⁻¹⁰ eV (torsion balance) |
| T006 | The Sun's mass loss (gravity) | L2 PASS: −8.76×10⁻¹⁴/yr calculated vs −6.13×10⁻¹⁴/yr MESSENGER, z = 1.48 |
| T007 | Diatom chemostats (ecology) | L2 PASS: Si/P boundaries 86.9 and 6.2 vs about 80 and 6 observed |
| T008 | White dwarf luminosity function (astronomy) | L2 PASS: slope 0.286 calculated vs 0.320 observed |
| T009 | ²³⁸U–²³⁴U decay chain (nuclear) | L2 PASS: half-life 245,670 ± 260 yr from abundances vs 244,900 ± 1,340 yr measured |
| T010 | GW170817: gravitational waves and light from one event (gravity) | L2 PASS: same speed within the bound −3×10⁻¹⁵ to +7×10⁻¹⁶ |
| T011 | Pulsating stars in binaries (astronomy) | L2 PASS: timing delay equals light-travel age from the orbit, ratio 1.006 and 1.021 |
| T012 | Quenched quantum many-body chain (quantum) | L2 PASS: correlations need contact through a common past, not direct contact only |
| T013 | Ives–Stilwell test with ⁷Li⁺ ions at 0.338c (relativity) | L2 PASS: ε = (1.47 ± 2.30)×10⁻⁹, consistent with the Lorentz time transformation |
| T023 | Lifetime energy of bats against birds (biology) | L2 INCONCLUSIVE: bats 1.96 times other mammals but below birds; flight explains about 60% of the bird offset |
| T025 | T023 repeated with a phylogenetic correction (PGLS on a TimeTree tree; biology) | L2 INCONCLUSIVE: central values unchanged (d_bat = 0.24) but intervals about 10 times wider (d_bat −0.31 to 0.78); with phylogeny counted the data cannot decide |
| T026 | Yeast on sucrose: shared glucose at the cooperative-growth switch (trace feedback; biology) | L2 INCONCLUSIVE: predicted switch at or below 1.6 mM glucose; the comparison figure reports a 23 h mean growth rate that never reaches the threshold (card-design error); two exponential rates lean against the prediction |
| T027 | Yeast switch glucose with exponential growth rates (retest of T026; biology) | FAILED: wild-type yeast reaches its fast rate near 16 mM glucose, ten times above the trace-model prediction of 1.6 mM; the well-mixed trace reading does not explain yeast cooperative growth |
| T028 | Does selection raise the readable fraction of energy-written bits? (genome bits per division energy against Ne; biology) | L2 INCONCLUSIVE: only five species carry both energy cost and Ne (eight needed); slope +0.83 with 95% CI -0.62 to 2.29 |
| T022 | Michelson–Morley and Kennedy–Thorndike tests (relativity) | L2 PASS: two-way light speed independent of orientation (z = 0.50) and of lab velocity (z = 1.30); with T013 the whole Lorentz transformation is tested |
| T016 | MICROSCOPE equivalence-principle test (gravity) | L2 PASS: bounds the portal to g_c < 1.16×10⁻¹⁵ eV, 11.6 times tighter than T005 |
| T017 | Yeast cell cycles (biology) | L2 PASS: doubling time from single-cell cycle times matches the counted one in all five conditions |
| T019 | Eöt-Wash equivalence-principle data (gravity) | L2 PASS: bounds the portal to g_c ≤ 1.30×10⁻¹² eV for ranges 2 m to 10⁵ m |
| Route B | Lunar laser ranging (gravity, AI proposal) | L2 PASS: bounds a coupling to free-energy destruction, time constant ≤ 1.46×10⁸ yr |
| T021 | Succession of lighting technologies (economics) | L2 PASS: no successor used more energy and more work hours per lumen-hour than what it replaced |
| T029 | Black-hole mergers in GWTC: mass radiated (gravity) | L2 PASS: 225 of 227 nearly non-spinning mergers radiate between the inspiral loss 0.0572 eta and the area-theorem cap; none above the cap; the inspiral alone is about a third of the loss (GR-derived final masses, weak test) |
| T040 | Dark-energy w(a) of the parent action against DESI DR2 BAO and Pantheon+ supernovae (cosmology) | L2 PASS: fits as well as a free linear w(a) (Δχ² = 0.03) and better than ΛCDM by Δχ² = 5.1; best thawing point w0 = −0.90, wa = −0.12; no CMB used |
| T041 | Same w(a) family with the CMB added: Planck 2018 distance priors (Chen et al. 2019) + DESI DR2 BAO + Pantheon+ (cosmology) | L2 PASS at the edge: Δχ² against a free linear w(a) = 3.94 (limit 4); better than ΛCDM by only 1.5; best point near ΛCDM (w0 = −0.97, wa = −0.05) on the grid edge; background only |

Several of these only bound UET's free parameters or pass because standard physics passes; none is a prediction of UET alone.
Failures are recorded the same way as passes; see [`docs/standard/results/`](docs/standard/results/).

## 5. Research topics

Each numbered folder under [`topics/`](topics/README.md) asks how the UET accounting applies to one field.
"Question studied" is what the topic works on; the earlier headline claims for each topic are in
[`docs/history/LEGACY_CLAIMS.md`](docs/history/LEGACY_CLAIMS.md) and are not current results.
"Package" is the documentation tier from [`topics/README.md`](topics/README.md) (A = most complete, D = concept only); it is not an evidence level.
No topic result has been raised to an evidence level under Standard v2 yet, except where a claim is named.

### Core research (0.0–0.26)

| ID | Topic | Question studied | Package |
|---|---|---|---|
| 0.0 | [Grand Unification](topics/0.0_Grand_Unification/) | Whether one balance law can link the other topics | C |
| 0.1 | [Galaxy Rotation](topics/0.1_Galaxy_Rotation_Problem/) | Galaxy rotation curves (SPARC) without added dark matter | A |
| 0.2 | [Black Holes](topics/0.2_Black_Hole_Physics/) | Horizons and black hole shadows | B |
| 0.3 | [Hubble Tension](topics/0.3_Cosmology_Hubble_Tension/) | The mismatch between early- and late-universe expansion rates | B |
| 0.4 | [Superconductivity](topics/0.4_Superconductivity_Superfluids/) | Phase locking in superconductors and superfluids | B |
| 0.5 | [Nuclear Binding](topics/0.5_Nuclear_Binding_Hadrons/) | Binding energy and stability of nuclei and hadrons | B |
| 0.6 | [Electroweak](topics/0.6_Electroweak_Physics/) | Electroweak parameters such as the W boson mass | B |
| 0.7 | [Neutrinos](topics/0.7_Neutrino_Physics/) | Neutrino mass and mixing (NuFIT) | B |
| 0.8 | [Muon g−2](topics/0.8_Muon_g2_Anomaly/) | The muon anomalous magnetic moment | B |
| 0.9 | [Quantum Nonlocality](topics/0.9_Quantum_Nonlocality/) | Bell correlations | B |
| 0.10 | [Fluid Dynamics](topics/0.10_Fluid_Dynamics_Chaos/) | Turbulence and chaos in fluids | B |
| 0.11 | [Phase Transitions](topics/0.11_Phase_Transitions/) | Critical points and critical exponents | B |
| 0.12 | [Vacuum Energy](topics/0.12_Vacuum_Energy_Casimir/) | Vacuum energy and the Casimir effect | B |
| 0.13 | [Thermodynamic Bridge](topics/0.13_Thermodynamic_Bridge/) | How energy use links to information and retained state (He-4, graphite) | B |
| 0.14 | [Complex Systems](topics/0.14_Complex_Systems/) | Emergence of order from noise | B |
| 0.15 | [Cluster Dynamics](topics/0.15_Cluster_Dynamics/) | Galaxy cluster dynamics and the virial theorem | B |
| 0.16 | [Heavy Nuclei](topics/0.16_Heavy_Nuclei/) | Stability of superheavy nuclei | B |
| 0.17 | [Mass Generation](topics/0.17_Mass_Generation/) | The particle mass hierarchy | B |
| 0.18 | [Mathnicry](topics/0.18_Mathnicry/) | Mathematical problems read through the UET structure | B |
| 0.19 | [Gravity & GR](topics/0.19_Gravity_GR/) | Gravity, the equivalence principle and the CODATA checkpoint | B · claim T001 at L2 |
| 0.20 | [Atomic Physics](topics/0.20_Atomic_Physics/) | Atomic spectra and the Rydberg constant (NIST) | B |
| 0.21 | [Yang–Mills](topics/0.21_Yang_Mills_Mass_Gap/) | The mass gap | A |
| 0.22 | [Origin of Life](topics/0.22_Biophysics_Origin_of_Life/) | Biophysics, protein folding and error correction | B |
| 0.23 | [Unity Scale Link](topics/0.23_Unity_Scale_Link/) | Stress-testing UET across scales; collecting ways it can fail | B |
| 0.24 | [Artificial Intelligence](topics/0.24_Artificial_Intelligence/) | AI systems as resource-using systems | B |
| 0.25 | [Strategy & Economics](topics/0.25_Strategy_Power_Economics/) | Energy, time and resources in economies and technology | A · claim T021 at L2 |
| 0.26 | [Cosmic Dynamic Frame](topics/0.26_Cosmic_Dynamic_Frame/) | A drag-like term for galaxy dynamics | B |

### Future concepts (0.27–0.39)

These are exploratory applications. They do not count toward the theory's credibility until they carry real data.

| ID | Topic | Question studied | Package |
|---|---|---|---|
| 0.27 | [Cold Light](topics/0.27_Cold_Light_Hologram/) | Slowing and storing light | D |
| 0.28 | [Material Synthesis](topics/0.28_Material_Synthesis/) | Resonant manufacturing, graphene from waste carbon | D |
| 0.29 | [Ocean Recovery](topics/0.29_Ocean_Recovery/) | Reducing ocean acidification | D |
| 0.30 | [Mega Flora](topics/0.30_Mega_Flora_Biotech/) | Nutrient delivery for plant growth | D |
| 0.31 | [SpaceTime Propulsion](topics/0.31_SpaceTime_Propulsion/) | Gravity-assist and high-speed trajectories | D |
| 0.32 | [Micro Fusion](topics/0.32_Micro_Nuclear_Fusion/) | Small-scale p-B11 fusion confinement | D |
| 0.33 | [Battery Tech](topics/0.33_Battery_Tech/) | Battery energy density | D |
| 0.34 | [Nanofabrication](topics/0.34_Information_Centric_Nanofabrication/) | Information-guided assembly at small scales | D |
| 0.35 | [Digital Automation](topics/0.35_ICN_Digital_Automation/) | Digital twins and automated production | D |
| 0.36 | [Orbital Manufacturing](topics/0.36_Orbital_Manufacturing/) | Manufacturing in orbit | D |
| 0.37 | [Quantum Photovoltaics](topics/0.37_Quantum_Photovoltaics/) | Solar-capture coatings | D |
| 0.38 | [Bio-Synthetic Integration](topics/0.38_Bio_Synthetic_Integration/) | Joining biological and synthetic materials | D |
| 0.39 | [Bio Smart City](topics/0.39_Bio_Smart_City/) | Cities as resource-using systems | not yet indexed |

## 6. How the research is done

The controlling rules are [`docs/STANDARD.md`](docs/STANDARD.md) (Research Standard v2). In brief:

- Each claim names its nearest known theory and what differs from it.
- A Test Card fixes numeric pass and fail criteria, and the author approves it, before any external data is compared.
- Data used to fit a model is never reused to test it. Raw external data is hash-locked in [`docs/standard/data_manifest.json`](docs/standard/data_manifest.json).
- AI agents assist with derivations, code and drafting. They cannot approve a card or raise a claim's level.
- Interpretations by AI are labelled as such and do not replace the author's intent.

## 7. Repository map

| Path | Contents |
|---|---|
| [`core/`](core/README.md) | Equations, theory and author cards, physics tests, calculation contracts |
| [`topics/`](topics/README.md) | Numbered research topics, each with its own data, code and results |
| [`docs/standard/`](docs/standard/) | Machine-checked claims, Test Cards, results and data manifest |
| [`docs/`](docs/README.md) | Standard, supporting documents and scripts |
| [`docs/history/`](docs/history/LEGACY_CLAIMS.md) | The v0.9.0 page and its earlier claims, unreviewed |
| [`WORK_LEDGER/`](WORK_LEDGER/) | Daily work history |

## 8. Reproduce the checks

```bash
git clone https://github.com/unityequilibrium/UnityEquilibriumTheory.git
cd UnityEquilibriumTheory
python -m venv .venv
.venv/Scripts/pip install -r .github/requirements-research.txt   # Windows; use .venv/bin/pip elsewhere
```

```bash
python -m pytest -q core/05_tests/physics
```

```bash
python docs/scripts/standard/check_schema.py
```

```bash
python docs/scripts/standard/check_preregistration.py
```

Each Test Card names the script that produced its result; rerunning that script reproduces the recorded numbers.

## What changed in v0.9.1

- The page opens with the core equations: the original Ω = C·I idea and the three layers that now make it calculable.
- It describes UET the way the author defined it: a calculation procedure for systems, built as a synthesis of published theory.
- Section 3 replaces the old "Tree of Physics" diagram with each borrowed result, its source and whether it was used correctly.
- The evidence table is taken from the claim registry, including the inconclusive result.
- The topic index lists all 40 topics with the question each one studies, instead of "Solved" marks.
- The v0.9.0 dashboard ("38 Solutions", Millennium Problems, the v0.9.0 test summary and the search-question table)
  is kept in [`docs/history/LEGACY_CLAIMS.md`](docs/history/LEGACY_CLAIMS.md) as `LEGACY_UNREVIEWED`. None of it is backed by a current result.
- The Uet-Cash section was removed; it is a separate project.
- Links point to the current `core/` and `topics/` folders.

## License

MIT. See [LICENSE](LICENSE).
