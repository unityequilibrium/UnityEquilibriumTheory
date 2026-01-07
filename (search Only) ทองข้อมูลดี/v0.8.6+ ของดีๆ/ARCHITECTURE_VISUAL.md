# UET HARNESS v2.0 - ARCHITECTURE VISUALIZATION

**ภาพรวมระบบใหม่แบบเห็นชัดเจน**

---

## 🏗️ สถาปัตยกรรม 5 ชั้น (5-Layer Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                     5. INTERFACES                            │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │  CLI (Typer) │  Web (React) │  API (FastAPI)       │    │
│  │  uet run     │  Dashboard   │  POST /runs/execute  │    │
│  │  uet sweep   │  Visualizer  │  GET /analysis/{id}  │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                   4. TOOLS & UTILITIES                       │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │ Visualization│   Analysis   │     Runners          │    │
│  │  - Plotters  │  - Metrics   │  - SingleRun         │    │
│  │  - Gallery   │  - Grading   │  - Sweep             │    │
│  │  - Themes    │  - Compare   │  - DTLadder          │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                  3. DOMAIN BRIDGES 🆕                        │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │   Market     │   Physical   │      Social          │    │
│  │  Price ↔ C   │  Temp ↔ C+I  │  Opinion ↔ C         │    │
│  │  Sent. ↔ I   │  Dens ↔ |C,I|│  Influence ↔ I       │    │
│  │  Strategy ←→ │  Units ←→    │  Spread ←→           │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
│            ┌────────────────────────────┐                   │
│            │  Ontology (Variable Defs)  │                   │
│            │  C, I, κ, β meanings       │                   │
│            └────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                   2. APPLICATIONS                            │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │   Finance    │   Physics    │   Neuroscience       │    │
│  │  - Markets   │  - Coffee    │  - E-I Balance       │    │
│  │  - Trading   │  - Cosmology │  - Networks          │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                      1. CORE ENGINE                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Solver (semi-implicit, backtracking)                │  │
│  │  Energy (Ω computation)                               │  │
│  │  Operators (spectral FFT)                             │  │
│  │  Coercivity (boundedness)                             │  │
│  │  Validation (gates)                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                    ⚠️ DON'T TOUCH! ⚠️                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow (การไหลของข้อมูล)

### 1️⃣ Traditional Flow (v0.1 - แค่จำลอง)

```
User → Config.json → Solver → Output → Plot
                                        (end)
```

**ปัญหา:** ไม่มีความหมาย ไม่ต่อยอดได้

---

### 2️⃣ New Bidirectional Flow (v2.0 - ใช้จริงได้!)

```
┌─────────────────────────────────────────────────────────┐
│                    REAL WORLD                            │
│  Market Data, Physical Measurements, Social Metrics      │
└─────────────────────────────────────────────────────────┘
                      ▼ INGEST
┌─────────────────────────────────────────────────────────┐
│                  DOMAIN BRIDGE                           │
│  Convert: Real Data → UET Fields (C, I, ...)            │
│  Example: Price[$] → C[-1,1], Sentiment[0,100] → I      │
└─────────────────────────────────────────────────────────┘
                      ▼ TRANSFORM
┌─────────────────────────────────────────────────────────┐
│                   UET SIMULATION                         │
│  Run dynamics: ∂C/∂t = -M(V'(C) - κΔC - βI)            │
│  Compute Ω trajectory, equilibrium points                │
└─────────────────────────────────────────────────────────┘
                      ▼ ANALYZE
┌─────────────────────────────────────────────────────────┐
│                STRATEGY ANALYSIS 🆕                      │
│  • Intervene: "What if we do X?"                         │
│  • Impact: How does X affect Y, Z?                       │
│  • Optimize: Best strategy to minimize Ω?               │
└─────────────────────────────────────────────────────────┘
                      ▼ EXTRACT
┌─────────────────────────────────────────────────────────┐
│                  DOMAIN BRIDGE                           │
│  Convert: UET Result → Actionable Strategy              │
│  Example: Ω↓ → "HOLD", C>I → "SELL", C<I → "BUY"       │
└─────────────────────────────────────────────────────────┘
                      ▼ OUTPUT
┌─────────────────────────────────────────────────────────┐
│                  ACTIONABLE ADVICE                       │
│  Dashboard, Reports, Trading Signals, Predictions        │
└─────────────────────────────────────────────────────────┘
```

