# Topic screen for UET-distinct prediction candidates (2026-11-16)

Question: which of the 27 physics-scope topics (`topics/0.0`-`0.26`) could still yield a prediction
that differs from standard physics? Screen applied to each topic:

1. Is there a real, open, quantitative problem in standard physics here?
2. Does the parent action (`core/THEORY_CARD.md`: scalar-tensor `xi psi^2 R` plus a trilinear portal
   to an O(2) scalar chi, with chi = ordinary matter) reach it directly, or does the topic use a
   topic-local engine?
3. With every fitted, calibrated or benchmark-anchored value removed, is a predicted number left?

Sources read: each topic's `LIMITATIONS.md` and `BASELINE_COMPARISON.md`, `topics/README.md`,
`docs/meta/UET_RESEARCH_RETROSPECTIVE.md`. Topic engines and artifacts were not rerun. All topic
results remain `LEGACY_UNREVIEWED`. This is an AI screen, not an evidence decision.

## Finding common to all topics

Only `0.13_Thermodynamic_Bridge` refers to the parent action. Every other topic computes with a
topic-local engine (for example `Engine_Muon_G2.py`), so criterion 2 fails by construction, and the
retrospective (R08-R12) already records fitted or anchored values in many of them. **No topic
passes all three criteria today.**

## Per topic

| Topic | 1 Open problem | 2 Parent action reaches | 3 Number left without fits | Note |
| :-- | :-- | :-- | :-- | :-- |
| 0.1 Galaxy rotation | yes (dark matter) | not as a force: scalar exchange is an attractive Yukawa that falls off beyond 1/m_psi, the wrong shape for flat curves (AI inference) | no: heuristic bridge terms, gate fails | see candidate A |
| 0.15 Cluster dynamics | yes (dark matter) | as for 0.1 | no: toy drag constants, a0 anchor | see candidate A |
| 0.26 Cosmic dynamic frame | partly (flows); Pioneer anomaly is explained by thermal recoil | no | no: visualization gate only | |
| 0.3 Hubble tension | yes | yes in principle: `xi psi^2 R` changes G_eff in the early universe (known "early modified gravity" class) | no: sqrt(alpha_em) chosen after the derived beta failed (R09) | see candidate B |
| 0.12 Vacuum energy | yes (cosmological constant, evolving dark energy hints) | only as the free constant Lambda_eff | no: Lambda anchored to the observed value | see candidate C |
| 0.2 Black holes | yes, no data tension | via scalar-tensor, no distinct handle found | no: GR shadow factor | |
| 0.19 Gravity / GR | no data tension | yes (T001, T005 already done) | no: CODATA check | |
| 0.8 Muon g-2 | **no longer**: 2025 SM minus experiment = (3.8 +- 6.3)e-10, 0.6 sigma | portal to muons is far too weak at the T005 bound (AI estimate, about 1e-37) | no | drop as a distinctness route |
| 0.7 Neutrinos | yes (mass origin) | no: no fermions in the action | no: benchmark-fed splittings | |
| 0.17 Mass generation | yes (mass pattern) | no | no: Koide imposed, kappa = 1 baseline | |
| 0.6 Electroweak | no | no gauge sector | no | |
| 0.5 Nuclear / hadrons | no | no | no: SEMF coefficients | |
| 0.16 Heavy nuclei | partly (island of stability) | no | no: SEMF mapping | |
| 0.21 Yang-Mills gap | mathematical problem | no gauge sector | no: parameter sweep | |
| 0.4 Superconductivity | yes (high-Tc) | chi is an O(2) order parameter, but Ginzburg-Landau level only | no: McMillan gate fails | |
| 0.13 Thermodynamic bridge | no data tension | yes (bounded He-4 O(2) closure) | no physical detection | |
| 0.9 Quantum nonlocality | no | no | no: Tsirelson bound is standard QM | |
| 0.11 Phase transitions | no (3D Ising exponents known) | no | no | |
| 0.20 Atomic | no | no | no: standard Rydberg | |
| 0.10, 0.18 | mathematical problems | no | no | |
| 0.0, 0.14, 0.22, 0.23, 0.24, 0.25 | integration or non-physics | no | no: synthetic or proxy data; 0.23 records that a fixed universal kappa fails | |

## Candidates worth a disciplined restart (AI proposals, not author requirements)

- **A. psi as dark matter, not as a new force.** The parent action already contains a massive
  scalar psi. If psi carries cosmological energy density, an ultralight psi behaves as wave
  ("fuzzy") dark matter, a known class. A UET reading (AI interpretation): the response field of
  space carries the missing mass. What could be distinct: the portal `g_c` and `xi_c` couplings
  give an oscillating fifth force and oscillating G tied to the same field, already bounded by
  T001 and T005. Needs: relic abundance from the action, then Lyman-alpha, rotation-curve core and
  oscillating-G limits.
- **B. Hubble tension through `xi psi^2 R`.** Reachable from the action, but the mechanism class is
  published and needs a Boltzmann code (for example hi_class) and CMB/BAO/SN data. A distinct
  number only appears if UET fixes `xi_c`, `m_psi` and the initial psi from something other than
  the H0 data.
- **C. Vacuum energy from accumulated records (author idea, 2026-11-09).** If the "vacuum is
  written by past behaviour", dark-energy density would track the cumulative free energy burned
  in the universe, so w(z) would differ from -1 in a specific way. Not in the action yet (needs a
  new term and an author decision), L0, and it must avoid double counting energy already carried
  by radiation. It is the only candidate here that ΛCDM does not already contain, and evolving
  dark energy is an open data question.

## Recommended stop rule

Pick at most two candidates, derive each from the action (or an author-approved extension) with
all parameters fixed before any comparison, and preregister one Test Card each. If neither gives
a number that standard physics does not, record that and present UET as a unifying framework
rather than new fundamental physics.
