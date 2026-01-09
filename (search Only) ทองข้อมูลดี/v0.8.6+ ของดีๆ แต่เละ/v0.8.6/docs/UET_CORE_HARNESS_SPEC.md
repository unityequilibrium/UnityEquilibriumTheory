# UET CORE HARNESS SPEC (v1)

## 1. Purpose
The **UET Core Harness** is a lightweight, reproducible simulation framework for the Universal Entanglement Theory (UET). It provides:
- A deterministic solver for the core equations (Newton/GR/PN/UET).
- A CLI (`uet_cli.py`) and a JSON/YAML **RunSpec** format for batch execution.
- Automatic logging of inputs, intermediate states and final metrics.

**What it does NOT do**: it does not include any web UI, database back‑ends, or external services. All configuration is file‑based and runs locally.

---

## 2. RunSpec v1
A RunSpec is a **single JSON (or YAML) file** that fully describes a simulation run. Only fields that already exist in the codebase are allowed.
```json
{
  "meta": {"name": "preset_name", "version": "1.0"},
  "run": {
    "seed": 42,
    "dt": 0.01,
    "steps": 20000,
    "integrator": "semiimplicit"
  },
  "world": {
    "units": "sim",
    "L": 10.0,
    "dim": 2,
    "bc": "periodic"
  },
  "grid": {"N": 32},
  "equations": {
    "enabled": ["UET"],
    "params": {
      "model": "C_only",
      "kappa": 0.5,
      "pot": {"type": "quartic", "a": 1.0, "delta": 1.0, "s": 0.0}
    }
  },
  "outputs": {
    "metrics": ["OMEGA", "KINETIC_ENERGY", "POTENTIAL_ENERGY"],
    "logEvery": 10,
    "snapshotEvery": 1000
  },
  "validation": {
    "gates": ["determinism", "no_nan", "energy_conservation"]
  }
}
```
*Only the keys shown above are recognised.*

---

## 3. Preset Policy
- **Location**: All preset files live in the repository folder `presets/` (created at the repo root).
- **Minimum required fields** (must be present in every preset JSON/YAML):
  - `meta.name` – human readable identifier.
  - `run.seed`, `run.dt`, `run.steps`, `run.integrator`.
  - `world.L`, `world.dim`, `world.bc`.
  - `grid.N`.
  - `equations.enabled` (at least one equation, e.g., `"UET"`).
  - `equations.params` – must contain the model‑specific parameters that the solver expects (see RunSpec).
  - `outputs.metrics` – list of metric names that will be recorded.
  - `validation.gates` – list of gate identifiers that the run should be checked against.

If a future feature needs additional fields, add a **TODO** entry here with the file path where the change must be made.

---

## 4. Output & Evidence
Each run creates a folder under `runs/<model>/<case_id>/<run_id>/` containing:
- `config.json` – the exact RunSpec used (including a SHA‑256 hash of the file for reproducibility).
- `meta.json` – timestamp, git commit hash (if available), and platform info.
- `timeseries.csv` – step‑wise log with columns `step,t,dt,OMEGA,…` (all metrics listed in `outputs.metrics`).
- `summary.json` – final aggregated results:
  ```json
  {
    "status": "PASS|FAIL|WARN",
    "Omega0": 2.34,
    "OmegaT": 0.78,
    "max_energy_increase": 0.12,
    "steps_total": 20000,
    "runtime_s": 12.3,
    "run_id": "<uuid>",
    "config_hash": "<sha256>"
  }
  ```
All numeric values are expressed in **simulation units** (see Section 6).

---

## 5. Validation Gates v1
The harness ships with a small set of built‑in validation gates. Each gate returns a pass/fail flag and a tolerance value where applicable.
| Gate | Description | Tolerance / Policy | Expected‑Fail Note |
|------|-------------|--------------------|-------------------|
| `determinism` | Same seed → identical `summary.json` and `timeseries.csv`. | Strict equality (hash compare). | N/A |
| `no_nan` | No `NaN` or `Inf` values in any logged column. | Immediate fail if found. | N/A |
| `energy_conservation` | For Newton‑only runs, `|ΔΩ| ≤ 1e‑3 * Ω0`. | Relative tolerance 1e‑3. | If the run uses UET, this gate is **TODO** – add to `validation.py` (see TODO below). |
| `com_drift` | Center‑of‑mass displacement ≤ 1e‑4 L. | Absolute tolerance 1e‑4. | N/A |
| `dt_convergence` | If `auto_dt` was enabled, the final `dt` must be ≤ the safe dt computed by `auto_scale.compute_safe_dt`. | Absolute check. | N/A |
| `uet_smoke` | Run finishes without raising an exception when `UET` is enabled. | Pass if run completes. | N/A |

**TODO** – `determinism` gate implementation is missing; add a function in `uet_core/validation.py` that loads two runs and compares their hashes.

---

## 6. Units v1
All quantities are stored in **simulation‑native units** (`sim`). The harness does not currently perform unit conversion, but every metric must declare a unit label.
```python
METRICS = {
    "OMEGA": {"category": "QNT", "unitLabel": "sim", "description": "Total discrete energy"},
    "KINETIC_ENERGY": {"category": "QNT", "unitLabel": "sim", "description": "Kinetic part of Ω"},
    "POTENTIAL_ENERGY": {"category": "QNT", "unitLabel": "sim", "description": "Potential part of Ω"},
    "COM_DRIFT": {"category": "QNT", "unitLabel": "sim", "description": "Center‑of‑mass displacement"},
    "STATUS": {"category": "QLT", "unitLabel": "state", "description": "PASS/FAIL/WARN"}
}
```
If a new metric is added later, it must be registered here with an explicit `unitLabel`. Until a formal mapping to physical units exists, the label `"sim"` is required.

---

*This specification reflects the current code base. Any future extensions should be added as TODO entries with the file path where the change belongs.*