---

## 🌉 Domain Bridge Example (Market)

```python
# INPUT: Real market data
prices = pd.DataFrame({
    'AAPL': [150, 152, 149, ...],
    'GOOGL': [2800, 2750, 2820, ...],
    ...
})
sentiment = get_twitter_sentiment()  # From social media

# ─────────────────────────────────────
# BRIDGE: Real → UET
# ─────────────────────────────────────
from uet.bridges.market import MarketBridge

bridge = MarketBridge()
uet_state = bridge.domain_to_uet(
    prices=prices,
    sentiment=sentiment
)
# Result: uet_state.C = normalized price field
#         uet_state.I = normalized sentiment field

# ─────────────────────────────────────
# SIMULATE: Run UET dynamics
# ─────────────────────────────────────
from uet.runners import SingleRunRunner

runner = SingleRunRunner()
result = runner.run(uet_state, T=5.0)

# ─────────────────────────────────────
# ANALYZE: Strategy impact
# ─────────────────────────────────────
from uet.analysis.strategies import StrategyAnalyzer

analyzer = StrategyAnalyzer()

# Scenario 1: What if Fed raises interest rates?
impact_1 = analyzer.analyze_intervention(
    baseline=result,
    intervention={"s": -0.5}  # Negative shock
)
print(f"Price impact: {impact_1.price_change}")
print(f"Equilibrium time: {impact_1.time_to_eq}")

# Scenario 2: What if we pump money into sector X?
impact_2 = analyzer.analyze_intervention(
    baseline=result,
    intervention={"C[region_X]": +0.3}
)
print(f"Spillover to sector Y: {impact_2.spillover['Y']}")

# ─────────────────────────────────────
# EXTRACT: UET → Actionable Strategy
# ─────────────────────────────────────
strategy = bridge.uet_to_domain(result)

if strategy.signal == "BUY":
    print(f"Recommendation: BUY {strategy.tickers}")
    print(f"Confidence: {strategy.confidence:.1%}")
    print(f"Expected Ω reduction: {strategy.omega_decrease}")
```

---

## 📊 File Organization Comparison

### Before (v0.1) - ไม่มีระเบียบ 😵

```
uet_harness_v0.1/
├── scripts/
│   ├── plot_run.py
│   ├── plot_run_extra.py
│   ├── plot_run_shifted.py
│   ├── plot_dt_ladder.py
│   ├── plot_atlas_A.py
│   ├── plot_atlas_B.py
│   ├── ... (50+ plotting scripts!)
│   ├── run_coffee_realistic.py
│   ├── run_galaxy_rotation.py
│   ├── run_toy_stock.py
│   ├── ... (30+ runner scripts!)
│   └── validate_*.py (scattered)
├── uet_core/
│   ├── solver.py
│   ├── energy.py
│   └── ...
└── (170+ files total!)
```

**ปัญหา:**
- หาไฟล์ยาก (ทุกอย่างอยู่ใน `scripts/`)
- ซ้ำซ้อน (50 plotting scripts ทำงานคล้ายๆ กัน)
- ไม่รู้ว่าอันไหนสำคัญ อันไหนแค่ demo

---

### After (v2.0) - จัดระเบียบชัดเจน ✨

```
uet_harness_v2/
├── uet/                          # MAIN PACKAGE
│   ├── core/                     # 🔬 Core (10 files)
│   │   ├── solver.py
│   │   ├── energy.py
│   │   └── ...
│   ├── applications/             # 🌍 Domains (grouped)
│   │   ├── finance/
│   │   │   ├── stock_market.py
│   │   │   └── strategies.py
│   │   ├── physics/
│   │   │   ├── coffee_milk.py
│   │   │   └── cosmology.py
│   │   └── neuroscience/
│   ├── bridges/                  # 🌉 NEW!
│   │   ├── market.py
│   │   ├── physical.py
│   │   └── ontology.py
│   ├── visualization/            # 📊 Plotters (5 classes)
│   │   └── plotters/
│   │       ├── field_plotter.py
│   │       ├── timeseries_plotter.py
│   │       └── landscape_plotter.py
│   ├── runners/                  # 🏃 Runners (4 classes)
│   │   ├── single_run.py
│   │   ├── sweep_runner.py
│   │   └── dt_ladder.py
│   └── analysis/                 # 📈 Analysis tools
│       ├── metrics.py
│       └── strategies.py         # NEW!
├── cli/                          # 🖥️ CLI
│   └── main.py (uet run/sweep/analyze)
├── web/                          # 🌐 Web UI
│   ├── backend/ (FastAPI)
│   └── frontend/ (React)
└── tests/                        # 🧪 Tests
    └── (pytest suite)
```

