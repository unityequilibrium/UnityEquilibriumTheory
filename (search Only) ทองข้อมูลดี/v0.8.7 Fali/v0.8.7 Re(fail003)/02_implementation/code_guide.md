# Code Guide

## How to use uet_landauer/

---

## Installation

```bash
cd Lab_uet_harness_v0.8.7
# Package is already available
```

---

## Quick Start

```python
from uet_landauer import (
    # Core functions
    energy_per_bit,
    value_function,
    
    # Systems
    LandauerSystem,
    ThermodynamicSystem,
    UniverseSpace,
    FullSimulator,
)
```

---

## 1. Energy per bit (Landauer)

```python
from uet_landauer import energy_per_bit

# At room temperature (300K)
E = energy_per_bit(300)
print(f"E = {E:.2e} J")  # ~2.87e-21 J

# At different temperatures
E_cold = energy_per_bit(100)   # Colder = less energy
E_hot = energy_per_bit(1000)   # Hotter = more energy
```

---

## 2. Value Function (V connects C and I)

```python
from uet_landauer import value_function

# Basic usage: V = M × (C/I)^α
V = value_function(C=2, I=1, M=1, alpha=1)
print(f"V = {V}")  # 2.0

# High communication, low isolation = high value
V_open = value_function(C=10, I=1)  # 10.0

# Low communication, high isolation = low value
V_closed = value_function(C=1, I=10)  # 0.1
```

---

## 3. Full Simulation

```python
from uet_landauer import FullSimulator, SimulationConfig

# Configure
config = SimulationConfig(
    T=300.0,           # Temperature
    dt=0.01,           # Time step
    duration=10.0,     # Total time
    n_agents=3         # Number of agents
)

# Run
sim = FullSimulator(config)
results = sim.run()

# Plot
sim.plot(save_path="result.png")

# Results
print(f"Final Energy: {results['final_E']:.2e} J")
print(f"Law 2 OK: {results['law_2_ok']}")
```

---

## 4. Thermodynamic System

```python
from uet_landauer import ThermodynamicSystem

# Create system
system = ThermodynamicSystem(T=300)

# Add behaviors
system.add_behavior(bits=1000)
system.add_behavior(bits=2000)

# Verify laws
results = system.verify_laws()
print(f"Law 1: {results['law_1']}")
print(f"Law 2: {results['law_2']}")
```

---

## 5. Space Recording

```python
from uet_landauer import UniverseSpace

# Create universe
universe = UniverseSpace(T=300)

# Create region
universe.create_region("Earth", radius=6.4e6)

# Record behavior
universe.record("Earth", bits=1e30, source="Human activity")

# Summary
print(universe.summary())
```

---

## Package Structure

```
uet_landauer/
├── core.py           ← E=kT ln 2, V=M(C/I)^α
├── thermodynamics.py ← Laws 0-3
├── space.py          ← Bekenstein, light cone
├── simulator.py      ← Full simulation
└── tests/            ← Unit tests
```

---

*Code Guide - Part 3*
