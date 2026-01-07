# UET HARNESS v2.0 - REORGANIZATION BLUEPRINT

**วันที่สร้าง:** 2025-12-27
**สถานะ:** Draft Blueprint
**เป้าหมาย:** จัดระเบียบโครงสร้างโค้ดใหม่ทั้งหมด โดยรักษา core functionality และใช้ประสบการณ์จาก v0.1 เป็น blueprint

---

## 📋 สรุปสถานะปัจจุบัน (v0.1)

### ✅ จุดแข็ง (ใช้ได้ดี - ไม่ต้องแก้)
- **Core Math/Physics:** Solver, Energy, Operators, Coercivity → **Excellent** ✨
- **Logging & Reproducibility:** Config hashing, meta tracking → **Excellent** ✨
- **Documentation:** Theory docs, mathematical specs → **Comprehensive** 📚
- **Validation Gates:** Energy conservation, determinism checks → **Rigorous** 🔬

### ⚠️ จุดอ่อน (ต้องปรับปรุง)
- **170+ ไฟล์กระจัดกระจาย** ไม่มีโครงสร้างชัดเจน 😵
- **50+ plotting scripts** ทำงานซ้ำซ้อน → ควรรวมเป็น library 📊
- **30+ runner scripts** แต่ละอันเขียนแยกกัน → ควรเป็น plugin system 🔌
- **Web UI ล้าสมัย** (vanilla JS) → ต้อง modernize 🌐
- **ไม่มี pytest suite** มีแต่ validation scripts กระจาย 🧪
- **Configuration ไม่มี schema validation** 📝

---

## 🎯 เป้าหมาย v2.0

### หลักการออกแบบใหม่

```
CLEAR HIERARCHY
├── 1. CORE (ไม่เปลี่ยน - แค่ clean up)
├── 2. APPLICATIONS (จัดกลุ่มตาม domain)
├── 3. TOOLS (consolidate utilities)
├── 4. INTERFACES (CLI, Web, API)
└── 5. TESTS (pytest suite ที่ complete)
```

### Key Principles