**ข้อดี:**
- ✅ หาง่าย (grouped by purpose)
- ✅ ไม่ซ้ำ (consolidated into libraries)
- ✅ ชัดเจน (core vs apps vs tools)

---

## 🆚 Script Consolidation Example

### Before: 15 Plotting Scripts

```
scripts/
├── plot_run.py                 (field snapshot)
├── plot_run_extra.py           (extended metrics)
├── plot_run_shifted.py         (shifted analysis)
├── plot_dt_ladder.py           (dt convergence)
├── plot_atlas_A.py             (landscape A)
├── plot_atlas_B.py             (landscape B)
├── plot_atlas_BC.py            (landscape BC)
├── plot_tier0_comparison.py    (tier 0)
├── plot_tier1_pass_comparison.py
├── plot_tier1_fail_comparison.py
├── plot_tier2_swept_summary.py
├── plot_tier3_dashboard_v3.py
├── plot_symmetry.py
├── plot_mratio_lines.py
└── plot_toy_coffee_milk.py

Total: 15 files, ~800 KB
Many copy-paste code
```

---

### After: 1 Modular Library

```python
# uet/visualization/plotters/field_plotter.py
class FieldPlotter:
    """Unified field plotting."""

    def snapshot(self, C, I, t, **kwargs):
        """Single timestep snapshot."""
        fig, axes = plt.subplots(1, 2)
        axes[0].imshow(C, ...)
        axes[1].imshow(I, ...)
        ...

    def evolution(self, history, **kwargs):
        """Animate field evolution."""
        ...

    def comparison(self, runs, **kwargs):
        """Compare multiple runs."""
        ...

# Usage:
from uet.visualization import FieldPlotter
plotter = FieldPlotter()
plotter.snapshot(C, I, t=5.0)
plotter.evolution(history)
plotter.comparison([run1, run2, run3])
```

**ผลลัพธ์:**
- 15 scripts → 1 class (5 methods)
- Reusable across all applications
- Consistent styling
- Easy to extend

---

## 🔌 Plugin Architecture Example

### Application Plugin

```python
# uet/applications/base.py
class Application(ABC):
    """Base application interface."""

    @abstractmethod
    def get_default_config(self) -> dict:
        """Return default configuration."""
        pass

    @abstractmethod
    def get_bridge(self) -> DomainBridge:
        """Return domain bridge."""
        pass

# uet/applications/finance/stock_market.py
class StockMarketApp(Application):
    """Stock market application."""

    def get_default_config(self):
        return {
            "model": "C_I",
            "params": {
                "beta": 0.6,  # Price-sentiment coupling
                "kC": 0.3,    # Price diffusion
                "kI": 0.2,    # Sentiment diffusion
            }
        }

    def get_bridge(self):
        return MarketBridge()

# Usage:
from uet.applications import get_app
app = get_app("finance.stock_market")
config = app.get_default_config()
bridge = app.get_bridge()
```

**ข้อดี:**
- เพิ่ม domain ใหม่ง่าย (แค่สร้าง class ใหม่)
- Consistent interface
- Auto-discovery

---

## 🧪 Testing Strategy

### Before: Scattered Validation Scripts

```
scripts/validate_run.py          # Validate single run
scripts/validate_suite.py        # Validate suite
scripts/determinism_probe.py     # Check reproducibility
scripts/coercivity_check.py      # Check boundedness
...
```

**ปัญหา:**
- ไม่ใช่ automated tests
- ต้อง run manually
- ไม่มี CI integration

---

### After: Pytest Suite

```python
# tests/core/test_solver.py
def test_energy_monotonic_decrease():
    """Test Ω decreases monotonically."""
    ...

def test_deterministic_reproducibility():
    """Test same config → same result."""
    ...

# tests/integration/test_full_pipeline.py
def test_market_strategy_pipeline():
    """Test full pipeline: data → UET → strategy."""
    # Ingest
    data = load_sample_market_data()
    bridge = MarketBridge()
    state = bridge.domain_to_uet(data)

    # Simulate
    runner = SingleRunRunner()
    result = runner.run(state)

    # Extract
    strategy = bridge.uet_to_domain(result)

    assert strategy.signal in ["BUY", "SELL", "HOLD"]
    assert 0 <= strategy.confidence <= 1
```

