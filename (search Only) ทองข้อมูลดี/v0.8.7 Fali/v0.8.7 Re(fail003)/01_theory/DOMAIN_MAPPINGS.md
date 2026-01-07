# UET Domain Mappings
## How UET Complements Each Physics Domain

**Date:** 2025-12-30

---

## 🔴 AXIOM: ห้ามขัดกับ physics

> ถ้า UET ขัดกับ physics ใดๆ = AI ผิด

---

## Domain 1: THERMODYNAMICS

### What Thermo Says (Established):

| Equation | Meaning |
|----------|---------|
| dS = d_eS + d_iS | Entropy = flow + production |
| d_iS ≥ 0 | Internal production never negative |
| dS_total ≥ 0 | Total entropy increases (2nd law) |
| dE = TdS - PdV | Energy balance |

### What UET ADDS (Not Replaces):

| UET Variable | Maps to Thermo | Meaning |
|--------------|----------------|---------|
| 𝒞 (openness) | d_eS/dt | Rate of entropy EXCHANGE |
| ℐ (closure) | d_iS/dt | Rate of entropy PRODUCTION |
| 𝒱 (value) | -ΔG (free energy) | "Useful" outcome |
| Ω (balance) | G (Gibbs) | Distance from equilibrium |

### How They Work Together:

```
THERMO (established):
  System exchanges heat → dS_e
  System produces entropy → dS_i ≥ 0
  
UET (adds):
  𝒞 = how much exchange → high 𝒞 = d_eS can be negative for system
  ℐ = how much friction → high ℐ = d_iS is high
  𝒱 = net result → 𝒱 = f(𝒞/ℐ)
  
TOGETHER:
  Open system (high 𝒞) can ↓ its entropy by exporting it
  This does NOT violate 2nd law: total entropy still ↑
```

### Validation:
- ✅ Does NOT contradict dS_total ≥ 0
- ✅ Does NOT replace any thermo equation
- ✅ ADDS interpretation of open vs closed

---

## Domain 2: CLASSICAL MECHANICS

### What Newton Says (Established):

| Equation | Meaning |
|----------|---------|
| F = ma | Force = mass × acceleration |
| E = ½mv² | Kinetic energy |
| U = -GMm/r | Potential energy |
| E_total = constant | Energy conserved |

### What UET ADDS (Not Replaces):

| UET Variable | Meaning in Mechanics |
|--------------|----------------------|
| 𝒞 | Coupling between systems (interaction rate) |
| ℐ | Friction/damping (energy loss rate) |
| 𝒱 | Efficiency of energy use |
| Ω | Potential/cost to minimize |

### How They Work Together:

```
NEWTON (established):
  Objects move: F = ma
  Energy conserved: E = constant
  
UET (adds):
  When objects interact, HOW EFFICIENTLY?
  𝒱 = outcome after friction ℐ
  Ω = "tension" driving motion (like potential)
  
TOGETHER:
  Newton tells you WHERE object goes
  UET tells you HOW VALUABLE that motion is
```

### Validation:
- ✅ Does NOT say F ≠ ma
- ✅ Does NOT say E not conserved
- ✅ ADDS value/efficiency layer

---

## Domain 3: QUANTUM MECHANICS

### What QM Says (Established):

| Equation | Meaning |
|----------|---------|
| Ĥψ = Eψ | Energy eigenvalue equation |
| ⟨H⟩ = ⟨ψ\|Ĥ\|ψ⟩ | Expected energy |
| ΔxΔp ≥ ℏ/2 | Uncertainty principle |
| S = -k Tr(ρ ln ρ) | von Neumann entropy |

### What UET ADDS (Not Replaces):

| UET Variable | Meaning in Quantum |
|--------------|-------------------|
| 𝒞 | Interaction with environment (coupling) |
| ℐ | Decoherence / isolation |
| 𝒱 | Information/coherence preserved |
| Ω | ⟨H⟩ or free energy functional |

### How They Work Together:

```
QUANTUM (established):
  System evolves: Ĥψ = Eψ
  Measurement: collapse + uncertainty
  
UET (adds):
  Open quantum system: 𝒞 = coupling to bath
  Decoherence: ℐ = loss of quantum info
  𝒱 = preserved coherence/information
  
TOGETHER:
  QM tells you HOW system evolves
  UET tells you HOW MUCH info survives
```

### Validation:
- ✅ Does NOT contradict Schrödinger equation
- ✅ Does NOT say uncertainty is wrong
- ✅ ADDS open-system interpretation

---

## Domain 4: INFORMATION THEORY

### What Info Theory Says (Established):

| Equation | Meaning |
|----------|---------|
| H = -Σ p ln p | Shannon entropy |
| E_bit = kT ln 2 | Landauer energy cost |
| C = B log(1+S/N) | Channel capacity |

### What UET ADDS (Not Replaces):

| UET Variable | Meaning in Info |
|--------------|-----------------|
| 𝒞 | Channel capacity / bandwidth |
| ℐ | Noise / overhead |
| 𝒱 | Effective info transmitted |
| Ω | Uncertainty / disorder |

### How They Work Together:

```
INFO THEORY (established):
  Bits cost energy: E = kT ln 2
  Channel has capacity: C = B log(1+S/N)
  
UET (adds):
  𝒞 is like channel capacity
  ℐ is like noise/loss
  𝒱 = useful info after losses
  
TOGETHER:
  Info theory tells you LIMITS
  UET tells you EFFICIENCY within limits
```

### Validation:
- ✅ Uses Landauer principle
- ✅ Does NOT violate Shannon bounds
- ✅ ADDS system-level interpretation

---

## Summary: UET as Complementary Layer

```
┌─────────────────────────────────────────────┐
│           ESTABLISHED PHYSICS               │
│  Newton, Einstein, Thermo, QM, Info Theory  │
│         (NEVER contradicted)                │
├─────────────────────────────────────────────┤
│                    ↕                        │
│              LANDAUER BRIDGE                │
│           E = kT ln 2 (bit↔energy)          │
├─────────────────────────────────────────────┤
│                    ↕                        │
│           UET (COMPLEMENTARY)               │
│    𝒞 (open), ℐ (closed), 𝒱 (value), Ω      │
│   Adds: efficiency, value, organization     │
└─────────────────────────────────────────────┘
```

---

*Domain Mappings - 2025-12-30*
