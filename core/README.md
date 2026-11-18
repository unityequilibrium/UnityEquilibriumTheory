# core/ — UET equations, models and tests

This folder holds the code of the UET core equations, the models built on them, and their tests.
It is a working area, not a claim source: the level of every claim is in [`docs/standard/claims.json`](../docs/standard/claims.json),
and the research rules are in [`docs/STANDARD.md`](../docs/STANDARD.md).

The previous README (the Omega = C·I engine and the foundation-gate era) is kept unchanged at
[`08_history/README_LEGACY_2026-11-14.md`](08_history/README_LEGACY_2026-11-14.md). Its wording is `LEGACY_UNREVIEWED`.

## Read in this order

| Step | File | What it gives |
|---|---|---|
| 1 | [`AUTHOR_PROPOSITION.md`](AUTHOR_PROPOSITION.md) | The author's intent and logic (the only source of intent) |
| 2 | [`CORE_MAP.md`](CORE_MAP.md) | Where each layer's equations, tests and real-data comparisons live (Thai) |
| 3 | [`THEORY_CARD.md`](THEORY_CARD.md) | Layer 1: the parent action, its field table and redundant parameters |
| 4 | [`FIDELITY_MATRIX.md`](FIDELITY_MATRIX.md) | Whether each point of the author's logic matches an equation |
| 5 | [`SYNTHESIS_AUDIT.md`](SYNTHESIS_AUDIT.md) | Whether borrowed principles are used within their conditions |
| 6 | [`CORE_ALIGNMENT_REGISTER.md`](CORE_ALIGNMENT_REGISTER.md) | One label per file in this folder: A use, B develop, C keep as history, D structure |

## The three layers (summary; details in CORE_MAP)

- **Layer 1, matter exchanges with the structure of space.** A conservative parent action with a response scalar φ,
  an O(2) matter field χ and a portal coupling (code in `02_equations/covariant/`). It maps onto a
  Damour–Esposito-Farèse scalar-tensor theory.
- **Layer 2, open systems burn free energy and leave a trace.** Models in `03_lanes/open_system/`.
  Not yet derived from the layer 1 action; the raw material for that derivation is the B-labelled O(2) SK/KMS code in `02_equations/o2/`.
- **Layer 3, selection by resource management.** A consumer-resource model in `03_lanes/persistence/`.
  It reduces term by term to the Lotka–Volterra model of Saavedra et al. (2025) (`uet_layer3_lv_map.py`).
- **Observation layer.** Records of the past, delay and Lorentz kinematics in `03_lanes/observation/`.

Every layer so far reduces to an existing theory. No Test Card yet separates UET from standard physics (see CORE_MAP §6).

## Folder layout

| Folder | Holds |
|---|---|
| `00_governance/` | Calculation contracts (read by the CI completeness audit), import aliases, redirect stubs, old migration records |
| `01_contracts/` | Specifications; most describe the old C-lane ontology and are kept as history |
| `02_equations/` | Equation code: `covariant/` (layer 1), `o2/` (O(2) matter at finite temperature), `matter_space/` (legacy Omega = C·I engine) |
| `03_lanes/` | Models and Test Card producers: `observation/`, `open_system/`, `scalar_tensor/`, `persistence/`; plus legacy lanes |
| `04_proofs/` | One legacy proof script (labelled C); derivation checks now live in `05_tests/physics/` |
| `05_tests/` | `physics/` holds the evidence-grade tests (`@pytest.mark.physics`); the other folders hold bookkeeping and legacy regression tests |
| `06_data/` | Legacy source packages; current external data is in `docs/data/external/` with `docs/standard/data_manifest.json` |
| `07_artifacts/` | Generated output of legacy lanes and gates; no current research record cites it |
| `08_history/` | Update logs, research notes, archived import shims and archived failing tests |
| `99_review/` | Quarantine |
| `engine/` | The shared calculation procedure and lane cards |

`core_paths.py` is the path authority; `core_compat.py` and `00_governance/uet_core_legacy_module_aliases.json` keep old `docs.core` imports working.

## Check your work

```bash
.venv/Scripts/python.exe -m pytest -m physics core/05_tests/physics
```

```bash
.venv/Scripts/python.exe topics/run_all_tests.py --changed origin/main
```

The second command runs what CI runs. Topics with no test suite are listed as advisory and do not fail the run.

## Wording

Use `hypothesis`, `model`, `derived relation`, `internally consistent (L1)`, `confronted with data (L2)`.
Do not call a fit a prediction or a normalized quantity SI. `C` is not universally mass, and `Phi` is not a metric or a substance.