1. **Separation of Concerns:** แยก Core / Apps / Tools / UI ชัดเจน
2. **DRY (Don't Repeat Yourself):** รวม plotting/runner scripts ที่ซ้ำ
3. **Type Safety:** เพิ่ม type hints + Pydantic validation
4. **Modularity:** Plugin architecture สำหรับ domains
5. **Testing:** Comprehensive pytest suite
6. **Modern Stack:** React UI + FastAPI backend

---

## 📁 โครงสร้างใหม่ (v2.0)

```
uet_harness_v2/
│
├── 📦 uet/                              # MAIN PACKAGE
│   │
│   ├── core/                            # 🔬 CORE THEORY (ไม่แตะ!)
│   │   ├── __init__.py
│   │   ├── operators.py                 # ✅ Spectral operators
│   │   ├── energy.py                    # ✅ Energy functionals
│   │   ├── coercivity.py                # ✅ Boundedness checks
│   │   ├── solver.py                    # ✅ Main solver
│   │   ├── validation.py                # ✅ Validation gates
│   │   ├── metrics.py                   # ✅ Metric computation
│   │   ├── logging.py                   # ✅ I/O & logging
│   │   │
│   │   ├── potentials/                  # Potential functions
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # ✅ Abstract base
│   │   │   ├── quartic.py               # ✅ Landau potential
│   │   │   └── sine_gordon.py           # ✅ Alternative
│   │   │
│   │   └── solvers/                     # Alternative solvers
│   │       ├── __init__.py
│   │       └── jax_solver.py            # ✅ JAX GPU acceleration
│   │
│   ├── applications/                    # 🌍 DOMAIN APPLICATIONS
│   │   ├── __init__.py
│   │   │
│   │   ├── finance/                     # 💰 Financial markets
│   │   │   ├── __init__.py
│   │   │   ├── bridge.py                # Market data ↔ UET bridge
│   │   │   ├── strategies.py            # Trading strategies
│   │   │   └── scenarios.py             # Market scenarios
│   │   │
│   │   ├── physics/                     # ⚛️ Physics simulations
│   │   │   ├── __init__.py
│   │   │   ├── coffee_milk.py           # Coffee-milk diffusion
│   │   │   ├── phase_transitions.py     # Phase field dynamics
│   │   │   └── cosmology.py             # Dark matter, galaxies
│   │   │
│   │   ├── neuroscience/                # 🧠 Neural dynamics
│   │   │   ├── __init__.py
│   │   │   ├── excitation_inhibition.py # E-I balance
│   │   │   └── network_dynamics.py      # Network models
│   │   │
│   │   ├── social/                      # 👥 Social systems
│   │   │   ├── __init__.py
│   │   │   ├── opinion_dynamics.py      # Opinion formation
│   │   │   └── information_flow.py      # Info spreading
│   │   │
│   │   └── base.py                      # Abstract application interface
│   │
│   ├── bridges/                         # 🌉 DOMAIN BRIDGES (NEW!)
│   │   ├── __init__.py
│   │   ├── base.py                      # Abstract bridge interface
│   │   ├── ontology.py                  # Variable ontology system
│   │   ├── market.py                    # Market ↔ UET
│   │   ├── physical.py                  # Physical units ↔ UET
│   │   └── social.py                    # Social metrics ↔ UET
│   │
│   ├── analysis/                        # 📊 ANALYSIS TOOLS
│   │   ├── __init__.py
│   │   ├── metrics.py                   # Metric computation
│   │   ├── grading.py                   # Run grading
│   │   ├── comparison.py                # Compare runs
│   │   └── strategies.py                # Strategy analysis (NEW!)
│   │
│   ├── visualization/                   # 📈 VISUALIZATION LIBRARY
│   │   ├── __init__.py
│   │   ├── plotters/                    # Modular plotters
│   │   │   ├── field_plotter.py         # Field heatmaps
│   │   │   ├── timeseries_plotter.py    # Time series plots
│   │   │   ├── energy_plotter.py        # Energy landscapes
│   │   │   └── comparison_plotter.py    # Multi-run comparison
│   │   ├── themes.py                    # Plot styling
│   │   └── gallery.py                   # Gallery generator
│   │
│   ├── runners/                         # 🏃 EXECUTION RUNNERS
│   │   ├── __init__.py
│   │   ├── base.py                      # Abstract runner
│   │   ├── single_run.py                # Single case runner
│   │   ├── sweep_runner.py              # Parameter sweeps
│   │   ├── dt_ladder.py                 # dt refinement studies
│   │   └── batch_runner.py              # Large batch execution
│   │
│   ├── config/                          # ⚙️ CONFIGURATION
│   │   ├── __init__.py
│   │   ├── schema.py                    # Pydantic schemas
│   │   ├── presets.py                   # Preset loader
│   │   └── validation.py                # Config validation
│   │
│   └── utils/                           # 🛠️ UTILITIES
│       ├── __init__.py
│       ├── io.py                        # File I/O utilities
│       ├── hashing.py                   # Config hashing
│       └── paths.py                     # Path management
│
├── 🖥️ cli/                              # COMMAND LINE INTERFACE
│   ├── __init__.py
│   ├── main.py                          # Main CLI entry (typer)
│   └── commands/
│       ├── run.py                       # uet run
│       ├── sweep.py                     # uet sweep
│       ├── analyze.py                   # uet analyze
│       └── visualize.py                 # uet visualize
│
├── 🌐 web/                              # WEB INTERFACE
│   ├── backend/                         # FastAPI backend
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app
│   │   ├── routes/
│   │   │   ├── runs.py                  # Run management
│   │   │   ├── analysis.py              # Analysis endpoints
│   │   │   └── viz.py                   # Visualization
│   │   └── models.py                    # Pydantic models
│   │
│   └── frontend/                        # React frontend
│       ├── package.json
│       ├── src/
│       │   ├── App.tsx
│       │   ├── components/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── RunViewer.tsx
│       │   │   └── StrategyAnalyzer.tsx # NEW!
│       │   └── api/
│       │       └── client.ts
│       └── public/
│
├── 🧪 tests/                            # PYTEST SUITE
│   ├── conftest.py
│   ├── core/
│   │   ├── test_solver.py
│   │   ├── test_energy.py
│   │   ├── test_operators.py
│   │   └── test_validation.py
│   ├── applications/
│   │   ├── test_finance.py
│   │   └── test_physics.py
│   ├── bridges/
│   │   └── test_ontology.py
│   └── integration/
│       ├── test_full_pipeline.py
│       └── test_reproducibility.py
│
├── 📚 docs/                             # DOCUMENTATION
│   ├── index.md                         # Main documentation
│   ├── theory/
│   │   ├── mathematical_foundation.md
│   │   ├── equations.md
│   │   └── physics_interpretation.md
│   ├── guides/
│   │   ├── quickstart.md
│   │   ├── advanced_usage.md
│   │   └── domain_mapping.md
│   ├── api/
│   │   ├── core_api.md
│   │   └── bridge_api.md
│   └── examples/
│       ├── market_analysis.md
│       └── physics_simulation.md
│
├── 📊 examples/                         # EXAMPLE SCRIPTS
│   ├── 01_quickstart.py
│   ├── 02_parameter_sweep.py
│   ├── 03_market_strategy.py           # NEW!
│   └── notebooks/
│       ├── intro_to_uet.ipynb
│       └── domain_bridging.ipynb       # NEW!
│
├── ⚙️ configs/                          # CONFIGURATIONS
│   ├── presets/
│   │   ├── minimal.yaml
│   │   ├── physics.yaml
│   │   └── finance.yaml
│   └── schemas/
│       └── run_config.schema.json
│
├── 🏃 runs/                             # OUTPUT DIRECTORY
│   └── (generated run outputs)
│
├── pyproject.toml                       # Modern Python packaging
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .github/
    └── workflows/
        └── ci.yml                       # GitHub Actions CI
```

---

## 🔄 Migration Plan (จาก v0.1 → v2.0)

### Phase 1: Foundation (Week 1) 🏗️

#### ขั้นที่ 1.1: สร้างโครงสร้างพื้นฐาน
```bash
# สร้าง directory structure ใหม่
mkdir -p uet_harness_v2/{uet/{core,applications,bridges,analysis,visualization,runners,config,utils},cli,web,tests,docs,examples,configs}
```

#### ขั้นที่ 1.2: ย้าย Core (ไม่แก้ไข - แค่ย้าย!)
```
v0.1 → v2.0
====================================
uet_core/operators.py           → uet/core/operators.py
uet_core/energy.py              → uet/core/energy.py
uet_core/coercivity.py          → uet/core/coercivity.py
uet_core/solver.py              → uet/core/solver.py
uet_core/validation.py          → uet/core/validation.py
uet_core/metrics.py             → uet/core/metrics.py
uet_core/logging.py             → uet/core/logging.py

uet_core/potentials/            → uet/core/potentials/
uet_core/solvers/               → uet/core/solvers/
```

**Action:** Copy ตรงๆ ไม่แก้ไข เพิ่มเฉพาะ `__init__.py`

---

### Phase 2: Consolidation (Week 2) 📦

#### ขั้นที่ 2.1: สร้าง Visualization Library

**จาก 50+ plotting scripts → 1 library**

```python
# uet/visualization/plotters/field_plotter.py
class FieldPlotter:
    """Unified field plotting with multiple backends."""

    def plot_heatmap(self, C, I, **kwargs):
        """Plot C, I fields as heatmap."""
        ...

    def plot_evolution(self, history, **kwargs):
        """Animate field evolution."""
        ...

    def plot_snapshot(self, C, I, t, **kwargs):
        """Single timestep snapshot."""
        ...
```

**การย้าย:**
```
scripts/plot_run.py              → uet/visualization/plotters/field_plotter.py (method)
scripts/plot_run_extra.py        → uet/visualization/plotters/timeseries_plotter.py (method)
scripts/plot_dt_ladder.py        → uet/visualization/plotters/convergence_plotter.py
scripts/plot_atlas_*.py          → uet/visualization/plotters/landscape_plotter.py
scripts/generate_uet_gallery.py  → uet/visualization/gallery.py
```

**ผลลัพธ์:**
- 50+ scripts → 5 modular classes
- Reusable plotting library
- Consistent styling

---

#### ขั้นที่ 2.2: สร้าง Runner System

**จาก 30+ runner scripts → Plugin architecture**

```python
# uet/runners/base.py
class AbstractRunner(ABC):
    """Base runner interface."""

    @abstractmethod
    def run(self, config: RunConfig) -> RunResult:
        pass

# uet/runners/single_run.py
class SingleRunRunner(AbstractRunner):
    """Run a single case."""
    def run(self, config):
        ...

# uet/runners/sweep_runner.py
class SweepRunner(AbstractRunner):
    """Parameter sweep runner."""
    def run(self, config):
        for params in config.sweep_grid:
            ...
```

**การย้าย:**
```
scripts/run_suite.py             → uet/runners/sweep_runner.py
scripts/run_dt_ladder.py         → uet/runners/dt_ladder.py
scripts/run_uet_jax.py           → uet/runners/batch_runner.py (JAX mode)
scripts/loop_driver.py           → uet/runners/nested_runner.py
```

---

### Phase 3: Applications & Bridges (Week 3) 🌉

#### ขั้นที่ 3.1: สร้าง Bridge System (NEW!)

```python
# uet/bridges/base.py
class DomainBridge(ABC):
    """Abstract bridge between domain and UET."""

    @abstractmethod
    def domain_to_uet(self, domain_data) -> UETState:
        """Convert domain-specific data to UET fields."""
        pass

    @abstractmethod
    def uet_to_domain(self, uet_state) -> DomainData:
        """Convert UET fields back to domain interpretation."""
        pass

# uet/bridges/market.py
class MarketBridge(DomainBridge):
    """Bridge between financial markets and UET."""

    def domain_to_uet(self, prices, sentiment):
        """Convert market data to C, I fields."""
        C = self._normalize_prices(prices)
        I = self._normalize_sentiment(sentiment)
        return UETState(C=C, I=I)

    def uet_to_domain(self, state):
        """Extract trading signals from UET state."""
        if state.Omega_decreasing:
            return TradingSignal("EQUILIBRATING", "HOLD")
        ...
```

**ย้ายและรวม:**
```
scripts/run_toy_stock.py         → uet/applications/finance/scenarios.py
uet_core/mappings.py             → uet/bridges/physical.py (refactor)
```

---

#### ขั้นที่ 3.2: จัดกลุ่ม Applications

```
Physics Domain:
├── scripts/run_coffee_realistic.py      → uet/applications/physics/coffee_milk.py
├── scripts/run_galaxy_rotation.py       → uet/applications/physics/cosmology.py
└── scripts/run_gr_realistic.py          → uet/applications/physics/relativity.py

Finance Domain:
├── scripts/run_toy_stock.py             → uet/applications/finance/stock_market.py
└── (new) market strategy analyzer       → uet/applications/finance/strategies.py

Neuroscience Domain:
├── scripts/run_neural_prediction.py     → uet/applications/neuroscience/network_dynamics.py
└── (from theory) E-I balance            → uet/applications/neuroscience/excitation_inhibition.py
```

---

### Phase 4: Modern Interfaces (Week 4) 🖥️

#### ขั้นที่ 4.1: CLI with Typer

```python
# cli/main.py
import typer
app = typer.Typer()

@app.command()
def run(
    preset: str = typer.Option("minimal", help="Preset configuration"),
    output: str = typer.Option("runs/", help="Output directory")
):
    """Run a single UET simulation."""
    from uet.runners import SingleRunRunner
    ...

@app.command()
def sweep(
    config: str = typer.Argument(..., help="Sweep config YAML"),
    parallel: int = typer.Option(4, help="Parallel workers")
):
    """Run parameter sweep."""
    from uet.runners import SweepRunner
    ...

@app.command()
def analyze(
    run_dir: str = typer.Argument(...),
    output_format: str = typer.Option("json", help="Output format")
):
    """Analyze simulation results."""
    ...
```

**ใช้แทน:**
- `uet.py` (เก่า) → `uet run` (ใหม่)
- `uet_cli.py` (เก่า) → `uet` (ใหม่ - unified CLI)

---

#### ขั้นที่ 4.2: Web UI with React + FastAPI

**Backend (FastAPI):**
```python
# web/backend/main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/runs")
async def list_runs():
    """List all simulation runs."""
    ...

@app.post("/runs/execute")
async def execute_run(config: RunConfig):
    """Execute a new simulation."""
    ...

@app.get("/analysis/{run_id}")
async def analyze_run(run_id: str):
    """Analyze specific run."""
    ...
```

**Frontend (React):**
```tsx
// web/frontend/src/components/Dashboard.tsx
export function Dashboard() {
  return (
    <div>
      <RunList />
      <StrategyAnalyzer />  {/* NEW! */}
      <VisualizationPanel />
    </div>
  );
}

// NEW: Strategy interaction analyzer
export function StrategyAnalyzer() {
  return (
    <div>
      <h2>Strategy Impact Analysis</h2>
      <InterventionSimulator />
      <RippleEffectGraph />
    </div>
  );
}
```

---

### Phase 5: Testing & Documentation (Week 5) 🧪

#### ขั้นที่ 5.1: Pytest Suite

```python
# tests/core/test_solver.py
import pytest
from uet.core import solver

def test_energy_monotonic_decrease():
    """Test that Omega decreases monotonically."""
    config = {...}
    result = solver.run_case(config)

    # Check monotonicity
    omegas = [row["Omega"] for row in result.timeseries]
    for i in range(len(omegas)-1):
        assert omegas[i+1] <= omegas[i] + tol

def test_deterministic_reproducibility():
    """Test that same config produces same result."""
    config = {...}
    result1 = solver.run_case(config, seed=42)
    result2 = solver.run_case(config, seed=42)

    assert result1.summary["OmegaT"] == result2.summary["OmegaT"]
```

**แปลงจาก validation scripts:**
```
scripts/validate_run.py          → tests/core/test_validation.py
scripts/determinism_probe.py     → tests/integration/test_reproducibility.py
scripts/coercivity_check.py      → tests/core/test_coercivity.py
```

---

#### ขั้นที่ 5.2: Documentation

**ใช้ MkDocs:**
```yaml
# mkdocs.yml
site_name: UET Harness v2.0
theme: material

nav:
  - Home: index.md
  - Theory:
      - Mathematical Foundation: theory/math.md
      - Equations: theory/equations.md
  - Guides:
      - Quickstart: guides/quickstart.md
      - Domain Bridges: guides/bridges.md
      - Strategy Analysis: guides/strategies.md  # NEW!
  - API Reference:
      - Core: api/core.md
      - Bridges: api/bridges.md
```

**ย้าย docs:**
```
docs/MATH_CORE.md                → docs/theory/mathematical_foundation.md
docs/UET_EQUATION_STRUCTURE.md   → docs/theory/equations.md
docs/UET_USAGE_PATTERNS.md       → docs/guides/advanced_usage.md
```

---

## 📊 Detailed File Migration Table

### Core Files (ไม่แก้ - แค่ย้าย)

| v0.1 Path | v2.0 Path | Action |
|-----------|-----------|--------|
| `uet_core/operators.py` | `uet/core/operators.py` | MOVE |
| `uet_core/energy.py` | `uet/core/energy.py` | MOVE |
| `uet_core/coercivity.py` | `uet/core/coercivity.py` | MOVE |
| `uet_core/solver.py` | `uet/core/solver.py` | MOVE |
| `uet_core/validation.py` | `uet/core/validation.py` | MOVE |
| `uet_core/metrics.py` | `uet/core/metrics.py` | MOVE |
| `uet_core/logging.py` | `uet/core/logging.py` | MOVE |
| `uet_core/potentials/` | `uet/core/potentials/` | MOVE |
| `uet_core/solvers/jax_solver.py` | `uet/core/solvers/jax_solver.py` | MOVE |

### Consolidation (รวม scripts หลายๆ ตัว)

| v0.1 Files (Multiple) | v2.0 File (Single) | Type |
|-----------------------|-------------------|------|
| `scripts/plot_run.py`<br>`scripts/plot_run_extra.py`<br>`scripts/plot_run_shifted.py` | `uet/visualization/plotters/field_plotter.py` | CONSOLIDATE → Class methods |
| `scripts/plot_dt_ladder.py`<br>`scripts/plot_tier*.py` | `uet/visualization/plotters/convergence_plotter.py` | CONSOLIDATE |
| `scripts/plot_atlas_*.py` (5 files) | `uet/visualization/plotters/landscape_plotter.py` | CONSOLIDATE |
| `scripts/run_suite.py`<br>`scripts/run_batch_simulation.py`<br>`scripts/run_comprehensive_sweep.py` | `uet/runners/sweep_runner.py` | CONSOLIDATE |
| `scripts/validate_*.py` (5 files) | `tests/core/test_validation.py` | CONSOLIDATE → pytest |

### Domain Applications (จัดกลุ่ม)

| v0.1 Path | v2.0 Path | Domain |
|-----------|-----------|--------|
| `scripts/run_coffee_realistic.py` | `uet/applications/physics/coffee_milk.py` | Physics |
| `scripts/run_galaxy_rotation.py` | `uet/applications/physics/cosmology.py` | Physics |
| `scripts/run_neural_prediction.py` | `uet/applications/neuroscience/network_dynamics.py` | Neuroscience |
| `scripts/run_toy_stock.py` | `uet/applications/finance/stock_market.py` | Finance |
| `uet_core/mappings.py` | `uet/bridges/physical.py` | Bridge |

### Utilities (จัดระเบียบ)

| v0.1 Path | v2.0 Path | Purpose |
|-----------|-----------|---------|
| `scripts/_bootstrap.py` | `uet/utils/paths.py` | Path management |
| `scripts/_plot_common.py` | `uet/visualization/themes.py` | Plotting utilities |
| `scripts/action_router.py` | `cli/commands/` (integrated) | CLI routing |

### Configuration & Presets

| v0.1 Path | v2.0 Path | Format Change |
|-----------|-----------|---------------|
| `presets/*.json` | `configs/presets/*.yaml` | JSON → YAML |
| (no schema) | `uet/config/schema.py` | ADD Pydantic schemas |

---

## 🚀 Implementation Checklist

### Week 1: Foundation ✅
- [ ] สร้าง directory structure ใหม่
- [ ] ย้าย core files (10 files)
- [ ] เพิ่ม `__init__.py` ทุก package
- [ ] ทดสอบ import paths
- [ ] สร้าง `pyproject.toml` ใหม่

### Week 2: Consolidation ✅
- [ ] สร้าง `uet/visualization/` library
  - [ ] `FieldPlotter` (รวม 15 scripts)
  - [ ] `TimeseriesPlotter` (รวม 8 scripts)
  - [ ] `LandscapePlotter` (รวม 5 scripts)
  - [ ] `GalleryGenerator`
- [ ] สร้าง `uet/runners/` system
  - [ ] `SingleRunRunner`
  - [ ] `SweepRunner`
  - [ ] `DTLadderRunner`
  - [ ] `BatchRunner`
- [ ] ทดสอบ consolidated modules

### Week 3: Bridges & Applications ✅
- [ ] สร้าง `uet/bridges/` system
  - [ ] `base.py` (abstract interface)
  - [ ] `ontology.py` (variable definitions)
  - [ ] `market.py` (financial bridge)
  - [ ] `physical.py` (physics bridge)
- [ ] จัดกลุ่ม applications
  - [ ] `physics/` (5 modules)
  - [ ] `finance/` (2 modules)
  - [ ] `neuroscience/` (2 modules)
- [ ] เขียน bridge examples

### Week 4: Interfaces ✅
- [ ] สร้าง CLI with Typer
  - [ ] `uet run`
  - [ ] `uet sweep`
  - [ ] `uet analyze`
  - [ ] `uet visualize`
- [ ] สร้าง Web backend (FastAPI)
  - [ ] `/runs` endpoints
  - [ ] `/analysis` endpoints
  - [ ] `/viz` endpoints
- [ ] สร้าง Web frontend (React)
  - [ ] Dashboard component
  - [ ] RunViewer component
  - [ ] StrategyAnalyzer component (NEW!)

### Week 5: Testing & Docs ✅
- [ ] สร้าง pytest suite
  - [ ] Core tests (5 modules)
  - [ ] Integration tests (3 modules)
  - [ ] Bridge tests (2 modules)
- [ ] เขียน documentation (MkDocs)
  - [ ] Theory docs
  - [ ] User guides
  - [ ] API reference
- [ ] สร้าง examples
  - [ ] 5 example scripts
  - [ ] 2 Jupyter notebooks
- [ ] Setup CI/CD (GitHub Actions)

---

## 📈 Expected Outcomes

### Before (v0.1)
- ❌ 170+ ไฟล์กระจัดกระจาย
- ❌ ซ้ำซ้อน (50 plotting scripts)
- ❌ ไม่มี type safety
- ❌ ไม่มี comprehensive tests
- ❌ UI ล้าสมัย
- ⚠️ ใช้ยากสำหรับคนใหม่

### After (v2.0)
- ✅ โครงสร้างชัดเจน 5 layers
- ✅ Modular libraries (reusable)
- ✅ Type-safe (Pydantic)
- ✅ Pytest suite ครบถ้วน
- ✅ Modern React UI
- ✅ Easy onboarding (examples + docs)
- 🆕 **Strategy Analysis System**
- 🆕 **Domain Bridge Architecture**

---

## 🎯 Next Steps

1. **Review Blueprint:** อ่านเอกสารนี้และ feedback
2. **Approve Structure:** ยืนยันโครงสร้างใหม่
3. **Start Phase 1:** สร้าง directories และย้าย core
4. **Incremental Migration:** ย้ายทีละ phase ทดสอบไปเรื่อยๆ
5. **Maintain v0.1:** ระหว่างย้ายยังใช้ v0.1 ได้ปกติ

---

## 📝 Notes

- **ไม่แก้ Core:** uet/core/ ยังใช้โค้ดเดิม (tested, stable)
- **Backward Compatible:** v2.0 ยัง run v0.1 configs ได้ (via adapter)
- **Gradual Migration:** ไม่ต้องย้ายทีเดียว แบ่งเป็น phases
- **Test Coverage:** ทุก consolidation ต้องมี tests

---

**Blueprint Version:** 1.0
**Last Updated:** 2025-12-27
**Status:** Ready for Review ✅
