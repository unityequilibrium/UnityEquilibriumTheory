# UET Framework - Language Reference

## 🎯 What is UET?

**UET is NOT new physics. UET is a COMMON LANGUAGE.**

A universal framework for modeling coupled dynamics across ANY domain.
Like math is a language for science, UET is a language for complex systems.

---

## 📐 Core Equations

```
∂C/∂t = κ∇²C - ∂V/∂C - β(C - I) + s
∂I/∂t = κ∇²I - ∂V/∂I - β(I - C)
```

Where:
- **V(φ) = (φ² - 1)² / 4** (Double-well potential)

---

## 🔤 Symbol Dictionary

| Symbol | Name | Meaning | Units |
|--------|------|---------|-------|
| **C** | Conscious Field | Observable/Visible state | domain-dependent |
| **I** | Instinctive Field | Hidden/Latent state | domain-dependent |
| **κ** | Kappa | Diffusion/Spreading rate | length²/time |
| **β** | Beta | Coupling strength | 1/time |
| **s** | Source | External drive/bias | field/time |
| **V(φ)** | Potential | Energy landscape | energy/volume |
| **Ω** | Omega | Total energy | energy |

---

## 🗺️ Domain Mapping Guide

### Physics
| UET | Maps to |
|-----|---------|
| C | Visible matter / Observable fields |
| I | Dark matter / Hidden sectors |
| β | Gravitational coupling |
| κ | Speed of propagation |
| V | Potential energy |

### Neuroscience  
| UET | Maps to |
|-----|---------|
| C | Excitatory neural activity |
| I | Inhibitory neural state |
| β | E-I balance |
| κ | Axonal connectivity |
| V | Attractor landscape |

### Economics
| UET | Maps to |
|-----|---------|
| C | Market price |
| I | Intrinsic/Fundamental value |
| β | Market efficiency |
| κ | Information spreading |
| s | External shocks (news) |

### Biology
| UET | Maps to |
|-----|---------|
| C | Activator (morphogen A) |
| I | Inhibitor (morphogen B) |
| β | Reaction rate |
| κ | Diffusion coefficient |
| V | Chemical potential |

### Machine Learning
| UET | Maps to |
|-----|---------|
| C | Observable features |
| I | Latent representation |
| β | Learning rate |
| κ | Weight sharing/convolution |
| V | Loss landscape |

---

## ⚙️ Key Parameters

### Double-Well Potential V(φ)
```
V(φ) = (φ² - 1)² / 4

Properties:
- Minima at φ = ±1
- Maximum at φ = 0
- Barrier height = 1/4
```

This creates **bistable dynamics**:
- Two stable states (φ = ±1)
- Energy barrier between them
- Spontaneous symmetry breaking

### Coupling β
```
β controls how strongly C and I interact:
- β → 0: C and I evolve independently
- β → ∞: C ≈ I (locked together)
- β moderate: Rich coupled dynamics
```

### Diffusion κ
```
κ controls spatial spreading:
- κ → 0: Local dynamics only
- κ large: Global/smooth patterns
- κ moderate: Pattern formation
```

---

## 📊 Observable Quantities

| Quantity | Formula | Meaning |
|----------|---------|---------|
| **Energy Ω** | ∫[κ(∇C)²/2 + V(C) + κ(∇I)²/2 + V(I) + β(C-I)²/2]dx | Total system energy |
| **Order Parameter** | ⟨C⟩ | Average field value |
| **Coherence** | 1 - Var(C)/Max | Spatial uniformity |
| **Entropy** | -∫P(C)log(P(C))dC | Disorder measure |
| **C-I Gap** | ⟨(C-I)²⟩ | Hidden-visible mismatch |

---

## 🧪 Simulation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `grid_size` | 32 | Spatial resolution (NxN) |
| `dt` | 0.01 | Time step |
| `T` | 10.0 | Total simulation time |
| `kappa` | 0.3 | Diffusion coefficient |
| `beta` | 0.5 | Coupling strength |
| `s` | 0.0 | External bias |
| `V_type` | quartic | Potential type |

---

## 🎬 Gallery Categories

| Category | Demos | Purpose |
|----------|-------|---------|
| **Archetypes** | BIAS_C, BIAS_I, SYM | Basic dynamics |
| **Physics** | Einstein, NR, GR | Field equations |
| **Neural** | Seizure, Sleep | Brain dynamics |
| **Finance** | Stock, Bubble | Market dynamics |
| **Traffic** | Rush hour, Smart | Flow dynamics |
| **Biology** | Physarum, Coffee | Pattern formation |
| **3D** | Galaxy, Shell | Volumetric |

---

## 🔧 How to Use

### 1. Identify your domain
What are you trying to model?

### 2. Map variables
- What's your "observable" → C
- What's your "hidden state" → I
- How do they interact → β
- How do they spread → κ

### 3. Choose initial conditions
- Symmetric? Biased? Random?

### 4. Run simulation
```bash
python scripts/run_case.py --kappa 0.3 --beta 0.5 --s 0.1
```

### 5. Analyze results
- Energy evolution
- Pattern formation
- Equilibrium states

---

## 📖 Philosophy

> **"UET doesn't explain everything. UET provides a language TO explain things."**

Like:
- Math doesn't create physics, but describes it
- Programming languages don't solve problems, but express solutions
- UET doesn't discover phenomena, but models them

**You bring the domain knowledge.**
**UET provides the vocabulary.**

---

## 🔗 Resources

- Gallery: `runs_gallery/gallery.html`
- Scripts: `scripts/`
- Docs: `docs/`
- Examples: `runs_demo/`

---

*UET Framework v0.1 - A Common Language for Complex Systems*