**ข้อดี:**
- ✅ Automated (CI/CD)
- ✅ Fast feedback
- ✅ Coverage metrics
- ✅ Integration tests

---

## 📱 Modern UI Mockup

### Dashboard Layout

```
┌───────────────────────────────────────────────────────────┐
│  UET Harness v2.0                    [User] [Settings]    │
├───────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────────────────────┐ │
│ │   Run List      │  │   Visualization Panel           │ │
│ │                 │  │                                 │ │
│ │ ✅ run_001      │  │  ┌───────────┬───────────┐      │ │
│ │ ✅ run_002      │  │  │ C Field   │ I Field   │      │ │
│ │ ⏳ run_003      │  │  │ [heatmap] │ [heatmap] │      │ │
│ │ ❌ run_004      │  │  └───────────┴───────────┘      │ │
│ │                 │  │                                 │ │
│ │ [+ New Run]     │  │  Ω Evolution:                   │ │
│ └─────────────────┘  │  [time series chart]            │ │
│                      └─────────────────────────────────┘ │
├───────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────────────┐ │
│ │  🆕 Strategy Interaction Analyzer                     │ │
│ ├───────────────────────────────────────────────────────┤ │
│ │  Baseline: run_002                                    │ │
│ │                                                       │ │
│ │  Intervention:                                        │ │
│ │  ┌─────────────────────────────────────────────────┐ │ │
│ │  │ Field: [C ▼]  Region: [All ▼]  Change: +0.3    │ │ │
│ │  │ [Simulate Impact]                               │ │ │
│ │  └─────────────────────────────────────────────────┘ │ │
│ │                                                       │ │
│ │  Predicted Impact:                                    │ │
│ │  • Direct effect on I: +0.15                          │ │
│ │  • Ω change: -2.3 (stabilizing)                       │ │
│ │  • Equilibrium time: 1.2s                             │ │
│ │  • Spillover effects: [interactive graph]             │ │
│ └───────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Examples

### v0.1 (Old Way)

```bash
# Run simulation
python uet.py run --preset coffee

# Plot results
python scripts/plot_run.py runs/demo001/

# Analyze
python scripts/compute_run_metrics.py runs/demo001/

# Grade
python scripts/grade_runs.py runs/
```

**ปัญหา:** ต้องจำ script names หลายตัว

---

### v2.0 (New Way)

```bash
# All in one CLI!
uet run --preset coffee --output runs/demo001
uet analyze runs/demo001 --visualize
uet sweep --config configs/market_sweep.yaml

# Or use Python API:
from uet.applications import get_app
from uet.runners import SingleRunRunner

app = get_app("finance.stock_market")
runner = SingleRunRunner()
result = runner.run(app.get_default_config())
print(result.summary)
```

**ข้อดี:** Unified interface, easy to remember

---

## 📋 Migration Phases Summary

```
Phase 1 (Week 1): FOUNDATION
├─ Create directory structure
├─ Move core files (no changes!)
└─ Setup pyproject.toml
   Status: [░░░░░░░░░░] 0%

Phase 2 (Week 2): CONSOLIDATION
├─ Build visualization library (50 scripts → 5 classes)
├─ Build runner system (30 scripts → 4 classes)
└─ Test consolidated modules
   Status: [░░░░░░░░░░] 0%

Phase 3 (Week 3): BRIDGES & APPS
├─ Create bridge system 🆕
├─ Group applications by domain
└─ Write bridge examples
   Status: [░░░░░░░░░░] 0%

Phase 4 (Week 4): INTERFACES
├─ CLI with Typer
├─ FastAPI backend
└─ React frontend
   Status: [░░░░░░░░░░] 0%

Phase 5 (Week 5): TESTING & DOCS
├─ Pytest suite
├─ MkDocs documentation
├─ Example notebooks
└─ CI/CD setup
   Status: [░░░░░░░░░░] 0%
```

---

**Ready to start?** 🚀

เริ่มจาก Phase 1 หรือต้องการปรับแก้อะไรก่อน?
